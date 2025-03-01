from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..models import Base

class ShortUrl(Base):
    __tablename__ = 'short_urls'
    
    id = Column(Integer, primary_key=True)
    url_key = Column(String, nullable=False, unique=True)
    target = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
