from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel


app = FastAPI(title="Data Legend — Facility Trust Desk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    facilityId: str
    capability: str
    decision: str
    note: str


@app.get("/api/health", response_class=PlainTextResponse)
def health() -> str:
    # TODO: Replace with real API health checks later.
    return "Data Legend API is running"


@app.get("/api/filters", response_class=PlainTextResponse)
def filters() -> str:
    # TODO: Return real capability, state, city, and trust level filter options later.
    return "Filters endpoint: will return capability, state, city, and trust level options"


@app.get("/api/summary", response_class=PlainTextResponse)
def summary() -> str:
    # TODO: Calculate real candidate counts, trust buckets, and data quality flag counts later.
    return "Summary endpoint: will return candidate count, high/medium/low trust counts, and data quality flag counts"


@app.get("/api/facilities/search", response_class=PlainTextResponse)
def facility_search() -> str:
    # TODO: Search and rank real facilities by capability, location, and trust score later.
    return "Facility search endpoint: will return ranked facilities by capability, location, and trust score"


@app.get("/api/facilities/{facilityId}", response_class=PlainTextResponse)
def facility_detail(facilityId: str) -> str:
    # TODO: Return real facility profile, evidence, gaps, contradictions, and quality flags later.
    return "Facility detail endpoint: will return facility profile, evidence breakdown, missing evidence, contradictions, and data quality flags"


@app.get("/api/data-quality", response_class=PlainTextResponse)
def data_quality() -> str:
    # TODO: Return real data quality findings for suspicious coordinates, capacity gaps, weak claims, and conflicts later.
    return "Data quality endpoint: will return suspicious coordinates, missing capacity, weak claims, and conflicting records"


@app.post("/api/reviews", response_class=PlainTextResponse)
def save_review(review: ReviewRequest) -> str:
    # TODO: Persist reviewer decisions, overrides, and notes later.
    return "Review endpoint: will save reviewer decision, override, and note later"
