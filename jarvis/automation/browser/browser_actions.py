"""Actions for navigating web browsers."""

from typing import List

from jarvis.actions import ActionBase, ActionResult
from .browser_automation import BrowserAutomation


class BrowserAction(ActionBase):
    """Base class for all Browser actions.

    We expect the BrowserAutomation instance to be instantiated
    and passed around to all the actions.
    """
    def __init__(self, browser: BrowserAutomation):
        super().__init__()
        self.browser = browser

    @classmethod
    def automations(cls) -> List[str]:
        # List of automation instances required to initialize
        return ["browser"]


class OpenBrowser(BrowserAction):
    """Open browser."""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.open(keep_open=True)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "open chrome",
            "open google chrome",
            "open browser",
        ]


class CloseBrowser(BrowserAction):
    """Open browser."""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.close()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "close chrome",
            "close browser",
        ]


class ChangeURL(BrowserAction):
    """Visit new URL in current tab."""
    def __init__(self, browser: BrowserAutomation, url: str):
        super().__init__(browser)
        self.url = url

    @property
    def params(self):
        return {"url": self.url}

    def run(self):
        print(f"ChangeURL to {self.url}")
        if not self.browser.is_open:
            self.browser.open(url=self.url)
        else:
            self.browser.change_url(self.url)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "open {url}",
            "open website {url}",
            "go to {url}",
            "change url to {url}",
            "visit {url}",
        ]


class OpenTab(BrowserAction):
    """Open new tab"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.new_tab()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "open new tab",
            "new tab",
        ]


class CloseTab(BrowserAction):
    """Open new tab"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.close_tab()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "close tab",
            "close current tab",
            "close open tab",
        ]


class ChangeTab(BrowserAction):
    """Open new tab"""
    def __init__(self, browser: BrowserAutomation, tab_name: str):
        super().__init__(browser)
        self.tab_name = tab_name

    @property
    def params(self):
        return {"tab_name": self.tab_name}

    def run(self):
        print(f"ChangeTab to {self.tab_name}")
        status = self.browser.switch_tab(name=self.tab_name)
        if status == "failed":
            msg = f"Unabled to find tab {self.tab_name}."
            return ActionResult(status="failed", error=msg)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "switch to {tab_name} tab",
            "switch to {tab_name}",
        ]


class GoBack(BrowserAction):
    """Go back to last webpage"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.back()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "go back",
            "back",
        ]


class GoForward(BrowserAction):
    """Go back to last webpage"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.forward()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "go forward",
            "forward",
        ]


class RefreshPage(BrowserAction):
    """Go back to last webpage"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        self.browser.refresh()
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "refresh page",
            "refresh",
            "reload",
        ]


class ClickLink(BrowserAction):
    """Go back to last webpage"""
    def __init__(self, browser: BrowserAutomation, link_text: str):
        super().__init__(browser)
        self.link_text = link_text

    @property
    def params(self):
        return {"link_text": self.link_text}

    def run(self):
        # TODO handle error / not found, or multiple found
        status = self.browser.click_link_by_text(self.link_text, fuzzy=True)
        if status == "failed":
            msg = f"Unabled to find element {self.link_text} on the page."
            return ActionResult(status="failed", error=msg)
        return ActionResult()

    @classmethod
    def phrases(cls):
        return [
            "click {link_text} link",
            "click link {link_text}",
            "click {link_text}",
            "click {link_text} button",
        ]


class FindSearchBar(BrowserAction):
    """Go back to last webpage"""
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        # TODO: Implement smart find search box and highlight
        return ActionResult()

    @classmethod
    def phrases(cls):
        # Add keywords?
        return [
            # "search",
            # "search for",
        ]
