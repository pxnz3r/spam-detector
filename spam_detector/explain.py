"""
explain.py - what Bernoulli Naive Bayes learned, and why it called one
email spam.

Naive Bayes keeps, for every input and class, the chance that the input is
present: for example P("free" appears | spam). To classify an email it
multiplies these chances (adds their logarithms) for everything present or
absent, and picks the class with the bigger total. "Naive" because it
treats every word as independent of the others, which is false but works.

The evidence of one input is log P(seen | spam) - log P(seen | legitimate):
positive pushes towards spam, negative towards legitimate.
"""

import numpy as np
import pandas as pd

from pxlab.common import save_table
from pxlab.tabular.data import label_for


def presence_chances(pipeline):
    """
    The chance each input is present, per class, from a fitted Bernoulli
    Naive Bayes pipeline.

    Input:
        pipeline: the fitted pipeline.
    Returns:
        (chance present in spam, chance present in legitimate) as arrays.
    """
    model = pipeline.named_steps["model"]
    spam_row = list(model.classes_).index("spam")
    legitimate_row = list(model.classes_).index("legitimate")
    chances = np.exp(model.feature_log_prob_)
    return chances[spam_row], chances[legitimate_row]


def word_evidence_table(pipeline, spec, filename):
    """
    For every input: how often it appears in spam and in legitimate email,
    and how strongly its presence points to spam. Saved as CSV.

    Inputs:
        pipeline: a fitted Bernoulli Naive Bayes pipeline.
        spec: the SPEC.
        filename: the CSV file inside outputs/.
    Returns:
        A DataFrame sorted from most spam-like to most legitimate-like.
    """
    in_spam, in_legitimate = presence_chances(pipeline)
    table = pd.DataFrame(
        {
            "Input": [label_for(spec, column) for column in spec["numeric"]],
            "Present in spam": in_spam.round(3),
            "Present in legitimate": in_legitimate.round(3),
            "Evidence if present": np.log(in_spam / in_legitimate).round(2),
        }
    ).sort_values("Evidence if present", ascending=False)
    save_table(table, filename)
    return table


def email_evidence(pipeline, example, spec):
    """
    How much each input pushed one email towards spam (positive) or
    legitimate (negative), counting both present and absent inputs.

    Inputs:
        pipeline: a fitted Bernoulli Naive Bayes pipeline.
        example: a one-row DataFrame of the 57 measurements.
        spec: the SPEC.
    Returns:
        A pandas Series: readable input name -> evidence, strongest first.
    """
    in_spam, in_legitimate = presence_chances(pipeline)
    present = example[spec["numeric"]].to_numpy()[0] > 0
    evidence = np.where(present, np.log(in_spam / in_legitimate), np.log((1 - in_spam) / (1 - in_legitimate)))
    series = pd.Series(evidence, index=[label_for(spec, column) for column in spec["numeric"]])
    return series.reindex(series.abs().sort_values(ascending=False).index)
