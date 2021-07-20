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
from jarvis.automation.desktop import create_desktop_automation
from jarvis.const import SILENCE_TIMEOUT_SEC, SUPPORTED_COMMANDS
from jarvis.nlp import nlp_utils
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
    text, resolver, desktop_automation, browser_automation=None, no_execute=False
):
    actions = resolver.parse(
        cmd=text,
        desktop=desktop_automation,
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
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="google")
@click.option('--no-stream', is_flag=True, help="Exit after first command is transcribed.")
def speech2text(transcriber, no_stream):
    """Convert text to speech."""
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
@click.option('--text', help='Text to convert into an Action', default=None)
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
def text2action(text, no_execute):
    """Convert text to action."""
    if text is None:
        text = click.prompt('Enter text')

    resolver = ActionResolver()
    desktop_automation = create_desktop_automation()

    _parse_and_execute_action(
        text=text,
        resolver=resolver,
        desktop_automation=desktop_automation,
        no_execute=no_execute
    )


@cli.command()
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="google")
@click.option('--no-execute', is_flag=True, default=False, help='Print Action(s) but do NOT execute them')
@click.option('--no-stream', is_flag=True, help="Exit after first command is transcribed.")
def speech2action(transcriber, no_execute, no_stream):
    """Convert speech to action."""
    click.echo(f"Initializing..")
    resolver = ActionResolver()
    desktop_automation = create_desktop_automation()
    listener = _get_transcriber(transcriber)
    click.echo(f"Listening... Say something!")
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
                
                _parse_and_execute_action(
                    text=transcript.text,
                    resolver=resolver,
                    desktop_automation=desktop_automation,
                    no_execute=no_execute
                )

                if no_stream:
                    return


if __name__ == '__main__':
    cli()
