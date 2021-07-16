
class ActionBase:
    def run() -> None:
        raise NotImplementedError("Needs to be implemented by the derived class")

    @property
    def name(self):
        return type(self).__name__
