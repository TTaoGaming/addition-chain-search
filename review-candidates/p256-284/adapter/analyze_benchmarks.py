#!/usr/bin/env python3
"""Summarize observed paired durations without dropping outliers."""
import csv, json, random, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'receipts'
lines=(R/'microbenchmark.log').read_text().splitlines()
(R/'microbenchmark.csv').write_text('kind,round,order,iterations,baseline_ns,candidate_ns\n'+'\n'.join(x for x in lines if x.startswith('scalar_inverse,'))+'\n')

def q(xs,p):
 x=sorted(xs);i=(len(x)-1)*p;j=int(i);f=i-j
 return x[j]*(1-f)+x[min(j+1,len(x)-1)]*f

def summarize(path):
 rows=list(csv.DictReader(path.open()))
 assert rows and all(int(r['iterations'])>0 and int(r['baseline_ns'])>0 and int(r['candidate_ns'])>0 for r in rows)
 assert [int(r['round']) for r in rows]==list(range(len(rows)))
 ratios=[int(r['candidate_ns'])/int(r['baseline_ns']) for r in rows]
 b=[int(r['baseline_ns'])/int(r['iterations']) for r in rows]
 c=[int(r['candidate_ns'])/int(r['iterations']) for r in rows]
 rng=random.Random(284)
 boots=[statistics.median(rng.choices(ratios,k=len(ratios))) for _ in range(20000)]
 ci=[q(boots,.025),q(boots,.975)]
 return {'file':str(path.name),'pairs':len(rows),'iterations_per_batch':int(rows[0]['iterations']),
         'baseline_median_ns_per_op':statistics.median(b),'candidate_median_ns_per_op':statistics.median(c),
         'median_paired_candidate_over_baseline':statistics.median(ratios),
         'median_paired_latency_reduction_pct':100*(1-statistics.median(ratios)),
         'paired_ratio_p10_p90':[q(ratios,.1),q(ratios,.9)],
         'paired_ratio_bootstrap_median_95pct':ci,
         'candidate_faster_pairs':sum(r<1 for r in ratios),
         'ratio_by_order':{o:statistics.median([int(r['candidate_ns'])/int(r['baseline_ns']) for r in rows if r['order']==o]) for o in ['BC','CB']},
         'all_observations_retained':True,
         'interpretation':'candidate faster in this run' if ci[1]<1 else ('candidate slower in this run' if ci[0]>1 else 'inconclusive: median ratio interval includes 1')}
result={'micro':summarize(R/'microbenchmark.csv'),'ecdsa_sign':summarize(R/'sign_benchmark.csv'),
        'method':'20,000 deterministic nonparametric bootstrap resamples of paired C/B ratios; median and percentile interval; no outlier removal; intervals describe these samples only and do not remove shared-host/temporal dependence or code-layout confounding'}
(R/'benchmark_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
