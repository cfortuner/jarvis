import pytest

from jarvis.actions.action_resolver import ActionResolver
from jarvis.automation.desktop import create_desktop_automation
from jarvis.automation.browser import selenium_automation as sel


URLS = {
    "amazon": "http://www.amazon.com",
    "facebook": "http://www.facebook.com",
    "google": "http://www.amazon.com",
    "github": "http://www.github.com",
    "wikipedia": "http://www.wikipedia.org",
}


@pytest.fixture(scope="function")
def desktop():
    return create_desktop_automation()


@pytest.fixture(scope="function")
def browser(desktop):
    browser = sel.SeleniumAutomation(desktop)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def resolver():
    return ActionResolver()


def test_find_action_phrases(resolver):
    phrases = resolver._find_action_phrases("jarvis/automation")
    print(phrases)
    assert len(phrases) > 0


@pytest.mark.parametrize(
    "phrase, expected_action, expected_params",
    [
        ("switch to chrome", "SwitchAction", {"app_name": "chrome"}),
        ("open chrome", "LaunchAction", {"app_name": "chrome"}),
    ]
)
def test_find_matching_actions(
    resolver, phrase, expected_action, expected_params
):
    actions = resolver._find_matching_actions(phrase)
    print(actions)

    assert len(actions) > 0

    action_cls, params = actions[0]
    assert action_cls.__name__ == expected_action
    assert params == expected_params


def test_get_all_menuitems_for_window(desktop):
    name = "terminal"
    menuitems = desktop.get_all_menuitems_for_window(name)
    print(name)
    for name, items in menuitems.items():
        print(f"{name} ---------------------")
        print(items)


@pytest.mark.parametrize(
    "phrase, expected_action, expected_app_name",
    [
        ("switch to terminal", "SwitchAction", "terminal"),
        ("open terminal", "LaunchAction", "terminal"),
    ]
)
def test_sort_actions_by_relevance(
    resolver, phrase, expected_action, expected_app_name
):
    actions = resolver._find_matching_actions(phrase)
    print(actions)

    actions = resolver._sort_actions_by_relevance(actions)
    for action_cls, action_params in actions:
        print(action_cls, action_params)

    # print(actions)
    # assert action_cls.__name__ == expected_action
    # assert action_params["app_name"] == expected_app_name
