# Data Legend — Facility Trust Desk

Hack Nation 6th Global AI Hackathon MVP skeleton.

Facility Trust Desk helps public-health planners evaluate whether a healthcare
facility's claimed capabilities, such as ICU, NICU, or Emergency, are supported
by available evidence.

This first MVP only verifies frontend-to-backend API wiring. It intentionally
does not include real data loading, Databricks access, cleaning logic, scoring
logic, database models, service layers, auth, or LLM logic.

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

Open http://localhost:5173 and use the API Smoke Test buttons.
