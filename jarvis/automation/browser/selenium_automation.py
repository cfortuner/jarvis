"""Selenium implementation of browser automation.

Install: https://www.selenium.dev/documentation/en/selenium_installation
Requires installing the web drivers separately (on MacOS you also have to grant permissions to web driver)

Docs: https://selenium-python.readthedocs.io/navigating.html
TODO: Selenium treats tabs/windows the same. Need way to differentiate. 
TODO: Simplify last_window storage. Perhaps just always fall back to window[0] if > 0 windows? What happens if parent window is closed?
TODO: Simplify list_tabs by returning all windows and tabs??

Selenium chrome://version (default selenium mode -- creates new profile path every time) 
-------------------------
User Agent	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36
Command Line	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --allow-pre-commit-input --disable-background-networking --disable-client-side-phishing-detection --disable-default-apps --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-repost --disable-sync --enable-automation --enable-blink-features=ShadowDOMV0 --enable-logging --log-level=0 --no-first-run --no-service-autorun --password-store=basic --remote-debugging-port=0 --test-type=webdriver --use-mock-keychain --user-data-dir=/var/folders/sh/nmjlw4rs5nq_xlggl3d20_9w0000gq/T/.com.google.Chrome.CkQeMn --flag-switches-begin --flag-switches-end data:,
Executable Path	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
Profile Path	/private/var/folders/sh/nmjlw4rs5nq_xlggl3d20_9w0000gq/T/.com.google.Chrome.CkQeMn/Default

Selenium chrome://version (with userdata) 
-------------------------
User Agent	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36
Command Line	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --allow-pre-commit-input --disable-background-networking --disable-client-side-phishing-detection --disable-default-apps --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-repost --disable-sync --enable-automation --enable-blink-features=ShadowDOMV0 --enable-logging --log-level=0 --no-first-run --no-service-autorun --password-store=basic --remote-debugging-port=0 --test-type=webdriver --use-mock-keychain --user-data-dir=./JarvisProfile/Default --flag-switches-begin --flag-switches-end --origin-trial-disabled-features=SecurePaymentConfirmation
Executable Path	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
Profile Path	/Users/brendan.fortuner/Library/Application Support/Google/Chrome/Profile 1

My personal account (logged in)
--------------------------
User Agent	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36
Command Line	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --flag-switches-begin --flag-switches-end --origin-trial-disabled-features=SecurePaymentConfirmation
Executable Path	/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
Profile Path	/Users/brendan.fortuner/Library/Application Support/Google/Chrome/Profile 1

NOTE: Selenium disables bunch of stuff (for security reasons likely). We could always do it manually... but then we need access to raw passwords
Cookies are way easier

driver.find_element_by_id(“email”).send_keys(‘fakeemail@gmail.com’)
driver.find_element_by_id(“pass”).send_keys(“fakepassword1”)
"""

import logging
import os
from pathlib import Path
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from jarvis.automation.auto_utils import speed_limit
from jarvis.automation.desktop import DesktopAutomation

from .browser_automation import BrowserAutomation

# May not be needed if we have access to the user profile data
DEFAULT_URL = "http://www.google.com"


def get_user_data_dir():
    """Load/find the Chrome profile of the user so we can leverage cookies/auth.

    FIXME: This is a very fragile function. Requires hand-tuning.
    Thoughts
    * Loading the user profile data takes a few seconds to launch the browser instance
    * Some websites like Gmail block Selenium and webdrivers
        https://security.googleblog.com/2019/04/better-protection-against-man-in-middle.html
    * Selenium runs with a lot of extra flags that disable stuff. We copy the user profile data, but not their cookies/passwords, etc.
    * Users can log in manually to a website. Once they do, the cookies are stored in the JarvisProfile and reused between sessions.

    List of locations: https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/user_data_dir.md
    Show your current user data: chrome://version/
    You can't use the same directory as an existing chrome session. You need to copy the directory.

    https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/user_data_dir.md#Mac-OS-X
    https://sites.google.com/a/chromium.org/chromedriver/capabilities
    https://stackoverflow.com/questions/49270109/how-to-open-a-chrome-profile-through-python/49280195#49280195
    https://stackoverflow.com/questions/52394408/how-to-use-chrome-profile-in-selenium-webdriver-python-3/52399027#52399027
    https://stackoverflow.com/questions/50635087/how-to-open-a-chrome-profile-through-user-data-dir-argument-of-selenium/50637211#50637211

    https://stackoverflow.com/questions/52394408/how-to-use-chrome-profile-in-selenium-webdriver-python-3
    https://stackoverflow.com/questions/49270109/how-to-open-a-chrome-profile-through-python
    """
    USER_HOME = str(Path.home())
    MACOS_CHROME_ROOT = "Library/Application Support/Google/Chrome/"
    USER_PROFILE = "Profile 1"
    JARVIS_PROFILE = "JarvisProfile"

    user_path = os.path.join(USER_HOME, MACOS_CHROME_ROOT, USER_PROFILE)
    if not os.path.exists(user_path):
        msg = f"Chrome user profile {user_path} doesn't exist. Need to input manually."
        raise Exception(msg)

    jarvis_path = os.path.join("./", JARVIS_PROFILE)

    shutil.copytree(user_path, jarvis_path, dirs_exist_ok=True)

    return jarvis_path


def get_chrome_options(keep_open: bool = True, user_data_dir: str = None):
    """Configure some default options."""
    options = Options()
    options.add_experimental_option("detach", keep_open)
    if user_data_dir is not None:
        print(f"Adding user data dir {user_data_dir}")
        options.add_argument(f"--user-data-dir={user_data_dir}")
    return options


def open_new_driver(keep_open: bool = True) -> webdriver.Chrome:
    """Open new web driver instance.

    Must call drive.quit() manually to avoid dangling processes.

    Args:
        website_url: URL of the website to open.
        keep_open: Optional; Leave window open after tasks are complete.

    Returns:
        Chromium Web Driver.
    """
    # I'm not sure how much help this gives us..
    user_data_dir = None  # get_user_data_dir()
    chrome_options = get_chrome_options(keep_open, user_data_dir)
    return webdriver.Chrome(chrome_options=chrome_options)


def get_tabs_and_windows(driver):
    # The handles are just string identifiers with no useful information
    # we need to keep a secondary mapping of metadata
    print(driver.window_handles)
    for w in driver.window_handles:
        print(w, type(w))


class SeleniumAutomation(BrowserAutomation):
    """Controls the browser using Selenium library."""
    def __init__(self, desktop: DesktopAutomation):
        super().__init__(desktop)
        # We might want multiple drivers? Or would that be multiple SeleniumAutomation?
        # Drivers are also closed/killed, so how does that work?
        self._driver = None
        self._windows = []
        self._last_window_handle = None

    @property
    def driver(self):
        return self._driver

    @property
    def last_window(self):
        _, win = self._get_window_by_handle(self.driver.current_window_handle)
        return win

    @property
    def current_window(self):
        _, win = self._get_window_by_handle(self.driver.current_window_handle)
        return win

    def open_driver(self, keep_open: bool = None):
        return open_new_driver(keep_open=keep_open)

    def open(self, url: str = DEFAULT_URL, keep_open: bool = False):
        """Initialize driver and open url."""
        if self._driver is not None:
            raise ValueError("Cannot call open() twice before calling close()")
        self._driver = open_new_driver(keep_open=keep_open)
        self.driver.get(url)
        self._register_window(
            handle=self.driver.current_window_handle,
            name=self.driver.title,
            url=url,
            # Debatable whether this is tab or window
            # Need a better mechanism for distinguishing
            type="tab",
        )
        self._last_window_handle = self.driver.current_window_handle

    def close(self):
        """Close driver and clear metadata."""
        if self._driver is None:
            logging.warning("Browser is already closed.")
        else:
            self._close_driver()
            self._windows = []
            self._last_window_handle = None

    def _close_driver(self):
        self.driver.quit()
        self._driver = None

    def _set_last_window(self, handle: str):
        self._last_window_handle = handle

    def _get_last_window(self):
        _, win = self._get_window_by_handle(self._last_window_handle)
        return win

    def _register_window(self, handle: str, name: str, url: str, type: str):
        self._windows.append(
            dict(handle=handle, name=name, url=url, type=type)
        )

    def _deregister_window(self, handle: str):
        idx, win = self._get_window_by_handle(handle)
        if idx is not None:
            self._windows.pop(idx)
        else:
            print(f"Window {win['handle']} - {win['name']} not exist.")

    def _get_window_by_handle(self, handle: str):
        for idx, win in enumerate(self._windows):
            if win["handle"] == handle:
                return idx, win
        return None, None

    def _get_window_by_name(self, name: str):
        for idx, win in enumerate(self._windows):
            if win["name"] == name:
                return idx, win
        return None, None

    def list_tabs(self):
        """Return tab names in current window.

        FIXME: Returns all tabs across all windows
        TODO: Normalize tab names to lowercase

        Alternative is to query in real-time, but the user sees the tabs change:

        ...: cur_handle = browser.driver.current_window_handle
        ...: websites = []
        ...: for handle in browser.driver.window_handles:
        ...:     browser.driver.switch_to.window(handle)
        ...:     websites.append((browser.driver.current_url, browser.driver.title))

        """
        return [win["name"] for win in self._windows if win["type"] == "tab"]

    @speed_limit()
    def new_tab(self, url: str = DEFAULT_URL):
        """Open new tab in current window.

        There seems to be a complicated history for this function: 
        https://stackoverflow.com/questions/28431765/open-web-in-new-tab-selenium-python
        """
        self._set_last_window(self.driver.current_window_handle)
        self.driver.switch_to.new_window("tab")
        self.driver.get(url)
        self._register_window(
            handle=self.driver.current_window_handle,
            name=self.driver.title,
            url=url,
            type="tab",
        )

    @speed_limit()
    def new_window(self, url: str = DEFAULT_URL):
        """Open new browser window."""
        self._set_last_window(self.driver.current_window_handle)
        self.driver.switch_to.new_window("window")
        self.driver.get(url)
        self._register_window(
            handle=self.driver.current_window_handle,
            name=self.driver.title,
            url=url,
            type="window",
        )

    def switch_to_last_window(self):
        # TODO: Handle edge cases
        _, win = self._get_window_by_handle(self.driver.current_window_handle)
        self.driver.switch_to.window(self._get_last_window()["handle"])
        self._set_last_window(win["handle"])

    def _close_tab_or_window(self, handle: str):
        """Close the tab/window (Must switch to another tab/window manually).

        Add method for closing by window handle, name, id, etc.

        NOTE: Might need to keep track of open windows or check whether session is invalid
        to avoid InvalidSessionIdException: Message: invalid session id
        """
        self._deregister_window(handle)
        self.driver.close()
        # Kill the driver if there are no remaining tabs/windows        
        if len(self._windows) > 0:
            self.driver.switch_to.window(self._get_last_window()["handle"])
        else:
            self._close_driver()

    @speed_limit()
    def close_tab(self, name: str = None):
        """Close tab by name, or active tab if no name provided."""
        if name is not None:
            _, win = self._get_window_by_name(name)
            handle = win["handle"]
        else:
            handle = self.driver.current_window_handle
        self._close_tab_or_window(handle)

    @speed_limit()
    def close_window(self, name: str = None):
        """Close current window (including all tabs).

        TODO: Handle closing multiple tabs in window (loop?)
        """
        if name is not None:
            _, win = self._get_window_by_name(name)
            handle = win["handle"]
        else:
            handle = self.driver.current_window_handle
        self._close_tab_or_window(handle)

    @speed_limit()
    def switch_tab(self, name: str = None, handle: str = None):
        """Switch to tab by name or handle.

        TODO: Selenium treats tabs/windows the same. Find way to differentiate.

        https://www.toolsqa.com/selenium-webdriver/window-handle-in-selenium/

        browser.driver.title <-- HTML Title of current tab
        browser.driver.window_handles
        browser.driver.switch_to.window(window_handle)
        browser.driver.switch_to.new_window("tab")

        element = driver.switch_to.active_element
        alert = driver.switch_to.alert
        driver.switch_to.default_content()
        driver.switch_to.frame('frame_name')
        driver.switch_to.frame(1)
        driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
        driver.switch_to.parent_frame()
        driver.switch_to.window('main')
        """
        if handle is None:
            if name is None:
                raise Exception("Must provide either `name` or `handle`")
            _, win = self._get_window_by_name(name)
            handle = win["handle"]
        self._last_window_handle = self.driver.current_window_handle
        self.driver.switch_to.window(handle)

    @speed_limit()
    def switch_window(self, name: str = None, handle: str = None):
        """Switch to window by name or handle.

        TODO: Selenium treats tabs/windows the same. Find way to differentiate.
        """
        if handle is None:
            assert name is not None, "Must provide either name or handle"
            _, win = self._get_window_by_name(name)
            handle = win["handle"]
        self._last_window_handle = self.driver.current_window_handle
        self.driver.switch_to.window(handle)

    @speed_limit()
    def change_url(self, url: str, wait: float = 0):
        """Change url in current window/tab."""
        self.driver.get(url)
        _ = WebDriverWait(self.driver, wait)

        _, win = self._get_window_by_handle(self.driver.current_window_handle)
        win["name"] = self.driver.title
        win["url"] = self.driver.current_url

    @speed_limit()
    def back(self):
        self.driver.back()

    @speed_limit()
    def forward(self):
        self.driver.forward()

    @speed_limit()
    def refresh(self):
        self.driver.refresh()

    @speed_limit()
    def click_link_by_text(self, link_text: str):
        """Click a link on page by name.

        TODO: Handle updating window metadata once new page is opened

        Args:
            link_text (str): Human-readable text on the link.
        """
        # Also, PARTIAL_LINK_TEXT, or return all the matching elements
        self.driver.find_element(by=By.LINK_TEXT, value=link_text).click()
        _, win = self._get_window_by_handle(self.driver.current_window_handle)
        win["url"]


# Experimental

def connect_to_existing_browser_instance():
    """Connect to existing browser opened manually by the user.

    Options:
    1. Don't. Only provide automation for browsers opened with Selenium.
    2. Launch Chrome in remote debugger mode. Override existing chrome.app path or provide a symlink.
    3. Fork/patch the open-source Selenium code (e.g. webdriver.py file).
    4. Use another library like Puppeteer https://medium.com/@jaredpotter1/connecting-puppeteer-to-existing-chrome-window-8a10828149e0

    Simplest path forward is to always launch Chrome in debug mode, and help the user set that up.
    Does this also work for Firefox? Microsoft Edge?
    How do we handle user cookies and sharing auth?
    """


def connect_to_existing_selenium_browser_instance():
    """Connect to an existing Selenium browser (opened by Selenium).

    Use case: User-in-the-loop automation where the user takes over (e.g. to sign in) and
    then Selenium takes the wheels again after they log in.

    We can keep the driver object alive after they takeover, then enter a while loop which checks a Queue
    for instructions. It keeps polling until the driver is killed manually by the user (some way to detect
    this or worst case try/except), or a new action is requested by the user. So we don't need to attach to
    a remote session...

    How do we map the active window to the selenium process which created it? So if the user says go to X, we need
    to know which selenium session they're running. Perhaps we can just assume they only have 1 running session..

    A) This might require launching Chrome in remote debugger mode:
        https://stackoverflow.com/questions/51563287/how-to-make-chrome-always-launch-with-remote-debugging-port-flag
        https://abodeqa.com/how-to-connect-selenium-to-existing-chrome-browser/
        https://cosmocode.io/how-to-connect-selenium-to-an-existing-browser-that-was-opened-manually/
        options.setExperimentalOption("debuggerAddress", "127.0.0.1:9222")
        Create a new chrome shortcut on your desktop and add --remote-debugging-port=9222 to the target.

    B) Or reconnecting to an existing session_id (this returns a WebDriver.Remote which doesn't have the same APIs
        But this might actually work)
        https://tarunlalwani.com/post/reusing-existing-browser-session-selenium/
        https://github.com/axelPalmerin/personal/commit/fabddb38a39f378aa113b0cb8d33391d5f91dca5

    It also might not be required if we cache the driver instance the user is playing with.
    Cleanup could be tricky though..
    """
    # https://stackoverflow.com/questions/8344776/can-selenium-interact-with-an-existing-browser-session/51145789#51145789
    # driver.service.service_url

