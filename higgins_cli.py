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

from higgins import const
from higgins.utils import prompt_utils
from jarvis.nlp.openai import completions
from jarvis.nlp.text2speech import speak_text

pp = pprint.PrettyPrinter(indent=2)

from higgins import Higgins


# CLI commands


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is on!")


def question_prompt(session, style, chat_history, speak):

    def prompt_func(question):
        print(
            HTML(
                f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{question}</bot-text>"
            ),
            style=style,
        )
        speak_text(text=question, enable=speak)
        prompt_utils.add_text_to_chat_history(chat_history, question, const.AGENT_NAME)
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{const.USERNAME}</user-prompt>: ")
        )
        prompt_utils.add_text_to_chat_history(chat_history, user_text, const.USERNAME)
        return user_text

    return prompt_func


@cli.command()
@click.option("--chat-history-path", default=None, help="Path to chat history file.")
@click.option('--speak', is_flag=True, help="Speak the answers and actions.")
def text2intent(chat_history_path, speak):
    """Parse user text 2 intent."""
    chat_history = []
    style = prompt_utils.get_default_style()
    session = prompt_utils.init_prompt_session(style=style)
    higgins = Higgins(prompt_func=question_prompt(session, style, chat_history, speak))
    while True:
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{const.USERNAME}</user-prompt>: ")
        )
        chat_history, is_prompt_cmd = prompt_utils.handle_prompt_commands(
            user_text, chat_history, chat_history_path=chat_history_path
        )
        if is_prompt_cmd:
            continue
        prompt_utils.add_text_to_chat_history(chat_history, user_text, const.USERNAME)
        try:
            action_result = higgins.parse(user_text)
            if action_result is None:
                agent_text = completions.open_ended_chat("\n".join(chat_history[-5:]))
            elif action_result.data is not None:
                agent_text = action_result.data
            else:
                agent_text = "How can I help you?"

            prompt_utils.add_text_to_chat_history(chat_history, agent_text, const.AGENT_NAME)
            print(
                HTML(
                    f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{agent_text}</bot-text>"
                ),
                style=style,
            )
            speak_text(text=agent_text, enable=speak)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    cli()
