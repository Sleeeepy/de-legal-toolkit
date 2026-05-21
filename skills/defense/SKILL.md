---
name: defense
description: |
  Assess an incoming Abmahnung / cease-and-desist letter against the toolkit's findings catalogue and the project's actual codebase. Produces a factual claim assessment, risk score, options menu, redline of the demanded Unterlassungserklärung, and three draft reply letter patterns (demand-evidence / narrowed-Unterlassung / reject-as-unfounded). Activate on "received Abmahnung", "got cease and desist", "Abmahn letter assessment", "responding to legal letter", "Unterlassungserklärung review", "DSGVO claim letter". NOT a substitute for a Fachanwalt — outputs are decision-support, not legal advice.
metadata:
  category: Defense & Response
  pairs-with:
    - skill: audit
      reason: defense runs targeted audit phases to verify whether the claimed violation actually exists on the live site.
    - skill: legal-research
      reason: defense cross-references the letter's cited rulings against the findings catalogue to check whether the citation is current or superseded.
---

# Defense — Abmahn / cease-and-desist assessment

> ⚠️ **NOT LEGAL ADVICE.** This skill produces a structured decision-support output to help you understand what an Abmahnung claims, whether the claim has technical merit, and what your typical response options are. **You are the person responsible for the response you actually send.** For a contested matter, an Anwaltskanzlei that specialises in IT-Recht (Fachanwalt) is the only authoritative interpretation. The toolkit can help you decide whether to engage one and what to ask them; it cannot replace one.

Run from the project root that received the letter. The skill needs to audit the actual codebase to verify whether the claim has merit.

---

## What it does

1. **Parses the letter** — claimed violation, cited rulings, demanded remedy, deadline, sender.
2. **Cross-references findings** — is the cited ruling still current per `findings/_current.md`? Is there a wave-defensive ruling that helps?
3. **Verifies the claim** — runs targeted phase(s) of the audit skill against the codebase to confirm whether the pattern actually exists.
4. **Recognises sender patterns** — checks against public watchlists (heise.de warnings, vzbv reports, drschwenke.de). Does NOT name specific firms (defamation risk); identifies by patterns: known mass-Abmahn template letter, identical wording sent to N other sites, unrealistic damages claim, etc.
5. **Outputs decision-support** — risk score, options menu, Unterlassungserklärung redline, three draft reply letter patterns. Each output explicitly marked NOT LEGAL ADVICE.

## What it does NOT do

- Give legal advice
- Predict litigation outcomes
- Negotiate on your behalf
- Replace a Fachanwalt's review
- Send anything anywhere — output is local only
- Process letters containing third-party personal data without your review (you redact before pasting)

---

## When to use

- An Abmahnung has arrived in the mail or via email
- Deadline is days away and you need a quick triage
- You want to know whether to ignore, narrow, settle, or engage a Fachanwalt
- You want to understand which clauses of the demanded Unterlassungserklärung are typically overbroad

**Do NOT use if:**
- The matter is already in court (Klage / einstweilige Verfügung) — engage a Fachanwalt immediately
- The letter is from a state authority (BfDI, LfDI, Bundeszentralamt für Steuern) — different procedural rules apply, also engage a Fachanwalt
- The letter alleges criminal conduct — different framework entirely

---

## Workflow

```
1. User invokes /defense from the project root.
2. Skill prompts: "Paste the letter text. Redact personal info first if you want."
3. User pastes (or attaches PDF; skill will OCR if possible).
4. Skill parses for:
   - Sender (Anwaltskanzlei name + address)
   - Claimed violation
   - Cited statute / ruling (in any format)
   - Demanded remedy (Unterlassung + Schadenersatz €X + Kostenerstattung €X)
   - Deadline (counted from receipt date)
   - Pre-formulated Unterlassungserklärung (if attached)
5. Skill cross-references:
   - Each cited ruling against findings/_current.md + lifecycle.json
   - Each cited statute against gesetze-im-internet.de (or skip if recently verified)
   - Sender pattern against known-mass-abmahn-firms.md (pattern recognition, not name lookup)
6. Skill verifies the claim:
   - Identifies which audit phase the claim maps to (e.g. Google Fonts claim → Phase 1)
   - Spawns a targeted subagent to check whether the pattern exists on the live site
7. Skill emits the structured output (see schema below).
8. User reviews and decides. The skill does not send anything.
```

---

## Output schema

```markdown
# Defense Assessment

> ⚠️ NOT LEGAL ADVICE. Decision-support output. For final action, consult a Fachanwalt für IT-Recht.

## Letter summary
- Sender: <Kanzlei name as it appears>
- Date: <YYYY-MM-DD>
- Deadline: <YYYY-MM-DD> (N days from now)
- Claimed violation: <what>
- Cited authority: <statute / ruling>
- Demanded remedy:
  - Unterlassungserklärung (pre-formulated)
  - Schadenersatz: €X
  - Kostenerstattung: €Y
  - Total claim: €(X+Y)

## Claim assessment
- Does the cited ruling still apply? <yes / superseded / wave-defensive ruling cuts it>
- Does the violation actually exist on your site? <yes / no / partial — with file:line evidence>
- Sender pattern: <known-mass-Abmahn template / unique letter / state authority — never names specific firms>

## Risk score: <LOW | MEDIUM | HIGH>

Reasoning:
- <1-2 sentences on what drives the score>

## Your options (ranked by typical effectiveness)

### Option 1 — <short label>
- What it means: ...
- When it fits: ...
- Risk: ...
- Cost: ...

### Option 2 — ...

(Typical options: ignore-as-frivolous / demand-evidence / modify-Unterlassung / settle-reduced / engage-Fachanwalt)

## Unterlassungserklärung redline

If the letter included a pre-formulated declaration, this section shows:

- Clauses typically overbroad
- Narrower alternatives
- Clauses that are standard and probably fine

## Draft reply letter (CHOOSE ONE, REVIEW CAREFULLY)

> ⚠️ Before sending: verify dates, addresses, claim numbers. The skill cannot read PDF metadata. The skill output may contain errors or paraphrases. The toolkit accepts NO LIABILITY for the consequences of a sent letter. If the matter is non-trivial, a Fachanwalt's signature on the letter shifts liability and signals seriousness to the sender.

### Draft A — demand evidence
<formal German letter, polite, asks for evidence the alleged violation occurred, IP/timestamp of the alleged visit, full identification of the affected person>

### Draft B — narrowed Unterlassung
<formal German letter, declines the pre-formulated declaration as overbroad under § 305c BGB, offers a narrowed version excluding the overbroad clauses, no admission of liability>

### Draft C — reject as unfounded
<formal German letter, denies the claim on the basis the cited ruling is superseded / wave-defensive / the violation does not exist on the site, points to the verifying evidence, asks for withdrawal>

## What NOT to do

- Do NOT sign the pre-formulated Unterlassungserklärung as-is. Always overbroad.
- Do NOT pay the demanded amount before negotiating. Reduced settlements are routine.
- Do NOT ignore the deadline. Even if you intend to reject, send a reply within the deadline noting the rejection.
- Do NOT discuss the letter publicly (Twitter / Mastodon / forums) before responding. Public statements can be used against you.
- Do NOT delete or modify the affected code before consulting a Fachanwalt if the matter is serious. Modifications can be framed as acknowledgement.

## When to engage a Fachanwalt

- Risk score: HIGH
- Total claim > €1000
- Letter cites recent or unsettled rulings the toolkit's findings have not yet verified
- You're considering Option B or C and want a signature that shifts liability
- The sender has filed against you before
- You are unsure about any of the above

Budget: €300-500 for a focused review of a single Abmahnung. Worth it if claim > €1000 or if uncertain.

## Documents to keep

- Original Abmahnung (with envelope showing receipt date, if mailed)
- All reply correspondence
- The Unterlassungserklärung you signed (if any), with redline visible
- Any payment receipt
- The audit output that informed your response

Retention: 3 years (general statute of limitations § 195 BGB).
```

---

## Anti-patterns

### Never:

1. **Name specific Anwaltskanzleien in the output as "mass-Abmahn firms".** Defamation risk for the toolkit and the user. Use pattern criteria only.
2. **Auto-send anything.** Output is decision-support, period.
3. **Frame the toolkit's output as legal advice.** Every output section has the NOT LEGAL ADVICE disclaimer; do not soften it.
4. **Commit Abmahn letter content to git.** Process locally only; suggest user not paste into a tracked file.
5. **Assume the cited ruling is current.** Always cross-reference against `findings/_current.md` and `lifecycle.json` — many Abmahn lawyers cite rulings that have been narrowed or superseded.

### Common mistakes:

```
❌ Output says "your site clearly violates DSGVO" based on letter alone.
✅ Output says "the letter claims X. Audit verifies X exists at file:line — claim has merit"
   OR "Audit confirms X does NOT exist; claim appears speculative".

❌ Skill drafts a confident reply that admits parts of the claim.
✅ Skill drafts three template patterns each marked NOT LEGAL ADVICE,
   prompting the user to choose and review.

❌ Skill names "RA XYZ" as a known mass-Abmahn lawyer.
✅ Skill notes "letter follows the typical Google-Fonts-batch template pattern
   per heise.de coverage 2022-2024 (article URL); sender's identity is not
   classified by the toolkit. See drschwenke.de blog for current watchlist."
```

---

## References

See `references/`:
- `known-mass-abmahn-firms.md` — pattern recognition criteria + links to public watchlists. Does NOT name firms.
- `unterlassung-redline-patterns.md` — typical overbroad clauses + narrower alternatives. Compiled from drschwenke.de + IHK guides.
- `response-letter-templates.md` — three reply templates (demand-evidence / narrowed-Unterlassung / rejection). With prominent NOT LEGAL ADVICE notices.

## Data handling

The Abmahnung text contains:
- Your personal data (recipient details, project metadata)
- The sender's data (Anwaltskanzlei details)
- Possibly third-party data (claimed-affected person details)

The skill:
- Processes locally — no cloud calls except the toolkit's normal Claude-Code-API path
- Does NOT commit the letter text to git
- Suggests user redact before pasting
- Output may be saved locally if user chooses; the skill does not auto-save anywhere
- Output should NOT be committed to git (contains personal data)

If the project repo's `.gitignore` does not exclude `defense-output/`, the skill will suggest adding it.
