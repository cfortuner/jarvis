from typing import Dict

from jarvis.actions import ActionResult

from higgins.actions import Action, ActionParamSpec


class MessagingAction(Action):

    def add_automations(self, automations: Dict) -> Dict:
        # self.desktop = automations["desktop"]
        return automations


class SendMessage(MessagingAction):

    @classmethod
    def param_specs(cls):
        return {
            "to": ActionParamSpec(name="to", question="Who would you like to message?", required=True),
            "body": ActionParamSpec(name="body", question="What would you like to say?", required=True),
            "application": ActionParamSpec(name="application", question="Which application should we use to send?", required=True),
        }

    def run(self):
        body = self.params["body"].value
        return ActionResult(
            data=f"Sending message '{body}' to {self.params['to'].value} using {self.params['application'].value}",
        )
