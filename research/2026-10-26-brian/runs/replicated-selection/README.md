# Replicated selection comparison — 26 October 2026

This is a finite comparison of two existing deterministic selection packages on the full, historically exposed P-256 scalar-order `n-2` target. It is not an agent-skill, collaboration, autonomous-memory, or held-out-target experiment.

The preregistration and input pins were written before execution. Eight fixed seeds used the unchanged corrected engine, beam width 16 and 256 assessment calls per arm. Arm order alternated by seed. All 16 arms completed; no failed or censored arms were dropped. Raw compressed rows, original producer results, final certificates and current replay records remain in each seed folder.

Guided selection won five pairs, tied three and lost none. Control-minus-guided differences were `[3,0,1,2,3,0,0,1]`; the median was 1 operation. The best emitted certificate had 312 operations, so none improved on the retained 284. Seven distinct arithmetic graphs occurred across 16 saved certificate files. Every arm had215 unique precompute states among 256 assessment calls.

All 16 final certificates passed exact target, dependency, charge, liveness and modular replay. A separate forward dynamic program also checked all 4,096 saved score assessments. The search/verification/audit run measured 1.9375 process CPU seconds; the later saved-run validation measured 1.421875 process CPU seconds. These boundaries exclude other report preparation, model work and unmetered host activity. Matched assessment limits are not a claim of equal realized CPU.

To verify the saved run, from the bundle root:

```text
python -B runs/replicated-selection/validate_saved_replication.py
```

This writes a new validation receipt and preserves earlier observations. To explicitly perform one fresh replication in a new child directory:

```text
python -B report-support/tools-and-ablations/reproduce_replication.py
```

The reproduction uses the same seeds, frozen source engine and current separate verifier identity. A changed verifier pin causes a hold rather than a silent rerun under a different oracle. Timestamps, process IDs and compressed-file hashes can differ; compare semantic results and exact arithmetic graph identities. The original producer retains legacy `below_291` counter names; the new experiment's frontier comparator is284.

`FILE_MANIFEST.json` pins files that existed at initial result finalization. The bundle's final manifest covers the subsequent policy audit, validation and documentation too. `PREREGISTRATION.json`, `PRE_RUN_PIN.json` and the original `run_replication.py` are immutable run inputs; do not edit them to make a result pass.
