---
phase: 7
name: E-commerce — Bestellbutton, Kündigungsbutton, Widerrufsbutton
tags: [bestellbutton, kuendigungsbutton, widerrufsbutton, b2c-checkout, subscription]
applies_when_compliance_yaml: { e_commerce: true } # OR { subscription: true }
---

# Phase 7 — E-commerce

**Goal:** Every B2C checkout flow has compliant Bestellbutton wording (§ 312j BGB). Every subscription has a compliant Kündigungsbutton (§ 312k BGB) per the LG München I 12.01.2026 and OLG Schleswig 04.03.2026 standards. From 19.06.2026 onward, B2C distance contracts also need an electronic Widerrufsbutton.

These are all **static-scrapable patterns** — competitor Abmahn lawyers can detect violations from outside the site without needing accounts. Highest scaling risk in the audit catalogue.

## 7a. Bestellbutton — § 312j(3) BGB

**Statute**: "Bei einem Verbrauchervertrag im elektronischen Geschäftsverkehr [...] hat der Unternehmer die Bestellsituation [...] mit den Worten 'zahlungspflichtig bestellen' oder mit einer entsprechenden eindeutigen Formulierung zu beschriften."

### Compliant button text

| Wording | Status |
|---------|--------|
| "zahlungspflichtig bestellen" | ✓ Statute-explicit, always safe |
| "kostenpflichtig bestellen" | ✓ Equivalent |
| "kaufen" | ✓ Used by BGH-approved e-commerce |
| "zahlungspflichtigen Vertrag schließen" | ✓ Verbose but safe |
| "Jetzt kaufen" | ✓ |

### Non-compliant button text

| Wording | Why |
|---------|-----|
| "Bestellen" | Doesn't make payment obligation clear |
| "Bestellung abschicken" | Same |
| "Anmelden" | Could be interpreted as registration |
| "Weiter" | Vague |
| "Order" | English-only — for DE consumers must be German |
| "Pay now" (English) | Same |

### What to check

- For each Stripe Checkout / custom checkout / subscription signup form:
  - Read the JSX of the submit button
  - Verify the visible text label matches a compliant phrase
  - If using Stripe Elements, check the `submitLabel` / `confirmationRequirement.confirmation_button.label` settings
  - Check for `aria-label` overrides that change accessibility text — must also be compliant

- Pre-contractual information per Art. 246a EGBGB displayed *immediately before* the button:
  - Total price including VAT
  - Delivery/processing terms
  - Payment method
  - Right of withdrawal info (link to Widerrufsbelehrung)

## 7b. Kündigungsbutton — § 312k BGB

**Statute**: introduced 01.07.2022. Required for any consumer subscription concluded online. Recent rulings:

- **LG München I, 3 HK O 13796/24 (12.01.2026, vzbv ./. Microsoft)**: cancellation must be **as easy as signup**. No login wall, no multi-step burial. Must be "transparent and comprehensible at first glance".
- **OLG Schleswig 6 U 42/25 (04.03.2026)**: button labelled "Kündigungswunsch" is misleading under § 5 UWG. Technical errors fall in operator's sphere of responsibility.

### Required button properties

1. **Label**: "Verträge hier kündigen" (statute-required), "Vertrag kündigen", or unambiguous equivalent. **NEVER** "Kündigungswunsch", "Kündigung beantragen", "Kündigung wünschen".
2. **Reachability**: accessible from the public homepage WITHOUT a login. The button (or a clearly-visible link to it) must appear on a page reachable from the homepage without authentication.
3. **Flow**: clicking opens a cancellation page that requires only data necessary to identify the contract. No upsell, no "are you sure" multi-step funnel, no winback offer interstitials gating the actual cancellation submit.
4. **Confirmation**: post-submit, the operator must send confirmation per § 312k(2) BGB.
5. **Technical reliability**: tested and known-working. Errors that block cancellation fall in the operator's sphere (secondary burden of proof).

### What to check

- Find every subscription/recurring product in the codebase
- For each: locate the cancellation flow (probably a server action or `/api/cancel` route)
- Verify the public-route button:
  - Exists? Find the JSX
  - Text label compliant?
  - Reachable without auth?
- Walk the flow once via Playwright (or visually inspect)
- Read any test for the cancellation flow — does it cover the unauthenticated entry point?

## 7c. Electronic Widerrufsbutton — BGB amendment effective 19.06.2026

A new electronic withdrawal button obligation lands 19.06.2026 for B2C distance contracts. Practitioner consensus is that it will mirror § 312k Kündigungsbutton in shape:

- In-product, accessible without authentication
- Unambiguous label (the statutory term is the analog of "Widerruf" — once the BMJ publishes the implementing wording, the audit will reference it)
- Triggers the same 14-day withdrawal mechanism as a paper form would

### What to check (after 19.06.2026)

- Same patterns as Kündigungsbutton but for the Widerruf flow
- If launch is before 19.06.2026: this phase reports "NOT-YET-APPLICABLE — must add by 19.06.2026"
- If launch is after 19.06.2026 or audit run is after: this is FAIL unless implemented

## Output schema

```markdown
## Phase 7 — E-commerce

Status: PASS | PASS-WITH-NOTES | FAIL | NOT-APPLICABLE

### 7a. Bestellbutton

| Checkout flow | Button file:line | Button text | Compliant? |
|---------------|------------------|-------------|------------|
| Teacher subscription | src/components/stripe-checkout-block.tsx:127 | "Jetzt kaufen" | ✓ |
| ... | ... | ... | ... |

### 7b. Kündigungsbutton (if subscription exists)

- Public-route button found at: <file:line> | NOT FOUND
- Label: "..." | NOT FOUND
- Compliant per LG München I 3 HK O 13796/24 + OLG Schleswig 6 U 42/25?

### 7c. Electronic Widerrufsbutton (after 19.06.2026)

- Status: implemented / not-yet-applicable / overdue

### Verdict
```

## Close gate

Lifted verbatim by the sink into each phase-7 issue's "Close gate" section. Phase-7 findings are uniformly HIGH (static-scrapable patterns + active wave of competitor Abmahnungen).

### 7a. Bestellbutton

- [ ] Every checkout-flow submit button has a visible label matching the compliant-text table above (verbatim or BGH-approved equivalent). Non-compliant entries in the table appear nowhere in production JSX.
- [ ] No `aria-label` override on a checkout button changes the accessibility text to a non-compliant phrase.
- [ ] Pre-contractual Art. 246a EGBGB information (total price incl. VAT, delivery/processing, payment method, Widerrufs link) renders immediately before the button on every checkout page.
- [ ] Re-audit of phase 7a: zero non-compliant buttons.

### 7b. Kündigungsbutton

- [ ] Public-route Kündigungsbutton exists, reachable from the homepage without authentication.
- [ ] Button label is "Verträge hier kündigen", "Vertrag kündigen", or unambiguous equivalent. Specifically not "Kündigungswunsch", "Kündigung beantragen", "Kündigung wünschen" — these are FAIL per OLG Schleswig 6 U 42/25.
- [ ] Cancellation flow requires only data necessary to identify the contract. No login wall, no winback interstitial gating the cancellation submit, no "are you sure" multi-step funnel.
- [ ] § 312k(2) BGB post-submit confirmation is sent.
- [ ] Cancellation flow walked end-to-end (Playwright spec or manual) on the production URL without errors. Errors in this flow fall in the operator's sphere of responsibility — they FAIL the gate even if "technical".
- [ ] Re-audit of phase 7b: button present, label compliant, unauthenticated path works.

### 7c. Electronic Widerrufsbutton (audit run after 19.06.2026)

- [ ] In-product Widerrufsbutton implemented for B2C distance contracts, reachable without authentication, mirroring Kündigungsbutton shape.
- [ ] Triggers the same 14-day withdrawal mechanism as the paper form.

### Regression guard (HIGH — all of 7a/7b/7c)

- [ ] Playwright spec committed AND wired into CI that walks (a) the checkout flow asserting button text matches the compliant table, (b) the public-route Kündigungsbutton existence + label + unauthenticated reachability, (c) post-19.06.2026 the Widerrufsbutton equivalent. Name the spec path in the close comment.

## Citation chain

- Bestellbutton → § 312j(3) BGB
- Pre-contractual info → Art. 246a § 1 EGBGB
- Kündigungsbutton requirements → § 312k BGB
- Kündigungsbutton ease-of-cancellation → LG München I 3 HK O 13796/24 (12.01.2026)
- Kündigungsbutton label specificity → OLG Schleswig 6 U 42/25 (04.03.2026)
- Electronic Widerrufsbutton → BGB amendment effective 19.06.2026 (BMJ implementing text — verify before audit run)
