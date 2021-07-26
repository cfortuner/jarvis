# https://stackoverflow.com/questions/8344776/can-selenium-interact-with-an-existing-browser-session

import warnings

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver


# This webdriver can directly attach to an existing session.
class AttachableWebDriver(WebDriver):
    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, session_id=None):
        """
        Create a new driver that will issue commands using the wire protocol.

        :Args:
         - command_executor - Either a string representing URL of the remote server or a custom
             remote_connection.RemoteConnection object. Defaults to 'http://127.0.0.1:4444/wd/hub'.
         - desired_capabilities - A dictionary of capabilities to request when
             starting the browser session. Required parameter.
         - browser_profile - A selenium.webdriver.firefox.firefox_profile.FirefoxProfile object.
             Only used if Firefox is requested. Optional.
         - proxy - A selenium.webdriver.common.proxy.Proxy object. The browser session will
             be started with given proxy settings, if possible. Optional.
         - keep_alive - Whether to configure remote_connection.RemoteConnection to use
             HTTP keep-alive. Defaults to False.
         - file_detector - Pass custom file detector object during instantiation. If None,
             then default LocalFileDetector() will be used.
        """
        if desired_capabilities is None:
            raise WebDriverException("Desired Capabilities can't be None")
        if not isinstance(desired_capabilities, dict):
            raise WebDriverException("Desired Capabilities must be a dictionary")
        if proxy is not None:
            warnings.warn("Please use FirefoxOptions to set proxy",
                          DeprecationWarning)
            proxy.add_to_capabilities(desired_capabilities)
        self.command_executor = command_executor
        if type(self.command_executor) is bytes or isinstance(self.command_executor, str):
            self.command_executor = RemoteConnection(command_executor, keep_alive=keep_alive)

        self.command_executor._commands['GET_SESSION'] = ('GET', '/session/$sessionId')  # added

        self._is_remote = True
        self.session_id = session_id  # added
        self.capabilities = {}
        self.error_handler = ErrorHandler()
        self.start_client()
        if browser_profile is not None:
            warnings.warn("Please use FirefoxOptions to set browser profile",
                          DeprecationWarning)

        if session_id:
            self.connect_to_session(desired_capabilities)  # added
        else:
            self.start_session(desired_capabilities, browser_profile)

        self._switch_to = SwitchTo(self)
        self._mobile = Mobile(self)
        self.file_detector = file_detector or LocalFileDetector()

        self.w3c = True  # added hardcoded

    def connect_to_session(self, desired_capabilities):
        response = self.execute('GET_SESSION', {
            'desiredCapabilities': desired_capabilities,
            'sessionId': self.session_id,
        })
        # self.session_id = response['sessionId']
        self.capabilities = response['value']







if use_existing_session:
    browser = AttachableWebDriver(command_executor=('http://%s:4444/wd/hub' % ip),
                                  desired_capabilities=(DesiredCapabilities.CHROME),
                                  session_id=session_id)
    self.logger.info("Using existing browser with session id {}".format(session_id))
else:
    browser = AttachableWebDriver(command_executor=('http://%s:4444/wd/hub' % ip),
                                  desired_capabilities=(DesiredCapabilities.INTERNETEXPLORER))
    self.logger.info('New session_id  : {}'.format(browser.session_id))





def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, options=Options())
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver


def test_attach_to_session2():
    driver = new_driver()
    executor_url = driver.command_executor._url
    session_id = driver.session_id
    driver.get("http://tarunlalwani.com")

    driver2 = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver2.session_id = session_id
    print(driver2.current_url)
    import pdb; pdb.set_trace()