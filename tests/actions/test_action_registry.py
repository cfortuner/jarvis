import os

import pytest

from jarvis.actions import action_registry


@pytest.fixture
def actions_dict():
    return {
        "name": "amazon shopping cart",
        "phrases": ["amazon shopping cart"],
        "executed_actions": [
            {
                "name": "OpenBrowser",
                "class_path": "jarvis.automation.browser.browser_actions.OpenBrowser",
                "params": {},
                "transcript": "open browser man.",
                "result": {"status": "succeeded"}
            },
            {
                "name": "ChangeURL",
                "class_path": "jarvis.automation.browser.browser_actions.ChangeURL",
                "params": {"url": "amazon.com"},
                "transcript": "go to amazon.com",
                "result": {"status": "succeeded"}
            },
            {
                "name": "ClickLink",
                "class_path": "jarvis.automation.browser.browser_actions.ClickLink",
                "params": {"link_text": "Cart"},
                "transcript": "click Cart",
                "result": {"status": "succeeded"}
            },
        ]
    }


@pytest.fixture
def chain_dict():
    return {
        "name": "amazon shopping cart",
        "phrases": ["amazon shopping cart"],
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
                "class_path": "jarvis.automation.browser.browser_actions.ClickLink",
                "params": {"link_text": "Cart"},
            },
        ]
    }


def test_create_action_chain(actions_dict, chain_dict):
    out = action_registry.create_action_chain(
        name=actions_dict["name"],
        phrases=actions_dict["phrases"],
        executed_actions=actions_dict["executed_actions"]
    )
    assert out.to_dict() == chain_dict


def test_register_action_chain(tmpdir, actions_dict, chain_dict):
    fpath = os.path.join(str(tmpdir), "actions.json")
    written_chain = action_registry.register_action_chain(
        name=actions_dict["name"],
        phrases=actions_dict["phrases"],
        executed_actions=actions_dict["executed_actions"],
        action_chain_path=fpath
    )
    assert written_chain.to_dict() == chain_dict

    read_chain = action_registry.load_action_chains_from_file(fpath)[0]

    assert read_chain == written_chain.to_dict()


def test_load_action_classes_from_modules():
    modules = action_registry.load_action_classes_from_modules("jarvis/automation")
    print(modules)
