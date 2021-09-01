import sys
import traceback

from higgins.actions import action_registry


def execute_action(action_class, action_params, automations, prompt_func=input):
    action = action_class.from_text(action_params["text"])
    #print(f"Text: {action_params['text']}")

    for param in action.params.values():
        if param.is_missing():
            # look up in database
            # prompt user for information
            param.value = prompt_func(f"{param.spec.question} ")
            # save in database

    #print(f"ActionAfterQuestions: {action}")

    # This could be moved inside run
    automations = action.add_automations(automations)

    action_result = None
    # Attempt to run the action (what params to pass to action??)
    try:
        action_result = action.run()  # Should we pass the previous action_result to the action?
        #print(f"ActionResult: {action_result}")
    except Exception as e:
        msg = "Uh oh! Failed to act on this: {}".format(str(e))
        traceback.print_exc(file=sys.stdout)
        print(msg)

    return action_result, automations


class Higgins:
    def __init__(self, prompt_func=input):
        self.prompt_func = prompt_func
        self.phrase_map = action_registry.load_action_phrase_map_from_modules("higgins/actions")
        self.automations = {}

    def parse(self, text: str):
        actions = action_registry.find_matching_actions(
            phrase=text, phrase_map=self.phrase_map
        )
        if len(actions) > 0:
            action_class, action_params = actions[0]  # We assume 1 matching action
            action_result, self.automations = execute_action(
                action_class, action_params, self.automations, self.prompt_func
            )
        else:
            return None
        return action_result


if __name__ == "__main__":
    H = Higgins()
    print(H.phrase_map)
    H.parse("send-msg text Mom with iMessage I'm coming home tonight")
    H.parse("send-msg text Mom I'm coming home tonight")
    H.parse("open-website apple.com")
    H.parse("open-website open the new yorker website")
