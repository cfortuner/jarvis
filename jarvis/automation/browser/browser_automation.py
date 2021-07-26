from jarvis.automation.desktop import DesktopAutomation


class BrowserAutomation():
    """Base class for all browser automation implementations."""

    def __init__(self, desktop: DesktopAutomation):
        self.desktop = desktop

    def list_tabs(self) -> list:
        raise NotImplementedError("Needs to be overridden by the derived class")

    def switch_tab(self, tab_title: str):
        raise NotImplementedError("Needs to be overridden by the derived class")

    def new_tab(self, url: str):
        raise NotImplementedError("Needs to be overridden by the derived class")
