"""Independent exact-integer replay of explicitly supported certificate formats.

No search code, network, source checker or secret is used. Base exponent is 1.
An operation (i,j) appends e[i]+e[j], charging S iff i==j, otherwise M.
Value-referenced triples are resolved only to already-created unique values.
All serialized rows are charged, including rows outside the output ancestry.
"""
import argparse
import copy
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 512_000
MAX_OPS = 2000
ROOT = Path(__file__).resolve().parents[1]


class Invalid(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Invalid(why)


def integer(x):
    need(type(x) is int, "integer type required (booleans rejected)")
    need(0 <= x < (1 << 1100), "integer outside certificate bounds")
    return x


def numeric(x):
    if type(x) is int:
        return integer(x)
    need(type(x) is str and re.fullmatch(r"(?:0x[0-9a-fA-F]+|[0-9]+)", x) is not None, "invalid decimal/0x integer metadata")
    return integer(int(x, 16 if x.startswith("0x") else 10))


def hexint(x):
    need(type(x) is str and re.fullmatch(r"(?:0x)?[0-9a-fA-F]+", x) is not None, "invalid hex metadata")
    return integer(int(x, 16))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def local_path(rel):
    p = ROOT / rel
    need(not Path(rel).is_absolute() and ".." not in Path(rel).parts, "non-portable bundle path")
    need(p.resolve().is_relative_to(ROOT), "path escaped bundle")
    for q in [p, *p.parents]:
        if q == ROOT.parent:
            break
        if q.exists():
            need(not (getattr(q.lstat(), "st_file_attributes", 0) & 0x400), "reparse path refused")
    return p


def load_bytes(rel):
    p = local_path(rel)
    with p.open("rb") as f:
        b = f.read(MAX_BYTES + 1)
    need(len(b) <= MAX_BYTES, "input size cap")
    return b


def decode(data, fmt):
    """Return exact exponent values, parent indices and original metadata."""
    if fmt == "integer-triples-text":
        s = data.decode("utf-8-sig")
        raw = []
        for line in s.splitlines():
            if not line.strip():
                continue
            need(re.fullmatch(r"\s*[0-9]+\s+[0-9]+\s+[0-9]+\s*", line) is not None, "text row is not exactly three unsigned integers")
            raw.append([int(x) for x in line.split()])
        d = {"rows": raw}
    else:
        d = json.loads(data.decode("utf-8-sig"))
        need(type(d) is dict, "certificate object required")
    vals, parents = [1], []

    def append(a, b, declared=None):
        a, b = integer(a), integer(b)
        need(a < len(vals) and b < len(vals), "operand reference is not earlier/available")
        v = vals[a] + vals[b]
        integer(v)
        if declared is not None:
            need(integer(declared) == v, "exact parent sum mismatch")
        need(len(parents) < MAX_OPS, "operation cap")
        vals.append(v); parents.append((a, b))

    if "nodes" in d:
        nodes = d["nodes"]
        need(type(nodes) is list and 1 < len(nodes) <= MAX_OPS + 1, "nodes shape/cap")
        need(type(nodes[0]) is dict and hexint(nodes[0]["exponent_hex"]) == 1 and nodes[0]["parents"] is None, "base node must be exponent 1 with no parents")
        for node in nodes[1:]:
            need(type(node) is dict and type(node["parents"]) is list and len(node["parents"]) == 2, "node parent shape")
            append(*node["parents"], declared=hexint(node["exponent_hex"]))
    elif "steps" in d or isinstance(d.get("operations"), list):
        steps = d["steps"] if "steps" in d else d["operations"]
        need(type(steps) is list and 0 < len(steps) <= MAX_OPS, "steps shape/cap")
        for step in steps:
            if type(step) is list:
                need(len(step) == 2, "index pair must have two operands")
                append(*step)
            else:
                need(type(step) is dict and "left" in step and "right" in step, "indexed operation shape")
                append(step["left"], step["right"])
        if "precompute_values" in d:
            pre = d["precompute_values"]
            need(type(pre) is list and 0 < len(pre) <= len(vals), "precompute values shape")
            need([integer(x) for x in pre] == vals[:len(pre)], "precompute values disagree with computed prefix")
            if "first_window" in d:
                fw = d["first_window"]
                need(type(fw) is dict and integer(fw["bits"]) > 0 and integer(fw["exponent"]) in pre, "first-window metadata mismatch")
    elif "rows" in d:
        rows = d["rows"]
        need(type(rows) is list and 0 < len(rows) <= MAX_OPS, "rows shape/cap")
        if type(rows[0]) is dict:
            names = {"x": 0}
            for row in rows:
                need(type(row) is dict and row["name"] not in names and row["op"] in ["S", "M"], "named operation shape or duplicate")
                args = row["args"]
                need(type(args) is list and len(args) == 2 and args[0] in names, "named first operand missing")
                if row["op"] == "S":
                    count = integer(args[1]); need(0 < count <= MAX_OPS, "squaring-run length")
                    a = names[args[0]]
                    for _ in range(count):
                        append(a, a); a = len(vals)-1
                else:
                    need(args[1] in names, "named second operand missing")
                    append(names[args[0]], names[args[1]])
                names[row["name"]] = len(vals)-1
            need(d.get("terminal") in names, "named terminal missing")
            need(names[d["terminal"]] == len(vals)-1, "named terminal is not final output")
        else:
            available = {1: 0}
            for row in rows:
                need(type(row) is list and len(row) in [3,4], "value triple shape")
                if len(row) == 4:
                    need(type(row[3]) is str, "fourth row member must be a phase label")
                v, a, b = [integer(x) for x in row[:3]]
                need(a in available and b in available, "value operand is not earlier/available")
                need(v not in available, "duplicate exponent makes value references ambiguous")
                append(available[a], available[b], declared=v)
                available[v] = len(vals)-1
    else:
        raise Invalid("unsupported encoding: no explicit rows/steps/nodes")
    return vals, parents, d


def verify(data, fmt, target, modulus, modular=True):
    vals, parents, d = decode(data, fmt)
    target, modulus = integer(target), integer(modulus)
    need(target > 1 and modulus == target + 2, "pinned inversion target/modulus relation")
    for key in ["target_hex"]:
        if key in d:
            need(hexint(d[key]) == target, key + " disagrees with pinned target")
    for key in ["target_decimal"]:
        if key in d:
            need(numeric(d[key]) == target, key + " disagrees with pinned target")
    if type(d.get("target")) is int or (type(d.get("target")) is str and d["target"].isdigit()):
        need(numeric(d["target"]) == target, "target disagrees with pinned target")
    for key in ["n_hex", "order_hex"]:
        if key in d:
            need(hexint(d[key]) == modulus, key + " disagrees with pinned modulus")
    for key in ["modulus", "order_decimal", "order_dec"]:
        if key in d:
            need(numeric(d[key]) == modulus, key + " disagrees with pinned modulus")
    out = integer(d.get("output_index", len(vals)-1))
    need(0 < out < len(vals) and vals[out] == target, "computed output is not exact pinned target")
    need(out == len(vals)-1, "serialized operations after declared output")
    s = sum(a == b for a,b in parents); m = len(parents)-s
    checked = []
    declared = {"operations": len(parents), "operation_count": len(parents), "squarings": s, "multiplications": m}
    for k,expected in declared.items():
        if k in d and not isinstance(d[k], list):
            need(integer(d[k]) == expected, k + " metadata disagrees with charged rows"); checked.append(k)
    for objkey in ["count", "counts"]:
        if objkey in d:
            need(type(d[objkey]) is dict, "count object shape")
            for k, expected in {"S":s,"M":m,"squarings":s,"multiplications":m,"operations":len(parents),"total":len(parents)}.items():
                if k in d[objkey]:
                    need(integer(d[objkey][k]) == expected, objkey+"."+k+" disagrees with charged rows"); checked.append(objkey+"."+k)
    live = {out}; todo = [out]
    while todo:
        i = todo.pop()
        if i == 0:
            continue
        for p in parents[i-1]:
            if p not in live:
                live.add(p); todo.append(p)
    dead = sorted(set(range(1,len(vals))) - live)
    if "all_rows_live" in d:
        need(type(d["all_rows_live"]) is bool and d["all_rows_live"] == (not dead), "all_rows_live metadata disagrees with reachability")
    live_s = sum(i in live and a==b for i,(a,b) in enumerate(parents,1))
    live_m = sum(i in live and a!=b for i,(a,b) in enumerate(parents,1))
    mod_bases = [2,3,5,7,11,17,257] if modular else []
    for base in mod_bases:
        v = [base % modulus]
        for a,b in parents:
            v.append(v[a]*v[b] % modulus)
        need(v[out] == pow(base,target,modulus), "modular exponent replay mismatch")
        need(v[out] * base % modulus == 1, "sample inverse identity failed")
    value_rows = sorted((vals[i], min(vals[a],vals[b]), max(vals[a],vals[b])) for i,(a,b) in enumerate(parents,1))
    canonical = json.dumps(value_rows,separators=(",",":"))
    return {"state": "PASS_EXACT_ARITHMETIC" if not dead else "PASS_EXACT_ARITHMETIC_WITH_DEAD_ROWS",
            "target_decimal":str(target),"target_hex":format(target,"x"),"modulus_hex":format(modulus,"x"),
            "charged":{"operations":len(parents),"S":s,"M":m},"live":{"operations":live_s+live_m,"S":live_s,"M":live_m},
            "dead":{"operations":len(dead),"indices":dead},"strictly_increasing_schedule":all(vals[i]>vals[i-1] for i in range(1,len(vals))),
            "arithmetic_graph_sha256":sha(canonical.encode()),"graph_hash_scope":"sorted exponent triples with unordered parents; row multiplicity retained",
            "checked_count_fields":checked,"modular_bases":mod_bases,
            "ceiling":"exact positive-integer exponent identity and counts; samples are not timing, optimality, security or acceptance"}


def controls(data, fmt, target, modulus):
    vals, parents, _ = decode(data,fmt)
    rows = [[vals[i],vals[a],vals[b]] for i,(a,b) in enumerate(parents,1)]
    base = {"target_hex":format(target,"x"),"rows":rows}
    # Mutants are deliberately re-encoded/repinned; rejection must be semantic.
    cases = {}
    x=copy.deepcopy(base);x["target_hex"]=format(target-1,"x");cases["wrong_declared_target"]=x
    x=copy.deepcopy(base);x["rows"][0][1]=target+1;cases["bad_future_reference"]=x
    x=copy.deepcopy(base);x["rows"][0][0]+=1;cases["wrong_sum"]=x
    x=copy.deepcopy(base);x["rows"].pop();cases["truncated_chain"]=x
    x=copy.deepcopy(base);x["rows"][-1][2]=1;cases["tampered_terminal_operand"]=x
    x=copy.deepcopy(base);x["operations"]=len(parents)+1;cases["false_count"]=x
    x=copy.deepcopy(base);x["rows"][0][1]=True;cases["boolean_operand"]=x
    x=copy.deepcopy(base);x["all_rows_live"]=False;cases["false_liveness_declaration"]=x
    out=[]
    for name,mut in cases.items():
        b=json.dumps(mut).encode()
        try:
            verify(b,"json",target,modulus,modular=False)
            out.append({"control":name,"state":"UNEXPECTED_ACCEPT","mutant_sha256":sha(b)})
        except (Invalid,ValueError,KeyError,TypeError) as e:
            out.append({"control":name,"state":"REJECTED","reason":str(e),"mutant_sha256":sha(b)})
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",default="inventory/BUNDLE_INPUTS.v2.json")
    parser.add_argument("--output")
    args=parser.parse_args()
    manifest_bytes=load_bytes(args.manifest)
    manifest=json.loads(manifest_bytes)
    results=[]; control_result=None; integrity_control=None
    for item in manifest["witnesses"]:
        if item["format"] == "unsupported":
            results.append({"id":item["id"],"state":"HOLD_ENCODING_NOT_IMPLEMENTED"});continue
        try:
            b=load_bytes(item["bundle_path"])
            need(sha(b)==item["sha256"],"original input SHA-256 mismatch")
            t=manifest["targets"][item["target_id"]]
            result=verify(b,item["format"],int(t["target_decimal"]),int(t["modulus_decimal"]))
            result.update({"id":item["id"],"input_sha256":sha(b),"target_id":item["target_id"]})
            results.append(result)
            if control_result is None and not result["dead"]["operations"]:
                control_result=controls(b,item["format"],int(t["target_decimal"]),int(t["modulus_decimal"]))
                tampered=b+b"\n"
                try:
                    need(sha(tampered)==item["sha256"],"original input SHA-256 mismatch")
                    integrity_control={"state":"UNEXPECTED_ACCEPT"}
                except Invalid as e:
                    integrity_control={"state":"REJECTED","reason":str(e),"original_sha256":item["sha256"],"tampered_sha256":sha(tampered),"mutation":"append newline; may preserve arithmetic, must fail original-byte pin"}
        except (Invalid,ValueError,KeyError,TypeError,UnicodeError,OSError) as e:
            results.append({"id":item["id"],"state":"FAIL_PRESERVED","reason":str(e)})
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")+"-"+str(time.time_ns())[-9:]
    out={"schema":"addition-chain-offline-replay.v1","observed_utc":datetime.now(timezone.utc).isoformat(),
         "verifier_sha256":sha(Path(__file__).read_bytes()),"input_manifest_sha256":sha(manifest_bytes),
         "author_independence":"new implementation; same collecting carrier, no distinct human/provider review",
         "results":results,"negative_controls":control_result,
         "positive_control":"first valid original certificate; semantic mutants verified without original hash gate",
         "tamper_integrity_control": integrity_control,
         "summary": {s:sum(r["state"]==s for r in results) for s in sorted({r["state"] for r in results})}}
    dest=local_path(args.output or f"verification/replay-{stamp}.json")
    with dest.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(out,f,indent=2);f.write("\n")
    print(json.dumps({"receipt":str(dest),"summary":out["summary"],"negative_controls_rejected":sum(c["state"]=="REJECTED" for c in control_result or [])}))
    return 1 if any(r["state"]=="FAIL_PRESERVED" for r in results) or any(c["state"]!="REJECTED" for c in control_result or []) or not integrity_control or integrity_control["state"]!="REJECTED" else 0


if __name__ == "__main__":
    sys.exit(main())
