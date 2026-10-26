# Independent support review of the Brian addition-chain bundle

Verdict: **PASS for the independently replayed arithmetic; two reproducibility fixes recommended.** No arithmetic or charge discrepancy was found in the three pinned originals or the other 89 explicit exponent-triple witnesses replayed here. This is a support review by a separate Codex agent, not an admitted Apex contribution or a held-out verifier receipt.

## Exact target and pinned results

The target contracts use subgroup scalar orders, with exponent n-2. P-256 modulus is `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551`, and the exact target is `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc63254f`. P-384 modulus is `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973`, and the exact target is `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52971`. These are pinned bundle contracts; this review did not fetch an external parameter standard.

| Original SHA-256 | Target | Charged operations | Live operations |
|---|---|---:|---:|
| `46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148` | P-256 scalar n-2 | 284 = 251S + 33M | 284 |
| `844866b0703ef55ca41fc616a7226fe6d8aca3022ead18cdaec1e0911422e02e` | P-384 scalar n-2 | 421 = 380S + 41M | 421 |
| `0a8c5bb288aefb494e64dfa793e9e9b8ca1e162dcbc6c79ae6a6015ee089b518` | P-384 scalar n-2 | 421 = 381S + 40M | 421 |

Base exponent 1 is the only uncharged seed. Each triple [v,a,b] has positive integer parents available before its row and satisfies v=a+b exactly. Every serialized row is charged, with S for equal parents and M otherwise. Backward ancestry from the exact final exponent reaches the seed. All three pinned schedules are strictly increasing, have no repeated output exponents, and have no dead rows. The tied 421-operation totals have different S/M splits; neither establishes a timing improvement.

## Independent replay and tests

The tiny `independent_core.py` was authored and SHA-256 frozen at `2026-10-26T15:41:55.9797454Z` before reading `tools/verify_bundle.py`. Its unchanged SHA-256 is `c5fa8a0fc340c13445cae75a37e6f46af8c617eb29da518f821c22271c6cc419`. The mathematical rules and expected key counts were already in the assignment, and some existing replay metadata had been inspected. This was a separate implementation, not a blind experiment.

`run_independent.py` checked **92 explicit exponent-triple originals** and verified the manifest byte pins for **all 121 originals**. It skipped 29 index/named-operation encodings; their arithmetic was not independently replayed in this review. For all 92, charged totals and liveness match the existing primary replay. Its node indices are 1-based; the independent core reports 0-based row indices. One first-run assertion exposed that representation difference; the comparison was corrected without changing the arithmetic core. The primary replay also preserves two certificates with dead rows, rather than discounting their serialized charges.

The frozen core passed three positive fixtures and rejected 14 invalid fixtures covering wrong sums, missing/forward ancestry, invalid seed values, booleans, floats, malformed rows, truncation, and an exact-target mismatch despite congruence. Fifteen further semantic mutants across the three pinned originals were rejected, and three newline mutations failed their original-byte hashes. The additional pinned mutants were defined after inspecting the primary source; they ran against the unchanged pre-inspection core. These are synthetic tamper controls, not private held-out material.

## Actionable findings

1. **PROOF-REPRO-1 / P2 — the default replay uses an older manifest.** `tools/verify_bundle.py:251` defaults to `BUNDLE_INPUTS.v2.json` with 119 originals. The requested v3 contains 121. Running without `--manifest inventory/BUNDLE_INPUTS.v3.json` omits `p521-ad9da1620b44` and `p521-b1e966bebfa4`. Require the manifest explicitly, or update the default and bind its hash in instructions. The supplied v3 replay already uses the intended manifest, so this does not invalidate its 121 results.

2. **PROOF-REPRO-2 / P2 — exit success does not guarantee complete coverage.** The unsupported-format branch at line 259 records HOLD and continues; the return condition at line 289 does not fail for HOLD. A bounded probe containing one valid original and one unsupported, nonexistent certificate returned exit 0 with `PASS_EXACT_ARITHMETIC:1` and `HOLD_ENCODING_NOT_IMPLEMENTED:1`. Return nonzero for incomplete coverage, or add an explicit coverage gate. This is a future-input failure mode; the actual v3 has no unsupported entries.

Two optional hardening probes were also accepted: a malformed present `target=True` field is ignored, and adding valid `steps` makes an inconsistent `rows` representation ignored. The computed pinned exponent remains correct in both probes. A schema-specific encoding allowlist and rejection of conflicting explicit representations would make the metadata contract clearer. Neither probe demonstrates an incorrect exponent accepted for the actual pinned originals.

## Scope and claim limits

The current primary verifier checks exact parent sums, earlier references, byte hashes, declared count fields, target agreement, live ancestry, and all serialized charges. No material mathematical blind spot was found for the reviewed triple encodings. Its eight semantic controls exercise a triple re-encoding of one certificate; they do not independently test every source-format adapter. The 29 skipped index/named encodings and adapter completeness remain outside this independent replay.

The arithmetic graph digest is explicitly a sorted exponent-triple multiset with unordered parents, not a complete index-labeled graph isomorphism proof. Keep that scope when discussing novelty or duplicate graphs. No search was rerun; no frozen search-region minimum, global optimality, native timing, novelty, cryptographic security, consumer acceptance, deployment, or Apex admission is certified here.

Independence ceiling: separate agent/sample and authored arithmetic code path, **same configured model family**. No independent human, provider-family quorum, privileged held-out oracle, or admitted Apex actor was used. No email body, credential, protected checker/evaluation bundle, source workspace, Gen137 runtime, external service, or judged file was changed or opened for this review. All writes stayed under `reviews/proof/`.

## Receipts

- `CORE_FREEZE.json`: pre-inspection core hash and scope.
- `independent-replay.json`: 92 complete per-input results, 29 explicit skips, target and code hashes, fixture controls.
- `key-tamper.json`: 15 semantic and three byte-pin tamper controls.
- `verifier-probes.json`: exact commands and results for the reproduced robustness gaps.
- `REVIEW_RECEIPT.json`: command ledger and code/input/output hashes.
