"""Utilities for interacting with keyboard"""

import pyautogui

class Keyboard():
    def type(self, text):
        """Type the text in the active window"""
        pyautogui.typewrite(text)

    def shortcut(self, keys: list):
        """Simulate pressing specified keyboard shortcut (all pressed together)
        on the currently active window.

        `keys` are specified as a list of keys including modifiers like ctrl, alt, etc.,
        """
        pyautogui.hotkey(keys)

