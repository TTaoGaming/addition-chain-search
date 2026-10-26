"""Add one cohort PNG/SVG; preserve all accepted primary files byte-for-byte."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;R=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SRC='analysis/COHORT_RESULTS.json';AUD='oracle/COHORT_AUDIT.v1.json'
EXPECTED='af5d20326c3df76ddca47f4dc5cd8fb3861a270d662877b22639c8330da954ac'
AUDHASH='a953bfe29797675b2561b2c9955bcbe8ac8477b453fef2721ae850c1323161bb'
def main():
    frozen={p.name:sha(p) for p in H.glob('primary_*') if p.is_file()}
    frozen['FIGURE_RECEIPT.json']=sha(H/'FIGURE_RECEIPT.json')
    assert sha(R/SRC)==EXPECTED and sha(R/AUD)==AUDHASH
    d=json.loads((R/SRC).read_text());a=json.loads((R/AUD).read_text())
    assert a['producer_result_sha256']==EXPECTED and a['verdict']=='VERIFICATION_PASS_COHORT_WITH_BROWSER_EXCLUSION_CONFIRMED'
    assert a['all_cloned_prefixes_byte_identical'] and a['all_runtime_prompts_match_declared_own_peer_masks']
    assert d['totals']['actual_model_calls']==24 and d['totals']['actual_candidate_evaluations_initial_once']==908
    assert d['rows']==a['rows'] and len(d['pairs'])==4 and len(d['rows'])==8
    by={(r['pair_id'],r['arm']):r for r in d['rows']}
    pairs=sorted(d['pairs'],key=lambda p:(p['task_id'],p['replicate_id']))
    for p in pairs:
        priv=by[(p['pair_id'],'private')];shared=by[(p['pair_id'],'shared')]
        assert priv['state']==shared['state']=='COMPLETED'
        assert priv['best_valid_cost']==shared['best_valid_cost'] and priv['best_identity']==shared['best_identity']
        assert shared['duplicate_evaluations']-priv['duplicate_evaluations']==p['duplicate_evaluations_shared_minus_private']
        for row in (priv,shared):assert row['duplicate_evaluations']+row['unique_schedules']==row['branch_evaluations_including_common_initial']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'cohort-supplement-v1','text.color':'#25313c'})
    fig,axes=plt.subplots(2,3,figsize=(16,8.8));blue='#235789';orange='#c46627'
    panels=[('Best valid charged cost','best_valid_cost'),('Duplicate candidate records','duplicate_evaluations'),('Between-worker schedule overlap','between_worker_schedule_overlap'),('New second-round regions','new_second_regions_over_team_initial'),('Branch-accounted evaluations','branch_evaluations_including_common_initial')]
    for ax,(title,key) in zip(axes.flat,panels):
        maximum=max(r[key] for r in d['rows']);limit=maximum*1.65
        for y,p in enumerate(pairs):
            pr=by[(p['pair_id'],'private')];sh=by[(p['pair_id'],'shared')];x1=pr[key];x2=sh[key]
            ax.plot([x1,x2],[y-.07,y+.07],color='#b2bbc3',lw=1.5,zorder=1)
            ax.scatter(x1,y-.07,s=58,facecolor='white',edgecolor=blue,lw=1.5,zorder=3)
            ax.scatter(x2,y+.07,s=45,facecolor=orange,edgecolor=orange,zorder=4)
            ax.text(maximum*1.10,y,f'{x1} → {x2}',ha='left',va='center',fontsize=11)
        ax.set_title(title,loc='left',fontsize=12,pad=14)
        ax.set_yticks(range(4),[('20b' if '20-' in p['task_id'] else '23b')+' · r'+str(p['replicate_id']) for p in pairs]);ax.set_ylim(3.6,-.6);ax.set_xlim(0,limit)
        ax.set_xticks([0,round(maximum*.5),maximum]);ax.grid(axis='x',color='#eef0f2');ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        ax.set_xlabel('Private → shared (raw counts)')
    ax=axes.flat[5];ax.axis('off');ax.set_title('Actual execution ≠ copied branch accounting',loc='left',fontsize=12,pad=14)
    ax.text(0,.96,'Actual execution\n24 model calls = 8 initial + 16 second\n908 evaluations = 86 initial + 822 second',va='top',fontsize=11,linespacing=1.5)
    ax.text(0,.56,'Both branch views include the same prefix\n32 branch-accounted decisions; 994 evaluations\nThe reused 86 initial evaluations are not new work.',va='top',fontsize=11,linespacing=1.5)
    ax.text(0,.17,'Audit replay: 1,080 materialized records, including clones.\nAll 8 branches complete; no missing/failed branch.\nBoth workers’ second actions changed in all 4 pairs.',va='top',fontsize=10,linespacing=1.5)
    fig.suptitle('Two-worker peer-observation cohort: cost and allocation',x=.045,ha='left',fontsize=18,y=.995)
    fig.text(.045,.935,'Open blue: private own history. Filled orange: own + peer first action/feedback. All four paired costs and best identities tied.',fontsize=11)
    fig.text(.045,.015,'Two exposed tasks × 2 repeat/order IDs; unmatched second-decision model randomness. Same actual first work cloned into both branches.\nDuplicates and overlap are schedule-based counts, not independent discoveries; fewer duplicates can accompany less realized work. Tiny descriptive sharing pilot, not full Apex autonomy.',fontsize=10)
    fig.subplots_adjust(top=.82,bottom=.16,left=.07,right=.98,hspace=.58,wspace=.50)
    name='supplement_cohort_allocation'
    fig.savefig(H/(name+'.png'),dpi=150,bbox_inches='tight')
    fig.savefig(H/(name+'.svg'),bbox_inches='tight',metadata={'Title':'Paired two-worker cohort: cost and allocation','Description':'All four raw pairs, separate cost and allocation metrics; actual work distinct from cloned accounting.','Date':None});plt.close(fig)
    (H/'COHORT_PLOT_DATA.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    assert frozen=={k:sha(H/k) for k in frozen}
    files=[H/(name+ext) for ext in ('.png','.svg')]+[Path(__file__),H/'COHORT_PLOT_DATA.json']
    receipt={'schema':'cohort-figure-supplement.v1','created_utc':datetime.now(timezone.utc).isoformat(),'state':'RENDERED_PENDING_VISUAL_QA','source_pins':{s:sha(R/s) for s in [SRC,'analysis/COHORT_RESULTS.csv',AUD,'COHORT_PROTOCOL.v1.json']},'preserved_primary_pins':frozen,'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'plots_total_bytes':sum(p.stat().st_size for p in H.iterdir() if p.is_file())}
    (H/'SUPPLEMENT_COHORT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    assert receipt['plots_total_bytes']<4000000
    print(json.dumps({'state':receipt['state'],'plots_total_bytes':receipt['plots_total_bytes']}))
if __name__=='__main__':main()
