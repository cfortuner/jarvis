"""Actions for manipulating Desktop/Mobile GUIs

Non-GUI realted operating system tasks should live elsewhere.
"""

import logging
from typing import List

from jarvis.actions import ActionBase, ActionResult
from jarvis.devices.mouse import Mouse
from jarvis.devices.keyboard import Keyboard
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

    @classmethod
    def automations(cls) -> List[str]:
        # List of automation instances required to initialize
        return ["desktop"]


class LaunchAction(DesktopAction):
    """Launch an application (not running yet)."""
    def __init__(self, desktop: DesktopAutomation, app_name: str):
        super().__init__(desktop)
        self.app_name = app_name

    @property
    def params(self):
        return {"app_name": self.app_name}

    def run(self):
        ret_code = self.desktop.open_application(self.app_name)
        if ret_code != 0:
            msg = f"Failed to launch the application: {ret_code}"
            return ActionResult(status="failed", error=msg)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "launch {app_name}",
            "open {app_name}",
        ]


class TypeText(DesktopAction):
    """Enter text using keyboard."""
    def __init__(self, desktop: DesktopAutomation, text: str):
        super().__init__(desktop)
        self.text = text
        self.keyboard = Keyboard()

    @property
    def params(self):
        return {"text": self.text}

    def run(self):
        print(f"Typing: {self.text}")
        self.keyboard.type(self.text)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "type {text}",
        ]


class ClickMouse(DesktopAction):
    """Click mouse."""
    def __init__(self, desktop: DesktopAutomation, button: str):
        super().__init__(desktop)
        self.button = button
        self.mouse = Mouse()

    @property
    def params(self):
        return {"button": self.button}

    def run(self):
        self.mouse.click(button=self.button)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "{button} click",
        ]


class Scroll(DesktopAction):
    """Scroll down/up/left/right from current mouse position.

    TODO: Automatically find the active window, perhaps using the keyboard
    instead of the mouse. Currently the location of the mouse pointer
    determines which window is scrolled.
    """
    def __init__(self, desktop: DesktopAutomation, direction: str):
        super().__init__(desktop)
        self.direction = direction
        self.mouse = Mouse()

    @property
    def params(self):
        return {"direction": self.direction}

    def run(self):
        self.mouse.scroll(direction=self.direction)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "scroll {direction}",
        ]


class PressKey(DesktopAction):
    """Press single key on Keyboard."""
    def __init__(self, desktop: DesktopAutomation, key: str):
        super().__init__(desktop)
        self.key = key
        self.keyboard = Keyboard()

    @property
    def params(self):
        return {"key": self.key}

    def run(self):
        print(f"Pressing: {self.key} key")
        self.keyboard.press_key(self.key)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "press {key}",
            "press {key} key",
            "press key {key}",
        ]


class KeyboardShortcut(DesktopAction):
    """Press single key on Keyboard."""
    def __init__(self, desktop: DesktopAutomation, shortcut: str):
        super().__init__(desktop)
        self.shortcut = shortcut
        self.keyboard = Keyboard()

    @property
    def params(self):
        return {"shortcut": self.shortcut}

    def run(self):
        shortcut = self.shortcut.split(" ")
        print(f"Pressing keyboard shortcut: {shortcut} from input {self.shortcut}")
        self.keyboard.shortcut(self.shortcut)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "keyboard shortcut {shortcut}",
            "type shortcut {shortcut}",
            "press shortcut {shortcut}",
            "shortcut {shortcut}",
            "hotkey {shortcut}"
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

    @property
    def params(self):
        return {"app_name": self.app_name}

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
            if app is None:
                logging.info("Falling back to fuzzy matching.")
                distances = list(map(
                    lambda w: nlp_utils.compute_levenshtein_distance(w, self.app_name),
                    windows_clean))
                min_dist = min(distances)
                if min_dist <= self.DISTANCE_THRESHOLD:
                    idx = distances.index(min_dist)
                    app = windows[idx]

        if app is None:
            msg = f"Failed to find any app with name {self.app_name}"
            logging.info(msg)
            return ActionResult(status="failed", error=msg)

        self.desktop.switch_to_window(app)

        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "switch to {app_name}",
        ]


class MaximizeWindowAction(DesktopAction):
    """Maximizes the main window of the application"""
    def __init__(self, desktop: DesktopAutomation, app_name: str):
        super().__init__(desktop)

        self.app_name = app_name

    def run(self):
        self.desktop.maximize_window(self.app_name)

    @classmethod
    def phrases(cls):
        return [
            "maximize {app_name}"
        ]


class MinimizeWindowAction(DesktopAction):
    """Minimizes the main window of the application"""
    def __init__(self, desktop: DesktopAutomation, app_name: str):
        super().__init__(desktop)

        self.app_name = app_name

    def run(self):
        self.desktop.minimize_window(self.app_name)

    @classmethod
    def phrases(cls):
        return [
            "minimize {app_name}"
        ]


class AttachWindowAction(DesktopAction):
    """Attach the main window of the application to one of the edges of the
    desktop - top half, bottom half, left half, right half"""

    EDGE_NAMES = [
        "top half",
        "bottom_half",
        "left half",
        "right half",
    ]

    def __init__(self, desktop: DesktopAutomation, app_name: str, edge_name: str):
        super().__init__(desktop)

        self.app_name = app_name
        self.edge_name = edge_name

    def run(self):
        screen_width, screen_height = self.desktop.get_screensize()
        # bounds encodes (x, y, width, height)
        if self.edge_name == 'top half':
            bounds = (0, 0, screen_width, screen_height/2)
        elif self.edge_name == 'bottom half':
            bounds = (0, screen_height/2, screen_width, screen_height/2)
        elif self.edge_name == 'left half':
            bounds = (0, 0, screen_width/2, screen_height)
        elif self.edge_name == 'right half':
            bounds = (screen_width/2, 0, screen_width/2, screen_height)
        else:
            raise Exception(f"Unsupported edge name {self.edge_name}")

        self.desktop.set_window_bounds(self.app_name, bounds)

    @classmethod
    def phrases(cls):
        return [
            "attach {app_name} to {edge_name}"
        ]


class ReadHighlightedText(DesktopAction):
    """Copy Text in an Application"""

    def __init__(self, desktop: DesktopAutomation):
        super().__init__(desktop)

    def run(self):
        try:
            text = self.desktop.capture_highlighted_text()
            print(text)
            return ActionResult(data=text)
        except Exception as e:
            print(e)
        return ActionResult(status="failed")

    @classmethod
    def phrases(cls):
        return [
            "read text"
        ]
