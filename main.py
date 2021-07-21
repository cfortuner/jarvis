import argparse
import os
import sys

from PIL import Image, ImageColor

# Set KIVY_NO_ARGS=1 in your environment or before you import Kivy to
# disable Kivy's argument parser.
os.environ["KIVY_NO_ARGS"] = "1"

from jarvis.app import DesktopApp


APP_NAME = "Jarvis"

def create_icon():
    # Generate an image and draw a pattern
    image = Image.new('RGB', (24, 24), ImageColor.getrgb("blue"))
    return image

def on_show(icon, item):
    print("Running")
    if DesktopApp.get_running_app() is not None:
        DesktopApp.get_running_app().show_window()
    else:
        speech_app = DesktopApp()
        speech_app.run()

def on_quit(icon, item):
    print("Quitting")
    icon.stop()
    sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run jarvis.')
    parser.add_argument('--no-taskbar', action='store_true', help="Disable task bar feature and launch app directly.")

    args = parser.parse_args()

    # The task bar doesn't work well on Mac yet and slows down iteration speed.
    if args.no_taskbar:
        import trio
        trio.run(DesktopApp().root_task)
        #DesktopApp().run()
    else:
        # Has to be imported after DesktopApp
        # otherwise it results in segfault
        import pystray

        taskbar_icon = pystray.Icon(
            APP_NAME,
            create_icon(),
            menu=pystray.Menu(
                pystray.MenuItem("Show", on_show),
                pystray.MenuItem("Quit", on_quit)))
        taskbar_icon.icon = create_icon()
        taskbar_icon.run()
