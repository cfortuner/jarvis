from gui_automation.gui_automation import GUIAutomation
from .base import ActionBase


class SwitchAction(ActionBase):
    DISTANCE_THRESHOLD = 2

    def __init__(self, app_name):
        self.app_name = app_name
    
    def run(self, gui: GUIAutomation):
        windows = gui.get_list_of_windows()
        distances = map(self._compute_levenshtein_distance, windows)
        min_dist = min(distances)
        if min_dist > self.DISTANCE_THRESHOLD:
            raise Exception(f"Failed to find any app with name {self.app_name}")

        idx = windows.index(min_dist)
        app = windows[idx]
        gui.switch_to_window(app)

    def _compute_levenshtein_distance(self, s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]
