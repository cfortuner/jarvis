"""CLI for testing the basic Jarvis APIs.

Examples
--------
python cli.py --help
python cli.py speech2text --transcriber google --stream
python cli.py text2action --text "switch to chrome" --no-execute
python cli.py speech2action --transcriber google --no-execute
"""

import logging
import time

import click

from jarvis.actions import ActionResolver
from jarvis.const import SILENCE_TIMEOUT_SEC, SUPPORTED_COMMANDS
from jarvis.automation.gui import create_gui_automation
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber

logging.basicConfig(level=logging.INFO)


## Helpers ##

def _get_transcriber(name):
    if name == "basic":
        return BasicTranscriber()  # Also Google, but via SpeechRecognition
    elif name == "google":
        return GoogleTranscriber(SUPPORTED_COMMANDS)  # Performant, streaming listener
    raise Exception("Transcriber {name} not supported!")


def _parse_and_execute_action(
    text, resolver, gui_automation, browser_automation=None, no_execute=False
):
    actions = resolver.parse(
        cmd=text,
        gui=gui_automation,
        browser=browser_automation
    )
    for a in actions:
        click.echo(f"Running: {a.name}")
        if not no_execute:
            a.run()


## CLI commands ##

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    if debug:
        click.echo(f"Debug mode is on!")


@cli.command()
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="basic")
@click.option('--stream', is_flag=True, default=False, help="Streaming mode for parsing multiple commands.")
def speech2text(transcriber, stream):
    """Convert text to speech."""
    click.echo(f"Using '{transcriber}' transcriber")
    listener = _get_transcriber(transcriber)
    click.echo(f"Listening... Say something!")
    start_time = time.time()
    while True:
        text = listener.listen()
        if text is None:
            if time.time() - start_time > SILENCE_TIMEOUT_SEC:
                logging.info("Max silence time reached. Turning off microphone..")
                break
        else:
            click.echo(f"You said: '{text}'")
            if text == "exit" or not stream:
                break
            start_time = time.time()


@cli.command()
@click.option('--text', help='Text to convert into an Action', default=None)
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
def text2action(text, no_execute):
    """Convert text to action."""
    if text is None:
        text = click.prompt('Enter text')

    resolver = ActionResolver()
    gui_automation = create_gui_automation()

    _parse_and_execute_action(
        text=text,
        resolver=resolver,
        gui_automation=gui_automation,
        no_execute=no_execute
    )


@cli.command()
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="basic")
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
@click.option('--stream', is_flag=True, default=False, help="Streaming mode for parsing multiple commands.")
def speech2action(transcriber, no_execute, stream):
    """Convert speech to action."""
    click.echo(f"Initializing..")
    resolver = ActionResolver()
    gui_automation = create_gui_automation()
    listener = _get_transcriber(transcriber)

    click.echo(f"Listening... Say something!")
    start_time = time.time()
    while True:
        text = listener.listen()
        if text is None:
            if time.time() - start_time > SILENCE_TIMEOUT_SEC:
                logging.info("Max silence time reached. Turning off microphone..")
                break
        elif text == "exit":
            break
        else:
            _parse_and_execute_action(
                text=text,
                resolver=resolver,
                gui_automation=gui_automation,
                no_execute=no_execute
            )
            if not stream:
                break
            start_time = time.time()

if __name__ == '__main__':
    cli()
