"""
FastAPI application entrypoint.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.api import conversations, search

app = FastAPI(title="ChatArchive API")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)
app.include_router(search.router)

# Error Handlers 

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Bad/malformed request body → 400 instead of FastAPI's default 422."""
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    """Catches anything unexpected → clean 500 JSON instead of a raw crash trace."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ChatArchive API"}