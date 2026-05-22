---
phase: 2
name: Runtime Playwright sweep
tags: [cookies, pre-consent, runtime, browser-state]
applies_when_compliance_yaml: { runtime_playwright: true }
---

# Phase 2 — Runtime Playwright sweep

**Goal:** Verify what actually fires from the browser on a fresh visit. Static analysis (Phase 1) can miss runtime-injected scripts; Playwright catches them.

Run against **production** (the actual customer-facing URL) when available — that's what mass-Abmahn scrapers see. Use dev only pre-launch or when production isn't accessible.

## What to check

Routes to sweep (project-specific; ask if unsure):

- Homepage (`/`)
- Public discovery / catalogue pages
- Each legal doc: `/datenschutz`, `/impressum`, `/agb`, `/widerrufsbelehrung`
- A representative content page (e.g. one teacher profile, one blog post)
- The contact form / consent surface
- The Stripe checkout flow if applicable (Phase 7 catches the wording; Phase 2 catches what fires)
- The newsletter signup if applicable
- Logged-in dashboard (skip if no test credentials available)

## Per-route, capture

1. Navigate via `mcp__playwright__browser_navigate`
2. Wait 2 seconds for deferred scripts
3. `browser_network_requests` — all requests
4. `browser_evaluate`:
   ```js
   () => ({
     cookies: document.cookie,
     localStorage: Object.keys(localStorage),
     sessionStorage: Object.keys(sessionStorage),
     localStorageValues: Object.fromEntries(
       Object.keys(localStorage).map(k => [k, localStorage.getItem(k)])
     ),
   })
   ```

## Classification

Each unique third-party domain hit → one of:
- `[SELF]` — your own domain or first-party-proxied
- `[SUPABASE]` — your project's Supabase URL (functional, OK)
- `[R2]` / `[STORAGE]` — your project's storage CDN (functional, OK)
- `[VERCEL]` — Vercel's own infra (`vitals.vercel-insights`, `_vercel/insights`); cookieless OK
- `[STRIPE]` — `js.stripe.com`, `m.stripe.com`, `q.stripe.com` (Phase 7 verifies the checkout-only scoping)
- `[FONT-INLINE]` — `/_next/static/media/*.woff2` or similar self-hosted font path
- `[FLAG]` — anything else

## Critical questions to answer

For each route:
- Are any **cookies** set before the user has had a chance to consent? Classify each as `[STRICTLY-NECESSARY]` (allowed without consent under § 25(2) TDDDG) or `[CONSENT-REQUIRED]`.
- Is `localStorage` written before consent? Same classification.
- Are any third-party fonts loaded? (The Google Fonts wave-trigger — see Phase 1 too.)
- Does GA / GTM / Meta Pixel / Hotjar fire? Cite OLG Frankfurt 6 U 81/23 (2025) — third-party SDK loaders are now independently liable.
- Does Vercel Analytics fire? Confirm it's cookieless (it usually is on default config).
- Cookie banner / CMP present? If yes, does anything fire BEFORE the user clicks?

## Output schema

```markdown
## Phase 2 — Runtime Playwright sweep

Status: PASS | PASS-WITH-NOTES | FAIL

### Per-route table

| Route | Cookies pre-consent | localStorage pre-consent | Third-party domains | Flags |
|-------|---------------------|--------------------------|---------------------|-------|
| /     | NEXT_LOCALE only    | none                     | [SELF]              | none  |
| ...   | ...                 | ...                      | ...                 | ...   |

### Findings

For each [FLAG], a row with: route, what fired, why it's a flag, citation, mitigation.

### Verdict

One paragraph. PASS = no consent-required tech fires before consent on any public route.
```

## Close gate

Lifted verbatim by the sink into each phase-2 issue's "Close gate" section. A phase-2 finding may only be closed when ALL apply:

- [ ] Fresh-visitor headless Playwright sweep against the production URL (NOT a logged-in or pre-consented session) records zero cookies in the `[CONSENT-REQUIRED]` class and zero `localStorage` writes in the `[CONSENT-REQUIRED]` class.
- [ ] Network requests on a fresh visit contain zero `[FLAG]` domains. Allow-list `[SELF]`, `[SUPABASE]`, `[R2]`, `[VERCEL]`, `[STRIPE]` (only on routes that touch checkout), `[FONT-INLINE]`.
- [ ] If a cookie banner/CMP exists: nothing in the `[CONSENT-REQUIRED]` class fires BEFORE the user clicks. The banner itself does not preload any consent-required tracker.
- [ ] Regression guard committed: a Playwright spec (or equivalent end-to-end script) that runs the sweep above on every PR and asserts the same conditions. Name the spec path in the close comment.
- [ ] Re-audit of phase 2 with the toolkit at HEAD against the same production URL: this finding no longer detected.

## Citation chain

- Pre-consent cookies → § 25 TDDDG + BGH I ZR 7/16 "Cookie II" (2020)
- Pre-consent tracking pixel → same
- Pre-consent Google Fonts → LG München I 03 O 17493/20 (2022)
- Third-party SDK independent liability → OLG Frankfurt 6 U 81/23 (2025/2026)

## Notes for the executing subagent

- Production URL is in the project's `compliance.yml` under `production_url:`. Fall back to git remote / package.json if not specified.
- Use `mcp__playwright__*` (headless). Not the `*-debug` variants.
- Screenshots → `.playwright-mcp/` directory, not repo root.
- If the site has a cookie banner, do NOT click it on the first pass — pre-consent behaviour is what matters. Then optionally a second pass after consent.
