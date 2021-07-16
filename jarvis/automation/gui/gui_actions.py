"""Actions for manipulating Desktop/Mobile GUIs

Non-GUI realted operating system tasks should live elsewhere.
"""

import logging

from jarvis.actions import ActionBase
from jarvis.nlp import nlp_utils

from .gui_automation import GUIAutomation


class GUIAction(ActionBase):
    """Base class for all GUI actions.
    
    We expect the GUIAutomation instance to already be instantiated
    and be passed around to all the actions.
    """
    def __init__(self, gui: GUIAutomation):
        super().__init__()
        self.gui = gui


class LaunchAction(GUIAction):
    """Launch an application (not running yet)."""
    def __init__(self, gui: GUIAutomation, app_name: str):
        super().__init__(gui)
        self.app_name = app_name
    
    def run(self):
        ret_code = self.gui.open_application(self.app_name)
        if ret_code != 0:
            raise Exception(f"Failed to launch the application: {ret_code}")


class ScreenshotAction(GUIAction):
    """Task a screenshot."""
    def __init__(self, gui: GUIAutomation, copy_name: str):
        super().__init__(gui)
        self.copy_name = copy_name

    def run(self):
        # TODO(hari): Copy the screenshot to clipboard with specific
        # name attached to it
        self.gui.screenshot()


class SwitchAction(GUIAction):
    """Switch to application window (one that's already running).

    TODO: Move command parsing utilities to a shared nlp module.
    TODO: Support app name synonyms (e.g. "Chrome", "Google Chrome", "Browser")
    TODO: Support "last window" switch action
    """
    DISTANCE_THRESHOLD = 2

    def __init__(self, gui: GUIAutomation, app_name: str):
        super().__init__(gui)
        self.app_name = app_name
    
    def run(self):
        logging.info(f"Attemping to switch to: {self.app_name}")
        app = None
        windows = self.gui.get_list_of_windows()
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
                    lambda w: nlp_utils.compute_levenshtein_distance(w, self.app_name), 
                    windows_clean))
                min_dist = min(distances)
                if min_dist <= self.DISTANCE_THRESHOLD:
                    idx = distances.index(min_dist)
                    app = windows[idx]
            
        if app == None:
            msg = f"Failed to find any app with name {self.app_name}"
            logging.info(msg)
            raise Exception(msg)

        self.gui.switch_to_window(app)
