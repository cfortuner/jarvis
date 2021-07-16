"""Actions for navigating web browsers."""

from jarvis.actions import ActionBase
from .browser_automation import BrowserAutomation


class BrowserAction(ActionBase):
    """Base class for all Browser actions.
    
    We expect the BrowserAutomation instance to be instantiated
    and passed around to all the actions.
    """
    def __init__(self, browser: BrowserAutomation):
        # TODO: We might want to change the name `browser` to avoid collisions
        self.browser = browser
