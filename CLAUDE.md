# CLAUDE.md

Guidance for AI assistants working in this repo. Keep it accurate — update it
when structure or conventions change.

## Language / Langue

**Respond to the user in French** and write user-facing documents in French;
READMEs are bilingual (EN + `*.fr.md` with cross-link banners — preserve that
pattern). Do not translate code, identifiers, Robot Framework keyword names,
CLI commands, JSON, or proper nouns. This CLAUDE.md, the agent definitions and
git commit messages stay in English.

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
| `.mcp.json` | rf-mcp server declaration (`robotmcp --transport stdio --without-frontend` — the installed fork has no `python -m robotmcp`). |
| `specs/` | Business test plans (Markdown, French) — **the source of truth**. See its README for the contract. |
| `resources/common.resource` | Cross-page business keywords + global Setup/Teardown wrappers. |
| `resources/page_objects/` | ONE `.resource` per page/screen/API domain: locator variables on top, business keywords below. The layer the generator writes and the healer patches. |
| `variables/` | `env_<env>.yaml` (environment data), `locators.py` (selectors shared across page objects). Never credentials — `Secret:` typed CLI variables only. |
| `tests/robot/` | Generated suites, ventilated: `api/`, `ui/web/`, `ui/mobile/`, `cross/`. |
| `scripts/check_spec_sync.py` | Provenance guard: each generated suite embeds its spec's sha256 (+ generation date); a spec changed without regeneration fails the guard, as does a spec carrying the healer's `> **Statut : PÉRIMÉE (…)**` marker. `--stamp` after each (re)generation. |
| `scripts/check_conventions.py` | Mechanical guard for conventions #1/#2: raw locators in test bodies, `Sleep` anywhere. Generator gate, hook, and CI. |
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
python -m pytest tests/unit -q                  # unit tests of the guard scripts
```

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
7. Agent definitions in `.claude/agents/` are the canonical source; if other
   assistant formats are derived later (VS Code chat modes…), generate them,
   never fork them.
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
- [ ] Optional: VS Code chat-mode generation from `.claude/agents/`.
