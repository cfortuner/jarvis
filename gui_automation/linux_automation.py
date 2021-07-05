import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk, Wnck, GdkX11, Gdk

from gui_automation import GUIAutomation


class LinuxAutomation(GUIAutomation):
    def __exit__(self):
        # TODO(hari): Make sure this gets called
        Wnck.shutdown()

    def _get_running_apps(self):
        screen = Wnck.Screen.get_default()
        screen.force_update()
        return screen.get_windows()

    def get_list_of_windows(self) -> list:
        return map(lambda w: w.get_name(), self._get_running_apps())

    def get_active_window(self) -> str:
        screen = Wnck.Screen.get_default()
        screen.force_update()
        return screen.get_active_window().get_name()

    def switch_to_window(self, app_name: str):
        # X11 requires that the correct time be set
        # for any events for them to act properly so
        # reading the current time from the server
        now = GdkX11.x11_get_server_time(
            GdkX11.X11Window.lookup_for_display(
                Gdk.Display.get_default(), 
                GdkX11.x11_get_default_root_xwindow()))
        windows = self._get_running_apps()
        for w in windows:
            if w.get_name() == app_name:
                w.activate(now)
        
        raise Exception(f"Failed to find an app with name {app_name}")

    def get_window_bounds(self, app_name) -> list:
        windows = self._get_running_apps()
        for w in windows:
            if w.get_name() == app_name:
                return list(w.get_geometry())

        raise Exception(f"Failed to find an app with name {app_name}")

    def set_window_bounds(self, app_name, bounds: list) -> None:
        windows = self._get_running_apps()
        for w in windows:
            if w.get_name() == app_name:
                w.set_geometry(
                    Wnck.WindowGravity.CURRENT,
                    # Resize mask specifies flags for which dimension of the
                    # geometry needs to be updated. Configuring here for all 
                    # dimensions to be updated.
                    # https://lazka.github.io/pgi-docs/Wnck-3.0/flags.html#Wnck.WindowMoveResizeMask
                    15,
                    bounds[0], bounds[1], bounds[2], bounds[3])

        raise Exception(f"Failed to find an app with name {app_name}")

    def open_application(self, app_name: str):
        raise NotImplementedError("Needs to be overriden by the derived class")
