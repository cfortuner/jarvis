import pytest

from jarvis.const import WAKE_WORDS, WAKE_WORD_PATHS
from jarvis.nlp.speech2text.wake_word_detector import WakeWordDetector


@pytest.mark.skip("Requires manual voice interaction.")
def test_wake_word_detector():
    print(WakeWordDetector.show_audio_devices())

    detector = WakeWordDetector(
        keywords=WAKE_WORDS,
        keyword_paths=WAKE_WORD_PATHS,
        exit_on_wake=True,
        sensitivities=[.5],
        input_device_index=None,
    )
    print(detector)

    detector.run()
