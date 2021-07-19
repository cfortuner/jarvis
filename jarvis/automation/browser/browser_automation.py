from automation.gui import GUIAutomation

class BrowserAutomation():
    """Base class for all browser automation implementations."""

    def __init__(self, gui: GUIAutomation):
        self.gui = gui

    def get_list_of_tabs(self) -> list:
        raise NotImplementedError("Needs to be overriden by the derived class")

    def switch_to_tab(self, tab_title):
        raise NotImplementedError("Needs to be overriden by the derived class")

def ChromiumBrowserAutomation(BrowserAutomation):
    """Browser automation for all Chromium derived browsers"""

    def __init__(self, gui: GUIAutomation, browser_name: str):
        super(gui)

        self.name = browser_name

    def get_list_of_tabs(self) -> list:
        """Returns the title for all the tabs in all the windows
        of the chromium browser instance"""
        action_list = self._get_menuitems_for_all_tabs()
        return [a.name() for a in action_list]

    def switch_to_tab(self, tab_title):
        """Switch to the tab with specific title"""
        action_list = self._get_menuitems_for_all_tabs()
        for a in action_list:
            if tab_title in a.name():
                a.click()
                return
        
        raise Exception("Failed to find a tab with that title")

    def _get_menuitems_for_all_tabs(self) -> list:
        """Returns menuitems for all tabs that when clicked
        will result in switching to that tab
        
        This makes use of the fact that Chromium browsers have a menu entry 
        in the Tab menu for all tabs open in that particular window.
        """
        windows = self.gui.get_list_of_windows()
        tabs = []
        tab_menu_name = 'Tab'
        tab_name_begin_str = 'move tab to new window'
        for w in windows:
            if self.name in w:
                menuitems = self.gui.get_all_menuitems_for_window(w)
                if tab_menu_name in menuitems:
                    idx = 0
                    for item in menuitems[tab_menu_name]:
                        idx += 1
                        if item.name().lower() == tab_name_begin_str:
                            break
                    tabs.extend([
                        t for t in menuitems[tab_menu_name][idx:]
                    ])

        return tabs
