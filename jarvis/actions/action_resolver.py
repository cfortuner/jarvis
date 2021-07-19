from jarvis.automation.desktop.desktop_automation import DesktopAutomation
import logging
from typing import List

from jarvis.actions import ActionBase
from jarvis.automation.browser import browser_actions, BrowserAutomation
from jarvis.automation.desktop import desktop_actions, DesktopAutomation
from jarvis.nlp import nlp_utils


class ActionResolver:
    """The "Brain" which routes commands to actions.
    
    Inputs include the transcribed command, current application state (e.g. open windows,
    previous command), and the library of supported actions. These inputs are combined to
    determine which Action to perform.
    """
    def parse(self, cmd: str, desktop: DesktopAutomation, browser: BrowserAutomation) -> List[ActionBase]:
        """Converts user command string in list of Actions.
        
        In the future this can also take the application state, command history, and inputs
        from other devices like the Camera for gaze estimation.
        """
        logging.info(f"CommandParser Input:  {cmd}")
        cmd = nlp_utils.normalize_text(cmd)
        logging.info(f"Command after cleaning: {cmd}")

        output_actions = []
        if cmd.startswith('switch to'):
            app_name = ' '.join(cmd.split(' ')[2:])
            output_actions.append(desktop_actions.SwitchAction(desktop, app_name))
        elif cmd.startswith('launch ') or cmd.startswith('open '):
            app_name = ' '.join(cmd.split(' ')[1:])
            output_actions.append(desktop_actions.LaunchAction(desktop, app_name))
        else:
            logging.info("No command matched with that!")
            raise NotImplementedError("No command matched with that!")

        return output_actions
