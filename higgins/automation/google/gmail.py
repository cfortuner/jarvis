"""Query, Search, Parse Emails from Gmail.

Setup instructions here: https://github.com/jeremyephron/simplegmail

1. Create/reuse a google cloud project
2. Enable the Gmail API https://developers.google.com/workspace/guides/create-project?authuser=1#enable-api
3. Enable OAuth sign-in
4. Create credentials and download the client_secret.json file into repo root

https://developers.google.com/gmail/api/quickstart/python
"""

from typing import Dict, List

from simplegmail import Gmail


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


def search_emails():
    """Search emails given query"""
    raise NotImplementedError



if __name__ == "__main__":
    msg = send_email(
        to="bfortuner@gmail.com",
        sender="bfortuner@gmail.com",
        subject="Hello Brendan",
        body_plain="This is an email body"
    )
    print(msg)
    
    # get_emails()
