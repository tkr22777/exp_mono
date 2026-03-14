from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.orm import Session

from src.modules.email_store.models import Base, Email, SyncState

SYNC_STATE_ID = "default"

# List of migrations to apply in order. Each is a raw SQL ALTER statement
# that is safe to skip if the column already exists.
_MIGRATIONS = [
    "ALTER TABLE emails ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT 0",
]


def get_engine(db_path: str):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    _run_migrations(engine)
    return engine


def _run_migrations(engine) -> None:
    existing_columns = {col["name"] for col in inspect(engine).get_columns("emails")}
    with engine.connect() as conn:
        for statement in _MIGRATIONS:
            # Derive column name from the ALTER statement to check if it exists
            col_name = statement.split("ADD COLUMN")[1].strip().split()[0]
            if col_name not in existing_columns:
                conn.execute(text(statement))
                conn.commit()


def insert_new(session: Session, emails: list[dict]) -> int:
    """Insert only emails whose IDs are not already in the DB. Returns count inserted."""
    ids = [e["id"] for e in emails]
    existing_ids = set(
        session.scalars(select(Email.id).where(Email.id.in_(ids)))
    )
    new_emails = [e for e in emails if e["id"] not in existing_ids]
    session.add_all([
        Email(
            id=e["id"],
            subject=e["subject"],
            sender=e["from"],
            date=e["date"],
            unread=e["unread"],
            body=e["body"],
        )
        for e in new_emails
    ])
    return len(new_emails)


def get_cursor(session: Session) -> str | None:
    state = session.get(SyncState, SYNC_STATE_ID)
    return state.cursor if state else None


def save_cursor(session: Session, cursor: str | None) -> None:
    session.merge(SyncState(id=SYNC_STATE_ID, cursor=cursor))


def get_ids_by_sender(session: Session, pattern: str) -> list[str]:
    return list(session.scalars(
        select(Email.id).where(Email.sender.ilike(f"%{pattern}%"))
    ))


def mark_deleted(session: Session, ids: list[str]) -> None:
    session.query(Email).where(Email.id.in_(ids)).update(
        {Email.deleted: True}, synchronize_session=False
    )


def total_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Email))
