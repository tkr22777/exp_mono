import base64
import os

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from scripts.email_analyzer import analyze_email

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

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
    """Extract plain text body from a Gmail message payload."""
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    return "(no body)"


def fetch_page(service, page_size: int, cursor: str | None) -> tuple[list[dict], str | None]:
    """Fetch one page of emails. Returns (emails, next_cursor)."""
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


@click.command()
@click.option("--page-size", default=10, show_default=True, help="Emails per page.")
@click.option("--cursor", default=None, help="Page token from a previous run to continue from.")
@click.option("--analyze", is_flag=True, default=False, help="Analyze each email with Gemini.")
def main(page_size: int, cursor: str | None, analyze: bool) -> None:
    """Crawl Gmail and print one page of email metadata.

    Pass --cursor <token> to fetch the next page. Use --analyze to get
    a Gemini verdict (IMPORTANT / NEUTRAL / SPAM) for each email.
    """
    service = get_gmail_service()
    emails, next_cursor = fetch_page(service, page_size, cursor)

    click.echo(f"Showing {len(emails)} email(s):\n")
    for email in emails:
        print_email(email, analyze)

    if next_cursor:
        click.echo(f"Next cursor: {next_cursor}")
    else:
        click.echo("No more pages.")
