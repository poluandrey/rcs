from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    db_session = scoped_session(sessionmaker(bind=engine, autoflush=False,))
    query = db_session.query_property()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    last_update = Column(DateTime(timezone=True), server_onupdate=func.now())
