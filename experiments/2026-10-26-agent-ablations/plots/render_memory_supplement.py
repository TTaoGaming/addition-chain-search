"""One frozen episode-memory supplement; no changes to primary/cohort artifacts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;R=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SRC='analysis/EPISODE_MEMORY_RESULTS.json';AUD='oracle/MEMORY_AUDIT.v1.json'
EXPECTED='99a15f538bdf37b0c39bd340ace13140936d59e8e55e6cc3834641ba0aea2b8a'
AH='46efbf6867aaef1b0e52744983c98db21abf10066f0e720a4919e3a355e98d92'
def main():
    preserve=[p for p in H.glob('primary_*') if p.is_file()]+[H/n for n in ['FIGURE_RECEIPT.json','SUPPLEMENT_COHORT_RECEIPT.json','SUPPLEMENT_COHORT_QA.json','supplement_cohort_allocation.png','supplement_cohort_allocation.svg','COHORT_PLOT_DATA.json','COHORT_CAPTION.md','render_cohort_supplement.py']]
    frozen={p.name:sha(p) for p in preserve}
    assert sha(R/SRC)==EXPECTED and sha(R/AUD)==AH
    d=json.loads((R/SRC).read_text());a=json.loads((R/AUD).read_text());rows=d['rows']
    assert a['producer_result_sha256']==EXPECTED and a['producer_csv_sha256']==sha(R/'analysis/EPISODE_MEMORY_RESULTS.csv')
    assert a['verdict']=='VERIFICATION_PASS_MEMORY_AND_COMBINED_LOGICAL_CLAIMS_WITH_SCOPED_LIMITS'
    assert len(rows)==12 and all(r['state']=='COMPLETED' for r in rows)
    assert sum(r['realized_evaluations'] for r in rows)==939 and sum(r['attempted_rounds'] for r in rows)==36
    assert sum(r['evaluations_matching_supplied_retained_schedule'] for r in rows)==73
    assert sum(r['direct_submissions_matching_supplied_retained'] for r in rows)==6
    assert sum(r['strict_cost_improvement_over_current_source'] for r in rows)==3
    assert sum(r['strict_cost_improvement_over_full_primary'] for r in rows)==0
    by={r['trajectory_id']:r for r in rows}
    for c in d['contrasts']:
        for p in c['pairs']:
            t=by[p['treatment_id']];b=by[p['control_id']]
            assert p['cost_delta_treatment_minus_control']==t['best_valid_cost']-b['best_valid_cost']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'episode-memory-supplement-v1','text.color':'#25313c'})
    fig=plt.figure(figsize=(16,10.4));gs=fig.add_gridspec(2,3,height_ratios=[1,1.55])
    titles=['W − U: same-target vs other-target episode','W − C: same-target episode vs cold','U − C: other-target episode vs cold']
    for ax,c,title in zip([fig.add_subplot(gs[0,i]) for i in range(3)],d['contrasts'],titles):
        ps=sorted(c['pairs'],key=lambda p:(p['task_id'],p['replicate_id']))
        ax.axvline(0,color='#7b8790',lw=1)
        for y,p in enumerate(ps):
            delta=p['cost_delta_treatment_minus_control'];ax.plot([0,delta],[y,y],color='#b6bec6',lw=1.5)
            ax.scatter(delta,y,s=55,color='#235789',zorder=3)
            ax.text(1.45,y,f"{p['cost_control']} → {p['cost_treatment']}",va='center',fontsize=11)
        ax.set_title(title,loc='left',fontsize=12,pad=14);ax.set_xlim(-1.35,2.75);ax.set_ylim(3.6,-.6);ax.set_xticks([-1,0,1])
        ax.set_yticks(range(4),[('20b' if '20-' in p['task_id'] else '23b')+' · r'+str(p['replicate_id']) for p in ps]);ax.grid(axis='x',color='#eef0f2');ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        ax.set_xlabel('Δ additions (treatment − control)')
    tableax=fig.add_subplot(gs[1,:2]);tableax.axis('off');tableax.set_title('Every trajectory: outcome, comparator and allocation',loc='left',pad=12,fontsize=12)
    ordered=sorted(rows,key=lambda r:(r['task_id'],r['replicate_id'],['C','U','W'].index(r['cell_id'])))
    cells=[]
    for r in ordered:
        label=('20b' if '20-' in r['task_id'] else '23b')+' r'+str(r['replicate_id'])+' '+r['cell_id']
        cells.append([label,r['best_valid_cost'],r['current_target_source_incumbent'],r['full_primary_incumbent'],r['realized_evaluations'],r['unique_regions'],f"{r['duplicate_candidates']} / {r['valid_candidates']}",r['evaluations_matching_supplied_retained_schedule'],r['direct_submissions_matching_supplied_retained']])
    cols=['Task / cell','Best\ncost','Source\nincumbent','Full primary\nfrontier','Evals','Unique\nregions','Dup / valid','Eval matches\ncertificate','Direct submit\nmatches']
    tab=tableax.table(cellText=cells,colLabels=cols,cellLoc='center',colWidths=[.14,.07,.10,.11,.07,.08,.12,.14,.14],bbox=[0,0,1,1]);tab.auto_set_font_size(False);tab.set_fontsize(10)
    for (i,j),entry in tab.get_celld().items():
        entry.set_edgecolor('white')
        if i==0:entry.set_facecolor('#dce5ec');entry.set_text_props(weight='bold',fontsize=9)
        else:entry.set_facecolor('#f2f5f7' if ((i-1)//3)%2==0 else 'white')
    notes=fig.add_subplot(gs[1,2]);notes.axis('off');notes.set_title('What the denominators show',loc='left',pad=12,fontsize=12)
    notes.text(0,.98,'12 complete trajectories\n36 actual calls; 939 exact evaluations\n0 failed/censored trajectories',va='top',fontsize=11,linespacing=1.6)
    notes.text(0,.73,'Same current-target source incumbent\nfor W, U and C: 24 / 31\nFull primary frontier: 24 / 29\n3 source-relative improvements\n0 full-frontier improvements',va='top',fontsize=11,linespacing=1.6)
    notes.text(0,.37,'73 matching candidate evaluations\n6 matching direct submissions\n\nMatching can include deterministic-tool\nrediscovery. These are different counts;\nneither proves a model’s copy mechanism.',va='top',fontsize=11,linespacing=1.55)
    fig.suptitle('Recorded search-episode memory: paired costs and retained-schedule matches',x=.04,ha='left',fontsize=17,y=.995)
    fig.text(.04,.945,'W: same-target source episode + retained certificate. U: truthful other-target episode. C: no episode. Skill, tools and final oracle held constant.',fontsize=11)
    fig.text(.04,.015,'Two exposed tasks × 2 repeat/order IDs; unmatched model randomness. Packet lengths differ (313 / 356 words); this is explicit context provision, not autonomous retrieval or persistent learning.\nPositive Δ is worse. Different schedule hashes do not establish new arithmetic graphs or global novelty. All source/full-primary comparators are current-target quantities.',fontsize=10)
    fig.subplots_adjust(top=.84,bottom=.16,left=.065,right=.98,hspace=.40,wspace=.34)
    name='supplement_episode_memory';fig.savefig(H/(name+'.png'),dpi=150,bbox_inches='tight')
    fig.savefig(H/(name+'.svg'),bbox_inches='tight',metadata={'Title':'Recorded episode memory supplement','Description':'All12raw trajectories and12paired contrasts; source/full-frontier comparators and matching/direct-submission counts separated.','Date':None});plt.close(fig)
    (H/'MEMORY_PLOT_DATA.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    assert frozen=={n:sha(H/n) for n in frozen}
    files=[H/(name+ext) for ext in ('.png','.svg')]+[Path(__file__),H/'MEMORY_PLOT_DATA.json']
    source_paths=[SRC,'analysis/EPISODE_MEMORY_RESULTS.csv',AUD,'EPISODE_MEMORY_PROTOCOL.v1.json','control/EPISODE_MEMORY_FREEZE.v1.json']
    out={'schema':'memory-figure-supplement.v1','created_utc':datetime.now(timezone.utc).isoformat(),'state':'RENDERED_PENDING_VISUAL_QA','source_pins':{s:sha(R/s) for s in source_paths},'preserved_primary_pins':frozen,'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'plots_total_bytes':sum(p.stat().st_size for p in H.iterdir() if p.is_file())}
    (H/'SUPPLEMENT_MEMORY_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');assert out['plots_total_bytes']<4000000
    print(json.dumps({'state':out['state'],'plots_total_bytes':out['plots_total_bytes']}))
if __name__=='__main__':main()
