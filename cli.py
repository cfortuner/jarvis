"""CLI for testing the basic Jarvis APIs.

Examples
--------
python cli.py --help
python cli.py speech2text
python cli.py text2action --no-execute
python cli.py speech2action
"""

import logging
import pprint

import click

from jarvis.actions import ActionBase, ActionResolver, ExecutedAction
from jarvis.actions import action_registry
from jarvis.const import SUPPORTED_COMMANDS
from jarvis.nlp import nlp_utils
from jarvis.nlp.openai import openai_action_resolver
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber

logging.basicConfig(level=logging.INFO)

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
def speech2action(transcriber, no_execute, openai):
    """Convert speech to action."""
    click.echo("Initializing..")
    resolver = ActionResolver()
    listener = _get_transcriber(transcriber)
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
            answer, resp = openai_action_resolver.ask_web_navigation_model(cmd)
            pp.pprint(answer)
        else:
            chain = openai_action_resolver.infer_action_chain(cmd, action_classes)
            pp.pprint(chain.to_dict())


if __name__ == '__main__':
    cli()
