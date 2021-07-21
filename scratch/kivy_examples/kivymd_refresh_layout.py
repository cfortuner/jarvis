from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import StringProperty

from kivymd.uix.button import MDIconButton
from kivymd.icon_definitions import md_icons
from kivymd.uix.list import ILeftBodyTouch, OneLineIconListItem
from kivymd.theming import ThemeManager
from kivymd.utils import asynckivy

Builder.load_string('''
<ItemForList>
    text: root.text

    IconLeftSampleWidget:
        icon: root.icon


<Example@FloatLayout>

    BoxLayout:
        orientation: 'vertical'

        MDToolbar:
            title: app.title
            md_bg_color: app.theme_cls.primary_color
            background_palette: 'Primary'
            elevation: 10
            left_action_items: [['menu', lambda x: x]]

        MDScrollViewRefreshLayout:
            id: refresh_layout
            refresh_callback: app.refresh_callback
            root_layout: root

            MDGridLayout:
                id: box
                adaptive_height: True
                cols: 1
''')


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class ItemForList(OneLineIconListItem):
    icon = StringProperty()


class Example(MDApp):
    title = 'Example Refresh Layout'
    screen = None
    x = 0
    y = 15
    limit = 1

    def build(self):
        self.screen = Factory.Example()
        self.set_list()
        Clock.schedule_interval(self.refresh_callback, 1)

        return self.screen

    def set_list(self):
        async def set_list():
            print(f"refreshing {self.limit}")
            names_icons_list = list(md_icons.keys())[self.x:self.y]
            for name_icon in names_icons_list[:self.limit]:
                await asynckivy.sleep(0)
                self.screen.ids.box.add_widget(
                    ItemForList(icon=name_icon, text=name_icon))
        asynckivy.start(set_list())

    def refresh_callback(self, interval):
        '''A method that updates the state of your application
        while the spinner remains on the screen.'''
        self.screen.ids.box.clear_widgets()
        if self.x == 0:
            self.x, self.y = 15, 30
        else:
            self.x, self.y = 0, 15
        self.set_list()
        self.screen.ids.refresh_layout.refresh_done()
        self.tick = 0
        self.limit += 1

        


Example().run()
