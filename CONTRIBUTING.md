# Contributing

Thanks for considering a contribution. The toolkit's value scales with the freshness of its findings catalogue and the breadth of its audit checks — both are easier to maintain with more eyes.

This guide covers what contributions look like, what gets accepted, and the conventions to follow.

---

## Three kinds of contribution

### 1. New finding — a ruling or statute that should be in the catalogue

This is the highest-leverage contribution. If you've encountered a BGH / ECJ / OLG ruling that affects DE digital, consumer, or copyright law and it's not already in `findings/_current.md`, please PR it.

Use the **New finding** issue template, or jump straight to a PR if you're confident.

### 2. Stale citation — a finding that's been superseded, narrowed, or withdrawn

Findings get superseded. A BGH ruling can overrule an OLG; an ECJ ruling can override a national wave. If you spot an entry in `findings/_current.md` whose citation is no longer current, please PR a status change in `findings/lifecycle.json` and add a short note in `findings/_current.md`.

Use the **Stale citation** issue template.

### 3. New audit check — a static-scrapable pattern not currently checked

If you find a real pattern (button label, header tag, cookie name, etc.) that scalable Abmahn lawyers detect and the audit doesn't cover, please PR a new entry in `skills/audit/checks/` or a new check within an existing phase file.

Use the **New check** issue template.

---

## What gets accepted

### High-bar criteria

1. **Primary source citation** for any new finding. A ruling MUST link to one of:
   - `gesetze-im-internet.de` (statute)
   - `bundesgerichtshof.de` (BGH press release or judgment)
   - `bundesverfassungsgericht.de`
   - `curia.europa.eu` (ECJ)
   - `openjur.de` (OLG / LG full text)
   - The relevant LfDI's official publication page
   - `eur-lex.europa.eu` (EU acts)

   Tier-3 sources (e-recht24.de, heise.de, attorney blogs) are fine as ADDITIONAL context but NEVER substitute for the primary citation. If the only source for a claim is a Kanzlei blog, the contribution doesn't meet the bar — please verify at Tier 1 first.

2. **Verbatim quotes** for new statute citations. If you're claiming "§ 312k BGB requires X", quote the relevant subparagraph verbatim with the URL. We've been bitten by paraphrased citations before.

3. **Abmahn-relevance scoring**. Each finding declares `high` / `medium` / `low` / `defensive`. The criterion is **scalability**: can a scraper detect this from outside the site? Or does it need facts-of-the-case proof?
   - High: static-scrapable browser-side pattern (Google Fonts CDN, button label, missing § 5 DDG header)
   - Medium: requires runtime analysis (cookie-pre-consent) or some context (subscription product visible)
   - Low: requires per-instance evidence (DSAR mishandling)
   - Defensive: this ruling NARROWS an obligation or gives defendants a shield

4. **Lifecycle entry**. Every new finding gets a corresponding entry in `lifecycle.json` with status (`active` / `pending-higher-court` / `defensive` / `imminent`) and date.

### What gets rejected

- Findings sourced only from anwalt.de / e-recht24.de / similar Tier-3 sources without primary verification
- Findings about a single Abmahn letter being sent (not a court ruling) — wait for a court to rule
- "I think this might happen" — speculation. Wait for the actual ruling.
- Tax law / employment law / trademark law — these are real concerns but **out of scope** for this toolkit (we focus on DSGVO / Abmahn / UrhG for web apps)
- US / UK / non-EU jurisdiction findings — focus is DE + EU-binding rulings
- Edit-war fixes ("change the wording from X to Y to sound more lawyerly") — keep PRs focused on substantive change

---

## File format conventions

### `findings/_current.md`

Each finding has an entry like:

```markdown
### FIND-2026-001 — One-line description
- **Citation:** Court, Urteil v. DD.MM.YYYY, AZ
- **Topic:** Statute or DSGVO article
- **Holding:** 1-3 sentence summary in English
- **Abmahn relevance:** HIGH | MEDIUM | LOW | DEFENSIVE
- **Audit phase:** 1 | 2 | ... | 8 (or multiple)
- **Action when found:** what the audit should do when this finding's pattern hits
```

Finding ID conventions:
- `FIND-YYYY-NNN` — new ruling from year YYYY
- `FIND-WAVE-NNN` — historical wave-trigger still active
- `IMMINENT-YYYY-NNN` — known upcoming statute with firm date
- `DEFENSIVE-YYYY-NNN` — wave-defensive ruling

### `findings/lifecycle.json`

Each finding gets:

```json
{
  "id": "FIND-2026-001",
  "status": "active",
  "since": "2026-MM-DD",
  "note": "short rationale"
}
```

Optional fields:
- `supersedes`: ID of finding this replaces
- `superseded_by`: ID of finding that replaced this
- `trigger_date`: for `imminent` status — the date the obligation binds

### `skills/audit/checks/phase-N-*.md`

Each check file is self-contained. A subagent reads it and executes against the project. Structure:

```markdown
---
phase: N
name: Short phase name
tags: [tag1, tag2]
applies_when_compliance_yaml: { field: true }
---

# Phase N — Name

**Goal:** ...

## What to check

(patterns, sources, tables)

## Output schema

(markdown skeleton the subagent fills in)

## Citation chain

(which findings / statutes / rulings this check enforces)
```

Adding a new check to an existing phase: append a section to the phase file. Adding a new phase: new check file + update `audit/SKILL.md` phases table.

---

## PR workflow

1. **Branch** off `main`: `git checkout -b find/2026-005-short-description`
2. **Edit** the relevant file(s)
3. **Verify** the citation chain: every claim points to a Tier-1 URL
4. **Update** `lifecycle.json` if you added a finding
5. **PR title**: `find: <id> <short description>` or `check: phase-N <pattern>` or `fix: <what>`
6. **PR body**:
   - Why this matters (1 paragraph)
   - The primary source URL
   - For findings: the verbatim citation
   - For checks: what code pattern triggers a hit, with an example

PRs are reviewed by the maintainer. Expect 1-2 days for review of straightforward findings; longer for new checks or schema changes.

---

## Maintenance cadence

- **Findings**: quarterly review of the catalogue against current case law. Anyone can propose at any time via PR.
- **Audit checks**: stable — new checks added only when a new finding warrants one or a new code pattern is identified.
- **Reference files** (`urhg-kug-landscape.md`, etc.): updated when statutes change. Statute changes typically have notice periods, so these are predictable.

---

## What this toolkit is NOT

To save everyone time on rejected PRs:

- **Not legal advice.** The toolkit produces structured pointers. For a contested interpretation in a real case, talk to a Fachanwalt für IT-Recht.
- **Not a replacement for a real DPO** at scales where one is required (BDSG § 38: 20+ employees processing personal data automatically).
- **Not a guarantee of compliance.** It catches what scalable-Abmahn lawyers can detect. A determined opponent with specific knowledge of your site can still find non-scalable issues.
- **Not for non-DE jurisdictions.** The findings catalogue and audit checks are German-specific (DSGVO via BDSG, DDG, MStV, BGB, UrhG, KUG). For AT / CH / US / UK rules, this isn't the right toolkit.

---

## Code of conduct

Be civil. Cite sources. Don't argue with court rulings — note them and move on. If you disagree with a maintainer decision on a PR, open an issue to discuss the framework, not the specific PR.

---

## Saying thanks

If the toolkit saved you a Fachanwalt invoice or an Abmahnung, a GitHub star or a short note in an issue is plenty. If you want to support maintenance, a GitHub Sponsors badge will appear once the project hits ~50 stars or first external PR — until then, contributions of findings and checks are the most valuable thing you can give back.
