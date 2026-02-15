from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency pro získání DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# U PostgreSQL vynutíme klientské kódování UTF8 (řeší UnicodeEncodeError pro diakritiku)
if settings.DATABASE_URL.startswith("postgresql+psycopg") or settings.DATABASE_URL.startswith("postgresql"):
    logger = logging.getLogger(__name__)

    @event.listens_for(engine, "connect")
    def set_client_encoding(dbapi_connection, connection_record):
        try:
            # psycopg3 API - use cursor to execute SQL
            cursor = dbapi_connection.cursor()
            cursor.execute("SET client_encoding TO 'UTF8'")
            cursor.close()
        except Exception as e:
            logger.warning("Nepodařilo se nastavit client_encoding UTF8: %s", e)