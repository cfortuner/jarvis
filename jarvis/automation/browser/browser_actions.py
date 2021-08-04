"""Actions for navigating web browsers."""

from typing import List

from jarvis.actions import ActionBase
from .browser_automation import BrowserAutomation


class BrowserAction(ActionBase):
    """Base class for all Browser actions.

    We expect the BrowserAutomation instance to be instantiated
    and passed around to all the actions.
    """
    def __init__(self, browser: BrowserAutomation):
        self.browser = browser

    @classmethod
    def automations(cls) -> List[str]:
        # List of automation instances required to initialize
        return ["browser"]
