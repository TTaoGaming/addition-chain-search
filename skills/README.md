# Agent Skills for verifiable search

MIT-licensed public edition, 2026-09-29 UTC. These five small skills are written
for any agent that can read Markdown and use the tools available in its own
environment. A client with Agent Skills support can load an individual
`SKILL.md`; another agent can be given that file and only its relevant
reference as task context. Copying a folder does not prove that an agent loaded
it, ran an engine, or produced a useful result.

| Skill | Use it when |
| --- | --- |
| `run-evolutionary-search` | Asked to run an actual named engine or a specified evolutionary algorithm |
| `verify-addition-chain` | Given a scalar- or field-inversion chain certificate to check |
| `report-search-frontier` | Reporting what a bounded search found or ruled out |
| `compare-chain-costs` | Comparing an exact chain with a published or implementation baseline |
| `package-reproducible-research` | Handing code, certificates, results, or negative evidence to another person |

The skills specify evidence boundaries, not a model, provider, scheduler, or
permission grant. An agent should run the requested engine if its route and
evaluator are safe and available; it must say `ENGINE_NOT_RUN` if they are not.
Do not substitute a hand-picked or shuffled candidate list and call it a
named-engine run. The separate `01_addition_chains_r3.zip` (SHA-256
`ac3f8d2b34ee1324f3c99f75bb5777ad63cb56496cef60531c348b3598816553`)
contains the actual certificates, checker code, method notes, attribution,
and MIT-covered original material; it is not embedded in any standalone skill.
These skills contain no credentials or private correspondence. Tao approved
publishing the five new skills under MIT; [LICENSE](LICENSE) and the per-skill
copies carry that grant. See [REUSE_TERMS.md](REUSE_TERMS.md) for the exact scope.
This public edition is part of the addition-chain-search repository.

Read [LESSONS.md](LESSONS.md) for the bounded cases that motivated the skills.
