# MLAgentBench Third-Task Feasibility Probe

Date: 2026-06-03

This probe asks whether the package can add another official MLAgentBench task
beyond the already scored CIFAR10/debug and OGBN-arxiv official-evaluator paths.
It does not report a new official score.

## Result

`babylm` is the most promising additional official task because its data setup
does not require Kaggle. The official prepare script completed successfully:
it downloaded the BabyLM archive from GitHub and unpacked a 157 MB task copy.

The tiny training/evaluation compatibility path remains unscored. After
repairing missing `evaluate`, `accelerate`, `datasets`, and deprecated
transformers helper issues in a marked probe copy, execution reached
`AutoTokenizer.from_pretrained("gpt2")`. The Ubuntu host could not reach
HuggingFace for the GPT-2 tokenizer/config assets, so no model checkpoint or
perplexity score was produced.

## Boundary

This is setup and blocker evidence only. It should not be counted as a third
scored MLAgentBench task. Its value is to keep the benchmark-selection story
honest: the next official score requires either cached GPT-2 assets for BabyLM,
Kaggle credentials/competition consent for Kaggle tasks, GPU/model access for
Llama inference, or a shift toward matched end-to-end co-pilot/autonomous
trajectories.
