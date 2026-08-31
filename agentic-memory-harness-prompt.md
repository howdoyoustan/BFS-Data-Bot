# Agentic Memory Harness — Design Notes + Master Prompt

Saved from planning session. Use the master prompt on the **work machine** (where TELOS, Lavish, and the enterprise gotchas index actually live).

---

## What’s the point of TELOS now?

**As always-on agent context: almost none.** That’s the clog you’re feeling. Progressive disclosure (Claude-Mem, Hermes 3-tier, Agent Skills) and Open Brain (SQL + MCP you own) beat “dump MISSION/BELIEFS/PROJECTS every session.” Even LifeOS/PAI itself separates **MEMORY** from **TELOS** — the anti-pattern is `LoadContext` injecting the life OS into every chat.

**As a human intentionality layer: still useful — if thin and opt-in.** Keep TELOS only for:

- Who you are / what you’re optimizing for (mission, values)
- Active life/work *portfolio* (standup buckets, personal projects, research threads)
- Planning sessions where you *want* Ideal State vs Current State

Don’t keep it for enterprise gotchas, tool edges, or session learnings — those belong in an **index → fetch** memory lane.

**Practical verdict:** TELOS becomes a **callable Life OS skill**, not your agent’s RAM. If you never open `/telos` except for standup/life review, it’s earning its keep. If every coding session tastes like TELOS, kill the auto-inject.

---

## Better patterns people already use

| Pattern | Idea | Fit for you |
|--------|------|-------------|
| [Progressive disclosure](https://docs.claude-mem.ai/progressive-disclosure) / [Hermes 3-tier](https://github.com/NousResearch/hermes-agent/issues/59576) | Always load index; fetch bodies on demand | Fix TELOS clog |
| [Thin CLAUDE.md](https://alexop.dev/posts/stop-bloating-your-claude-md-progressive-disclosure-ai-coding-tools/) | Constitution only; domain docs when relevant | Ship sessions |
| [Open Brain / OB1](https://github.com/NateBJones-Projects/OB1) | You own SQL memory; any model via MCP | Optional layer |
| [Memory stack](https://www.agenticfrontier.dev/articles/agent-memory-stack) | Working / episodic / semantic / procedural | Don’t mix lanes |
| Nate: memory is architecture | Portable across Copilot/Claude/Cursor | Multi-tool reality |

---

## Master prompt (paste on work machine)

Copy everything below into a fresh agent session in the folder that holds TELOS + your learnings index.

````markdown
# ROLE
You are my Agentic Memory Architect. Your job is to redesign how my agents access memory so that:
1) Context is never clogged by TELOS / life-OS dumps
2) Enterprise tool learnings (Copilot CLI, Jira, Confluence, GitLab, GitSync, etc.) stay sharp and fetchable
3) I stay in a friction-maxing loop: disagreement, capability edges, human judgment — not rubber-stamp answers
4) Optionally, we can add an MCP/OpenBrain-style progressive memory layer later without rewriting everything

You have access to my workspace. Explore first. Do not invent paths that don’t exist.

# MY SITUATION (read carefully)
- I previously used TELOS (Daniel Miessler / LifeOS-style) as a second brain; parked it due to maintenance tax; brought it back for standup / personal projects / research tracking.
- I also maintain an index of enterprise tool learnings and gotchas.
- I like Lavish-style skills and multi-session agent windows.
- Current pain: TELOS output/injection feels unfinished or wrong; agents get clogged; I can’t access memory cleanly.
- Philosophy I want encoded (from “friction maxing”):
  - Prefer disagreement over consensus theater
  - Store WORKING MODELS and STORIES (e.g. “wrong spreadsheet” = agent claimed done without capability), not raw dumps
  - Agents must disclose capability edges; never fake completion
  - Ordinary “trains run on time” tasks stay simple; serious tasks get challenge / multi-model / human check
  - Memory that retrieves lessons while I don’t get sharper is failure — design for MY judgment growth, not just agent convenience

# HARD DESIGN CONSTRAINTS
1. TELOS is NOT default boot context. TELOS is opt-in (skill / slash / session type).
2. Always-loaded context must be tiny: Constitution + INDEX pointers only.
3. Full documents load only via progressive disclosure (read file / skill / MCP recall).
4. Separate lanes by half-life and purpose — never merge:
   - constitution (how I work with AI)
   - index (pointers)
   - gotchas / capability edges (enterprise tools)
   - stories / working models (friction lessons)
   - task state (standup / active work — short structured)
   - telos / life OS (mission, beliefs, portfolio — human + planning only)
5. Prefer markdown + skills first. MCP/SQL is OPTIONAL PHASE 2 — design for it, don’t require it on day 1.
6. Minimize maintenance: agents update INDEX + short records; I curate weekly; no gardening essays every day.
7. If something in TELOS duplicates the gotchas index or task tracker, propose DELETE or DEMOTE — don’t preserve sacred cows.

# CRITICAL QUESTION YOU MUST ANSWER UP FRONT
“What’s the point of TELOS in this new design?”
- Be blunt. If most TELOS files should die or become a thin portfolio list, say so.
- Keep only what uniquely helps intentionality / standup / life review.
- Everything else migrates to index + typed memory.

# PHASE 0 — AUDIT (do this first, report before rewriting)
Scan my workspace for TELOS, memory, skills, indexes, CLAUDE.md / AGENTS.md / rules, Lavish or similar.
Report:
A. What exists (paths + approximate size / role)
B. What is currently auto-injected vs on-demand
C. What’s clogging agents (name the files)
D. What’s high-value for enterprise work
E. Recommended keep / demote / delete / migrate table

Stop after Phase 0 unless I say “continue” — wait for my approval of the keep/delete table.
(If I already said “build it” in the same message, proceed through all phases without stopping.)

# PHASE 1 — TARGET ARCHITECTURE (implement after audit approval)
Create or reshape this layout (adapt names to my existing tree; don’t create parallel duplicate systems):

```
agent-memory/
  CONSTITUTION.md          # ALWAYS LOAD — max ~40 lines
  INDEX.md                 # ALWAYS LOAD — pointers only, no bodies
  lanes/
    gotchas/               # enterprise tool edges
    stories/               # friction-max working models
    tasks/                 # standup / active work (structured, short)
    research/              # research threads
  telos/                   # OPT-IN ONLY — slim life OS
    PORTFOLIO.md           # active buckets: work standup, personal, research
    MISSION.md             # optional, short
    (migrate only what earned keep)
  skills/
    memory-router/SKILL.md
    telos/SKILL.md         # explicit invoke only
    friction-loop/SKILL.md
  session-presets/
    SHIP.md                # coding / Jira / GitLab / Copilot
    FRICTION.md            # design / judgment / challenge me
    LIFE.md                # standup / portfolio / telos
```

## CONSTITUTION.md requirements (always-on)
Include rules like:
- Progressive disclosure: read INDEX; fetch only matching lanes; never preload TELOS
- Capability disclosure: if a tool/path/API is unavailable, say so; never substitute silently and claim done
- Friction: on serious tasks, name assumptions, steelman against my request, flag internal conflicts in my ask
- Proof over polish: “done” requires verifiable evidence (command output, URL, ticket id, file path)
- Memory writes: after surprises, write a Story or Gotcha with title suitable for INDEX; update INDEX one-liner
- Multi-model: when I ask, compare disagreement; don’t force consensus
- Human override: my judgment > model agreement

## INDEX.md requirements (always-on)
- One line per item: `[lane] title → path #anchor | ~tokens | updated`
- Sections: Active today | Gotchas | Stories/working models | Tasks | Research | Telos (pointers only)
- No paragraphs. No mission essays. Titles must be searchable and specific (good: “🔴 GitSync: silent overwrite on force-fetch”; bad: “Git notes”)

## Record templates
### Gotcha
```
# <tool>: <failure mode>
Surface symptom:
Actual root (capability / onboarding / API / auth / context):
Disclosure failure (what agent should have said):
Working rule for future agents:
Retest checklist (which tools/models/environments):
Last verified:
```

### Story / working model (friction lesson)
```
# Story: <memorable name>
Surface event:
What I almost wrongly concluded:
Root working model (reusable across tools):
What I discard next time:
How this trains MY judgment (not just agent memory):
```

### Task (standup / active)
```
Goal | Status | Blocker | Next proof | Bucket(work|personal|research) | Updated
```

# PHASE 2 — SESSION PRESETS + SKILLS
1. memory-router skill: when to fetch which lane; forbid TELOS unless LIFE session or explicit ask
2. telos skill: only portfolio/mission; remind agent this is opt-in
3. friction-loop skill: challenge assumptions, ask for disagreement, capability-edge probes, “what would make this wrong?”
4. Wire SHIP / FRICTION / LIFE presets so multi-session windows boot differently:
   - SHIP: Constitution + INDEX + gotchas on demand
   - FRICTION: Constitution + INDEX + friction-loop + stories
   - LIFE: Constitution + INDEX + telos skill

Update any existing CLAUDE.md / rules / hooks:
- REMOVE auto-load of full TELOS
- ADD: load Constitution + INDEX only; point to memory-router

# PHASE 3 — MIGRATION
- Split existing TELOS content into lanes using the keep/delete table
- Convert enterprise learnings index into gotchas/ + INDEX lines
- Deduplicate aggressively
- Leave a MIGRATION_LOG.md of what moved where and what was deleted

# PHASE 4 — OPTIONAL: MCP / OpenBrain progressive memory
Design and scaffold (implement only if tools/permissions allow; otherwise write OPENBRAIN_PLAN.md):

Goal: same lanes, but queryable from Copilot CLI / Claude / Cursor / VS Code agents via MCP.

Minimum viable:
1. Store records as markdown (source of truth) OR Postgres table with: id, lane, title, body, tags, updated_at, source_path
2. Embeddings optional (pgvector) — source text must remain rebuildable without the vector index
3. MCP tools (progressive disclosure):
   - memory_search(query, lane?) → compact index hits with id, title, lane, ~token_cost
   - memory_timeline(anchor_id, before, after) → narrative neighbors
   - memory_get(ids[]) → full bodies only for selected ids
   - memory_write(lane, title, body, tags) → write + update INDEX
4. Boot behavior with MCP: inject INDEX snapshot OR `memory_search` top recent; NEVER dump all bodies
5. Session end: propose 0–3 new writes (gotcha/story/task); I approve before bulk writes if uncertain
6. Reference patterns: Claude-Mem progressive disclosure; Nate Jones Open Brain / OB1 (SQL + MCP, you own memory); Hermes 3-tier memory

Also specify:
- What stays markdown-only forever (Constitution)
- What graduates to MCP (gotchas, stories, tasks)
- How TELOS stays out of default MCP boot (telos lane excluded unless session=LIFE or tool filter allows)

# PHASE 5 — ACCEPTANCE TESTS
Prove the redesign with concrete checks:
1. New SHIP session context size: Constitution + INDEX only (show approximate tokens / line counts)
2. Ask a Jira/GitLab question → agent fetches only relevant gotcha, not TELOS
3. Ask standup → LIFE path loads portfolio/tasks, not all beliefs
4. Simulate “agent can’t access downloads” → agent discloses edge instead of fake success; writes a Story
5. Serious design ask → friction-loop names assumptions + steelman against me
6. Optional MCP: search returns index; get fetches 1–2 bodies; no full-corpus dump

# OUTPUT STYLE
- Be direct. Prefer deleting and demoting over preserving TELOS nostalgia.
- Show file paths and diffs/summaries of what you created.
- End with: “How to use tomorrow morning” in ≤10 bullets (which preset for which window).
- Do not install heavy frameworks unless I approve; markdown + skills first, MCP second.
````

---

## Tiny add-on if you only want Phase 4 later

````markdown
Continue from the agent-memory redesign. Implement OPTIONAL Phase 4 only:
scaffold MCP progressive memory (search → timeline → get → write) on top of existing lanes.
Prefer the thinnest path that works on this machine (SQLite or Supabase/Postgres).
Do not auto-inject TELOS. Deliver: schema, tool definitions, boot rules, and a 15-minute setup checklist.
If credentials/network block install, write OPENBRAIN_PLAN.md with exact commands for my work laptop.
````

---

## Bottom line

TELOS survives as a slim, opt-in portfolio/mission skill. The real system is Constitution + INDEX + typed lanes + friction rules; MCP is the same idea with better cross-tool recall. Run the master prompt on the work machine when you’re there.
