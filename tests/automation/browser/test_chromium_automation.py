import pytest

from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser import chromium_automation as chrome


URLS = {
    "amazon": "http://www.amazon.com",
    "facebook": "http://www.facebook.com",
    "google": "http://www.amazon.com",
    "github": "http://www.github.com",
    "wikipedia": "http://www.wikipedia.org",
}


@pytest.fixture(scope="function")
def browser():
    desktop = create_desktop_automation()
    browser = chrome.ChromiumAutomation(desktop, "browser")
    yield browser
    # browser.close()


def test_get_menu_items_for_all_tabs(browser):
    windows = browser.desktop.get_list_of_windows()
    print(windows)
    # tabs = browser._get_menuitems_for_all_tabs()
    # print(tabs)


@pytest.mark.skip()
def test_list_tabs(browser):
    browser.open(URLS["wikipedia"])
    name1 = browser.current_window["name"]
    browser.new_tab(URLS["github"])
    name2 = browser.current_window["name"]

    expected = sorted([name1, name2])
    assert sorted(browser.list_tabs()) == expected


@pytest.mark.skip()
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
