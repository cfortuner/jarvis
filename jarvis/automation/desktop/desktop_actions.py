"""Actions for manipulating Desktop/Mobile GUIs

Non-GUI realted operating system tasks should live elsewhere.
"""

import logging

from jarvis.actions import ActionBase
from jarvis.nlp import nlp_utils

from .desktop_automation import DesktopAutomation


class DesktopAction(ActionBase):
    """Base class for all Desktop actions.
    
    We expect the DesktopAutomation instance to already be instantiated
    and be passed around to all the actions.
    """
    def __init__(self, desktop: DesktopAutomation):
        super().__init__()
        self.desktop = desktop


class LaunchAction(DesktopAction):
    """Launch an application (not running yet)."""
    def __init__(self, desktop: DesktopAutomation, app_name: str):
        super().__init__(desktop)

        self.app_name = app_name
    
    def run(self):
        ret_code = self.desktop.open_application(self.app_name)
        if ret_code != 0:
            raise Exception(f"Failed to launch the application: {ret_code}")

    @classmethod
    def phrases(cls):
        return [
            "launch {app_name}",
            "open {app_name}",
        ]


class ScreenshotAction(DesktopAction):
    """Task a screenshot."""
    def __init__(self, desktop: DesktopAutomation):
        super().__init__(desktop)

    def run(self):
        # TODO(hari): Copy the screenshot to clipboard with specific
        # name attached to it
        self.desktop.screenshot()

    @classmethod
    def phrases(cls):
        return [
            "take a screenshot",
            "screenshot",
            "capture screen",
        ]


class SwitchAction(DesktopAction):
    """Switch to application window (one that's already running).

    TODO: Move command parsing utilities to a shared nlp module.
    TODO: Support app name synonyms (e.g. "Chrome", "Google Chrome", "Browser")
    TODO: Support "last window" switch action
    """
    DISTANCE_THRESHOLD = 2

    def __init__(self, desktop: DesktopAutomation, app_name: str):
        super().__init__(desktop)

        self.app_name = app_name
    
    def run(self):
        logging.info(f"Attemping to switch to: {self.app_name}")
        app = None
        windows = self.desktop.get_list_of_windows()
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

        self.desktop.switch_to_window(app)

    @classmethod
    def phrases(self):
        return [
            "switch to {app_name}",
        ]
