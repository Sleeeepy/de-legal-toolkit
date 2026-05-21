# Case-law landscape 2024-2026

The rulings and statute changes that actually matter for German digital-law pre-launch audits. Reviewed and curated — not exhaustive. Verify any cited holding at the primary source before relying on it; this list goes stale.

## Statute changes since Jan 2024

| Date | Change | Where to verify |
|------|--------|-----------------|
| 14 Feb 2024 | **TMG largely repealed; replaced by DDG.** § 5 TMG → § 5 DDG (Impressum). § 25 TTDSG → § 25 TDDDG (cookie consent). Substantive content unchanged in both cases. | https://www.gesetze-im-internet.de/ddg/ |
| 17 Feb 2024 | **DSA (Regulation EU 2022/2065)** fully applicable to all online intermediaries (VLOPs since Aug 2023). For small DE sites the binding obligations are §§ 14-18 DSA (notice-and-action, T&C transparency, complaint handling). "Very small enterprises" (under 50 employees / €10m turnover) are exempt from the major Art. 15+ transparency obligations. | https://eur-lex.europa.eu/eli/reg/2022/2065 |
| 13 Mar 2024 | **AI Act adopted** (Regulation EU 2024/1689); phased entry. Feb 2025: prohibited practices binding. Aug 2025: GPAI obligations. Aug 2026: high-risk system obligations. Art. 50 transparency (chatbot disclosure, AI-content labelling) applies broadly. | https://eur-lex.europa.eu/eli/reg/2024/1689 |
| Oct 2023 | **VDuG (Verbraucherrechtedurchsetzungsgesetz)** in force. Introduced the **Abhilfeklage** (representative collective consumer action). Has not produced a mass-Abmahn wave through 2026 but lowers the bar for collective claims. | https://www.gesetze-im-internet.de/vdug/ |
| 1 Aug 2022 | **§ 312k BGB Kündigungsbutton** in force. Required for any subscription-style consumer contract concluded online — button labelled "Verträge hier kündigen" or equivalent, leading to a cancellation form. Multiple Abmahnungen 2023-2024 for missing or mis-labelled buttons. | https://www.gesetze-im-internet.de/bgb/__312k.html |

## In-window 2026 verified rulings (Jan-May 2026)

### LG München I — 3 HK O 13796/24 (vzbv ./. Microsoft, 12 Jan 2026)

- **Holding**: Online cancellation under § 312k BGB must be **as easy as signup**. No login wall, no multi-step burial, no hidden subpages. The cancellation route must be "transparent, unambiguous, and comprehensible at first glance". Action brought by Verbraucherzentrale Baden-Württemberg.
- **Why it matters**: Verbraucherverbände run § 312k template claims; the bar is now visibly high. Any monthly subscription must expose an unauthenticated cancellation button.
- **Source**: https://dejure.org/dienste/vernetzung/rechtsprechung?Text=3%20HK%20O%2013796/24

### OLG Schleswig — 6 U 42/25 (4 Mar 2026)

- **Holding**: Labelling the cancellation button "Kündigungswunsch" is misleading under § 5 UWG because termination is a unilateral declaration, not a request. Technical errors on the cancellation flow fall in the operator's sphere of responsibility (secondary burden of proof). Revision denied.
- **Why it matters**: Hardens § 312k as competitor-Abmahnbar under UWG. Button wording AND technical reliability are now expressly enforceable. Use "Vertrag kündigen", never "Kündigungswunsch", never "Kündigung beantragen".
- **Source**: https://www.dr-bahr.com/news/unternehmen-darf-online-kuendigung-des-kunden-nicht-erschweren-bezeichnung-kuendigungswunsch-techn-fehlermeldung.html

### OLG Frankfurt — 6 U 81/23 (11 Dec 2025, broadly published Jan 2026)

- **Holding**: Any party whose code stores cookies without valid consent is liable under § 25 TDDDG and Art. 82 DSGVO, including **third-party tech providers** (tag managers, analytics SDKs), not only the site operator. Liability confirmed but immaterial damages **reduced from €1,500 to €100** because the plaintiff visited specifically to provoke evidence.
- **Why it matters**: Widens defendant pool (any SDK/tag-manager vendor) but cuts damages economics for mass-Abmahn schemes. Sites that audit their own SDK loading should be fine.
- **Source**: https://dejure.org/dienste/vernetzung/rechtsprechung?Gericht=OLG+Frankfurt&Datum=11.12.2025&Aktenzeichen=6+U+81/23

### ECJ — C-526/24 (Brillen Rottler, 19 Mar 2026)

- **Holding**: Even a *first* Art. 15 DSAR can be classified as "excessive" under Art. 12(5) DSGVO where the requester acts in bad faith (e.g. signs up to a newsletter solely to manufacture an Art. 82 damages claim). Controllers may refuse or charge a fee but bear a high burden of proof — publicly available patterns of repeat-requesting plus claims activity may be used as evidence. Art. 82(1) damages remain available even where the Art. 15 breach does not itself involve "processing".
- **Why it matters**: **Defensive ruling**. Documented shield against "DSGVO-hopping" newsletter+DSAR+damages mills. Keep newsletter signup logs (timestamp + IP + DOI trail) to substantiate the abuse defense if invoked.
- **Source**: https://curia.europa.eu/site/upload/docs/application/pdf/2026-03/cp260038en.pdf

### OLG Bamberg — 3 UKl 5/25 e (18 Mar 2026)

- **Holding**: DSA accessibility requirements for de-personalisation and reporting menus on TikTok. Revision admitted.
- **Why it matters**: Platform-specific (VLOP duties under DSA Art. 27/38). No relevance to non-VLOP marketplaces or service sites.

## Imminent statute triggers (firm dates within months of mid-2026)

| Date | Source | What changes | Abmahn vector |
|------|--------|--------------|---------------|
| 19 Jun 2026 | BGB amendment (electronic Widerrufsbutton) | B2C distance contracts must offer an electronic withdrawal button mirroring § 312k Kündigungsbutton | Wettbewerber-Abmahnung expected; practitioners flag as next § 312k-style wave |
| 2 Aug 2026 | AI Act Art. 50 + Art. 113 phase-in | Chatbot disclosure obligation (Art. 50(1)) + AI-generated public-interest text labelling (Art. 50(4)) bind without grace period | Wettbewerber-Abmahnung is the practitioner-consensus enforcement channel; first wave likely on launch dates |

## Wave-trigger rulings (scalable Abmahn vectors)

These rulings produced sustained Abmahn campaigns because they target patterns a scraper can detect at scale. **Order: most recent / most active first.**

### LG München I — 03 O 17493/20 (Google Fonts, 20 Jan 2022)

- **Holding**: Loading Google Fonts from `fonts.googleapis.com` without user consent constitutes an unlawful DSGVO transfer of the visitor's IP to Google LLC (US). Court awarded €100 immaterial-damages claim under Art. 82 DSGVO.
- **Why it's a wave**: Scrapers can grep for `fonts.googleapis.com` in millions of sites. 2022-2023 saw thousands of template Abmahnungen.
- **Mitigation**: Self-host fonts. `next/font/google` and `next/font/local` do this automatically by inlining at build time.
- **Status**: Still active. Many lawyers have shifted from €100 Schadenersatz to €170-300 Aufwendungsersatz claims; same underlying scraper logic.
- **Primary source**: https://openjur.de/u/2392252.html

### § 312j BGB Bestellbutton

- **Holding**: The button completing a B2C online order must read "zahlungspflichtig bestellen" or use **only** equivalent wording explicitly making the payment obligation clear. Wording deemed insufficient by courts: "Jetzt kaufen", "Bestellen", "Bestellung abschicken", "Order", "Pay now" (without the obligation phrasing).
- **Why it's a wave**: Trivially scrapable HTML — just grep the checkout submit button's label.
- **Mitigation**: Audit `<button>` text in every checkout flow. Stripe Elements lets you control the label; default Stripe wording is **not** compliant.
- **Status**: Active since 2014; one of the longest-running Abmahn lines.

### Pre-consent cookies / tracking pixels

- **Holding** (multiple rulings; foundational: BGH I ZR 7/16 "Cookie II" 28 May 2020): Non-essential cookies and tracking pixels require prior, specific, freely-given consent — opt-out is insufficient. § 25 TDDDG (formerly § 25 TTDSG) codifies this.
- **Why it's a wave**: Browser-detectable — a scraper loads the page headless, checks `document.cookie` and outbound requests before any click.
- **Mitigation**: No GA/GTM/Meta Pixel/Hotjar/etc. firing before explicit opt-in. Strict-necessary-only cookies pre-consent. Cookieless analytics (e.g. Vercel Analytics in cookieless mode, Plausible) are acceptable under Art. 6(1)(f) without § 25 TDDDG consent.
- **Status**: Active. Less attention than fonts but ongoing.

### Newsletter single-opt-in / missing DOI

- **Holding**: BGH I ZR 218/07 (Double-Opt-In, 10 Feb 2011) — confirmed-opt-in via working confirmation link is the only safe path under § 7 UWG; single-opt-in or pre-checked boxes are spam under § 7(2) UWG (+ DSGVO Art. 6(1)(a) consent invalidity).
- **Why it's a wave**: Trivially testable — submit a fake email, see if a real confirmation step happens or whether you're added straight to the list.
- **Mitigation**: Standard DOI flow: form → email confirmation → only then DB write. The Resend `resend-react-email` patterns implement this if used correctly.
- **Status**: Steady drumbeat, not spiking.

## One-off recent rulings to note (not waves but worth tracking)

### ECJ C-621/22 (Schufa scoring, 7 Dec 2023)

- **Holding**: Automated credit scoring that has decisive effect on contract conclusion is an Art. 22 DSGVO automated decision and requires the data subject's explicit consent / specific legal basis.
- **Relevance**: Mostly affects FinTech and credit; not directly Abmahn-relevant for non-financial sites. But it does tighten the Art. 22 disclosure obligation in any Datenschutz that mentions scoring/profiling.

### OLG Köln 6 U 58/22 ("Google Maps Embed", 3 Nov 2023)

- **Holding**: Embedding Google Maps via the standard JS embed without consent is a DSGVO violation comparable to Google Fonts.
- **Wave potential**: Medium — same scraper logic as Fonts, but fewer sites use Google Maps embeds, and the two-click solution (preview image + click-to-load) is standard mitigation.
- **Mitigation**: Use OpenStreetMap (e.g. Leaflet+OSM tiles) or implement a click-to-load shim before the Google Maps iframe.

### LG Köln (cookieless analytics, various 2024-2025)

- **Trend**: Multiple LG-level rulings have accepted cookieless server-side analytics (Plausible, Matomo without cookies, Vercel Analytics cookieless mode) as compatible with § 25 TDDDG and Art. 6(1)(f) DSGVO. No BGH ruling yet; LG/OLG level only.
- **Relevance**: Provides defensible cover for cookieless analytics without a consent banner. Document the legitimate-interests balancing test in the Datenschutz.

## Things that are NOT waves

These get Abmahn-Drohung letters but rarely produce binding rulings or sustained campaigns:

- **Missing telephone in Impressum**: § 5 DDG accepts contact form OR phone. Most demand letters here settle for nuisance value or are dropped.
- **Missing Verantwortlicher § 18 MStV on non-editorial sites**: only enforceable where genuine editorial content exists.
- **USt-IdNr missing on Kleinunternehmer site**: not required under § 19 UStG. Speculative letters get rebutted.
- **OS-Plattform link missing on a site that doesn't sell to consumers**: Art. 14 ODR-VO only applies to B2C-online-trader scenarios.

## Sources kept for periodic re-check

- Heise Recht (https://www.heise.de/recht/) — weekly news.
- Datenschutz-Notizen (https://www.datenschutz-notizen.de) — Heise's privacy blog.
- LTO Legal Tribune Online (https://www.lto.de) — legal trade press.
- DSK Datenschutzkonferenz publications (https://www.datenschutzkonferenz.de) — joint LfDI position papers (semi-binding).
- BfDI Tätigkeitsberichte (annual) — flags enforcement priorities.
