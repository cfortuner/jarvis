from typing import Dict, List

from higgins.episode import Episode
from higgins.intents import IntentParser
from higgins.nlp.openai import (
    completion_utils,
    email_completions
)


class SendEmail(IntentParser):

    @classmethod
    def phrases(cls):
        return ["send-email {text}"]

    def parse(cls, text: str, episode: Episode = None) -> List[Dict]:
        answer = email_completions.send_email_completion(text)
        actions = completion_utils.convert_string_to_action_chain(answer)
        return actions


class SearchEmail(IntentParser):

    @classmethod
    def phrases(cls):
        return ["search-email {text}"]

    def parse(cls, text: str, episode: Episode = None) -> List[Dict]:
        answer = email_completions.search_email_completion(text)
        actions = completion_utils.convert_string_to_action_chain(answer)
        return actions


class SearchEmailReplyHandler(IntentParser):

    def parse(cls, text: str, episode: Episode) -> List[Dict]:
        return [
            {
                "action": "AnswerEmailQuestion",
                "params": {
                    "data": episode.action_result.data, "question": text
                }
            }
        ]


if __name__ == "__main__":
    print(SendEmail().parse("email mom I'm coming home tonight"))
    print(SearchEmail().parse("get unread emails"))
    print(SearchEmail().parse("get emails sent by Yoon Manivanh"))
