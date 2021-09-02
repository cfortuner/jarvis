from typing import Dict, List

from jarvis.actions import ActionResult
from jarvis.nlp.openai import completions

from higgins.actions import Action, ActionParamSpec


class BrowserAction(Action):

    def add_automations(self, automations: Dict) -> Dict:
        # self.browser = automations["browser"]
        # self.desktop = automations["desktop"]
        return automations


class WebNavigation(BrowserAction):

    @classmethod
    def phrases(cls):
        return ["web-nav {text}"]

    @classmethod
    def param_specs(cls):
        return {}

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        answer = completions.web_navigation_completion(text)
        intent = completions.convert_answer_to_intent(answer)
        return intent

    def run(self):
        return ActionResult(data="Running website navigation")


class OpenWebsite(BrowserAction):

    @classmethod
    def phrases(cls):
        return ["open-website {text}"]

    @classmethod
    def param_specs(cls):
        return {
            "website": ActionParamSpec(name="website", question="What is the URL?", required=True),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        answer = completions.open_website_completion(text)
        intent = completions.convert_answer_to_intent(answer)
        return intent

    def run(self):
        return ActionResult(
            data=f"Opening website {self.params['website'].value}"
        )


class ClickLink(BrowserAction):

    @classmethod
    def phrases(cls):
        # This means it's not directly callable
        return []

    @classmethod
    def param_specs(cls):
        return {
            "link_text": ActionParamSpec(name="link_text", question="Which link should we click on?", required=True),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        # This means it can only be called by others
        raise NotImplementedError

    def run(self):
        return ActionResult(
            data=f"Clicking link '{self.params['link_text'].value}'"
        )


class SearchOnWebsite(BrowserAction):

    @classmethod
    def phrases(cls):
        # This means it's not directly callable
        return []

    @classmethod
    def param_specs(cls):
        return {
            "text": ActionParamSpec(name="text", question="What should we search for?", required=True),
            "filter": ActionParamSpec(name="filter", question="Would you like to apply any filters?", required=False),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        # This means it can only be called by others
        raise NotImplementedError

    def run(self):
        text = self.params['text'].value
        filter = self.params['filter'].value
        return ActionResult(
            data=f"Searching for '{text}' with filter '{filter}'"
        )


class SignOut(BrowserAction):

    @classmethod
    def phrases(cls):
        # This means it's not directly callable
        return []

    @classmethod
    def param_specs(cls):
        return {
            "website": ActionParamSpec(name="website", question="Which website should we sign out of?", required=False),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        # This means it can only be called by others
        raise NotImplementedError

    def run(self):
        if self.params['website'].is_missing():
            self.params['website'].value = "[CURRENT_URL]"

        return ActionResult(
            data=f"Logging out of {self.params['website'].value}"
        )


class LogIn(BrowserAction):

    @classmethod
    def phrases(cls):
        # This means it's not directly callable
        return []

    @classmethod
    def param_specs(cls):
        return {
            "website": ActionParamSpec(name="website", question="Which website should we log into?", required=False),
            "username": ActionParamSpec(name="username", question="What is your username?", required=True),
            "password": ActionParamSpec(name="password", question="What is your password?", required=True),
        }

    @classmethod
    def parse_intent(cls, text: str) -> List[Dict]:
        # This means it can only be called by others
        raise NotImplementedError

    def run(self):
        if self.params['website'].is_missing():
            self.params['website'].value = "[CURRENT_URL]"
        username = self.params['username'].value
        password = "*" * len(self.params['password'].value)
        return ActionResult(
            data=f"Logging into {self.params['website'].value} with username: {username} and password: {password}"
        )


if __name__ == "__main__":
    print(OpenWebsite.parse_intent("open google"))
    print(OpenWebsite.parse_intent("go to yahoo.com"))
    print(OpenWebsite.parse_intent("open the Walmart homepage"))
    print(OpenWebsite.parse_intent("visit the website"))
    print(WebNavigation.parse_intent("login to coinbase"))
