from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.modules.email_store.models import Base, Email


def get_engine(db_path: str):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def save(session: Session, email: dict) -> None:
    session.merge(Email(
        id=email["id"],
        subject=email["subject"],
        sender=email["from"],
        date=email["date"],
        unread=email["unread"],
        body=email["body"],
    ))


def total_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Email))
