import os

from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase


class ScreenshotAction(ActionBase):
    def __init__(self, copy_name: str):
        self.copy_name = copy_name
    
    def run(self, gui: GUIAutomation):
        # TODO(hari): Copy the screenshot to clipboard with specific
        # name attached to it
        gui.screenshot()
