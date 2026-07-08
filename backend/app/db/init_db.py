"""
Creates all tables. Fine for SQLite + a resume project; for production-grade
schema evolution, swap this for Alembic migrations.
"""
import logging

from app.db.session import engine
from app.models.db_models import Base

logger = logging.getLogger(__name__)


def init_db() -> None:
    logger.info("Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready.")
