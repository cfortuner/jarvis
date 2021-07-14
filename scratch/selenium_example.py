"""Selenium examples

Install: https://www.selenium.dev/documentation/en/selenium_installation
Requires installing the web drivers separately (on MacOS you also have to grant permissions to web driver)

Run `python scratch/selenium_example.py`
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def test_click_a_link():
    """Click a link on a website by its name."""
    website_url = input("website url: ")

    # Manually initialize the driver
    driver = webdriver.Chrome()
    try:    
        driver.get(f"https://{website_url}")
        wait = WebDriverWait(driver, 2)
        link_text = input("name of link: ")
        # Also, PARTIAL_LINK_TEXT, or return all the matching elements
        driver.find_element(by=By.LINK_TEXT, value=link_text).click()
    except Exception as e:
        print(e)
    finally:
        # Clean up all windows and background processes
        # https://www.selenium.dev/documentation/en/webdriver/browser_manipulation/#quitting-the-browser-at-the-end-of-a-session
        input("Press any key to exit.")
        driver.quit()


def test_browser_keep_open():
    """Keep the browser window open after program exits."""
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    website_url = input("website url: ")
    driver.get(f"https://{website_url}")


def test_switch_tab_windows():
    """Navigate between multiple tabs and windows."""
    with webdriver.Chrome() as driver:

        # Open website
        driver.get(f"https://amazon.com")
        print(f"Current page title: {driver.title}")
        print(f"Current page url: {driver.current_url}")
        last_window = driver.current_window_handle

        # Opens a new tab and switches to new tab
        website_url = input("website url: ")
        driver.switch_to.new_window('tab')
        driver.get(f"https://{website_url}")

        # To help the humans avoid nausea..
        time.sleep(2)

        # back, forward, and refresh commands are built-in
        driver.refresh()
        # driver.back()
        # driver.forward()

        # Switch back to last window
        time.sleep(2)
        print(f"Switching to old window: {last_window}")
        print(driver.window_handles)
        driver.switch_to.window(last_window)
        
        # Opens a new window/tab by user input
        website_url = input("website url: ")
        open_type = input("window or tab: ")
        
        driver.switch_to.new_window(open_type)
        driver.get(f"https://{website_url}")

        # The handles are just string identifiers with no useful information
        # we need to keep a secondary mapping of metadata
        print(driver.window_handles)
        for w in driver.window_handles:
            print(w, type(w))

        time.sleep(2)

        # Close the current tab (Must switch to another window manually)
        driver.close()
        if len(driver.window_handles) > 0:
            driver.switch_to.window(driver.window_handles[0])
        
        input("Press any key to exit")



if __name__ == "__main__":
    test_click_a_link()
    # test_browser_keep_open()
    # test_switch_tab_windows()
