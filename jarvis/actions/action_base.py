
class ActionBase:
    def run(self, **kwargs) -> None:
        raise NotImplementedError("Needs to be implemented by the derived class")

    @property
    def name(self):
        return type(self).__name__

    @classmethod
    def phrases(cls):
        # List of string phrases where variables are encoded using {var_name}.
        # Any variable in the string will be parsed and the value will be fed
        # to the `run` method as input.
        raise NotImplementedError("Needs to be implemented by the derived class")