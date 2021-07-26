import pytest

from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser import selenium_automation as sel


URLS = {
    "amazon": "http://www.amazon.com",
    "facebook": "http://www.facebook.com",
    "google": "http://www.amazon.com",
    "github": "http://www.github.com",
    "wikipedia": "http://www.wikipedia.org",
}


@pytest.fixture(scope="function")  # function is default (called every test. Not reused.)
def browser():
    desktop = create_desktop_automation()
    browser = sel.SeleniumAutomation(desktop)
    yield browser
    browser.close()


def test_open_driver(browser):
    driver = browser.open_driver(keep_open=True)
    driver.quit()


def test_open_browser(browser):
    browser.open(URLS["amazon"])
    browser.close()


def test_change_url(browser):
    browser.open()
    browser.change_url(URLS["facebook"])


def test_back_forward_refresh(browser):
    browser.open(URLS["amazon"])
    browser.change_url(URLS["facebook"])
    browser.back()
    browser.refresh()


def test_new_tab(browser):
    browser.open(URLS["google"])
    browser.new_tab(URLS["facebook"])
    browser.close_tab()


def test_new_window(browser):
    browser.open(URLS["google"])
    browser.new_window(URLS["facebook"])
    browser.close_window()


def test_switch_tab(browser):
    browser.open(URLS["google"])
    W1 = browser.current_window

    browser.new_tab(URLS["facebook"])
    W2 = browser.current_window

    # By name
    browser.switch_tab(name=W1["name"])
    assert browser.current_window == W1
    browser.switch_tab(name=W2["name"])
    assert browser.current_window == W2

    # By handle
    browser.switch_tab(handle=W1["handle"])
    assert browser.current_window == W1
    browser.switch_tab(handle=W2["handle"])
    assert browser.current_window == W2


def test_list_tabs(browser):
    browser.open(URLS["wikipedia"])
    name1 = browser.current_window["name"]
    browser.new_tab(URLS["github"])
    name2 = browser.current_window["name"]

    expected = sorted([name1, name2])
    assert sorted(browser.list_tabs()) == expected


def test_click_link_by_text(browser):
    browser.open(URLS["amazon"])
    browser.click_link_by_text("Best Sellers")
    print(browser.current_window)
