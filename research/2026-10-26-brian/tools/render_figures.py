"""Rebuild research figures and editable graph sources from this frozen bundle.

Only figures/ and report-support/FIGURE_GUIDE.md are written. Matplotlib is
needed for rendering; the offline certificate verifier uses only stdlib.
"""
import csv
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
BLUE, ORANGE, PURPLE, GREY = "#235789", "#d66d27", "#8054a1", "#6c7580"
INK, PALE = "#172b3a", "#edf3f8"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelcolor": INK, "text.color": INK, "axes.titleweight": "bold",
    "svg.fonttype": "none", "figure.facecolor": "white", "axes.facecolor": "white"})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(rel):
    p=ROOT/rel
    raw=gzip.open(p,"rb").read() if p.suffix==".gz" else p.read_bytes()
    return json.loads(raw.decode("utf-8-sig"))


def write(rel, text):
    (OUT / rel).write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def csvout(name, rows, fields):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def save(fig, name):
    fig.savefig(OUT / (name + ".png"), dpi=135, facecolor="white")
    fig.savefig(OUT / (name + ".svg"), facecolor="white")
    plt.close(fig)


def footer(fig, text):
    fig.text(.055, .018, text, fontsize=8, color=GREY, va="bottom")


def budget_plot(ablation, memory):
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8))
    fig.subplots_adjust(left=.07, right=.97, top=.79, bottom=.27, wspace=.24)
    fig.suptitle("Which selection policies helped in their tested regions?", x=.055, ha="left", y=.97, fontsize=16, fontweight="bold")
    fig.text(.055, .88, "Matched assessment/attempt counts; different sampled work and realized CPU. Lower is better.", fontsize=10)
    data = []
    for row in ablation["p256_matched_assessment_runs"]:
        if row["group"] != "p256_policy_correction_20260929":
            continue
        points = row["trajectory"]
        xs = [p["assessment"] for p in points] + [row["assessments"]]
        ys = [p["operations"] for p in points] + [points[-1]["operations"]]
        label = "Score guided" if row["policy"] == "score_guided" else "Hash control"
        color = BLUE if row["policy"] == "score_guided" else ORANGE
        axes[0].step(xs, ys, where="post", color=color, lw=2, label=label)
        axes[0].scatter(xs[-1], ys[-1], color=color, s=25, zorder=3)
        axes[0].annotate(str(ys[-1]), (xs[-1], ys[-1]), xytext=(-4, -12 if label == "Score guided" else 8), textcoords="offset points", ha="right", color=color, fontweight="bold")
        for p in points:
            data.append({"target":"P-256 scalar n-2", "arm":row["policy"], "unit":"assessment", "ordinal":p["assessment"], "operations":p["operations"], "weighted_0_8S_plus_M":"", "source":"verification/ABLATION_AUDIT.json"})
    axes[0].axhline(291, color=GREY, ls="--", lw=1.2, label="Then-incumbent 291")
    axes[0].set(xscale="log", xlim=(1, 27000), ylim=(282, 430), xlabel="Scored assessments (log scale)", ylabel="Best total S + M", title="P-256: 24,000 assessments / arm")
    axes[0].grid(axis="y", alpha=.18)
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.text(.07, .095, "Correction rerun: 0 changed state ordinals\nand 0 changed score ordinals in both arms.", fontsize=8.5, color=GREY)
    for row in memory["arms"]:
        points = row["trajectory"]
        xs = [p["attempt"] for p in points] + [row["attempts"]]
        ys = [p["weighted_fifths"] / 5 for p in points] + [points[-1]["weighted_fifths"] / 5]
        guided = row["arm"] == "memory_guided"
        color = BLUE if guided else ORANGE
        label = "History-guided order" if guided else "SHA-ordered control"
        axes[1].step(xs, ys, where="post", color=color, lw=2, label=label)
        axes[1].scatter(xs[-1], ys[-1], color=color, s=25, zorder=3)
        axes[1].annotate(f"{ys[-1]:.1f} ({row['best_total']} ops)", (xs[-1], ys[-1]), xytext=(-4, 30 if guided else -14), textcoords="offset points", ha="right", color=color, fontsize=8, fontweight="bold")
        for p in points:
            data.append({"target":"P-521 scalar n-2", "arm":row["arm"], "unit":"attempt", "ordinal":p["attempt"], "operations":p["operations"], "weighted_0_8S_plus_M":p["weighted_fifths"] / 5, "source":"verification/P521_MEMORY_AUDIT.json"})
    axes[1].axhline(478.2, color=GREY, ls="--", lw=1.2, label="Then-incumbent 582 ops")
    axes[1].set(xscale="log", xlim=(1, 1200), ylim=(476.7, 489), xlabel="Attempted cases (log scale)", ylabel="Best illustrative 0.8S + M", title="P-521: 1,024 attempts / arm")
    axes[1].grid(axis="y", alpha=.18)
    axes[1].legend(frameon=False, fontsize=8, loc="upper right")
    fig.text(.57, .095, "744 vs 701 valid-DAG reports; 224 shared cases.\nOne manually designed order / control seed.", fontsize=8.5, color=GREY)
    footer(fig, "Retained historical traces audited 2026-10-26. These comparisons do not establish autonomous learning, collaboration gains or generalization.")
    save(fig, "budgeted_policy_controls")
    csvout("budgeted_policy_controls.csv", data, list(data[0]))


def helper_graph(manifest):
    witness = next(w for w in manifest["witnesses"] if w["sha256"].startswith("46ba0fb4"))
    assert hashlib.sha256(gzip.open(ROOT/witness["bundle_path"],"rb").read()).hexdigest() == witness["sha256"], "witness byte drift"
    raw = load(witness["bundle_path"])
    rows = raw["rows"]
    values = [1] + [r[0] for r in rows]
    index = {v:i for i,v in enumerate(values)}
    parents = [(index[r[1]], index[r[2]]) for r in rows]
    helper = index[8415]
    selected = {helper}; todo = [helper]
    while todo:
        i = todo.pop()
        if i:
            for p in parents[i-1]:
                if p not in selected:
                    selected.add(p); todo.append(p)
    sq = sum(parents[i-1][0] == parents[i-1][1] for i in selected if i)
    mu = len(selected)-1-sq
    assert helper == 136 and len(selected)-1 == 17 and sq == 8 and mu == 9
    full = []
    for i,(v,a,b) in enumerate(rows,1):
        full.append({"row":i,"exponent_decimal":str(v),"left_exponent_decimal":str(a),"right_exponent_decimal":str(b),"left_row":index[a],"right_row":index[b],"charge":"S" if a == b else "M","in_helper8415_ancestry":i in selected})
    csvout("p256_284_full_dag.csv", full, list(full[0]))
    dot = ["// Exact original DAG; node0 is base exponent1. No sorting or repair.", f"// Original SHA256 {witness['sha256']}", 'digraph P256_284 {', 'rankdir=LR;', 'node [shape=box, fontsize=9];', 'n0 [label="row0 | exponent1", fillcolor="#eeeeee", style=filled];']
    mmd = ["%% Exact original DAG; raw row order preserved; node0 is base exponent1.", "%% Original SHA256 " + witness["sha256"], "flowchart LR", '  n0["r0: 1"]']
    helper_mmd = ["%% Exact ancestor closure of paid helper8415 in the 284-operation witness.", "%% 17 operations = 8S + 9M; only unrelated rows omitted.", "flowchart LR", '  n0["r0: 1"]']
    for i,(v,a,b) in enumerate(rows,1):
        label = str(v) if len(str(v)) < 20 else format(v,"x")[:10] + "... (hex)"
        charge = "S" if a == b else "M"
        color = "#dce9f4" if charge == "S" else "#fce6d6"
        dot.append(f'n{i} [label="r{i} | {label} | {charge}", fillcolor="{color}", style=filled];')
        mmd.append(f'  n{i}["r{i}: {label} ({charge})"]')
        if i in selected:
            helper_mmd.append(f'  n{i}["r{i}: {v} ({charge})"]')
        for p in sorted(set(parents[i-1])):
            dot.append(f'n{p} -> n{i};')
            mmd.append(f'  n{p} --> n{i}')
            if i in selected:
                helper_mmd.append(f'  n{p} --> n{i}')
    dot.append('}')
    write("p256_284_full_dag.dot", "\n".join(dot))
    write("p256_284_full_dag.mmd", "\n".join(mmd))
    write("p256_284_helper8415.mmd", "\n".join(helper_mmd))
    fig, ax = plt.subplots(figsize=(11.3, 4.5))
    fig.subplots_adjust(left=.035, right=.98, top=.79, bottom=.18)
    fig.suptitle("A paid helper can reuse an already charged scaffold", x=.055, ha="left", y=.96, fontsize=16, fontweight="bold")
    fig.text(.055, .865, "P-256 scalar n−2: selected ancestor closure from the original 284-row DAG", fontsize=10)
    ax.set(xlim=(0,11), ylim=(0,3)); ax.axis("off")
    def box(x,y,w,h,text,color):
        p=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.06,rounding_size=.07",fc=color,ec="#9caab6",lw=1)
        ax.add_patch(p);ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=10)
    def arrow(a,b,text,rad=0):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=12,color=GREY,lw=1.4,connectionstyle=f"arc3,rad={rad}"))
        ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,text,ha="center",va="bottom",fontsize=9,color=GREY)
    box(.2,1.5,2.6,.9,"Base x¹ → x²⁵⁵\nRows 1–11: 3S + 8M",PALE)
    box(4.15,1.5,2.45,.9,"x⁸¹⁶⁰\nRows 12–16",PALE)
    box(8.1,.8,2.5,1.1,"x⁸⁴¹⁵ = x²⁵⁵ × x⁸¹⁶⁰\nRow 136: 1M", "#fce6d6")
    arrow((2.86,1.96),(4.08,1.96),"5 S")
    arrow((6.65,1.87),(8.02,1.46),"")
    arrow((2.83,1.68),(8.03,1.04),"",rad=.16)
    ax.text(5.5,1.05,"reuse row 11",ha="center",fontsize=9,color=GREY)
    ax.text(.25,.7,"Exact helper ancestry: 17 charged operations = 8S + 9M",fontsize=11,fontweight="bold",color=BLUE)
    ax.text(.25,.12,"Row 135 is 340282366841710300967557013911933812735; row 136 drops to 8415.\nBoth operands were available earlier. This is a legal topological DAG, not a strictly increasing chain.",fontsize=9,color=GREY)
    footer(fig, "Contracted view: unrelated rows are omitted here. Full original row order, exponents and edges are in p256_284_full_dag.csv/.dot/.mmd.")
    save(fig,"p256_284_paid_helper")
    return {"original_sha256":witness["sha256"],"helper_row":helper,"helper_ancestor_operations":17,"S":sq,"M":mu,"previous_row135_exponent":str(values[135]),"full_DAG_operations":len(rows)}


def history_plot(sources, replay):
    source = next(s for s in sources if s["group"] == "historical-report-support" and Path(s["source_path"]).name == "manifest.json")
    assert digest(ROOT/source["bundle_path"]) == source["sha256"], "history source byte drift"
    history = load(source["bundle_path"])
    ledger = next(s for s in sources if "PRIVATE_SEARCH_EPISODE_SOURCES" in s["source_path"])
    milestones = history["milestones"]
    current = {r.get("input_sha256"):r for r in replay["results"]}
    events = [
        {"label":"432","operations":432,"S":"UNKNOWN","M":"UNKNOWN","reported_date":"2026-09-10","raw_clock":"2026-09-10 13:42:05 UTC","precision":"second, reported in secondary reconstruction","method":"dictionary / prefix + tail DP","raw_witness_in_bundle":False,"sha256":"","source":ledger["bundle_path"]},
        {"label":"429","operations":429,"S":381,"M":48,"reported_date":"2026-09-10","raw_clock":"2026-09-10 13:42:54–13:42:55 UTC","precision":"reported interval","method":"corrected dictionary probe","raw_witness_in_bundle":False,"sha256":"","source":ledger["bundle_path"]},
        {"label":"426","operations":426,"S":380,"M":46,"reported_date":"2026-09-10","raw_clock":"2026-09-10 15:08:01–15:08:08 UTC","precision":"reported interval","method":"joint dictionary-DAG MILP","raw_witness_in_bundle":False,"sha256":"565353709cba96a918ed307ba426da62dc4ee1dd962a3d41e5d536483ad5b83d","source":ledger["bundle_path"]}]
    methods={425:"overlap / carry DP",424:"helper / weighted frontier",423:"star-prefix + tail",422:"prefix insertion + helpers",421:"CPU anneal + tail DP"}
    for m in milestones:
        result=current[m["sha256"]]
        assert result["charged"]["operations"] == m["operations"]
        # 425 has a Sep21 first-observed/capture field and a Sep10 reported run.
        # Keep both clocks. The categorical figure does not invent elapsed time.
        events.append({"label":str(m["operations"])+("-A" if m["operations"]==421 else ""),"operations":m["operations"],"S":m["squarings"],"M":m["other_multiplications"],"reported_date":"2026-09-10" if m["operations"]==425 else m["first_observed_utc"][:10],"raw_clock":"2026-09-10 15:18–15:25 UTC (reported run); manifest first_observed="+m["first_observed_utc"] if m["operations"]==425 else m["first_observed_utc"],"precision":"reported minute interval + distinct first-observed clock" if m["operations"]==425 else "source manifest second precision; historical event claim","method":methods[m["operations"]],"raw_witness_in_bundle":True,"sha256":m["sha256"],"source":source["bundle_path"]})
    csvout("p384_reported_history.csv",events,list(events[0]))
    fig,ax=plt.subplots(figsize=(11.4,4.9));fig.subplots_adjust(left=.07,right=.97,top=.73,bottom=.26)
    fig.suptitle("P-384 history: representation changes and selected checkpoints",x=.055,ha="left",y=.97,fontsize=15,fontweight="bold")
    fig.text(.055,.875,"Reported episode sequence; dashed links are chronological, not proven mutation ancestry or a continuous trajectory.",fontsize=9.5)
    xs=list(range(len(events)));ys=[e["operations"] for e in events]
    ax.plot(xs,ys,ls="--",lw=1,color="#a3adb7",zorder=1)
    for i,e in enumerate(events):
        filled=e["raw_witness_in_bundle"]
        ax.scatter(i,e["operations"],s=72,facecolor=BLUE if filled else "white",edgecolor=BLUE if filled else GREY,lw=1.6,zorder=3)
        ax.text(i,e["operations"]+.45,e["label"],ha="center",fontweight="bold",fontsize=10)
        ax.text(i,418.6,e["reported_date"][5:],ha="center",color=GREY,fontsize=8)
    ax.scatter(7.55,421,s=75,marker="D",facecolor=PURPLE,edgecolor=PURPLE,zorder=4)
    ax.annotate("421-B: 381S + 40M\nDiscovery time unknown; known by Sep 28",(7.55,421),xytext=(4.6,429.4),textcoords="data",fontsize=8.5,color=PURPLE,arrowprops={"arrowstyle":"-","color":PURPLE})
    short_labels=["dictionary /\nprefix +\ntail DP","corrected\ndictionary\nprobe","joint\ndictionary-DAG\nMILP","overlap /\ncarry DP","helper /\nweighted\nfrontier","star-prefix +\ntail DP","prefix insertion +\nhelpers","CPU anneal +\ntail DP"]
    ax.set(xlim=(-.4,8),ylim=(418,434),ylabel="Total charged S + M",xticks=xs,xticklabels=short_labels)
    ax.tick_params(axis="x",length=0,labelsize=8);ax.grid(axis="y",alpha=.15)
    fig.text(.07,.775,"Open markers: historical reported counts, exact bytes not recovered here.\nFilled markers: selected original/reconstructed bytes replayed this morning.",fontsize=8.5,color=GREY)
    footer(fig,"Missing: full per-candidate histories and six raw annealing seed logs. 425 report/capture clocks remain distinct. 421-A and 421-B are different DAGs.")
    save(fig,"p384_representation_history")
    mmd=["%% Reconstructed episode order, not a mutation-parent graph.","%% Exact byte identity and event-time claims are separate.","flowchart LR",'  p432["432: dictionary/prefix + exact tail DP<br/>Sep10; reported; bytes not recovered"]','  p429["429 =381S+48M<br/>corrected dictionary probe; reported"]','  p426["426 =380S+46M<br/>joint dictionary-DAG MILP; reported"]']
    for m in milestones:
        op=m['operations'];name='p'+str(op)
        mmd.append(f'  {name}["{op} ={m["squarings"]}S+{m["other_multiplications"]}M<br/>SHA {m["sha256"][:12]}<br/>current exact replay"]')
    seq=['p432','p429','p426','p425','p424','p423','p422','p421']
    for a,b in zip(seq,seq[1:]):mmd.append(f'  {a} -.-> {b}')
    mmd += ['  legend["Dotted edges: reported episode sequence<br/>not proven mutation parents"]','  p421b["421-B =381S+40M<br/>SHA0a8c5bb288ae; exact replay<br/>discovery clock UNKNOWN"]','  target["Same exact P-384 scalar n-2 exponent<br/>No optimality or native-speed claim"]','  p421 -->|"exact exponent equality"| target','  p421b -->|"exact exponent equality"| target','  gap["Missing raw proposal/seed trajectories<br/>Dates are source/run/capture claims as labelled in CSV"]','  gap -.-> p421']
    write("history_and_representation.mmd","\n".join(mmd))


def frontier_plot(manifest,replay):
    byhash={r.get('input_sha256'):r for r in replay['results']}
    chosen=[]
    for target in ['p256','p384','curve25519','p521','secp256k1','curve448-field']:
        rs=[r for r in replay['results'] if r.get('target_id')==target]
        least=min(r['charged']['operations'] for r in rs)
        splits={}
        for r in rs:
            if r['charged']['operations']==least:splits[(r['charged']['S'],r['charged']['M'])]=r
        for (s,m),r in sorted(splits.items()):
            chosen.append({'target_id':target,'label':{'p256':'P-256 scalar n−2','p384':'P-384 scalar n−2','curve25519':'Curve25519 scalar l−2','p521':'P-521 scalar n−2','secp256k1':'secp256k1 scalar n−2','curve448-field':'Curve448 field p−2'}[target],'operations':least,'S':s,'M':m,'input_sha256':r['input_sha256'],'target_hex':r['target_hex'],'domain':manifest['targets'][target]['domain'],'scope':'lowest retained total in this collection; not current-world-best or cross-target runtime ranking'})
    csvout('retained_minimum_counts.csv',chosen,list(chosen[0]))
    fig,ax=plt.subplots(figsize=(10.8,5.4));fig.subplots_adjust(left=.24,right=.95,top=.8,bottom=.15)
    fig.suptitle("Replayable retained witnesses: keep squarings and multiplications separate",x=.055,ha='left',y=.96,fontsize=14,fontweight='bold')
    fig.text(.055,.87,"Lowest retained total for each exact target; equal totals can have different S/M splits. Field and scalar domains differ.",fontsize=9)
    for y,row in enumerate(chosen):
        ax.barh(y,row['S'],color=BLUE,height=.56,label='S: squarings' if y==0 else None)
        ax.barh(y,row['M'],left=row['S'],color=ORANGE,height=.56,label='M: other multiplications' if y==0 else None)
        ax.text(row['operations']+5,y,f"{row['operations']} = {row['S']}S + {row['M']}M",va='center',fontsize=9)
    ax.set(yticks=range(len(chosen)),yticklabels=[x['label'] for x in chosen],xlim=(0,710),xlabel='Charged operations in each certificate (not a speed comparison)')
    ax.invert_yaxis();fig.legend(*ax.get_legend_handles_labels(),frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(.24,.835),fontsize=9);ax.grid(axis='x',alpha=.13);ax.set_axisbelow(True)
    footer(fig,"Current exact positive-integer replay covers identity, references, counts and liveness. It does not establish shortest chains, cryptographic suitability or adoption.")
    save(fig,'retained_witness_counts')


def architecture():
    mmd='''%% Historical source: operator description in the 2026-10-26 chat.
%% Proposal source: inputs/architecture/GENOME-v1.md, 2026-10-23, explicitly PROPOSED.
%% Captured Git blob727f01aa0718014d4c05bc54dcce2330d1765829.
%% Historical reconstruction and proposed unfinished architecture are deliberately separate.
flowchart TB
  subgraph observed["Operator-described historical workflow — reconstruction, not a measured runtime census"]
    tao["Tao: manual direction and coordination"] --> board["Blackboard: tasks, hints, source pointers"]
    board --> workers["Many manually coordinated search/review workers"]
    workers --> reports["Candidate artifacts + reports"]
    reports --> board
    tao --> workers
    reports --> exact["Exact arithmetic replay / selected checks"]
    exact --> manual["Tao gathers evidence and writes email"]
  end
  subgraph proposed["APEX GENOME v1 — explicitly PROPOSED, 2026-10-23; current installation not verified here"]
    genotype["Versioned genotype: identity, laws, role, factories, lane envelope"] -.-> pack["Code builds wake pack: genotype + goals + queue + memory + last5 episodes + scoreboard"]
    persistent["Persistent room conversation; new conversation requires rehydration pack"] -.-> pack
    pack -.-> plan["Apex plans wave and predicts outcomes"]
    plan -.-> work["Code dispatches and gathers receipts + independent checks"]
    work -.-> episode["Code writes episode and ground-truth scoreboard"]
    episode -.-> reflect["Apex reflects in at most5 lines; proposes lessons"]
    reflect -.-> gate["Code promotes lesson after2 checked outcomes agree; retires after2 disagree"]
    gate -.-> memory["Apex-owned memory changes the next wake"]
    memory -.-> pack
    reflect -.-> skill["Skill proposal → A1 champion/challenger check → loaded champion version"]
    skill -.-> pack
    episode -.-> guide["Proof bundle + graphs + write-up guide"]
  end
  manual --> email["Tao handwrites and sends email; email body stays private"]
  guide -.-> email
  hold["Not established by these figures: useful autonomous concurrency, causal agent-skill gains, qualified unattended operation"] -.-> proposed
'''
    write('blackboard_to_apex_proposal.mmd',mmd)
    fig,axes=plt.subplots(1,2,figsize=(11.4,5.3));fig.subplots_adjust(left=.03,right=.98,top=.80,bottom=.15,wspace=.13)
    fig.suptitle("From manual blackboard coordination to an unfinished Apex proposal",x=.055,ha='left',y=.97,fontsize=15,fontweight='bold')
    fig.text(.055,.87,"Left: operator-described history. Right: APEX GENOME v1 (Oct 23, explicitly PROPOSED); dashed arrows are not runtime proof.",fontsize=9)
    for ax in axes:ax.set(xlim=(0,5),ylim=(0,6));ax.axis('off')
    def box(ax,x,y,w,h,text,fc=PALE):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.05,rounding_size=.06',fc=fc,ec='#9ba8b4'))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
    def arrow(ax,a,b,dashed=False):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color=GREY,lw=1.2,linestyle='--' if dashed else '-'))
    ax=axes[0];ax.set_title('Historical blackboard workflow',color=BLUE,fontsize=11)
    box(ax,.5,4.9,4,.7,'Tao: manual coordination')
    box(ax,.5,3.55,4,.7,'Blackboard: tasks, hints, pointers')
    box(ax,.5,2.2,4,.7,'Search / review workers → artifacts')
    box(ax,.5,.85,4,.7,'Selected checks + manual evidence gathering')
    for y in [4.9,3.55,2.2]:arrow(ax,(2.5,y),(2.5,y-.65))
    arrow(ax,(4.5,2.6),(4.5,3.6))
    ax.text(2.5,.18,'Worker counts and resource efficiency are not\nmeasured by this reconstruction.',ha='center',va='center',fontsize=8,color=GREY)
    ax=axes[1];ax.set_title('Apex proposal — unfinished',color=PURPLE,fontsize=11)
    labels=['Versioned genotype + goal / lane envelope','Persistent room + memory + last 5 episodes','Code dispatches → receipts + independent checks','Gated lessons / scoreboard → next wake']
    for y,label in zip([4.9,3.55,2.2,.85],labels):box(ax,.35,y,4.3,.7,label,'#f0e9f5')
    for y in [4.9,3.55,2.2]:arrow(ax,(2.5,y),(2.5,y-.65),True)
    ax.text(2.5,.18,'Proposal: 2 checked outcomes promote a lesson;\n2 disagreements retire it. Installation unverified here.',ha='center',va='center',fontsize=8,color=GREY)
    footer(fig,'Both routes feed evidence for Tao’s handwritten email. These diagrams do not publish or reconstruct private email contents.')
    save(fig,'blackboard_to_apex_proposal')
    write('architecture_source_statement.json',json.dumps({'historical_source':'direct operator message in current local chat, 2026-10-26','historical_statement':'Blackboard architecture with manual coordination of many swarm workers','proposal_source':'inputs/architecture/GENOME-v1.md','proposal_source_sha256':digest(ROOT/'inputs/architecture/GENOME-v1.md'),'proposal_captured_git_blob_sha1':'727f01aa0718014d4c05bc54dcce2330d1765829','proposal_source_repository':'TTaoGaming/sigrun-cloud','proposal_source_ref':'claude/h43-apex-genome-20261023','proposal_statement':'APEX GENOME v1 is explicitly PROPOSED, source dated2026-10-23; current installation not established by this figure','diagram_scope':'operator-described reconstruction plus cited proposal loop; no new architecture implementation or admission'},indent=2))


def serialization_graph(manifest,replay,sources):
    source=next(s for s in sources if s['group']=='p256-episodes' and Path(s['source_path']).name=='RESOURCE_DENOMINATOR_CORRECTION.json')
    assert digest(ROOT/source['bundle_path']) == source['sha256'], 'correction source byte drift'
    correction=load(source['bundle_path'])
    replays={r.get('input_sha256'):r for r in replay['results']}
    seed='cf2f652a6fe1b240cfbeb0ffdf718feeaec2a7ae07875445357035c83ca0eeac'
    graph_hash=replays[seed]['arithmetic_graph_sha256']
    raws=sorted({c['file']['sha256'] for c in correction['cases']})
    text=['%% Verified mapping from six emitted files to four byte hashes to one existing arithmetic DAG.','%% This is artifact identity, not mutation-parent lineage.','flowchart LR']
    table=[]
    for i,c in enumerate(correction['cases']):
        original=Path(c['file']['path']);arm=original.parent.name;sha=c['file']['sha256'];r=replays[sha]
        assert r['arithmetic_graph_sha256']==graph_hash
        text.append(f'  f{i}["{arm}<br/>{original.name}"]')
        text.append(f'  f{i} --> h{raws.index(sha)}')
        table.append({'arm':arm,'filename':original.name,'raw_file_sha256':sha,'arithmetic_graph_sha256':graph_hash,'equals_retained_285_source':True})
    for i,h in enumerate(raws):
        text += [f'  h{i}["Raw bytes SHA {h[:12]}"]',f'  h{i} -->|"current exact replay + canonical exponent triples"| arithmetic']
    text += [f'  arithmetic["ONE arithmetic DAG<br/>285 =252S+33M<br/>graph SHA {graph_hash[:12]}"]',f'  seed["Existing285 source<br/>file SHA {seed[:12]}"]','  seed --> arithmetic','  arithmetic --> novelty["New arithmetic graphs:0<br/>Six files ≠ six discoveries"]']
    write('serialization_vs_arithmetic_identity.mmd','\n'.join(text))
    csvout('serialization_vs_arithmetic_identity.csv',table,list(table[0]))


def morning_replication():
    path=ROOT/'runs/replicated-selection/PAIRED_RESULTS.csv'
    result_path=ROOT/'runs/replicated-selection/RESULT.json'
    if not path.exists() or not result_path.exists():
        return
    result=load('runs/replicated-selection/RESULT.json')
    rows=list(csv.DictReader(path.open(encoding='utf-8')))
    assert result['completed_arms']==16 and result['completed_assessments']==4096 and len(rows)==8
    for row in rows:
        for key in row:row[key]=int(row[key])
        assert row['control_minus_guided']==row['hash_operations']-row['guided_operations']
        for policy,column in [('score_guided','guided_operations'),('hash_control','hash_operations')]:
            record=next(r for r in result['records'] if r['seed']==row['seed'] and r['policy']==policy)
            assert record['assessments']==256 and record['best']['operations']==row[column]
    guided_graphs=len({r['arithmetic_graph_sha256'] for r in result['records'] if r['policy']=='score_guided'})
    control_graphs=len({r['arithmetic_graph_sha256'] for r in result['records'] if r['policy']=='hash_control'})
    fig,axes=plt.subplots(1,2,figsize=(11.4,4.8));fig.subplots_adjust(left=.075,right=.97,top=.78,bottom=.23,wspace=.25)
    fig.suptitle('This morning: a tiny replicated deterministic selection comparison',x=.055,ha='left',y=.97,fontsize=15,fontweight='bold')
    fig.text(.055,.875,'8 paired seeds × 2 policies × 256 assessments = 4,096 scored calls on one exposed P-256 scalar n−2 target.',fontsize=9.5)
    xs=list(range(1,9));guided=[r['guided_operations'] for r in rows];control=[r['hash_operations'] for r in rows];diff=[r['control_minus_guided'] for r in rows]
    axes[0].plot(xs,guided,'o-',color=BLUE,lw=1.6,label='Score-guided package')
    axes[0].plot(xs,control,'s-',color=ORANGE,lw=1.6,label='Hash-control package')
    axes[0].axhline(284,color=GREY,ls='--',lw=1.2,label='Retained incumbent 284')
    axes[0].set(xticks=xs,xticklabels=[str(r['seed'])[-2:] for r in rows],ylim=(280,318),xlabel='Seed suffix (full IDs in CSV)',ylabel='Final best charged S + M',title='All outcomes remained worse than 284')
    axes[0].grid(axis='y',alpha=.15);axes[0].legend(frameon=False,fontsize=8,loc='center left')
    axes[1].bar(xs,diff,color=[BLUE if d else '#bac3cb' for d in diff],width=.58)
    axes[1].scatter([x for x,d in zip(xs,diff) if not d],[0 for d in diff if not d],s=25,facecolor='white',edgecolor=GREY,zorder=3)
    for x,d in zip(xs,diff):axes[1].text(x,d+.12,str(d),ha='center',fontsize=10)
    axes[1].set(xticks=xs,xticklabels=[str(r['seed'])[-2:] for r in rows],ylim=(-.25,4),xlabel='Paired seed suffix',ylabel='Control operations − guided operations',title='5 lower counts / 3 ties / 0 higher counts')
    axes[1].axhline(0,color=GREY,lw=1);axes[1].grid(axis='y',alpha=.15);axes[1].set_axisbelow(True)
    fig.text(.075,.105,f'Final arithmetic DAG identities: guided {guided_graphs}; control {control_graphs}. Seeds are not held-out targets.',fontsize=8.5,color=GREY)
    footer(fig,'Package-level local pilot, not agent skills, memory, cooperation or generalization. Matched call caps are not equal realized CPU. No 284 improvement.')
    save(fig,'morning_selection_replication')
    csvout('morning_selection_replication.csv',rows,list(rows[0]))


def main():
    OUT.mkdir(exist_ok=True)
    manifest=load('inventory/BUNDLE_INPUTS.final.json')
    replay=load('verification/replay-reference.json')
    ablation=load('verification/ABLATION_AUDIT.json')
    memory=load('verification/P521_MEMORY_AUDIT.json')
    sources=load('inventory/EXPERIMENT_SOURCES.v2.json')['sources']
    budget_plot(ablation,memory)
    helper=helper_graph(manifest)
    history_plot(sources,replay)
    frontier_plot(manifest,replay)
    architecture()
    serialization_graph(manifest,replay,sources)
    morning_replication()
    guide='''# Figure guide for the handwritten report

These figures support explanations, not an approved email draft. Research figures contain no email text. Keep any separately restricted checker or held-out sources out of publication.

| Figure | A useful point to explain | Limit to keep in the caption |
|---|---|---|
| [Budgeted controls](../figures/budgeted_policy_controls.png) | Which ordering policy changed outcomes in these exact regions: P-256 guided301 versus hash305; P-521 manually history-guided587 versus control586. | Matched counts are not equal realized compute. One region/seed per historical comparison; no general memory, cooperation or learning claim. |
| [Paid helper](../figures/p256_284_paid_helper.png) | Why helper8415 is charged, and why a topological DAG may drop numerically at row136 without being invalid. | This image contracts the scaffold. The original certificate has284 rows, not17;17 is only this helper's ancestor closure. |
| [P-384 history](../figures/p384_representation_history.png) | Representation changes accompanied the reported432→421 checkpoint sequence. | Dashed links are chronological reconstruction, not proven mutation ancestry. Full candidate trajectories and six raw seed logs are missing. The later421-B is a distinct witness. |
| [Retained counts](../figures/retained_witness_counts.png) | Exact targets and S/M splits matter; equal totals do not make identical DAGs. | This is the retained collection, not a world-best census or cross-curve speed ranking. Curve448 is field p−2; others are scalar n−2/l−2. |
| [Coordination](../figures/blackboard_to_apex_proposal.png) | Describe the actual human-coordinated blackboard process separately from the unfinished Apex proposal. | Operator-described reconstruction is not a measured runtime census. Dashed proposed gates are not implementation or qualification evidence. |
| [This morning's tiny replication](../figures/morning_selection_replication.png) | Across8 paired seeds, guided returned312; controls312–315:5 lower counts,3 ties,0 higher counts under256 calls/arm. | One exposed target and very small budgets; repeated arithmetic identities occur. This is a deterministic selection-package effect, not an agent-skill, memory, collaboration, held-out transfer or frontier-improvement claim. |

Each rendered figure has an editable SVG and a matching PNG. Rebuild with `python -B tools/render_figures.py` from the bundle root. This uses local Matplotlib, no network or source search. CSV files hold exact plotted data. Full DAG edges and row order are available in `figures/p256_284_full_dag.csv`, `.dot`, and `.mmd`; `p256_284_helper8415.mmd` contains the exact17-operation ancestor closure.

Mermaid files: `history_and_representation.mmd`, `blackboard_to_apex_proposal.mmd`, and `serialization_vs_arithmetic_identity.mmd`, plus the two exact DAG Mermaid files. The artifact-identity map verifies that six emitted files/four byte hashes were one already available285 DAG, with zero new arithmetic graphs. It is not a mutation-parent graph.

The proposed architecture is grounded in the actual `inputs/architecture/GENOME-v1.md`, source dated2026-10-23 and explicitly marked PROPOSED, captured Git blob `727f01aa0718014d4c05bc54dcce2330d1765829`. It distinguishes stable genotype, persistent conversation/memory, code-written episodes and scoreboard, checked lesson promotion/retirement, and skill champion/challenger selection. The figure does not establish that these proposal components have been installed.

Clock handling: the history CSV retains raw reported clocks and precision. The425 record preserves a Sep10 reported run separately from the manifest's Sep21 first-observed/capture field. P-384421-B discovery time remains UNKNOWN, bounded by its later receipt; it is not assigned the421-A annealing seed or timestamp. The history figure uses categorical episode order, not elapsed time. Current replay time belongs to validation, not discovery.

Provenance: `inventory/BUNDLE_INPUTS.final.json` pins exact target/witness bytes; `verification/replay-reference.json` supplies current arithmetic counts; `verification/ABLATION_AUDIT.json` and `verification/P521_MEMORY_AUDIT.json` bind the historical traces. `figures/FIGURE_MANIFEST.json` records their SHA-256 values and all generated outputs.
'''
    (ROOT/'report-support/FIGURE_GUIDE.md').write_text(guide,encoding='utf-8',newline='\n')
    inputs=['inventory/BUNDLE_INPUTS.final.json','verification/replay-reference.json','verification/ABLATION_AUDIT.json','verification/P521_MEMORY_AUDIT.json','inventory/EXPERIMENT_SOURCES.v2.json','inputs/architecture/GENOME-v1.md']
    for p in ['runs/replicated-selection/PAIRED_RESULTS.csv','runs/replicated-selection/RESULT.json']:
        if (ROOT/p).exists():inputs.append(p)
    generated=[p for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='FIGURE_MANIFEST.json']
    out={'schema':'addition-chain-figure-set.v1','created_utc':datetime.now(timezone.utc).isoformat(),'renderer_sha256':digest(Path(__file__)),'input_sha256':{p:digest(ROOT/p) for p in inputs},'helper_current_replay_structure':helper,'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':digest(p)} for p in generated],'scope':'historical traces + current arithmetic + explicitly unfinished proposal; no model/provider/search execution','visual_QA':'rendered artifacts require reviewer inspection; this field does not claim inspection before it occurs'}
    write('FIGURE_MANIFEST.json',json.dumps(out,indent=2))
    size=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())+Path(__file__).stat().st_size+(ROOT/'report-support/FIGURE_GUIDE.md').stat().st_size
    if size>2_000_000:raise SystemExit('OUTPUT_BUDGET_EXCEEDED '+str(size))
    print(json.dumps({'figure_pngs':len(list(OUT.glob('*.png'))),'figure_svgs':len(list(OUT.glob('*.svg'))),'mermaids':len(list(OUT.glob('*.mmd'))),'output_bytes_including_code_and_guide':size,'helper_ancestry':helper}))


if __name__=='__main__':main()
