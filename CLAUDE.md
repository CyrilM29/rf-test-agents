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
| `.claude/commands/` | Slash commands `/rf-plan`, `/rf-generate`, `/rf-heal`. |
| `.mcp.json` | rf-mcp server declaration (`python -m robotmcp --transport stdio --without-frontend`). |
| `specs/` | Business test plans (Markdown, French) — **the source of truth**. See its README for the contract. |
| `resources/common.resource` | Cross-page business keywords + global Setup/Teardown wrappers. |
| `resources/page_objects/` | ONE `.resource` per page/screen/API domain: locator variables on top, business keywords below. The layer the generator writes and the healer patches. |
| `variables/` | `env_<env>.yaml` (environment data), `locators.py` (selectors shared across page objects). Never credentials — `Secret:` typed CLI variables only. |
| `tests/robot/` | Generated suites, ventilated: `api/`, `ui/web/`, `ui/mobile/`, `cross/`. |
| `scripts/check_spec_sync.py` | Provenance guard: each generated suite embeds its spec's sha256; a spec changed without regeneration fails the guard. `--stamp` after each (re)generation. |
| `results/` | Robot outputs (gitignored) — always `--outputdir` here. |

## Commands

```bash
pip install -r requirements.txt                 # uncomment the channel libraries you need
robot --dryrun --outputdir results/dry tests/robot/    # keyword/import resolution, no target system
robot --outputdir results -v "APP_PASSWORD: Secret:..." tests/robot/ui/web/<suite>.robot
python scripts/check_spec_sync.py               # spec ↔ suite provenance guard
python scripts/check_spec_sync.py --stamp tests/robot/ui/web/<s>.robot specs/<p>.md
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

## Relationship to SAPFX

SAP-specific capabilities (SAP GUI perception, UI5 engines, healing telemetry,
`sapfx-mcp` overlay) stay in SAPFX. Improvements to the *agent methodology*
(workflow, ground rules, layout) discovered here should be considered for
back-porting to SAPFX's agents, and vice versa — the two agent sets are kept
conceptually aligned but have no code dependency.

## Status / next steps

- [x] Project bootstrap (2026-07-23): agents + commands + layout + provenance
      guard + bilingual READMEs, generalized from SAPFX.
- [ ] First live validation: run the full cycle (/rf-plan → /rf-generate →
      /rf-heal on a simulated drift) against a real web app.
- [ ] Optional: unit tests for `check_spec_sync.py` (port from SAPFX), CI.
- [ ] Optional: VS Code chat-mode generation from `.claude/agents/`.
