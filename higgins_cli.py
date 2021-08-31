"""CLI for testing the Higgins APIs.

Examples
--------
python higgins_cli.py --help
python higgins_cli.py text2intent
"""

import pprint
import traceback
import sys

import click
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from jarvis import const

from higgins.utils import prompt_utils


pp = pprint.PrettyPrinter(indent=2)


# CLI commands


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is on!")


@cli.command()
@click.option("--chat-history-path", default=None, help="Path to chat history file.")
def text2intent(chat_history_path):
    """Parse user text 2 intent."""
    style = prompt_utils.get_default_style()
    session = prompt_utils.init_prompt_session(style=style)
    chat_history = []
    while True:
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{const.USERNAME}</user-prompt>: ")
        )
        chat_history = prompt_utils.handle_prompt_commands(
            user_text, chat_history, chat_history_path=chat_history_path
        )
        try:
            bot_text = "Hello, Brendan"
            print(
                HTML(
                    f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{bot_text}</bot-text>"
                ),
                style=style,
            )
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    cli()
