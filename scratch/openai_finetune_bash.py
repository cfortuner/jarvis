"""Preparing data for open.ai fine tuning

Follow the instructions here:
https://beta.openai.com/docs/guides/fine-tuning/preparing-your-dataset

Fine tuning the curie model on a 2MB dataset only took a few minutes.
"""

import jsonlines


NL_PATH = "/Users/brendan.fortuner/workplace/nl2bash/data/bash/all.nl.filtered"
CMD_PATH = "/Users/brendan.fortuner/workplace/nl2bash/data/bash/all.cm.filtered"


def create_bash_dataset(nl_path, cmd_path, outpath):
    nl_lines = open(nl_path)
    cmd_lines = open(cmd_path)

    examples = []
    for nl, cmd in zip(nl_lines, cmd_lines):
        examples.append({"prompt": f"{nl}", "completion": f"{cmd}"})

    print(examples[:10])
    with jsonlines.open(outpath, 'w') as writer:
        writer.write_all(examples)


def read_bash_dataset(dataset_path):
    with jsonlines.open(dataset_path) as reader:
        for obj in reader:
            print(obj)


if __name__ == "__main__":
    create_bash_dataset(
        nl_path=NL_PATH,
        cmd_path=CMD_PATH,
        outpath="openai_bash_dataset.jsonl"
    )
#     read_bash_dataset("dataset_prepared.jsonl")
