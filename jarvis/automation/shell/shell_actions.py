"""Actions for executing shell commands."""

from jarvis.actions import ActionBase
from jarvis.automation.desktop import DesktopAutomation


class ShellAction(ActionBase):
    """Base class for all Shell actions.

    We expect the BrowserAutomation instance to be instantiated
    and passed around to all the actions.
    """
    def __init__(self, desktop: DesktopAutomation):
        self.desktop = desktop
