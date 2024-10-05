from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Cache(Base):
    __tablename__ = "cache"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    type = Column(String)
    value = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Cache {self.key}>"
