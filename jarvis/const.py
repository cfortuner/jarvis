"""Project constants."""

import os

# Parameter names to exclude for serialization
AUTOMATION_PARAMS = ["browser", "desktop"]

# The Google Speech Recognition quality improves if you "prime" it with known keywords
# In the future, we can auto-generate a list of supported commands and keywords and pass
# it to the speech recognition engine. For now, I'm just hard-coding it here so we can share
# between the CLI and the DesktopApp.
SUPPORTED_COMMANDS = [
    "switch to chrome",
    "switch to code",
    "switch to terminal",
    "switch to python",
    "open chrome",
    "new tab",
    "close window",
    "scroll down",
    "exit",
]

# How long to wait before turning of the microphone (seconds)
SILENCE_TIMEOUT_SEC = 10

# How long to wait between GUI actions (e.g. debugging)
SPEED_LIMIT = float(os.getenv("SPEED_LIMIT", "0"))


COMMON_ACTION_CHAINS = [
    # {
    #     "name": "amazon shopping cart",
    #     "phrases": ["amazon shopping cart", "go to amazon shopping cart"],
    #     "steps": [
    #         {
    #             "class_path": "jarvis.automation.browser.browser_actions.OpenBrowser",
    #             "params": {}
    #         },
    #         {
    #             "class_path": "jarvis.automation.browser.browser_actions.ChangeURL",
    #             "params": {"url": "amazon.com"}
    #         },
    #         {
    #             "class_path": "jarvis.automation.browser.browser_actions.ClickLink",
    #             "params": {"link_text": "Cart"}
    #         },
    #     ]
    # },
    {
        "name": "Crazy window switch",
        "phrases": ["crazy windows"],
        "steps": [
            {
                "class_path": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "params": {"app_name": "code"}
            },
            {
                "class_path": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "params": {"app_name": "chrome"}
            },
        ]
    }
]

# Speech Synthesis
DEFAULT_VOICE_NAME = "en-GB-Wavenet-D"
JARVIS_PHRASES = [
    "Right!",
    "Very well!",
    "As you wish!",
    "Certainly.",
    "It shall be done!",
]
JARVIS_WAKE_PHRASES = [
    "Sir",
    "Sire",
    "M'lady",
    "M'lord",
    "Ready and waiting",
    # not as good...
    # "At your service",
    # "My queen",
    # "My lord",
    # "Your Grace",
    # "Your highness",
    # "Your excellency",
]
USERNAME = "Brendan"
AGENT_NAME = "Higgins"
JARVIS_INTRO_SSML = f"""
<speak>
    <break time="200ms"/>
    Hello {USERNAME}, <break time="400ms"/>
    How can I help you?
</speak>
"""
JARVIS_WAKE_SSML = """
<speak>
    <break time="400ms"/>
    {wake_phrase} <break time="400ms"/>
</speak>
"""


def get_jarvis_wake_ssml():
    import random
    phrase = random.choices(JARVIS_WAKE_PHRASES)
    return JARVIS_WAKE_SSML.format(wake_phrase=phrase)


# User macros
ACTION_CHAIN_PATH = "./action_chains.json"

# Some files are platform specific like mac_automation.py.
# To avoid loading them, we only load files that contain actions
# which are determined by looking for file with this suffix.
ACTION_FILE_SUFFIX = "_actions.py"

OPENAI_CACHE_DIR = "openai_cache/"

WAKE_WORDS = ["jarvis"]
WAKE_WORD_PATHS = ["higgins__en_mac_2021-09-25-utc_v1_9_0.ppn"]  # "Higgins"
