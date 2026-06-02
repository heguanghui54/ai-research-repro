# Focused Submission Rewrite Plan

This plan converts the current research-production package into a stronger
conference-style manuscript. The current `paper_en.md` is useful as a complete
lab record, but the latest model-review pass identifies it as too log-like for
a strong ML/NLP systems venue. The next draft should separate the main paper
from appendices and repository artifacts.

## Target Main Claim

IGRE is a reproducible workflow architecture for converting human scientific
taste and expert-review insight into explicit control signals inside
AI Scientist-v2-style automated research loops. The current evidence supports
workflow-design and measurement-readiness claims, not superiority over
autonomous AI Scientist-v2.

## Main Paper Shape

1. **Abstract**
   - State the problem: automated research agents lack a principled way to use
     human scientific taste at creative and claim-responsibility points.
   - State the method: five IGRE gates.
   - State evidence honestly: OpenReview utility maps and regeneration probes
     show which review signals are actionable; FML matched-budget evidence is
     mixed or negative for short-budget average performance.
   - State release: schema, scripts, bilingual docs, reusable Codex skill.

2. **Introduction**
   - Motivate why full automation and generic co-pilot approval are both
     insufficient for scientific research.
   - Present the core design question: which human inputs are useful as
     workflow-control signals?
   - Contributions should be limited to method, audit protocol, OpenReview
     signal mapping, regeneration/cross-model review, and negative matched
     budget findings.

3. **Related Work**
   - AI Co-Scientist: hypothesis/frontier organization.
   - AI Scientist-v2: experiment execution and paper writing.
   - AlphaEvolve/OpenEvolve: machine-gradeable code evolution.
   - Human-AI co-pilot systems and review-feedback datasets.

4. **Method: Insight-Gated Research Evolution**
   - Present only the five gates and the data schema.
   - Explain how each gate changes search pressure.
   - State which prior system each loop is inspired by, but keep the algorithm
     named and adapted as IGRE rather than a collage of prior papers.

5. **Experiments**
   - **H1: Human review text can be mapped to actionable workflow gates.**
     Use the review-utility map: 473 snippets, 398 actionable signals, gate
     counts.
   - **H2: Review-guided regeneration improves some artifacts but not all.**
     Use the six-paper regeneration probe plus Claude cross-model review:
     generating-model scorer gives 5/6 review-guided wins; Claude gives 3/6
     wins, 1 baseline win, and 2 ties.
   - **H3: Short-budget human gates do not yet beat autonomous baselines.**
     Report FML prospective packages as negative or mixed results.
   - **H4: OpenEvolve-style micro-evolution should be selectively triggered.**
     Use Max-Cut, knapsack, vectorization, and tabular probes to show when
     search helps and when direct editing is enough.

6. **Discussion**
   - Human participation is a high-variance search operator, not guaranteed
     average-performance improvement.
   - The most useful human input is specific, actionable, and gate-routable.
   - Negative short-budget findings are valuable because they identify where
     human gates are not worth their cost.

7. **Limitations**
   - No independent human expert review yet.
   - Single-author trace corpus.
   - Underpowered matched-budget experiments.
   - High-tail hypothesis not yet statistically operationalized.
   - OpenReview is offline asynchronous review data, not online co-pilot data.

## Material To Move Out Of Main Paper

- Setup probes blocked by network or missing data.
- Long chronological narration of each smoke run.
- Full artifact path lists.
- Detailed command logs.
- Individual gate JSON examples except one compact representative table.
- Full model-review raw outputs.

## Minimum Next Empirical Upgrade

Before claiming top-conference empirical support, the package needs one of:

- at least 10 matched co-pilot/autonomous pairs across at least 3 tasks, with a
  pre-registered primary metric and confidence intervals;
- blind independent expert review over matched manuscript pairs;
- a fixed external paper-quality benchmark such as PaperBench or another
  rubric-based evaluator that was not used to design IGRE.

If the matched-budget result remains negative, the stronger paper is a negative
systems result: human scientific taste is intuitively attractive, but naive
short-budget gates fail unless review signals are concrete, gate-routable, and
budget-aware.
