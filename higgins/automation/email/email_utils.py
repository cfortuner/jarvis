import sys
from typing import Dict, List


def get_email_list_preview(emails: List[Dict], limit: int = 50) -> str:
    display = []
    for idx, email in enumerate(emails):
        display.append(f"[{idx}] {email['from']} subject: {email['subject']}")
    text = f"Found {len(emails)} emails.\n"
    if len(emails) > limit:
        text += f"Displaying {limit} out of {len(emails)} emails:\n"
    text += "\n".join(display[:limit])
    return text


def get_email_preview(email: Dict, max_lines=sys.maxsize) -> str:
    body_lines = email["body"].split("\n")[:max_lines]
    lines = [
        f"\nFrom: {email['from']}",
        f"\nDate: {email['date']}",
        f"\nSubject: {email['subject']}\n",
    ]
    lines += [f"\n{line}" for line in body_lines]
    preview = "".join(lines)
    return preview


def clean_email_body(body: str):
    body = body.replace("\r", "")
    return body


def get_body_stats(body):
    lines = body.split("\n")
    words = body.replace("\n", " ").split()
    return {
        "lines": len(lines),
        "words": len(words),
        "chars": len(body),
    }
