from typing import List, Tuple

from jarvis.actions import ActionBase
from jarvis.automation.desktop import DesktopAutomation


class Context:
    """Stores current state of Jarvis application."""

    def __init__(self, desktop: DesktopAutomation):
        self.desktop = desktop
        self.action_history: List[Tuple[ActionBase, str]] = []
        self.utterance_history: List[str] = []

    @property
    def last_action(self):
        if len(self.action_history) > 0:
            action, _ = self.action_history[-1]
            return action
        return None

    @property
    def last_utterance(self):
        if len(self.utterance_history) > 0:
            return self.utterance_history[-1]
        return None

    @property
    def active_window(self) -> str:
        # Returns window name string
        return self.desktop.get_active_window()

    @property
    def available_windows(self) -> List[str]:
        # Returns list of running program names with GUIs
        self.desktop.get_list_of_windows()
