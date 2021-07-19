# actions (a.k.a. The Brain)

This package includes all the logic for mapping user inputs to actions. Inputs to this module include the transcribed voice command, the current application state (e.g. open windows, previous command), and the library of supported actions. These inputs are then combined to determine which Action to perform. For example, if the user says “switch tab”, it’s important to know the active window. If the window is Chrome, we can change tabs. If the application is VSCode, we may take a different action. 

Example layout

```txt
action_resolver/
    action_resolver.py
    context.py
    episode.py
```

Classes in `action_resolver`:

* `ActionResolver(context, command)`
* `ActionBase` implementation and shared code for all application-specific actions.
* `Episode` - the current “live” sequence of voice commands.
  * This can include one action, or a chain of commands.
  * The Episode ends after the action is performed, or the user says “quit” in the case of a streaming interaction.
* `Context` - the current state of the Jarvis application. Parameters include:
  * active_window
  * available_windows
  * current_episode
  * episode_history
  * desktop_automation_instance
  * browser_automation_instance
  