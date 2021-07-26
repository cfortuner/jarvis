"""Selenium examples

Install: https://www.selenium.dev/documentation/en/selenium_installation
Requires installing the web drivers separately (on MacOS you also have to grant permissions to web driver)

Run `python scratch/selenium_example.py`

Interesting tool to research: https://cucumber.io/docs/guides/overview/
https://cucumber.io/docs/guides/overview/#what-is-gherkin (for defining functions with natural language)
"""
import pdb

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver

from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser.selenium_automation import SeleniumAutomation
from jarvis.automation.browser import selenium_automation as sel


def enter_selenium_debugger():
    desktop = create_desktop_automation()
    browser = sel.SeleniumAutomation(desktop)
    browser.open(url="http://amazon.com", keep_open=True)
    pdb.set_trace()


if __name__ == "__main__":
    enter_selenium_debugger()
