# Current findings — DE compliance landscape

**Last updated:** 2026-05-31
**Update mechanism:** Run `/legal-research` with a "case-law sweep" prompt; new findings get committed here after review. Findings may also land from downstream project feedback (e.g. FIND-2026-005 from the MusikMeister audit) — same review bar, citation required.

This file is the canonical input to the `audit` skill. Every entry has a `status` in `lifecycle.json`.

---

## Active rulings (cite when raising audit findings)

### FIND-2026-001 — § 312k Kündigungsbutton ease-of-cancellation
- **Citation:** LG München I, Urteil v. 12.01.2026, 3 HK O 13796/24 (vzbv ./. Microsoft)
- **Topic:** § 312k BGB
- **Holding:** Online cancellation must be as easy as signup. No login wall, no multi-step burial. Must be "transparent, unambiguous, and comprehensible at first glance".
- **Abmahn relevance:** HIGH. Verbraucherverbände actively run § 312k template claims.
- **Audit phase:** 7b
- **Action when found:** raise as HIGH severity if cancellation flow violates the standard.

### FIND-2026-002 — § 312k Kündigungsbutton label specificity
- **Citation:** OLG Schleswig, Urteil v. 04.03.2026, 6 U 42/25
- **Topic:** § 312k BGB + § 5 UWG
- **Holding:** "Kündigungswunsch" label is misleading. Technical errors on cancellation flow fall in operator's sphere (secondary burden of proof).
- **Abmahn relevance:** HIGH. Competitor-Abmahnbar under UWG.
- **Audit phase:** 7b
- **Action when found:** raise as HIGH if label is "Kündigungswunsch" / "Kündigung beantragen" / "Kündigung wünschen". Acceptable: "Vertrag kündigen" / "Verträge hier kündigen".

### FIND-2026-003 — Third-party SDK independent liability
- **Citation:** OLG Frankfurt, Urteil v. 11.12.2025, 6 U 81/23
- **Topic:** § 25 TDDDG + Art. 82 DSGVO
- **Holding:** Third-party tech providers (tag managers, analytics SDKs) are independently liable for cookies without consent. Damages reduced to €100 when plaintiff "provoked" violation.
- **Abmahn relevance:** MEDIUM. Widens defendant pool; cuts damages economics for individual claimants.
- **Audit phase:** 1, 2
- **Action when found:** flag any third-party SDK that loads pre-consent; verify Phase 2 runtime confirms no pre-consent fires.

### FIND-2026-004 — DSAR abuse defensive ruling
- **Citation:** EuGH, Urteil v. 19.03.2026, C-526/24 (Brillen Rottler)
- **Topic:** DSGVO Art. 15 + Art. 82
- **Holding:** First DSAR can be "excessive" under Art. 12(5) where requester acts in bad faith. Controllers may refuse/charge but bear high burden of proof.
- **Abmahn relevance:** DEFENSIVE. Shield against fake-signup → DSAR → Art. 82 claim mills.
- **Audit phase:** 4 (sub-processor — newsletter DOI logging), Datenschutz / DSAR SOP
- **Action when found:** ensure newsletter signup preserves timestamp + IP + DOI trail for the abuse-defense paper trail.

### FIND-2026-005 — Over-collected consent (Art. 13 / contract step gated as Art. 6(1)(a) consent)
- **Citation:** DSK Kurzpapier Nr. 20 (Einwilligung nach der DSGVO) + DSGVO Art. 7(3)+(4), Art. 6(1)(a)/(b)/(f), Rec. 32 + 43. **Not a court ruling** — this is a regulatory-body (Datenschutzkonferenz) position + statute, so there is no single AZ. Cite the statute + Kurzpapier, same shape as FIND-WAVE-002 (§ 312j without a single AZ).
- **Topic:** DSGVO Art. 6(1)(a) / Art. 7(3)+(4) / Art. 13
- **Holding (position):** A consent is valid only where the legal basis genuinely *is* Art. 6(1)(a)/9(2)(a) — freely given and withdrawable. Modelling an Art. 13 information duty (e.g. acceptance of the Datenschutzerklärung) or an Art. 6(1)(b) contract step as a gating, recorded consent is over-collection: a Kopplungsverbot violation (Art. 7(4)) where the box is required, and a non-withdrawable pseudo-consent (Art. 7(3)) where the act is logically un-doable. The Datenschutzerklärung is an *information notice* — presented (linked/inline), never accepted via a gating tick.
- **Abmahn relevance:** MEDIUM — needs runtime/context, **not statically scrapable**. Elevated for any DSGVO self-audit because it is a *false sense of compliance*: the box looks more compliant while being less so, so existing checks rubber-stamp it (symmetry holds, doc mentions it, code records it).
- **Audit phase:** 3b (consent-kind legal-basis validity); secondary phase 2 (the signup consent surface).
- **Action when found:** Audit each consent kind in the codebase enum 1:1. A kind that maps to Art. 6(1)(b)/(f) or a pure Art. 13 duty, or that cannot be withdrawn, is over-collection → **FAIL**. A required "Ich akzeptiere die Datenschutzerklärung" checkbox → **FAIL** (Kopplungsverbot). Remediation: convert to an inline Art. 13 notice; a version-stamp kept for the Rechenschaftspflicht trail is fine only if it no longer gates the flow as a consent.
- **Motivating case:** MusikMeister (okapi-music), issue #95 — Datenschutz added as a gated, recorded consent kind across four signup entry points; ratified by a `/grill-me` DSGVO session citing DSK "never bundle" guidance. It passed every existing audit check yet was an over-collected, non-withdrawable pseudo-consent. Fixed 2026-05-31 by converting to an inline Art. 13 notice (version-stamp retained for Rechenschaftspflicht, not as a consent gate). Exactly the class of error the 3b check now catches.

## Historical wave-trigger baseline (still active)

### FIND-WAVE-001 — Google Fonts wave (paused, ECJ pending)
- **Citation:** LG München I, Urteil v. 20.01.2022, 03 O 17493/20
- **Topic:** Google Fonts loaded from googleapis.com without consent → DSGVO Art. 6/82
- **Holding:** €100 Schadenersatz for unlawful third-country transfer of IP via Google Fonts CDN.
- **Wave status:** Paused. BGH VI ZR 258/24 (28.08.2025) referred Vorlagefragen to ECJ; lower courts staying. Reanimation possible after ECJ ruling.
- **Audit phase:** 1
- **Action:** any `fonts.googleapis.com` / `fonts.gstatic.com` reference in `src/` or `public/` is HIGH. Mitigation: self-host via `next/font/google` (auto-inlines).

### FIND-WAVE-002 — § 312j Bestellbutton wording
- **Citation:** § 312j(3) BGB (in force since 2014); multiple OLG enforcements
- **Topic:** B2C checkout button label
- **Holding:** Submit button on B2C checkout must read "zahlungspflichtig bestellen" or unambiguous equivalent.
- **Wave status:** Steady drumbeat — one of the longest-running Abmahn lines.
- **Audit phase:** 7a
- **Action:** verify each checkout submit button's visible text.

### FIND-WAVE-003 — Pre-consent cookies / tracking
- **Citation:** BGH I ZR 7/16 (Cookie II, 28.05.2020); § 25 TDDDG
- **Topic:** Non-essential cookies and tracking pixels require prior opt-in
- **Wave status:** Active but less spiked than 2020-2022 — most sites have banners. Pre-consent firing still a textbook Abmahn.
- **Audit phase:** 2
- **Action:** Phase 2 Playwright must show zero non-essential cookies / tracking firing before consent.

### FIND-WAVE-004 — Newsletter Double-Opt-In
- **Citation:** BGH I ZR 218/07 (10.02.2011); § 7 UWG
- **Topic:** Single-opt-in newsletter signup → spam under § 7(2) UWG → Abmahn
- **Wave status:** Steady. Easy to test (submit fake email, see if real confirmation fires).
- **Audit phase:** 7 (e-commerce) or general doc audit
- **Action:** verify DOI flow exists. Newsletter signup → confirmation email → only-then-DB-write.

## Imminent statute triggers (firm dates)

### IMMINENT-2026-001 — Electronic Widerrufsbutton (19.06.2026)
- **Source:** BGB amendment, BMJ implementing wording
- **What:** B2C distance contracts must offer an in-product electronic withdrawal route mirroring § 312k Kündigungsbutton
- **Vector:** Wettbewerber-Abmahnung. Practitioners flag as next § 312k-style wave.
- **Audit phase:** 7c
- **Action:** projects with `e_commerce: true` and launch date > 19.06.2026 must implement.

### IMMINENT-2026-002 — AI Act Art. 50 phase-in (02.08.2026)
- **Source:** Regulation (EU) 2024/1689 Art. 50 + Art. 113
- **What:** Chatbot disclosure (Art. 50(1)) + AI-generated public-interest text labelling (Art. 50(4)) binding without grace period.
- **Vector:** Wettbewerber-Abmahnung (practitioner consensus).
- **Audit phase:** 8
- **Action:** projects with `ai_features: true` must comply — either label AI output OR document editorial-responsibility carve-out (acceptance logging + UI note + Datenschutz framing).
- **Carve-out:** Art. 50(4) sentence 2 has a "human review / editorial responsibility" exception. Editorial-responsibility allocation is the project's choice; toolkit assumes this is the default mitigation.

## Defensive postures (infrastructure to have BEFORE precedent forces it)

These are not violations and they're not enforceable rulings yet — they're defensive evidence-trails the catalogue tracks so the audit doesn't quietly judge "no current violation = no work outstanding" when, in fact, infrastructure work is needed before an imminent regulation binds.

Per-surface scoped: every AI / e-commerce / data-handling surface in a project re-triggers the relevant posture check.

### FIND-POSTURE-2026-AI-TRAIL — Art. 50(4) editorial-responsibility evidence trail
- **Topic:** Art. 50(4) AI Act + Recital 134 editorial-responsibility / human-review exception
- **Defensive holding:** Where AI-generated text is reviewed, accepted, and published under a user's identity, the operator's strongest Art. 50(4) defence is a *contemporaneous evidence trail* proving the human review actually happened. Absent precedent (Commission Art. 50 guidelines aren't expected until well into Q3 2026), an aggressive reading of "matters of public interest" or "editorial responsibility" by a competitor-Anwalt or a supervisory authority could otherwise force a labelling obligation onto profile / blog / dashboard AI surfaces.
- **Abmahn relevance:** LOW-but-time-bounded. No precedent yet. Defensive infrastructure is cheap to build now and expensive to retrofit during an active Abmahn.
- **Trigger date:** 2026-08-02 (when Art. 50 binds without grace period).
- **Audit phase:** 8.
- **Action when found:** For each AI surface that emits text into public user-facing content (profile editor, blog assistant, chatbot, content rewriter, etc.) the audit expects all three pieces:
  1. **Acceptance-log table** persisting at minimum `ai_suggestion`, `final_text`, `was_edited`, `accepted_at`, `user_id` per event
  2. **Inline responsibility note** in the UI of the affected surface — not just on the consent modal, not just in the import flow. Pattern: "Du bist verantwortlich für den finalen Text — bitte prüfen, bevor du übernimmst." Visible in screenshots.
  3. **Datenschutz framing** of the editorial-control exception in regulation language. Cites Art. 50(4) sentence 2 explicitly; states the operator's position that the user holds editorial responsibility for AI-touched published content.
- **Raise as:** MEDIUM, separately per surface where any of (1)–(3) is missing. Per-surface scoping prevents this becoming a one-time tick — every new AI feature re-triggers the check.
- **Why not HIGH:** no precedent → not imminently Abmahnbar → MEDIUM. Will be re-classified once Commission guidelines land or first OLG ruling appears.

## Statute baseline (current as of 2026-05-21)

- **§ 5 DDG** replaces § 5 TMG (Feb 2024). Citations of "§ 5 TMG" in Impressum docs are stale.
- **§ 25 TDDDG** replaces § 25 TTDSG (Feb 2024). Citations of "§ 25 TTDSG" are stale.
- **DSA** (Reg. EU 2022/2065) fully applicable to all online intermediaries since 17.02.2024. Most small DE sites are exempt from Art. 15+ obligations under the "very small enterprises" carve-out (under 50 employees / €10m turnover).
- **AI Act** (Reg. EU 2024/1689) — Chapter II prohibited practices binding since 02.02.2025; GPAI obligations since 02.08.2025; full Chapter IV (transparency, incl. Art. 50) from 02.08.2026; high-risk system obligations from 02.08.2027.
- **VDuG** (Verbraucherrechtedurchsetzungsgesetz, Oct 2023) — Abhilfeklage available; no Abmahn-wave-equivalent through mid-2026.

## Findings retired or wave-defensive

(Tracked here for transparency.)

- **DEFENSIVE-2026-001**: OLG Frankfurt 6 U 81/23 cut Cookie/Fonts non-material damages to €100 when plaintiff "provoked" violation — undercuts mass-Abmahn economics for individual claimants.
- **DEFENSIVE-2026-002**: BGH VI ZR 258/24 (28.08.2025) ECJ-referral on Google Fonts has frozen the wave.

---

## Last sweep metadata

- **Date:** 2026-05-21
- **Window covered:** 2026-01-01 to 2026-05-21
- **Skill version:** legal-research v0.1
- **Run by:** manual orchestration (3 parallel subagents — BGH/ECJ, OLG/LG, Tier-3 narrative)
- **Output token usage:** ~150K subagent + <10K orchestration
- **Materially-new findings:** 4 in-window + 2 imminent triggers
