from __future__ import annotations

import logging
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.app.config import Settings, get_settings
from api.app.dependencies import get_rag_service, get_retrieval_service, get_store_manager
from api.app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    RetrievalResult,
    SearchRequest,
    SearchResponse,
    Source,
)
from api.app.rag import RagService
from api.app.retrieval import RetrievalService, ScoredDocument

logger = logging.getLogger("vidzy_rag")


def _safe_metadata(item: ScoredDocument, public: bool) -> dict:
    metadata = item.document.metadata
    allowed = {
        "scope",
        "category",
        "document_type",
        "status",
        "tags",
        "question_id",
        "fact_id",
        "canonical_question",
        "source_fact_ids",
        "heading",
    }
    if not public:
        allowed |= {"source_document", "source_id", "registered_scope", "chunk_index"}
    return {key: value for key, value in metadata.items() if key in allowed}


def _source(item: ScoredDocument, public: bool) -> Source:
    metadata = item.document.metadata
    identifier = metadata.get("question_id") or metadata.get("fact_id") or metadata.get("source_id") or "knowledge"
    if public:
        label = metadata.get("canonical_question") or metadata.get("source_label") or "Vidzy product knowledge"
    else:
        label = metadata.get("source_document") or metadata.get("source_label") or "Internal knowledge"
    return Source(
        id=str(identifier),
        label=str(label),
        category=metadata.get("category"),
        document_type=str(metadata.get("document_type", "knowledge")),
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", docs_url="/api/docs" if settings.app_env != "production" else None)
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Internal-API-Key"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"location": error["loc"], "message": error["msg"], "type": error["type"]} for error in exc.errors()]
        return JSONResponse(status_code=422, content=jsonable_encoder({"error": "invalid_request", "details": details}))

    @app.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled request error: %s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"error": "internal_error", "message": "The request could not be completed."})

    @app.get("/api/health", response_model=HealthResponse)
    def health(manager=Depends(get_store_manager)) -> HealthResponse:
        counts = {scope: manager.count(scope) for scope in ("public", "internal")}
        ready = counts["public"] > 0
        return HealthResponse(
            status="ok" if ready else "degraded",
            response_mode=settings.rag_response_mode,
            vector_store_ready=ready,
            collections=counts,
        )

    @app.post("/api/search", response_model=SearchResponse)
    def search(
        payload: SearchRequest,
        x_internal_api_key: str | None = Header(default=None),
        retrieval: RetrievalService = Depends(get_retrieval_service),
    ) -> SearchResponse:
        if len(payload.query) > settings.max_question_length:
            raise HTTPException(status_code=422, detail="Query is too long")
        is_private = payload.scope in {"internal", "combined"}
        if is_private and (
            not settings.internal_api_key
            or not x_internal_api_key
            or not secrets.compare_digest(x_internal_api_key, settings.internal_api_key)
        ):
            raise HTTPException(status_code=403, detail="Internal search is unavailable or unauthorized")
        scopes = ["public", "internal"] if payload.scope == "combined" else [payload.scope]
        results = retrieval.retrieve_scopes(payload.query, scopes=scopes, limit=payload.limit)
        public = payload.scope == "public"
        return SearchResponse(
            query=payload.query,
            scope=payload.scope,
            results=[
                RetrievalResult(
                    content=item.document.page_content,
                    score=round(item.score, 4),
                    metadata=_safe_metadata(item, public),
                    citation=_source(item, public),
                )
                for item in results
            ],
        )

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(payload: ChatRequest, rag: RagService = Depends(get_rag_service)) -> ChatResponse:
        if len(payload.message) > settings.max_question_length:
            raise HTTPException(status_code=422, detail="Message is too long")
        return rag.answer(payload.message)

    static_dir = Path(settings.static_dir)
    if static_dir.is_dir():
        assets_dir = static_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str) -> FileResponse:
            requested = static_dir / full_path
            if full_path and requested.is_file() and static_dir in requested.resolve().parents:
                return FileResponse(requested)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
