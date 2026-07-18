# Data Legend — Facility Trust Desk

Hack Nation 6th Global AI Hackathon MVP skeleton.

Facility Trust Desk helps public-health planners evaluate whether a healthcare
facility's claimed capabilities, such as ICU, NICU, or Emergency, are supported
by available evidence.

This MVP verifies frontend-to-backend API wiring with a layered structure and
mock data. It intentionally does not include real data loading, Databricks
access, cleaning logic, scoring algorithms, database persistence, auth, or LLM
logic.

## Current structure

```text
backend/
  main.py                 FastAPI app entrypoint
  routes/                 API route declarations
  controllers/            Request orchestration layer
  services/               Mock business/data access layer
  schemas/                Pydantic request/response shapes
  data/                   Replaceable mock data

frontend/
  index.html              Dashboard list page
  detail.html             Facility detail page
  css/styles.css          Shared styling
  js/services/            API client functions
  js/components/          Reusable render helpers
  js/pages/               Page-level behavior
```

## Run the backend

```bash
cd healthcare-facility-trust
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

## Run the frontend

In a second terminal:

```bash
cd healthcare-facility-trust/frontend
python -m http.server 5173
```

Open http://localhost:5173.

The dashboard shows filters, summary metrics, and all mock hospitals. Click
`Open Detail` on a facility card to inspect the mock trust score, score reasons,
data quality flags, and capability checklist.
