"""Standalone primary-v2 PNG/SVG figures from audited frozen data.
Run: python -B plots/render_primary.py --render
Writes only plots/. No network, model calls or source edits.
"""
import argparse, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
KEYS=('task_id','replicate_id','cell_id','model')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

from collections import Counter
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch

EXPECTED='5d884748187c90fb7413a9ba17e65103955ea736ad142da26826945c93f75ac8'
SOURCES=['analysis/PRIMARY_RESULTS.json','analysis/PRIMARY_RESULTS.csv','oracle/PRIMARY_AUDIT.v1.json',
 'PROTOCOL.v1.json','control/EXECUTION_FREEZE.v1.json','control/INTERFACE_AMENDMENT.v2.json',
 'control/STIMULUS_AMENDMENT.v1.json','control/RUNNER_SCOPE_AMENDMENT.v3.json']
BLUE='#235789'; ORANGE='#c46627'; PURPLE='#725285'; INK='#25313c'
FAMILY={'search:window':('SW','#c5d8e7'),'search:dictionary':('SD','#ecd0b6'),
 'submit_chain:explicit':('EX','#d8cce2'),'construct:binary':('CB','#d6dcc5')}
LABELS={'name_only':('N − B','Name-only framing'),'skill_packet':('S − B','Operative skill packet'),
 'memory_relevance':('M − I','Relevant vs irrelevant memory'),'memory_order':('O − M','Order of the same facts'),
 'search_tools_absent':('T − B','Construction/search tools absent'),
 'verifier_feedback_withheld':('V − B','Verifier feedback withheld'),
 'combined_exploratory':('A − B','Bundled changes · exploratory'),
 'actual_backend_luna_minus_sol':('B Luna − B Sol','Configured backend · separate')}
ORDER=['B','N','S','I','M','O','T','V','A','Luna']; TASKS=['synthetic-20-v1','synthetic-23-v1']
def dump(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def cell(r): return 'Luna' if r['model']=='gpt-6-luna' else r['cell_id']
def pk(p): return p['task_id'],p['replicate_id']
def pairlabel(p): return ('20b' if '20-' in p['task_id'] else '23b')+' · r'+str(p['replicate_id'])

def load_verified():
    p=ROOT/SOURCES[0]
    assert sha(p)==EXPECTED, 'Frozen result hash changed'
    d=json.loads(p.read_text(encoding='utf-8-sig')); audit=json.loads((ROOT/SOURCES[2]).read_text())
    assert audit['producer_result_sha256']==sha(p) and audit['producer_csv_sha256']==sha(ROOT/SOURCES[1])
    assert audit['verdict']=='VERIFICATION_PASS_SCOPED_PRIMARY_WITH_CENSORING_NOTES'
    assert d['all40terminal'] and d['analysis_partition']=='runs/v2' and len(d['rows'])==40
    assert len({tuple(r[k] for k in KEYS) for r in d['rows']})==40
    assert Counter(r['state'] for r in d['rows'])=={'COMPLETED':39,'TIMEOUT':1}
    assert sum(r['realized_evaluations'] for r in d['rows'])==3098
    assert all(r['valid_candidates']==r['realized_evaluations'] for r in d['rows'])
    assert all(r['duplicate_candidates']+r['unique_schedule_count']==r['valid_candidates'] for r in d['rows'])
    assert len(d['contrasts'])==8 and all(len(c['pairs'])==4 for c in d['contrasts'])
    by_id={r['trajectory_id']:r for r in d['rows']}
    for c in d['contrasts']:
        for pair in c['pairs']:
            t=by_id[pair['treatment_id']]; b=by_id[pair['control_id']]
            assert pair['cost_treatment']==t['best_valid_cost'] and pair['cost_control']==b['best_valid_cost']
            assert pair['cost_delta_treatment_minus_control']==t['best_valid_cost']-b['best_valid_cost']
            assert pair['action_sequence_changed']==(t['action_sequence']!=b['action_sequence'])
            assert pair['action_families_changed']==(t['action_family_sequence']!=b['action_family_sequence'])
            for key,col in [('unique_regions_delta','unique_regions'),('duplicates_delta','duplicate_candidates'),('evaluations_delta','realized_evaluations')]:
                assert pair[key]==t[col]-b[col], (c['contrast'],pk(pair),key)
    return d

def save(fig,name,title,description):
    fig.savefig(HERE/(name+'.png'),dpi=150,bbox_inches='tight')
    fig.savefig(HERE/(name+'.svg'),bbox_inches='tight',metadata={'Title':title,'Description':description,'Date':None})
    plt.close(fig)

def cost_pairs(d):
    fig,axes=plt.subplots(2,4,figsize=(15.4,7.5),sharex=True)
    for ax,c in zip(axes.flat,d['contrasts']):
        code,label=LABELS[c['contrast']]; pairs=sorted(c['pairs'],key=pk)
        ax.axvline(0,color='#7b8790',lw=1)
        for y,p in enumerate(pairs):
            delta=p['cost_delta_treatment_minus_control']; partial=p['treatment_state']!='COMPLETED' or p['control_state']!='COMPLETED'
            ax.plot([0,delta],[y,y],color='#afb7be',lw=1.5,zorder=1)
            ax.scatter(delta,y,s=65,marker='D' if partial else 'o',facecolor='white' if partial else BLUE,edgecolor=BLUE,linewidth=1.6,zorder=3)
            ax.text(2.35,y,f"{p['cost_control']} → {p['cost_treatment']}"+(' †' if partial else ''),va='center',ha='left',fontsize=10)
        ax.set_yticks(range(4),[pairlabel(p) for p in pairs]); ax.set_ylim(3.65,-.65); ax.set_xlim(-2.7,4.0)
        ax.set_xticks([-2,-1,0,1,2]); ax.grid(axis='x',color='#eef0f2',lw=.7)
        ax.set_title(code+'\n'+label,loc='left',pad=12,color=PURPLE if 'backend' in c['contrast'] else INK)
        ax.set_xlabel('Δ additions (treatment − control)');ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    fig.suptitle('Best valid cost: every paired task × replicate',x=.04,ha='left',fontsize=17,y=1.00)
    fig.text(.04,.935,'Two synthetic tasks; two repeat/order IDs per task. Negative Δ is a lower operation count. Right labels show control → treatment.',fontsize=10)
    fig.text(.04,.015,'† Open diamond: best valid prefix from the T/20b/r2 timeout; later decisions are censored.\nNo confidence intervals: repeats are not controlled model RNG seeds; this pilot has two tasks, not 40 independent tasks. Primary runs/v2 only.',fontsize=10)
    fig.subplots_adjust(top=.82,bottom=.16,left=.07,right=.99,hspace=.75,wspace=.45)
    save(fig,'primary_paired_costs','Primary paired cost results','Eight separately labeled contrasts; all four raw pairs, exact costs and timeout prefix retained.')

def behavior_pairs(d):
    cs=d['contrasts'];pairs=[sorted(c['pairs'],key=pk) for c in cs]
    fig,axes=plt.subplots(1,4,figsize=(17.4,7.5),sharey=True)
    for ax,title,key in zip(axes,['Exact action / family changed','Δ unique generator regions','Δ duplicate candidate records','Δ realized evaluations'],[None,'unique_regions_delta','duplicates_delta','evaluations_delta']):
        if key:
            vals=np.array([[p[key] for p in ps] for ps in pairs]);lim=max(abs(vals.min()),abs(vals.max()),1)
            ax.imshow(vals,cmap='PuOr_r',vmin=-lim,vmax=lim,aspect='auto',alpha=.32)
        else:
            vals=np.array([[int(p['action_families_changed']) for p in ps] for ps in pairs])
            ax.imshow(vals,cmap=ListedColormap(['#e7edf1','#c8d8e5']),vmin=0,vmax=1,aspect='auto')
        for i,ps in enumerate(pairs):
            for j,p in enumerate(ps):
                text=('Y / '+('Y' if p['action_families_changed'] else 'N')) if not key else f'{p[key]:+d}'
                if p['treatment_state']!='COMPLETED' or p['control_state']!='COMPLETED':text+=' †'
                ax.text(j,i,text,ha='center',va='center',fontsize=11)
        ax.set_title(title,loc='left',pad=15);ax.set_xticks(range(4),['20b r1','20b r2','23b r1','23b r2']);ax.xaxis.tick_top();ax.tick_params(length=0)
        ax.set_yticks(range(8),[LABELS[c['contrast']][0] for c in cs]);ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,8,1),minor=True)
        ax.grid(which='minor',color='white',lw=2);ax.tick_params(which='minor',length=0)
        for spine in ax.spines.values():spine.set_visible(False)
    fig.suptitle('Behavior and search work: paired changes, separately from cost',x=.04,ha='left',fontsize=17,y=.99)
    fig.text(.04,.91,'All 32 exact action sequences changed. Family changes, distinct regions, duplicate schedules and work counts are different measurements.',fontsize=10)
    fig.text(.04,.03,'Signed values are treatment − control; color intensity is scaled separately in each metric panel. Y / N compares exact actions, then coarse action families.\nRegions use exact method + normalized knobs. Duplicates use commutative parent-index schedules, preserving row order/multiplicity/output. † Censored prefix pair.',fontsize=10)
    fig.subplots_adjust(top=.79,bottom=.15,left=.13,right=.99,wspace=.18)
    save(fig,'primary_paired_behavior','Primary paired behavior and work','Action/family changes and signed region, duplicate and evaluation changes; all raw pairs.')

def raw_trajectories(d):
    fig,axes=plt.subplots(1,2,figsize=(16,11.4))
    for ax,task in zip(axes,TASKS):
        rows=sorted([r for r in d['rows'] if r['task_id']==task],key=lambda r:(ORDER.index(cell(r)),r['replicate_id']))
        ax.set_xlim(-.5,7.2);ax.set_ylim(19.8,-1.9);ax.axis('off')
        for j,h in enumerate(['Decision\n1','Decision\n2','Decision\n3','Cost','Evals','Regions','Dup / valid']):ax.text(j,-1.05,h,ha='center',va='center',fontsize=10,fontweight='bold')
        for i,r in enumerate(rows):
            ax.text(-.6,i,cell(r)+' r'+str(r['replicate_id'])+(' †' if r['state']!='COMPLETED' else ''),ha='right',va='center',fontsize=10)
            if i%2==0:ax.axhspan(i-.47,i+1.47,color='#f7f8f9',zorder=0)
            for j in range(3):
                if j<len(r['action_family_sequence']):t,color=FAMILY[r['action_family_sequence'][j]]
                elif j<r['attempted_rounds']:t,color='TIMEOUT','#edd3b2'
                else:t,color='—','#f0f1f3'
                ax.add_patch(Rectangle((j-.44,i-.39),.88,.78,facecolor=color,edgecolor='white',lw=1));ax.text(j,i,t,ha='center',va='center',fontsize=9)
            vals=[r['best_valid_cost'],r['realized_evaluations'],r['unique_regions'],f"{r['duplicate_candidates']} / {r['valid_candidates']}"]
            for j,t in enumerate(vals,start=3):ax.text(j,i,str(t),ha='center',va='center',fontsize=10)
        ax.set_title('20-bit target 750339 · binary baseline 28' if '20-' in task else '23-bit target 7162463 · binary baseline 35',loc='left',fontsize=13,pad=15)
    fig.legend(handles=[Patch(facecolor=v[1],label=v[0]+': '+k.replace(':',' ')) for k,v in FAMILY.items()],loc='lower center',ncol=4,bbox_to_anchor=(.51,.055),frameon=False,fontsize=10)
    fig.suptitle('All 40 trajectories: actions, best valid cost and realized search work',x=.05,ha='left',fontsize=17,y=.99)
    fig.text(.05,.012,'B,N,S,I,M,O,T,V,A use gpt-6.1-sol; Luna is a separate gpt-6-luna baseline. Cell definitions are in CAPTION_GUIDE.md.\n† T/20b/r2: decision 2 timed out after one valid 24-operation submission; decision 3 was unstarted. Zero invalid candidate records and zero refused actions in primary v2.',fontsize=10)
    fig.subplots_adjust(top=.91,bottom=.14,left=.10,right=.99,wspace=.18)
    save(fig,'primary_raw_trajectories','All primary trajectories','Raw decision families, costs, evaluations, unique regions and duplicate/valid denominators for40 terminal trajectories.')

def budget_completion(d):
    fig=plt.figure(figsize=(15.6,7.8));gs=fig.add_gridspec(1,3,width_ratios=[.75,1.45,1.45])
    ax=fig.add_subplot(gs[0]);work=fig.add_subplot(gs[1]);dup=fig.add_subplot(gs[2],sharey=work)
    ax.barh(1.85,39,color=BLUE,height=.25);ax.barh(1.85,1,left=39,color='#d8af7c',height=.25)
    ax.text(19.5,1.85,'39',va='center',ha='center',color='white',fontsize=13);ax.text(40,2.07,'1 timeout',va='center',ha='right',fontsize=10)
    ax.set_xlim(0,40);ax.set_yticks([]);ax.set_xlabel('Planned trajectories');ax.set_title('Terminal status',loc='left',pad=25)
    ax.text(0,.68,'40 planned\n39 complete\n1 timed out\n0 other failures\n0 unstarted trajectories',transform=ax.transAxes,va='top',fontsize=11,linespacing=1.65)
    ax.text(0,.25,'119 / 120 decisions attempted\n118 / 119 attempts returned\n3,098 exact evaluations\n3,098 valid candidate records\n0 native tool events',transform=ax.transAxes,va='top',fontsize=10,linespacing=1.5)
    ax.set_ylim(-.4,2.2);ax.grid(axis='x',color='#eef0f2');ax.spines['left'].set_visible(False)
    offsets={(TASKS[0],1):-.18,(TASKS[0],2):-.06,(TASKS[1],1):.06,(TASKS[1],2):.18}
    for r in d['rows']:
        y=ORDER.index(cell(r))+offsets[(r['task_id'],r['replicate_id'])];color=BLUE if r['task_id']==TASKS[0] else ORANGE
        marker='D' if r['state']!='COMPLETED' else ('o' if r['replicate_id']==1 else 's');face='none' if r['replicate_id']==2 or r['state']!='COMPLETED' else color
        for a,x in [(work,r['realized_evaluations']),(dup,r['duplicate_fraction'])]:a.scatter(x,y,s=52,marker=marker,facecolor=face,edgecolor=color,lw=1.5,zorder=3)
    work.axvline(192,color='#78848d',ls='--',lw=1);work.set_xlim(-3,202);work.set_xticks([0,64,128,192]);work.set_xlabel('Realized exact candidate evaluations');work.set_title('Realized work',loc='left',pad=25)
    dup.set_xlim(-.03,1.03);dup.set_xticks([0,.25,.5,.75,1],['0','25%','50%','75%','100%']);dup.set_xlabel('Duplicate / valid candidate records');dup.set_title('Schedule duplication',loc='left',pad=25)
    for a in (work,dup):a.set_yticks(range(10),ORDER);a.set_ylim(9.6,-.6);a.grid(axis='x',color='#e9edf0');a.tick_params(axis='y',length=0)
    fig.suptitle('The common decision cap did not produce equal realized work',x=.045,ha='left',fontsize=17,y=.98)
    fig.text(.045,.905,'Every task × replicate point is shown. Blue:20b; orange:23b. Circles:r1; open squares:r2; open diamond:censored T/20b/r2 prefix.',fontsize=10)
    fig.text(.045,.035,'192 is an upper bound (3 decisions ×64 search candidates), not a required workload. Explicit submissions and constructions evaluate fewer candidates.\nDuplicate fractions count repeated schedules among valid candidate records; identity is narrower than general DAG isomorphism. Primary runs/v2 only; no browser or v1 pooling.',fontsize=10)
    fig.subplots_adjust(top=.82,bottom=.16,left=.065,right=.99,wspace=.35)
    save(fig,'primary_budget_completion','Primary completion and realized work','Failure/censoring counts, every realized evaluation point and duplicate/valid fractions with common-cap context.')

def render_main():
    p=argparse.ArgumentParser(description='Render standalone primary-v2 PNG/SVG figures from independently audited frozen data.');p.add_argument('--check-inputs',action='store_true');p.add_argument('--render',action='store_true');a=p.parse_args()
    d=load_verified()
    if not a.render:print(json.dumps({'state':'PASS_FROZEN_AUDITED_INPUTS','rows':len(d['rows'])}));return
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'text.color':INK,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'brian-primary-v2-frozen','savefig.facecolor':'white'})
    for fn in (cost_pairs,behavior_pairs,raw_trajectories,budget_completion):fn(d)
    dump('PLOT_DATA.json',{'source_sha256':EXPECTED,'analysis_partition':d['analysis_partition'],'rows':d['rows'],'contrasts':d['contrasts'],'definitions':d['definitions'],'totals':d['totals']})
    files=sorted(p for p in HERE.iterdir() if p.is_file() and p.name not in ['FIGURE_RECEIPT.json','VISUAL_QA.json']);size=sum(p.stat().st_size for p in HERE.iterdir() if p.is_file());assert size<4000000
    dump('FIGURE_RECEIPT.json',{'schema':'primary-figures.v1','created_utc':datetime.now(timezone.utc).isoformat(),'state':'RENDERED_PENDING_VISUAL_QA','source_pins':{s:sha(ROOT/s) for s in SOURCES},'renderer_sha256':sha(Path(__file__)),'figures':['primary_paired_costs','primary_paired_behavior','primary_raw_trajectories','primary_budget_completion'],'rows':40,'independent_tasks':2,'repeat_ids':[1,2],'complete':39,'censored_timeout':1,'scope_cap_bytes':4000000,'bytes_before_receipt':size,'source_mutations':[],'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]})
    print(json.dumps({'state':'RENDERED_PENDING_VISUAL_QA','bytes':sum(p.stat().st_size for p in HERE.iterdir() if p.is_file())}))

if __name__=='__main__':render_main()
