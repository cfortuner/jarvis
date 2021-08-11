import json
import os
from typing import Dict, List, Union

from jarvis.const import ACTION_CHAIN_PATH
from jarvis.actions.action_chain import ActionChain, ActionChainStep
from jarvis.actions.action_history import ExecutedAction


def create_action_chain(
    name: str,
    phrases: List[str],
    executed_actions: List[Union[ExecutedAction, Dict]],
    action_chain_path: str = ACTION_CHAIN_PATH,
):
    """Convert sequence of executed actions into an ActionChain."""
    steps = []
    for action in executed_actions:
        if isinstance(action, Dict):
            action = ExecutedAction(**action)
        steps.append(
            ActionChainStep(action.class_path, action.params)
        )
    return ActionChain(
        name=name,
        phrases=phrases,
        steps=steps
    )


def register_action_chain(
    name: str,
    phrases: List[str],
    executed_actions: List[Union[ExecutedAction, Dict]],
    action_chain_path: str,
):
    """Convert sequence of executed actions into an ActionChain and save to file."""
    chain = create_action_chain(name, phrases, executed_actions)

    chains = {"chains": []}
    if os.path.exists(action_chain_path):
        print(f"Founding existing action chain cache. Loading: {action_chain_path}")
        chains = json.load(open(action_chain_path))

    chains["chains"].append(chain.to_dict())

    json.dump(chains, open(action_chain_path, "w"), indent=4)

    return chain


def load_action_chains_from_file(fpath: str):
    chains = []
    if os.path.exists(fpath):
        print(f"Founding existing action chain cache. Loading: {fpath}")
        with open(fpath) as f:
            chains = json.load(f)["chains"]
    return chains
