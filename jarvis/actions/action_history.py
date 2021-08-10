from dataclasses import dataclass
from typing import List

from jarvis.actions import ActionResult


@dataclass
class ExecutedAction:
    """State of an executed action."""
    action_classname: str
    action_params: dict
    transcript: str
    result: ActionResult


@dataclass
class ActionHistory:
    """History of executed actions.

    Has method to convert to JSON.
    Sorted chronologically.
    """
    actions: List[ExecutedAction]
