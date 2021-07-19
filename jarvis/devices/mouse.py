"""Utilities for interacting with mouse"""

import pyautogui

class Mouse():
    def current_position(self) -> list:
        """Return the `x` and `y` coords of the mouse"""
        return pyautogui.position()

    def move_to(self, x, y) -> None:
        """Move mouse to specified `x` and `y` coordinates"""
        pyautogui.moveTo(x, y)

    def click(self, num_clicks=1, button='left'):
        """Click the specified button for the specified number of times.
        
        Valid options for button include `left`, `right` and `middle`."""
        pyautogui.click(clicks=num_clicks, button=button)

    def scroll(self, amount_to_scroll):
        """Scroll mouse for the specified amount"""
        pyautogui.mouse_scroll(amount_to_scroll)
