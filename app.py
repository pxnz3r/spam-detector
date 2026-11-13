"""
app.py - the spam detector demo. Run it with:

    streamlit run app.py

Tabs:
    Overview        what the project is and how Naive Bayes works,
    Check an email  paste any email, see the verdict and the words that
                    pushed it towards spam or legitimate,
    Spam words      what Naive Bayes learned about each word,
    Results         the saved tables and figures from main.py.
It needs the saved models, so run `python main.py` once first.
"""

import os

import streamlit as st

from pxlab.app import (
    cutoff_choice,
    probability_bar,
    setup_page,
    show_figure,
    show_markdown_file,
    show_results_tabs,
    show_table,
    signed_bars,
)
from pxlab.common import MODELS_FOLDER
from pxlab.tabular.data import label_for
from pxlab.tabular.train import load_models, models_are_saved
from spam_detector.explain import email_evidence
from spam_detector.features import email_features
from spam_detector.report import FOLDER, results_sections
from spam_detector.spec import SPAM_SPEC

MODEL_FOLDER = os.path.join(MODELS_FOLDER, FOLDER)
MAIN_MODEL = "Bernoulli Naive Bayes"

# Short emails written for this demo, one of each kind.
EXAMPLES = {
    "A prize offer": (
        "CONGRATULATIONS!!! You have been selected to receive $1,000,000 in FREE money! "
        "To claim your prize, reply with your address and credit card number. "
        "Order now, this offer ends today. Click here to remove your name from our mail list. "
        "Make money fast from home, no business experience needed!!!"
    ),
    "A team message": (
        "Hi all, the project meeting is moved to 2 pm on Thursday in the lab. "
        "Please bring the data tables from the original report so we can go through "
        "the conference paper draft. Re: the budget question, I will send the numbers later today. "
        "Thanks, Sam"
    ),
    "Write your own": "",
}


@st.cache_resource
def load_everything():
    """
    Load the saved models (cached, so this happens once).

    Returns:
        (model_info, models)
    """
    return load_models(MODEL_FOLDER)


def show_check_page(model_info, models):
    """
    The Check an email tab: the text on the left, the verdict and the
    evidence on the right.

    Inputs:
        model_info, models: from load_models().
    Returns:
        Nothing.
    """
    spec = SPAM_SPEC
    left, right = st.columns([3, 2], gap="large")
    with left:
        picker, model_box = st.columns(2)
        example = picker.selectbox("Start from", list(EXAMPLES))
        model_name = model_box.selectbox("Model", list(models), index=list(models).index(MAIN_MODEL))
        text = st.text_area("Email text", EXAMPLES[example], height=260, key=f"text-{example}")

    if not text.strip():
        with right:
            st.info("Paste or type an email to check it.")
        return

    features = email_features(text)
    pipeline = models[model_name]
    spam_column = list(pipeline.classes_).index("spam")
    chance = float(pipeline.predict_proba(features)[0, spam_column])
    with right:
        cutoff = cutoff_choice(model_info, model_name, key=f"cutoff-{model_name}")
        st.subheader("Spam" if chance >= cutoff else "Legitimate", anchor=False)
        st.markdown(f"Chance of spam **{chance:.0%}**")
        probability_bar(chance, threshold=cutoff)
        st.caption(
            f"Spam when the chance is at least {cutoff:.0%} (the line). Losing a real email counts five times "
            "letting one spam through, so the tuned cut-off needs more evidence than 50%."
        )
        if model_name == MAIN_MODEL:
            st.subheader("What pushed it", anchor=False)
            st.caption(
                "Evidence per input: right points to spam, left to legitimate. Absent words count too: "
                'a spam email without "george" is no surprise, a real HP Labs email without it is.'
            )
            signed_bars(email_evidence(pipeline, features, spec).head(10))
        else:
            st.caption(f"Pick {MAIN_MODEL} to see the words that pushed the verdict.")

    with st.expander("The 57 numbers measured from this text"):
        measured = features.T.rename(columns={0: "Value"})
        measured = measured[measured["Value"] > 0]
        measured.index = [label_for(spec, column) for column in measured.index]
        st.dataframe(measured.round(3), width="stretch")


def show_words_page():
    """
    The Spam words tab: what Naive Bayes learned per input.

    Returns:
        Nothing.
    """
    st.markdown(
        "For every word Naive Bayes keeps how often it appears in spam and in legitimate email. "
        "The evidence is the logarithm of their ratio: 2 means about 7 times more common in spam, "
        "−2 about 7 times more common in legitimate email."
    )
    show_figure(f"{FOLDER}/word_evidence.png")
    st.markdown(
        'Note "george", "hp", "650" and "lab": the legitimate emails came from one person\'s inbox at '
        "Hewlett-Packard Labs, so their name, employer and phone area code became signs of a real email. "
        "A filter trained this way works for that inbox and nobody else's."
    )
    show_table("Every input", f"{FOLDER}/word_evidence.csv")


def main():
    """
    Build the page.

    Returns:
        Nothing.
    """
    setup_page("Spam detector")
    if not models_are_saved(MODEL_FOLDER):
        st.error("No saved models yet. Run `python main.py` first.")
        st.stop()
    model_info, models = load_everything()

    overview, check, words, results = st.tabs(["Overview", "Check an email", "Spam words", "Results"])
    with overview:
        show_markdown_file("app_overview.md")
    with check:
        show_check_page(model_info, models)
    with words:
        show_words_page()
    with results:
        show_results_tabs(results_sections())


main()
