import logging
import os
import psutil
import gi
gi.require_version('Wnck', '3.0')
gi.require_version('Keybinder', '3.0')

from gi.repository import Wnck, GdkX11, Gdk, Keybinder

from gui_automation import GUIAutomation


class LinuxAutomation(GUIAutomation):
    COMMON_APP_NAME_MAPPINGS = {
        "browser": "xdg-open https://www.google.com",
        "chrome": "google-chrome",
        "explorer": "nautilus",
        "finder": "nautilus",
        "file explorer": "nautilus",
        "terminal": "x-terminal-emulator",
        "command line": "x-terminal-emulator",
        "command prompt": "x-terminal-emulator",
    }

    def __init__(self):
        super().__init__()

        Keybinder.init()

    def __exit__(self):
        # TODO(hari): Make sure this gets called
        Wnck.shutdown()

    def _get_running_apps(self):
        screen = Wnck.Screen.get_default()
        screen.force_update()
        return screen.get_windows()

    def _get_window_name(self, win):
        return psutil.Process(win.get_pid()).name()

    def _get_window_with_name(self, win_name):
        for w in self._get_running_apps():
            if self._get_window_name(w) == win_name:
                return w
        
        return None

    def get_list_of_windows(self) -> list:
        return list(map(self._get_window_name, 
                        self._get_running_apps()))

    def get_active_window(self) -> str:
        screen = Wnck.Screen.get_default()
        screen.force_update()
        return self._get_window_name(screen.get_active_window())

    def switch_to_window(self, app_name: str):
        w = self._get_window_with_name(app_name)
        if w is None:
            raise Exception(f"Failed to find an app with name {app_name}")

        # X11 requires that the correct time be set
        # for any events for them to act properly so
        # reading the current time from the server
        now = GdkX11.x11_get_server_time(
            GdkX11.X11Window.lookup_for_display(
                Gdk.Display.get_default(), 
                GdkX11.x11_get_default_root_xwindow()))
        w.activate(now)

    def get_window_bounds(self, app_name) -> list:
        w = self._get_window_with_name(app_name)
        if w is None:
            raise Exception(f"Failed to find an app with name {app_name}")

        return list(w.get_geometry())

    def set_window_bounds(self, app_name, bounds: list) -> None:
        w = self._get_window_with_name(app_name)
        if w is None:
            raise Exception(f"Failed to find an app with name {app_name}")

        w.set_geometry(
            Wnck.WindowGravity.CURRENT,
            # Resize mask specifies flags for which dimension of the
            # geometry needs to be updated. Configuring here for all 
            # dimensions to be updated.
            # https://lazka.github.io/pgi-docs/Wnck-3.0/flags.html#Wnck.WindowMoveResizeMask
            15,
            bounds[0], bounds[1], bounds[2], bounds[3])

    def open_application(self, app_name: str):
        if app_name in self.COMMON_APP_NAME_MAPPINGS:
            app_name = self.COMMON_APP_NAME_MAPPINGS[app_name]
        logging.info(app_name)
        return os.system(app_name)

    def register_hotkey(self, keys, callback):
        def add_tags(key):
            if key == 'ctrl':
                return '<Ctrl>'
            elif key == 'alt':
                return '<Alt>'
            elif key == 'shift':
                return '<Shift>'
            
            return key

        keys = [add_tags(k.lower()) for k in keys]
        shortcut_key = ''.join(keys)
        logging.info(shortcut_key)
        Keybinder.bind(shortcut_key, callback)
