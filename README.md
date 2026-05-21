# de-legal-toolkit

> ⚠️ **NOT LEGAL ADVICE.** Decision-support tooling for solo / small-team German operators. For contested matters or specific interpretation questions, consult a Fachanwalt für IT-Recht. The toolkit can help you decide whether to engage one and what to ask; it cannot replace one.

Four Claude Code skills + three utility scripts for solo / small-team operators of German web apps who want to keep their DSGVO / Abmahn / UrhG compliance current without paying €30/month to a compliance SaaS.

**Skills:**

- **`legal-research`** — agent-powered research over Tier-1 German legal sources (gesetze-im-internet.de, BGH, BfDI/LfDI, openjur.de, dejure.org). Outputs structured citations. **Runs from the toolkit repo only** — its output is committed to `findings/`.
- **`audit`** — code-walking audit that applies the curated findings to a project across 8 phases: static external resources, runtime Playwright sweep, legal docs (Impressum / Datenschutz / AGB / Widerruf), sub-processor reconciliation, music-library copyright, image attribution, e-commerce (Bestellbutton + Kündigungsbutton + Widerrufsbutton), AI Act Art. 50.
- **`compliance-init`** — scans a project's `package.json` + source tree + DB and writes a `compliance.yml` declaring which audit phases apply. Run once per project at onboarding.
- **`defense`** — assesses an incoming Abmahnung / cease-and-desist letter against the findings catalogue and the project's actual codebase. Outputs risk score, options menu, Unterlassungserklärung redline, and three reply-letter templates (demand-evidence / narrowed-Unterlassung / rejection). Every output marked NOT LEGAL ADVICE.

**Utility scripts** (in `scripts/`):

- **`dpia-generator.py`** — generates an Art. 35 DSGVO DPIA report from a JSON input template. Useful for projects that trigger the DPIA threshold (e.g. health-adjacent data processing).
- **`dsar-tracker.py`** — SQLite-backed Data Subject Rights tracker with deadline alerts. Useful operationally once a project starts receiving DSAR requests post-launch.
- **`research-sample-scan.py`** — anonymised aggregate Phase 1 + Phase 2 sweep across sampled DE SME sites. Produces a public exposure-statistics report; no per-domain disclosure.

Plus a **curated `findings/` directory** that's the canonical input to the audit. Commit-tracked. Reviewable. No telemetry.

## How it works

```
                  ┌─────────────────────────────────────────┐
                  │       de-legal-toolkit (this repo)      │
                  │                                         │
                  │  skills/legal-research/    ──┐          │
                  │      ↓ research                ↓        │
                  │  findings/_current.md  ←─── runs        │
                  │      ↓                                  │
                  │  skills/audit/checks/*  ←── reads       │
                  │                                         │
                  └─────────────────────────────────────────┘
                              ↓ pulled into
                  ┌───────────────────────┐  ┌───────────────────────┐
                  │   your-project-1      │  │   your-project-2      │
                  │   .claude/skills/     │  │   .claude/skills/     │
                  │   compliance.yml      │  │   compliance.yml      │
                  └───────────────────────┘  └───────────────────────┘
```

## Install

Clone the repo once, then run `install.sh`:

```bash
git clone https://github.com/Sleeeepy/de-legal-toolkit ~/de-legal-toolkit
cd ~/de-legal-toolkit
./install.sh
```

`install.sh` creates two sets of symlinks:

1. **Toolkit-local** at `~/de-legal-toolkit/.claude/skills/` → all four skills, so when you open Claude Code inside the toolkit (to do research and commit findings) every skill is available.
2. **Global** at `~/.claude/skills/` → only the consumer-side skills (`audit`, `compliance-init`, `defense`), so they're reachable from any project you happen to be in. `legal-research` is intentionally NOT global — it only runs from the toolkit, where its output is committed to `findings/`.

`audit` reads findings via its own symlink — when the symlink resolves, the relative path `../../findings/_current.md` lands inside the toolkit. No separate findings symlink is needed.

To update later:
```bash
cd ~/de-legal-toolkit && git pull
# Symlinks resolve to the updated files; no further install step needed.
```

To uninstall:
```bash
cd ~/de-legal-toolkit && ./uninstall.sh
```

## Onboard a project

From within the project root, in Claude Code:

```
> /compliance-init
```

`compliance-init` scans `package.json`, `CLAUDE.md`, and the source tree to detect which audit phases apply, then drafts a `compliance.yml` at the project root. Confirm and write.

## Run an audit

From within an onboarded project (one that has a `compliance.yml`):

```
> /audit
```

The audit skill will:
1. Read `compliance.yml` to determine applicable phases
2. Read `findings/_current.md` from the toolkit (resolved via its symlink target)
3. Spawn parallel subagents (one per applicable phase)
4. Output a single markdown report with findings ranked by severity

Typical wall-clock: 7-10 minutes for a full 8-phase sweep.

For a single-phase refresh, add a hint in natural language:

```
> /audit — Phase 5 only, music-library copyright check.
```

## Respond to an Abmahnung

If a cease-and-desist letter arrives, from within the affected project:

```
> /defense — assess this letter [attach or paste]
```

The skill reads the letter, checks the alleged violation against the findings catalogue and the actual codebase, and emits a risk score, an Unterlassungserklärung redline, and three reply-letter templates. Every output is stamped NOT LEGAL ADVICE — for the final letter, run it past a Fachanwalt.

## Refreshing findings

From within the toolkit repo:

```
> /legal-research — case-law sweep, what's new since {date of last update}?
```

The skill spawns research subagents against BGH/ECJ, OLG/LG, and Tier-3 narrative sources. New findings get reviewed by the maintainer, then committed to `findings/_current.md` and `findings/lifecycle.json`. The maintainer then tags the commit `findings-YYYY-MM-DD` and publishes a GitHub release with the diff as release notes.

## Staying updated as a consumer

When findings change, you decide whether your projects need re-auditing.

**Passive (recommended):** Click **Watch → Custom → Releases** on this repo. GitHub will notify you of every new `findings-*` release. The release notes summarise what's added, what's superseded, and which audit phases are affected — you can decide per project whether a re-audit is warranted.

Pin the toolkit release a project was last audited against in its own `compliance.yml`:

```yaml
findings_pinned_version: findings-2026-05-21
```

The `audit` skill records this on each run so you have a clean version history per project.

**Active (later):** A sample GitHub Actions workflow will land in `examples/` that polls this repo weekly, compares the latest release against the consumer's pinned version, and opens a self-issue if they differ. Coming in a future minor release — for v0.1, the passive model is what's shipped.

**Recommended cadence: quarterly.** Statutes phase in with notice (the AI Act gave a 2-year warning; the electronic Widerrufsbutton gives 6 months). Case-law wave-triggers are rare (~1 per 3-5 years) and well-publicised when they hit; you'll see it on heise.de before any monthly cron would catch it.

## Repo structure

```
de-legal-toolkit/
├── install.sh                            # symlinks skills into ~/.claude/skills + toolkit-local
├── uninstall.sh                          # removes the symlinks
├── skills/
│   ├── legal-research/                   # research skill (toolkit-local only)
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── lfdi-by-bundesland.md
│   │       ├── case-law-landscape-2024-2026.md
│   │       ├── urhg-kug-landscape.md
│   │       └── source-urls-cheatsheet.md
│   ├── audit/                            # audit skill (global)
│   │   ├── SKILL.md
│   │   ├── checks/
│   │   │   ├── phase-1-static-resources.md
│   │   │   ├── phase-2-runtime.md
│   │   │   ├── phase-3-docs.md
│   │   │   ├── phase-4-sub-processors.md
│   │   │   ├── phase-5-copyright-music.md
│   │   │   ├── phase-6-image-attribution.md
│   │   │   ├── phase-7-ecommerce.md
│   │   │   └── phase-8-ai-act.md
│   │   └── sinks/
│   │       ├── github-issues.md
│   │       ├── gitlab-issues.md
│   │       └── local-markdown.md
│   ├── compliance-init/                  # project onboarding skill (global)
│   │   └── SKILL.md
│   └── defense/                          # Abmahn response skill (global)
│       ├── SKILL.md
│       └── references/
├── scripts/
│   ├── dpia-generator.py
│   ├── dsar-tracker.py
│   └── research-sample-scan.py
├── findings/
│   ├── _current.md                       # canonical baseline
│   └── lifecycle.json                    # per-finding status
└── README.md
```

## Scope

- **In scope**: DSGVO (EU + BDSG), DDG (Impressum + telemedia rules), MStV § 18, BGB (consumer e-commerce: § 312j Bestellbutton, § 312k Kündigungsbutton, § 355-356 Widerruf), UrhG (copyright on music + images), KUG (right of own image), AI Act Art. 50 (transparency), and Abmahn-relevant § 7 UWG (newsletter DOI).
- **Out of scope**: Steuerrecht, Arbeitsrecht, Markenrecht, Gewerbeanmeldung. These are real concerns but not what this toolkit covers.

## Liability disclaimer

This toolkit produces structured pointers to current German law and identifies code-level patterns that may attract Abmahn or DSGVO claims. It does **not** provide legal advice. For an authoritative interpretation in a contested matter, consult a Fachanwalt für IT-Recht.

The toolkit is offered without warranty under MIT (skills + scripts) and CC-BY 4.0 (findings content). Use at your own risk.

## Contributing

PRs welcome — particularly:

- **New findings**: a verified BGH/OLG/ECJ ruling not in `_current.md`, with a one-paragraph reason for inclusion.
- **New audit checks**: a static-scrapable pattern not covered in `checks/`. Include the citation that makes it audit-worthy.
- **Source corrections**: a statute citation that's stale (e.g. TMG → DDG).
- **Bundesland-specific updates**: changes to LfDI organisation, contacts, addresses.

When adding a finding, include the verbatim citation, the primary source URL (Tier 1: gesetze-im-internet.de / BGH / openjur.de / curia.europa.eu), and at most one Tier-3 source for narrative context. Tier-3 sources never substitute for primary citation.

## Versioning

- **v0.1** (current): manual research and audit runs. Skills callable; findings committed by hand; signal to consumers via tagged releases (`findings-YYYY-MM-DD`).
- **v0.2** (planned): sample consumer workflows (`examples/check-findings.yml` for GitHub Actions, `examples/check-findings.gitlab-ci.yml` for GitLab CI) that poll for new findings releases and auto-open re-audit issues in the consumer's repo. Also: optional quarterly research cron in the toolkit's own CI.

## Why this exists

Solo and small-team German operators face the same DSGVO / Abmahn risk profile as enterprise operators but cannot justify €30-200/month compliance SaaS subscriptions or €5K legal retainers. The agent-skill ecosystem can fill that gap if the rule catalogue is curated, current, and code-aware.

This toolkit is what €30/month bought, minus the liability indemnification, plus open and forkable findings.
