import pyautogui


class GUIAutomation():
    """Base class for all functionality related to
    automating GUI interactions across different platforms"""
    
    # Standard device automation functions that should
    # work on all OS and Desktop environments
    def mouse_current_position(self) -> list:
        """Return the `x` and `y` coords of the mouse"""
        return pyautogui.position()

    def mouse_move_to(self, x, y) -> None:
        """Move mouse to specified `x` and `y` coordinates"""
        pyautogui.moveTo(x, y)

    def mouse_click(self, num_clicks=1, button='left'):
        """Click the specified button for the specified number of times.
        
        Valid options for button include `left`, `right` and `middle`."""
        pyautogui.click(clicks=num_clicks, button=button)

    def mouse_scroll(self, amount_to_scroll):
        """Scroll mouse for the specified amount"""
        pyautogui.mouse_scroll(amount_to_scroll)

    def keyboard_type(self, text):
        """Type the text in the active window"""
        pyautogui.typewrite(text)

    def keyboard_shortcut(self, keys: list):
        """Simulate pressing specified keyboard shortcut (all pressed together)
        on the currently active window.

        `keys` are specified as a list of keys including modifiers like ctrl, alt, etc.,
        """
        pyautogui.hotkey(keys)

    def get_screensize(self) -> list:
        """Return the screen size in pixels (width, height)"""
        return pyautogui.size()

    # Standard OS interaction functions that should work on
    # all OS and Desktop environments
    def screenshot(self) -> None:
        """Take a screenshot of the entire desktop environment"""
        # TODO(hari): Save this to standard location
        pyautogui.screenshot()

    # Abstract methods that should be implemented for
    # each desktop environment separately
    def get_list_of_windows(self) -> list:
        """Return the name of the currently open windows"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def get_active_window(self) -> str:
        """Return the name of currently active window"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def switch_to_window(self, app_name: str):
        """Switch to the window of the specific app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def get_window_bounds(self, app_name) -> list:
        """Return the (x, y, width, height) bounds of the window for the app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def set_window_bounds(self, app_name, bounds: list) -> None:
        """Set the (x, y, width, height) bounds of the window for the app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def open_application(self, app_name: str):
        """Launch an application with the name specified by app_name while
        also doing some mapping between common application names. For ex.,
        browser should mean default browser application."""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def register_hotkey(self, keys, callback):
        """Register a global hotkey that triggers the callback whenever
        it is pressed"""
        raise NotImplementedError("Needs to be overriden by the derived class")
