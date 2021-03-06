import pytest

from jarvis.actions.action_chain import ActionChain
from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser import create_browser_automation


@pytest.fixture
def chain_dict():
    return {
        "name": "amazon shopping cart",
        "phrases": ["amazon shopping cart", "shopping cart"],
        "steps": [
            {
                "class_path": "jarvis.automation.browser.browser_actions.OpenBrowser",
                "params": {}
            },
            {
                "class_path": "jarvis.automation.browser.browser_actions.ChangeURL",
                "params": {"url": "amazon.com"}
            },
            {
                "class_path": "jarvis.automation.desktop.desktop_actions.SwitchAction",
                "params": {"app_name": "Code"}
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
