from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

if TYPE_CHECKING:
    from . import Base  # noqa: F401
from ..models import Base

class ShortUrl(Base):
    __tablename__ = 'short_urls'

    id = Column(Integer, primary_key=True)
    url_key = Column(String, unique=True, nullable=False)
    target = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
