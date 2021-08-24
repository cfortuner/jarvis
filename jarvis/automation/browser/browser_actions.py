"""Actions for navigating web browsers."""

import sys
import traceback
from typing import List

from selenium.webdriver.common.by import By

from jarvis.actions import ActionBase, ActionResult
from jarvis.devices.keyboard import Keyboard

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
    """Find and select search bar on website.

    NOTE: This is extremely brittle..
    """
    def __init__(self, browser: BrowserAutomation):
        super().__init__(browser)

    def run(self):
        # TODO: Handle non-standard naming, fields, forms, and javascript
        for selector in ['input', 'input[type=text]', 'input[type=search]']:
            try:
                element = self.browser.find_element_on_page(
                    By.CSS_SELECTOR,
                    selector
                )
                if element is not None:
                    # Focus search bar
                    # TODO: Handle buttons, javascript
                    element.click()
                    return ActionResult()
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)

        return ActionResult(status="failed", error="Failed to find search bar")

    @classmethod
    def phrases(cls):
        return []


class SearchWebsiteFor(BrowserAction):
    """Search using the search bar on website.

    NOTE: This is extremely brittle..
    """
    def __init__(self, browser: BrowserAutomation, text: str):
        super().__init__(browser)
        self.text = text

    @property
    def params(self):
        return {"text": self.text}

    def run(self):
        try:
            FindSearchBar(self.browser).run()
            element = self.browser.get_active_element()

            if element is not None:
                element.clear()
                element.send_keys(self.text)
                element.submit()
                return ActionResult()
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        return ActionResult(status="failed", error="Failed to search ")

    @classmethod
    def phrases(cls):
        return [
            "search for {text}",
            "search website for {text}"
            "search current website for {text}"
        ]


class FindOnPage(BrowserAction):
    """Find text on page (CTRL-F).

    TODO: This is sensitive to the active window and element. Sometimes
    this doesn't work unless you click the webpage and make sure another
    button or app is in-focus. Selenium probably has a feature for this.
    """
    def __init__(self, browser: BrowserAutomation, text: str):
        super().__init__(browser)
        self.text = text

    @property
    def params(self):
        return {"text": self.text}

    def run(self):
        keyboard = Keyboard()
        try:
            # TODO: support linux
            keyboard.shortcut(keys=["command", "f"])
            keyboard.type(self.text)
            return ActionResult()
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
        return ActionResult(status="failed", error="Failed to search ")

    @classmethod
    def phrases(cls):
        return [
            "find {text}",
            "find on page {text}",
            "find text {text}",
            "ctrl f {text}",
            "control f {text}",
        ]
