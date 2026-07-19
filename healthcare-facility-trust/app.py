from __future__ import annotations

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from backend.main import app as backend_app


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"
CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"
PUBLIC_DIR = FRONTEND_DIR / "public"
LOCAL_FRONTEND_CONFIG = FRONTEND_DIR / "config.local.js"

app = backend_app

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend",
)

app.mount("/css", StaticFiles(directory=str(CSS_DIR)), name="css")
app.mount("/js", StaticFiles(directory=str(JS_DIR)), name="js")
app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/index.html")
def read_index_html() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/config.local.js")
def read_local_frontend_config():
    if LOCAL_FRONTEND_CONFIG.exists():
        return FileResponse(LOCAL_FRONTEND_CONFIG, media_type="application/javascript")
    return Response("", media_type="application/javascript")


@app.get("/api/config")
def read_public_config() -> dict[str, str]:
    return {
        "mapboxToken": os.getenv("MAPBOX_TOKEN", ""),
    }


@app.get("/{full_path:path}")
def frontend_fallback(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    return FileResponse(INDEX_FILE)
