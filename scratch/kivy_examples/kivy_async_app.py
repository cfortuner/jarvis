import trio

from kivy.app import async_runTouchApp
from kivy.uix.label import Label
from kivy.app import App
from kivy.lang import Builder

KV_CODE = '''
Label:
    text: 'Kivy & Trio'
'''

class TestApp(App):
    nursery = None
    def build(self):
        return Builder.load_string(KV_CODE)

    def on_start(self):
        self.nursery.start_soon(self.animate_label)

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

    async def animate_label(self):
        label = self.root
        sleep = trio.sleep
        await sleep(1)
        while True:
            await sleep(3)
            label.text = "First Call"
            await sleep(3)
            label.text = "Second Call"


if __name__ == '__main__':
    trio.run(TestApp().root_task)
