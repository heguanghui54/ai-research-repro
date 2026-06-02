# Original Paper: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback

- Paper ID: `openreview_sample_1`
- Venue/source: `colmweb_org_COLM_2024_Conference`
- arXiv: `2403.18349`
- Decision: `True`
- Mean score: `0.53125`

## Abstract Excerpt

Large Language Models (LLMs) often generate erroneous outputs, known as hallucinations, due to their limitations in discerning questions beyond their knowledge scope. While addressing hallucination has been a focal point in research, previous efforts primarily concentrate on enhancing correctness without giving due consideration to the significance of rejection mechanisms. In this paper, we conduct a comprehensive examination of the role of rejection, introducing the alignment goal of model reliability along with corresponding metrics. This goal requires the model to provide accurate responses while adeptly rejecting questions exceeding its knowledge boundaries, thereby minimizing hallucinations. To improve the inherent reliability of LLMs, we present a novel alignment framework called Reinforcement Learning from Knowledge Feedback (RLKF). RLKF leverages knowledge feedback to dynamically

## Decision Excerpt

This paper addresses the problem of model hallucination, when models generate incorrect responses to questions. The paper proposes that a fundamental underlying problem is that models cannot recognize when they cannot produce a correct answer, and that one solution is to train models to explicitly reject questions when they are not able to answer correctly. Authors propose a RL-based fine-tuning method that uses external knowledge and/or self-consistency to create train-time preference data that incentivizes correctness and consistency of outputs. 

Reviewers point out several limitations of the paper. Experiments are limited by the choice of benchmarks (arithmetic only, though authors add T
