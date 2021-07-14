import os

from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase


class LaunchAction(ActionBase):
    def __init__(self, app_name):
        self.app_name = app_name
    
    def run(self, gui: GUIAutomation):
        ret_code = gui.open_application(self.app_name)
        if ret_code != 0:
            raise Exception(f"Failed to launch the application: {ret_code}")
