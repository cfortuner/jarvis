"""CLI for testing the basic Jarvis APIs.

Examples
--------
python cli.py --help
python cli.py speech2text
python cli.py text2action --no-execute
python cli.py speech2action
"""

import os
from pathlib import Path
import pprint
import traceback
import sys

import click
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import NestedCompleter

from jarvis.actions import ActionBase, ActionResolver, ExecutedAction
from jarvis.actions import action_registry
from jarvis.const import SUPPORTED_COMMANDS, DEFAULT_VOICE_NAME
from jarvis import const
from jarvis.nlp import nlp_utils
from jarvis.nlp.openai import openai_action_resolver, completions, navigation, search
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber
from jarvis.nlp.speech2text import wake_word_detector
from jarvis.nlp.text2speech import audio_utils
from jarvis.nlp.text2speech import google_synthesizer


# logging.basicConfig(level=logging.WARNING)

pp = pprint.PrettyPrinter(indent=2)


## Helpers ##

def _get_transcriber(name):
    if name == "basic":
        return BasicTranscriber()  # Also Google, but via SpeechRecognition
    elif name == "google":
        return GoogleTranscriber(
            supported_commands=SUPPORTED_COMMANDS,
            single_utterance=False
        )  # Performant, streaming listener
    raise Exception("Transcriber {name} not supported!")


def _speak_text(text=None, ssml=None, enable=True, voice=DEFAULT_VOICE_NAME):
    if enable:
        audio_bytes = google_synthesizer.load_or_convert_text_to_speech(
            text=text, ssml=ssml, voice_name=voice
        )
        audio_utils.play_audio_bytes(audio_bytes)


def parse_and_execute_action(text, resolver, no_execute=False, openai=False):
    if openai:
        actions = resolver.attempt_model_based_resolve(text)
    else:
        actions = resolver.parse(cmd=text)
    print("Matching actions: ", actions)
    for a in actions:
        print(f"Running: {a.name}")
        if not no_execute:
            result = a.run()
            print("Action result", result)
            if result.status == "succeeded":
                # TODO: Support adding action chains to history
                if isinstance(a, ActionBase):
                    executed_action = ExecutedAction.from_action(
                        action=a,
                        result=result,
                        transcript=text,
                    )
                    print(executed_action)
                break


## CLI commands ##

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is on!")


@cli.command()
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="google")
@click.option('--no-stream', is_flag=True, help="Exit after first command is transcribed.")
@click.option('--wake-word', is_flag=True, help="Wait until wake word is called.")
def speech2text(transcriber, no_stream, wake_word):
    """Convert text to speech."""
    if wake_word:
        click.echo("Waiting for wake word..")
        wake_word_detector.listen_for_wake_word()

    listener = _get_transcriber(transcriber)
    click.echo(f"Listening... Say something!")
    while True:
        transcripts = listener.listen()
        for transcript in transcripts:
            if transcript.is_final:
                if transcript.deadline_exceeded:
                    click.echo(f"Silence detected. Exiting...")
                    return
                click.echo(f"Final transcript: '{transcript.text}'")
                if no_stream or transcript.text == "exit":
                    return
            elif transcript.text is not None:
                nlp_utils.display_live_transcription(transcript.text, transcript.overwrite_chars)
            else:
                click.echo(f"No results yet.")


@cli.command()
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
@click.option('--openai', is_flag=True, default=False, help='Use GPT3-based OpenAI action resolver')
def text2action(no_execute, openai):
    """Convert text to action."""
    resolver = ActionResolver()

    while True:
        text = click.prompt('Enter text')
        try:
            parse_and_execute_action(
                text=text,
                resolver=resolver,
                no_execute=no_execute,
                openai=openai
            )
        except Exception as e:
            print(e)


@cli.command()
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="google")
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
@click.option('--openai', is_flag=True, default=False, help='Use GPT3-based OpenAI action resolver')
@click.option('--wake-word', is_flag=True, help="Wait until wake word is called.")
@click.option('--question', is_flag=True, help="Answer the user question.")
@click.option('--speak', is_flag=True, help="Speak the answers and actions.")
def speech2action(transcriber, no_execute, openai, wake_word, question, speak):
    """Convert speech to action."""
    click.echo("Initializing..")
    resolver = ActionResolver()
    listener = _get_transcriber(transcriber)

    if wake_word:
        click.echo("Waiting for wake word..")
        wake_word_detector.listen_for_wake_word()
        _speak_text(ssml=const.get_jarvis_wake_ssml(), enable=speak)

    click.echo("Listening... Say something!")
    while True:
        transcripts = listener.listen()
        for transcript in transcripts:
            if transcript.is_final:
                if transcript.deadline_exceeded:
                    click.echo(f"Silence detected. Exiting...")
                    return

                assert transcript.text is not None, "We shouldn't have an empty transcript thats final unless its silence"
                click.echo(f"Final transcript: '{transcript.text}'")

                if transcript.text == "exit":
                    return
                elif question:
                    print(_answer_question(transcript.text, speak=speak))
                else:
                    parse_and_execute_action(
                        text=transcript.text,
                        resolver=resolver,
                        no_execute=no_execute,
                        openai=openai,
                    )


@cli.command()
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
def openai(no_execute):
    action_classes = action_registry.load_action_classes_from_modules("jarvis/automation")
    while True:
        cmd = click.prompt('Enter command')
        if no_execute:
            answer = navigation.ask_web_navigation_model(cmd)
            pp.pprint(answer)
        else:
            chain = openai_action_resolver.infer_action_chain(cmd, action_classes)
            pp.pprint(chain.to_dict())


# OPENAI Stuff


def _answer_question(question, speak=False):
    try:
        resp = search.ask_question(
            question=question,
            file_id="file-u7jUNn5dIIvV4cVMMeROSyRI",  # our personal db of information
        )
        answer = resp["answers"][0]
        _speak_text(text=answer, enable=speak)
        return answer
    except Exception as e:
        print(e)


def _get_prompt_session(history_path, style):
    # https://python-prompt-toolkit.readthedocs.io/en/stable/pages/dialogs.html
    # Yes/No, or List of options, etc
    # https://python-prompt-toolkit.readthedocs.io/en/stable/pages/asking_for_input.html
    # Custom WordCompleter, FuzzyCompleter

    completer = NestedCompleter.from_nested_dict({
        'show': {
            'history': None,
            'commands': {
                'interface': {'brief'}
            }
        },
        "clear": {
            "history": None,
        },
        'exit': None,
        "quit": None,
    })

    kwargs = dict(
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        style=style,
    )
    if history_path:
        kwargs["history"] = FileHistory(history_path)

    return PromptSession(**kwargs)


def _dummy_answer_question():
    return f"Hello, {const.USERNAME}"


def _get_prompt_history(session, limit=10):
    # Ordered chronologically in desceneding order
    messages = []
    for text in session.history.load_history_strings():
        messages.append(text)
        if len(messages) >= limit:
            return messages
    return messages


def _load_chat_history(chat_history_path):
    history = []
    if os.path.exists(chat_history_path):
        with open(chat_history_path) as f:
            context = f.readlines()
            return [line.strip() for line in context]
    return history


def _save_chat_history(history, chat_history_path):
    Path(chat_history_path).parent.mkdir(parents=True, exist_ok=True)
    with open(chat_history_path, "w") as f:
        f.write("\n".join(history))


def _add_text_to_chat_history(history, text, speaker):
    text = f"{speaker.upper()}: {text}"
    history.append(text)


@cli.command()
@click.option('--chat-history-path', default="chat_history.txt", help='Path to chat history file.')
@click.option(
    '--mode',
    type=click.Choice(["AnswerQuestion", "NavigateWeb", "GenerateQuestions", "Teach", "Chat", "Ignore"]),
    default="Chat",
    help="Which model behaviors to summon"
)
def chat(chat_history_path, mode):
    style = Style.from_dict({
        "": "#ffffff",  # default
        "user-prompt": "#884444",
        "bot-prompt": "#00aa00",
        "bot-text": "#A9A9A9",
    })
    session = _get_prompt_session("promptkit_history.txt", style=style)
    chat_history = _load_chat_history(chat_history_path)
    print(HTML(f"<bot-prompt>Higgins</bot-prompt>: <bot-text>Hello, {const.USERNAME}.</bot-text>"), style=style)
    while True:
        user_text = session.prompt(
            message=HTML(f"<user-prompt>{const.USERNAME}</user-prompt>: "),
            mouse_support=False,  # breaks the copy and paste from terminal
        )  # multiline=True
        if user_text.lower().strip() in ["exit", "quit"]:
            _save_chat_history(chat_history, chat_history_path)
            sys.exit(0)
        elif user_text.lower().strip() == "show history":
            print("\n".join(chat_history[-10:]))
            continue
        elif user_text.lower().strip() == "clear history":
            chat_history = []
            continue
        try:
            if mode == "AnswerQuestions" or user_text.lower().startswith("ask"):
                user_text = user_text.lstrip("ask").strip()
                bot_text = _answer_question(user_text)
            elif mode == "NavigateWeb" or user_text.lower().startswith("nav"):
                user_text = user_text.lstrip("nav").strip()
                bot_text = navigation.ask_web_navigation_model(user_text)
            elif mode == "GenerateQuestions" or user_text.lower().startswith("clarify"):
                user_text = user_text.lstrip("clarify").strip()
                text = "\n".join(chat_history[-5:] + [f"{const.USERNAME}: " + user_text])
                questions = completions.generate_questions(text, mode="finetune")
                bot_text = " ".join(questions)
            elif mode == "Teach":
                bot_text = session.prompt(message=HTML(f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: "))
            elif mode == "Ignore":
                bot_text = _dummy_answer_question()
            else:
                text = "\n".join(chat_history[-10:])
                bot_text = completions.open_ended_chat(text)
            _add_text_to_chat_history(chat_history, user_text, const.USERNAME)
            _add_text_to_chat_history(chat_history, bot_text, const.AGENT_NAME)
            if mode != "Teach":
                print(HTML(f"<bot-prompt>{const.AGENT_NAME}</bot-prompt>: <bot-text>{bot_text}</bot-text>"), style=style)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        finally:
            _save_chat_history(chat_history, chat_history_path)



if __name__ == '__main__':
    cli()
