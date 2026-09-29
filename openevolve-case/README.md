# Bounded P-384 scalar OpenEvolve case study

Public review edition, 2026-09-29 UTC. This is a small data-only adapter
and a negative-result case study, **not** a virtual-actor harness, background
service, or bundled copy of OpenEvolve. It targets the P-384 scalar subgroup
order `n−2`, not the field-prime inversion exponent.

`seed.json` is a 71-byte genome. Trusted `decoder.py` expands four helper
selectors into an exact-target addition-chain certificate; candidate JSON is
never executed as Python. `evaluator.py` supplies OpenEvolve's scoring ABI.
`independent_verify.py` replays certificate arithmetic, dependencies,
liveness, and modular powers without importing the decoder. `selftest.py`
rebuilds the seed and tests invalid mutations plus 100 distinct valid
one-gene certificates. The offline selftest uses only Python's standard
library and may take around two minutes on a typical desktop:

```text
python -B selftest.py
```

The sanitized [candidate ledger](candidate_ledger.jsonl) lists all 17
reported child genomes, parent pointers, counts, and certificate hashes.
Replay each one with the separate verifier and a tampered-hash control:

```text
python -B replay_ledger.py --selftest
```

This confirms arithmetic and the internal consistency of the shared ledger;
it does **not** authenticate the omitted engine trace, model responses, or
timing. The ledger labels iteration 6 of the last run as sourced from the
private engine log and checkpoint because its trace row is missing.

`config_v2.yaml` and `prompt_v2/full_rewrite_user.txt` show the bounded
OpenEvolve 0.3.2 local-Ollama setup used for the final diversity probe. They
contain a loopback URL and a dummy `ollama` API-key placeholder, not a
credential. The named engine, model, wall-limit supervisor, and recipient's
resource controls are **not** bundled. Do not treat a successful import or
config load as an engine run. If adapting this example, bind the exact model
route, enforce your own wall and resource limits, and independently replay
every selected certificate. The sample config enables prompt/trace logging;
keep that output private or disable it for sensitive inputs. The five portable
Agent Skills in the adjacent package give the full evidence contract.

[RESULTS.md](RESULTS.md) reports what actually happened, including failed
integration, model collapse, prompt diversity, the trace/checkpoint mismatch,
and the unchanged 421-operation incumbent. This archive omits raw private
logs, personal paths, email, and correspondence. Source-file hashes are in
`SHA256SUMS.txt`; source-level replay is not a claim of native speed,
shortest-chain optimality, deployment, or recipient acceptance.

[REUSE_TERMS.md](REUSE_TERMS.md) states the review-only permission boundary.
The separate chain-certificate archive carries its own provenance. A public
background reference for addition-chain cost comparison is
[Brian Smith's *ECC Inversion Addition Chains*](https://briansmith.org/ecc-inversion-addition-chains-01);
no code from that article is bundled here, and this mention does not imply
endorsement.
