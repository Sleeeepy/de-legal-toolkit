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
- **`location`**: matches the service's actual region — **must be verified in the vendor dashboard**, not just guessed
  - Supabase: project region from Supabase dashboard
  - Vercel: `vercel.json` regions, edge deployment
  - Cloudflare R2: bucket jurisdiction setting
  - Resend: account region tier
  - Stripe: account country + data-residency claim
  - Anthropic / OpenAI: USA (default, no EU option as of 2026)
  - Jina: Berlin, Germany
- **`transferBasis`**: SCCs / DPF / Adequacy / N/A-EU. Sanity-check:
  - US-domiciled vendor → SCCs (2021/914) and/or DPF (where certified)
  - EU vendor → N/A
- **`dpa`**: either signed copy on file or "standard online DPA" with link

### 3. Reverse check — zombies

For each entry in `sub-processors.ts`, find at least one code-level call that justifies its presence. Zombies (listed but unused, e.g. a removed feature's vendor still disclosed) should be flagged for removal.

### 4. Datenschutz cross-check

The Datenschutzerklärung must list (or reference) every entry from `sub-processors.ts`. Most projects pull the list dynamically into the doc — verify the render still shows all entries.

## Region claims — verification

This is the single most common failure mode. The doc claims "EU (Frankfurt)" for Supabase; the actual project might be in `us-east-1`. To verify:

```yaml
# Add to project's compliance.yml:
sub_processor_regions_verified:
  supabase: { region: "eu-central-1", verified_on: "2026-05-20" }
  vercel: { region: "fra1", verified_on: "2026-05-20" }
  r2: { jurisdiction: "EU", verified_on: "2026-05-20" }
  resend: { region: "eu-west-1", verified_on: "2026-05-20" }
  stripe: { country: "DE", verified_on: "2026-05-20" }
```

The audit checks: each entry has a `verified_on` date within the last 12 months. Stale verifications FAIL.

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

| Service | In doc? | Code justifies? | Purpose match | Region claim | Region verified? | DPA |
|---------|---------|-----------------|---------------|--------------|------------------|-----|
| ...     | ✓       | ✓               | ✓             | EU/Frankfurt | 2026-05-20 ✓     | ✓   |

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
- [ ] Every entry's region claim is backed by `compliance.yml -> sub_processor_regions_verified[<service>]` with a `verified_on` date within the last 12 months. Region claims without a verification record are not allowed to close — they are the exact loophole this phase exists to detect.
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
