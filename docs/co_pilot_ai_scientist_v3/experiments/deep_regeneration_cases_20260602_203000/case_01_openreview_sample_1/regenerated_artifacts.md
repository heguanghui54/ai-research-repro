# Regenerated Artifacts: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback

## Paper-Only / Baseline Artifact

**Core contribution:** This paper proposes a novel framework for improving the reliability of Large Language Models (LLMs) by training them to reject questions they cannot answer accurately.

**Method sketch:** The proposed method utilizes Reinforcement Learning from Knowledge Feedback (RLKF) to create a training regime that incentivizes LLMs to prefer rejection over incorrect answers.

**Experiment plan:** We will evaluate the effectiveness of the RLKF framework on standard datasets, comparing performance metrics such as accuracy and rejection rates against baseline models that do not employ rejection mechanisms.

**Limitations:** The method may not generalize well to all types of questions, particularly those that require nuanced understanding beyond simple factual knowledge.

**Claim boundary:** The claims are limited to the context of LLMs and may not apply to other types of models or domains.

In this paper, we propose a novel framework aimed at enhancing the reliability of Large Language Models (LLMs) by training them to reject questions that exceed their knowledge boundaries. Current models often generate erroneous outputs, known as hallucinations, when faced with unfamiliar queries. Our approach introduces Reinforcement Learning from Knowledge Feedback (RLKF), which incentivizes LLMs to prefer rejection over incorrect answers. We plan to evaluate our method on established datasets, measuring accuracy and rejection rates against baseline models. However, we acknowledge that our method may not generalize to all question types, particularly those requiring nuanced understanding. The claims made are specifically relevant to LLMs and may not extend to other model types.

## Review-Guided Artifact

Review insights used:

- The proposed method trains models to prefer saying 'I don't know' versus outputting incorrect answers.
- Empirical experiments on math question datasets validate the effectiveness of the proposed method.

**Core contribution:** This paper presents a new RL-based fine-tuning method that trains LLMs to recognize when they cannot provide accurate answers, thereby improving their reliability.

**Method sketch:** We utilize RLKF to create preference data that includes pairs of (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect) to train the model effectively.

**Experiment plan:** We will conduct experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks, to measure the model's ability to reject inappropriate questions and its overall accuracy.

**Limitations:** The experiments are currently limited to specific benchmarks, and the performance on more complex or nuanced questions remains to be explored.

**Claim boundary:** The findings are primarily relevant to LLMs and may not generalize to other AI models or broader contexts.

In this paper, we address the critical issue of hallucination in Large Language Models (LLMs) by introducing a novel RL-based fine-tuning method that trains models to prefer saying 'I don't know' when faced with questions outside their knowledge scope. Our approach leverages Reinforcement Learning from Knowledge Feedback (RLKF) to create effective preference data, allowing the model to learn from both correct and incorrect responses. We plan to validate our method through empirical experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks. While our findings suggest improvements in model reliability, the current experiments are limited to specific benchmarks, and further exploration is needed for more complex queries. The claims made are primarily relevant to LLMs and may not extend to other AI models.
