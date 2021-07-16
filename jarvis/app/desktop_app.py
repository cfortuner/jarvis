import functools
import logging
import sys
import traceback

import kivy
kivy.require('2.0.0')

from kivy.config import Config

# Size of the Kivy voice recognition window
# shown at the top-right corner of the screen
window_width = 400
window_height = 100

Config.set('graphics', 'borderless', 'true')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '0')
Config.set('graphics', 'width', str(window_width))
Config.set('graphics', 'height', str(window_height))

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from jarvis.actions import ActionResolver
from jarvis.automation.gui import create_gui_automation
from jarvis.nlp.speech2text import BasicTranscriber, GoogleTranscriber


# Used for early-exit during speech recognition
SUPPORTED_COMMANDS = [
    "switch to chrome",
    "switch to code",
    "switch to terminal",
    "open chrome",
    "new tab",
    "close window",
    "scroll down",
]
ShortCutKeys = ['ctrl', 'alt', 'j']


class DesktopApp(App):
    GREETING_TEXT = "What can I do for you?"
    LISTENING_TEXT = "Continuous listening mode. Say 'exit' to close"

    def build(self):
        # This seems to first create regular sized window
        # and then update it to the specified size. It's
        # better to override size using Config.set methods
        # at the top of the file.
        # Window.borderless = True
        # Window.size = (100, 50)
        # self.clistener = BasicTranscriber()
        self.resolver = ActionResolver()
        self.clistener = GoogleTranscriber()
        self.gui_automation = create_gui_automation()

        logging.info("Getting screen size")
        screensize = self.gui_automation.get_screensize()
        Window.left = screensize[0] - window_width - 15
        Window.top = 40
        # Window.clearcolor = (1, 1, 1, 0.5)

        label = Label(
            text=self.GREETING_TEXT,
            size_hint=(0.8, .5),
            color=(1, 1, 1, 1),
            font_size="14sp",
            halign="center",
            font_name='Roboto-Regular',
        )
        talk_btn = Button(
            background_normal="images/microphone.png",
            on_press=functools.partial(self.record, label),
            size_hint=(0.2, 1.0),
            # pos_hint={"x": .5, "y": .5},
            font_size="50sp",
        )
        close_btn = Button(
            text="Close",
            on_press=self.close_window,
            size_hint=(0.2, 1.0),
            # pos_hint={"x": .5, "y": .5},
            font_size="50sp",
        )
        stream_btn = Button(
            text="Stream",
            on_press=functools.partial(self.stream, label),
            size_hint=(0.2, 1.0),
            # pos_hint={"x": .5, "y": .5},
            font_size="50sp",
        )

        main_layout = BoxLayout(padding=2, orientation='vertical')
        main_layout.size = Window.size
        main_layout.pos = (0, 0)
        top_layout = BoxLayout(padding=2, orientation='horizontal')
        top_layout.add_widget(label)
        top_layout.add_widget(close_btn)
        main_layout.add_widget(top_layout)

        bottom_layout = BoxLayout(padding=2, orientation='horizontal')
        # adding labels as spacers
        bottom_layout.add_widget(Label(size_hint=(0.40, 1.0)))
        bottom_layout.add_widget(talk_btn)
        bottom_layout.add_widget(Label(size_hint=(0.05, 1.0)))
        bottom_layout.add_widget(stream_btn)
        bottom_layout.add_widget(Label(size_hint=(0.40, 1.0)))
        main_layout.add_widget(bottom_layout)

        # TODO(hari): Doesn't seem to work for some reason
        # self.gui_automation.register_hotkey(ShortCutKeys, 
        #     lambda k, u: self.record(label, talk_btn))
        
        return main_layout
    
    def record(self, label, button):
        msg = "Say Something! Listening..."
        logging.info(msg)
        
        button.disabled = True
        text = self.clistener.listen()

        label.text = text
        logging.info(f"You said: '{text}'")

        try:
            actions = self.resolver.parse(
                cmd=text,
                gui=self.gui_automation,
                browser=None
            )
            for a in actions:
                logging.info(f"Running: {a.name}")
                a.run()

            label.text = self.GREETING_TEXT
        except Exception as e:
            msg = f"Uh oh! Failed to act on this: {str(e)}"
            label.text = msg
            traceback.print_exc(file=sys.stdout)
            logging.error(msg)

        button.disabled = False

    def close_window(self, button):
        # self.get_running_app().stop()
        # self.root_window.close()
        Window.hide()

    def show_window(self):
        Window.restore()
    
    def stream(self, label, button):
        logging.info(self.LISTENING_TEXT)
        
        button.disabled = True

        while True:
            text = self.clistener.listen()

            # Stop Word
            if text == "exit":
                logging.info("Exiting continuous record mode.")
                break

            label.text = text
            logging.info(f"You said: '{text}'")

            try:
                actions = self.resolver.parse(
                    cmd=text,
                    gui=self.gui_automation,
                    browser=None
                )
                for a in actions:
                    logging.info(f"Running: {a.name}")
                    a.run()

                label.text = self.LISTENING_TEXT
            except Exception as e:
                msg = f"Uh oh! Failed to act on this: {str(e)}"
                label.text = msg
                traceback.print_exc(file=sys.stdout)
                logging.error(msg)

        button.disabled = False
        