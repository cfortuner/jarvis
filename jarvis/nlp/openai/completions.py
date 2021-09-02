# Fine-tune Curie on https://github.com/daveshap/NLCA_Question_Generator
# model_id = ft-YMaOF6HNpubqL2FsWM0yAlGt

import json
import os
from pathlib import Path
import re
import time

import openai

from jarvis.nlp.openai import OPENAI_CACHE_DIR
from jarvis.nlp import nlp_utils

from higgins import const


COMPLETION_CACHE_FILE = os.path.join(OPENAI_CACHE_DIR, "completions.json")

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_IMPORTANT = """Write a list of the most important and salient questions an observer would ask about the following passage:

PASSAGE:
{text}
END PASSAGE

IMPORTANT OBSERVER QUESTIONS:
-"""
PROMPT_PROCEDURAL = """Write a list of procedural and task-oriented questions about the following passage:

PASSAGE:
{text}
END PASSAGE

PROCEDURAL AND TASK-ORIENTED QUESTIONS:
-"""
PROMPT_TEXT_MESSAGE = """Write a list of clarifying questions about the following message:

MESSAGE:
{text}
END MESSAGE

LIST OF CLARIFYING QUESTIONS:
-"""


# Trained to write clarifying questions given some text, paragraph, dialog..
ft_model_id = "curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-08-30-21-28-18"
# openai api completions.create -m curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-08-30-21-28-18 -p <YOUR_PROMPT>


def generate_questions_finetune(
    prompt, model, temp=0.5, top_p=0.95, tokens=60, freq_pen=0.2, pres_pen=0.2, stop=['<<END>>']
):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temp,
        max_tokens=tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop)
    return response['choices'][0]['text'].strip().splitlines()


def generate_questions_base(prompt, engine, temp=0.9, top_p=0.95, tokens=200, freq_pen=0.5, pres_pen=0.5, stop=['\n\n']):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temp,
        max_tokens=tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop)
    text = response['choices'][0]['text'].strip().split("\n-")
    return text


def generate_questions(text: str, mode="finetune"):
    if mode == "finetune":
        prompt = f"{text}\nQUESTIONS:"
        print(f"prompt: {prompt}")
        questions = generate_questions_finetune(prompt, ft_model_id)
    elif mode == "important":
        prompt = PROMPT_IMPORTANT.format(text=text)
        questions = generate_questions_base(prompt, engine="davinci-instruct-beta")
    elif mode == "procedural":
        prompt = PROMPT_TEXT_MESSAGE.format(text=text)
        questions = generate_questions_base(prompt, engine="davinci-instruct-beta")
    return questions


def first_person_to_third_person(text, model="davinci"):
    PROMPT = f"""First-person to third-person

    Input: I decided to make a movie about Ada Lovelace.
    Output: He decided to make a movie about Ada Lovelace.

    Input: My biggest fear was that I wasn't able to write the story adequately.
    Output: His biggest fear was that he wouldn't be able to write the story adequately.

    Input: {text}
    Output:"""
    response = openai.Completion.create(
        engine=model,
        prompt=PROMPT,
        temperature=0.3,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )
    print(response)
    text = response['choices'][0]['text'].strip()
    return text


def third_person_to_second_person(text, model="davinci"):
    PROMPT = f"""Third-person to second-person

    Input: Brendan decided to make a movie about Ada Lovelace.
    Output: You decided to make a movie about Ada Lovelace.

    Input: What does Janelle want to do with her life?
    Output: What do you want to do with your life?

    Input: His biggest fear was that he wouldn't be able to write the story adequately.
    Output: Your biggest fear was that you wouldn't be able to write the story adequately.

    Input: {text}
    Output:"""
    response = openai.Completion.create(
        engine=model,
        prompt=PROMPT,
        temperature=0.3,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )
    text = response['choices'][0]['text'].strip()
    return text


def open_ended_chat(chat_history, username=const.USERNAME, agent_name=const.AGENT_NAME, engine="davinci"):
    prompt = f"""The following is a chat between {username} and his personal assistant {agent_name}. {agent_name} only asks {username} clarifying questions to better understand {username}'s intent.
    \n{chat_history}\n{agent_name}:"""
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=["\n", " Higgins:"]
    )
    return response.choices[0]["text"].strip()


def summarize_model(prompt: str, engine="davinci"):
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=0.2,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.2,
        presence_penalty=0.0,
    )
    answer = response["choices"][0]["text"]
    return answer


def send_message_completion(
    cmd: str, engine="davinci", cache_path: str = COMPLETION_CACHE_FILE
):
    prompt = f"""Convert the following text into commands:

    Q: Text mom I love her
    A: `SendMessage` PARAMS to=>mom ### body=>I Love her ### application=>??? <<END>>
    Q: text message steve and ask if he's coming to the meeting
    A: `SendMessage` PARAMS to=>steve ### body=>are you coming to the meeting? ### application=>??? <<END>>
    Q: msg Jackie and let her know I'll be home by 10 tonight
    A: `SendMessage` PARAMS to=>Jackie ### body=>I'll be home by 10pm ### application=>??? <<END>>
    Q: text Colin on Facebook Messenger and ask him if he's free for tennis tomorrow
    A: `SendMessage` PARAMS to=>Colin ### body=>Are you free for tennis tomorrow? ### application=>Facebook Messenger <<END>>
    Q: Want to hang out tonight?
    A: `SendMessage` PARAMS to=>??? ### body=>Want to hang out tonight? ### application=>??? <<END>>
    Q: Reply to Sam Fortuner on WhatsApp
    A: `SendMessage` PARAMS to=>Sam Fortuner ### body=>??? ### application=>WhatsApp <<END>>
    Q: slack Sean Bean and tell him I'm running late to the meeting
    A: `SendMessage` PARAMS to=>Sean Bean ### body=>Hey, running late to our meeting ### application=>Slack <<END>>
    Q: email David
    A: `SendMessage` PARAMS to=>David ### body=>??? ### application=>email <<END>>
    Q: Let Hari know I just pushed my latest changes to the github repo
    A: `SendMessage` PARAMS to=>Hari ### body=>I pushed my latest changes to the repo ### application=>??? <<END>>
    Q: tell Dad I'll see him next month
    A: `SendMessage` PARAMS to=>Dad ### body=>See you next month ### application=>??? <<END>>
    Q: Reply Sounds fun!
    A: `SendMessage` PARAMS to=>??? ### body=>Sounds fun! ### application=>??? <<END>>
    Q: {cmd}
    A:"""

    # Check cache to avoid API calls
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path))

    cache_string = nlp_utils.hash_normalized_text(prompt)
    if cache_string not in cache:
        start = time.time()
        response = openai.Completion.create(
            engine=engine,
            model=None,
            prompt=prompt,
            temperature=0.2,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.0,
            stop=["<<END>>"],
        )
        # print(f"Time: {time.time() - start:.2f}")
        answer = response["choices"][0]["text"]
        cache[cache_string] = {
            "cmd": cmd,
            "answer": answer,
            "response": response
        }
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        json.dump(cache, open(cache_path, "w"))
    else:
        answer = cache[cache_string]["answer"]
        response = cache[cache_string]["response"]

    answer = answer.strip("Q:").strip()
    return answer


def open_website_completion(
    cmd: str, engine="davinci", cache_path: str = COMPLETION_CACHE_FILE
):
    prompt = f"""Convert the following text into commands:

    Q: goto amazon.com
    A: `OpenWebsite` PARAMS website=>amazon.com <<END>>
    Q: open Target website
    A: `OpenWebsite` PARAMS website=>target.com <<END>>
    Q: leetcode.com
    A: `OpenWebsite` PARAMS website=>leetcode.com <<END>>
    Q: goto Ebay
    A: `OpenWebsite` PARAMS website=>ebay.com <<END>>
    Q: Open the openai website
    A: `OpenWebsite` PARAMS website=>open.ai <<END>>
    Q: go to facebook homepage
    A: `OpenWebsite` PARAMS website=>facebook.com <<END>>
    Q: go to website
    A: `OpenWebsite` PARAMS website=>??? <<END>>
    Q: Open wikipedia
    A: `OpenWebsite` PARAMS website=>wikipedia.org <<END>>
    Q: Open the New York Times website
    A: `OpenWebsite` PARAMS website=>nyt.com <<END>>
    Q: {cmd}
    A:"""

    # Check cache to avoid API calls
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path))

    cache_string = nlp_utils.hash_normalized_text(prompt)
    if cache_string not in cache:
        start = time.time()
        response = openai.Completion.create(
            engine=engine,
            model=None,
            prompt=prompt,
            temperature=0.2,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.0,
            stop=["<<END>>"],
        )
        # print(f"Time: {time.time() - start:.2f}")
        answer = response["choices"][0]["text"]
        cache[cache_string] = {
            "cmd": cmd,
            "answer": answer,
            "response": response
        }
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        json.dump(cache, open(cache_path, "w"))
    else:
        answer = cache[cache_string]["answer"]
        response = cache[cache_string]["response"]

    answer = answer.strip("Q:").strip()
    return answer


def web_navigation_completion(
    cmd: str, engine="davinci", cache_path: str = COMPLETION_CACHE_FILE
):
    prompt = f"""Convert the following text into commands:

    Q: Go to my amazon cart
    A: `OpenWebsite` PARAMS website=>www.amazon.com -> `ClickLink` PARAMS link_text=>cart <<END>>
    Q: open my github pull requests
    A: `OpenWebsite` PARAMS website=>www.github.com -> `ClickLink` PARAMS link_text=>pull requests <<END>>
    Q: search wikipedia for grizzly bears
    A: `OpenWebsite` PARAMS website=>www.wikipedia.org -> `SearchOnWebsite` PARAMS text=>grizzly bears ### filter=>??? <<END>>
    Q: search amazon for ski mask filter for Prime only
    A: `OpenWebsite` PARAMS website=>www.amazon.com -> `SearchOnWebsite` PARAMS text=>ski mask ### filter=>Prime <<END>>
    Q: go to openai homepage
    A: `OpenWebsite` PARAMS website=>www.open.ai <<END>>
    Q: leetcode.com
    A: `OpenWebsite` PARAMS website=>leetcode.com <<END>>
    Q: search twitter for $index mentions
    A: `OpenWebsite` PARAMS website=>www.twitter.com -> `SearchOnWebsite` PARAMS text=>$index ### filter=>??? <<END>>
    Q: Sign out of my account
    A: `SignOut` PARAMS website=>??? <<END>>
    Q: Sign out of my Amazon account
    A: `SignOut` PARAMS website=>www.amazon.com <<END>>
    Q: Login to my new york times account
    A: `OpenWebsite` PARAMS website=>www.nyt.com -> `LogIn` PARAMS website=>??? ### username=>??? ### password=>??? <<END>>
    Q: search for hard-shell rain jackets on ebay
    A: `OpenWebsite` PARAMS website=>www.ebay.com -> `SearchOnWebsite` PARAMS text=>hard-shell rain jackets ### filter=>??? <<END>>
    Q: open walmart
    A: `OpenWebsite` PARAMS website=>www.walmart.com <<END>>
    Q: search wikipedia
    A: `OpenWebsite` PARAMS website=>www.wikipedia.org -> `SearchOnWebsite` PARAMS text=>??? ### filter=>??? <<END>>
    Q: log out
    A: `SignOut` PARAMS website=>??? <<END>>
    Q: log in
    A: `LogIn` PARAMS website=>??? ### username=>??? password=>???<<END>>
    Q: open facebook marketplace
    A: `OpenWebsite` PARAMS website=>www.facebook.com -> `ClickLink` PARAMS link_text=>marketplace <<END>>
    Q: Go to circle ci and login with the username bfortuner
    A: `LogIn` PARAMS website=>www.circleci.com ### username=>bfortuner ### password=>??? <<END>>
    Q: {cmd}
    A:"""

    # Check cache to avoid API calls
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path))

    cache_string = nlp_utils.hash_normalized_text(prompt)
    if cache_string not in cache:
        start = time.time()
        response = openai.Completion.create(
            engine=engine,
            model=None,
            prompt=prompt,
            temperature=0.2,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.0,
            stop=["<<END>>"],
        )
        # print(f"Time: {time.time() - start:.2f}")
        answer = response["choices"][0]["text"]
        cache[cache_string] = {
            "cmd": cmd,
            "answer": answer,
            "response": response
        }
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        json.dump(cache, open(cache_path, "w"))
    else:
        answer = cache[cache_string]["answer"]
        response = cache[cache_string]["response"]

    answer = answer.strip("Q:").strip()
    return answer


def extract_params_from_string(param_string):
    # to:"mom" body:"I Love her" application:None
    # out: {"to": "mom", "body":"I love here", "application": None}
    params = param_string.strip().split("###")
    out = {}
    for param in params:
        argument, value = param.strip().split("=>")
        out[argument.strip()] = value.strip()
    return out


def convert_answer_to_intent(answer: str):
    # answer: `SendMessage` to:"mom" body:"I Love her" application:None <<END>>
    if const.DEBUG_MODE:
        print(f"Answer: {answer}")

    PARAMS_REGEX = r"`([a-zA-Z]+)`\sPARAMS\s(.*)"
    NO_PARAMS_REGEX = r"`([a-zA-Z]+)`"
    # print(f"Parsing answer: {answer}")
    cmds = answer.split(" -> ")
    intent = []
    for cmd in cmds:
        cmd = cmd.strip()
        match_with_params = re.match(PARAMS_REGEX, cmd)
        if match_with_params and len(match_with_params.groups()) == 2:
            class_name, param_string = match_with_params.groups()
            intent.append({
                "action": class_name,
                "params": extract_params_from_string(param_string)
            })
            continue

        match_no_params = re.match(NO_PARAMS_REGEX, cmd)
        if match_no_params and len(match_no_params.groups()) == 1:
            class_name = match_no_params.group(0)
            intent.append({"action": class_name, "params": None})
        else:
            raise Exception(
                f"Unabled to parse command: {cmd}, from answer: {answer}"
            )
    if const.DEBUG_MODE:
        print(f"Intent: {intent}")
    return intent


if __name__ == "__main__":
    # # Send message completions
    # examples = [
    #     "message Liam Briggs and see if he wants to get together",
    #     "send an email to Xin letting him know I'm leaving Cruise soon",
    #     "whatsapp Kabir how are you doing?",
    #     "This is something isn't it",
    #     "Can you ping Joe Boring and say thanks",
    #     "msg Stew on Slack are you coming to Burning man?",
    #     "text Colin on iMessage and see if he's still going to the store",
    # ]
    # for text in examples:
    #     answer = send_message_completion(text)
    #     intent = convert_answer_to_intent(answer)
    #     print(f"Q: {text}\nA: {answer}\nI: {intent}")

    examples = [
        "sign in to my yahoo account",
        "go to target.com",
        "find me airpods on ebay",
        "search wikipedia",
        "search google",
        "search bing for Harley-Davidson motorcycles",
    ]
    for text in examples:
        answer = web_navigation_completion(text)
        intent = convert_answer_to_intent(answer)
        print(f"Q: {text}\nA: {answer}\nI: {intent}")
