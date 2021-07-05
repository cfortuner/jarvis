from gui_automation import GUIAutomation


class ActionBase(object):
    def run(gui: GUIAutomation):
        raise NotImplementedError("Needs to be implemented by the derived class")

    @property
    def name(self):
        return type(self).__name__
