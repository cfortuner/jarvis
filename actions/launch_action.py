import os

from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase


class LaunchAction(ActionBase):
    def __init__(self, app_name):
        self.app_name = app_name
    
    def run(self, gui: GUIAutomation):
        # TODO(hari): Find if this is a valid app name before launching
        os.system(self.app_name)
