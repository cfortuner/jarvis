"""Mac automation using AppKit.

https://developer.apple.com/documentation/accessibility/integrating_accessibility_into_your_app
"""

import atomac

import AppKit

from ApplicationServices import *
from CoreFoundation import *

from .desktop_automation import DesktopAutomation


class MacAutomation(DesktopAutomation):

    @property
    def ws(self):
        return AppKit.NSWorkspace.sharedWorkspace()

    def get_running_apps(self, with_gui: bool = True) -> list:
        """Returns list of NSRunningApplication instances."""
        app_policies = {
            0: [],  # appears in the Dock and may have a user interface.
            1: [],  # doesn’t appear in the Dock, but may be activated programmatically or by clicking on one of its windows.
            2: [],  # doesn’t appear in the Dock and may not create windows or be activated.
        }
        apps = self.ws.runningApplications()
        for app in apps:
            app_policies[app.activationPolicy()].append(app)

        if with_gui:
            # NOTE: This code may not be necessary any more... but leaving here for reference
            # TODO(hari): Currently returning all the apps and not just
            # the ones with UI associated to them. Need to filter out background
            # apps here.
            # for app in apps:
            #     pid = app.processIdentifier()
            #     app_ref = AXUIElementCreateApplication(pid)
            #     app_ref = NativeUIElement(ref = app_ref)
            #     if hasattr(app_ref, 'windows') and len(app_ref.windows()) > 0:
            #         out_apps.append(app)
            return app_policies[0]
        return app_policies[0] + app_policies[1]

    def get_list_of_windows(self) -> list:
        # Returns running apps with GUIs (may not be visible, but still running.)
        apps = self.get_running_apps(with_gui=True)
        return [a.localizedName().lower() for a in apps]

    def get_active_window(self) -> str:
        # https://gist.github.com/luckman212/91cdd9a08e98a9f01214bdfde3057e85
        # frontmostApplication doesn't seem to refresh
        app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
        return str(app["NSApplicationName"]).lower()

    def switch_to_window(self, app_name):
        ra = AppKit.NSRunningApplication
        apps = self.get_running_apps()
        chosen_apps = [a for a in apps if a.localizedName().lower() == app_name]
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

    def _get_all_menu_items(self, ax_item):
        """Using mac accessibility elements, we fetch all the leaf nodes
        of a menu bar"""
        output = []
        try:
            if len(ax_item.AXChildren) > 0:
                for item in ax_item.AXChildren:
                    output.extend(self._get_all_menu_items(item))
            else:
                    output.append(ax_item)
        except:
            # some menu items may have special things like "text edit items"
            # let's ignore such cases
            pass 
        return output

    def get_all_menuitems_for_window(self, app_name) -> dict:
        ra = AppKit.NSRunningApplication
        apps = self.get_running_apps()
        chosen_apps = [a for a in apps if a.localizedName().lower() == app_name]
        if len(chosen_apps) == 0:
            raise Exception("Application is not found")

        # pyatom(aka atomac) gets the app details by using mac accessibility api.
        # Anything prefixed with ax implies an accessibility element.
        ax_app = atomac.getAppRefByPid(chosen_apps[0].processIdentifier())
        menuitems = {}
        for menuitem in ax_app.menuItem().AXChildren:
            try:
                menuitems[menuitem.AXTitle] = self._get_all_menu_items(menuitem)
            except:
                pass
        return menuitems

    def get_window_bounds(self, app_name) -> list:
        raise NotImplementedError()

    def set_window_bounds(self, app_name, bounds) -> None:
        raise NotImplementedError()

if __name__ == '__main__':
    mac = MacAutomation()
    apps = mac.get_list_of_windows()
    import pdb; pdb.set_trace()
