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
app.py                   Databricks/FastAPI single app entrypoint
app.yaml                 Databricks Apps startup command

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

## Local run

```bash
cd healthcare-facility-trust
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

Test:

```text
http://localhost:8000/api/health
http://localhost:8000/api/filters
http://localhost:8000/api/facilities/search?capability=ICU&limit=20
```

The root `app.py` reuses `backend.main:app`, serves all `/api` routes, serves
`frontend/index.html` at `GET /`, and mounts static frontend assets for the
HTML/CSS/JS paths used by the vanilla frontend.

For older split local development, the frontend can still call
`http://localhost:8000` when opened from a separate localhost port. The
Databricks deployment path uses same-origin API requests.

## Databricks Apps deployment

This app is designed for Databricks Apps on Free Edition. The hackathon
submission requires a live Databricks App, so root-level `app.py` and
`app.yaml` are the deployment entrypoints.

Deployment steps:

1. Push this repository to GitHub.
2. Open Databricks Free Edition.
3. Go to Databricks Apps.
4. Create a custom app.
5. Connect the Git repository and target branch.
6. Confirm `app.yaml` is at the app project root.
7. Deploy.
8. Open the Databricks App URL and test the dashboard.

`app.yaml` runs:

```yaml
command:
  - uvicorn
  - app:app
  - --host
  - 0.0.0.0
  - --port
  - $DATABRICKS_APP_PORT
```

`DATABRICKS_APP_PORT` is provided by the Databricks Apps runtime. Do not
hardcode port `8000` in deployment config.

## Environment variables

Mapbox support uses one environment variable:

```text
MAPBOX_TOKEN=Mapbox pk token for frontend map rendering and optional backend geocoding
```

Do not commit the real token. Configure it locally in `.env` or
`frontend/config.local.js`, or configure it as a Databricks App secret resource.

For Databricks Apps, add one Secret resource:

```text
Secret scope: facility-trust-desk
Secret key: MAPBOX_TOKEN
Resource key: mapbox_token
Permission: Can read
```

`app.yaml` injects it with:

```yaml
env:
  - name: MAPBOX_TOKEN
    valueFrom: mapbox_token
  - name: DATABRICKS_AI_ENDPOINT
    valueFrom: ai_model
```

The public config endpoint `GET /api/config` returns:

```json
{
  "mapboxToken": ""
}
```

If `MAPBOX_TOKEN` is missing, the app still starts. The Evidence Review map
shows a clean unavailable state instead of crashing.

Optional placeholders are documented in `.env.example`.

## Databricks AI Evidence Summary

The Evidence Review panel includes a manual `Generate AI Summary` button. It
does not run automatically for every facility or every search result.

The backend route is:

```text
POST /api/facilities/{facility_id}/ai-summary
```

The route uses the Databricks SDK and reads the serving endpoint from:

```text
DATABRICKS_AI_ENDPOINT
```

For the Databricks App, configure the serving endpoint resource:

```text
Serving endpoint: databricks-gpt-5-6-luna
Permission: Can query
Resource key: ai_model
```

If `DATABRICKS_AI_ENDPOINT` is missing or the endpoint call fails, the dashboard
shows a clean unavailable message and the rest of the app continues to work.

## Troubleshooting

- If the frontend loads but API calls fail, check that requests use same-origin
  `/api/...` paths in deployed mode.
- If CSS or JS files are missing, confirm `/frontend` is mounted by `app.py`.
- If the Databricks App fails to start, check `app.yaml`, `requirements.txt`,
  and the `uvicorn app:app` command.
- If Mapbox is blank, check `MAPBOX_TOKEN` and that the map container has
  visible height.
- If backend geocoding fails, check `MAPBOX_TOKEN`.
- If AI summary is unavailable in Databricks, check the `ai_model` app resource
  and `DATABRICKS_AI_ENDPOINT`.
- If review persistence fails, confirm the runtime can create the local
  `.runtime/` directory.
