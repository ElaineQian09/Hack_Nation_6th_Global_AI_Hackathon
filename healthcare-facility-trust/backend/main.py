from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import data_quality_routes
from backend.routes import facility_routes
from backend.routes import filter_routes
from backend.routes import health_routes
from backend.routes import map_routes
from backend.routes import review_routes
from backend.routes import summary_routes


def create_app() -> FastAPI:
    api = FastAPI(title="Data Legend - Facility Trust Desk API")

    api.add_middleware(
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

    api.include_router(health_routes.router)
    api.include_router(filter_routes.router)
    api.include_router(summary_routes.router)
    api.include_router(facility_routes.router)
    api.include_router(map_routes.router)
    api.include_router(data_quality_routes.router)
    api.include_router(review_routes.router)

    return api


app = create_app()
"""ASGI app entrypoint for uvicorn."""
