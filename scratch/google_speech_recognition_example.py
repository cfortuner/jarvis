"""Google Speech Recognition Examples.

Techniques for achieving real-time speech-to-text:
1. Google streaming API
2. Offline model

We can prime the model with our list of supported commands/keywords for more accurate translations:
https://cloud.google.com/speech-to-text/docs/speech-adaptation

And set `single_utterance=True` for voice commands
https://cloud.google.com/speech-to-text/docs/reference/rpc/google.cloud.speech.v1#streamingrecognitionconfig
"""

import re
import sys

from google.cloud import speech

import pyaudio
import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


def verify_google_auth_is_working():
    """Verify auth is working and project is set.
    
    >> gcloud config list
    >> gcloud auth application-default login  
    """
    client = speech.SpeechClient()

    gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate=RATE, chunk=CHUNK):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_for_command(responses, supported_commands):
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

        # Command recognition - Eagerly return command if matches result
        if transcript.lstrip().rstrip().lower() in supported_commands:
            return transcript.lower()

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
            print(f"Transcript: {transcript}")
            print(f"Overwrite_chars: {overwrite_chars}")
            print(transcript + overwrite_chars)

            # Exit recognition
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                return "exit"
        
            # Command recognition - return command if matches result
            if transcript.lstrip().rstrip().lower() in supported_commands:
                return transcript.lower()

            num_chars_printed = 0


def test_streaming_speech_recognition():
    """Call the streaming speech-to-text API.
    
    https://cloud.google.com/speech-to-text/docs/streaming-recognize#speech-streaming-recognize-python
    https://github.com/googleapis/python-speech/blob/master/samples/microphone/transcribe_streaming_infinite.py
    https://github.com/googleapis/python-speech/blob/master/samples/microphone/transcribe_streaming_mic.py
    https://github.com/Uberi/speech_recognition/blob/master/examples/threaded_workers.py
    """
    
    # The listener will exit if it recognizes these commands:
    SUPPORTED_COMMANDS = [
        "switch to chrome",
        "open chrome",
        "new tab",
        "close window",
        "scroll down",
    ]

    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "en-US"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True, # single_utterance=True,
    )

    with MicrophoneStream() as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        command = listen_for_command(responses, SUPPORTED_COMMANDS)

        print(f"Executing user command: {command}")


if __name__ == "__main__":
    # verify_google_auth_is_working()
    test_streaming_speech_recognition()
