# Product boundaries

Adapted from the user-provided **“Notice Decoder for Japan: Product Boundaries”** (November 14, 2026). This file is the working product rule set for implementation; it is not a legal review.

## Guiding principle

The product explains and organizes notices. It is never the authority. Where a mistake is costly or irreversible, show the original and direct the user to a human or official source.

## Supported routine notices

Landlord, ward or city office, delivery, utility, and school notices can receive a plain-English explanation, action triage, extracted details, and evidence highlights. Typical examples include redelivery slips, garbage rule changes, maintenance notices, payment slips, and ward events.

## Response routes

| Route | Behavior |
|---|---|
| Routine | Explain the notice, possible action, and key details with source highlights. |
| Money | Extract facts and prompt verification of amounts and deadlines against the original. Do not recommend whether to pay, dispute, or contest. |
| Legal, immigration, medical, threatening | Identify the document type briefly and direct the user to the issuing office or an appropriate professional. Do not interpret or advise. |
| Scam-suspect | Flag unusual signals and advise verification through an official source. Never certify a notice as legitimate. |
| Unsupported or unreadable | Say that the input cannot be read or does not appear to be a supported notice; request a clearer photo or manual check. |

The early risk route must be conservative. A low-confidence decision should say **unsure** and put the original contact details first.

## Evidence and uncertainty

- Keep the original photo one tap away.
- Each extracted field needs an exact quote found in OCR text. Highlights come from OCR coordinates, not LLM-generated boxes.
- Show confidence and change wording when it is low. Flag disagreement between OCR and vision or language-model readings.
- Parse dates deterministically, including Japanese era dates. Show the original date and converted date together.
- Ask for verification when a notice concerns money or a critical deadline.

## Consent and data

- Do not save a notice or create a calendar event until the user confirms.
- Keep notice-history retrieval separate from curated public guidance.
- Record high-risk redirect rates for later evaluation without treating model outputs as ground truth.

## Future evaluation

Collect 50–100 consented, labeled examples across difficult layouts and high-risk categories. Measure field-level extraction accuracy, evidence matching, uncertainty behavior, and missed high-risk routes. Review disclaimers, referral details, and the out-of-scope list with a qualified professional before launch.
