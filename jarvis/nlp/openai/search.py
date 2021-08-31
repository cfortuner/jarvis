import os

import openai


openai.api_key = os.getenv("OPENAI_API_KEY")


def find_similar_documents(documents, query):
    # Openai /search 
    # Run semantic search over list of strings
    resp = openai.Engine("davinci").search(
        search_model="davinci",
        documents=documents,
        query=query,
        max_rerank=5,
    )
    return resp


def ask_question(question, file_id=None, documents=None):
    # Openai /answers
    # Answer user query, doing a 2-stage search -> answer.
    # Pass file_id OR documents, not both
    # file_id: id of the uploaded document
    # documents: List of strings
    resp = openai.Answer.create(
        search_model="ada",
        model="curie",
        question=question,
        file=file_id,
        documents=documents,
        examples_context="Full Name: Stephanie Joy\nBirthday: December 18, 2000\nAge: 21\nEmail address: stephanie123@gmail.com",
        examples=[
            ["How old is Stephanie?", "21"],
            ["What is Stephanie's last name?", "Joy"],
            ["When was Stephanie born?", "December 18, 2000"],
        ],
        max_rerank=5,
        max_tokens=10,
        stop=["\n", "<|endoftext|>"]
    )
    return resp


def upload_document(fpath, purpose="search"):  # or "answers"
    """Upload document to OpenAI servers.

    # List files: openai api files.list
    # Upload files: openai api files.create -f path_to_file -p [answers|search]
    # OAR.upload_document(data_fpath, purpose="answers")
    # print(openai.File.list())

    Args:
        fpath ([type]): [description]
        purpose (str, optional): [description]. Defaults to "search".
    """
    openai.File.create(file=open(fpath), purpose=purpose)


if __name__ == "__main__":
    resp = ask_question(
        question="Who is Brendan dating?",
        documents=[
            "Brendan Fortuner was born on February 10, 1990. He is 31 years old. His email address address is bfortuner@gmail.com. His phone number is 860-459-8424. His Amazon password is MyPassword567. His girlfriend is Jackie First.",
            "David Brewster was born on March 1, 2005. He is 15 years old. His email address is dbrewster@gmail.com. His Amazon password is BD17826. His Facebook username is dboy253.",
        ]
    )
    print(resp)

    resp = ask_question(
        question="What is Colin's discord alias?",
        file_id="file-u7jUNn5dIIvV4cVMMeROSyRI",
    )
    print(resp)
