"""CLI for testing the basic Jarvis APIs.

Examples
--------
python cli.py --help
python cli.py speech2text --transcriber google
python cli.py text2action --text "switch to chrome" --no-execute
python cli.py speech2action --transcriber google --no-execute
"""

import logging

import click

from jarvis.actions import ActionResolver
from jarvis.automation.gui import create_gui_automation
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber

logging.basicConfig(level=logging.INFO)


## Helpers ##

def _get_transcriber(name):
    if name == "basic":
        return BasicTranscriber()  # Also Google, but via SpeechRecognition
    elif name == "google":
        return GoogleTranscriber()  # Performant, streaming listener
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
def speech2text(transcriber):
    """Convert text to speech."""
    click.echo(f"Using '{transcriber}' transcriber")
    listener = _get_transcriber(transcriber)
    click.echo(f"Listening... Say something!")
    text = listener.listen()
    click.echo(f"You said: '{text}'")

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
def speech2action(transcriber, no_execute):
    """Convert speech to action."""
    resolver = ActionResolver()
    gui_automation = create_gui_automation()
    listener = _get_transcriber(transcriber)

    click.echo(f"Listening... Say something!")
    text = listener.listen()

    _parse_and_execute_action(
        text=text,
        resolver=resolver,
        gui_automation=gui_automation,
        no_execute=no_execute
    )


if __name__ == '__main__':
    cli()
