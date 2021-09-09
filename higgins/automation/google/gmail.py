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
        "recipient": to,
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


def get_email(email_id: str, user_id: str = "me") -> Dict:
    client = Gmail()
    message = client._build_message_from_ref(
        user_id="me", message_ref={"id": email_id}
    )
    return convert_message_to_dict(message)


def search_emails(
    query_dicts: List[Dict], limit: int = 100, include_html: bool = False
) -> List[Dict]:
    """Search emails given queries.

    Args:
        query_dicts: List of email query parameters
        limit: Maximum number of emails to return

    Returns:
        List of dictionaries with email body and metadata

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

    print(f"Searching emails with query {query_dicts}")

    for dct in query_dicts:
        dct = format_terms(dct)

    client = Gmail()
    # TODO: Add INBOX labels, Sent, etc
    # Get your available labels
    # User labels: [Label(name='CHAT', id='CHAT'), Label(name='SENT', id='SENT'), Label(name='INBOX', id='INBOX'), Label(name='IMPORTANT', id='IMPORTANT'), Label(name='TRASH', id='TRASH'), Label(name='DRAFT', id='DRAFT'), Label(name='SPAM', id='SPAM'), Label(name='CATEGORY_FORUMS', id='CATEGORY_FORUMS'), Label(name='CATEGORY_UPDATES', id='CATEGORY_UPDATES'), Label(name='CATEGORY_PERSONAL', id='CATEGORY_PERSONAL'), Label(name='CATEGORY_PROMOTIONS', id='CATEGORY_PROMOTIONS'), Label(name='CATEGORY_SOCIAL', id='CATEGORY_SOCIAL'), Label(name='STARRED', id='STARRED'), Label(name='UNREAD', id='UNREAD'), Label(name='[Imap]/Drafts', id='Label_1'), Label(name='Urgent', id='Label_10'), Label(name='[Imap]/Sent', id='Label_2'), Label(name='craigslist', id='Label_2858204817852213362'), Label(name='[Imap]/Trash', id='Label_3'), Label(name='Notes', id='Label_4'), Label(name='Personal', id='Label_5'), Label(name='Receipts', id='Label_6'), Label(name='Work', id='Label_8'), Label(name='TODO', id='Label_8430892267769255145'), Label(name='Sent Messages', id='Label_9')]
    # labels = client.list_labels()
    # print(f"User labels: {labels}")
    messages = client.get_messages(
        query=construct_query(*query_dicts)
    )
    print(f"Query returned {len(messages)} messages")
    emails = []
    for message in messages[:limit]:
        print(message)
        email = convert_message_to_dict(message, include_html)
        emails.append(email)
    return emails


def convert_message_to_dict(
    message: Message, include_html: bool = False
) -> Dict:
    email = {
        "recipient": message.recipient,
        "sender": message.sender,
        "subject": message.subject,
        "date": message.date,
        "preview": message.snippet,
        "plain": email_utils.clean_email_body(message.plain or ""),
        "google_id": message.id,
        "label_ids": [label.name for label in message.label_ids],
        "html": None,
    }
    if include_html:
        email["html"] = message.html or ""
    return email


def format_terms(terms: Dict) -> Dict:
    # Bug in library. If unread=False, it behaves as unread=True
    if "unread" in terms and not terms["unread"]:
        del terms["unread"]
    if "read" in terms and not terms["read"]:
        del terms["read"]
    return terms


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
