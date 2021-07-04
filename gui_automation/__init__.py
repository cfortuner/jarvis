import sys

from .gui_automation import GUIAutomation


def create_automation_instance():
    """Creates an instance of automation corresponding to the
    OS on which the current app is running on"""
    if 'darwin' in sys.platform.lower():
        from .mac_automation import MacAutomation
        return MacAutomation()
    else:
        raise NotImplementedError(f"{sys.platform} is not currently supported")
