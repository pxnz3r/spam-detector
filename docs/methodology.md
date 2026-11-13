# Methodology

## Question

How well does Naive Bayes separate spam from legitimate email using word frequencies, which kind of Naive Bayes suits the data, and which words does it rely on?

## Data

Spambase: 4,601 emails from 1999, 1,813 spam (39%) and 2,788 legitimate. The legitimate ones came from work and personal email at Hewlett-Packard Labs. Each email is described by 57 numbers:

| Group | Inputs |
| --- | --- |
| Words (48) | percentage of the email's words that are this word, e.g. *free*, *money*, *meeting*, *george* |
| Characters (6) | percentage of characters that are `;` `(` `[` `!` `$` `#` |
| Capitals (3) | average and longest run of capital letters, and total capital letters |

`spam_detector/features.py` measures the same 57 numbers from any text, so the demo can check new emails. Words are runs of letters and digits, lower-cased.

## Steps

1. **Checks**: missing values, duplicates and the spam/legitimate split.
2. **Split**: 75% training, 25% test, stratified.
3. **Models**, each in a scikit-learn Pipeline:
   - Bernoulli Naive Bayes: each input becomes present (above 0) or absent, and the model learns the chance of each word appearing in spam and in legitimate email.
   - Multinomial Naive Bayes: treats the inputs as counts, so frequent words weigh more.
   - Gaussian Naive Bayes: a bell curve per input and class.
   - Random Forest, 300 trees, a benchmark beyond the course.
   - Always legitimate, the baseline.
   The Naive Bayes smoothing strength alpha is tuned over 0.01, 0.1, 0.5 and 1. Smoothing adds a small count to every word so a word never seen in one class doesn't make that class impossible.
4. **Tuning**: 5-fold stratified cross-validation scored by F1 for spam, which balances catching spam (recall) against flagging real email (precision).
5. **Test scores**: accuracy, balanced accuracy, precision, recall and F1 for spam, and ROC-AUC. Confusion matrices and ROC curves.
6. **Word evidence**: for Bernoulli Naive Bayes, the log of (chance the word appears in spam / chance in legitimate email) for every input. In the app, the evidence for one email adds up every input, present or absent.
7. **Importance**: permutation importance on the test set for Bernoulli Naive Bayes and the forest, 10 shuffles per input.

## Limits

- **One inbox.** The legitimate emails all come from one HP Labs mailbox, so *george*, *hp*, *650* and *lab* are strong signs of a real email. A filter trained like this works for that person and would need retraining on anyone else's mail.
- **1999 email.** Spam has changed: images, links and obfuscated words. The 48 fixed words can't see any of that.
- **A fixed vocabulary.** Only the 48 chosen words count; a modern filter learns its vocabulary from the text.
- **The naive assumption.** Words are treated as independent given the class. *credit* and *card* aren't, so the model double-counts their evidence and its probabilities are overconfident (close to 0% or 100%), even when the verdict is right.
- **The cut-off is 50%.** Losing a real email to the spam folder usually costs more than letting one spam through; a real filter would raise the cut-off.
