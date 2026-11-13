<div align="center">

<h1>Spam detector</h1>

<p>Classifies email as spam or legitimate with Naive Bayes, from how often particular words and characters appear. Built on the UCI Spambase data, with an interactive demo that checks any email you paste in and shows which words pushed the verdict.</p>

<p>
<a href="https://github.com/pxnz3r/spam-detector/actions/workflows/ci.yml"><img src="https://github.com/pxnz3r/spam-detector/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<img src="https://img.shields.io/badge/python-3.14-blue" alt="Python 3.14">
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

<p><a href="docs/results.md">Results</a> · <a href="docs/methodology.md">Methodology</a> · <a href="docs/deploy.md">Deploy the demo</a></p>

<img src="outputs/figures/spam/word_evidence.png" width="720" alt="Words Naive Bayes ties to spam and to legitimate email">

</div>

## How it works

1. **Load and check** 4,601 emails from UCI Spambase, described by word and character frequencies.
2. **Tune** Naive Bayes and its rivals with cross-validation inside leak-free pipelines.
3. **Test how sure the scores are** with bootstrap intervals, a paired test against every rival, learning curves and a baseline that ignores the inputs.
4. **Pick the cut-off** at the lowest cost, counting a legitimate email lost to the spam folder as five times worse than a spam that gets through, and check calibration.
5. **Study the mistakes** and **paste any email** into the Streamlit demo to see which words pushed it either way.

## Results

Test set: 1,151 of the 4,601 emails (stratified), never used for tuning or model choice. 39% of emails are spam.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | --- | --- | --- | --- | --- |
| **Bernoulli Naive Bayes** (word present or not) | 0.883 | 0.879 | 0.815 | 0.846 | 0.951 |
| Multinomial Naive Bayes (word counts) | 0.780 | 0.729 | 0.705 | 0.717 | 0.833 |
| Gaussian Naive Bayes (bell curve per input) | 0.831 | 0.713 | 0.954 | 0.816 | 0.947 |
| Random Forest (benchmark) | 0.953 | 0.963 | 0.916 | 0.939 | 0.986 |
| Always legitimate (baseline) | 0.606 | 0 | 0 | 0 | 0.500 |

Precision, recall and F1 are for the spam class.

- **Presence beats counts here.** Bernoulli Naive Bayes, which only asks whether each word appears, is the best Naive Bayes. Multinomial does worst because the capital-letter totals run into the thousands and drown out the word frequencies.
- **Spam words:** *remove*, *money*, *000*, *credit*, *addresses* and `$`. **Legitimate words:** *george*, *cs*, *857*, *telnet*, *hp* and *lab*.
- **The legitimate words are the dataset's quirk.** The real emails came from one person's inbox at Hewlett-Packard Labs, so their first name, employer and phone area codes became signs of a real email. The filter fits that inbox, not yours.
- **The forest is stronger** (F1 0.94) but can't be read word by word; Naive Bayes can.

Full tables and figures: [docs/results.md](docs/results.md). How it was done: [docs/methodology.md](docs/methodology.md).

## How sure the results are

**The scores are tight.** Random Forest reaches F1 0.939 on the test set (95% interval 0.923 to 0.955), and beats every Naive Bayes variant on McNemar's test (p < 0.001).

**Nothing overfits.** Training and validation F1 are within 0.06 for every model, and the learning curves have levelled off.

**The cut-off moves to 0.65.** Losing a real email to the spam folder counts as 5 times worse than letting spam through, which cuts the cost per 100 emails from 10.3 to 9.6.

**Confidence means something.** When the forest is at least 90% sure, it is right 99% of the time, and that covers 68% of emails.

**Missed spam has no dollar signs.** Caught spam averages 0.19% `$` characters, missed spam 0.008%.

Every table and figure behind these is in [docs/results.md](docs/results.md).

## Run it

Needs Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py
uv run streamlit run app.py
```

`main.py` downloads the data once into `data/`, then writes figures and tables to `outputs/`, models to `models/` and the tables to `docs/results.md`. Outputs and models are committed, so the demo works without running it.

## The demo

- **Overview**: what the project is, how Naive Bayes decides and what was found.
- **Check an email**: paste an email or start from an example, pick a model, and see the chance of spam and the inputs that pushed it.
- **Spam words**: what Naive Bayes learned about every word and character.
- **Results**: model comparison, ROC curves, mistakes, permutation importance and data checks.

## Layout

```
spam_detector/   spec.py (inputs and models), data.py (download), features.py (text to the 57 inputs),
                 explain.py (word evidence), report.py
pxlab/           shared engine (vendored): data checks, pipelines, tuning, evaluation, app helpers
main.py          the full study
app.py           the Streamlit demo
docs/            methodology, results, deploy
```

## Data

Hopkins, Reeber, Forman and Suermondt (1999), [Spambase](https://archive.ics.uci.edu/dataset/94/spambase), UCI Machine Learning Repository, CC BY 4.0. The emails themselves aren't published, only the 57 measurements per email.

## License

MIT
