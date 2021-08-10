"""Project constants."""

import os


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


COMMUNITY_ACTION_CHAINS = [
    {
        "name": "Amazon shopping cart",
        "phrases": ["amazon shopping cart", "go to amazon shopping cart"],
        "steps": [
            {
                "action_classname": "jarvis.automation.browser.browser_actions.OpenBrowser",
                "action_params": {}
            },
            {
                "action_classname": "jarvis.automation.browser.browser_actions.ChangeURL",
                "action_params": {"url": "amazon.com"}
            },
            {
                "action_classname": "jarvis.automation.browser.browser_actions.ClickLink",
                "action_params": {"link_text": "Cart"}
            },
        ]
    },
    {
        "name": "Crazy window switch",
        "phrases": ["crazy windows"],
        "steps": [
            {
                "action_classname": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "action_params": {"app_name": "code"}
            },
            {
                "action_classname": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "action_params": {"app_name": "chrome"}
            },
        ]
    }
]
