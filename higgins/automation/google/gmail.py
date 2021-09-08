"""Query, Search, Parse Emails from Gmail.

TODO: Paginate over large requests. Right now it will timeout trying to download 1000s of emails.

Setup instructions here: https://github.com/jeremyephron/simplegmail

1. Create/reuse a google cloud project
2. Enable the Gmail API https://developers.google.com/workspace/guides/create-project?authuser=1#enable-api
3. Enable OAuth sign-in
4. Create credentials and download the client_secret.json file into repo root

https://developers.google.com/gmail/api/quickstart/python
"""

from typing import Dict, List

from simplegmail import Gmail
from simplegmail.message import Message
from simplegmail.query import construct_query

from higgins.automation.email import email_utils


def send_email(
    to: str,
    sender: str,
    subject: str,
    body_html: str = None,
    body_plain: str = None,
    cc: List[str] = None,
    bcc: List[str] = None,
    attachments: List[str] = None,
) -> Dict:
    assert body_html is not None or body_plain is not None
    client = Gmail()

    params = {
        "to": to,
        "sender": sender,
        "cc": cc,
        "bcc": bcc,
        "subject": subject,
        "msg_html": body_html,  # "<h1>Woah, my first email!</h1><br />This is an HTML email.",
        "msg_plain": body_plain,
        "attachments": attachments,  # ["path/to/something/cool.pdf", "path/to/image.jpg", "path/to/script.py"],
        "signature": True  # use my account signature
    }
    message = client.send_message(**params)  # equivalent to send_message(to="you@youremail.com", sender=...)
    return message


def get_emails():
    client = Gmail()

    # Unread messages in your inbox
    messages = client.get_unread_inbox()
    print(f"You have {len(messages)} unread messages.")

    # Starred messages
    # messages = client.get_starred_messages()

    # ...and many more easy to use functions can be found in gmail.py!

    # Print them out!
    for message in messages[:2]:
        print("To: " + message.recipient)
        print("From: " + message.sender)
        print("Subject: " + message.subject)
        print("Date: " + message.date)
        print("Preview: " + message.snippet)
        print("Message Body: " + message.plain)  # or message.html


def search_emails(query_dicts: List[Dict]) -> List[Message]:
    """Search emails given queries.

    Example: Return messages that are either:
    - newer than 2 days old, unread, labeled "Finance" or both "Homework" and "CS"
    OR
    - newer than 1 month old, unread, labeled "Top Secret", but not starred.

    query_dicts = [
        {
            "newer_than": (2, "day"),
            "unread": True,
            "labels":[["Finance"], ["Homework", "CS"]]
        },
        {
            "newer_than": (1, "month"),
            "unread": True,
            "labels": ["Top Secret"],
            "exclude_starred": True
        }
    ]
    """
    client = Gmail()
    # Get your available labels
    # labels = client.list_labels()
    messages = client.get_messages(
        query=construct_query(*query_dicts)
    )
    # print(f"Query returned {len(messages)} messages")
    emails = []
    for message in messages:
        emails.append({
            "to": message.recipient,
            "from": message.sender,
            "subject": message.subject,
            "date": message.date,
            "preview": message.snippet,
            "body": email_utils.clean_email_body(message.plain or ""),
            "id": message.id,
        })
    return emails


if __name__ == "__main__":
    # msg = send_email(
    #     to="bfortuner@gmail.com",
    #     sender="bfortuner@gmail.com",
    #     subject="Hello Brendan",
    #     body_plain="This is an email body"
    # )
    # print(msg)

    # get_emails()

    messages = search_emails([
        dict(
            sender="bfortuner@gmail.com",
            recipient="cfortuner@gmail.com",
            newer_than=(7, "day"),
            # unread=None,
            # labels=None,
            # exact_phrase=None,
            # subject=None,
        )
    ])
    print(len(messages))
    print(messages[0])
