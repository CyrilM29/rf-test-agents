> 🇫🇷 Version française : [README.fr.md](README.fr.md)

# rf-test-agents

**Universal test agents for Robot Framework — plan → generate → heal — driven
by a live application through the [rf-mcp](https://github.com/manykarim/robotmcp)
(RobotMCP) server.**

Technology-agnostic: the agents work with whatever Robot Framework library
rf-mcp can load — web (Browser/Playwright, SeleniumLibrary), HTTP APIs
(RequestsLibrary), mobile (AppiumLibrary), databases… They transpose the
Playwright Test Agents idea (planner / generator / healer) to the Robot
Framework ecosystem, generalized from the SAP-specific agents of the SAPFX
project (same author). License: Apache-2.0.

## The three agents

| Agent | Command | What it does |
|-------|---------|--------------|
| **rf-planner** | `/rf-plan` | Explores the live application through rf-mcp (perceive → act → perceive, ARIA snapshots, real API responses) and writes a business-readable test plan under `specs/`. Every fact in the plan was observed live, never assumed. |
| **rf-generator** | `/rf-generate` | Turns one `specs/` plan into a runnable `.robot` suite. Its defining discipline: **no step lands in a file before it was executed live** through rf-mcp. Missing business keywords are added to the resource layer (page objects), never inlined in tests. |
| **rf-healer** | `/rf-heal` | Repairs a failing suite by fixing the **automation layer** (`resources/`), never by weakening what the test proves. Locator drift, timing, data drift and genuine functional changes each get their own treatment; genuine flow changes go back to the planner. |

The cycle is closed by a provenance guard: each generated suite embeds the
content hash of its source spec, and `python scripts/check_spec_sync.py` fails
whenever a spec changed without regeneration — **the plan is the source of
truth**.

## Non-negotiable conventions (what the agents enforce)

1. **Tests contain no raw locators.** CSS/XPath/element ids live in
   `resources/page_objects/*.resource` (one page object per page/screen/API
   domain) or `variables/locators.py`; tests speak business language.
2. **Never `Sleep` to wait.** Real synchronization only (`Wait For Elements
   State`, `Wait Until Element Is Visible`, `Wait Until Keyword Succeeds`).
3. **Robust assertions.** Stable ids, ARIA role + accessible name,
   `data-testid`, HTTP status codes, JSON field names, counts — never a
   localized display text when a stable anchor exists.
4. **Never fabricate locators.** Every locator was observed/probed live before
   being committed.
5. **Credentials never land in a file.** RF 7.4+ typed `Secret:` command-line
   variables, masked even at TRACE.

## Layout

```text
.claude/agents/        rf-planner / rf-generator / rf-healer (canonical definitions)
.claude/commands/      /rf-plan  /rf-generate  /rf-heal
.mcp.json              rf-mcp server declaration (project scope)
specs/                 business test plans (source of truth)
resources/             common.resource + page_objects/ — the layer agents write & heal
variables/             env_<env>.yaml, shared locators.py (never credentials)
tests/robot/           generated suites — api/ · ui/web/ · ui/mobile/ · cross/
scripts/               check_spec_sync.py (spec ↔ suite provenance guard)
results/               robot outputs (gitignored)
```

## Quickstart

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements.txt                     # uncomment your channel's library first
rfbrowser init                                      # only if you enabled robotframework-browser
```

Open the folder in Claude Code (or any MCP-capable agent host): `.mcp.json`
declares the rf-mcp server. Then:

```
/rf-plan     the login flow of https://myapp.example.com
/rf-generate specs/login-flow.md
/rf-heal     tests/robot/ui/web/login_flow.robot
```

## Relationship to SAPFX

The SAP-specific incarnation of these agents (SAP GUI perception keywords,
UI5 locator engines, healing telemetry) lives in the SAPFX project and stays
there. This project is the **universal core**: rf-mcp's generic contracts only
(`manage_session`, `execute_step`, `get_session_state`, `get_locator_guidance`,
`run_test_suite`…), no application-specific plugin required.
