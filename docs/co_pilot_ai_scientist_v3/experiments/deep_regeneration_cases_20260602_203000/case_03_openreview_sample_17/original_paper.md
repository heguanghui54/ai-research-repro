# Original Paper: Knowledge Unlearning for Mitigating Privacy Risks in Language Models

- Paper ID: `openreview_sample_17`
- Venue/source: `ICLR_cc_2023_Conference`
- arXiv: `not available`
- Decision: `False`
- Mean score: `0.55`

## Abstract Excerpt

Pretrained Language Models (LMs) memorize a vast amount of knowledge during initial pretraining, including information that may violate the privacy of personal lives and identities. Previous work addressing privacy issues for language models has mostly focused on data preprocessing and differential privacy methods, both requiring re-training the underlying LM. We propose knowledge unlearning as an alternative method to reduce privacy risks for LMs post hoc. We show that simply applying the unlikelihood training objective to target token sequences is effective at forgetting them with little to no degradation of general language modeling performances; it sometimes even substantially improves the underlying LM with just a few iterations. We also find that sequential unlearning is better than trying to unlearn all the data at once and that unlearning is highly dependent on which kind of data

## Decision Excerpt

The main contribution of this work lies in proposing the use of gradient ascent on equation 1 for unlearning to provide empirical privacy guarantees for large language models.

This paper has generated considerable response to the authors' rebuttal and an active discussion from the reviewers. 

While we have found the findings interesting, two main concerns remain after reviewing the authors' responses:

(A) It is unclear if the authors' claim of "the simple approach of gradient ascent ... results in little to no degradation of general performance for LMs" would indeed hold when larger datasets are unlearned. In particular, when would be the "breaking point"? Reviewers 9RUh and 4t9e have bot
