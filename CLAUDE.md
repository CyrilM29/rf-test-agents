# CLAUDE.md

Guidance for AI assistants working in this repo. Keep it accurate — update it
when structure or conventions change.

## Language / Langue

**Respond to the user in French** and write user-facing documents in French;
READMEs are bilingual (EN + `*.fr.md` with cross-link banners — preserve that
pattern). Do not translate code, identifiers, Robot Framework keyword names,
CLI commands, JSON, or proper nouns. This CLAUDE.md, the agent definitions and
git commit messages stay in English.

## Memory (three coexisting layers)

1. **Project memory (this repo, public-safe)**: `memory/` at the repo root —
   anonymized durable project facts (no personal data, no machine paths, no
   private URLs); index `memory/MEMORY.md`, rules in `memory/README.md`.
2. **Private cross-project base**: `E:\QA_GenAI\agent-memory\` — user
   profile/preferences, machine specifics, cross-project facts, research
   notes; contract in its `PROTOCOLE.md`. Never published.
3. **Claude Code auto-memory** (Claude only) — internal pointers, no
   duplication of the other layers.

Read both indexes at session start. New fact: publishable + project-specific
→ layer 1; personal/machine/cross-project → layer 2. One fact per file,
update the index in the same operation, never secrets anywhere.

## What this is

**Universal Robot Framework test agents** — the plan → generate → heal cycle
(style Playwright Test Agents) driven on live applications through the
**rf-mcp** (RobotMCP) MCP server, generalized from the SAP-specific agents of
the SAPFX project (same author). No
application-specific plugin required: only rf-mcp's generic contracts
(`manage_session`, `execute_step`, `get_session_state` with ARIA snapshots,
`get_locator_guidance`, `build_test_suite`, `run_test_suite`).

Channels: web (Browser/Playwright or SeleniumLibrary), HTTP APIs
(RequestsLibrary), mobile (AppiumLibrary) — anything rf-mcp can load.

## Layout

| Path | Role |
|------|------|
| `.claude/agents/` | **Canonical agent definitions**: `rf-planner.md` (live exploration → spec), `rf-generator.md` (spec → suite, every step executed live before writing), `rf-healer.md` (repairs `resources/`, never tests). |
| `.claude/commands/` | Slash commands `/rf-plan`, `/rf-generate`, `/rf-generate-all` (batch, sequential), `/rf-heal`. |
| `.claude/settings.json` | Project hooks: after every Write/Edit of specs/tests/resources/variables, `scripts/hook_guards.py` runs both guards (conventions violations block; spec-sync drift is reported non-blocking). |
| `.mcp.json` | rf-mcp server declaration (`robotmcp --transport stdio --without-frontend`); the console script survives rf-mcp 0.35 unchanged — see « rf-mcp compatibility notes ». |
| `specs/` | Business test plans (Markdown, French) — **the source of truth**. See its README for the contract. |
| `resources/common.resource` | Cross-page business keywords + global Setup/Teardown wrappers. |
| `resources/page_objects/` | ONE `.resource` per page/screen/API domain: locator variables on top, business keywords below. The layer the generator writes and the healer patches. |
| `variables/` | `env_<env>.yaml` (environment data), `locators.py` (selectors shared across page objects). Never credentials — `Secret:` typed CLI variables only. |
| `tests/robot/` | Generated suites, ventilated: `api/`, `ui/web/`, `ui/mobile/`, `cross/`. |
| `scripts/check_spec_sync.py` | Provenance guard: each generated suite embeds its spec's sha256 (+ generation date); a spec changed without regeneration fails the guard, as does a spec carrying the healer's `> **Statut : PÉRIMÉE (…)**` marker. `--stamp` after each (re)generation. |
| `scripts/check_conventions.py` | Mechanical guard for conventions #1/#2: raw locators in test bodies, `Sleep` anywhere. Generator gate, hook, and CI. |
| `scripts/check_guidance_sync.py` | Consistency guard for convention #8: the numbered conventions must stay carried by the three agent definitions (they exist in four copies by design). Ported from SAPFX. |
| `scripts/regen_agent_definitions.py` | Generates `.github/chatmodes/*.chatmode.md` (VS Code / Copilot dialect) from `.claude/agents/rf-*.md`; `--check` guards drift in CI. Ported from SAPFX. |
| `docs/heal-journal.md` | Drift memory: one entry per heal session (class, before → after, evidence). The planner reads it before writing locator notes. |
| `docs/validation-live.md` | Runbook for the first live end-to-end validation of the cycle. |
| `tests/unit/` | pytest tests of the guard scripts (`python -m pytest tests/unit -q`). |
| `.github/workflows/ci.yml` | CI: unit tests + both guards (no robot dry run — channel libraries are not installed in CI). |
| `results/` | Robot outputs (gitignored) — always `--outputdir` here. |

## Commands

```bash
pip install -r requirements.txt                 # uncomment the channel libraries you need
robot --dryrun --outputdir results/dry tests/robot/    # keyword/import resolution, no target system
robot --outputdir results -v "APP_PASSWORD: Secret:..." tests/robot/ui/web/<suite>.robot
#                             ^ the SPACE after the name's colon is REQUIRED by RF's
#                               -v type syntax; without it the value stays the literal
#                               string "Secret:..." and Fill Secret rejects it
python scripts/check_spec_sync.py               # spec ↔ suite provenance guard (+ stale-spec markers)
python scripts/check_spec_sync.py --stamp tests/robot/ui/web/<s>.robot specs/<p>.md
python scripts/check_conventions.py             # conventions #1/#2 guard (raw locators, Sleep)
python scripts/check_guidance_sync.py           # conventions still carried by the agent definitions (#8)
python scripts/regen_agent_definitions.py       # (re)write the VS Code chat modes; --check in CI
python -m pytest tests/unit -q                  # unit tests of the guard scripts
```

## rf-mcp compatibility notes

- Validated against the **0.31.x** contract and re-validated on **0.35.0**
  (2026-07-24, then exercised live end-to-end on 2026-07-25): the generic tool
  contracts the agents rely on (`manage_session`, `execute_step`,
  `get_session_state`, `build_test_suite`…) are unchanged; the 0.32/0.33 series
  were never published.
- The PyPI distribution is **`rf-mcp`** (importable package `robotmcp`; there
  is no `robotmcp` distribution on PyPI). The `robotmcp` console script that
  `.mcp.json` launches still exists in 0.35 (now alongside an `rf-mcp` alias,
  plus onboarding subcommands `init`/`doctor`/… handled before the server).
- **Desktop classification trap (rf-mcp ≥ 0.34)** — re-measured live on 0.35.0
  (2026-07-25), and the trap is **`analyze_scenario`, not `manage_session
  init`**: `analyze_scenario` classifies from the scenario TEXT, so native-
  desktop tokens ("desktop", "win32", an `.exe` name…) yield
  `detected_session_type: desktop_testing` **even with `context="web"`
  explicitly passed** — no web library is loaded (`libraries_loaded:
  ["BuiltIn"]`, `PlatynUI.BareMetal` first in the search order) and
  `get_session_state` serves a desktop stub (placeholder `page_source`,
  `aria_snapshot: null`) instead of the DOM/ARIA snapshot — the agents'
  perception channel. The classification is **sticky**: importing `Browser`
  afterwards and opening the right URL restores `is_browser_session: true` but
  NOT perception; only a new session does. `manage_session init` classified
  nothing from its `scenario` text (`session_type` stayed `unknown`) — which is
  why the agents' ritual opens sessions with `init` + explicit `libraries=[...]`
  and deliberately diverges from the server's own instructions ("call
  analyze_scenario ONCE to start… NEVER call manage_session(action='init')").
  The three agent definitions carry the warning in their session ritual
  (convention #8).
- Since 0.34 the server's agent-instructions template defaults to `lean`
  (`ROBOTMCP_INSTRUCTIONS_TEMPLATE=standard` restores the verbose one).

## Conventions (do not break)

1. **Tests contain no raw locators** — CSS/XPath/ids live in
   `resources/page_objects/` or `variables/locators.py`; tests speak business
   language.
2. **Never `time.sleep`/`Sleep`** — real synchronization only.
3. **Robust assertions** — stable ids, ARIA role + accessible name, HTTP
   status, JSON field names, counts; never localized display text when a
   stable anchor exists.
4. **Never fabricate locators** — everything committed was observed/probed
   live through rf-mcp.
5. **The spec is the source of truth** — never hand-edit a generated suite to
   catch up with its spec; regenerate (or consciously re-stamp).
6. **Credentials never in files** — `Secret:` typed command-line variables.
7. Agent definitions in `.claude/agents/` are the canonical source; other
   assistant formats are **generated**, never forked —
   `python scripts/regen_agent_definitions.py` writes
   `.github/chatmodes/*.chatmode.md`, and `--check` fails CI when a chat mode
   drifts from its source (edit the agent, then regenerate in the same commit).
8. **Ground rules are quadruplicated by design** — conventions and the rf-mcp
   session ritual appear in the three agent files AND here. Any change must be
   mirrored in all four in the same commit (each agent carries a sync note).
9. **Spec lifecycle markers** close the feedback loops: the healer marks a
   functionally-changed spec `> **Statut : PÉRIMÉE (date)** — …` (blocks
   `check_spec_sync.py` until the planner re-explores and removes it); the
   generator records reality/spec divergences under
   `## Écarts constatés à la génération` before re-stamping; every heal
   session appends to `docs/heal-journal.md`.

## Relationship to SAPFX

SAP-specific capabilities (SAP GUI perception, UI5 engines, healing telemetry,
`sapfx-mcp` overlay) stay in SAPFX. Improvements to the *agent methodology*
(workflow, ground rules, layout) discovered here should be considered for
back-porting to SAPFX's agents, and vice versa — the two agent sets are kept
conceptually aligned but have no code dependency.

## Status / next steps

- [x] Project bootstrap (2026-07-23): agents + commands + layout + provenance
      guard + bilingual READMEs, generalized from SAPFX.
- [x] Agentic-system hardening (2026-07-24): feedback loops (PÉRIMÉE marker,
      « Écarts constatés » section, heal journal), mechanical guards
      (`check_conventions.py`, post-edit hook, CI), dated provenance stamp,
      unit tests for both guards, `/rf-generate-all`, `.mcp.json` launch fix
      (`robotmcp` console script).
- [x] **First live validation (2026-07-24)**: full cycle run end-to-end against
      https://www.saucedemo.com through rf-mcp — `/rf-plan` (live exploration →
      `specs/saucedemo-connexion-panier.md`), `/rf-generate` (3 tests, 3 gates
      green, live run 3/3 PASS), simulated locator drift → suite red (1/3) →
      `/rf-heal` (diagnosed unaided, one-line resource fix, back to 3/3 PASS,
      first `docs/heal-journal.md` entry). Results and findings in
      `docs/validation-live.md`.
- [x] **Bidirectional port with SAPFX (2026-07-24)**: pushed the feedback
      loops and `check_conventions.py` to SAPFX (branch
      `port-agent-feedback-loops`); pulled back its two better answers —
      `regen_agent_definitions.py` (VS Code chat modes generated from the
      canonical agents, closing the item below) and `check_guidance_sync.py`
      (convention #8 enforced by a guard rather than by a prose note). The
      guard immediately caught a real gap: only `rf-generator.md` carried
      convention #6, so the healer had no `Secret:` syntax to reproduce a
      failure with.
- [x] **Live re-validation on rf-mcp 0.35.0 (2026-07-25)**: MCP session ritual,
      ARIA perception, live suite run (`3/3 PASS`) and a full `/rf-heal` cycle
      on a simulated drift (red `2/3` → diagnosed unaided → `3/3 PASS`, journal
      entry). Two corrections came out of it: the desktop-classification trap
      was documented against the wrong entry point (it is `analyze_scenario`,
      not `manage_session init`, and it is sticky), and this environment's
      `PYTHONIOENCODING=utf-8:surrogateescape` crashes Robot's console writer
      under PowerShell — run `robot` from Bash, or set `PYTHONIOENCODING=utf-8`.
      Details in `docs/validation-live.md`.
