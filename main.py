import sys

from PIL import Image, ImageDraw, ImageColor

from speech_app import SpeechApp

# Has to be imported after SpeechApp
# otherwise it results in segfault
import pystray

APP_NAME = "Jarvis"

def create_icon():
    # Generate an image and draw a pattern
    image = Image.new('RGB', (24, 24), ImageColor.getrgb("blue"))
    return image

def on_show(icon, item):
    print("Running")
    if SpeechApp.get_running_app() is not None:
        SpeechApp.get_running_app().show_window()
    else:
        speech_app = SpeechApp()
        speech_app.run()

def on_quit(icon, item):
    print("Quitting")
    icon.stop()
    sys.exit()

if __name__ == '__main__':
    taskbar_icon = pystray.Icon(
        APP_NAME,
        create_icon(),
        menu=pystray.Menu(
            pystray.MenuItem("Show", on_show),
            pystray.MenuItem("Quit", on_quit)))
    taskbar_icon.icon = create_icon()
    taskbar_icon.run()
