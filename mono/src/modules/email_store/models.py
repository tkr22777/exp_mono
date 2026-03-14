from sqlalchemy import Boolean, Column, DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Email(Base):
    __tablename__ = "emails"

    id = Column(Text, primary_key=True)
    subject = Column(Text)
    sender = Column(Text)
    date = Column(Text)
    unread = Column(Boolean)
    body = Column(Text)
    deleted = Column(Boolean, default=False, nullable=False, server_default="0")


class SyncState(Base):
    __tablename__ = "sync_state"

    id = Column(Text, primary_key=True, default="default")
    cursor = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
