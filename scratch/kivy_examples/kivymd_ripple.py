"""
I think this is what we want. In particular `ripple_duration_out`
https://kivymd.readthedocs.io/en/latest/behaviors/ripple/

For the elevated microphone:
https://kivymd.readthedocs.io/en/latest/behaviors/elevation/

For the list of parsed commands
https://kivymd.readthedocs.io/en/latest/components/list/


"""

from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from kivymd.app import MDApp
from kivymd.uix.behaviors import CircularRippleBehavior

KV = '''
#:import images_path kivymd.images_path


Screen:

    CircularRippleButton:
        source: f"{images_path}/kivymd.png"
        size_hint: None, None
        size: "250dp", "250dp"
        pos_hint: {"center_x": .5, "center_y": .5}
'''


class CircularRippleButton(CircularRippleBehavior, ButtonBehavior, Image):
    def __init__(self, **kwargs):
        self.ripple_scale = 0.85
        super().__init__(**kwargs)


class Example(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)


Example().run()
