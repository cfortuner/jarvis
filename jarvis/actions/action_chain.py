from dataclasses import asdict, dataclass
import logging
from typing import List

from jarvis.automation.desktop import DesktopAutomation
from jarvis.automation.browser import BrowserAutomation

from jarvis.actions import ActionResult
from jarvis.actions import action_utils


@dataclass
class ActionChainStep:
    """State of an executed action."""
    action_classname: str
    action_params: dict


class ActionChain:
    """A sequence of actions."""
    def __init__(
        self,
        name: str,
        phrases: List[str],
        steps: List[ActionChainStep],
        no_execute: bool = False,
    ):
        self.name = name
        self.phrases = phrases
        self.steps = steps
        self.no_execute = no_execute
        self._actions = None
        self._desktop = None
        self._browser = None

    def add_automations(
        self, desktop: DesktopAutomation, browser: BrowserAutomation
    ):
        # For simplicity, we assume all action chains require both automations
        self._desktop = desktop
        self._browser = browser

    @property
    def actions(self):
        if self._actions is None:
            self._actions = []
            for step in self.steps:
                action_cls = action_utils.load_action_class_by_name(
                    name=step.action_classname
                )
                action_utils.add_automation_to_action_params(
                    action_cls=action_cls,
                    action_params=step.action_params,
                    desktop=self._desktop,
                    browser=self._browser,
                )
                action = action_cls(**step.action_params)
                self._actions.append(action)
        return self._actions

    def run(self, **kwargs):
        assert self._desktop is not None, "Must call add_automations() before run()"
        for i, action in enumerate(self.actions):
            logging.info(f"Running {self.name}[{i}]: {action.name}")
            if not self.no_execute:
                result = action.run()
                if result.status == "error":
                    return ActionResult(status="failed", error=result.error)
        return ActionResult()

    def app_names(self):
        return []

    @classmethod
    def from_dict(cls, dct):
        return cls(
            name=dct["name"],
            phrases=dct["phrases"],
            steps=[
                ActionChainStep(**kwargs) for kwargs in dct["steps"]
            ]
        )

    def to_dict(self):
        return dict(
            name=self.name,
            phrases=self.phrases,
            steps=[asdict(step) for step in self.steps]
        )
