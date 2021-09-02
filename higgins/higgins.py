import sys
import traceback

from higgins.actions import ActionResult, action_registry
from higgins import const


def execute_command(cmd_class, cmd_params, automations, class_map, prompt_func=input, print_func=None):
    intents = cmd_class.parse_intent(cmd_params["text"])

    for intent in intents:
        action_class = class_map[intent["action"]]
        action = action_class.from_dict(intent["params"])

        if const.DEBUG_MODE:
            print(action)

        for param in action.params.values():
            if param.is_missing():
                if param.spec.required:
                    param.value = prompt_func(f"{param.spec.question} ")
                else:
                    param.value = None

        automations = action.add_automations(automations)

        try:
            action_result = action.run()
            if action_result.data is not None and print_func is not None:
                print_func(action_result.data)
        except Exception as e:
            msg = "Uh oh! Failed to act on this: {}".format(str(e))
            traceback.print_exc(file=sys.stdout)
            print(msg)
            return ActionResult(status="failed", error=msg), automations

    return ActionResult(), automations


class Higgins:
    def __init__(self, prompt_func=input, print_func=print):
        self.prompt_func = prompt_func
        self.print_func = print_func
        self.phrase_map = action_registry.load_action_phrase_map_from_modules("higgins/actions")
        self.action_class_map = action_registry.load_action_classes_from_modules("higgins/actions")
        self.automations = {}

    def parse(self, text: str):
        # Regex search for command prefix (e.g. send-msg, web-nav, open-website)
        commands = action_registry.find_matching_actions(
            phrase=text, phrase_map=self.phrase_map
        )
        if len(commands) > 0:
            cmd_class, cmd_params = commands[0]  # We assume 1 matching command

            action_result, self.automations = execute_command(
                cmd_class, cmd_params, self.automations, self.action_class_map, self.prompt_func, self.print_func
            )
        else:
            return None
        return action_result


if __name__ == "__main__":
    H = Higgins()
    print(H.phrase_map)

    # Messaging
    # H.parse("send-msg text Mom with iMessage I'm coming home tonight")
    # H.parse("send-msg text Mom I'm coming home tonight")

    # Opening websites
    # H.parse("open-website apple.com")
    # H.parse("open-website open the new yorker website")

    # Web Navigation
    H.parse("web-nav search for highlighters on google")
    H.parse("web-nav sign out")
    H.parse("web-nav log out of my amazon account")
    H.parse("web-nav log in to coinbase")
