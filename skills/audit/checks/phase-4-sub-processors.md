---
phase: 4
name: Sub-processor reconciliation
tags: [sub-processors, third-country-transfer, scc, dpf, art-28-dsgvo]
applies_when_compliance_yaml: { sub_processors: true }
---

# Phase 4 — Sub-processor reconciliation

**Goal:** Every external service the codebase calls must be in the sub-processor list, and vice versa. No zombie disclosures (listed but unused), no undisclosed processors (used but not listed).

Server-to-server API calls still count as sub-processor relationships under Art. 28 DSGVO. They're invisible to scrapers but must be disclosed in the Datenschutzerklärung.

## What to check

### 1. Outbound API grep

Search codebase for calls to external services:

| Service | Patterns to search |
|---------|--------------------|
| OpenAI | `api.openai.com`, `from 'openai'`, `from "openai"`, `new OpenAI(` |
| Anthropic | `api.anthropic.com`, `from '@anthropic-ai/sdk'`, `new Anthropic(` |
| Jina | `r.jina.ai`, `JINA_API_KEY` |
| Resend | `api.resend.com`, `from 'resend'`, `new Resend(` |
| Supabase | `createClient(`, `@supabase/supabase-js`, `@supabase/ssr` |
| Cloudflare R2 / S3 | `cloudflarestorage`, `r2.dev`, `S3Client`, `R2_` |
| Stripe | `api.stripe.com`, `js.stripe.com`, `new Stripe(`, `@stripe/stripe-js` |
| Vercel Analytics | `@vercel/analytics`, `@vercel/speed-insights` |
| Google OAuth | `accounts.google.com`, in Supabase Auth flow |
| Sentry | `@sentry/`, `sentry.io` |
| Plausible / Matomo | `plausible.io`, `matomo.cloud` |

For each match: file:line + 1-2 lines of context.

### 2. Sub-processor list verification

Read `src/lib/legal/sub-processors.ts` (or wherever the project keeps the list). For each entry, verify:

- **`name`**: matches the actual service
- **`purpose`**: still describes what the code uses the service for (no over-disclosure, no under-disclosure)
- **`location`**: matches the service's actual region — **must be read from the vendor dashboard/API for THIS account**, never inferred. Record the raw region identifier the vendor reports (e.g. `eu-west-1`), then map it to a city/country using the vendor's own documentation — do not translate a region code to a city from memory, and do not let a generic "EU" claim stand in for a specific location.
  - Supabase: project region from the Supabase dashboard (Project Settings → General). Record the raw code, e.g. `eu-central-1` (Frankfurt) vs `eu-west-1` (Ireland) vs `us-east-1`.
  - Vercel: `vercel.json` regions / deployment region (Project Settings → Functions). Raw code, e.g. `fra1` (Frankfurt), `dub1` (Dublin).
  - Cloudflare R2: bucket **jurisdiction** setting (`eu` / `fedramp` / default). A bucket with no jurisdiction set is **not** guaranteed EU.
  - Resend: the account region from the Resend dashboard (Settings → General → Region). The EU tier is `eu-west-1` = **Ireland**, NOT Frankfurt. The default is `us-east-1`. Do not assume Frankfurt.
  - Stripe: account country + any data-residency add-on (Stripe does not let you pick an EU-only region by default — US processing applies unless a residency contract says otherwise).
  - Anthropic / OpenAI: USA (default, no EU option as of 2026)
  - Jina: Berlin, Germany — but still confirm against current vendor docs; do not carry this forward unchecked.

  ⚠️ The classic mistake this phase exists to catch: writing a plausible city ("Frankfurt") because the vendor is "EU", when the account is actually in a different EU region (Ireland) or even the US. AWS region codes are the usual trap — `eu-west-1` is Ireland, `eu-central-1` is Frankfurt. Always read the code, then map it.
- **`transferBasis`**: SCCs / DPF / Adequacy / N/A-EU. Sanity-check:
  - US-domiciled vendor → SCCs (2021/914) and/or DPF (where certified)
  - EU vendor → N/A
- **`dpa`**: either signed copy on file or "standard online DPA" with link

### 3. Reverse check — zombies

For each entry in `sub-processors.ts`, find at least one code-level call that justifies its presence. Zombies (listed but unused, e.g. a removed feature's vendor still disclosed) should be flagged for removal.

### 4. Datenschutz cross-check

The Datenschutzerklärung must list (or reference) every entry from `sub-processors.ts`. Most projects pull the list dynamically into the doc — verify the render still shows all entries.

## Region claims — verification

This is the single most common failure mode. The doc claims "EU (Frankfurt)" for Supabase; the actual project might be in `us-east-1`. A `verified_on` date alone is not enough — it does not prove the value was read rather than guessed. Each entry must record **the raw region value AND where it came from**:

```yaml
# Add to project's compliance.yml:
sub_processor_regions_verified:
  supabase: { region: "eu-central-1", method: "dashboard", source: "Supabase → Project Settings → General → Region", verified_on: "2026-05-20" }
  vercel:   { region: "fra1",         method: "config",    source: "vercel.json:regions", verified_on: "2026-05-20" }
  r2:       { jurisdiction: "EU",     method: "dashboard", source: "Cloudflare → R2 → <bucket> → Settings → Jurisdiction", verified_on: "2026-05-20" }
  resend:   { region: "eu-west-1",    method: "api",       source: "GET https://api.resend.com/... → region field", verified_on: "2026-05-20" }
  stripe:   { country: "DE",          method: "api",       source: "Stripe API account.country", verified_on: "2026-05-20" }
```

`method` must be one of:

- **`dashboard`** — the auditor read the value in the vendor console. `source` names the exact screen path.
- **`config`** — the region is pinned in a repo file the deploy actually uses (e.g. `vercel.json` regions). `source` is `file:field`.
- **`api`** — **preferred when available.** If the repo already holds credentials for the vendor, query the vendor's API for the account/project region instead of trusting a dashboard read or a memory of where the account "should" be. This is reproducible and can be re-run in CI. `source` names the endpoint and the field read. Examples:
  - Supabase: Management API `GET /v1/projects/{ref}` → `region`
  - Resend / Stripe / R2: account or bucket metadata endpoint → region/jurisdiction field
  - Treat the credentials as read-only; never write, and never print the secret into the issue or compliance.yml — only the returned region value.

The audit checks each entry has: a non-empty raw `region`/`jurisdiction`/`country`, a `method`, a non-empty `source`, and a `verified_on` date within the last 12 months. A bare `{ region: "...", verified_on: ... }` with no `method`/`source` FAILS — that is the "wrote a plausible city" loophole.

## Output schema

```markdown
## Phase 4 — Sub-processor reconciliation

Status: PASS | PASS-WITH-NOTES | FAIL

### Code-level external services

| Service | File:line | Purpose-in-code |
|---------|-----------|-----------------|
| OpenAI  | src/app/.../actions.ts:300 | Text polish on teacher opt-in |
| ...     | ...       | ...             |

### Sub-processor list reconciliation

| Service | In doc? | Code justifies? | Purpose match | Region claim | Raw region | Verify method + source | Verified on | DPA |
|---------|---------|-----------------|---------------|--------------|------------|------------------------|-------------|-----|
| Resend  | ✓       | ✓               | ✓             | Ireland      | eu-west-1  | api · GET /…→region    | 2026-05-20  | ✓   |

The "Raw region" and "Verify method + source" columns are mandatory — an empty cell means the location was assumed and the row FAILS.

### Discrepancies

- Each finding: service, what's wrong, what to fix
- Zombie disclosures section
- Region-claim-without-verification section

### Verdict
```

## Close gate

Lifted verbatim by the sink into each phase-4 issue's "Close gate" section. A phase-4 finding may only be closed when ALL apply:

- [ ] Every external service detected in the code-grep table appears as a `sub-processors.ts` entry, with `name` / `purpose` / `location` / `transferBasis` / `dpa` fields populated (no placeholders, no `unknown`).
- [ ] Every `sub-processors.ts` entry has a code-level call that justifies its presence (zombies removed, not just commented out).
- [ ] Every entry's region claim is backed by `compliance.yml -> sub_processor_regions_verified[<service>]` carrying the raw vendor region value (`region`/`jurisdiction`/`country`), a `method` (`dashboard` / `config` / `api`), a non-empty `source`, and a `verified_on` date within the last 12 months. A record that has a date but no `method`+`source` does NOT satisfy this gate — it cannot prove the location was read rather than assumed, which is the exact loophole this phase exists to detect.
- [ ] The `location` string in `sub-processors.ts` is the city/country that the recorded raw region code actually maps to per vendor docs (e.g. `eu-west-1` → Ireland, not Frankfurt). A mismatch between the raw code and the disclosed city is a FAIL even if `verified_on` is fresh.
- [ ] The Datenschutzerklärung's rendered sub-processor section lists every entry from `sub-processors.ts` (or pulls the list dynamically — verify the render).
- [ ] Re-audit of phase 4 with the toolkit at HEAD: zero undisclosed processors, zero zombies, zero stale region verifications.

### Lifecycle-state loophole

- [ ] No `sub-processors.ts` entry has `transferBasis: "pending"`, `dpa: "pending"`, or `location: "tbd"`. If lifecycle markers were used during remediation, a deploy-time gate rejects them.

### Regression guard (HIGH)

- [ ] CI step that re-runs the outbound-API grep table and fails the build if any service appears in code without a matching entry in `sub-processors.ts`. Name the script in the close comment.

## Citation chain

- Sub-processor disclosure → Art. 13(1)(e) + Art. 28 DSGVO
- Region claim accuracy → Art. 13(1)(f) + Chapter V DSGVO
- DPA requirement → Art. 28(3) DSGVO
- Joint controllership (if any service co-determines purposes/means) → Art. 26 DSGVO
