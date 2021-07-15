# automation.browser

This package uses libraries like Selenium to parse and manipulate the DOM. If Jarvis detects the active application is Chrome, then the ActionResolver will first search the library of supported browser Actions, before falling back to GUI Actions, etc. Example commands could include: “open tab”, “refresh page”, “switch to Amazon tab“, “click Best Sellers link”, etc.

Example layout

```txt
automation/
    browser/
        actions.py
        browser_controller.py
        selenium_controller.py
        playwright_controller.py
```
