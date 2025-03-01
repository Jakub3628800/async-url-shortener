from sqlalchemy.ext.declarative import declarative_base
from .url import ShortUrl

Base = declarative_base()

__all__ = ["Base", "ShortUrl"]
