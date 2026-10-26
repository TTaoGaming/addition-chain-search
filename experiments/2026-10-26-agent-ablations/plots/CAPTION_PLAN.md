# Primary-v2 plotting plan — no outcome claims yet

Input release: root-owned `analysis/PRIMARY_RESULTS.json` and CSV, using only `runs/v2`. The retained first v1 integration trajectory and integration-smoke data are excluded. No result figure exists at this scaffold checkpoint.

1. **All raw paired costs:** one plotted pair per task × replicate for each prespecified contrast. Show both costs and their difference; missing/censored values remain labelled missing, never zero. Use distinct task markers and replicate IDs. N−B is a name-framing contrast; backend B(Luna)−B(Sol) gets a separate panel. M−I tests relevance under approximate length control; O−M tests the order of identical memory facts. Keep M−B and A−B in a separately labelled exploratory display.
2. **Action and region choices:** a task × replicate facet with each condition's three actual action decisions, construction family and region identity. Distinguish direct submission, construct, search, refusal and missing round. Compare action/region changes separately from valid best cost. Region identity and candidate identity must use the root's definitions, not model prose or filenames.
3. **Duplicates and refusals:** show actual numerator/denominator values per trajectory; a trajectory with no candidate is NA for candidate-duplicate rate. Keep repeated-region actions, repeated candidate schedules, invalid proposals and refused actions separate.
4. **Completion and realized evaluations:** show every planned assignment as completed, failed, censored/partial or unstarted, plus realized evaluation counts per task × replicate. A common maximum of64 evaluations/action does not imply equal realized evaluations or CPU. Keep proposal-round, generator-evaluation and verifier-check units distinct.

Primary descriptive unit: task. Two tasks each have two trajectory replicate IDs. Replicate IDs control ordering/repetition; they are not controlled model RNG seeds. Forty assignments do not become40 independent tasks. Show all four raw pairs for each primary contrast, no task-general significance or narrow inferential confidence interval from these two tasks.

Name framing is not Apex actor admission. A requested/configured model label is not an independent serving-family census. Own research can be shared; no email bodies, credentials or restricted checker material belongs in plots. The architecture remains outside these experimental outcomes.

Planned output: PNG + editable SVG for each result chart, plotted CSV extracts, local renderer source, captions with denominators/limitations, and SHA-256/visual-QA receipt. No Slack/GitHub publication by this lane. The4MB plot allocation is inside the existing8MB report/control cap.
