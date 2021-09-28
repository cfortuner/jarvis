import mistletoe

from pathlib import Path
import pandas as pd
import pypandoc
import json
import sys
import re
from html2text import HTML2Text
from bs4 import BeautifulSoup


def html2md(html):
    parser = HTML2Text()
    parser.ignore_images = True
    parser.ignore_anchors = True
    parser.body_width = 0
    md = parser.handle(html)
    return md


def html2plain(html):
    # HTML to Markdown
    md = html2md(html)
    # Normalise custom lists
    md = re.sub(r"(^|\n) ? ? ?\\?[•·–-—-*]( \w)", r"\1  *\2", md)
    # Convert back into HTML
    html_simple = mistletoe.markdown(md)
    # Convert to plain text
    soup = BeautifulSoup(html_simple)
    text = soup.getText()
    # Strip off table formatting
    text = re.sub(r"(^|\n)\|\s*", r"\1", text)
    # Strip off extra emphasis
    text = re.sub(r"\*\*", "", text)
    # Remove trailing whitespace and leading newlines
    text = re.sub(r" *$", "", text)
    text = re.sub(r"\n\n+", r"\n\n", text)
    text = re.sub(r"^\n+", "", text)
    return text


def html2plain_pandoc(html):
    # ...but you can overwrite the format via the `format` argument:
    # output = pypandoc.convert_file('somefile.txt', 'rst', format='md')
    # alternatively you could just pass some string. In this case you need to
    # define the input format:
    output = pypandoc.convert_text(html, to="md", format="html")
    # output == 'some title\r\n==========\r\n\r\n'
    return output


if __name__ == "__main__":
    from higgins.automation.email import email_utils

    email_id = "0f84cbaf27e24d6d3eb96b734e8f8c776a8fc7250ed479ba252d47a9fc56fcc2"
    # email_id = "e9e027410ae591c3ea94c3d2c67fe7ac05025dd92579e224b1e9abe8dd6ff72d"
    email_id = "365b47046e7027df274d0a26de33461f99c4cb054e47a6aaa4a6bc791e263585"
    email = email_utils.load_email(email_id)
    html = email["html"]
    md = html2md(html)
    print(md)
    with open("email.md", "w") as f:
        f.write(md)

    html_simple = mistletoe.markdown(md)
    with open("email.html", "w") as f:
        f.write(html_simple)

    # soup = BeautifulSoup(html_simple)
    # text = soup.getText()
    # print(text)

    print("_--------------------------------------------------")

    plain = html2plain(html)
    print(plain)
    with open("email.plain", "w") as f:
        f.write(plain)

    print("_--------------------------------------------------")

    md = html2plain_pandoc(html)
    print(md)
