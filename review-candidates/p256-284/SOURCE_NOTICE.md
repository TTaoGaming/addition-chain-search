# Sources and review rights

This directory extends the repository's review-only materials. No new reuse license is granted for the project certificate, generator, checker, test harness, research prose or measurements. The MIT terms in `chains/` and `skills/` do not automatically cover this directory. Publication enables inspection and does not imply upstream acceptance or endorsement.

The mathematical certificate was produced by the project's AI-assisted search and is retained byte-for-byte under SHA-256 `46ba0fb4a02926e02aad7c51cb9c41225952a5549e4c0012964f2de5ad15d148`. Its format uses the existing `hfo.addition_chain_dag.v0` schema tag solely for parser compatibility. The separate exact checker validates arithmetic and charged operations; hashes do not certify authorship.

Copied ring source is an explicit exception to the project's review-only notice: its original upstream permissions remain unchanged. `upstream_p256.rs`, the context in the production patch, generated replacement source and saved baseline in the test module derive from Brian Smith's ring source at commit `840167e18e4fa837eb48de46500454a616a15a6e`. The original source header is retained. `LICENSE-ring-source.txt` and `licenses/ring/` retain the relevant upstream notices. Those notices do not license unrelated new project materials.

No third-party library binary or dependency source tree is distributed. Native reproduction fetches the pinned ring checkout and its locked dependencies under their respective licenses. Public comparison references link to their original primary sources; their articles are not reproduced. This review contains no private correspondence or private-source access requirement.
