import AppKit

from ApplicationServices import *
from CoreFoundation import *

from .gui_automation import GUIAutomation


class MacAutomation(GUIAutomation):
    def _get_running_apps(self) -> list:
        """Returns all the running apps with an open window"""
        ws = AppKit.NSWorkspace.sharedWorkspace()
        apps = ws.runningApplications()
        out_apps = apps
        # TODO(hari): Currently returning all the apps and not just
        # the ones with UI associated to them. Need to filter out background
        # apps here.
        # for app in apps:
        #     pid = app.processIdentifier()
        #     app_ref = AXUIElementCreateApplication(pid)
        #     app_ref = NativeUIElement(ref = app_ref)
        #     if hasattr(app_ref, 'windows') and len(app_ref.windows()) > 0:
        #         out_apps.append(app)
        return out_apps

    def get_list_of_windows(self) -> list:
        apps = self._get_running_apps()
        return [a.localizedName() for a in apps]

    def get_active_window(self) -> str:
        app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        return app

    def switch_to_window(self, app_name):
        ra = AppKit.NSRunningApplication
        apps = self._get_running_apps()
        chosen_apps = [a for a in apps if a.localizedName() == app_name]
        if len(chosen_apps) == 0:
            raise Exception("Application is not found")
    
        # chosen_apps and app_ra are of the same type but somehow
        # I can't directly use chosen_apps instance to make the activate
        # call but this is working
        app_ra = ra.runningApplicationWithProcessIdentifier_(chosen_apps[0].processIdentifier())

        # NSApplicationActivateAllWindows | NSApplicationActivateIgnoringOtherApps
        # == 3 - PyObjC in 10.6 does not expose these constants though so I have
        # to use the int instead of the symbolic names
        app_ra.activateWithOptions_(3)

    def get_window_bounds(self, app_name) -> list:
        raise NotImplementedError()

    def set_window_bounds(self, app_name, bounds) -> None:
        raise NotImplementedError()

if __name__ == '__main__':
    mac = MacAutomation()
    apps = mac.get_list_of_windows()
    import pdb; pdb.set_trace()
