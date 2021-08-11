"""Convert text to speech and play audio.

Libraries for playing audio:
- https://github.com/TaylorSMarks/playsound (simple, play from file only)
- https://github.com/jleb/pyaudio (low-level)
- https://github.com/jiaaro/pydub (popular!)
- https://github.com/hamiltron/py-simple-audio (pydub benefits from this being installed)
Might need to `brew install ffmpeg` 

"""
import logging
import os

from google.cloud import texttospeech
from google.cloud.texttospeech import (
    AudioEncoding,
    SsmlVoiceGender
)

from pydub import AudioSegment
from pydub.playback import play

from jarvis.nlp import nlp_utils


def list_voices():
    """Lists the available voices."""

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        # Display the voice's name. Example: tpc-vocoded
        print(f"Name: {voice.name}")

        # Display the supported language codes for this voice. Example: "en-US"
        for language_code in voice.language_codes:
            print(f"Supported language: {language_code}")

        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print(f"SSML Voice Gender: {ssml_gender.name}")

        # Display the natural sample rate hertz for this voice. Example: 24000
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")

    return voices


def convert_text_to_speech(
    text=None,
    ssml=None,
    voice_name=None,  # If set, will override the following 2 params
    voice_gender=SsmlVoiceGender.FEMALE,
    language_code="en-US",
    encoding=AudioEncoding.LINEAR16,
):
    """Synthesizes speech from the input string of text or ssml.

    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/

        LINEAR16 = Wav files (uncompressed)
        MP3 (compressed, for distribution)
    """
    assert text is not None or ssml is not None, "must provide text or ssml"

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text, ssml=ssml)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=voice_gender, name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=encoding,
        speaking_rate=1.05,
        pitch=0,  # -20,20
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The `response.audio_content` is binary.
    return response.audio_content


def play_audio_bytes(bytes):
    # LINEAR_16 / Wav encoding
    sound = AudioSegment(data=bytes)
    play(sound)


def play_audio_from_file(fpath):
    sound = AudioSegment.from_file(fpath, format="wav")
    play(sound)


def save_audio_to_file(fpath, audio_bytes, tags=None):
    from pathlib import Path
    Path(fpath).parent.mkdir(parents=True, exist_ok=True)
    sound = AudioSegment(data=audio_bytes)
    sound.export(fpath, format="wav", tags=tags)


def load_audio_from_file(fpath, format="wav"):
    # https://github.com/jiaaro/pydub/issues/402
    # sound = AudioSegment.from_file(fpath, format="wav")
    # sound.raw_data  <-- doesn't have headers
    with open(fpath, "rb") as f:
        audio_bytes = f.read()
    return audio_bytes


def load_or_convert_text_to_speech(
    text=None,
    ssml=None,
    voice_name=None,  # If set, will override the following 2 params
    voice_gender=SsmlVoiceGender.FEMALE,
    language_code="en-US",
    encoding=AudioEncoding.LINEAR16,  # wav
    cache_dir="audio_cache/",
):
    assert text is not None or ssml is not None, "must provide text or ssml"
    text_hash = nlp_utils.hash_normalized_text(f"{text or ssml}__{voice_name}")
    fpath = os.path.join(cache_dir, f"{text_hash}.wav")
    if os.path.exists(fpath):
        print(f"Found existing audio file for '{text or ssml}'")
        audio_bytes = load_audio_from_file(fpath)
    else:
        print("Converting text to speech")
        audio_bytes = convert_text_to_speech(
            text=text,
            ssml=ssml,
            voice_name=voice_name,
            voice_gender=voice_gender,
            language_code=language_code,
            encoding=encoding
        )
        print(f"No existing audio file found. Saving audio file {fpath}")
        save_audio_to_file(fpath, audio_bytes, tags={
            "text": text or ssml, "hash": text_hash}
        )
    return audio_bytes


def main(text=None, ssml=None, voice_name=None):
    if text is not None:
        audio_bytes = load_or_convert_text_to_speech(text=text, voice_name=voice_name)
        play_audio_bytes(audio_bytes)
    elif ssml is not None:
        audio_bytes = load_or_convert_text_to_speech(ssml=ssml, voice_name=voice_name)
        play_audio_bytes(audio_bytes)
    else:
        while True:
            text_input = input("Text: ")
            audio_bytes = load_or_convert_text_to_speech(text=text_input, voice_name=voice_name)


if __name__ == "__main__":
    ssml = "<speak>Hello there.</speak>"
    text = "Hey Brendan, what's up?"
    ssml = """
    <speak>
        Hey there.
        <break time="300ms"/> How's your day going?
        <break time="800ms"/> It's been a rough week.. Not many things happening..
        <break time="1000ms"/> What would you like to do?
    </speak>
    """
    text = """Hey there... How's your day going? It's been a rough week.. Not many things happening.. What would you like to do?
    """

    voices = list_voices()
    # audio_bytes = convert_text_to_speech(text=text)
    # audio_bytes = convert_text_to_speech(ssml=ssml)

    # fpath = "output.wav"
    # save_audio_to_file(fpath, audio_bytes)
    # play_audio_from_file(fpath)
    # play_audio_bytes(audio_bytes)

    # Female - en-US = en-US-Wavenet-H, en-US-Wavenet-F
    # Female - en-GB = en-GB-Wavenet-A, en-GB-Wavenet-C, en-GB-Wavenet-F
    # Female - en-IN = en-IN-Wavenet-D, en-IN-Wavenet-A
    # Male - en-US = Sucks
    # Male - en-GB = en-GB-Wavenet-B, en-GB-Wavenet-D (slightly speeded up: 1.05)
    # Male - en-IN = en-IN-Wavenet-B, en-IN-Wavenet-C

    for voice in voices.voices:
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)
        if ("en-GB" in voice.language_codes and gender == SsmlVoiceGender.MALE and "Wavenet" in voice.name):
            print(voice.name)
            # main(ssml=ssml, voice_name=voice.name)
            main(text=text, voice_name=voice.name)


#     main(ssml=ssml)
