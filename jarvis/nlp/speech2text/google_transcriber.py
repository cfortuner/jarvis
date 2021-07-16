import logging
import re
import sys
from typing import List

from google.cloud import speech

from jarvis.devices.microphone import MicrophoneStream
from jarvis.nlp import nlp_utils

from .audio_transcriber import AudioTranscriber

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
LANGUAGE_CODE = "en-US"


def _get_speech_contexts(supported_commands):
    """Tell Google about phrases we expect to improve transcription quality.
    
    https://cloud.google.com/speech-to-text/docs/speech-adaptation
    """
    contexts = []

    # Add the hard-coded leaf-node commands
    contexts.append(speech.SpeechContext(phrases=supported_commands))

    # Add common command prefixes and keywords
    prefixes = ["launch", "switch to", "open", "Chrome", "Spotify", "code", "terminal"]
    contexts.append(speech.SpeechContext(phrases=prefixes))

    return contexts


class GoogleTranscriber(AudioTranscriber):
    """Parse audio from microphone using Google Cloud Speech API.

    This class transcribes microphone audio to text. In the future, we
    should also support pre-recorded audio files for integration tests.
    """
    def __init__(self, supported_commands: List[str] = None):
        """Instantiate the Listener.

        Args:
            supported_commands (List[str], optional): A hard-coded list of text commands. If we detect
                one of these phrases during transcription, we can exit early and return the phrase, 
                instead of waiting for Google to detect that the user has stopped speaking.
        """
        self.supported_commands = supported_commands or []
        self._client = speech.SpeechClient()        
        self._config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=LANGUAGE_CODE,
                model="command_and_search",  # Recommended for short commands
                speech_contexts=_get_speech_contexts(supported_commands)
            ),
            interim_results=True,
            single_utterance=True,
        )

    def listen(self) -> str:
        """Record and transcribe user utterance using Microphone.

        Returns:
            str: Detected utterance
        """
        with MicrophoneStream(rate=RATE, chunk=CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = self._client.streaming_recognize(self._config, requests)
            utterance = _handle_transcription_stream(responses, self.supported_commands)
            logging.info(f"Google Detected: '{utterance}'")
            return utterance


def _is_supported_command(text, supported_commands):
    return nlp_utils.normalize_text(text) in supported_commands


def _handle_transcription_stream(responses, supported_commands):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.

    TODO: The SpeechApp GUI might need access to this stream so it can display what
    it's seeing to the user.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Eagerly return command if matches result
        if _is_supported_command(transcript, supported_commands):
            logging.info("Detected a supported command! Exiting early.")
            return transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            logging.info(f"Current transcript: {transcript + overwrite_chars}")

            # Exit recognition
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                logging.info("Detected exit request. Exiting..")
                return "exit"
        
            num_chars_printed = 0

            return transcript

    # TODO: Do we raise or return a code?
    raise Exception("No speech detected")
