---
name: compliance-init
description: |
  User-invocable only via /compliance-init — not auto-triggered. Onboards a project to the de-legal-toolkit. Scans the project's package.json, CLAUDE.md, source tree, and database to detect which compliance phases apply, then writes a compliance.yml at the project root that drives subsequent audit runs. Run once per project at onboarding.
metadata:
  category: Compliance & Audit
  invocation: user-only
  pairs-with:
    - skill: audit
      reason: compliance-init writes the config file that audit consumes.
---

# Compliance Init

Detect what kinds of compliance scrutiny a project needs and write a `compliance.yml` at the project root. The `audit` skill reads this file to decide which phases run.

This is a one-shot initialiser. Run it once per project. Re-run only when the project's surface materially changes (e.g. you add Stripe to a previously-free site).

---

## When to use

- A new project is being onboarded to the toolkit
- `audit` complains "no compliance.yml found"
- Project added a major surface (Stripe checkout, AI features, music library) and the existing `compliance.yml` is now stale

**Do NOT use for:**
- Running the audit (that's `/audit`)
- Updating findings (that's `/legal-research` from inside the toolkit)

---

## Detection signals

Walk the project's `pwd` and detect:

### `static_resources` — always `true` for web projects

PASS detection: project has any `.tsx` / `.jsx` / `.html` files.

### `runtime_playwright` — has a public web surface?

PASS detection:
- `next.config.*` or `vite.config.*` present
- OR `public/` directory
- OR `src/app/` or `src/pages/`

If none of the above → likely a library, set `false`.

### `legal_docs` — has Impressum/Datenschutz?

PASS detection: `src/app/**/impressum/` OR `src/app/**/datenschutz/` exist.

If a site is operating commercially in DE/EU and these don't exist → flag this in the output. The init shouldn't *create* the docs but should warn that they're required.

### `sub_processors` — uses external APIs?

PASS detection: grep `package.json` dependencies for any of:
- `openai`, `@anthropic-ai/sdk`, `cohere-ai`, `@mistralai/mistralai` (AI SDKs)
- `resend`, `@sendgrid/mail`, `mailgun`, `postmark` (email)
- `stripe`, `@stripe/stripe-js` (payments)
- `@supabase/*`, `firebase`, `mongodb` (DB-as-a-service)
- `@aws-sdk/client-s3`, `cloudflare`, `r2-*` (storage)
- `posthog-js`, `@vercel/analytics`, `mixpanel-browser`, `amplitude-js` (analytics)

If any present → `sub_processors: true`. If only the project's own backend → `false`.

### `music_library` — has music content?

PASS detection (heuristic):
- DB migrations mentioning `works`, `pieces`, `compositions`, `scores`
- Files matching `**/*.mxl` or `**/*.musicxml`
- `package.json` mentions `opensheetmusicdisplay` or `verovio`

### `image_attribution` — has sourced/stock imagery?

PASS detection:
- `public/images/` exists with > 10 files
- OR project mentions a stock-photo-finder skill in `.claude/`
- OR has a `bildnachweise` / `attribution` page

### `e_commerce` — sells to consumers?

PASS detection:
- `stripe` in `package.json`
- OR JSX text grep for "kaufen", "bestellen", "zahlungspflichtig", "checkout"
- OR file paths containing `checkout`, `kasse`, `bestellung`

### `subscription` — has recurring payments?

PASS detection:
- Stripe present AND any of: `subscription`, `recurring`, `abo`, `monthly`, `jährlich` mentioned in code/CLAUDE.md
- OR DB migrations mentioning `subscriptions` / `subscription_status` / `subscription_tier`

### `ai_features` — has user-facing AI?

PASS detection:
- AI SDK in `package.json` AND any of: code grep for chat UI patterns (`useChat`, `useCompletion`), button text mentioning "KI" / "AI" / "verbessern" / "vorschlagen" / "generate"
- File paths with `enhance`, `polish`, `suggest`, `ai-`

If AI SDKs are server-side only with no user-facing surface (e.g. used for moderation, classification, embeddings) → `false`.

### `health_data` — collects health-adjacent personal data?

PASS detection:
- Forms mentioning `pregnancy`, `Schwangerschaft`, `Geburt`, `birth`, `medical`, `condition`, `allergy`, `health`, `Gesundheit`
- DB tables for `appointments` in health-adjacent contexts (doula, therapist, clinic)
- CLAUDE.md mentions health/wellness domain

If true → audit Phase 6/8 also flags potential Art. 9 DSGVO / Art. 35 DPIA requirement.

### `audit_output` — where the audit posts findings

This isn't a phase trigger — it's the routing config for where per-finding artifacts go.

Detection:

1. `git remote get-url origin`:
   - hostname matches `github.com` → suggest `sink: github_issues`
   - hostname matches `gitlab.com` or contains `gitlab` → suggest `sink: gitlab_issues`
   - no remote OR hostname unrecognised → suggest `sink: local_markdown`
2. CLI availability check:
   - For github_issues: run `gh auth status` (no flags). Exit 0 = authenticated, otherwise downgrade to `local_markdown` and warn.
   - For gitlab_issues: run `glab auth status`. Same logic.
3. Always ask the user to confirm or override. Never write the audit_output block without an explicit confirmation — this is the one section that has external side-effects (it'll start creating issues in their repo), so it warrants a deliberate yes.

Default values to propose:
- `severity_threshold: medium` (HIGH + MEDIUM each get their own issue/file; LOW collapses)
- `dedupe: true` (re-runs update existing open issues rather than duplicating)
- Default labels: `[compliance, ready-for-agent]` — create them if missing in the target tracker
- Assignee: blank
- `local_markdown.output_dir: audit-results` — suggest adding to `.gitignore`

---

## Workflow

```
1. Check if compliance.yml already exists at project root.
   → If yes: read it, show current values, ask "regenerate (y/n)?"
   → If no: proceed to scan.

2. Run detection passes (above). Use Bash, Read, Grep — no subagents needed,
   this is a quick local scan.

3. Build the proposed compliance.yml.

4. Read the project's CLAUDE.md (if present) to extract:
   - production_url
   - operator identity / Bundesland (informs LfDI default in audit Phase 3b)
   - any explicit compliance notes

5. Detect git host + CLI availability for audit_output (see section above).
   Propose a sink + ask the user to confirm.

6. Show the full proposed compliance.yml to the user. Ask: "Write this? (y/n/edit)"
   - n: abort
   - edit: ask which field to change, loop
   - y: write to <project>/compliance.yml

7. If sink is `local_markdown` AND the output_dir is not in `.gitignore`:
   ask whether to add it. Default y.

8. After write, suggest next steps:
   - "Run /audit now for a baseline."
   - "Click Watch → Custom → Releases on the de-legal-toolkit repo to be
      notified when findings update."
```

---

## Output schema — the compliance.yml

```yaml
# Generated by compliance-init <date>. Edit freely; re-run compliance-init to
# regenerate based on current project state.

# Which audit phases apply. Toggle off any phase that genuinely doesn't apply
# to skip it during /audit runs.
applies:
  static_resources: true      # phase 1
  runtime_playwright: true    # phase 2
  legal_docs: true            # phase 3
  sub_processors: true        # phase 4
  music_library: false        # phase 5
  image_attribution: true     # phase 6
  e_commerce: false           # phase 7
  subscription: false         # phase 7
  ai_features: false          # phase 8
  health_data: false          # Art. 9 DSGVO / Art. 35 DPIA tag

# URL the audit hits for Phase 2 Playwright runs.
production_url: https://www.example.com

# Operator's Bundesland — drives competent LfDI lookup for Datenschutz §11.
operator_bundesland: Brandenburg

# Pinned toolkit release the project was last audited against. The audit skill
# writes this on each run. Compare against the toolkit's latest release tag to
# decide whether a re-audit is warranted.
# Empty on first install; set by /audit.
findings_pinned_version: ""

# Where the audit posts its per-finding output. See skills/audit/sinks/ for details.
audit_output:
  sink: github_issues          # github_issues | gitlab_issues | local_markdown | single_report
  severity_threshold: medium   # high | medium | low — items below threshold collapse into one notes issue
  dedupe: true                 # re-runs update existing open issues rather than duplicating
  github:
    # repo: auto-detected from `git remote get-url origin` if omitted
    labels: [compliance, ready-for-agent]
    assignee: ""               # blank = unassigned; single user or array for round-robin
  gitlab:
    labels: [compliance, ready-for-agent]
    assignee: ""
    confidential: false        # if true, created issues use --confidential
  local_markdown:
    output_dir: audit-results  # relative to project root; suggest adding to .gitignore

# Per-sub-processor region claims with verification dates. The audit checks
# these are populated and recent (< 12 months old).
sub_processor_regions_verified: {}
```

---

## Anti-patterns

### Never:

1. **Auto-create legal documents.** compliance-init detects whether they exist; it does NOT generate them. Drafting is a manual task against the audit's Phase 3 checklists.
2. **Overwrite compliance.yml without confirmation.** Always show the proposed file and ask before writing.
3. **Assume English signal words.** Detection patterns should include German equivalents (kaufen / Schwangerschaft / Abo etc.) because the projects are DE-targeted.
4. **Run the audit automatically after init.** The user explicitly invokes audit when ready. Don't pre-empt.

### Common mistakes:

```
❌ Detect `stripe` in package.json → set e_commerce: true unconditionally.
✅ Detect `stripe` → ask whether it's used for B2C consumer checkout (true)
    or platform-fee billing only (still true but different audit emphasis)
    or just type imports without runtime use (false).

❌ Set ai_features: true because @anthropic-ai/sdk is in package.json.
✅ Check whether AI output is user-facing. Server-side classification with
   no UI surface → false. User-facing chatbot or text-polish → true.

❌ Default operator_bundesland to "Berlin" if not detectable.
✅ Leave blank and prompt the user — competent-LfDI accuracy is too important
   to guess.
```

---

## Example session

```
User: "/compliance-init — onboard this project."

Skill:
1. Detect project root from pwd → /path/to/your-project
2. No existing compliance.yml found. Scanning...
3. Detected:
   - next.config.ts present → static_resources, runtime_playwright: true
   - src/app/[locale]/impressum/, datenschutz-v1/ exist → legal_docs: true
   - package.json: openai, @anthropic-ai/sdk, @supabase, resend, vercel/analytics → sub_processors: true
   - opensheetmusicdisplay in deps + works/pieces tables → music_library: true
   - public/images/composers + genres + instruments → image_attribution: true
   - no stripe → e_commerce, subscription: false (but planned per docs/adr — flag)
   - server actions with OpenAI calling enhanceText → ai_features: true
   - no health-data signals → health_data: false
4. From CLAUDE.md: production_url = https://www.your-project.example
5. Operator Bundesland not detectable → prompt user: "Brandenburg"
6. Audit-output detection:
   - git remote → github.com/your-org/your-project
   - `gh auth status` → ok
   - Propose: sink = github_issues, labels = [compliance, ready-for-agent], threshold = medium
   - User confirms.
7. Show full proposed compliance.yml including audit_output block.
8. User: "y"
9. `audit-results/` not in .gitignore? Not relevant (sink = github_issues).
10. Write file. Print:
    "Done. Run /audit for a baseline pre-launch audit. Watch the
     de-legal-toolkit repo (Releases only) to be notified when findings
     update — each new `findings-*` release is a candidate re-audit trigger."
```
