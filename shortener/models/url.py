from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from . import Base

class ShortURL(Base):
    __tablename__ = 'short_urls'
    
    id = Column(Integer, primary_key=True)
    original_url = Column(String(2048), nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)