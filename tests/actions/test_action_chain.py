import logging

import pytest

from jarvis.actions.action_chain import ActionChain
from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser import create_browser_automation


@pytest.fixture
def chain_dict():
    return {
        "name": "Amazon shopping cart",
        "phrases": ["Amazon shopping cart", "shopping cart"],
        "steps": [
            {
                "action_classname": "jarvis.automation.browser.browser_actions.OpenBrowser",
                "action_params": {}
            },
            {
                "action_classname": "jarvis.automation.browser.browser_actions.ChangeURL",
                "action_params": {"url": "amazon.com"}
            },
            {
                "action_classname": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "action_params": {"app_name": "Code"}
            },
        ]
    }


@pytest.fixture
def desktop():
    desktop = create_desktop_automation()
    yield desktop


@pytest.fixture
def browser(desktop):
    browser = create_browser_automation(desktop)
    yield browser
    browser.close()


def test_action_chain_serdes(chain_dict):
    chain = ActionChain.from_dict(chain_dict)
    assert chain.to_dict() == chain_dict


def test_action_chain_run(desktop, browser, chain_dict):
    chain = ActionChain.from_dict(chain_dict)
    chain.add_automations(desktop, browser)
    chain.run()
