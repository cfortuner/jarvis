from jarvis.const import JARVIS_INTRO_SSML, DEFAULT_VOICE_NAME
from jarvis.nlp.text2speech import google_synthesizer
from jarvis.nlp.text2speech import audio_utils


def test_load_or_convert_text_to_speech():
    ssml = JARVIS_INTRO_SSML

    # Will call API and write audio .wav file to cache
    audio_bytes = google_synthesizer.load_or_convert_text_to_speech(
        ssml=ssml, voice_name=DEFAULT_VOICE_NAME
    )
    audio_utils.play_audio_bytes(audio_bytes)

    # Will load audio .wav file from cache
    audio_bytes = google_synthesizer.load_or_convert_text_to_speech(
        ssml=ssml, voice_name=DEFAULT_VOICE_NAME
    )
    audio_utils.play_audio_bytes(audio_bytes)
