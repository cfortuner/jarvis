import functools
import logging
import time

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


from command_listener import CommandListener
from command_parser import CommandParser


class SpeechApp(App):
    def build(self):
        self.clistener = CommandListener()

        label = Label(
            text="",
            size_hint=(.5, .5),
            # pos_hint={"x": .5, "y": .5},
            font_size="20sp",
        )
        talk_btn = Button(
            text="Record",
            on_press=functools.partial(self.record, label),
            size_hint=(.5, .5),
            # pos_hint={"x": .5, "y": .5},
            font_size="50sp",
        )

        layout = BoxLayout(padding=10, orientation='vertical')
        layout.add_widget(label)
        layout.add_widget(talk_btn)
        
        return layout
    
    def record(self, label, button):
        msg = "Say Something! Listening..."
        logging.info(msg)
        
        button.disabled = True
        text = self.clistener.listen()

        label.text = f"You said:\n\n'{text}'\n\nClick to record again."
        button.disabled = False

        # parser = CommandParser()
        # actions = parser.parse(text)
        # for a in actions:
        #     a.run()
        