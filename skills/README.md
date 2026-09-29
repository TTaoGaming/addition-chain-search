# Agent Skills for verifiable search

MIT-licensed public edition, 2026-09-29 UTC. These five small skills are written
for any agent that can read Markdown and use the tools available in its own
environment. A client with Agent Skills support can load an individual
`SKILL.md`; another agent can be given that file and only its relevant
reference as task context. Copying a folder does not prove that an agent loaded
it, ran an engine, or produced a useful result.

## General search and research handoff

| Skill | Plain-language use |
| --- | --- |
| [`run-evolutionary-search`](run-evolutionary-search/SKILL.md) | Run the named optimizer against a frozen evaluator and report what it actually evaluated. |
| [`report-search-frontier`](report-search-frontier/SKILL.md) | Show searched and unsearched regions, failed attempts, and evidence limits. |
| [`package-reproducible-research`](package-reproducible-research/SKILL.md) | Prepare an independently checkable, privacy-screened handoff. |

## Addition-chain-specific checks

| Skill | Plain-language use |
| --- | --- |
| [`verify-addition-chain`](verify-addition-chain/SKILL.md) | Check a chain's exact target, arithmetic, operation counts, and negative controls. |
| [`compare-chain-costs`](compare-chain-costs/SKILL.md) | Compare a chain with a pinned published or implementation baseline without calling counts speed. |

The skills specify evidence boundaries, not a model, provider, scheduler, or
permission grant. An agent should run the requested engine if its route and
evaluator are safe and available; it must say `ENGINE_NOT_RUN` if they are not.
Do not substitute a hand-picked or shuffled candidate list and call it a
named-engine run. The separate `01_addition_chains_r4.zip` (SHA-256
`e850af310dc732eba5329692987e6ce43fcc15e8186c1c691cf47f9c1fd0ac4e`)
contains the actual certificates, checker code, method notes, attribution,
and MIT-covered original material; it is not embedded in any standalone skill.
These skills contain no credentials or private correspondence. Tao approved
publishing the five new skills under MIT; [LICENSE](LICENSE) and the per-skill
copies carry that grant. See [REUSE_TERMS.md](REUSE_TERMS.md) for the exact scope.
This public edition is part of the addition-chain-search repository.

Read [LESSONS.md](LESSONS.md) for the bounded cases that motivated the skills.
