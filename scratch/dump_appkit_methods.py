# Write list of methods/attribs on AppKit classes
# python -m scratch.dump_appkit_methods

import AppKit

# from jarvis.automation.desktop.mac_automation import MacAutomation
from PyObjCTools import AppHelper

# def write_methods_to_file(obj):
#     fpath = f"scratch/{obj.className()}_methods.txt"
#     methods = list(dir(obj))
#     with open(fpath, "w") as f:
#         f.write("\n".join(methods))
#     return fpath


# def dump_methods(write=True):
#     M = MacAutomation()

#     ws = M.ws
#     print(type(ws))

#     app = M.ws.runningApplications()[0]
#     print(type(app))

#     runLoop = AppKit.NSRunLoop.currentRunLoop()
#     print(type(runLoop))

#     if write:
#         write_methods_to_file(ws)
#         write_methods_to_file(app)
#         write_methods_to_file(runLoop)
#     else:
#         # play with the objects
#         import pdb; pdb.set_trace()

from Foundation import NSAutoreleasePool


def log_running_apps(name, debug=False):
    import time

    while True:
        pool = NSAutoreleasePool.alloc().init()
        ws = AppKit.NSWorkspace.sharedWorkspace()
        apps = ws.runningApplications()
        unterminated = ws.unterminatedApplications()
        app_names = [a.localizedName() for a in apps]
        print(f"NumRunningApps: {len(apps)}", "NumUnterminated", len(unterminated))
        print("ActiveApp", ws.activeApplication())
        print(f"App {name} Running: {name in app_names}")
        del pool

        time.sleep(2)

        if debug:
            import pdb; pdb.set_trace()


def print_activation_policy(name):
    # Shows the list of applications by which ones are visible/have GUI
    # https://developer.apple.com/documentation/appkit/nsapplication/activationpolicy

    app_policies = {
        0: [],
        1: [],
        2: [],
    }
    apps = AppKit.NSWorkspace.sharedWorkspace().runningApplications()
    for app in apps:
        print(app, app.activationPolicy())
        app_policies[app.activationPolicy()].append((app, app.localizedName()))

    for policy, apps in app_policies.items():
        print(f"\nPolicy: {policy} -------------------\n")
        apps_ = '\n'.join([a[1] for a in apps])
        print(apps_)

    # Get notification about changes to applications
    # https://stackoverflow.com/questions/32533525/nsworkspaces-frontmostapplication-doesnt-change-after-initial-use
    
    # We can listen for notifications or trigger the runloop
    # https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Multithreading/RunLoopManagement/RunLoopManagement.html

    # Accessing lower-level processes from AppKit https://pilky.me/appreciating-appkit-part-2/


class ExampleDelegate(AppKit.NSObject):

    def applicationDidFinishLaunching_(self, notification):
        import time
        print(notification)
        print("Hello world!")
        while True:
            apps = self.get_running_app_names()
            print(apps)
            print("WhatsApp" in apps)
            time.sleep(2)

    @property
    def ws(self):
        return AppKit.NSWorkspace.sharedWorkspace()

    def get_running_apps(self, with_gui: bool = False) -> list:
        """Returns list of NSRunningApplication instances."""
        apps = self.ws.runningApplications()
        out_apps = apps
        if with_gui:
            pass
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

    def get_running_app_names(self, with_gui: bool = False) -> list:
        """Returns list of NSRunningApplication names."""
        apps = self.get_running_apps(with_gui)
        return [a.localizedName() for a in apps]


if __name__ == "__main__":
    import sys
    debug = False if len(sys.argv) < 2 else sys.argv[1]
#    dump_methods(write=False)
    # log_running_apps("WhatsApp", debug)
    print_activation_policy("WhatsApp")
    # app = AppKit.NSApplication.sharedApplication()
    # print(app)
    # print(AppKit.NSApp)
    # delegate = ExampleDelegate.new()
    # print(delegate)
    # app.setDelegate_(delegate)
    # # example.run()
    # # print(example)
    # # print(example.get_running_apps())
    # # print(example.get_running_app_names())
    # AppHelper.runEventLoop()
    # print("running event loop")
    # # import pdb; pdb.set_trace()
