"""Module for shared NLP utilities.

Methods here should eventually be moved to specialist modules once common themes
can be identified across a number of utility methods. But this is a good starting place
for methods which don't have an obvious home yet.
"""

def normalize_text(text, method="naive"):
    if method == "naive":
        return normalize_text_naive(text)
    raise Exception(f"Method: '{method}' not supported!")


def normalize_text_naive(text):
    return text.lstrip().rstrip().lower()


def compute_levenshtein_distance(s1, s2):
    """Measure difference between 2 strings. 
    
    https://en.wikipedia.org/wiki/Levenshtein_distance.

    TODO: Replace with open-source implementation
    """
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]
