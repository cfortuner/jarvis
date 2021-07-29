import pytest

from jarvis.automation.shell import shell_automation as sa


COMMANDS = [
    ["ls", "-ltrh"]
]


# function is default (called every test. Not reused.)
@pytest.fixture(scope="function")
def shell():
    return sa.ShellAutomation()


def test_run_cmd(shell):
    cmd = ["ls", "-ltr"]
    result = shell.run_cmd(cmd)
    print(result)
    #import pdb; pdb.set_trace()
