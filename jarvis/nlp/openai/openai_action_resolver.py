import json
import logging
import os
from pathlib import Path
import re
import time
from typing import Dict, List, Tuple

from dotenv import load_dotenv
import openai

from jarvis.const import (
    ACTION_CHAIN_PATH,
    COMMON_ACTION_CHAINS,
    OPENAI_CACHE_DIR,
    AUTOMATION_PARAMS,
)
from jarvis.actions import ActionBase, ActionChain, ActionChainStep, action_registry, action_utils
from jarvis.actions.context import Context
from jarvis.automation.browser import create_browser_automation
from jarvis.automation.desktop import create_desktop_automation
from jarvis.nlp import nlp_utils

from jarvis.actions import action_registry
# Q: Refresh page
# A: RefreshPage
# Q: new tab
# A: OpenTab
# Q: close tab
# A: CloseTab
# Q: open browser
# A: OpenBrowser
# Q: open chrome
# A: OpenBrowser

WEB_NAVIGATION_PROMPT = """Q: Go to my amazon cart
A: ChangeURL `amazon.com` -> ClickLink `cart`
Q: open my github pull requests
A: ChangeURL `http://www.github.com` -> ClickLink `pull requests`
Q: search google for tents
A: ChangeURL `google.com` -> FindSearchBar -> TypeText `tents` -> PressKey `enter`
Q: search amazon for ski mask
A: ChangeURL `amazon.com` -> FindSearchBar -> TypeText `ski mask` -> PressKey `enter`
Q: open facebook marketplace
A: ChangeURL `www.facebook.com` -> ClickLink `marketplace`
Q: go to openai homepage
A: ChangeURL `open.ai`
Q: search twitter for $index mentions
A: ChangeURL `twitter.com` -> FindSearchBar -> TypeText `$index` -> PressKey `enter`
Q: open my youtube profile page
A: ChangeURL `www.youtube.com` -> ClickLink `profile`
Q: search bestbuy for smart tv
A: ChangeURL `www.bestbuy.com` -> FindSearchBar -> TypeText `smart tv` -> PressKey `enter`
Q: search for roger federer highlights on youtube
A: ChangeURL `www.youtube.com` -> FindSearchBar -> TypeText `roger federer` -> PressKey `enter`
Q: search twitter for latest #elonmusk tweets
A: ChangeURL `twitter.com` -> FindSearchBar -> TypeText `#elonmusk` -> PressKey `enter`
Q: search for backpacks at REI
A: ChangeURL `www.rei.com` -> FindSearchBar -> TypeText `backpacks` -> PressKey `enter`
Q: Login to my amazon account
A: ChangeURL `amazon.com` -> ClickLink `sign in`
Q: Sign out of my account
A: ClickLink `sign out`
Q: Logout
A: ClickLink `logout`
Q: Login to my new york times account
A: ChangeURL `www.nytimes.com` -> ClickLink `sign in`
Q: {question}
A:"""
WEB_NAVIGATION_PROMPT = """Q: Go to my amazon cart
A: ChangeURL `amazon.com` -> ClickLink `cart`
Q: open my github pull requests
A: ChangeURL `http://www.github.com` -> ClickLink `pull requests`
Q: search google for tents
A: ChangeURL `google.com` -> FindSearchBar -> TypeText `tents` -> PressKey `enter`
Q: search amazon for ski mask
A: ChangeURL `amazon.com` -> FindSearchBar -> TypeText `ski mask` -> PressKey `enter`
Q: open facebook marketplace
A: ChangeURL `www.facebook.com` -> ClickLink `marketplace`
Q: go to openai homepage
A: ChangeURL `open.ai`
Q: search twitter for $index mentions
A: ChangeURL `twitter.com` -> FindSearchBar -> TypeText `$index` -> PressKey `enter`
Q: Sign out of my account
A: ClickLink `sign out`
Q: Login to my new york times account
A: ChangeURL `www.nytimes.com` -> ClickLink `sign in`
Q: search for hard-shell rain jackets on ebay
A: ChangeURL `ebay.com` -> FindSearchBar -> TypeText `hard-shell rain jackets` -> PressKey `enter`
Q: open yahoo
A: ChangeURL `yahoo.com`
Q: {question}
A:"""
start_sequence = "\nA:"
restart_sequence = "\nQ:"

load_dotenv(".env.secret")

openai.api_key = os.getenv("OPENAI_API_KEY")

OPENAI_ENGINES = [
    "davinci",
    "curie",
    "davinci-instruct-beta",
]

FINED_TUNED_MODELS = [
    # fine-tuned on 11k bash commands from nl2bash (4 epochs, lr_multipler .1, bs 4)
    "curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-07-29-21-05-24",
    # fine-tuned on 11k bash commands from nl2bash (1 epoch1, lr_multipler .05, bs 8)
    "curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-07-29-23-29-05",
]
WEB_NAV_CACHE_FILE = os.path.join(OPENAI_CACHE_DIR, "web_nav.json")


def ask_web_navigation_model(
    cmd: str, engine="davinci", cache_path: str = WEB_NAV_CACHE_FILE
):
    # Check cache to avoid API calls
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path))

    if cmd not in cache:
        start = time.time()
        prompt = WEB_NAVIGATION_PROMPT.format(question=cmd)
        print(prompt)
        response = openai.Completion.create(
            engine=engine,
            model=None,
            prompt=prompt,
            temperature=0.2,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.0,
            stop=["\n"],
        )
        print(f"Time: {time.time() - start:.2f}")
        answer = response["choices"][0]["text"]
        cache[cmd] = {
            "cmd": cmd,
            "answer": answer,
            "response": response
        }
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        json.dump(cache, open(cache_path, "w"))
    else:
        print(f"Cache Hit. Loading {cmd} from cache")
        answer = cache[cmd]["answer"]
        response = cache[cmd]["response"]

    answer = answer.strip("Q:").strip()

    return answer, response


def parse_answer_to_actions(answer: str) -> Tuple[str, str]:
    # HACK: Only supports single parameter Actions
    # TODO: These Regex still capture badly formed strings
    PARAMS_REGEX = r"([a-zA-Z]+)+\s+`(.*)`"
    NO_PARAMS_REGEX = r"([a-zA-Z]+)"
    print(f"Parsing answer: {answer}")
    cmds = answer.split(" -> ")
    print(f"Commands: {cmds}")
    actions = []
    for cmd in cmds:
        cmd = cmd.strip()
        match_with_params = re.match(PARAMS_REGEX, cmd)
        if match_with_params and len(match_with_params.groups()) == 2:
            print("found match with params")
            class_name, param = match_with_params.groups()
            actions.append((class_name, param))
            continue

        match_no_params = re.match(NO_PARAMS_REGEX, cmd)
        if match_no_params and len(match_no_params.groups()) == 1:
            print("found match with no params")
            class_name = match_no_params.group(0)
            actions.append((class_name, None))
        else:
            raise Exception(
                f"Unabled to parse command: {cmd}, from answer: {answer}"
            )
    return actions


def convert_actions_to_chain(
    cmd: str,
    actions: List[Tuple[str, str]],
    action_classes: Dict[str, ActionBase],
) -> ActionChain:
    # HACK: Provide another way to alias classes.
    action_steps = []
    for class_name, param in actions:
        action_class = action_classes[class_name]
        class_path = action_utils.get_fully_qualified_class_name(action_class)
        param_names = action_utils.get_class_init_args(action_class)
        print(action_class, param_names)
        step = ActionChainStep(
            class_path=class_path,
            # HACK: we only support 1 param for Action
            params={name: param for name in param_names if name not in AUTOMATION_PARAMS}
        )
        action_steps.append(step)

    return ActionChain(
        name=cmd,
        phrases=[cmd],
        steps=action_steps,
    )


def infer_action_chain(cmd: str, action_classes: Dict[str, ActionBase]) -> ActionChain:
    # action_classes["ChangeURL"] = action_classes["ChangeURL"]
    answer, response = ask_web_navigation_model(cmd, engine="davinci")
    actions = parse_answer_to_actions(answer)
    for class_name, _ in actions:
        if class_name not in action_classes.keys():
            raise Exception(f"Action: {class_name} not found for answer: {answer}")
    chain = convert_actions_to_chain(cmd, actions, action_classes)
    return chain
