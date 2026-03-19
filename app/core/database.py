"""Database initialization helpers."""

from collections.abc import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app import models  # noqa: F401


engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session dependency."""
    with SessionLocal() as session:
        yield session


def init_db() -> None:
    """Initialize database metadata.

    Notes:
        This is placeholder initialization for the bootstrap phase.
        Alembic migrations will become the source of truth in Phase 1.
    """
    SQLModel.metadata.create_all(engine)
