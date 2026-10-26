# Figure guide for the handwritten report

These figures support explanations, not an approved email draft. Research figures contain no email text. Keep any separately restricted checker or held-out sources out of publication.

| Figure | A useful point to explain | Limit to keep in the caption |
|---|---|---|
| [Budgeted controls](../figures/budgeted_policy_controls.png) | Which ordering policy changed outcomes in these exact regions: P-256 guided301 versus hash305; P-521 manually history-guided587 versus control586. | Matched counts are not equal realized compute. One region/seed per historical comparison; no general memory, cooperation or learning claim. |
| [Paid helper](../figures/p256_284_paid_helper.png) | Why helper8415 is charged, and why a topological DAG may drop numerically at row136 without being invalid. | This image contracts the scaffold. The original certificate has284 rows, not17;17 is only this helper's ancestor closure. |
| [P-384 history](../figures/p384_representation_history.png) | Representation changes accompanied the reported432→421 checkpoint sequence. | Dashed links are chronological reconstruction, not proven mutation ancestry. Full candidate trajectories and six raw seed logs are missing. The later421-B is a distinct witness. |
| [Retained counts](../figures/retained_witness_counts.png) | Exact targets and S/M splits matter; equal totals do not make identical DAGs. | This is the retained collection, not a world-best census or cross-curve speed ranking. Curve448 is field p−2; others are scalar n−2/l−2. |
| [Coordination](../figures/blackboard_to_apex_proposal.png) | Describe the actual human-coordinated blackboard process separately from the unfinished Apex proposal. | Operator-described reconstruction is not a measured runtime census. Dashed proposed gates are not implementation or qualification evidence. |
| [This morning's tiny replication](../figures/morning_selection_replication.png) | Across8 paired seeds, guided returned312; controls312–315:5 lower counts,3 ties,0 higher counts under256 calls/arm. | One exposed target and very small budgets; repeated arithmetic identities occur. This is a deterministic selection-package effect, not an agent-skill, memory, collaboration, held-out transfer or frontier-improvement claim. |

Each rendered figure has an editable SVG and a matching PNG. Rebuild with `python -B tools/render_figures.py` from the bundle root. This uses local Matplotlib, no network or source search. CSV files hold exact plotted data. Full DAG edges and row order are available in `figures/p256_284_full_dag.csv`, `.dot`, and `.mmd`; `p256_284_helper8415.mmd` contains the exact17-operation ancestor closure.

Mermaid files: `history_and_representation.mmd`, `blackboard_to_apex_proposal.mmd`, and `serialization_vs_arithmetic_identity.mmd`, plus the two exact DAG Mermaid files. The artifact-identity map verifies that six emitted files/four byte hashes were one already available285 DAG, with zero new arithmetic graphs. It is not a mutation-parent graph.

The proposed architecture is grounded in the actual `inputs/architecture/GENOME-v1.md`, source dated2026-10-23 and explicitly marked PROPOSED, captured Git blob `727f01aa0718014d4c05bc54dcce2330d1765829`. It distinguishes stable genotype, persistent conversation/memory, code-written episodes and scoreboard, checked lesson promotion/retirement, and skill champion/challenger selection. The figure does not establish that these proposal components have been installed.

Clock handling: the history CSV retains raw reported clocks and precision. The425 record preserves a Sep10 reported run separately from the manifest's Sep21 first-observed/capture field. P-384421-B discovery time remains UNKNOWN, bounded by its later receipt; it is not assigned the421-A annealing seed or timestamp. The history figure uses categorical episode order, not elapsed time. Current replay time belongs to validation, not discovery.

Provenance: `inventory/BUNDLE_INPUTS.v3.json` pins exact target/witness bytes; `verification/replay-20261026T153224-425600300.json` supplies current arithmetic counts; `verification/ABLATION_AUDIT.json` and `verification/P521_MEMORY_AUDIT.json` bind the historical traces. `figures/FIGURE_MANIFEST.json` records their SHA-256 values and all generated outputs.
