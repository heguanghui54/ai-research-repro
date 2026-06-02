# Review-Guided Mini-Paper: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback

## Source Paper

- Paper ID: `openreview_sample_1`
- Venue/source: `colmweb_org_COLM_2024_Conference`
- arXiv: `2403.18349`
- Original mean score: `0.53125`

## Human Review Guidance Used

- The proposed method trains models to prefer saying 'I don't know' versus outputting incorrect answers.
- Empirical experiments on math question datasets validate the effectiveness of the proposed method.

## Review Evidence Excerpts

### Review 1

{"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new approach for creating preference data for training reward models, which they call **Reinforcement Learning from Knowledge Feedback** (RLKF). Whereas existing preference data consists of (preferred, non-preferred) pairs where the non-preferred pair might be either incorrect or not helpful, RLKF creates three types of pairs: (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect). This way, the reward model explicitly learns

### Review 2

{"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: One of the big problems with LMs is that they constantly hallucinate. They do this a lot when given questions that they don't know the answer to. Some of these questions that are particularly hard for LMs are arithmetic questions where the inputs are more than just a digit or two long. \n\nThe authors here propose an RL framework to remedy this issue. This framework trains the model to prefer saying \"I don't know\" versus outputting an incorrect answer. \n\nThey have experime

### Review 3

{"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new RLHF framework to address LLM hallucinations by defining a new reward model for model reliability. It trains LLMs to generate \"I don't know\" answers to questions outside the model's knowledge boundary. It conducts empirical experiments on two math question datasets to validate the effectiveness of the proposed method in enhancing LLM reliability. \n\nThe proposed method is simple and easy to follow and the evaluation is comprehensive, but the result

## Paper-Only Baseline Artifact

**Core contribution:** This paper proposes a novel framework for improving the reliability of Large Language Models (LLMs) by training them to reject questions they cannot answer accurately.

**Experiment plan:** We will evaluate the effectiveness of the RLKF framework on standard datasets, comparing performance metrics such as accuracy and rejection rates against baseline models that do not employ rejection mechanisms.

In this paper, we propose a novel framework aimed at enhancing the reliability of Large Language Models (LLMs) by training them to reject questions that exceed their knowledge boundaries. Current models often generate erroneous outputs, known as hallucinations, when faced with unfamiliar queries. Our approach introduces Reinforcement Learning from Knowledge Feedback (RLKF), which incentivizes LLMs to prefer rejection over incorrect answers. We plan to evaluate our method on established datasets, measuring accuracy and rejection rates against baseline models. However, we acknowledge that our method may not generalize to all question types, particularly those requiring nuanced understanding. The claims made are specifically relevant to LLMs and may not extend to other model types.

## Human-Review-Guided Artifact

**Core contribution:** This paper presents a new RL-based fine-tuning method that trains LLMs to recognize when they cannot provide accurate answers, thereby improving their reliability.

**Method sketch:** We utilize RLKF to create preference data that includes pairs of (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect) to train the model effectively.

**Experiment plan:** We will conduct experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks, to measure the model's ability to reject inappropriate questions and its overall accuracy.

**Limitations:** The experiments are currently limited to specific benchmarks, and the performance on more complex or nuanced questions remains to be explored.

**Claim boundary:** The findings are primarily relevant to LLMs and may not generalize to other AI models or broader contexts.

In this paper, we address the critical issue of hallucination in Large Language Models (LLMs) by introducing a novel RL-based fine-tuning method that trains models to prefer saying 'I don't know' when faced with questions outside their knowledge scope. Our approach leverages Reinforcement Learning from Knowledge Feedback (RLKF) to create effective preference data, allowing the model to learn from both correct and incorrect responses. We plan to validate our method through empirical experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks. While our findings suggest improvements in model reliability, the current experiments are limited to specific benchmarks, and further exploration is needed for more complex queries. The claims made are primarily relevant to LLMs and may not extend to other AI models.

## Short-Term Review Scores

### gpt-4o-mini

- Winner: `review_guided`
- Context-control overall: `3`
- Review-guided overall: `4`
- Specific review value: The review-guided version provides clearer insights into the empirical validation of the proposed method, enhancing the overall framing and experimental design.

### claude-3-7-sonnet-latest

- Winner: `review_guided`
- Context-control overall: `3`
- Review-guided overall: `4`
- Specific review value: The review insight about constructing preference data with (correct, refuse), (refuse, incorrect), (correct, incorrect) triples is a concrete methodological detail that meaningfully sharpens the method sketch beyond generic RL framing. The focus on arithmetic/math datasets as a specific evaluation domain also grounds the experiment plan.

## Later-Frontier Evidence

- Citation-frontier winner: `shuffled_review_control`
- Citation temporal pattern: `short_term_positive_long_term_negative`
- Semantic-frontier winner: `paper_context`
- Latent delayed-value candidate: `False`
- Frontier terms: `chatbot, moral, refusal, llm, value, user, discourse, tenor, rhetoric, sorry, dave, afraid, can, regulation, article, explore`

## Evidence Boundary

This PDF displays a concrete human-review-guided mini-paper artifact from the current pilot. It is not yet a full benchmark-executed deep reproduction.
