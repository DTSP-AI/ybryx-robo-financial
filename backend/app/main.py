"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config import settings
from app.database.session import init_db
from app.routers import prequalifications, robots, dealers, chat

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.log_format == "console"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper())
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize database
    await init_db()
    logger.info("database_initialized")

    # TODO: Initialize Mem0 memory manager
    # TODO: Initialize Redis connection pool
    # TODO: Warm up LLM connections

    yield

    # Shutdown
    logger.info("application_shutdown")
    # TODO: Cleanup connections


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ybryx Capital Robotics Financing Platform - Multi-Agent LangGraph Backend",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.ybryxcapital.com", "ybryxcapital.com"],
    )


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "message": "Internal server error",
                "code": "internal_error",
            },
        },
    )


# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "success": True,
        "data": {
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
        "error": None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": settings.app_version,
        },
        "error": None,
    }


# Include routers
app.include_router(prequalifications.router, prefix=settings.api_v1_prefix, tags=["prequalifications"])
app.include_router(robots.router, prefix=settings.api_v1_prefix, tags=["robots"])
app.include_router(dealers.router, prefix=settings.api_v1_prefix, tags=["dealers"])
app.include_router(chat.router, prefix=settings.api_v1_prefix, tags=["chat"])
# TODO: Add industries and agents routers
# app.include_router(industries.router, prefix=settings.api_v1_prefix, tags=["industries"])
# app.include_router(agents.router, prefix=settings.api_v1_prefix, tags=["agents"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
