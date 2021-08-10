from jarvis.actions import action_utils
from jarvis.automation.browser.browser_actions import ChangeTab


def test_action_to_dict():
    dct = action_utils.action_to_dict(
        action_cls=ChangeTab,
        action_params={"tab_name": "amazon.com", "browser": None}
    )
    assert dct == {
        "class": "jarvis.automation.browser.browser_actions.ChangeTab",
        "params": {"tab_name": "amazon.com"}
    }


def test_dict_to_action():
    dct = {
        "class": "jarvis.automation.browser.browser_actions.ChangeTab",
        "params": {"tab_name": "amazon.com"}
    }
    out = action_utils.dict_to_action(dct)

    assert out == {
        "class": ChangeTab,
        "params": {"tab_name": "amazon.com"}
    }
