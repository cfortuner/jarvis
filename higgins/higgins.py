import sys
import traceback
from typing import Callable, Dict, List, Type

from jarvis.nlp.phrase_matcher import PhraseMatcher

from higgins.actions import Action, ActionResult, action_registry
from higgins.intents import intent_registry
from higgins import const


def execute_command(
    action_chain: List[Dict],
    automations: Dict,
    action_class_map: Dict[PhraseMatcher, Type[Action]],
    prompt_func: Callable = input,
    print_func: Callable = None
):
    for step in action_chain:
        action_class = action_class_map[step["action"]]
        action = action_class.from_dict(step["params"])

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
    """Primary entrypoint for app.

    commands = prefix used for routing to intent parsers (send-msg, web-nav, etc)
        eventually these will be replaces by higher-level intent/classification algorithms
        right now, they're hard-coded to route to the matching intent parser(s)
    intents = routing functions which parse raw text into a sequence of actions (WebNav). Right
        now these are equivalent to commands
    actions = execute user intents (SendMessage, OpenWebsite, LogIn, SignOut) <-- are names globally unique?
    automations = API integrations for executing actions
    """
    def __init__(self, prompt_func=input, print_func=print):
        self.prompt_func = prompt_func
        self.print_func = print_func
        self.intent_parser_class_map = intent_registry.load_intent_phrase_map_from_modules("higgins/intents")
        self.action_class_map = action_registry.load_action_classes_from_modules("higgins/actions")
        self.automations = {}

    def parse(self, text: str):
        # Regex search for command prefix (e.g. send-msg, web-nav, open-website)
        intent_parsers = intent_registry.find_matching_intents(
            phrase=text, phrase_map=self.intent_parser_class_map
        )
        if len(intent_parsers) > 0:
            intent_class, intent_params = intent_parsers[0]  # We assume 1 matching intent parser
            intent_parser = intent_class()
            action_chain = intent_parser.parse(intent_params["text"])
            print("action chain", action_chain)

            action_result, self.automations = execute_command(
                action_chain,
                self.automations,
                self.action_class_map,
                self.prompt_func,
                self.print_func,
            )
        else:
            return None
        return action_result


if __name__ == "__main__":
    H = Higgins()
    print(H.intent_parser_class_map)
    print(H.action_class_map)

    # Messaging
    H.parse("send-msg text Mom with iMessage I'm coming home tonight")
    H.parse("send-msg text Mom I'm coming home tonight")

    # Opening websites
    H.parse("open-website apple.com")
    H.parse("open-website open the new yorker website")

    # Web Navigation
    H.parse("web-nav search for highlighters on google")
    H.parse("web-nav sign out")
    H.parse("web-nav log out of my amazon account")
    H.parse("web-nav log in to coinbase")
