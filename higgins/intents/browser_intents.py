from typing import Dict, List

from jarvis.nlp.openai import browser_completions, completion_utils

from higgins.intents import IntentParser


class NavigateWeb(IntentParser):

    @classmethod
    def phrases(cls):
        return ["web-nav {text}"]

    def parse(self, text: str) -> List[Dict]:
        answer = browser_completions.web_navigation_completion(text)
        actions = completion_utils.convert_answer_to_action_chain(answer)
        return actions


class OpenWebsite(IntentParser):

    @classmethod
    def phrases(cls):
        return ["open-website {text}"]

    @classmethod
    def parse(cls, text: str) -> List[Dict]:
        answer = browser_completions.open_website_completion(text)
        actions = completion_utils.convert_answer_to_action_chain(answer)
        return actions


class SearchOnWebsite(IntentParser):

    @classmethod
    def phrases(cls):
        return ["search-website {text}"]

    def parse(self, text: str) -> List[Dict]:
        raise NotImplementedError


if __name__ == "__main__":
    print(NavigateWeb().parse("login to coinbase"))
    print(OpenWebsite().parse("goto amazon.com"))
