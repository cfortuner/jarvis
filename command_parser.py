from typing import List

from actions import ActionBase, SwitchAction


class CommandParser(object):
    def parse(cmd: str) -> List[ActionBase]:
        output_actions = []
        if cmd.startswith('switch to'):
            app_name = ' '.join(cmd.split(' ')[2:])
            output_actions.append(SwitchAction(app_name))

        return output_actions
