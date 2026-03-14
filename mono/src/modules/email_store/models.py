from sqlalchemy import Boolean, Column, Text
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
