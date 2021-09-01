from typing import Dict

from jarvis.actions import ActionResult
from jarvis.nlp.openai import completions

from higgins.actions import Action, ActionParamSpec


class BrowserAction(Action):

    def add_automations(self, automations: Dict) -> Dict:
        # self.browser = automations["browser"]
        # self.desktop = automations["desktop"]
        return automations


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
    def parse_intent(cls, text: str) -> Dict:
        answer = completions.open_website_completion(text)
        #print(f"Answer: {answer}")
        intent = completions.convert_answer_to_intent(answer)
        return intent[0]

    def run(self):
        return ActionResult(
            data=f"Opening website {self.params['website'].value}"
        )


if __name__ == "__main__":
    print(OpenWebsite.from_text("open google"))
    print(OpenWebsite.from_text("go to yahoo.com"))
    print(OpenWebsite.from_text("open the Walmart homepage"))
    print(OpenWebsite.from_text("visit the website"))
