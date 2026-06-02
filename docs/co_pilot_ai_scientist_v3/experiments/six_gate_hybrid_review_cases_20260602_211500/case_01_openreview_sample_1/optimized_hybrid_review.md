# Six-Gate Hybrid Review: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback

## Scientific taste prior

- Evidence count: `3`
- Optimized action: Reweight the research direction toward the most scientifically meaningful problem framing.

- Matched keywords: `impact, novel`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new approach for creating preference data for training reward models, which they call **Reinforcement Learning from Knowledge Feedback** (RLKF). Whereas existing preference data consists of (preferred, non-preferred) pairs where the non-preferred pair might be either incorrect or not helpful, RLKF creates three types of pairs: (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect). This way, the reward model explicitly learns

- Matched keywords: `impact, novel, problem`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: One of the big problems with LMs is that they constantly hallucinate. They do this a lot when given questions that they don't know the answer to. Some of these questions that are particularly hard for LMs are arithmetic questions where the inputs are more than just a digit or two long. \n\nThe authors here propose an RL framework to remedy this issue. This framework trains the model to prefer saying \"I don't know\" versus outputting an incorrect answer. \n\nThey have experime

- Matched keywords: `impact, novel`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new RLHF framework to address LLM hallucinations by defining a new reward model for model reliability. It trains LLMs to generate \"I don't know\" answers to questions outside the model's knowledge boundary. It conducts empirical experiments on two math question datasets to validate the effectiveness of the proposed method in enhancing LLM reliability. \n\nThe proposed method is simple and easy to follow and the evaluation is comprehensive, but the result

## Evaluator stress test

- Evidence count: `1`
- Optimized action: Add or repair benchmarks, baselines, metrics, and ablations before trusting a result.

- Matched keywords: `dataset, evaluation, experiment`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new RLHF framework to address LLM hallucinations by defining a new reward model for model reliability. It trains LLMs to generate \"I don't know\" answers to questions outside the model's knowledge boundary. It conducts empirical experiments on two math question datasets to validate the effectiveness of the proposed method in enhancing LLM reliability. \n\nThe proposed method is simple and easy to follow and the evaluation is comprehensive, but the result

## Frontier steering

- Evidence count: `0`
- Optimized action: Move the follow-up trajectory toward later-relevant concepts and higher-upside branches.

## Verifiable micro-evolution

- Evidence count: `1`
- Optimized action: Identify a machine-gradeable subproblem where OpenEvolve-style search or controlled code improvement is justified.

- Matched keywords: `training`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new approach for creating preference data for training reward models, which they call **Reinforcement Learning from Knowledge Feedback** (RLKF). Whereas existing preference data consists of (preferred, non-preferred) pairs where the non-preferred pair might be either incorrect or not helpful, RLKF creates three types of pairs: (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect). This way, the reward model explicitly learns

## Structured feedback

- Evidence count: `3`
- Optimized action: Transform vague feedback into concrete sections, claims, missing definitions, and reader-facing explanations.

- Matched keywords: `clarity`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new approach for creating preference data for training reward models, which they call **Reinforcement Learning from Knowledge Feedback** (RLKF). Whereas existing preference data consists of (preferred, non-preferred) pairs where the non-preferred pair might be either incorrect or not helpful, RLKF creates three types of pairs: (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect). This way, the reward model explicitly learns

- Matched keywords: `clarity`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: One of the big problems with LMs is that they constantly hallucinate. They do this a lot when given questions that they don't know the answer to. Some of these questions that are particularly hard for LMs are arithmetic questions where the inputs are more than just a digit or two long. \n\nThe authors here propose an RL framework to remedy this issue. This framework trains the model to prefer saying \"I don't know\" versus outputting an incorrect answer. \n\nThey have experime

- Matched keywords: `clarity`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new RLHF framework to address LLM hallucinations by defining a new reward model for model reliability. It trains LLMs to generate \"I don't know\" answers to questions outside the model's knowledge boundary. It conducts empirical experiments on two math question datasets to validate the effectiveness of the proposed method in enhancing LLM reliability. \n\nThe proposed method is simple and easy to follow and the evaluation is comprehensive, but the result

## Claim calibration

- Evidence count: `3`
- Optimized action: Narrow unsupported conclusions and state exactly what the current evidence can and cannot prove.

- Matched keywords: `limitation`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new approach for creating preference data for training reward models, which they call **Reinforcement Learning from Knowledge Feedback** (RLKF). Whereas existing preference data consists of (preferred, non-preferred) pairs where the non-preferred pair might be either incorrect or not helpful, RLKF creates three types of pairs: (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect). This way, the reward model explicitly learns

- Matched keywords: `limitation`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: One of the big problems with LMs is that they constantly hallucinate. They do this a lot when given questions that they don't know the answer to. Some of these questions that are particularly hard for LMs are arithmetic questions where the inputs are more than just a digit or two long. \n\nThe authors here propose an RL framework to remedy this issue. This framework trains the model to prefer saying \"I don't know\" versus outputting an incorrect answer. \n\nThey have experime

- Matched keywords: `boundary, limitation`
- Evidence excerpt: {"clarity": null, "confidence": 0.75, "correctness": null, "ethics": null, "impact": null, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a new RLHF framework to address LLM hallucinations by defining a new reward model for model reliability. It trains LLMs to generate \"I don't know\" answers to questions outside the model's knowledge boundary. It conducts empirical experiments on two math question datasets to validate the effectiveness of the proposed method in enhancing LLM reliability. \n\nThe proposed method is simple and easy to follow and the evaluation is comprehensive, but the result
