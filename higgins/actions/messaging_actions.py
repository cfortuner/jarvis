from typing import Callable, Dict, List

from jarvis.actions import ActionResult

from higgins.actions import Action, ActionParamSpec
from higgins.database import tiny
from higgins.personal import contacts


class MessagingAction(Action):

    def __init__(self, params: Dict = None, db=None):
        super().__init__(params)
        self.db = db

    def add_automations(self, automations: Dict) -> Dict:
        if "db" not in automations:
            automations["db"] = tiny.load_database()
        self.db = automations["db"]
        return automations


class SendMessage(MessagingAction):

    def __init__(self, params: Dict = None, db=None, contact_info=None):
        super().__init__(params, db)
        self.contact_info = contact_info

    @classmethod
    def param_specs(cls):
        return {
            "to": ActionParamSpec(name="to", question="Who would you like to message?", required=True),
            "body": ActionParamSpec(name="body", question="What would you like to say?", required=True),
            "application": ActionParamSpec(name="application", question="Which application should we use to send?", required=True),
        }

    def clarify(self, prompt_fn: Callable) -> List[str]:
        super().clarify(prompt_fn)
        name = self.params["to"].value.strip()
        possible_alias = None
        contact_info = None
        while contact_info is None:
            users = contacts.find_contact(self.db, name)
            if len(users) == 1:
                contact_info = contacts.Contact(**users[0])
            elif len(users) > 1:
                name = prompt_fn(f"Found {len(users)} contacts named {name}. Who do you mean by {name}?")
            else:
                possible_alias = name
                name = prompt_fn(f"No contacts found for {name}. Who do you mean by {name}?")

        if possible_alias is not None:
            add_alias = prompt_fn(
                f"Is '{possible_alias}' an alias for '{contact_info.name}'?"
            )
            if add_alias.strip().lower() in ["yes", "y"]:
                contact_info.alias = possible_alias.strip()
                contacts.update_contact(self.db, contact_info)

        self.contact_info = contact_info

    def run(self):
        body = self.params["body"].value
        application = self.params["application"].value
        print("Contact", self.contact_info)
        return ActionResult(
            data=f"Sending message '{body}' to {self.contact_info.name} using {application}",
        )
