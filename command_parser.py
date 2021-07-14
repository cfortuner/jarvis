import logging
from typing import List

from actions import (
    ActionBase, 
    SwitchAction, 
    LaunchAction
)

# TODO: Move text_parser out of listener into a shared module
from command_listener import text_parser

class CommandParser(object):
    def parse(self, cmd: str) -> List[ActionBase]:
        logging.info(f"CommandParser Input:  {cmd}")
        cmd = text_parser.normalize_text(cmd)
        logging.info(f"Command after cleaning: {cmd}")

        output_actions = []
        if cmd.startswith('switch to'):
            app_name = ' '.join(cmd.split(' ')[2:])
            output_actions.append(SwitchAction(app_name))
        elif cmd.startswith('launch ') or cmd.startswith('open '):
            app_name = ' '.join(cmd.split(' ')[1:])
            output_actions.append(LaunchAction(app_name))
        else:
            logging.info("No command matched with that!")
            raise NotImplementedError("No command matched with that!")

        return output_actions
