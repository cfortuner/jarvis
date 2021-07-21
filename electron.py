"""Entrypoint called by Electron.js frontend app."""

from enum import Enum
import json
import logging
import math
import random
import sys
import time

import click

from jarvis.actions import ActionResolver
from jarvis.const import SILENCE_TIMEOUT_SEC, SUPPORTED_COMMANDS
from jarvis.automation.desktop import create_desktop_automation
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber

logging.basicConfig(level=logging.INFO)


## Helpers ##

# Entrypoint for the backend -> client communication

# This needs to be kept in sync with BackendMessageType in ./electron/pythonBridge.ts
class ClientMessageType(Enum):
    VOICE_CONTROL = 'voiceControl'
    DISPLAY_ACTIONS = 'displayActions'
    CLEAR_ACTIONS = 'clearActions'
    SHOW = 'show'
    HIDE = 'hide'


def _send_message(messageType, data=None):
    """Use sendMessage to send message to the electron app."""
    print("Sending data", data)
    sys.stdout.flush()
    print(json.dumps({ 'type': messageType, 'data': data}))
    sys.stdout.flush()


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
@click.option('--transcriber', type=click.Choice(['basic', 'google']), default="basic")
def speech2text(transcriber):
    """Convert text to speech."""
    print("Running speech2text")
    resolver = ActionResolver()
    desktop_automation = create_desktop_automation()
    listener = _get_transcriber(transcriber)
    while True:
        _send_message(ClientMessageType.DISPLAY_ACTIONS.value, ["Listening.."])
        last_text = None
        transcripts = listener.listen()
        for transcript in transcripts:
            if transcript.text is not None and transcript.text != last_text:
                _send_message(ClientMessageType.VOICE_CONTROL.value, True)
                _send_message(ClientMessageType.DISPLAY_ACTIONS.value, [transcript.text])
                last_text = transcript.text
                if transcript.is_final and not transcript.deadline_exceeded:
                    try:            
                        _parse_and_execute_action(
                            text=transcript.text,
                            resolver=resolver,
                            desktop_automation=desktop_automation
                        )
                    except Exception as e:
                        print(e)
            else:
                # _send_message(ClientMessageType.VOICE_CONTROL.value, False)
                print("Transcript empty or text is the same")
        
        print("transcript complete")
        _send_message(ClientMessageType.VOICE_CONTROL.value, False)
        

if __name__ == "__main__":
    cli()
