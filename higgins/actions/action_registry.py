import logging
import os
from typing import Dict, List

from jarvis.nlp.phrase_matcher import PhraseMatcher

from higgins.actions import Action
from higgins import const


def load_action_phrase_map_from_modules(dir_name: str) -> dict:
    """Loop through sub directories and load all the packages
    and return them as a dictionary"""
    phrase_map = {}
    file_list = os.listdir(os.path.join(os.getcwd(), dir_name))
    for file_name in file_list:
        full_path = os.path.join(os.path.abspath(dir_name), file_name)
        rel_path = os.path.join(dir_name, file_name)
        if os.path.isdir(full_path) and \
            os.path.exists(os.path.join(full_path, "__init__.py")):
            phrase_map.update(load_action_phrase_map_from_modules(rel_path))
        elif full_path.endswith(const.ACTION_FILE_SUFFIX) and file_name != "__init__.py":
            module_name = os.path.splitext(file_name)[0]
            logging.info(module_name)
            module = __import__(
                f"{dir_name.replace(os.sep, '.')}.{module_name}",
                fromlist = ["*"])
            for _, t_value in module.__dict__.items():
                try:
                    if issubclass(t_value, Action):
                        for phrase in t_value.phrases():
                            # TODO(hari): Validate the phrases to make sure
                            # they don't use invalid param names and types
                            phrase_matcher = PhraseMatcher(phrase)
                            phrase_map[phrase_matcher] = t_value
                except:
                    # Some members of the module aren't classes. Ignore them.
                    pass
    return phrase_map


def find_matching_actions(
    phrase: str, phrase_map: Dict[str, PhraseMatcher]
) -> List[Action]:
    actions = []
    for phrase_matcher, action_type in phrase_map.items():
        status, params = phrase_matcher.match(phrase)
        if status:
            actions.append((action_type, params))
    return actions


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
        elif full_path.endswith(const.ACTION_FILE_SUFFIX) and file_name != "__init__.py":
            module_name = os.path.splitext(file_name)[0]
            module = __import__(
                f"{dir_name.replace(os.sep, '.')}.{module_name}", fromlist = ["*"])
            for _, t_value in module.__dict__.items():
                try:
                    if issubclass(t_value, Action):
                        class_name = t_value.__name__
                        class_map[class_name] = t_value
                except:
                    # Some members of the module aren't classes. Ignore them.
                    pass
    return class_map


def load_action_class_by_name(action_name, action_class_map):
    if action_name not in action_class_map:
        raise Exception(f"Action: {action_name} not found!")
    action_class = action_class_map[action_name]
    return action_class
