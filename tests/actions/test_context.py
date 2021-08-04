import pytest

from jarvis.automation.desktop import create_desktop_automation
from jarvis.actions.context import Context


@pytest.fixture(scope="function")
def desktop():
    return create_desktop_automation()


@pytest.fixture(scope="function")
def context(desktop):
    return Context(desktop=desktop)


def test_context(context):
    print(context.active_window)
    print(context.available_windows)
    print(context.last_action)
    print(context.last_utterance)
