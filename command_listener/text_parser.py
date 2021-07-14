"""Methods for cleaning and parsing text strings.

TODO: Move this to a separate nlp module we can share.
"""

def normalize_text(text, method="naive"):
    if method == "naive":
        return normalize_text_naive(text)
    raise Exception(f"Method: '{method}' not supported!")


def normalize_text_naive(text):
    return text.lstrip().rstrip().lower()
