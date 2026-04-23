# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.14.0] — 2026-04-23

### Added

- **`main(argv: list[str] | None = None) -> int` in-process entry point**
  (afi agent-first CLI contract item 1). Culture's `_passthrough.py`
  helper can now call `from agent_experience.cli import main` and invoke
  agex in-process without `sys.exit`. Returns int for every normal path;
  `SystemExit` reserved for `--help` / `--version` per Click convention.
  `_main_entrypoint` (the `agex` console script) delegates to `main()`.
- **`--json` flag on `explain`, `overview`, and `learn`** (afi contract
  item 3). Wraps the markdown output in a JSON envelope on stdout:
  `{agex_version, command, content, format, exit_code, …}`. Errors emit
  a `{code, message, remediation}` object on stderr. Default (no flag)
  behaviour unchanged — raw markdown to stdout, plain error to stderr.
- **`agex explain` (no args) returns the root page** (afi contract
  item 2). `explain` now accepts an optional path list (`[path...]`);
  empty path = root (`agex explain agex`). The current flat-topic form
  (`agex explain overview`) keeps working.

### Changed

- **Exit codes aligned to the afi agent-first contract:**
  `0` = success, `1` = user error, `2` = env/setup or usage error.
  Previously all errors used exit code 2. Affected commands: `explain`,
  `overview`, `learn`, and the unknown-command router. `gamify` and
  `hook` (not in afi scope) retain their existing exit codes.
- Typer callback renamed from `main` to `_app_callback` (internal) to
  free the `main` name for the new in-process entry point.

## [0.13.1] — 2026-04-21

### Fixed

- **Stale canonical URL in PyPI metadata and README.** Follow-up to
  0.13.0 flagged by Copilot and Qodo on PR #26: the docs site moved
  to `https://culture.dev/agex/` but `project.urls.Homepage` in
  `pyproject.toml` still pointed at `https://agex.culture.dev`, and
  the `Docs` link in `README.md` still read
  `[agex.culture.dev](https://agex.culture.dev) (coming soon)`. Both
  user-facing entrypoints now match the Jekyll `url + baseurl`
  canonical — PyPI package page, README docs link, jekyll-seo-tag
  `<link rel="canonical">`, OG URL, and schema.org `url` all agree
  on `https://culture.dev/agex/`.

## [0.13.0] — 2026-04-21

### Changed

- **Docs site now canonically served at `https://culture.dev/agex/`**
  (was `https://agex.culture.dev/`). Path-based hosting under the
  shared origin eliminates cross-origin white flash and the transient
  403s caused by Cloudflare's cross-subdomain bot heuristic — both
  issues reported during 0.12.x rollout. Same-origin navigation also
  lets the Culture aux-nav link transition with zero handshake latency.
- `docs/_config.yml`: `url` → `https://culture.dev`, `baseurl` →
  `/agex`. Jekyll `relative_url` / `absolute_url` filters (already
  used throughout the site) regenerate all internal links under the
  `/agex/` prefix automatically.
- `docs/_includes/head_custom.html`: dropped **all** preconnect /
  dns-prefetch hints — both `https://culture.dev` (self-origin) and
  `https://agentirc.dev` (also moving to `https://culture.dev/agentirc`
  in a paired follow-up on the culture repo, becoming self-origin
  too). Kept the inline critical CSS dark-paint from 0.12.1.
- `docs/_config.yml`: `AgentIRC` aux-link + `footer_content` link now
  point at `https://culture.dev/agentirc` so the nav stays correct
  after the agentirc migration lands. Same-origin = same tab = no
  handshake = no flash.
- `docs/_includes/head_custom.html`: `<link rel="related">` for
  AgentIRC retargeted from `https://agentirc.dev` to
  `https://culture.dev/agentirc` for the same reason.

### Hosting topology (external to this repo)

The Cloudflare Pages project `agex` continues to deploy as before, but
is now proxied under `culture.dev/agex/*` by a Worker on the culture
zone (landing in a follow-up PR on `OriNachum/culture`). The legacy
`https://agex.culture.dev/` hostname is 301-redirected to
`https://culture.dev/agex/` via a Cloudflare Redirect Rule, preserving
SEO and existing bookmarks. Do **not** merge this PR until both the
Worker route and the redirect rule are live in Cloudflare — otherwise
`agex.culture.dev` will serve HTML with broken `/agex/...` internal
links for the switchover window.

## [0.12.3] — 2026-04-21

### Fixed

- **Unknown paths under `agex` served the homepage with a 200 status
  instead of returning a real 404.** Cloudflare Pages' default
  behavior, when a project has no `404.html`, is to fall back to
  `index.html`. That let `/agex/docs`, `/agex/about`, and any other
  bogus path render the agex homepage with the wrong URL — bad for
  users (confusing), bad for SEO (duplicate content across many
  URLs). Added `docs/404.md` (`permalink: /404.html`,
  `sitemap: false`, `search_exclude: true`) — Jekyll emits
  `_site/404.html`, CF Pages now serves it with an actual 404
  response.

## [0.12.2] — 2026-04-20

### Fixed

- **Sibling-site aux-nav links open in a new tab**, defeating the
  white-flash fix from 0.12.1. A fresh tab has none of the preconnect
  hints, none of the warmed TLS connection, and no shared visual
  state — so clicking "Culture" or "AgentIRC" from agex.culture.dev
  still felt like leaving the site. Flipped `aux_links_new_tab` from
  `true` to `false` in `docs/_config.yml` so the Culture / AgentIRC /
  GitHub links navigate in-tab. Users who prefer a new tab can still
  Ctrl/Cmd-click.

## [0.12.1] — 2026-04-20

### Fixed

- **Cross-site white flash** when navigating from `agex.culture.dev`
  to `culture.dev` / `agentirc.dev` (or back). Browsers painted the
  default white page before the dark-terminal stylesheet loaded,
  breaking the illusion of one unified ecosystem. Fix in
  `docs/_includes/head_custom.html`:
  - `<meta name="color-scheme" content="dark">` so the browser's own
    chrome (initial paint, scrollbars) is dark.
  - Inline critical CSS `html{background:#0B0F12;color:#F3F5F7;
    color-scheme:dark}` applied in `<head>` before the external
    stylesheet, so the very first frame is already dark.
  - `<link rel="preconnect">` + `<link rel="dns-prefetch">` for
    `https://culture.dev` and `https://agentirc.dev`, so clicking the
    aux-nav skips DNS + TLS handshake time on the hop.

Sibling fix landing in the culture repo (`culture` + `agentirc` sites)
in a separate PR; once both sides deploy the transition should feel
like a same-origin navigation instead of three separate sites.

## [0.12.0] — 2026-04-20

### Changed

- **docs site: unified with `culture.dev` ecosystem.** `agex.culture.dev`
  now feels like a sibling of `culture.dev` and `agentirc.dev` — same
  favicon, same dark-terminal chrome, shared footer voice, top-right
  aux-nav to Culture / AgentIRC / GitHub. Previously rendered as bare
  theme with no chrome because `docs/` was missing `_includes/`,
  `assets/images/`, and the `aux_links` / `footer_content` / social
  metadata keys that culture's Jekyll config provides.

### Added

- `docs/_includes/head_custom.html` — injects favicons and
  `rel="related"` links to `culture.dev` and `agentirc.dev` for
  cross-site discovery.
- `docs/assets/images/` — favicons (`favicon.ico`, `favicon-16x16.png`,
  `favicon-32x32.png`, `apple-touch-icon.png`) and OG preview images
  (`og-agex.png`, `og-culture.png`), mirrored from the culture repo.
  `og-agex.png` is currently a placeholder (a copy of `og-culture.png`)
  until an agex-specific OG image is designed.
- `docs/_config.yml` — new keys: `logo`, `twitter`, `social`, `author`,
  default OG image under `defaults`, `aux_links` (Culture / AgentIRC /
  GitHub), `aux_links_new_tab: true`, and a `footer_content` block that
  links to both sibling sites and the GitHub repo.
- `docs/index.md` — culture-style hero (`.hero` + `.btn-cta--*` classes,
  already defined in `docs/_sass/custom/custom.scss`) with `nav_order:
  0` and `permalink: /`. Existing quickstart kept below the hero.

## [0.11.1] — 2026-04-19

### Fixed

- **SonarCloud quality gate — 4 open issues resolved.** After the switch
  to Automatic Analysis (`6a6160e`), project-level suppressions in
  `sonar-project.properties` stopped being honored. Re-surfaced two
  previously suppressed false positives and two real workflow-hygiene
  findings:
  - `pythonsecurity:S2083` on `commands/gamify/scripts/install.py` —
    now suppressed inline with `# NOSONAR`; backend remains enum-validated
    via `parse_backend()` before reaching the write. False positive.
  - `pythonsecurity:S5496` on `core/render.py` — now suppressed inline
    with `# NOSONAR(pythonsecurity:S5496)`; markdown-only output, Jinja
    templates are always package-shipped. False positive.
  - `githubactions:S8264` on `.github/workflows/publish.yml` — dropped
    workflow-level `permissions: contents: read` and moved it onto the
    `build` job (the only job without explicit job-level permissions).
  - `githubactions:S7630` on `.github/workflows/docs.yml` — moved
    `${{ github.head_ref }}` out of the inline `run:` script and into an
    `env:` block so a crafted PR branch name can no longer inject shell
    commands ahead of the sed sanitiser.

## [0.11.0] — 2026-04-19

### Added

- **Auto-tag + PyPI release on main.** Every push to `main` now publishes
  the stable version to TestPyPI (canary), auto-creates the `v<version>`
  git tag if missing, publishes to PyPI, and creates a GitHub Release with
  the matching CHANGELOG section. No manual tagging needed; the version
  field in `pyproject.toml` is the release signal.
- **`version-check` CI job** (`.github/workflows/test.yml`) — PRs that
  touch `src/`, `tests/`, or `pyproject.toml` without bumping the version
  fail with a sticky PR comment pointing at `/version-bump`. Mirrors the
  enforcement pattern already in use by culture.

### Changed

- Dropped the `v*` tag trigger from `publish.yml`. Manual tagging is
  superseded by the auto-tag job; tags still exist as historical/Release
  anchors, they just get created for you.

## [0.10.0] — 2026-04-19

### Added
- **`.github/workflows/publish.yml`** — automated publish pipeline.
  Every push to `main` builds an sdist + wheel and publishes to
  **TestPyPI** (`skip-existing: true` makes it idempotent across
  pushes that don't bump the version). Every push of a `v*` tag
  publishes to **PyPI**. Both jobs use **Trusted Publishing** (OIDC),
  so no API tokens are required — the matching PyPI/TestPyPI
  publishers and GitHub repo Environments (`pypi`, `testpypi`) must
  be configured once out-of-band.
- All third-party actions SHA-pinned with trailing `# vN` comments
  per project convention #10: `actions/checkout@v4`,
  `astral-sh/setup-uv@v3`, `actions/setup-python@v5`,
  `actions/upload-artifact@v4`, `actions/download-artifact@v4`,
  `pypa/gh-action-pypi-publish@release/v1`.

### Release notes
This is the closing phase of the v0.1 implementation plan. Phases
1–11 + 13 shipped the CLI, docs site (with per-PR previews), the
Claude dogfooding workspace, and the docs-drift guards. Phase 12
(this release) lights up the publishing pipeline — `agex-cli` is
now installable from TestPyPI via `uv tool install --index-url
https://test.pypi.org/simple/ agex-cli` immediately after the first
post-merge build, and from PyPI after the maintainer pushes a
`v0.10.0` tag.

## [0.9.0] — 2026-04-19

### Added
- **`tester-agents/claude/`** — culture-meshed dogfooding workspace
  that exercises every `agex` command end-to-end from a Claude Code
  runtime. Ships `CLAUDE.md` (persona + ordered test plan),
  `culture.yaml` (mesh config), `.claude/settings.json` (allows
  `Bash(agex:*)`), and a `README.md` with registration instructions.
- **Symlink** `tester-agents/claude/.claude/skills →
  ../../../src/agent_experience/commands` so the tester invokes the
  same `SKILL.md` files the CLI ships — no stale-copy drift. Git
  stores mode `120000`; on Windows clones, directory symlinks need
  Developer Mode or an elevated shell with `core.symlinks=true` (per
  the spec's known platform limitation, documented in the workspace
  README).

## [0.8.0] — 2026-04-19

### Added
- **Jekyll documentation site** under `docs/` — landing page
  (`index.md`), `getting-started.md`, and auto-imported `commands/`
  pages (one per top-level command, plus a `Commands` parent index).
  Styled with the same just-the-docs `dark-terminal` theme + `_sass`
  overlay used by culture / agentic-human / agentic-guides so the
  agentic sites share a visual identity. Builds cleanly via
  `bundle exec jekyll build`.
- **`scripts/sync_skill_md.py`** — reuses the in-repo
  `skill_loader.load_skill` to strip each command's agex-flavored YAML
  frontmatter and emit a Jekyll-friendly one (`title`, `layout`,
  `parent`, `nav_order`). Iterates `src/agent_experience/commands/` in
  sorted order; writes with `encoding="utf-8"`. Lessons
  (`learn/assets/topics/*`) stay in CLI territory for v0.1.
- **`.github/workflows/docs.yml`** — triggers on `docs/**`,
  `commands/**/SKILL.md`, `skill_loader.py`, the sync script, and the
  workflow itself. Runs `sync_skill_md.py` before building so the
  deployed site cannot drift from the CLI's shipped docs. Deploys to
  Cloudflare Pages (project `agex`) on push-to-main only — PRs never
  deploy.

### Changed
- Swapped the plan's reference from `cloudflare/pages-action@v1` (now
  archived / DEPRECATED upstream) to `cloudflare/wrangler-action@v3`
  with `pages deploy`. All third-party actions SHA-pinned with
  trailing `# vN` comments per project convention.

### Notes
- The Cloudflare Pages project (`agex`) and the `agex.culture.dev`
  custom-domain binding require a one-time manual setup step in the
  Cloudflare dashboard; the workflow expects `CLOUDFLARE_API_TOKEN`
  and `CLOUDFLARE_ACCOUNT_ID` repo secrets. Tracked separately.

## [0.7.0] — 2026-04-19

### Added
- **Unknown-command routing** — invoking `agex <unknown>` (e.g.,
  `agex frobnicate`) now prints a one-line
  `agex: error: unknown command '<name>'` to stderr, emits the body of
  `agex explain agex` to stdout (so the agent immediately sees the full
  command list), and exits with code 2. Previously Typer's default
  "No such command" message was emitted with no recovery guidance.
  Implemented via a thin `_main_entrypoint` wrapper in `cli.py` and a
  new `agent_experience/__main__.py` so `python -m agent_experience`
  routes through the same handler as the `agex` console script.
- **SKILL.md consistency meta-test** — `tests/test_skill_md_consistency.py`
  parametrizes over every `SKILL.md` shipped under the `commands/`
  package and asserts valid frontmatter (`name`, `description`,
  `type ∈ {command, lesson}`). A companion guard test
  (`test_meta_test_discovers_all_known_skills`) fails loudly if the
  resource-discovery glob returns fewer than the expected 9 files, so
  a future packaging regression cannot silently turn every parametrize
  case into a zero-item pass-through. 15 new tests total.

### Changed
- `pyproject.toml` script entry flipped from
  `agent_experience.cli:app` to `agent_experience.cli:_main_entrypoint`
  so the unknown-command router runs before Typer's dispatcher.

### Fixed
- **#12** — `agex hook write` on Windows + Python 3.13 occasionally
  aborted with `portalocker.exceptions.AlreadyLocked` when two
  concurrent writers raced for the append lock (the kernel surfaces
  `EDEADLK` from `msvcrt.locking()`; portalocker maps it to
  `AlreadyLocked`). `core/hook_io.append_event` now retries up to
  `_LOCK_MAX_ATTEMPTS = 5` times with jittered linear backoff
  (`10ms × attempt + up to 10ms of jitter`), re-raising only if every
  attempt fails. Two deterministic regression tests monkeypatch
  `portalocker.lock` to simulate the flake and verify both the
  recovery and the final-giveup paths.

## [0.6.0] — 2026-04-19

### Added
- Minimal **stub probes** for the three remaining v0.1 backends:
  - `codex` — records the `AGENTS.md` path in
    `ProbeResult.claude_md` if present (field name reused pending a
    future `project_memory` rename); the probe does not read the
    file's contents. Further discovery deferred.
  - `copilot` — empty `ProbeResult()`; full discovery tracked as an
    open issue.
  - `acp` — empty `ProbeResult()`; full discovery tracked as an open
    issue.
- **Capability matrix data** under
  `src/agent_experience/backends/capabilities/` — one YAML per backend
  (`claude-code.yaml`, `codex.yaml`, `copilot.yaml`, `acp.yaml`)
  keyed by the four v0.1 capability facets (`hooks`, `mcp`, `skills`,
  `agents`) plus a `*_alternative` free-text field for unsupported
  ones. These YAMLs are loadable by the existing
  `core/capabilities.py::CapabilityMatrix.load(...)` API; callers that
  wire up capability-based routing (e.g., `learn.py`) land in a later
  phase.
- **Backend-specific overview YAMLs** for `codex`, `copilot`, `acp`
  under `commands/overview/assets/backends/` — mirror the `claude-
  code.yaml` shape so `agex overview --agent <backend>` renders a
  consistent snapshot across all four backends.

### Changed
- `commands/overview/scripts/overview.py` registers all four probes in
  `_PROBES`; the interim `if backend in _PROBES / else empty
  ProbeResult` fallback from Phase 4 is removed (every backend now has
  a probe, so the dead branch + stale "Phase 8 will..." comment are
  gone). `run(backend)` is now a direct dict lookup.

### Tests
- `tests/backends/test_stub_probes.py` — 4 new smoke tests exercising
  the three stub probes (codex empty + codex AGENTS.md + copilot
  empty + acp empty).
- `tests/commands/test_gamify.py` adds one regression test pinning
  that `agex gamify --agent codex` returns exit 0 with an
  "unsupported"-notice in stdout and does **not** create `.claude/`
  on disk (spec invariant #5: unsupported is success, no side
  effects).
- 66 tests passing (was 61 on 0.5.0).

## [0.5.0] — 2026-04-19

### Added
- `agex gamify --agent claude-code` — installs Claude Code hook
  fragments (tagged `agex:post-tool-use`, `agex:user-prompt`,
  `agex:stop`) into `.claude/hooks.json` so every tool use, prompt,
  and stop event calls `agex hook write`. Preserves user-authored
  hooks already in the file. Idempotent: re-running is a byte-
  identical no-op (the `[installed.gamify].at` timestamp is only
  rewritten when the fragment set actually changes).
- `agex gamify --uninstall --agent claude-code` — surgical removal:
  only entries whose `id` is tracked in `.agex/config.toml`'s
  `[installed.gamify].hook_fragment_ids` are stripped; user entries
  survive. Empty event arrays are deleted. The `gamify` record is
  popped from config.
- `commands/gamify/` skill-folder (`SKILL.md` doubles as
  `agex explain gamify`; `assets/hooks/claude-code.json` carries the
  three shipped fragments).
- Unsupported-backend path returns a markdown notice + issue-tracker
  link at exit 0 (spec invariant #5).
- 58 tests passing (53 from 0.4.0 + 4 plan tests + 1 corrupt-hooks-
  file guard).

### Safety
- Malformed `.claude/hooks.json` is NOT silently overwritten — the
  file is left untouched and `agex gamify` exits 2 with a clear
  stderr message pointing at the file. This is the first agex
  command with real side effects on the user's project; the error
  path was designed to make accidental data loss impossible.

## [0.4.0] — 2026-04-18

### Added
- `agex hook write <event> [key=value ...]` — append a JSON line with a
  UTC ISO timestamp + parsed `key=value` pairs to
  `.agex/data/<event>.json`. Silent, safe for concurrent invocation via
  `portalocker`. Empty keys (`=foo`) are dropped; the positional
  `<event>` always wins over any `event=...` pair.
- `agex hook read --agent <backend>` — render `.agex/data/*.json` as a
  markdown table with `ts | event | details` columns, one section per
  known stream (`post-tool-use`, `user-prompt`, `stop`, `sessions`).
  Empty streams show `_no events_`.
- `commands/hook/` skill-folder (`SKILL.md` doubles as
  `agex explain hook`; `assets/table.md.j2` for the read template).
- Typer sub-app pattern — `hook` is wired via `app.add_typer(...)` with
  two subcommands (`write` and `read`).
- 51 tests passing (46 from 0.3.0 + 3 CLI tests + 1 empty-key guard
  test + 1 malformed-JSON warning test); overall coverage 96%.

### Changed
- `core/hook_io.load_events` now catches `json.JSONDecodeError` on each
  line and emits a `warnings.warn(...)` instead of raising, keeping
  `agex hook read` read-only even when a `.agex/data/*.json` file is
  partially written or externally edited.

## [0.3.0] — 2026-04-18

### Added
- `agex learn [topic] --agent <backend>` — menu of available lessons
  without a topic, or teaches one with a topic. Lessons emit a
  Jinja-rendered markdown body plus an inline backend-native skill
  template the agent can write into the project itself. Rejects
  path-traversal topic arguments via the same `^[a-z][a-z0-9-]*$`
  whitelist as `agex explain`.
- Four v0.1 lessons under `commands/learn/assets/topics/`:
  `introspect`, `visualize`, `gamify` (bundles the `levelup` template),
  and `levelup`. Each ships with a `claude-code` skill template;
  Phase 8 will route non-claude-code backends through `capabilities.py`.
  The `gamify` and `levelup` lessons reference `agex gamify` and
  `agex hook read` which land in Phase 6/7 — both lessons carry an
  explicit "Preview" note until those commands ship.
- `commands/learn/` skill-folder (`SKILL.md` doubles as
  `agex explain learn`; `assets/menu.md.j2` for the topic menu).
- `tests/commands/test_learn.py` with 7 tests including a
  path-traversal guard mirroring the `explain` precedent. 46 tests
  passing total; overall coverage 97%.

## [0.2.0] — 2026-04-18

### Added
- `agex overview --agent claude-code` — deterministic markdown snapshot of
  a project's Claude Code setup (CLAUDE.md, skills, hooks, MCP, settings).
  Read-only except for first-run `.agex/` init. Unknown backends currently
  render as an empty snapshot; Phase 8 will route them to the
  unsupported-notice markdown.
- `backends/claude_code/probe.py` — `ProbeResult` dataclass + `probe()`
  that reuses `core/skill_loader.load_skill` for frontmatter parsing and
  records per-file warnings on malformed inputs instead of raising.
- `commands/overview/` skill-folder (`SKILL.md`, Jinja template,
  per-backend YAML). The `SKILL.md` doubles as `agex explain overview`.
- CLI `_agent_option()` helper and `@app.command("overview")` wiring.
- Test fixtures under `tests/fixtures/claude-code/` (`empty/`, `typical/`,
  `malformed/`). Probe test coverage 100%; overall project 98%.

### Changed
- Renamed PyPI distribution from `agent-experience` to `agex-cli` (CLI
  entry point stays `agex`); renamed GitHub repo from
  `OriNachum/agent-experience` to `OriNachum/agex`; updated issue and
  repo URLs, Homepage (`agex.culture.dev`), and SonarCloud project key
  (`OriNachum_agex`).
