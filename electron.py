"""Entrypoint called by Electron.js frontend app."""

from dataclasses import asdict
import threading
import sys
import random
import traceback
import logging

from enum import Enum

from jarvis.bridge import Bridge, BridgeMessage
from jarvis.actions import ActionBase, ActionResolver, ExecutedAction
from jarvis import const
from jarvis.const import ACTION_CHAIN_PATH, SUPPORTED_COMMANDS, DEFAULT_VOICE_NAME, JARVIS_PHRASES
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber
from jarvis.nlp.speech2text import wake_word_detector
from jarvis.actions import action_registry
from jarvis.nlp.text2speech import audio_utils
from jarvis.nlp.text2speech import google_synthesizer

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
    REGISTER_ACTION_CHAIN = 'registerActionChain'


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


def speak_text(text=None, ssml=None, enable=True, voice=DEFAULT_VOICE_NAME):
    if enable:
        audio_bytes = google_synthesizer.load_or_convert_text_to_speech(
            text=text, ssml=ssml, voice_name=voice
        )
        audio_utils.play_audio_bytes(audio_bytes)
    else:
        # For summarization, Q/A, chat
        if text is not None:
            print(text)


def speech2text(speak_mode, wake_word: bool = False):

    # start speech2Text loop and pass bridge
    # on transcript
    print("Running speech2text")
    resolver = ActionResolver()

    global current_transcript_text
    current_transcript_text = "Listening..."

    # Start the ws server
    bridge = Bridge()

    global listening
    listening = False

    # Setup subscriptions
    def on_update_transcript(msg: ClientMessage):
        print(f"Received UpdateTranscript: {msg}")
        global current_transcript_text
        current_transcript_text = msg.data

    def on_execute_command(msg: ClientMessage):
        print(f"Received ExecuteCommand: {msg}")
        # TODO: execute action from client
        # phrase = random.choices(JARVIS_PHRASES)
        # speak(text=phrase)

    def on_start_listening(msg):
        print(f"Received StartListening: {msg}")
        global listening
        # FIXME: if wake_word=True, then you need to say "higgins" to begin listening
        # regardless of the state of the UI. As the listen_for_wake_word is blocking
        # and will only exit
        if not wake_word:
            speak_text(ssml=const.get_jarvis_wake_ssml(), enable=speak_mode)
        listening = True

    def on_stop_listening(msg):
        print(f"Received StopListening: {msg}")
        global listening
        listening = False

    def on_register_action_chain(msg):
        print(f"Received register_action_chain: {msg.data}")
        chain = action_registry.register_action_chain(
            name=msg.data["name"],
            phrases=msg.data["phrases"],
            executed_actions=msg.data["executed_actions"],
            action_chain_path=ACTION_CHAIN_PATH
        )
        print(chain)
        print("Registered chain!")
        resolver.reload_user_action_chains()
        # TODO: add user phrases to Google Speech Context object...

    bridge.subscribe(ClientMessageType.UPDATE_TRANSCRIPT.value, on_update_transcript)
    bridge.subscribe(ClientMessageType.EXECUTE_ACTION.value, on_execute_command)
    bridge.subscribe(ClientMessageType.START_LISTENING.value, on_start_listening)
    bridge.subscribe(ClientMessageType.STOP_LISTENING.value, on_stop_listening)
    bridge.subscribe(ClientMessageType.REGISTER_ACTION_CHAIN.value, on_register_action_chain)

    # Start listening for client connections in a separate thread
    t = threading.Thread(target = bridge.listen)
    # t.daemon = True # die when the main thread dies
    t.start()

    # Start listening for commands
    listener = _get_transcriber('google')

    def reset_microphone_viz():
        # Reset the Siri Wave if silence is detected
        bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, False)

    # Timer which resets the Siri Wave if silence is detected
    reset_mic_viz_timer = None

    bridge.send_message(JarvisMessageType.ACTIONS_MODIFIED.value, SUPPORTED_COMMANDS)

    while True:
        if not listening:
            if wake_word:
                print("Waiting for wake word..")
                wake_word_detector.listen_for_wake_word()
                bridge.send_message(JarvisMessageType.SHOW.value)
                speak_text(ssml=const.get_jarvis_wake_ssml(), enable=speak_mode)
                listening = True
        else:
            print("We've started listening")
            # TODO: Move the generator to a background thread and pull from queue
            transcripts = listener.listen()
            for transcript in transcripts:
                if not listening:
                    break
                if transcript.text is not None:
                    current_transcript_text = transcript.text
                    bridge.send_message(JarvisMessageType.VOICE_CONTROL.value, True)
                    bridge.send_message(JarvisMessageType.TRANSCRIPT_MODIFIED.value, current_transcript_text)

                    # reset voice control after a few ms
                    if reset_mic_viz_timer is not None:
                        reset_mic_viz_timer.cancel()
                    reset_mic_viz_timer = threading.Timer(.5, reset_microphone_viz)
                    reset_mic_viz_timer.start()

                    if transcript.text == "exit":
                        print(f"Okay goodbye :)")
                        speak_text(text="Goodbye", enable=speak_mode)
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

                        # Exit as soon as the first action succeeds
                        for a in actions:
                            logging.info("Running: {} - {}".format(a.name, current_transcript_text))
                            # speak_text(text=f"Running: {current_transcript_text}")
                            speak_text(text=random.choices(JARVIS_PHRASES)[0], enable=False)
                            result = a.run()
                            logging.info("Action: {} status: {}, error: {}".format(
                                a.name, result.status, result.error)
                            )
                            if result.status == "succeeded":
                                # TODO: Support adding action chains to history
                                if isinstance(a, ActionBase):
                                    executed_action = ExecutedAction.from_action(
                                        action=a,
                                        result=result,
                                        transcript=current_transcript_text,
                                    )
                                    print(asdict(executed_action))

                                    if executed_action.result.data:
                                        speak_text(text=executed_action.result.data, enable=speak_mode)

                                    bridge.send_message(
                                        JarvisMessageType.ACTION_EXECUTED.value,
                                        asdict(executed_action)
                                    )
                                break

                    except Exception as e:
                        msg = "Uh oh! Failed to act on this: {}".format(str(e))
                        traceback.print_exc(file=sys.stdout)
                        print(msg)
                        speak_text(text="Sorry I didn't understand that.", enable=speak_mode)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run jarvis.')
    parser.add_argument('--speak', action='store_true', help="Include speech synthesis audio")
    parser.add_argument('--wake-word', action='store_true', help="Don't transcribe until wake word called.")
    args = parser.parse_args()

    try:
        speech2text(speak_mode=args.speak, wake_word=args.wake_word)
    except Exception as e:
        print(e)
