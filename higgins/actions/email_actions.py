from copy import deepcopy
from pprint import PrettyPrinter
import time
from typing import Callable, Dict, List

from higgins.actions import Action, ActionParam, ActionParamSpec, ActionResult
from higgins.actions import contact_actions
from higgins.automation.google import gmail
from higgins.database import tiny
from higgins.automation.email import email_utils
from higgins.nlp.openai import data_question_completions
from higgins.nlp import nlp_utils

pp = PrettyPrinter(indent=2)


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
            action_text=f"Emailing message '{body}' to {self.params['to'].value}"
        )


class SearchEmail(EmailAction):

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
        reply_handler = "SearchEmailReplyHandler" if len(emails) > 0 else None
        return ActionResult(
            action_text=f"Found {len(emails)} emails using query {query}.",
            reply_text=email_utils.get_email_list_preview(emails) if emails else None,
            data=emails,
            reply_handler_classname=reply_handler,
        )


class AnswerEmailQuestion(EmailAction):

    def add_automations(self, automations: Dict) -> Dict:
        super().add_automations(automations)
        if "tokenizer" not in automations:
            automations["tokenizer"] = nlp_utils.get_tokenizer()
        self.tokenizer = automations["tokenizer"]
        return automations

    @classmethod
    def param_specs(cls):
        return {
            "data": ActionParamSpec(name="data", question="What data would you like to parse?", required=True),
            "question": ActionParamSpec(name="question", question="What is your question?", required=True),
        }

    def clarify(self, prompt_fn: Callable) -> List[str]:
        super().clarify(prompt_fn)
        data = self.params["data"].value
        if isinstance(data, list):
            if len(data) == 0:
                self.params["data"].value = None
            elif len(data) == 1:
                self.params["data"].value = data[0]
            else:
                index = None
                while index is None:
                    index = int(prompt_fn(f"{len(data)} emails found. Which one to query? Index number (0-{len(data)-1}): "))
                    if index < 0 or index >= len(data):
                        index = None
                self.params["data"].value = data[index]
        else:
            assert data is None or isinstance(data, dict), "Must be dict or list or None"

    def _ask_model(self, question: str, data: Dict) -> str:
        # OpenAI doesn't support completions with context > 2049 tokens, which includes the completion tokens (100-300)
        MAX_BODY_TOKENS = 1024  # https://beta.openai.com/tokenizer
        data = deepcopy(data)
        data["body"] = data["body"].replace("\n", " ")
        # print("num tokens", nlp_utils.get_num_tokens(data["body"], self.tokenizer))
        data["body"] = nlp_utils.trim_tokens(
            text=data["body"], max_tokens=MAX_BODY_TOKENS, tokenizer=self.tokenizer
        )
        # print("num tokens", nlp_utils.get_num_tokens(data["body"], self.tokenizer))
        answer = data_question_completions.data_question_completion(question=question, data=data)
        return answer

    def run(self):
        data = self.params["data"].value
        question = nlp_utils.normalize_text(self.params["question"].value)
        if not data:  # None or empty list:
            return ActionResult(status="failed", reply_text="No emails matched your search.")

        stats = email_utils.get_body_stats(data["body"])
        # print(f"Email stats: {stats}")

        if "preview" in question or "snippet" in question:
            answer = email_utils.get_email_preview(data, max_lines=10)
        elif question in ["show email", "display email", "show body", "show text"]:
            answer = email_utils.get_email_preview(data)
        elif "summarize" in question:
            answer = "I don't support summarize yet"

        else:
            answer = self._ask_model(question, data)

        return ActionResult(
            reply_text=answer,
            data=self.params["data"].value,
            reply_handler_classname="SearchEmailReplyHandler"
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
        elif unit == "hour":
            query["after"] = int(time.time()) - int(num) * 3600
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
