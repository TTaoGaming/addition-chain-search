#!/usr/bin/env python3
"""Alternate baseline/candidate processes; timings exclude spawn/key setup/warmup."""
import argparse, csv, datetime, os, subprocess, sys
p = argparse.ArgumentParser()
p.add_argument('baseline')
p.add_argument('candidate')
p.add_argument('--iterations', type=int, default=2000)
p.add_argument('--rounds', type=int, default=31)
a = p.parse_args()
w = csv.writer(sys.stdout)
w.writerow(['kind','round','order','iterations','baseline_ns','candidate_ns'])
for i in range(a.rounds):
    values = {}
    order = [('baseline', a.baseline), ('candidate', a.candidate)]
    if i % 2:
        order.reverse()
    for label, path in order:
        out = subprocess.check_output([path, str(a.iterations)], text=True).strip()
        values[label] = int(out)
    w.writerow(['ecdsa_p256_sign', i, 'BC' if i % 2 == 0 else 'CB', a.iterations, values['baseline'], values['candidate']])
    sys.stdout.flush()
