import pyautogui


class DesktopAutomation():
    """Base class for all functionality related to
    automating Desktop interactions across different platforms"""

    # Standard OS interaction functions that should work on
    # all OS and Desktop environments
    def get_screensize(self) -> list:
        """Return the screen size in pixels (width, height)"""
        return pyautogui.size()

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

    def get_all_menuitems_for_window(self, app_name) -> dict:
        """Return all menu items as a dict with the key being the name of the menu
        
        An example would be:

        {
            "File" : [
                MenuItem("New"),
                MenuItem("Save")
            ],
            "Edit" : [
                MenuItem("Undo"),
                MenuItem("Redo")
            ]
        }
        """
        raise NotImplementedError("Needs to be overriden by the derived class")

    def switch_to_window(self, app_name: str):
        """Switch to the window of the specific app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def get_window_bounds(self, app_name: str) -> list:
        """Return the (x, y, width, height) bounds of the window for the app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def set_window_bounds(self, app_name: str, bounds: list) -> None:
        """Set the (x, y, width, height) bounds of the window for the app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def maximize_window(self, app_name: str):
        """Maximize the main widow of the app"""
        raise NotImplementedError("Needs to be overriden by the derived class")

    def minimize_window(self, app_name: str):
        """Minimize the main widow of the app"""
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
