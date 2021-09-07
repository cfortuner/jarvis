from typing import Dict, List

from higgins.nlp.openai import email_completions, completion_utils

from higgins.intents import IntentParser


class SendEmail(IntentParser):

    @classmethod
    def phrases(cls):
        return ["send-email {text}"]

    def parse(cls, text: str) -> List[Dict]:
        answer = email_completions.send_email_completion(text)
        actions = completion_utils.convert_string_to_action_chain(answer)
        return actions


class SearchEmail(IntentParser):

    @classmethod
    def phrases(cls):
        return ["search-email {text}"]

    def parse(cls, text: str) -> List[Dict]:
        answer = email_completions.search_email_completion(text)
        actions = completion_utils.convert_string_to_action_chain(answer)
        return actions


if __name__ == "__main__":
    print(SendEmail().parse("email mom I'm coming home tonight"))
    print(SearchEmail().parse("get unread emails"))
    print(SearchEmail().parse("get emails sent by Yoon Manivanh"))
