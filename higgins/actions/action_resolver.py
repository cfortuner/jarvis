import re
from typing import Tuple


def parse_answer_to_actions(answer: str) -> Tuple[str, str]:
    # HACK: Only supports single parameter Actions
    # TODO: These Regex still capture badly formed strings
    PARAMS_REGEX = r"([a-zA-Z]+)+\s+`(.*)`"
    NO_PARAMS_REGEX = r"([a-zA-Z]+)"
    print(f"Parsing answer: {answer}")
    cmds = answer.split(" -> ")
    print(f"Commands: {cmds}")
    actions = []
    for cmd in cmds:
        cmd = cmd.strip()
        match_with_params = re.match(PARAMS_REGEX, cmd)
        if match_with_params and len(match_with_params.groups()) == 2:
            print("found match with params")
            class_name, param = match_with_params.groups()
            actions.append((class_name, param))
            continue

        match_no_params = re.match(NO_PARAMS_REGEX, cmd)
        if match_no_params and len(match_no_params.groups()) == 1:
            print("found match with no params")
            class_name = match_no_params.group(0)
            actions.append((class_name, None))
        else:
            raise Exception(
                f"Unabled to parse command: {cmd}, from answer: {answer}"
            )
    return actions


def find_action_phrases(self, dir_name: str) -> dict:
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