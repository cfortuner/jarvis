"""Text2Bash commands

OpenAI documentation:
https://beta.openai.com/docs

12k Dataset from nl2bash for fine-tuning
https://github.com/TellinaTool/nl2bash

The default curie/davinci models both perform well out-of-the-box. After fine-tuning curie on the
nl2bash dataset, I started to get very verbose commands with logs unnecessary arguments. I think
this is because that dataset has very complex bash commands, with very explicit instructions.

Here is an example from the dataset:

    "prompt":"Find all files in current directory with the extension \".ext\" and remove all \"^M\" in those files",
    "completion":" find $(pwd) -type f -name \"*.ext\" | while read file; do sed -e 's\/^M\/\/g' -i \"$file\"; done;"

After fine-tuning, we start to see unnecessarily complex commands for simple tasks:

```
Prompt: Search for keyword brendan in log.text file
Curie: grep -i brendan log.text
FineTune: find /var/log/syslog -type f -name "log.text" -exec grep brendan {} \;

Prompt: How much disk space do I have left?
Curie: df -h
FineTune: df -h | tail -n 1 | tr -s ' ' | cut -d' ' -f1 | tail -n 1
```

Inference speed varies, but super duper, rough approximation:
Davinci: 600ms
Curie: 250ms
Curie(FineTune): 400ms
"""

import argparse
import json
import os
import time

from dotenv import load_dotenv
import openai

load_dotenv(".env.secret")


openai.api_key = os.getenv("OPENAI_API_KEY")


def text2bash_with_examples(text, engine=None, model=None):
    prompt = """Input: List files
    Output: ls -l

    Input: Count files in directory
    Output: ls -l | wc -l

    Input: Disk space used by home directory
    Output: du ~

    Input: Delete the models subdirectory
    Output: rm -r ./models

    Input: Checkout branch homerun
    Output: git checkout homerun"""

    template = f"""

    Input: {text}
    Output:"""
    assert not (model is None and engine is None), "must provide either fine-tuned model or engine"

    prompt += template

    response = openai.Completion.create(
        engine=engine,
        model=model,
        prompt=prompt,
        temperature=0.0,
        max_tokens=100,
        # top_p=1.0,
        # frequency_penalty=0.2,
        # presence_penalty=0.0,
        stop=["\n"]
    )
    return response


def text2bash(text, engine=None, model=None):
    prompt = f"""{text}\n\n\n###\n\n"""
    assert not (model is None and engine is None), "must provide either fine-tuned model or engine"

    response = openai.Completion.create(
        engine=engine,
        model=model,
        prompt=prompt,
        temperature=0.0,
        max_tokens=100,
        # top_p=1.0,
        # frequency_penalty=0.2,
        # presence_penalty=0.0,
        stop=["+++"]
    )
    return response


engines = [
    "davinci",
    "curie",
    "davinci-instruct-beta",
]

models = [
    # fine-tuned on 11k bash commands from nl2bash (4 epochs, lr_multipler .1, bs 4)
    "curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-07-29-21-05-24",
    # fine-tuned on 11k bash commands from nl2bash (1 epoch1, lr_multipler .05, bs 8)
    "curie:ft-user-7rs1dte2m2824vd5bddi84s8-2021-07-29-23-29-05",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", help="default openai engines")
    parser.add_argument("--model", help="id of custom fine-tuned model")
    parser.add_argument("--cmd", help="natural language bash command")
    args = parser.parse_args()

    cache_file = f"openai_cache_{args.model or args.engine}.json"
    cache = {}
    if os.path.exists(cache_file):
        cache = json.load(open(cache_file))

    examples = []
    if args.cmd is not None:
        examples += [args.cmd]
    else:
        # Many of these are ambiguous, with multiple correct interpretations
        # or just underspecified.
        examples += [
            "Search for keyword brendan in log.text file",
            "Show top 5 processes by CPU usage",
            "upload files larger than 1MB with git lfs",
            "show top 3 largest files in current directory in megabytes",
            "show current directory size in megabytes",
            "Display differences between file1 and file2 side-by-side.",
            "Find *.dat files recursively in the current directory.",
            "count number of lines in readme.md",
            "Calculate the total size of all *.py files in the directory tree",
            "Copy all directories recursively from source/ to destination/",
            "Create a tarball 'files.tar.gz' containing all regular files under current directory tree",
            "Find all .txt files in current directory except README.md",
            "Find all files in current directory that were modified less than 1 day ago",
            "checkout git branch bfortuner/jarvis",
            "create new git branch hari/jarvis",
            "remove all *.pyc files recursively in current directory",
            "remove all __pycache__ directories recursively",
            "print all environment variables with keyword OPENAI",
            "how much disk space do I have left?"
        ]

    for i, example in enumerate(examples):
        if example not in cache:
            start = time.time()

            if args.engine is not None:
                resp = text2bash_with_examples(example, args.engine, args.model)
            else:
                resp = text2bash(example, args.engine, args.model)

            cache[example] = {
                "input": example,
                "output": resp["choices"][0]["text"],
                "resp": resp,
            }
            end = time.time()
            print(f"Time: {end - start:.2f}")
        else:
            resp = cache[example]

        print(f"[{i}] Input: {cache[example]['input']}\n[{i}] Output:{cache[example]['output']}""")

        json.dump(cache, open(cache_file, "w"))
