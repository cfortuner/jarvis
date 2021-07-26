# automation.web

This package allows users to contribute Actions specific to certain websites. If the ActionResolver detects the active tab is “Gmail”, then it will search the gmail package for commands unique to Gmail, before falling back to Browser Actions and then Desktop actions etc. Example commands for Gmail could include: “open email”, “mark as read”, etc. This package can also include code for calling REST APIs, if available. Gmail and Twitter both have developer APIs, which may be more convenient and reliable for certain actions.

Example Layout

```txt
automation/
    web/
        gmail/
            Actions.py
            Gmail_controller.py ← Navigating the Desktop (possibly not required)
            Gmail_client.py  ← REST API
        amazon/
            actions.py
```
