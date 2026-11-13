"""
main.py - run the whole spam study with one command:

    python main.py

It:
    1. downloads (once) and checks the Spambase data,
    2. keeps 25% of the emails back as a test set,
    3. trains three kinds of Naive Bayes (word present or not, how often,
       bell curve), a Random Forest benchmark and an "always legitimate"
       baseline, tuning smoothing with 5-fold cross-validation,
    4. scores them on the test set (spam is the positive class) and draws
       confusion matrices and ROC curves,
    5. lists the words Naive Bayes ties most to spam and to real email,
    6. measures which inputs matter and lists the mistakes,
    7. saves the models for the app and writes docs/results.md.
Figures and tables go to outputs/spam/, models to models/spam/.
"""

import os

import matplotlib.pyplot as plt

from pxlab.common import MODELS_FOLDER, save_figure, save_table, set_plot_style, write_results_doc
from pxlab.tabular.data import check_columns, input_summary, plot_target, quality_report, split_data
from pxlab.tabular.evaluate import (
    comparison_table,
    plot_confusion_matrices,
    plot_roc_curves,
    test_scores,
    wrong_predictions,
)
from pxlab.tabular.explain import permutation_importance_table, plot_permutation_importance
from pxlab.tabular.train import best_model_name, save_models, train_models
from spam_detector.data import load_spambase
from spam_detector.explain import word_evidence_table
from spam_detector.report import FOLDER, results_sections
from spam_detector.spec import SPAM_SPEC


def plot_word_evidence(table, top=12, filename="word_evidence.png"):
    """
    The inputs whose presence points most to spam and most to legitimate
    email, as a horizontal bar chart.

    Inputs:
        table: from word_evidence_table().
        top: how many from each end.
        filename: the image file name.
    Returns:
        The saved path.
    """
    # The table is sorted most spam-like first; take both ends, reversed so
    # the most spam-like bar ends up on top.
    ends = table.iloc[list(range(top)) + list(range(len(table) - top, len(table)))].iloc[::-1]
    figure, axis = plt.subplots(figsize=(8, 7))
    colours = ["#C44E52" if value > 0 else "#4C72B0" for value in ends["Evidence if present"]]
    axis.barh(ends["Input"], ends["Evidence if present"], color=colours)
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_xlabel("Evidence if present: log(chance in spam / chance in legitimate)")
    axis.set_title("What Naive Bayes learned: red points to spam, blue to legitimate email")
    figure.tight_layout()
    return save_figure(figure, filename)


def main():
    """
    The full study.

    Returns:
        Nothing.
    """
    spec = SPAM_SPEC
    set_plot_style()
    data = load_spambase()
    check_columns(data, spec)
    quality_report(data, spec, f"{FOLDER}/data_quality.csv")
    plot_target(data, spec, f"{FOLDER}/target.png")

    train_features, test_features, train_target, test_target = split_data(data, spec)
    model_folder = os.path.join(MODELS_FOLDER, FOLDER)
    os.makedirs(model_folder, exist_ok=True)

    print("Tuning with 5-fold cross-validation:")
    results = train_models(spec, train_features, train_target)
    table = comparison_table(results, test_features, test_target, spec, f"{FOLDER}/model_comparison.csv")
    print(table.to_string(index=False))
    plot_confusion_matrices(results, test_features, test_target, f"{FOLDER}/confusion_matrices.png")
    plot_roc_curves(results, test_features, test_target, spec["positive_class"], f"{FOLDER}/roc_curves.png")

    bernoulli = results["Bernoulli Naive Bayes"]["pipeline"]
    evidence = word_evidence_table(bernoulli, spec, f"{FOLDER}/word_evidence.csv")
    plot_word_evidence(evidence, filename=f"{FOLDER}/word_evidence.png")
    save_table(wrong_predictions(bernoulli, test_features, test_target, spec), f"{FOLDER}/wrong_predictions.csv")

    explained = {name: result for name, result in results.items() if name in ("Bernoulli Naive Bayes", "Random Forest")}
    importance = permutation_importance_table(
        explained, test_features, test_target, spec, filename=f"{FOLDER}/permutation_importance.csv"
    )
    plot_permutation_importance(importance, filename=f"{FOLDER}/permutation_importance.png")

    model_info = {
        "dataset": "UCI Spambase",
        "classes": ["legitimate", "spam"],
        "best_model": best_model_name(results),
        "test_scores": {
            name: test_scores(r["pipeline"], test_features, test_target, spec) for name, r in results.items()
        },
        "cv_scores": {name: r["cv_score"] for name, r in results.items()},
    }
    model_info.update(input_summary(train_features, spec))
    save_models(results, model_info, folder=model_folder)

    write_results_doc(
        "Results",
        "Produced by `python main.py`. The test set is 25% of the 4,601 emails (stratified) and was not used for "
        "tuning or model choice. Spam is the positive class: precision is the share of emails flagged as spam that "
        "really were spam, recall the share of spam that was caught.",
        results_sections(),
    )
    print("Done. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
