"""CLI for testing the Higgins APIs.

Examples
--------
python higgins_cli.py --help
python higgins_cli.py text2intent
"""

import html
import pprint
import sys
import traceback

import click
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML

from jarvis.nlp.text2speech import speak_text

from higgins import const
from higgins.context import Context
from higgins.episode import Episode, save_episode
from higgins.higgins import Higgins
from higgins.intents.intent_resolver import OpenAIIntentResolver, RegexIntentResolver
from higgins.utils import prompt_utils

pp = pprint.PrettyPrinter(indent=2)


# CLI commands


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is on!")


def question_prompt(session, style, chat_history, chat_history_path, speak):

    def prompt_func(question):
        nonlocal chat_history, chat_history_path
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
        chat_history, is_prompt_cmd = prompt_utils.handle_prompt_commands(
            user_text, chat_history, chat_history_path=chat_history_path
        )
        if is_prompt_cmd:
            return
        prompt_utils.add_text_to_chat_history(chat_history, user_text, const.USERNAME)
        return user_text

    return prompt_func


def print_func(style):
    def func(text):
        print(
            HTML(
                f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{text}</bot-text>"
            ),
            style=style,
        )
    return func


@cli.command()
@click.option("--chat-history-path", default=None, help="Path to chat history file.")
@click.option('--speak', is_flag=True, help="Speak the answers and actions.")
def text2intent(chat_history_path, speak):
    """Parse user text 2 intent."""
    chat_history = []
    style = prompt_utils.get_default_style()
    session = prompt_utils.init_prompt_session(style=style)
    higgins = Higgins(
        intent_resolver=OpenAIIntentResolver(),  # RegexIntentResolver()
        prompt_func=question_prompt(session, style, chat_history, chat_history_path, speak),
        print_func=print_func(style),
    )
    context = Context()
    episode = None
    while True:
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{const.USERNAME}</user-prompt>: ")
        )
        chat_history, is_prompt_cmd = prompt_utils.handle_prompt_commands(
            user_text, chat_history, chat_history_path=chat_history_path
        )
        if not user_text or is_prompt_cmd:
            # NOTE: We clear the episode if the user types blank lines
            print("clearing episode...")
            episode = None
            continue

        episode_start = len(chat_history)
        prompt_utils.add_text_to_chat_history(chat_history, user_text, const.USERNAME)
        try:
            action_result = higgins.parse(user_text, episode)
            agent_text = action_result.reply_text if action_result.reply_text is not None else None
            if agent_text:
                speak_text(text=agent_text, enable=speak)
                print(
                    HTML(
                        f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{html.escape(agent_text)}</bot-text>"
                    ),
                    style=style,
                )
                prompt_utils.add_text_to_chat_history(chat_history, agent_text, const.AGENT_NAME)

            episode = Episode(
                chat_text=" ".join(chat_history[episode_start:]),
                context=context,
                action_result=action_result
            )
            save_episode(episode, db=higgins.db)
            context.add_episode(episode.episode_id)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    cli()
