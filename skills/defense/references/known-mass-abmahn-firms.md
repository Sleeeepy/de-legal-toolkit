# Pattern recognition for mass-Abmahn campaigns

This file deliberately does **NOT** name specific Anwaltskanzleien. Naming firms as "mass-Abmahn lawyers" without rigorous proof carries defamation risk. Instead, this file lists **pattern criteria** that an LLM can apply to an incoming letter to classify the campaign type without making accusations about individual firms.

For current public watchlists, the skill should consult Tier-3 sources at runtime — they update faster than this static file:

- **heise.de** — search "Abmahnung [year]" for current wave coverage
- **drschwenke.de blog** — Dr. Carsten Schwenke maintains running posts about active campaigns
- **iitr.de/datenschutzanwalt** — weekly digest of Abmahn-relevant activity
- **vzbv press releases** — Verbraucherzentrale Bundesverband tracks consumer-protection campaigns

---

## Campaign pattern categories

Classify the incoming letter by matching against these patterns. The pattern category (NOT the firm name) goes into the defense skill's output.

### Pattern A — Google Fonts batch template (2022-2024 wave)

Indicators:
- Cites **LG München I, 03 O 17493/20** as primary authority
- Demanded amount typically €100-300 individual claim
- Sometimes paired with €200-500 Kostenerstattung for the lawyer
- Letter phrasing references "unrechtmäßige Übermittlung der IP-Adresse"
- Sender claims to have visited the site and been "affected" personally
- Often boilerplate paragraphs identical across many letters

Defense-skill posture: HIGH defensibility. The wave is currently paused pending BGH VI ZR 258/24 → ECJ. OLG Frankfurt 6 U 81/23 cut individual damages to €100 in provoked-visit scenarios. Likely Option B or C (modify-Unterlassung or rejection).

### Pattern B — § 312j Bestellbutton wording

Indicators:
- Cites § 312j(3) BGB
- Screenshot or quote of your checkout button text
- Filed by competitor (not consumer)
- Demands UWG-style cost reimbursement + Unterlassungserklärung
- Damages claim typically lower; main goal is the Unterlassung

Defense-skill posture: Check whether your button text actually fails. If it says "zahlungspflichtig bestellen" or equivalent ("kaufen", "Jetzt kaufen" with payment context), the claim is wrong. If genuinely defective, Option B (narrowed Unterlassung) + fix the code is typical.

### Pattern C — § 312k Kündigungsbutton

Indicators:
- Cites § 312k BGB + recent rulings (LG München I 3 HK O 13796/24 from Jan 2026, OLG Schleswig 6 U 42/25 from Mar 2026)
- Filed by Verbraucherverband or competitor
- Demands an Unterlassung + Wettbewerbsabmahnungspauschale (typically €200-300)
- Often accompanied by a screenshot of the cancellation flow

Defense-skill posture: Fix the flow per the cited rulings (unauthenticated, single-click, label "Vertrag kündigen"). Verify whether the violation actually exists at audit Phase 7b before responding.

### Pattern D — DSAR-extortion / newsletter signup loop

Indicators:
- Cites DSGVO Art. 15 or Art. 82
- The claimant signed up for the newsletter shortly before claiming
- Demands €500-2000 immaterial damages
- Often filed by individual claimants represented by repeat-Anwaltskanzleien

Defense-skill posture: Cite **ECJ C-526/24 Brillen Rottler (19.03.2026)** as defense — first DSAR can be "excessive" under Art. 12(5) when requester acts in bad faith. Likely Option C (rejection) with documented newsletter signup logs as evidence.

### Pattern E — Cookie / tracking without consent

Indicators:
- Cites § 25 TDDDG + Art. 6 / Art. 82 DSGVO
- Names specific cookie or tracking pixel
- Filed by individual claimant or competitor
- Damages €100-300

Defense-skill posture: Verify Phase 2 runtime audit confirms the cookie/pixel actually fires pre-consent. If it does, fix + narrowed Unterlassung. If it doesn't (audit shows clean), Option C (rejection with evidence).

### Pattern F — Copyright / image use

Indicators:
- Cites § 97 / § 97a UrhG
- Names specific image or text on the site
- Claimant is photographer / agency / heir
- Damages €500-3000 (much higher than DSGVO claims)
- Often legitimate — image-rights mills target genuine infringement

Defense-skill posture: This is NOT typically a mass-Abmahn pattern; usually a real claim from a real rights-holder. Run Phase 6 audit to verify whether the image is on the site and whether attribution/licence is in order. If genuine infringement: settle quickly + remove + comply. If false (you have proper licence): Option C with licence evidence.

### Pattern G — State authority enforcement (NOT an Abmahnung)

Indicators:
- Sender is BfDI, LfDI, Bundeszentralamt für Steuern, etc.
- Cites a specific Bescheid number
- Demands specific compliance action or fine

Defense-skill posture: This is NOT in scope for this skill. Engage a Fachanwalt immediately. State authority procedures have different timelines and reply requirements than civil Abmahn letters.

---

## Pattern-classification output

The defense skill should emit a single category (A through G) plus confidence level, NOT a firm name:

```
Letter pattern classification: Pattern A (Google Fonts batch template)
Confidence: HIGH (matches all 5 indicators)
Public watchlist reference: heise.de Abmahn-Welle coverage 2022-2024
Sender identification: NOT CLASSIFIED by the toolkit (defamation risk).
                       Recipient may consult drschwenke.de blog for current sender watchlist.
```

This pattern is then used to choose appropriate defensive findings (e.g. for Pattern A, surface FIND-WAVE-001, DEFENSIVE-2026-001, DEFENSIVE-2026-002).
