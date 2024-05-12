from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """
    Generator function that yields a new SQLAlchemy SessionLocal instance.

    This function is a dependency for FastAPI routes. It creates a new SQLAlchemy session, yields it for use in the route, and ensures the session is closed after the route has finished processing.

    Yields:
        Session: SQLAlchemy session.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/items/")
        >>> async def read_items(db: Session = Depends(get_db)):
        >>>     items = db.query(Item).all()
        >>>     return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
