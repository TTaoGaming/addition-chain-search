"""Create frozen candidate stimuli/schema and preassigned run order; no inference."""
import hashlib,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"stimuli"
OUT.mkdir(exist_ok=True)
def write(name,data):
 p=OUT/name
 if p.exists(): raise SystemExit("refuse overwrite "+str(p))
 b=(json.dumps(data,indent=2)+"\n").encode() if not isinstance(data,str) else data.encode()
 p.write_bytes(b)
 return {"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
relevant=[
 "Episode A, public training target 15: the binary construction used 6 charged operations. The retained sequence [1,2,3,6,12,15] used 5. Its helper nodes were constructed and charged; there is no shortest-chain claim.",
 "Episode B, public training target 31: the binary construction used 8 charged operations. The retained sequence [1,2,3,5,10,15,30,31] used 7. This is a valid construction, not a claim about the present task.",
 "Episode C, identity accounting: repeated exponent values can have different index consumers. Distinct serialized files may describe the same arithmetic schedule. Track parent indices and charged rows separately from filenames; dead rows remain charged."
]
irrelevant=[
 "Archive note A records that a plain UTF-8 inventory can retain relative paths and human-readable labels. A filename is a locator. Modification time and a later capture time are different metadata fields. The note makes no mathematical assertion.",
 "Archive note B records that a table can contain a header row followed by records. A JSON document may carry the same labels as a CSV document. File extensions help a reader choose a viewer. This note describes storage conventions.",
 "Archive note C records that a figure caption can link to a source table. A document can retain a title, a date and an author field. These are navigation facts rather than a search result. This note describes report organization."
]
# Match word count exactly using a fixed neutral truncation/padding rule, not outcome tuning.
n=len("\n\n".join(relevant).split())
words="\n\n".join(irrelevant).split()
while len(words)<n: words.extend(["Record","metadata","remain","available","for","navigation."])
irrelevant_text=" ".join(words[:n])
skill="""Operative search skill:
- Treat every helper as paid; preserve exact earlier-index dependencies.
- Keep a valid incumbent when feedback supplies one.
- Before another tool request, compare its region with earlier requests; avoid repeating an identical region without a reason.
- Explore a different construction family or parameter region when the previous attempt did not improve the incumbent.
- Check target equality and all indices before submitting a direct chain.
- Use measured candidate costs, when supplied, to allocate the remaining decisions. An assertion of improvement is not a valid certificate.
"""
schema={"type":"object","additionalProperties":False,"properties":{
 "type":{"type":"string","enum":["submit_chain","construct","search"]},
 "method":{"type":"string","enum":["none","binary","window","dictionary"]},
 "width":{"type":"integer","minimum":1,"maximum":6},
 "variant":{"type":"string","enum":["fixed","sliding"]},
 "widths":{"type":"array","items":{"type":"integer","minimum":1,"maximum":6},"maxItems":6},
 "digits":{"type":"array","items":{"type":"integer","minimum":1,"maximum":63},"maxItems":32},
 "candidate_digits":{"type":"array","items":{"type":"integer","minimum":1,"maximum":63},"maxItems":16},
 "max_added_digits":{"type":"integer","minimum":0,"maximum":3},
 "max_window_bits":{"type":"integer","minimum":1,"maximum":6},
 "max_evaluations":{"type":"integer","minimum":1,"maximum":64},
 "steps":{"type":"array","items":{"type":"array","items":{"type":"integer","minimum":0,"maximum":256},"minItems":2,"maxItems":2},"maxItems":256},
 "output_index":{"type":"integer","minimum":0,"maximum":256},
 "rationale":{"type":"string"}
}}
schema["required"]=list(schema["properties"])
pins=[write("relevant.txt","\n\n".join(relevant)+"\n"),
 write("reordered.txt","\n\n".join(reversed(relevant))+"\n"),
 write("irrelevant.txt",irrelevant_text+"\n"),write("skill.txt",skill),
 write("action.schema.json",schema)]
protocol=json.loads((ROOT/"PROTOCOL.v1.json").read_text())
jobs=[]
for task in protocol["tasks"]:
 for rep in protocol["replicate_ids"]:
  for cell in protocol["cells"]:
   jobs.append({"id":task["id"]+"__r"+str(rep)+"__"+cell["id"]+"__sol","task":task,"replicate":rep,"cell":cell,"model":"gpt-6.1-sol"})
  base=dict(protocol["cells"][0])
  jobs.append({"id":task["id"]+"__r"+str(rep)+"__B__luna","task":task,"replicate":rep,"cell":base,"model":"gpt-6-luna"})
random.Random(protocol["assignment"]["order_seed"]).shuffle(jobs)
pins.append(write("RUN_ORDER.json",jobs))
pins.append(write("PROMPT_TEMPLATE.txt","""You are a bounded addition-chain proposal controller. Native CLI tools are unavailable; return only the requested JSON data. Do not read files, browse, execute code, delegate, or seek hidden evaluation material.
Identity framing: {label}.
Task: exact integer target {target}, exponent base e[0]=1, unit-cost additions, public binary baseline {baseline} operations.
Every row [a,b] creates a new exponent by adding earlier nodes. S iff a==b, otherwise M. All rows including dead rows are charged. Repeated values are allowed. output_index selects any computed non-base node; it defaults to the last created node. At most256 rows and65536 candidate bytes.
Objective: minimize exact valid charged operations. Three decisions total. Each attempted action/refusal consumes one decision. Search actions evaluate at most64 deterministic candidates. Search tools are {tools}; verifier feedback is {feedback}. Final exact evaluation is identical in every condition.
{skill}
Retrieved static memory packet ({memory_kind}):
{memory}
Action interface:
- submit_chain: explicit steps and output_index.
- construct binary: no knobs. construct window: width1..6, variant fixed/sliding.
- construct dictionary: positive odd digits, max_window_bits1..6.
- search window: widths list, variants fixed+sliding, max_evaluations1..64.
- search dictionary: digits as base_digits, candidate_digits, max_added_digits0..3, max_window_bits1..6, max_evaluations1..64.
If search tools are off, construct/search are refused; submit_chain remains available.
Fill the common JSON schema. Irrelevant fields may use simple defaults: method none, width1, variant sliding, empty arrays, max_added_digits0, max_window_bits1, max_evaluations1, output_index0. For submit_chain, output_index must select the intended result. Keep rationale under100 words; rationale is not an evaluated candidate.
Decision {round} of3.
Earlier actions and visible feedback from this trajectory only:
{history}
Return one JSON action now.
"""))
manifest={"schema":"frozen-ablation-stimuli.v1","pins":pins,"memory_word_counts":{"relevant":n,"reordered":n,"irrelevant":len(irrelevant_text.split())},"tokenizer_equivalence":"NOT_CLAIMED","run_count":len(jobs),"oracle_material_exposed":"task integer and binary count only; no oracle paths/source"}
write("MANIFEST.json",manifest)
print(json.dumps(manifest))

