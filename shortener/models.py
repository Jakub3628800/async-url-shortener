from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ShortUrl(Base):  # type: ignore
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True)
    url_key = Column(String, unique=True, nullable=False)
    target = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


__all__ = ["Base", "ShortUrl"]
