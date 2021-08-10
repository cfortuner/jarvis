"""Entrypoint called by Electron.js frontend app."""

import signal
import threading
import sys
import time
import logging

from enum import Enum

from jarvis.bridge import Bridge, BridgeMessage
from jarvis.actions import ActionResolver
from jarvis.const import SUPPORTED_COMMANDS
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber

logging.basicConfig(level=logging.INFO)

# Entrypoint for the backend -> electron communication
class ClientMessage(BridgeMessage):
    def __init__(self, messageType, data):
        super(messageType, data)
class ClientMessageType(Enum):
    STOP_LISTENING = 'stopListening'
    START_LISTENING = 'startListening'
    UPDATE_TRANSCRIPT = 'updateTranscript'
    EXECUTE_ACTION = 'executeAction'
class JarvisMessageType(Enum):
  VOICE_CONTROL = 'voiceControl'
  ACTION_EXECUTED = 'actionExecuted'
  ACTIONS_MODIFIED = 'actionsModified'
  TRANSCRIPT_MODIFIED = 'transcriptModified'
  SHOW = 'show'
  HIDE = 'hide'


def _get_transcriber(name):
    if name == "basic":
        return BasicTranscriber()  # Also Google, but via SpeechRecognition
    elif name == "google":
        return GoogleTranscriber(
            supported_commands=SUPPORTED_COMMANDS,
            single_utterance=False
        )  # Performant, streaming listener
    raise Exception("Transcriber {name} not supported!")

def speech2text():
    # start speech2Text loop and pass bridge
    # on transcript
    print("Running speech2text")
    resolver = ActionResolver()

    global current_transcript_text
    current_transcript_text = "Listening..."

    # Start the ws server
    bridge = Bridge()

    global listening
    listening = True

    # Setup subscriptions
    def on_update_transcript(message: ClientMessage):
        print(f"Received UpdateTranscript: {message}")
        global current_transcript_text
        current_transcript_text = message.data

    def on_execute_command(message: ClientMessage):
        print(f"Received ExecuteCommand: {message}")
        # TODO: execute action from client

    def on_start_listening(message):
        print(f"Received StartListening: {message}")
        global listening
        listening = True

    def on_stop_listening(message):
        print(f"Received StopListening: {message}")
        global listening
        listening = False


    bridge.subscribe(ClientMessageType.UPDATE_TRANSCRIPT.value, on_update_transcript)
    bridge.subscribe(ClientMessageType.EXECUTE_ACTION.value, on_execute_command)
    bridge.subscribe(ClientMessageType.START_LISTENING.value, on_start_listening)
    bridge.subscribe(ClientMessageType.STOP_LISTENING.value, on_stop_listening)

    # Start listening for client connections in a separate thread
    t = threading.Thread(target = bridge.listen)
    # t.daemon = True # die when the main thread dies
    t.start()

    # Start listening for commands
    listener = _get_transcriber('google')

    def silence():
        bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, False)
    silenceTimer = None


    bridge.send_message(JarvisMessageType.ACTIONS_MODIFIED.value, SUPPORTED_COMMANDS)

    while True:
        if listening:
            # TODO: Move the generator to a background thread and pull from queue
            transcripts = listener.listen()
            for transcript in transcripts:
                if transcript.text is not None:
                    current_transcript_text = transcript.text
                    bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, True)
                    bridge.send_message(JarvisMessageType.TRANSCRIPT_MODIFIED.value, current_transcript_text)

                    # reset voice control after a few ms
                    if silenceTimer is not None:
                        silenceTimer.cancel()
                    silenceTimer = threading.Timer(.5, silence)
                    silenceTimer.start()

                    if transcript.text == "exit":
                        print(f"Okay goodbye :)")
                        bridge.send_message(JarvisMessageType.TRANSCRIPT_MODIFIED.value, "")
                        bridge.send_message(JarvisMessageType.HIDE.value)
                        listening = False
                        # TODO: Don't break, jsut sleep and wait until we receive a startListening msg
                        break
                else:
                    bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, False)

                if transcript.is_final:
                    bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, False)
                    current_transcript_text = transcript.text
                    bridge.send_message(JarvisMessageType.TRANSCRIPT_MODIFIED.value, current_transcript_text)
                    print(current_transcript_text)
                    try:
                        actions = resolver.parse(cmd=current_transcript_text)
                        # phrases = []
                        # for a in actions:
                        #     for phrase in a.phrases():
                        #         phrases.append(phrase)
                        # bridge.send_message(
                        #     JarvisMessageType.ACTIONS_MODIFIED.value,
                        #     phrases
                        # )
                        # Exit as soon as the first action succeeds
                        for a in actions:
                            logging.info("Running: {} - {}".format(a.name, current_transcript_text))
                            result = a.run()
                            logging.info("Action: {} status: {}, error: {}".format(
                                a.name, result.status, result.error)
                            )
                            if result.status == "succeeded":
                                bridge.send_message(
                                    JarvisMessageType.ACTION_EXECUTED.value,
                                    a.name
                                )
                                break

                    except Exception as e:
                        msg = "Uh oh! Failed to act on this: {}".format(str(e))
                        # traceback.print_exc(file=sys.stdout)
                        logging.error(msg)
                        # break

if __name__ == "__main__":
    try:
        speech2text()
    except Exception as e:
        print(e)