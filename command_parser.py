from typing import List

from actions import (
    ActionBase, 
    SwitchAction, 
    LaunchAction
)


class CommandParser(object):
    def parse(self, cmd: str) -> List[ActionBase]:
        output_actions = []
        if cmd.startswith('switch to'):
            app_name = ' '.join(cmd.split(' ')[2:])
            output_actions.append(SwitchAction(app_name))
        elif cmd.startswith('launch ') or cmd.startswith('open '):
            app_name = ' '.join(cmd.split(' ')[1:])
            output_actions.append(LaunchAction(app_name))
        else:
            raise NotImplementedError("No command matched with that!")

        return output_actions
