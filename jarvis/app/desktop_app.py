import logging
import sys
import traceback

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDTextButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
from kivymd import icon_definitions

from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import (
    CircularRippleBehavior,
    FakeCircularElevationBehavior,
)
from kivy.core.window import Window

import trio


from jarvis.actions import ActionResolver
from jarvis.const import SUPPORTED_COMMANDS
from jarvis.nlp.speech2text import GoogleTranscriber

# Alternative library which claims to be faster than trio/asyncio for Kivy
from kivymd.utils import asynckivy


KV="""
<CircularElevationButton>:
    size_hint: None, None
    radius: self.size[0] / 2
    md_bg_color: 0, 0, 1, 1

    MDIcon:
        icon: "microphone"
        halign: "center"
        valign: "center"
        size: root.size
        pos: root.pos
        font_size: root.size[0] * .6
        theme_text_color: "Custom"
        text_color: [1] * 4

MDScreen:
    GridLayout:
        id: layout
        cols: 2
        size: root.size
        GridLayout:
            id: left_layout
            rows: 3
            FloatLayout:
                id: microphone_layout
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                RecordButton:
                    id: microphone_button
                    size: self.parent.height / 2, self.parent.size[1] / 2
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    elevation: 35
            BoxLayout:
                id: transcript_layout
                size: self.size
                canvas.before:
                    Color:
                        rgba: .2, .2, .2, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Label:
                    id: transcript_box
                    padding_x: 20.0
                    padding_y: 20.0
                    text: ""
                    text_size: self.width, self.height
                    valign: "top"
                    canvas.before:
                        Color:
                            rgba: .3, .2, .6, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
            ScrollView:
                id: actions_scroll_view
                canvas.before:
                    Color:
                        rgba: .2, .5, .8, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                MDList:
                    id: actions_list
                    canvas.before:
                        Color:
                            rgba: .2, .5, .8, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    size_hint_y: None

        ScrollView:
            id: right_layout
            canvas.before:
                Color:
                    rgba: .0, 0, 0, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: console_text
                padding_x: 20.0
                padding_y: 20.0
                size_hint_y: None
                height: self.texture_size[1]  # the size needed to fit the text
                text_size: self.width, None
"""


class CircularElevationButton(
    FakeCircularElevationBehavior,
    CircularRippleBehavior,
    ButtonBehavior,
    MDBoxLayout,
):
    pass
 

class RecordButton(CircularElevationButton):
    """Button for turning microphone on/off."""
    recording = False
    voice_activity_event = None

    def on_press(self):
        if not self.recording:
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        logging.info("Turning microphone ON!")
        self.recording = True
        self.children[0].icon = "circle"
        self.md_bg_color = (1, 0, 0, 1)
        self.voice_activity_event = Clock.schedule_interval(self.handle_voice_activity, 1)

    def turn_off(self):
        logging.info("Turning microphone OFF!")
        self.children[0].icon = "microphone"
        self.md_bg_color = (0, 0, 1, 1)
        self.recording = False
        if self.voice_activity_event is not None:
            Clock.unschedule(self.voice_activity_event)

    def handle_voice_activity(self, *args):
        """Can be used to animate the microphone.."""
        # logging.info("Handling voice activity")
        pass


def _make_icon_list_item(text_primary, text_secondary, icon):
    list_item = TwoLineIconListItem(
        text=text_primary,
        secondary_text=text_secondary,
    )
    icon = IconLeftWidget(icon=icon)
    list_item.add_widget(icon)
    return list_item


class DesktopApp(MDApp):
    nursery = None

    def build(self):
        self.listener = GoogleTranscriber(SUPPORTED_COMMANDS, single_utterance=True)
        self.resolver = ActionResolver()

        self.theme_cls.theme_style="Light"
        screen = Builder.load_string(KV)
        screen.size = Window.size
        logging.info("Screen size: {}".format(screen.size))
        logging.info("Screen pos: {}".format(screen.pos))

        self.recording = False
        screen.ids.microphone_button.bind(on_press=self.microphone_on)

        return screen

    async def root_task(self):
        async with trio.open_nursery() as nursery:
            self.nursery = nursery
            async def app_task():
                # call App.async_run () instead of # App.run ().
                 # This demonstrates that the use of trio as asynchronous input and output library.
                 await self.async_run(async_lib='trio')
                # When event loop of kivy is closed, when the Window is closed other words
                # all other task also terminate.
                 nursery.cancel_scope.cancel()
            nursery.start_soon(app_task)

    def on_start(self):
        self.nursery.start_soon(self.async_record)

    async def add_action_to_list(self, name, text, icon="language-python"):
        logging.info("Adding action to List {}".format(name))
        actions_list = self.root.ids.actions_list
        actions_scroll_view = self.root.ids.actions_scroll_view
        num_items = len(actions_list.children)
        list_item = _make_icon_list_item(
            f"[{num_items}] {name}", text, icon
        )
        actions_list.add_widget(list_item)
        # This seems to hang/make the list disappear after 3 commands
        #actions_scroll_view.scroll_to(list_item)
        await trio.sleep(0)

    async def add_text_to_console(self, msg):
        console_feed = self.root.ids.console_text
        console_feed.text = console_feed.text + f"{msg}\n"
        await trio.sleep(0)

    async def add_text_to_transcript(self, text):
        label = self.root.ids.transcript_box
        if label.text != text:
            label.text = text
        await trio.sleep(0)

    async def log(self, msg):
        logging.info(msg)
        await self.add_text_to_console(msg)
        await trio.sleep(0)
    
    def microphone_on(self, dt):
        self.recording = True
        self.root.ids.transcript_box.text = "Listening..."

    def microphone_off(self):
        self.recording = False
        self.root.ids.microphone_button.turn_off()
        self.root.ids.transcript_box.text = ""

    async def async_record(self):
        await self.log("Running Async record")
        while True:
            if self.recording:
                await self.record()
                self.microphone_off()
            else:
                await trio.sleep(.1)

    async def record_real_time_transcript(self):
        while True:
            await self.log("Beginning transcription loop")
            transcripts = self.listener.listen()
            for transcript in transcripts:                
                await self.add_text_to_transcript(transcript.text)
                if transcript.text == "exit":
                    return
            await self.add_text_to_transcript("Listening...")
            await self.log("Exiting after silence")

    async def record(self):
        """Async Kivy allows you to update the UI inside a method without returning.
        The method can loop and do stuff, and still update UI elements. Without Async Kivy,
        Kivy waits for your method to return before calling Clock.tick() and updating the UI
        to reflect your changes.

        NOTE: The transcript generator still runs synchronously and the entire App appears to hang 
        (I can't play with the UI) while waiting for a new transcript. I think we can solve this by
        moving making the transcriber generator async, but it might be easier to scrap Async Kivy and
        do the following:

            1. Create a background thread for the transcriber
            2. Establish a thread-safe queue for the transcriber to push transcripts
            3. Write a `poll_queue` method to query the queue and update the UI if it's not empty
            4. Initialize a polling thread with `Clock.schedule_interval(self.poll_queue, .01)`

        This way we don't have to make all our functions `async` and use `await` to call them.
        """
        should_exit = False
        while not should_exit:
            await self.add_text_to_transcript("Listening...")
            # TODO: Move the generator to a background thread and pull from queue
            transcripts = self.listener.listen()
            for transcript in transcripts:
                if transcript.text is not None:
                    await self.add_text_to_transcript(transcript.text)
                if transcript.text == "exit" or transcript.deadline_exceeded:
                    await self.log(f"Exiting...")
                    should_exit = True
                    break
                elif transcript.is_final:
                    try:
                        actions = self.resolver.parse(cmd=transcript.text)
                        # Exit as soon as the first action succeeds
                        for a in actions:
                            await self.log("Running: {} - {}".format(a.name, transcript.text))
                            result = a.run()
                            await self.log("Action: {} status: {}, error: {}".format(
                                a.name, result.status, result.error)
                            )
                            if result.status == "succeeded":
                                await self.add_action_to_list(a.name, transcript.text)
                                break
                    except Exception as e:
                        msg = "Uh oh! Failed to act on this: {}".format(str(e))
                        traceback.print_exc(file=sys.stdout)
                        await self.log(msg)
                        break

        await self.log("Exiting streaming mode.")
