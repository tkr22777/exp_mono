import base64
import logging
import os

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from sqlalchemy.orm import Session

from src.modules.email_analyzer.analyzer import analyze_email
from src.modules.email_store import repository as repo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCOPES = ["https://mail.google.com/"]

CREDENTIALS_DIR = os.path.join(os.path.dirname(__file__), "..", "credentials")
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.json")


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}\n"
                    "See credentials/README.md for setup instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def extract_body(payload: dict) -> str:
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    return "(no body)"


def fetch_page(service, page_size: int, cursor: str | None) -> tuple[list[dict], str | None]:
    kwargs = {"userId": "me", "maxResults": page_size}
    if cursor:
        kwargs["pageToken"] = cursor

    result = service.users().messages().list(**kwargs).execute()
    messages = result.get("messages", [])
    next_cursor = result.get("nextPageToken")

    emails = []
    for msg in messages:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full",
                 metadataHeaders=["Subject", "From", "Date"])
            .execute()
        )

        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        is_unread = "UNREAD" in detail.get("labelIds", [])

        emails.append({
            "id": detail["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", "(unknown)"),
            "date": headers.get("Date", "(unknown)"),
            "unread": is_unread,
            "body": extract_body(detail["payload"]),
        })

    return emails, next_cursor


def print_email(email: dict, analyze: bool) -> None:
    status = "UNREAD" if email["unread"] else "  READ"
    click.echo(f"[{status}] {email['id']}")
    click.echo(f"  From   : {email['from']}")
    click.echo(f"  Date   : {email['date']}")
    click.echo(f"  Subject: {email['subject']}")

    if analyze:
        verdict = analyze_email(email)
        for line in verdict.strip().splitlines():
            click.echo(f"  {line}")

    click.echo("")


@click.group()
def main() -> None:
    """Gmail CLI — browse and analyse your inbox."""


@main.command()
@click.option("--page-size", default=10, show_default=True, help="Emails per page.")
@click.option("--cursor", default=None, help="Page token from a previous run to continue from.")
@click.option("--analyze", is_flag=True, default=False, help="Analyze each email with Gemini.")
def browse(page_size: int, cursor: str | None, analyze: bool) -> None:
    """Browse a page of emails. Use --cursor to paginate."""
    service = get_gmail_service()
    emails, next_cursor = fetch_page(service, page_size, cursor)

    click.echo(f"Showing {len(emails)} email(s):\n")
    for email in emails:
        print_email(email, analyze)

    if next_cursor:
        click.echo(f"Next cursor: {next_cursor}")
    else:
        click.echo("No more pages.")


@main.command()
@click.option("--db-path", default="data/gmail.db", show_default=True, help="SQLite DB path.")
@click.option("--pages", default=0, show_default=True, help="Number of pages to fetch (0 = all).")
@click.option("--fresh", is_flag=True, default=False, help="Ignore saved cursor and start from the beginning.")
def sync(db_path: str, pages: int, fresh: bool) -> None:
    """Pull inbox emails into SQLite. Skips existing emails. Resumes automatically if interrupted."""
    service = get_gmail_service()
    engine = repo.get_engine(db_path)

    with Session(engine) as session:
        saved_cursor = None if fresh else repo.get_cursor(session)

    if saved_cursor:
        logger.info("Resuming previous sync from saved cursor.")
    else:
        logger.info("Starting fresh sync.")

    logger.info(f"Syncing to {db_path} ...")

    cursor = saved_cursor
    page_count = 0
    total_inserted = 0

    while True:
        emails, next_cursor = fetch_page(service, page_size=50, cursor=cursor)

        with Session(engine) as session:
            inserted = repo.insert_new(session, emails)
            repo.save_cursor(session, next_cursor)
            session.commit()

        page_count += 1
        total_inserted += inserted
        logger.info(f"Page {page_count}: {inserted} new of {len(emails)} fetched (running total: {total_inserted})")

        cursor = next_cursor
        if not cursor or (pages and page_count >= pages):
            break

    with Session(engine) as session:
        db_total = repo.total_count(session)

    logger.info(f"Sync complete. {total_inserted} new email(s) added. Total in DB: {db_total}.")


def fetch_all_ids_from_gmail(service, query: str) -> list[str]:
    """Fetch all message IDs from Gmail matching a search query."""
    ids = []
    cursor = None
    while True:
        kwargs = {"userId": "me", "q": query, "maxResults": 500}
        if cursor:
            kwargs["pageToken"] = cursor
        result = service.users().messages().list(**kwargs).execute()
        ids.extend(m["id"] for m in result.get("messages", []))
        cursor = result.get("nextPageToken")
        if not cursor:
            break
    return ids


@main.command("delete-sender")
@click.argument("pattern")
@click.option("--db-path", default="data/gmail.db", show_default=True, help="SQLite DB path.")
def delete_sender(pattern: str, db_path: str) -> None:
    """Permanently delete all emails from Gmail and DB matching PATTERN (e.g. 'robinhood')."""
    service = get_gmail_service()

    logger.info(f"Searching Gmail for emails from '{pattern}'...")
    ids = fetch_all_ids_from_gmail(service, query=f"from:{pattern}")

    if not ids:
        click.echo(f"No emails found in Gmail matching '{pattern}'.")
        return

    click.echo(f"Found {len(ids)} email(s) in Gmail matching '{pattern}'.")
    click.confirm("Permanently delete from Gmail and local DB?", abort=True)

    deleted = 0
    for email_id in ids:
        service.users().messages().delete(userId="me", id=email_id).execute()
        deleted += 1
        if deleted % 50 == 0:
            logger.info(f"Deleted {deleted}/{len(ids)} from Gmail...")

    engine = repo.get_engine(db_path)
    with Session(engine) as session:
        repo.mark_deleted(session, ids)
        session.commit()

    logger.info(f"Done. {deleted} email(s) permanently deleted from Gmail and marked deleted in DB.")


@main.command()
def count() -> None:
    """Print the total and unread email counts for the inbox."""
    service = get_gmail_service()
    label = service.users().labels().get(userId="me", id="INBOX").execute()

    total = label.get("messagesTotal", 0)
    unread = label.get("messagesUnread", 0)

    click.echo(f"Inbox total : {total}")
    click.echo(f"Unread      : {unread}")
    click.echo(f"Read        : {total - unread}")
