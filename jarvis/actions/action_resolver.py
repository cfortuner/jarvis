import os
import re

import logging
from typing import List, Tuple

from jarvis.actions import ActionBase
from jarvis.actions.context import Context
from jarvis.automation.browser import create_browser_automation
from jarvis.automation.desktop import create_desktop_automation
from jarvis.nlp import nlp_utils


class PhraseMatcher:
    def __init__(self, phrase, conjunctive=False):
        super()

        self._phrase = phrase
        self._matcher = self._convert_to_regex(phrase)
        self._conjunctive = conjunctive

    def match(self, cmd) -> Tuple[bool, dict]:
        """Returns a tuple of (success, matched_params_dict)"""
        m = self._matcher.match(cmd)
        if m is None: return (False, None)

        return (True, m.groupdict())

    def is_conjunctive(self):
        return self._conjunctive

    def _convert_to_regex(self, phrase):
        # TODO(hari): Support and handle different types
        # of variables here. For now everything is assumed
        # as a string.
        regexp = phrase.replace('{', '(?P<').replace('}', '>.+)')
        # logging.info(phrase)
        # logging.info(regexp)
        return re.compile(regexp)


class ActionResolver:
    """The "Brain" which routes commands to actions.

    Inputs include the transcribed command, current application state (e.g. open windows,
    previous command), and the library of supported actions. These inputs are combined to
    determine which Action to perform.
    """

    # Some files are platform specific like mac_automation.py.
    # To avoid loading them, we only load files that contain actions
    # which are determined by looking for file with this suffix.
    ACTIONS_FILE_SUFFIX = "_actions.py"

    def __init__(self):
        super()

        self.desktop = create_desktop_automation()
        self.context = Context(desktop=self.desktop)
        self._browser = None

        # Map between phrase string and the action type
        self._phrase_map = {}
        # Support multiple actions by using conjunctive and.
        # This will not have any action mapped to it.

        # TODO(bfortuner): Support multiple actions
        # Right now this makes the resolve logic complex and breaks
        # when a user says the word "and" as part of a link name
        # self._phrase_map[PhraseMatcher("{a} and {b}", True)] = None

        self._phrase_map.update(self._find_action_phrases("jarvis/automation"))
        logging.info(f"Found {len(self._phrase_map)} phrases to match against")

    @property
    def browser(self):
        if self._browser is None:
            self._browser = create_browser_automation(self.desktop)
        return self._browser

    def parse(self, cmd: str) -> List[ActionBase]:
        """Converts user command string in list of Actions.

        NOTE: Right now we only support 1 action per command, but we
        return a list of matching actions to attempt ordered by the
        most relevant as determined by context (e.g. active window).
        """

        logging.info(f"CommandParser Input:  {cmd}")
        cmd = nlp_utils.normalize_text(cmd)
        logging.info(f"Command after cleaning: {cmd}")

        matching_actions = self._find_matching_actions(cmd)

            # TODO: Support conjunctives
            # if phrase_matcher.is_conjunctive():
            #     # For conjunctive phrases, param name doesn't
            #     # matter
            #     for _, param_value in params.items():
            #         output_actions.extend(
            #             self.parse(param_value, self.desktop, self.browser)
            #         )

        if len(matching_actions) == 0:
            logging.info("No command matched with that!")
            raise NotImplementedError("No command matched with that!")

        # Use Context to disambiguate commands
        actions = self._sort_actions_by_relevance(matching_actions)

        # Add required automation instances
        actions = self._add_automation_instances(actions)

        # Initialize the actions
        action_instances = []
        for action_cls, action_params in actions:
            action_instances.append(action_cls(**action_params))
        return action_instances

    def _sort_actions_by_relevance(self, matching_actions):
        # If the active window supports the action, push it to the top
        ordered_actions = []
        active_window_actions = []
        for i, (action_type, _) in enumerate(matching_actions):
            if self.context.active_window in action_type.app_names():
                active_window_actions.append(matching_actions[i])
            else:
                ordered_actions.append(matching_actions[i])
        return active_window_actions + ordered_actions

    def _add_automation_instances(self, actions):
        for action_cls, action_params in actions:
            if "browser" in action_cls.automations():
                action_params["browser"] = self.browser
            if "desktop" in action_cls.automations():
                action_params["desktop"] = self.desktop
        return actions

    def _find_matching_actions(self, phrase: str):
        # Returns list of (action type, action params)
        actions = []
        for phrase_matcher, action_type in self._phrase_map.items():
            status, params = phrase_matcher.match(phrase)
            if status:
                actions.append((action_type, params))
        return actions

    def _find_action_phrases(self, dir_name: str) -> dict:
        """Loop through sub directories and load all the packages
        and return them as a dictionary"""
        phrase_map = {}
        file_list = os.listdir(os.path.join(os.getcwd(), dir_name))
        for file_name in file_list:
            full_path = os.path.join(os.path.abspath(dir_name), file_name)
            rel_path = os.path.join(dir_name, file_name)
            if os.path.isdir(full_path) and \
                os.path.exists(os.path.join(full_path, "__init__.py")):
                phrase_map.update(self._find_action_phrases(rel_path))
            elif full_path.endswith(self.ACTIONS_FILE_SUFFIX) and file_name != "__init__.py":
                module_name = os.path.splitext(file_name)[0]
                logging.info(module_name)
                module = __import__(
                    f"{dir_name.replace(os.sep, '.')}.{module_name}", 
                    fromlist = ["*"])
                for _, t_value in module.__dict__.items():
                    try:
                        if issubclass(t_value, ActionBase):
                            for phrase in t_value.phrases():
                                # TODO(hari): Validate the phrases to make sure
                                # they don't use invalid param names and types
                                phrase_matcher = PhraseMatcher(phrase)
                                phrase_map[phrase_matcher] = t_value
                    except:
                        # Some members of the module aren't classes. Ignore them.
                        pass
        
        return phrase_map
