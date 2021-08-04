from jarvis.automation.desktop import DesktopAutomation

from .browser_automation import BrowserAutomation


def create_browser_automation(desktop: DesktopAutomation) -> BrowserAutomation:
    from .selenium_automation import SeleniumAutomation
    return SeleniumAutomation(desktop=desktop)
