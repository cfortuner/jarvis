import pytest

from jarvis.actions import load_action_class_by_name
from jarvis.automation.desktop import create_desktop_automation


@pytest.fixture(scope="function")
def desktop():
    desktop = create_desktop_automation()
    yield desktop


def test_switch_action_serdes(desktop):
    dct = {
        "name": "SwitchAction",
        "class": "jarvis.automation.desktop.desktop_actions.SwitchAction",
        "params": {"app_name": "Chrome", "desktop": None}
    }
    cls = load_action_class_by_name(dct["class"])
