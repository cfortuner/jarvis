import functools
import logging

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
from command_listener import CommandListener
from command_parser import CommandParser


ShortCutKeys = ['ctrl', 'alt', 'j']

class SpeechApp(App):
    GREETING_TEXT = "What can I do for you?"

    def build(self):
        # This seems to first create regular sized window
        # and then update it to the specified size. It's
        # better to override size using Config.set methods
        # at the top of the file.
        # Window.borderless = True
        # Window.size = (100, 50)
        logging.info("Running build")
        self.clistener = CommandListener()
        self.ui_automation = create_automation_instance()

        logging.info("Getting screen size")
        screensize = self.ui_automation.get_screensize()
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

        layout = BoxLayout(padding=2, orientation='vertical')
        layout.size = Window.size
        layout.pos = (0, 0)
        top_layout = BoxLayout(padding=2, orientation='horizontal')
        top_layout.add_widget(label)
        top_layout.add_widget(close_btn)
        layout.add_widget(top_layout)

        bottom_layout = BoxLayout(padding=2, orientation='horizontal')
        # adding labels as spacers
        bottom_layout.add_widget(Label(size_hint=(0.42, 1.0)))
        bottom_layout.add_widget(talk_btn)
        bottom_layout.add_widget(Label(size_hint=(0.42, 1.0)))
        layout.add_widget(bottom_layout)

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
        logging.info(f"Received {text}")

        try:
            parser = CommandParser()
            actions = parser.parse(text)
            for a in actions:
                logging.info(f"Running {a.name}")
                a.run(self.ui_automation)

            label.text = self.GREETING_TEXT
        except Exception as e:
            label.text = f"Uh oh! Failed to act on this: {str(e)}"

        button.disabled = False

    def close_window(self, button):
        # self.get_running_app().stop()
        # self.root_window.close()
        Window.hide()

    def show_window(self):
        Window.restore()
        