import sys
import traceback
from typing import Callable, Dict, List, Type

from higgins.nlp.phrase_matcher import PhraseMatcher

from higgins.actions import Action, ActionResult
from higgins.database import tiny
from higgins.utils import class_registry
from higgins import const


def execute_command(
    action_chain: List[Dict],
    automations: Dict,
    action_class_map: Dict[PhraseMatcher, Type[Action]],
    prompt_func: Callable = input,
    print_func: Callable = None,
):
    for step in action_chain:
        try:
            action_class = action_class_map[step["action"]]
            action = action_class.from_dict(step["params"])

            if const.DEBUG_MODE:
                print(action)

            automations = action.add_automations(automations)

            # Ask questions or query db for missing information
            action.clarify(prompt_func)

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
    """Primary entrypoint for app."""
    def __init__(self, intent_resolver, prompt_func=input, print_func=print):
        self.intent_resolver = intent_resolver
        self.prompt_func = prompt_func
        self.print_func = print_func
        self.action_class_map = class_registry.load_classes_from_modules(
            dir_name="higgins/actions",
            file_suffix=const.ACTION_FILE_SUFFIX,
            class_type=Action,
        )
        self.db = tiny.load_database()
        self.automations = {
            "db": self.db
        }

    def parse(self, text: str):
        intent_class, text = self.intent_resolver.resolve(text)
        if intent_class is not None:
            intent_parser = intent_class()
            action_chain = intent_parser.parse(text)
            action_result, self.automations = execute_command(
                action_chain,
                self.automations,
                self.action_class_map,
                self.prompt_func,
                self.print_func,
            )
            return action_result
        return None


if __name__ == "__main__":
    from higgins.intents.intent_resolver import (
        RegexIntentResolver, OpenAIIntentResolver
    )

    examples = [
        # Messaging
        ("send-msg", "ping Liam Fortuner and ask him when his flight lands using WhatsApp"),
        ("send-msg", "message Dad and let him know I'm coming home for the holidays"),
        ("send-msg", "tell colin to grab me toilet paper at the store"),
        ("send-msg", "tell Mom I'm coming home for dinner"),
        ("send-msg", "ping Colin on slack"),
        # WebNav
        ("web-nav", "log in to my spotify account username david123"),
        ("web-nav", "search for apples and oranges on Instacart"),
        ("web-nav", "open etherscan"),
        ("web-nav", "search arxiv for resnet50 paper"),
        ("web-nav", "find airpods on ebay"),
        ("web-nav", "go to Best Sellers on Amazon.com"),
        ("web-nav", "go to circle ci and login with the username bfortuner"),
        ("web-nav", "find Jackie First on facebook"),
        ("web-nav", "open opensea io"),
        ("web-nav", "search for rainbows on google"),
        ("web-nav", "logout"),
        ("web-nav", "sign out"),
        ("web-nav", "login to Walmart.com"),
        ("web-nav", "login to coinbase"),
        # Other
        ("", "wondering what the air quality will be"),
        # ("", "play Stan Getz on Spotify"),
        ("", "turn on the lights"),
        ("", "close all applications"),
        ("", "which app is using the most CPU?)")
    ]

    # H = Higgins(intent_resolver=RegexIntentResolver())
    # print("Regex intent resolver ------")
    # for category, text in examples:
    #     combined = " ".join([category, text])
    #     result = H.parse(combined)
    #     print(combined, result)
    from higgins.datasets import email_datasets
    examples += [
        ("send-email", action["query"]) for action in email_datasets.SEND_EMAIL_DATASET_TEST
    ]
    examples += [
        ("search-email", action["query"]) for action in email_datasets.SEARCH_EMAIL_DATASET_TEST
    ]
    H = Higgins(intent_resolver=OpenAIIntentResolver())
    print("\nOpenAI intent resolver ------")
    for category, text in examples:
        result = H.parse(text)
        data = result.data if result is not None else None
        print(text, result)
