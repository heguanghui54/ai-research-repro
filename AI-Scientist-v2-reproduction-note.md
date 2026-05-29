# AI Scientist-v2 简短复现说明

本次复现目标是尽量低成本地跑通 `SakanaAI/AI-Scientist-v2` 的论文生成流程，并输出可检查的 PDF 产物。

## 结果

- 已生成论文 PDF：
  - `/Users/hgh54913/Documents/research/artifacts/AI-Scientist-v2-reflection1.pdf`
- 远端 Ubuntu 上对应产物：
  - `/home/heshi/research/AI-Scientist-v2/experiments/2026-05-29_06-27-55_mnist_robustness_attempt_0/2026-05-29_06-27-55_mnist_robustness_attempt_0_reflection1.pdf`
- 已推送到 GitHub 的 draft PR：
  - `https://github.com/heguanghui54/AI-Scientist/pull/1`
- 当前 PR 分支：
  - `codex/ai-scientist-v2-repro`

## 这次实际做了什么

1. 用低成本模型优先跑通实验，主模型选用 `gpt-4o-mini`。
2. 在远端 Ubuntu 上运行 `AI-Scientist-v2` 的实验与写作流程。
3. 修复了写作阶段的两个阻塞点：
   - LaTeX 编译器在远端环境中需要改用 `tectonic`
   - 写作反思阶段需要兼容 `gpt-4o-mini` 的 VLM 初始化，并在不可用时安全跳过
4. 补齐了写作模板需要的图文件，确保 PDF 能正常编译输出。

## 复现结论

- 论文生成流程已经跑通，并产出可打开的 PDF。
- 复现改动与说明已同步到 GitHub 的 draft PR。
- 后续如果继续迭代，优先方向是：
  - 让写作反思阶段完全无报错结束
  - 进一步压缩运行成本
  - 把结果整理为更完整的复现记录
