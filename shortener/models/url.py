from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from ..models import Base

class ShortUrl(Base):  # type: ignore[misc,valid-type]
    __tablename__ = 'short_urls'

    id = Column(Integer, primary_key=True)
    url_key = Column(String, unique=True, nullable=False)
    target = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
