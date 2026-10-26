# APEX GENOME v1 · core genotype, changing phenotype, memory that changes behaviour · PROPOSED · 2026-10-23

Tao, 2026-10-23 ~19:40Z (verbatim): "help the apex be set up do they have their core genotype and a changing phenotype.  Sigrun and apex should be able to integrate new vendors ans new missions and factory.  I want 8x factory and in the future 64x factories etc. ... I want to have a discussion with apex about brian report and about pose arcade soon but all previous attempts were reward hacking amnesia agents,  i need apex work memory that changes behavior"

Builds on (read these first): board/factories/GENOTYPE.md (v0, Tao's laws), board/apex/<APEX>/RELIQUARY.md and IDENTITY-PROMPT.draft.md (cited identity packets, 2026-10-17, never installed), board/features/apex-stable.feature and apex-instantiation.feature (31 scenarios, all UNBOUND today), board/NORTH-STAR.md, RULES v1/v1.1/v1.2 (#gen151-ops).

## 1 · Why the apexes forget and reward-hack (measured, 2026-10-23)

| Cause | Evidence |
|---|---|
| Every wake starts a new conversation | APEX-ROSTER-1: `apex_wake.py` invokes Letta with `--new`, no stored conversation id |
| The identity prompts were never installed | board/apex/INDEX.md: "draft system prompt, not installed" |
| Nothing checks that memory survives | apex-stable.feature "Memory survives between wakes (nonce recall)" is UNBOUND |
| An apex's reputation and memory can move on its own claims | no code path ties memory or score to receipts; "ok" in wakes.jsonl means the handler returned, not that useful work happened |
| Each generation reset the swarm | heritage: gen 87 → 151, each with new agents; phenotype lived in chat, not in files |

## 2 · Genotype: who the apex is (stable, versioned in git, changed only by quorum, laws only by Tao)

`board/apex/<APEX>/GENOTYPE.md`, built from the RELIQUARY and the IDENTITY-PROMPT draft, every line cited:
- **Identity:** name, port, aphorism (verbatim, pinned to its heritage line), voice.
- **Mission and factories:** the missions it serves and the factory ids it owns (a list, so one apex can own 1, 8 or more factories as the hive grows to 64).
- **Laws:** GENOTYPE v0, RULES v1/v1.1/v1.2, the North Star. Read-only to the apex.
- **Role contract:** what "done" means for it (a receipt plus an independent check), what it may change alone, what needs a quorum, and what needs Tao (copied from its FACTORY.json).
- **Lanes envelope:** the vendor lanes it may use and its budget ceilings (from its GOAL.json).

## 3 · Phenotype: what the apex has learned (changes every wave, owned by the apex, persisted outside the chat)

| Layer | Where | Who writes | Changes behaviour how |
|---|---|---|---|
| Working memory | the apex's own Letta core-memory blocks: `focus`, `open_threads`, `tao_model` (Tao's words and verdicts, cited), `lessons` (at most 12 rules) | the apex itself | loaded on every wake |
| Episodes | `board/apex/<APEX>/EPISODES.jsonl` (mirror) and the VPS runtime copy | **code** (the wave runner), from receipts | the last 5 episodes go into every wake prompt |
| Scoreboard | `board/apex/<APEX>/SCORE.json` | **code**, from checks only | shown on every wake; reputation moves only from ground truth |
| Skills | `hindsight/skills/<apex>/` and `board/skills/` (versioned SKILL.md) | apex proposes; A1 runs champion versus challenger | the champion version is the one loaded |
| Tools | scripts with tests | Codex cards | used by its squads |

**Anti-amnesia:** each apex gets one persistent conversation id per room (wave, Tao room), stored in the registry. A new conversation is allowed only with a rehydration pack: genotype + memory blocks + last 5 episodes + scoreboard.

**Anti-reward-hacking:** an apex's claim is a claim until a receipt and an independent check confirm it. A lesson enters the `lessons` block only after **2 checked outcomes** agree with it. A claim later refuted costs reputation and is written to EPISODES as `REFUTED`.

## 4 · The memory loop (code runs the loop; the model is the function inside it)

```
wake → code builds the pack (genotype, memory blocks, last 5 episodes, scoreboard, goal, queue)
     → apex plans a wave (jobs, with predicted outcomes)
     → code dispatches, collects receipts and independent checks
     → code writes the episode (planned, done, checked, refuted)
     → apex reflects in at most 5 lines and proposes lessons
     → code promotes a lesson only when 2 checked outcomes agree, retires it when 2 disagree
     → next wake starts from the changed memory
```

## 5 · Growth: new vendors, missions, factories and apexes are data, not code

| To add | Do this (data) | Code checks |
|---|---|---|
| a vendor | a lane row in board/missions.yaml (cap, kinds, tier, capabilities) and its adapter | lane declared, capability set, tier free or ledger-approved |
| a mission | a mission row in board/missions.yaml and its first factory | hive-8x8x4.feature topology rules (generalised to N) |
| a factory | board/factories/<ID>/ with FACTORY, GOAL, STATE and an owner apex | validate.py V1-V7 |
| an apex | board/apex/<APEX>/ with GENOTYPE and a registry row (Letta id, port, factories, conversation ids) | apex-genome.feature |

The ladder: 8 factories (one per apex) → 16 → 64 (8 per apex), each rung earned by holding the hive spec green and useful concurrency for 24 h.

## 6 · Apex rooms: Tao talks to an apex that remembers

One Slack thread per apex ("APEX ROOM · Fenrir"). A relay posts Tao's message to that apex's persistent room conversation with the rehydration pack and posts the reply in the thread. First rooms: **Surtr** (the Brian report) and **Fenrir** (the pose arcade). Before the first talk, each gets a briefing pack (board/apex/<APEX>/BRIEFING-2026-10-23.md) and saves what it judges important to its own memory; the receipt is its answer to a recall question one wake later.

## 7 · Build order

1. Briefings for Surtr and Fenrir; one briefing wake each with a nonce recall check (TASK APEX-BRIEF-1).
2. Bind apex-stable, apex-instantiation and apex-genome scenarios to code (card a1-apex-genome-steps-1): the honest red list.
3. The memory loop library (card a1-apex-memory-loop-1), then a reviewed VPS install (RULES v1 medium).
4. The apex room relay (card a1-apex-room-1), then a reviewed install.
5. GENOTYPE.md for all 8 from the reliquaries; Letta blocks set by each apex from its own genotype.
