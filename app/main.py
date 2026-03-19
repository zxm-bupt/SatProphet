"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.ingester.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
	"""Manage scheduler lifecycle."""
	if settings.enable_scheduler:
		start_scheduler()
	try:
		yield
	finally:
		if settings.enable_scheduler:
			stop_scheduler()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
	CORSMiddleware,
	allow_origins=[item.strip() for item in settings.cors_origins.split(",") if item.strip()],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
