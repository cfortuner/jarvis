import functools
import logging
import time

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


from gui_automation import create_automation_instance
from command_listener.basic_listener import BasicListener
from command_listener.google_listener import GoogleListener
from command_parser import CommandParser

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

class SpeechApp(App):
    GREETING_TEXT = "What can I do for you?"
    LISTENING_TEXT = "Continuous listening mode. Say 'exit' to close"

    def build(self):
        # This seems to first create regular sized window
        # and then update it to the specified size. It's
        # better to override size using Config.set methods
        # at the top of the file.
        # Window.borderless = True
        # Window.size = (100, 50)
        # self.clistener = BasicListener()
        self.clistener = GoogleListener()
        self.ui_automation = create_automation_instance()

        screensize = self.ui_automation.get_screensize()
        Window.left = screensize[0] - window_width - 15
        Window.top = 40
        # Window.clearcolor = (1, 1, 1, 0.5)

        label = Label(
            text=self.GREETING_TEXT,
            size_hint=(1.0, .5),
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
        stream_btn = Button(
            text="Stream",
            on_press=functools.partial(self.stream, label),
            size_hint=(0.2, 1.0),
            # pos_hint={"x": .5, "y": .5},
            font_size="50sp",
        )

        layout = BoxLayout(padding=2, orientation='vertical')
        layout.size = Window.size
        layout.pos = (0, 0)
        layout.add_widget(label)

        vlayout = BoxLayout(padding=2, orientation='horizontal')
        # adding labels as spacers
        vlayout.add_widget(Label(size_hint=(0.42, 1.0)))
        vlayout.add_widget(talk_btn)
        vlayout.add_widget(Label(size_hint=(0.42, 1.0)))
        vlayout.add_widget(stream_btn)
        vlayout.add_widget(Label(size_hint=(0.42, 1.0)))
        layout.add_widget(vlayout)

        # TODO(hari): Doesn't seem to work for some reason
        # self.ui_automation.register_hotkey(ShortCutKeys, 
        #     lambda k, u: self.record(label, talk_btn))
        
        return layout
    
    def record(self, label, button):
        msg = "Say Something! Listening..."
        logging.info(msg)
        
        button.disabled = True
        text = self.clistener.listen()

        label.text = text
        logging.info(f"You said: '{text}'")

        try:
            parser = CommandParser()
            actions = parser.parse(text)
            for a in actions:
                logging.info(f"Running: {a.name}")
                a.run(self.ui_automation)

            label.text = self.GREETING_TEXT
        except Exception as e:
            label.text = f"Uh oh! Failed to act on this: {str(e)}"

        button.disabled = False
    
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
                parser = CommandParser()
                actions = parser.parse(text)
                for a in actions:
                    logging.info(f"Running: {a.name}")
                    a.run(self.ui_automation)

                label.text = self.LISTENING_TEXT
            except Exception as e:
                label.text = f"Uh oh! Failed to act on this: {str(e)}"

        button.disabled = False
        