# Data Legend - Facility Trust Desk

Hack Nation 6th Global AI Hackathon project.

Facility Trust Desk helps public-health planners evaluate whether a healthcare
facility's claimed capabilities, such as ICU, NICU, Emergency, or Maternity, are
supported by available evidence.

The current MVP includes a demo facility dataset, evidence-backed trust scoring,
ranked facility search, citation-style evidence snippets, missing-context
warnings, and saved planner review notes.

## Current structure

```text
backend/
  main.py                 FastAPI app entrypoint
  routes/                 API route declarations
  controllers/            Request orchestration layer
  services/               Evidence scoring and review persistence
  schemas/                Pydantic request/response shapes

frontend/
  index.html              Facility Trust Desk dashboard
  css/styles.css          Shared styling
  js/services/            API client functions
  js/components/          Reusable render helpers
  js/pages/               Page-level behavior

sample_data/
  demo_facilities.json    Demo records for local scoring and app development
  clean_facilities.csv    Optional clean CSV loaded before demo data when present
```

## Load clean data

Place the clean CSV at:

```text
sample_data/clean_facilities.csv
```

When this file exists, the backend loads it instead of `demo_facilities.json`.
The CSV can use the schema field names directly, including `name`,
`address_city`, `address_stateOrRegion`, `description`, `capability`,
`procedure`, `equipment`, `specialties`, `numberDoctors`, `capacity`,
`yearEstablished`, `officialWebsite`, and `websites`.

Common aliases such as `facilityId`, `facilityName`, `city`, `state`, `pin`,
`capabilities`, and `procedures` are also normalized automatically.

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
