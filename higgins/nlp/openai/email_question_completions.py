import copy
import math
import os
import pprint
import random
from typing import Any, Dict, List

import openai

from higgins.automation.email import email_utils
from higgins.nlp import nlp_utils

from . import caching


openai.api_key = os.getenv("OPENAI_API_KEY")

tokenizer = nlp_utils.get_tokenizer()

pp = pprint.PrettyPrinter(indent=2)


def build_email_question_completion_prompt(
    user_email: Dict,
    user_question: str,
    prompt_emails: List[Dict],
    task_description: str = None,
) -> str:
    prompt = ""
    if task_description is not None:
        prompt += f"{task_description}"

    for example in prompt_emails:
        prompt += f"\n\nEMAIL\n{example['plain']}\n"
        prompt += "\nQUESTIONS"

        for question, answer in example["model_labels"]["questions"]:
            prompt += f"\nQ: {question}"
            prompt += f"\nA: {answer} <<END>>"

    prompt += "\n\nEMAIL\n{data}\n".format(data=user_email["plain"])
    prompt += "\nQUESTIONS"
    prompt += "\nQ: {question}".format(question=user_question)
    prompt += "\nA:"
    return prompt


def email_question_completion(
    user_email: Dict,
    user_question: str,
    prompt_emails: List[Dict],
    completion_tokens: int = 30,
    task_description: str = "Answer questions about the following emails",
    engine="davinci",
    cache: Any = None,
):
    num_tokens = 100000
    i = 0
    while num_tokens > 2040 - completion_tokens:
        prompt = build_email_question_completion_prompt(
            user_email=user_email,
            user_question=user_question,
            prompt_emails=prompt_emails[i:],
        )
        num_tokens = nlp_utils.get_num_tokens(prompt, tokenizer)
        i += 1
        print(f"prompt tokens: {num_tokens}")
    print(prompt)
    cache = cache if cache is not None else caching.get_default_cache()
    cache_key = nlp_utils.hash_normalized_text(prompt)
    if cache_key not in cache:
        response = openai.Completion.create(
            engine=engine,
            model=None,
            prompt=prompt,
            temperature=.1,
            max_tokens=completion_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["<<END>>"],
        )
        answer = response["choices"][0]["text"].strip()
        cache.add(
            key=cache_key,
            value={
                "question": user_question,
                "data": user_email,
                "answer": answer,
                "response": response
            }
        )
    else:
        answer = cache[cache_key]["answer"]
        response = cache[cache_key]["response"]

    return answer


def make_email_false_positive_questions(
    emails: List[Dict], questions: List[str]
):
    """Create new false positive emails with questions that have ??? answer."""
    emails = copy.deepcopy(emails)
    shuffled = random.sample(questions, len(questions))
    for fp in emails:
        fp["model_labels"]["questions"] = [
            (shuffled[0], "???")
        ]
    return emails


def make_train_test_split(examples: List[Dict], sort_key: str, train_pct: float = .7):
    examples = sorted(examples, key=lambda dct: dct[sort_key])
    num_examples = len(examples)
    train_count = math.floor(num_examples * train_pct)
    return examples[:train_count], examples[train_count:]


def extract_existing_train_test_split(examples: List[Dict]):
    train = []
    test = []
    for example in examples:
        if example["model_labels"].get("split") == "train":
            train.append(example)
        else:
            test.append(example)
    return train, test


def test_email_question_completion():
    # Assumption is that the 
    questions = [
        "What is the verification code?",
        "Get verification code",
        "Get security code",
    ]
    example_emails = email_utils.search_local_emails(
        categories=["verification_code"]
    )
    # train_emails, test_emails = make_train_test_split(
    #     example_emails, sort_key="email_id"
    # )
    train_emails, test_emails = extract_existing_train_test_split(example_emails)

    false_positives = make_email_false_positive_questions(
        emails=email_utils.search_local_emails(categories=["personal"])[:2],
        questions=questions
    )
    false_positives += make_email_false_positive_questions(
        emails=email_utils.search_local_emails(categories=["recruiting"])[:2],
        questions=questions
    )
    random.shuffle(false_positives)
    train_emails += false_positives[:2]
    test_emails += false_positives[2:4]

    random.shuffle(train_emails)
    print(f"Train: {len(train_emails)} Test: {len(test_emails)}")

    for email in train_emails + test_emails:
        num_tokens = nlp_utils.get_num_tokens(email['plain'], tokenizer)
        print(f"Num tokens before cleaning: {num_tokens}")
        email['plain'] = email_utils.remove_whitespace(email['plain'])
        num_tokens = nlp_utils.get_num_tokens(email['plain'], tokenizer)
        print(f"Num tokens after cleaning: {num_tokens}")
        email["plain"] = nlp_utils.trim_tokens(email["plain"], max_tokens=500, tokenizer=tokenizer)
        print(f"Email_id: {email['email_id']} Subject: {email['subject']} num_tokens: {num_tokens}")

    failed = 0
    for example in test_emails:
        for question, expected_answer in example["model_labels"]["questions"]:
            answer = email_question_completion(
                user_email=example,
                user_question=random.choice(questions),
                prompt_emails=train_emails,
                completion_tokens=10,
            )
            if answer != expected_answer:
                print("Answers below do not match ----")
                print(example["email_id"], example["model_labels"]["categories"])
                print(f"Q: {question}\nA: {answer}\nE: {expected_answer}")
                failed += 1
    print(f"Failed: {failed}/{len(test_emails)}")


def test_email_question_completion_flights():
    # Assumption is that the 
    questions = [
        "Extract flight details",
        "Get flight details",
    ]
    example_emails = email_utils.search_local_emails(
        categories=["flights", "flights_false_positive"], match_all=False
    )
    # train_emails, test_emails = make_train_test_split(
    #     example_emails, sort_key="email_id"
    # )
    train_emails, test_emails = extract_existing_train_test_split(example_emails)

    # false_positives = make_email_false_positive_questions(
    #     emails=email_utils.search_local_emails(categories=["personal"])[:2],
    #     questions=questions
    # )
    # false_positives += make_email_false_positive_questions(
    #     emails=email_utils.search_local_emails(categories=["recruiting"])[:2],
    #     questions=questions
    # )
    # random.shuffle(false_positives)
    # train_emails += false_positives[:1]
    # test_emails += false_positives[1:2]

    random.shuffle(train_emails)
    train_emails = random.sample(train_emails, 2)
    print(f"Train: {len(train_emails)} Test: {len(test_emails)}")

    for email in train_emails + test_emails:
        num_tokens = nlp_utils.get_num_tokens(email['plain'], tokenizer)
        print(f"Num tokens before cleaning: {num_tokens}")
        email['plain'] = email_utils.remove_whitespace(email['plain'])
        num_tokens = nlp_utils.get_num_tokens(email['plain'], tokenizer)
        print(f"Num tokens after cleaning: {num_tokens}")
        email["plain"] = nlp_utils.trim_tokens(email["plain"], max_tokens=500, tokenizer=tokenizer)
        print(f"Email_id: {email['email_id']} Subject: {email['subject']} num_tokens: {num_tokens}")

    failed = 0
    for example in test_emails:
        for _, expected_answer in example["model_labels"].get("questions", [(None, {})]):
            answer = email_question_completion(
                user_email=example,
                user_question="flight details",
                prompt_emails=train_emails,
                completion_tokens=200,
                task_description="Extract flight details from the following emails. Input '???' to indicate missing or unknown fields."
            )
            # if answer != expected_answer:
            #     print("Answers below do not match ----")
            print(example["email_id"], example["model_labels"]["categories"])
            pp.pprint(answer)
            failed += 1
    print(f"Failed: {failed}/{len(test_emails)}")


if __name__ == "__main__":
    test_email_question_completion()
    # test_email_question_completion_flights()
