import logging
import subprocess
from typing import List


class ShellAutomation:
    def run_cmd(self, command: List[str]):
        result = subprocess.run(command, stdout=subprocess.PIPE)
        print(result)
        logging.info(result.stdout)
        return result
