"""
report.py - which saved tables and figures make up the results. The app's
Results tab and docs/results.md both read this list, so they always match.
"""

FOLDER = "spam"


def results_sections():
    """
    The results, grouped into sections.

    Returns:
        A list of (section name, items) for pxlab's show_results_tabs() and
        write_results_doc().
    """
    return [
        (
            "Models",
            [
                ("table", "Test-set scores (spam is the positive class)", f"{FOLDER}/model_comparison.csv"),
                ("figure", f"{FOLDER}/confusion_matrices.png"),
                ("figure", f"{FOLDER}/roc_curves.png"),
            ],
        ),
        (
            "Spam words",
            [
                ("figure", f"{FOLDER}/word_evidence.png"),
                ("table", "What Bernoulli Naive Bayes learned per input", f"{FOLDER}/word_evidence.csv"),
            ],
        ),
        (
            "Which inputs matter",
            [
                ("figure", f"{FOLDER}/permutation_importance.png"),
                (
                    "table",
                    "Permutation importance (drop in F1 when the input is shuffled)",
                    f"{FOLDER}/permutation_importance.csv",
                ),
            ],
        ),
        ("Mistakes", [("table", "Test emails Bernoulli Naive Bayes got wrong", f"{FOLDER}/wrong_predictions.csv")]),
        (
            "Data",
            [
                ("table", "Data quality", f"{FOLDER}/data_quality.csv"),
                ("figure", f"{FOLDER}/target.png"),
            ],
        ),
    ]
