import pyautogui


class GUIAutomation(object):
    """Base class for all functionality related to
    automating GUI interactions across different platforms"""
    
    # Standard device automation functions that should
    # work on all OS and Desktop environments
    def mouse_current_position() -> list:
        return pyautogui.position()

    def mouse_move_to(x, y) -> None:
        pyautogui.moveTo(x, y)

    def mouse_click(num_clicks=1, button='left'):
        pyautogui.click(clicks=num_clicks, button=button)

    def mouse_scroll(amount_to_scroll):
        pyautogui.mouse_scroll(amount_to_scroll)

    def keyboard_type(text):
        pyautogui.typewrite(text)

    def keyboard_shortcut(keys: list):
        pyautogui.hotkey(keys)

    # Standard OS interaction functions that should work on
    # all OS and Desktop environments
    def screenshot() -> None:
        # TODO(hari): Save this to standard location
        pyautogui.screenshot()

    # Abstract methods that should be implemented for
    # each desktop environment separately
    def get_list_of_windows() -> list:
        pass

    def get_active_window() -> str:
        pass

    def switch_to_window():
        pass

    def get_window_bounds() -> list:
        pass

    def set_window_bounds(bounds) -> None:
        pass
