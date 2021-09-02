from typing import Dict, List

from jarvis.nlp.openai import messaging_completions, completion_utils

from higgins.intents import IntentParser


class MessagingIntent(IntentParser):

    @classmethod
    def phrases(cls):
        return ["send-msg {text}"]

    def parse(cls, text: str) -> List[Dict]:
        # text: message mom I'm coming home tonight
        # answer: `SendMessage` PARAMS to=>mom ### body=>I'm coming home tonight ### application=>???
        # intent: {'action': 'SendMessage', 'params': {'to': 'mom', 'body': "I'm coming home tonight", 'application': '???'}}
        # TODO: Validate parameters and method names are valid. Perhaps tell GPT about them in the prompt.
        answer = messaging_completions.send_message_completion(text)
        actions = completion_utils.convert_answer_to_action_chain(answer)
        return actions


if __name__ == "__main__":
    print(MessagingIntent().parse("message mom I'm coming home tonight"))
