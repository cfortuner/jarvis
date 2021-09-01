from jarvis.nlp import nlp_utils
import json
import os
from typing import Dict, List, Union

from jarvis.const import ACTION_CHAIN_PATH, ACTION_FILE_SUFFIX
from jarvis.actions import ActionBase, ActionChain, ActionChainStep
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
    name = nlp_utils.normalize_text_naive(name)
    phrases = [nlp_utils.normalize_text_naive(p) for p in phrases]
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


def load_action_classes_from_modules(dir_name: str) -> dict:
    """Loop through sub directories and load all the packages
    and return them as a dictionary"""
    class_map = {}
    file_list = os.listdir(os.path.join(os.getcwd(), dir_name))
    for file_name in file_list:
        full_path = os.path.join(os.path.abspath(dir_name), file_name)
        rel_path = os.path.join(dir_name, file_name)
        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
            class_map.update(load_action_classes_from_modules(rel_path))
        elif full_path.endswith(ACTION_FILE_SUFFIX) and file_name != "__init__.py":
            module_name = os.path.splitext(file_name)[0]
            module = __import__(
                f"{dir_name.replace(os.sep, '.')}.{module_name}", fromlist = ["*"])
            for _, t_value in module.__dict__.items():
                try:
                    if issubclass(t_value, ActionBase):
                        class_name = t_value.__name__
                        class_map[class_name] = t_value
                except:
                    # Some members of the module aren't classes. Ignore them.
                    pass
    return class_map


