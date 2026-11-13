"""
data.py - the UCI Spambase data: 4,601 emails collected at Hewlett-Packard
Labs in 1999, 1,813 of them spam (Hopkins, Reeber, Forman and Suermondt;
UCI Machine Learning Repository, CC BY 4.0). Downloaded once into data/.

The emails themselves are not included, only the 57 numbers measured from
each, so features.py measures the same 57 numbers from any pasted text.
"""

import os
import zipfile

import pandas as pd

from pxlab.common import DATA_FOLDER, download_once
from spam_detector.spec import CAPITALS, CHARACTER_COLUMNS, WORD_COLUMNS

SPAMBASE_URL = "https://archive.ics.uci.edu/static/public/94/spambase.zip"


def load_spambase():
    """
    The Spambase table with named columns and a readable label.

    Returns:
        A DataFrame with the 57 measurements and "label" (spam or legitimate).
    """
    path = download_once(SPAMBASE_URL, os.path.join(DATA_FOLDER, "spambase.zip"))
    columns = WORD_COLUMNS + CHARACTER_COLUMNS + CAPITALS + ["is_spam"]
    with zipfile.ZipFile(path) as archive:
        frame = pd.read_csv(archive.open("spambase.data"), header=None, names=columns)
    frame["label"] = frame.pop("is_spam").map({1: "spam", 0: "legitimate"})
    return frame
