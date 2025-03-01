from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .url import ShortUrl  # noqa: E402

__all__ = ["Base", "ShortUrl"]
