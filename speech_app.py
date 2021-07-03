import functools
import logging
import time

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()


def audio_to_text(audio):
    logging.info("Transcribing audio to text...")
    try:
        text = r.recognize_google(audio)
    except sr.UnknownValueError:
        text = "Speech Recognition could not understand audio."
    except sr.RequestError as e:
        text = "Could not request results from Speech Recognition service; {0}".format(e)
    finally:
        logging.info(text)
        return text


class SpeechApp(App):
    def build(self):
        logging.info("Calibrating microphone. Be quiet..")
        with m as source:
            r.adjust_for_ambient_noise(source)
        
        label = Label(
            text="",
            size_hint=(.5, .5),
            pos_hint={"x": .5, "y": .5},
            font_size="20sp",
        )
        talk_btn = Button(
            text="Record",
            on_press=functools.partial(self.record, label),
            size_hint=(.5, .5),
            pos_hint={"x": .5, "y": .5},
            font_size="50sp",

        )

        layout = BoxLayout(padding=10)
        layout.add_widget(talk_btn)
        layout.add_widget(label)
        
        return layout
    
    def record(self, label, button):
        msg = "Say Something! Listening..."
        logging.info(msg)
        
        with m as source:
            logging.info("Listening for audio...")
            audio = r.listen(source)

        text = audio_to_text(audio)

        label.text = f"You said:\n\n'{text}'\n\nClick to record again."
        

if __name__ == "__main__":
    SpeechApp().run()
