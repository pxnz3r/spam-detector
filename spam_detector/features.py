"""
features.py - turn the text of an email into the same 57 numbers Spambase
measured, so the trained models can score any pasted email.

The definitions follow the dataset's documentation:
    word frequency      = 100 * (times the word appears) / (words in the email)
                          where a word is a run of letters and digits,
    character frequency = 100 * (times the character appears) / (characters),
    capital runs        = runs of consecutive CAPITAL letters: their average
                          length, the longest one and the total count.
"""

import re

import pandas as pd

from spam_detector.spec import CAPITALS, CHARACTER_COLUMNS, CHARACTERS, WORD_COLUMNS, WORDS


def email_features(text):
    """
    The 57 Spambase measurements of one email.

    Input:
        text: the email text.
    Returns:
        A one-row DataFrame with the Spambase columns.
    """
    words = [word.lower() for word in re.findall(r"[A-Za-z0-9]+", text)]
    word_count = max(len(words), 1)
    character_count = max(len(text), 1)
    capital_runs = [len(run) for run in re.findall(r"[A-Z]+", text)]

    values = {}
    for column, word in zip(WORD_COLUMNS, WORDS):
        values[column] = 100 * words.count(word) / word_count
    for column, character in zip(CHARACTER_COLUMNS, CHARACTERS):
        values[column] = 100 * text.count(character) / character_count
    # Spambase never has a run shorter than 1, so an email with no capitals
    # gets the smallest values the dataset uses.
    values["capital_run_length_average"] = sum(capital_runs) / len(capital_runs) if capital_runs else 1.0
    values["capital_run_length_longest"] = max(capital_runs) if capital_runs else 1
    values["capital_run_length_total"] = sum(capital_runs) if capital_runs else 1
    return pd.DataFrame([values], columns=WORD_COLUMNS + CHARACTER_COLUMNS + CAPITALS)
