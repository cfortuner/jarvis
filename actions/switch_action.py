import logging

from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase
from .utils import compute_levenshtein_distance

class SwitchAction(ActionBase):
    DISTANCE_THRESHOLD = 2

    def __init__(self, app_name):
        self.app_name = app_name
    
    def run(self, gui: GUIAutomation):
        app = None
        windows = gui.get_list_of_windows()
        # First: Try to find exact match
        if self.app_name in windows:
            idx = windows.index(self.app_name)
            app = windows[idx]
        else:
            # Second: See if any open window has app name as
            # the substring
            for win in windows:
                if self.app_name in win:
                    app = win
                    break

            # Third: Try to do fuzzy matching to find the app
            if app == None:
                distances = list(map(
                    lambda w: compute_levenshtein_distance(w, self.app_name), 
                    windows))
                min_dist = min(distances)
                if min_dist <= self.DISTANCE_THRESHOLD:
                    idx = distances.index(min_dist)
                    app = windows[idx]
            
        if app == None:
            raise Exception(f"Failed to find any app with name {self.app_name}")

        gui.switch_to_window(app)
