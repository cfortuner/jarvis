from dataclasses import dataclass
from typing import List


@dataclass
class ActionResult:
    """Stores the status and error of an executed action."""
    status: str = "succeeded"  # succeeded, failed
    error: str = None  # exception message


class ActionBase:
    def run(self, **kwargs) -> ActionResult:
        raise NotImplementedError("Needs to be implemented by the derived class")

    @property
    def name(self):
        return type(self).__name__

    @property
    def params(self) -> dict:
        # TODO: Automate this
        # Return the __init__ args except for automations
        return {}

    @property
    def class_path(self):
        cls = type(self)
        return ".".join([cls.__module__, cls.__name__])

    @classmethod
    def phrases(cls):
        # List of string phrases where variables are encoded using {var_name}.
        # Any variable in the string will be parsed and the value will be fed
        # to the `run` method as input.
        raise NotImplementedError("Needs to be implemented by the derived class")

    @classmethod
    def app_names(cls) -> List[str]:
        # List of app names this action can operate on
        # If empty, the action can operate on all apps or desktops
        # In combination with active window, this can be used to disambiguate
        # user commands when the same phrase is supported by multiple actions.
        return []

    @classmethod
    def automations(cls) -> List[str]:
        # List of automation instances required to initialize
        return []
