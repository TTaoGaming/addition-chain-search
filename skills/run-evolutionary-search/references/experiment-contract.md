# Experiment contract and run receipt

Complete before launch. A field marked `UNKNOWN` is not permission to infer
it. Keep this in the existing project record rather than creating a new
control plane.

```text
Objective and named consumer:
Target ID, exact bytes/hash, and scalar/field domain:
Incumbent certificate/program hash and measured score:
Engine, installed version, candidate representation, seed:
Prior engine locator (repo/ref/path/command/hash), access check, and prior checkpoint:
Generator/model/provider/account/quota pool, if applicable:
Current route admission/availability and quota or resource-budget receipt:
Immutable evaluator path/hash, validity gates, and score direction:
Training cases visible to the proposer:
Held-out commitment/hash, independent custodian, and verifier route only
  (never put the held-out inputs in the proposer-visible record):
Maximum iterations, concurrency, wall time, output bytes, and spend:
Allowed effects, safe execution boundary, and stop reason:
Output directory and independent verifier:
```

After the run append: UTC start/end; exact command/config hash; engine log and
candidate hashes; configured iterations and actual evaluations separately;
counts proposed/invalid/scored/unique/selected; baseline and
selected scores; held-out verdict; cost and resource observations; reason for
stop; what a downstream consumer actually accepted; previous receipt
superseded, if any. Preserve generator source, selected genotype, output
certificate, and raw trajectory as separately addressable artifacts. If the
engine was never
invoked, record `ENGINE_NOT_RUN` and the first failed gate. If it was invoked
but generated no distinct evaluated candidate, record `ENGINE_INVOKED=YES`,
`DISTINCT_EVALUATED_CHILD=NO`, and the failed gate. A candidate receipt is
not a native performance or adoption receipt.
