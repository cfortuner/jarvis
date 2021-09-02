import re
from typing import Dict

from higgins import const


def extract_params_from_string(param_string) -> Dict:
    # to:"mom" body:"I Love her" application:None
    # out: {"to": "mom", "body":"I love here", "application": None}
    params = param_string.strip().split("###")
    out = {}
    for param in params:
        argument, value = param.strip().split("=>")
        out[argument.strip()] = value.strip()
    return out


def convert_answer_to_action_chain(answer: str) -> Dict:
    # answer: `SendMessage` to:"mom" body:"I Love her" application:None <<END>>
    if const.DEBUG_MODE:
        print(f"Answer: {answer}")

    PARAMS_REGEX = r"`([a-zA-Z]+)`\sPARAMS\s(.*)"
    NO_PARAMS_REGEX = r"`([a-zA-Z]+)`"
    # print(f"Parsing answer: {answer}")
    cmds = answer.split(" -> ")
    actions = []
    for cmd in cmds:
        cmd = cmd.strip()
        match_with_params = re.match(PARAMS_REGEX, cmd)
        if match_with_params and len(match_with_params.groups()) == 2:
            class_name, param_string = match_with_params.groups()
            actions.append({
                "action": class_name,
                "params": extract_params_from_string(param_string)
            })
            continue

        match_no_params = re.match(NO_PARAMS_REGEX, cmd)
        if match_no_params and len(match_no_params.groups()) == 1:
            class_name = match_no_params.group(0)
            actions.append({"action": class_name, "params": None})
        else:
            raise Exception(
                f"Unabled to parse command: {cmd}, from answer: {answer}"
            )
    if const.DEBUG_MODE:
        print(f"Actions: {actions}")
    return actions
