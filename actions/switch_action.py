"""Switch to window/application.

TODO: Move command parsing utilities to a shared nlp module.
TODO: Support app name synonyms (e.g. "Chrome", "Google Chrome", "Browser")
TODO: Support "last window" switch action
"""

import logging

from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase
from .utils import compute_levenshtein_distance


class SwitchAction(ActionBase):
    DISTANCE_THRESHOLD = 2

    def __init__(self, app_name):
        self.app_name = app_name
    
    def run(self, gui: GUIAutomation):
        logging.info(f"Attemping to switch to: {self.app_name}")
        app = None
        windows = gui.get_list_of_windows()
        # TODO: Move this normalization logic somewhere else
        windows_clean = [w.lower() for w in windows]
        logging.info(f"Available Windows: {windows}")
        
        # First: Try to find exact match
        if self.app_name in windows_clean:
            idx = windows_clean.index(self.app_name)
            app = windows[idx]
        else:
            # Second: See if any open window has app name as
            # the substring
            for idx, win in enumerate(windows_clean):
                if self.app_name in win:
                    app = windows[idx]
                    break

            # Third: Try to do fuzzy matching to find the app
            if app == None:
                logging.info("Falling back to fuzzy matching.")
                distances = list(map(
                    lambda w: compute_levenshtein_distance(w, self.app_name), 
                    windows_clean))
                min_dist = min(distances)
                if min_dist <= self.DISTANCE_THRESHOLD:
                    idx = distances.index(min_dist)
                    app = windows[idx]
            
        if app == None:
            msg = f"Failed to find any app with name {self.app_name}"
            logging.info(msg)
            raise Exception(msg)

        gui.switch_to_window(app)
