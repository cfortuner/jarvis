from .command_listener import CommandListener
from .command_parser import CommandParser

if __name__ == '__main__':
    parser = CommandParser()
    cmd = CommandListener.listen()
    actions = parser.parse(cmd)
    for a in actions:
        a.run()
