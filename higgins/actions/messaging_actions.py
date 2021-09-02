from typing import Dict, List

from jarvis.actions import ActionResult
from jarvis.nlp.openai import completions

from higgins.actions import Action, ActionParamSpec


class MessagingAction(Action):

    def add_automations(self, automations: Dict) -> Dict:
        # self.desktop = automations["desktop"]
        return automations


class SendMessage(MessagingAction):

    @classmethod
    def phrases(cls):
        return ["send-msg {text}"]

    @classmethod
    def param_specs(cls):
        return {
            "to": ActionParamSpec(name="to", question="Who would you like to message?", required=True),
            "body": ActionParamSpec(name="body", question="What would you like to say?", required=True),
            "application": ActionParamSpec(name="application", question="Which application should we use to send?", required=True),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        # text: message mom I'm coming home tonight
        # answer: `SendMessage` PARAMS to=>mom ### body=>I'm coming home tonight ### application=>???
        # intent: {'action': 'SendMessage', 'params': {'to': 'mom', 'body': "I'm coming home tonight", 'application': '???'}}
        # TODO: Validate parameters and method names are valid. Perhaps tell GPT about them in the prompt.
        answer = completions.send_message_completion(text)
        intent = completions.convert_answer_to_intent(answer)
        return intent

    def run(self):
        body = self.params["body"].value
        return ActionResult(
            data=f"Sending message '{body}' to {self.params['to'].value} using {self.params['application'].value}",
            speak=False
        )


if __name__ == "__main__":
    intent = SendMessage.parse_intent("message mom I'm coming home tonight")
    print(intent)
