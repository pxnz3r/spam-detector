"""
spec.py - the Spambase dataset and the models trained on it.

Every email is described by 57 numbers: how often 48 particular words and
6 particular characters appear, and how long its runs of CAPITAL LETTERS
are. The pxlab engine reads this dictionary: which column to predict, which
columns are inputs, readable names, and the models with the settings that
grid search tries.
"""

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB

from pxlab.common import RANDOM_STATE

WORDS = [
    "make", "address", "all", "3d", "our", "over", "remove", "internet", "order", "mail", "receive", "will",
    "people", "report", "addresses", "free", "business", "email", "you", "credit", "your", "font", "000",
    "money", "hp", "hpl", "george", "650", "lab", "labs", "telnet", "857", "data", "415", "85", "technology",
    "1999", "parts", "pm", "direct", "cs", "meeting", "original", "project", "re", "edu", "table", "conference",
]  # fmt: skip
CHARACTERS = [";", "(", "[", "!", "$", "#"]
CAPITALS = ["capital_run_length_average", "capital_run_length_longest", "capital_run_length_total"]

WORD_COLUMNS = ["word_freq_" + word for word in WORDS]
CHARACTER_COLUMNS = ["char_freq_" + character for character in CHARACTERS]


def readable_labels():
    """
    Readable names for all 57 columns, e.g. word_freq_free -> "free" (% of words).

    Returns:
        A dictionary column -> label.
    """
    labels = {column: f'"{word}" (% of words)' for column, word in zip(WORD_COLUMNS, WORDS)}
    labels.update(
        {column: f'"{character}" (% of characters)' for column, character in zip(CHARACTER_COLUMNS, CHARACTERS)}
    )
    labels.update(
        {
            "capital_run_length_average": "Average run of capitals",
            "capital_run_length_longest": "Longest run of capitals",
            "capital_run_length_total": "Total capital letters",
            "label": "Email",
        }
    )
    return labels


def naive_bayes_grid():
    """
    The smoothing values tried for Multinomial and Bernoulli Naive Bayes.

    Smoothing (alpha) pretends every word was seen a few extra times in
    each class, so a word never seen in spam doesn't make spam impossible.

    Returns:
        A grid dictionary.
    """
    return {"alpha": [0.01, 0.1, 0.5, 1.0]}


SPAM_SPEC = {
    "name": "Spambase",
    "folder": "spam",
    "task": "classification",
    "target": "label",
    "positive_class": "spam",
    "numeric": WORD_COLUMNS + CHARACTER_COLUMNS + CAPITALS,
    "categorical": [],
    "labels": readable_labels(),
    "test_size": 0.25,
    "scoring": "f1",
    # Sending a real email to the spam folder (false positive) is assumed
    # five times as bad as letting one spam through. The cut-off is tuned for it.
    "error_costs": {
        "false_positive": 5,
        "false_negative": 1,
        "reason": "A real email lost in the spam folder can be missed for good; a spam that gets through is deleted "
        "in a second.",
    },
    "models": {
        "Bernoulli Naive Bayes": {
            "estimator": BernoulliNB(binarize=0.0),
            "grid": naive_bayes_grid(),
            "scale": False,
            "role": "Naive Bayes: word present or not",
        },
        "Multinomial Naive Bayes": {
            "estimator": MultinomialNB(),
            "grid": naive_bayes_grid(),
            "scale": False,
            "role": "Naive Bayes: how often each word appears",
        },
        "Gaussian Naive Bayes": {
            "estimator": GaussianNB(),
            "grid": {},
            "scale": False,
            "role": "Naive Bayes: bell curve per input",
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=1),
            "grid": {"min_samples_leaf": [1, 3]},
            "scale": False,
            "role": "Benchmark beyond the course",
        },
        "Always legitimate": {
            "estimator": DummyClassifier(strategy="most_frequent"),
            "grid": {},
            "scale": False,
            "role": "Baseline",
        },
    },
}
