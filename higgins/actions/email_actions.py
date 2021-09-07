from typing import Callable, Dict, List

from jarvis.actions import ActionResult

from higgins.actions import Action, ActionParam, ActionParamSpec
from higgins.actions import contact_actions
from higgins.automation.google import gmail
from higgins.database import tiny


class EmailAction(Action):

    def __init__(self, params: Dict = None, db=None):
        super().__init__(params)
        self.db = db

    def add_automations(self, automations: Dict) -> Dict:
        if "db" not in automations:
            automations["db"] = tiny.load_database()
        self.db = automations["db"]
        return automations


class SendEmail(EmailAction):

    def __init__(self, params: Dict = None, db=None, contact_info=None):
        super().__init__(params, db)
        self.contact_info = contact_info

    @classmethod
    def param_specs(cls):
        return {
            "to": ActionParamSpec(name="to", question="Who would you like to email?", required=True),
            "body": ActionParamSpec(name="body", question="What should the email body contain?", required=True),
            "subject": ActionParamSpec(name="subject", question="What is the subject?"),
        }

    def clarify(self, prompt_fn: Callable) -> List[str]:
        super().clarify(prompt_fn)
        name = self.params["to"].value.strip()
        if not contact_actions.is_valid_email(name):
            contact_info = contact_actions.clarify_contact_info(
                name=name, db=self.db, prompt_fn=prompt_fn
            )
            self.params["to"].value = contact_info.email

    def run(self):
        body = self.params["body"].value
        return ActionResult(
            data=f"Emailing message '{body}' to {self.params['to'].value}"
        )


class SearchEmail(EmailAction):

    def __init__(self, params: Dict = None, db=None, contact_info=None):
        super().__init__(params, db)
        self.contact_info = contact_info

    @classmethod
    def param_specs(cls):
        return {
            "to": ActionParamSpec(name="to", question=""),
            "from": ActionParamSpec(name="from", question=""),
            "subject": ActionParamSpec(name="subject", question=""),
            "unread": ActionParamSpec(name="unread", question=""),
            "labels": ActionParamSpec(name="labels", question=""),
            "exact_phrase": ActionParamSpec(name="exact_phrase", question=""),
            "newer_than": ActionParamSpec(name="newer_than", question=""),
        }

    def clarify(self, prompt_fn: Callable) -> List[str]:
        super().clarify(prompt_fn)
        recipient = self.params["to"].value
        if recipient and not contact_actions.is_valid_email(recipient):
            recipient_info = contact_actions.clarify_contact_info(
                name=recipient, db=self.db, prompt_fn=prompt_fn, loop_until_found=False,
            )
            if recipient_info is not None:
                self.params["to"].value = recipient_info.email

        sender = self.params["from"].value
        if sender and not contact_actions.is_valid_email(sender):
            sender_info = contact_actions.clarify_contact_info(
                name=sender, db=self.db, prompt_fn=prompt_fn, loop_until_found=False,
            )
            if sender_info is not None:
                self.params["from"].value = sender_info.email

    def run(self):
        query = action_params_to_query(self.params)
        emails = gmail.search_emails(query_dicts=[query])
        return ActionResult(
            data=f"Found {len(emails)} emails using query {query}.",
        )


def action_params_to_query(params: Dict[str, ActionParam]) -> List[Dict]:
    query = {}
    if params["to"].value is not None:
        query["recipient"] = params["to"].value
    if params["from"].value is not None:
        query["sender"] = params["from"].value
    if params["newer_than"].value is not None:
        num, unit = params["newer_than"].value.split()
        # TODO: Replace these handlers with more training data for GPT
        if unit[-1] == "s":
            unit = unit[:-1]
        if unit == "week":
            query["newer_than"] = (int(num)*7, "day")
        elif unit not in ["day", "month", "year"]:
            raise Exception(f"`newer_than` unit '{unit}' not supported.")
        else:
            query["newer_than"] = (int(num), unit)
    if params["unread"].value is not None:
        query["unread"] = True
    if params["subject"].value is not None:
        query["subject"] = params["subject"].value
    if params["exact_phrase"].value is not None:
        query["exact_phrase"] = params["exact_phrase"].value
    if params["labels"].value is not None:
        labels = params["labels"].value
        if " AND " in labels:
            labels = labels.split(" AND ")
        elif " OR " in labels:
            labels = [[label] for label in labels.split(" OR ")]
        query["labels"] = labels

    return query
