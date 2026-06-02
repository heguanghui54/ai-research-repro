# pair_01: Blind Pair

## Source Paper Context

Title: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback

Abstract excerpt:

Large Language Models (LLMs) often generate erroneous outputs, known as hallucinations, due to their limitations in discerning questions beyond their knowledge scope. While addressing hallucination has been a focal point in research, previous efforts primarily concentrate on enhancing correctness without giving due consideration to the significance of rejection mechanisms. In this paper, we conduct a comprehensive examination of the role of rejection, introducing the alignment goal of model reliability along with corresponding metrics. This goal requires the model to provide accurate responses while adeptly rejecting questions exceeding its knowledge boundaries, thereby minimizing hallucinations. To improve the inherent reliability of LLMs, we present a novel alignment framework called Reinforcement Learning from Knowledge Feedback (RLKF). RLKF leverages knowledge feedback to dynamically

## Variant A

Core contribution: This paper presents a new RL-based fine-tuning method that trains LLMs to recognize when they cannot provide accurate answers, thereby improving their reliability.

Method sketch: We utilize RLKF to create preference data that includes pairs of (correct, refuse-to-answer), (refuse-to-answer, incorrect), and (correct, incorrect) to train the model effectively.

Experiment plan: We will conduct experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks, to measure the model's ability to reject inappropriate questions and its overall accuracy.

Limitations: The experiments are currently limited to specific benchmarks, and the performance on more complex or nuanced questions remains to be explored.

Claim boundary: The findings are primarily relevant to LLMs and may not generalize to other AI models or broader contexts.

Mini-paper artifact:
In this paper, we address the critical issue of hallucination in Large Language Models (LLMs) by introducing a novel RL-based fine-tuning method that trains models to prefer saying 'I don't know' when faced with questions outside their knowledge scope. Our approach leverages Reinforcement Learning from Knowledge Feedback (RLKF) to create effective preference data, allowing the model to learn from both correct and incorrect responses. We plan to validate our method through empirical experiments on various datasets, particularly focusing on arithmetic and other knowledge-intensive tasks. While our findings suggest improvements in model reliability, the current experiments are limited to specific benchmarks, and further exploration is needed for more complex queries. The claims made are primarily relevant to LLMs and may not extend to other AI models.

## Variant B

Core contribution: This paper introduces a novel alignment framework, RL from Knowledge Feedback (RLKF), aimed at enhancing the reliability of Large Language Models (LLMs) by effectively rejecting questions outside their knowledge scope.

Method sketch: RLKF utilizes knowledge feedback to dynamically adjust the model's responses, ensuring that it not only provides accurate answers but also appropriately refuses questions that exceed its knowledge boundaries.

Experiment plan: We will evaluate RLKF against traditional LLMs on a dataset of questions, measuring both the accuracy of responses and the frequency of appropriate rejections. Metrics will include precision, recall, and user satisfaction scores.

Limitations: The proposed method may struggle with ambiguous questions that lie on the boundary of the model's knowledge, potentially leading to inconsistent rejection rates.

Claim boundary: The claims made regarding the effectiveness of RLKF are bounded by the specific datasets used for evaluation and may not generalize across all types of questions.

Mini-paper artifact:
Large Language Models (LLMs) are known to produce erroneous outputs, commonly referred to as hallucinations, when faced with questions beyond their knowledge scope. This paper presents a novel approach to addressing this issue by focusing on the rejection mechanisms of LLMs. We introduce a new alignment framework, Reinforcement Learning from Knowledge Feedback (RLKF), which aims to enhance the reliability of LLMs by allowing them to reject questions that exceed their knowledge boundaries. Through a series of experiments, we will assess the performance of RLKF compared to traditional methods, focusing on metrics such as accuracy and rejection rates. While RLKF shows promise in improving model reliability, it is essential to acknowledge its limitations, particularly in handling ambiguous queries. Our findings suggest that RLKF can significantly reduce hallucinations while maintaining high accuracy, thus paving the way for more trustworthy LLM applications.
