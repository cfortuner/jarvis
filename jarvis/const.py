"""Project constants."""

# The Google Speech Recognition quality improves if you "prime" it with known keywords
# In the future, we can auto-generate a list of supported commands and keywords and pass
# it to the speech recognition engine. For now, I'm just hard-coding it here so we can share
# between the CLI and the DesktopApp.
SUPPORTED_COMMANDS = [
    "switch to chrome",
    "switch to code",
    "switch to terminal",
    "open chrome",
    "new tab",
    "close window",
    "scroll down",
]

# How long to wait before turning of the microphone (seconds)
SILENCE_TIMEOUT_SEC = 15
