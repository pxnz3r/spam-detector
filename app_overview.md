### What this is

A spam filter built with **Naive Bayes**. It learns from 4,601 emails collected at Hewlett-Packard Labs in 1999, 39% of them spam, and checks any email you paste in.

The original emails aren't published. For each one the dataset keeps 57 numbers: how often 48 particular words (like *free*, *money*, *meeting*) and 6 characters (like `!` and `$`) appear, and how long its runs of CAPITAL LETTERS are. The app measures the same 57 numbers from your text.

### How Naive Bayes decides

From the training emails it counts, for every word, how common it is in spam and how common in legitimate email. For a new email it asks: *if this were spam, how likely is this mix of words? And if it were legitimate?* It multiplies the chances word by word and picks the more likely class.

It is "naive" because it treats every word as independent of the others, as if *credit* and *card* had nothing to do with each other. That is false, but the method is fast, needs little data and works well on text.

Three kinds are compared:

- **Bernoulli**: only whether each word appears. The main model.
- **Multinomial**: how often each word appears.
- **Gaussian**: a bell curve per input.

A **Random Forest** is a benchmark beyond the course, and **Always legitimate** is the floor.

### What to try

- **Check an email**: start from the example prize offer or team message, or write your own, and watch which words push the verdict.
- **Spam words**: the words Naive Bayes ties most to spam and to real email.
- **Results**: scores on 1,151 held-back emails, mistakes and which inputs matter.

### What was found

- **Bernoulli Naive Bayes catches 82% of spam** with 88% of its flags correct (F1 0.85, ROC-AUC 0.95). The Random Forest benchmark does better (F1 0.94) but can't be read word by word.
- **Presence beats counts here.** Multinomial Naive Bayes does worst (F1 0.72), because the capital-letter totals run into the thousands and drown out the word frequencies.
- ***remove*, *money*, *000*, *credit* and `$` point to spam.** *george*, *hp*, *650* and *lab* point to legitimate email, only because the real emails came from one HP Labs inbox. The filter learned that person's name and phone area code.

Code and every figure: [github.com/pxnz3r/spam-detector](https://github.com/pxnz3r/spam-detector).
