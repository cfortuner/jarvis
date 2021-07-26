# automation.apps

This package includes native integrations with desktop and mobile apps. In many cases, it’s simplest to call a native API, rather than parsing the GUI with OCR and using keyboard/mouse commands. For example, the Calendar App has an API we can call to create events. This will be easier than trying to manipulate the Calendar using raw Mouse + Keyboard commands.

Example layout:

```txt
automation/
    apps/
        xp/
            VSCode/
                actions.py
                controller.py
            Spotify/
                actions.py
                controller.py
        mac/
            Calendar/
                actions.py
                controller.py
            Messages
    actions.py
    controller.py
        ubuntu/
            ExampleApp/
            ...
```

Example of website specific commands (We can build on Caster)
https://caster.readthedocs.io/en/latest/readthedocs/Caster_Commands/Application_Commands_Quick_Reference/#visual-studio-code