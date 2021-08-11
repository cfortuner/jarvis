from dataclasses import dataclass
from typing import Any, Dict

from jarvis.actions import ActionBase, ActionResult


@dataclass
class ExecutedAction:
    """State of an executed action."""
    name: str
    class_path: str
    params: Dict[str, Any]
    transcript: str
    result: ActionResult

    @classmethod
    def from_action(
        cls, action: ActionBase, result: ActionResult, transcript: str
    ):
        return cls(
            name=action.name,
            class_path=action.class_path,
            params=action.params,
            transcript=transcript,
            result=result,
        )
