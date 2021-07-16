"""TODO: develop a global registration mechanism for Actions."""

from .gui_automation import GUIAutomation

import sys


def create_gui_automation() -> GUIAutomation:
    """Creates an instance of automation corresponding to the
    OS on which the current app is running on"""
    if 'darwin' in sys.platform.lower():
        from .mac_automation import MacAutomation
        return MacAutomation()
    elif 'linux' in sys.platform.lower():
        from .linux_automation import LinuxAutomation
        return LinuxAutomation()
    else:
        raise NotImplementedError(f"{sys.platform} is not currently supported")
