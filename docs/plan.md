# Notice Decoder: implementation plan

## Goal

Help a Japanese or English reader understand routine notices in plain English while keeping the original document as the authority. The app must show uncertainty, evidence, and appropriate redirects for high-risk documents. See [product boundaries](product-boundaries.md).

## Architecture decisions

- **Frontend:** React + Vite.
- **Backend:** FastAPI and Python. LangGraph will orchestrate the analysis pipeline.
- **OCR:** local RapidOCR with Japanese recognition for the prototype; keep an OCR interface so quality can be compared with other providers.
- **Decisions:** Jev behind a `DecisionEngine` interface. Run it in shadow mode against labeled notices before it controls routing.
- **Explanation and extraction:** Claude, with exact source quotes for fields. The OCR engine supplies image coordinates for highlights.
- **Database:** one PostgreSQL database with pgvector for app records, guide passages, embeddings, and LangGraph checkpoints. Photos are stored as files, with paths in PostgreSQL.
- **Deployment:** run locally first. A future Cloudflare setup can host the web app, FastAPI in a Container, and photos in R2; PostgreSQL would need a separate host.

## Ordered milestones

| # | Milestone | Done when |
|---|---|---|
| 1 | Local app setup | React and FastAPI start locally. |
| 2 | Smallest complete flow | A photo upload produces a preliminary three-card result beside the original. |
| 3 | OCR and evidence | OCR lines have coordinates and confidence; extracted details link to a highlighted source line. |
| 4 | LangGraph pipeline | Image check, OCR, risk route, extraction, validation, and response are explicit nodes. High-risk and unreadable paths are tested. |
| 5 | Field validation | Dates, amounts, and phone numbers are checked against OCR quotes; Japanese era dates are parsed in code and shown in both formats. |
| 6 | Curated-guide RAG | A small reviewed guide corpus is indexed in PostgreSQL; explanations cite retrieved sources and distinguish them from notice facts. |
| 7 | Jev comparison | Jev answers bounded risk, action, and urgency questions; disagreements and uncertainty are measured against labeled examples before routing changes. |
| 8 | Confirmed saving and history RAG | The user confirms before saving. Past notices can be searched without mixing their content into the curated guide corpus. |
| 9 | Accuracy evaluation | A consented set of 50–100 notices covers vertical text, handwriting, blur, stamps, money, and high-risk cases; measure field accuracy and missed redirects. |
| 10 | Accounts, calendar, reminders, deployment | Add these after the core reading flow meets evaluation targets. |

Milestones 1–3 are implemented as a prototype. The result is currently rule-based, and nothing is persisted. The next work is milestone 4.

## Definition of a reliable result

- Every displayed extracted field has a quote present in OCR output and a location on the original image, or is marked for manual verification.
- Low-confidence or conflicting reads say **unsure** rather than presenting a clean answer.
- Legal, immigration, medical, and threatening notices do not receive action advice.
- Money and date-critical notices prompt verification against the original.
- RAG citations identify the guide source; retrieved content cannot override the notice.
- No save or reminder occurs without explicit confirmation.
