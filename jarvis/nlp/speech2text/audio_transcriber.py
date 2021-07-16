
class AudioTranscriber:
    """Base class for all speech-to-text listeners.
    
    These classes transcribe microphone audio to text. In the future,
    we should also support pre-recorded audio files for integration tests.
    """

    def listen(self) -> str:
        raise NotImplementedError
