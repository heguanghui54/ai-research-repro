const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const state = {
  running: false,
  stepIndex: 0,
  runCount: 0,
  difficulty: 1,
  timer: null,
  currentNode: "root",
  rng: mulberry32(20250529),
};

const stageOrder = ["idea", "search", "debug", "review", "paper"];

const stageCopy = {
  idea: {
    title: "想点子",
    note: "系统先把一个大主题拆成几个小问题。",
  },
  search: {
    title: "树搜索",
    note: "把最有希望的实验分支继续往下挖。",
  },
  debug: {
    title: "修 bug",
    note: "如果代码报错，就回去修，再继续跑。",
  },
  review: {
    title: "审稿",
    note: "检查图、表、结论是不是讲得通。",
  },
  paper: {
    title: "写论文",
    note: "把结果整理成能读懂的论文草稿。",
  },
};

const nodeInfo = {
  root: {
    title: "起点：一个大主题",
    body: "先给系统一个总方向，比如“研究自动科学发现”。",
  },
  idea: {
    title: "想法节点",
    body: "把主题拆成几个候选研究方向，像在草稿纸上列点子。",
  },
  search: {
    title: "树搜索节点",
    body: "从多个实验分支里挑更值得继续投资的那条路。",
  },
  debug: {
    title: "调试节点",
    body: "如果程序报错，就先修复，再继续往下走。",
  },
  tune: {
    title: "调参节点",
    body: "调整学习率、步数、正则强度等，让实验更稳。",
  },
  review: {
    title: "审稿节点",
    body: "让 AI 看图、看结果、看论文是不是讲得清楚。",
  },
  paper: {
    title: "论文节点",
    body: "把实验结果写成论文草稿，并给出结论。",
  },
  final: {
    title: "最终结果",
    body: "系统会选出一个最值得继续写下去的版本。",
  },
};

const modeInfo = [
  {
    label: "简单",
    note: "简单模式：几乎不报错，像一个特别顺手的实验。",
    bugRate: 0.08,
    effectBias: 0.16,
  },
  {
    label: "标准",
    note: "标准模式：有一点点 bug，像真实科研。",
    bugRate: 0.22,
    effectBias: 0.06,
  },
  {
    label: "困难",
    note: "困难模式：更容易报错，但也更像真实探索。",
    bugRate: 0.38,
    effectBias: -0.02,
  },
];

const scripts = {
  idea: [
    "先生成 3 个研究点子。",
    "做一次简短的文献检查，避免重复。",
    "挑一个最值得试的方向进入实验。",
  ],
  search: [
    "并行跑 3 条实验分支。",
    "如果某条路表现好，就继续往下挖。",
    "如果某条路报错，就拉回去修。",
  ],
  debug: [
    "读取报错日志。",
    "把明显的 bug 修掉。",
    "重新运行这条实验线。",
  ],
  review: [
    "检查图表是否清楚。",
    "检查论文结论是否过度夸张。",
    "给出审稿风格评分。",
  ],
  paper: [
    "汇总结果，写出标题和摘要。",
    "把实验过程翻译成论文语言。",
    "导出最终论文草稿。",
  ],
};

const baselineCurve = [1.78, 1.66, 1.58, 1.51, 1.47, 1.42, 1.39, 1.37, 1.36, 1.35];

const defaultRealWorkflow = {
  source: "GitHub README + bfts_config.yaml + 论文摘要",
  treeSearchOrigin: "AIDE",
  codeModel: "Claude 3.5 Sonnet",
  feedbackModel: "GPT-4o",
  reportModel: "GPT-4o",
  execTimeoutSeconds: 3600,
  workers: 4,
  stages: [20, 12, 12, 18],
  numDrafts: 3,
  maxDebugDepth: 3,
  debugProb: 0.5,
};

let realWorkflow = structuredClone(defaultRealWorkflow);

const appEls = {
  run: $("#runDemo"),
  run2: $("#runDemo2"),
  reset: $("#resetDemo"),
  step: $("#stepDemo"),
  difficulty: $("#difficulty"),
  difficultyLabel: $("#difficultyLabel"),
  modeNote: $("#modeNote"),
  timeline: $("#timeline"),
  treeNodes: $$(".tree-svg .node"),
  logStream: $("#logStream"),
  logTemplate: $("#logTemplate"),
  paperTitle: $("#paperTitle"),
  paperAbstract: $("#paperAbstract"),
  paperBody: $("#paperBody"),
  baselineMetric: $("#baselineMetric"),
  candidateMetric: $("#candidateMetric"),
  deltaMetric: $("#deltaMetric"),
  reviewMetric: $("#reviewMetric"),
  lossChart: $("#lossChart"),
  factsGrid: $("#factsGrid"),
  repoTree: $("#repoTree"),
  artifactList: $("#artifactList"),
};

bindEvents();
setMode(1);
renderNode("root");
renderChart(baselineCurve, []);
bootstrap();

function bindEvents() {
  appEls.run.addEventListener("click", () => startDemo());
  appEls.run2.addEventListener("click", () => startDemo());
  appEls.reset.addEventListener("click", () => resetDemo(true));
  appEls.step.addEventListener("click", () => stepOnce());
  appEls.difficulty.addEventListener("input", (event) => {
    setMode(Number(event.target.value));
  });

  appEls.treeNodes.forEach((node) => {
    const key = node.dataset.node;
    node.addEventListener("click", () => renderNode(key));
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        renderNode(key);
      }
    });
  });
}

function setMode(index) {
  state.difficulty = index;
  const mode = modeInfo[index];
  appEls.difficultyLabel.textContent = mode.label;
  appEls.modeNote.textContent = mode.note;
}

function resetDemo(clearLogs = false) {
  stopTimer();
  state.running = false;
  state.stepIndex = 0;
  state.currentNode = "root";
  updateControls();
  updateTimeline();
  renderNode("root");
  if (clearLogs) {
    appEls.logStream.innerHTML = "";
    seedIntroLogs();
  }
  appEls.paperTitle.textContent = "点击开始，论文标题会出现";
  appEls.paperAbstract.textContent =
    "这次演示不是随便编的，而是尽量贴近 AI Scientist-v2 仓库里公开的模型、阶段和树搜索配置。";
  appEls.paperBody.textContent = "# 论文草稿\n\n先运行模拟实验，再看这里怎么变化。";
  updateMetrics(null);
  renderChart(baselineCurve, []);
  renderDynamicPanels();
}

async function bootstrap() {
  try {
    const response = await fetch("./data/aiscientist-v2.json", { cache: "no-store" });
    if (response.ok) {
      const raw = await response.json();
      realWorkflow = normalizeRealWorkflow(raw);
    }
  } catch (error) {
    console.warn("Failed to load AI Scientist-v2 data file:", error);
  }
  renderDynamicPanels();
  seedIntroLogs();
}

function normalizeRealWorkflow(raw) {
  const execution = raw.execution || {};
  const models = raw.models || {};
  return {
    source: "GitHub README + bfts_config.yaml + 论文摘要",
    treeSearchOrigin: raw.treeSearchOrigin || "AIDE",
    codeModel: models.code || defaultRealWorkflow.codeModel,
    feedbackModel: models.feedback || defaultRealWorkflow.feedbackModel,
    reportModel: models.report || defaultRealWorkflow.reportModel,
    vlmFeedbackModel: models.vlmFeedback || defaultRealWorkflow.feedbackModel,
    aggPlotsModel: models.aggPlots || "o3-mini-2025-01-31",
    writeupModel: models.writeup || "o1-preview-2024-09-12",
    citationModel: models.citation || defaultRealWorkflow.feedbackModel,
    execTimeoutSeconds: execution.timeoutSeconds || defaultRealWorkflow.execTimeoutSeconds,
    workers: execution.workers || defaultRealWorkflow.workers,
    stages: Array.isArray(raw.stages) ? raw.stages : [],
    numDrafts: execution.numDrafts || defaultRealWorkflow.numDrafts,
    maxDebugDepth: execution.maxDebugDepth || defaultRealWorkflow.maxDebugDepth,
    debugProb: execution.debugProb ?? defaultRealWorkflow.debugProb,
    numSeeds: execution.numSeeds || 3,
    kFoldValidation: execution.kFoldValidation ?? 1,
    exposePrediction: Boolean(execution.exposePrediction),
    dataPreview: Boolean(execution.dataPreview),
    repoName: raw.repoName || "SakanaAI/AI-Scientist-v2",
    repoUrl: raw.repoUrl || "https://github.com/SakanaAI/AI-Scientist-v2",
    paperUrl: raw.paperUrl || "https://arxiv.org/abs/2504.08066",
    summary: raw.summary || "",
    artifacts: Array.isArray(raw.artifacts) ? raw.artifacts : [],
    repoLayout: Array.isArray(raw.repoLayout) ? raw.repoLayout : [],
  };
}

function renderDynamicPanels() {
  renderFactsGrid();
  renderRepoTree();
  renderArtifactList();
  renderStageLabels();
}

function renderFactsGrid() {
  if (!appEls.factsGrid) return;
  const cards = [
    {
      label: "仓库",
      value: realWorkflow.repoName,
      detail: `来自 ${realWorkflow.repoUrl}`,
    },
    {
      label: "树搜索来源",
      value: realWorkflow.treeSearchOrigin,
      detail: "README 说明 ai_scientist 的 tree search 建立在 AIDE 上。",
    },
    {
      label: "代码模型",
      value: realWorkflow.codeModel,
      detail: "对应 bfts_config.yaml 的 code.model。",
    },
    {
      label: "反馈 / 审稿",
      value: realWorkflow.feedbackModel,
      detail: "feedback、VLM feedback 和 review / report 主要由 GPT-4o 系列完成。",
    },
    {
      label: "执行上限",
      value: `${realWorkflow.execTimeoutSeconds} 秒 / 节点`,
      detail: `搜索最多 ${realWorkflow.maxDebugDepth} 层 debug，debug 概率 ${Math.round(realWorkflow.debugProb * 100)}%。`,
    },
    {
      label: "并行探索",
      value: `${realWorkflow.workers} workers`,
      detail: `${realWorkflow.numDrafts} 个草稿树，${realWorkflow.numSeeds} 个 seed。`,
    },
  ];
  appEls.factsGrid.innerHTML = cards
    .map(
      (card) => `
        <div class="facts-card">
          <span>${card.label}</span>
          <strong>${card.value}</strong>
          <p>${card.detail}</p>
        </div>
      `,
    )
    .join("");
}

function renderRepoTree() {
  if (!appEls.repoTree) return;
  appEls.repoTree.innerHTML = realWorkflow.repoLayout
    .map(
      (item, index) => `
        <div class="repo-item">
          <code>${item}</code>
          <span>${index === 0 ? "自动科研主目录" : index === 1 ? "文档与说明" : index === 2 ? "快速入口" : index === 3 ? "树搜索配置" : "运行入口"}</span>
        </div>
      `,
    )
    .join("");
}

function renderArtifactList() {
  if (!appEls.artifactList) return;
  const artifacts = realWorkflow.artifacts.length ? realWorkflow.artifacts : [
    "experiments/<timestamp_ideaname>/logs/0-run/unified_tree_viz.html",
    "experiments/<timestamp_ideaname>/timestamp_ideaname.pdf",
  ];
  appEls.artifactList.innerHTML = artifacts.map((item) => `<li>${item}</li>`).join("");
}

function renderStageLabels() {
  const stageNames = realWorkflow.stages.length
    ? realWorkflow.stages
    : [
        { name: "Stage 1 初步验证", maxIters: 20 },
        { name: "Stage 2 调参", maxIters: 12 },
        { name: "Stage 3 研究推进", maxIters: 12 },
        { name: "Stage 4 消融", maxIters: 18 },
      ];
  const steps = $$(".timeline-step", appEls.timeline);
  steps.forEach((step, index) => {
    const label = stageNames[index];
    if (!label) return;
    const strong = $("strong", step);
    if (strong) {
      strong.textContent = `${label.name} · ${label.maxIters} 节点`;
    }
  });
}

function seedIntroLogs() {
  appendLog("欢迎", "这个页面把 AI Scientist-v2 变成了一个会动的故事。");
  appendLog("提示", "点击“开始模拟”，你会看到想点子、树搜索、修 bug、写论文的完整循环。");
  appendLog("真实参数", `代码模型是 ${realWorkflow.codeModel}，反馈和审稿主要用 ${realWorkflow.feedbackModel}。`);
  appendLog(
    "真实参数",
    `${realWorkflow.workers} 个 worker、${realWorkflow.execTimeoutSeconds} 秒节点上限、${realWorkflow.stages.length} 个阶段。`,
  );
}

function startDemo() {
  if (state.running) return;
  state.running = true;
  state.stepIndex = 0;
  state.runCount += 1;
  updateControls();
  clearSimulationNodes();
  appendLog("开始", `第 ${state.runCount} 次模拟实验启动。`);
  appendLog("对照", `模拟尽量贴近真实仓库：${realWorkflow.source}。`);
  runCurrentDemo().catch((error) => {
    appendLog("错误", `模拟中断：${error.message}`);
    stopTimer();
    state.running = false;
    updateControls();
  });
}

function stopTimer() {
  if (state.timer) {
    clearTimeout(state.timer);
    state.timer = null;
  }
}

async function runCurrentDemo() {
  const mode = modeInfo[state.difficulty];
  const seed = 20250529 + state.runCount * 1337 + state.difficulty * 97;
  state.rng = mulberry32(seed);

  const idea = pickIdea();
  const title = idea.title;
  const effect = idea.effect + mode.effectBias;
  const bugRoll = state.rng();
  const bugHappens = bugRoll < mode.bugRate;
  const shouldImprove = effect >= 0.08 && !bugHappens;
  const candidateLoss = roundTo(1.52 - effect * 0.9 + (bugHappens ? 0.18 : 0), 3);
  const baselineLoss = roundTo(1.52, 3);
  const delta = roundTo(candidateLoss - baselineLoss, 3);
  const reviewScore = roundTo(6.0 + Math.max(-1.2, Math.min(1.2, -delta * 3.1)) + (bugHappens ? -0.6 : 0.5), 1);
  const accepted = reviewScore >= 6.5 && !bugHappens;
  const abstract =
    `这个演示把 AI Scientist-v2 变成一台“小型科研机器”。它先从主题里找想法，再用树搜索挑更好的实验路线，` +
    `遇到报错会修复，最后把结果写成论文。这里的模拟尽量对齐真实仓库：代码生成使用 ${realWorkflow.codeModel}，` +
    `反馈与审稿主要用 ${realWorkflow.feedbackModel}，写作阶段也主要围绕 ${realWorkflow.reportModel} 展开，` +
    `节点执行时间上限是 ${realWorkflow.execTimeoutSeconds} 秒。` +
    `模拟中，候选实验${delta <= 0 ? "优于" : "略差于"}基线，所以系统会把它继续推向写作阶段。`;

  const paperMarkdown = [
    "# 自动科研演示论文",
    "",
    `**标题：** ${title}`,
    "",
    "**摘要：**",
    "我们用一个可视化演示展示了 AI Scientist-v2 的工作方式：先生成想法，再在树搜索中挑选更优实验节点，",
    "如果实验出错就进入调试分支，最后把结果汇总成论文。",
    "",
    "**实验结果：**",
    `- 基线验证损失：${baselineLoss.toFixed(3)}`,
    `- 候选验证损失：${candidateLoss.toFixed(3)}`,
    `- 差值：${delta > 0 ? "+" : ""}${delta.toFixed(3)}`,
    `- 审稿分数：${reviewScore.toFixed(1)}`,
    `- 审稿结果：${accepted ? "接收" : "拒稿，但保留为负结果"} `,
    "",
    "**解读：**",
    shouldImprove
      ? "树搜索找到了一个更好的实验分支，因此系统会继续把这条路写下去。"
      : "这条实验分支没有明显提升，系统也会如实保留这个负结果。"
      ,
    "",
    "**备注：**",
    bugHappens
      ? "这次运行里有一个明显的 bug，系统先修再继续。"
      : "这次运行没有明显 bug，实验更顺畅。",
  ].join("\n");

  updateTimeline(0);
  renderNode("idea");
  renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 2));
  appendLog("想点子", scripts.idea[0]);
  await sleep(650);
  appendLog("想点子", `生成了 ${realWorkflow.numDrafts} 个候选方向，当前选中的是「${title}」。`);
  pulseStep("idea");
  updateTimeline(1);
  renderNode("search");
  renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 4));
  await sleep(650);

  appendLog("树搜索", scripts.search[0]);
  markNodeDone("idea");
  markNodeActive("search");
  animateTreeSearch(bugHappens);
  appendLog("树搜索", `树搜索借鉴了 ${realWorkflow.treeSearchOrigin} 的思路，会并行探索 ${realWorkflow.workers} 条线。`);
  renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 6));
  await sleep(850);
  appendLog("树搜索", scripts.search[1]);
  await sleep(560);

  if (bugHappens) {
    updateTimeline(2);
    renderNode("debug");
    markNodeError("debug");
    appendLog("修 bug", scripts.debug[0]);
    await sleep(520);
    appendLog("修 bug", "发现一处路径或超参数问题，正在自动修正。");
    await sleep(620);
    appendLog("修 bug", scripts.debug[1]);
    await sleep(620);
    appendLog("修 bug", scripts.debug[2]);
    markNodeDone("debug");
    renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 8));
  } else {
    updateTimeline(2);
    renderNode("tune");
    markNodeDone("search");
    markNodeActive("tune");
    appendLog("调参", "这条实验线跑通了，开始做更细的调参。");
    await sleep(600);
    appendLog("调参", "系统微调学习率、训练轮数和正则强度。");
    await sleep(600);
    markNodeDone("tune");
    renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 8));
  }

  updateTimeline(3);
  renderNode("review");
  markNodeActive("review");
  appendLog("审稿", scripts.review[0]);
  await sleep(600);
  appendLog("审稿", scripts.review[1]);
  await sleep(600);
  appendLog("审稿", `给出模拟评分 ${reviewScore.toFixed(1)} 分；真实系统里这一步主要交给 ${realWorkflow.feedbackModel}。`);
  markNodeDone("review");
  renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 10));
  await sleep(400);

  updateTimeline(4);
  renderNode("paper");
  markNodeActive("paper");
  appendLog("写论文", scripts.paper[0]);
  await sleep(560);
  appendLog("写论文", scripts.paper[1]);
  await sleep(560);
  appendLog("写论文", scripts.paper[2]);
  markNodeDone("paper");
  await sleep(460);

  renderNode("final");
  markNodeDone("final");
  updateMetrics({
    baselineLoss,
    candidateLoss,
    delta,
    reviewScore,
    accepted,
    title,
    abstract,
    paperMarkdown,
  });
  fillPaperPreview(title, abstract, paperMarkdown, accepted, bugHappens);
  appendLog(
    "完成",
    accepted
      ? `模拟论文接收为 workshop 结果；写作与审稿模型对照真实配置 ${realWorkflow.reportModel} / ${realWorkflow.feedbackModel}。`
      : "模拟论文没有接收，但负结果也被保留。",
  );
  renderChart(baselineCurve, buildCandidateCurve(effect, bugHappens, 10));
  state.running = false;
  updateControls();
}

function stepOnce() {
  if (state.running) return;
  const next = stageOrder[state.stepIndex] || "paper";
  state.stepIndex = Math.min(stageOrder.length - 1, state.stepIndex + 1);
  updateTimeline(state.stepIndex);
  renderNode(next);
  pulseStep(next);
  appendLog("单步", `你推进了 ${stageCopy[next].title}。`);
}

function updateControls() {
  appEls.run.disabled = state.running;
  appEls.run2.disabled = state.running;
  appEls.step.disabled = state.running;
  appEls.reset.disabled = state.running;
  appEls.difficulty.disabled = state.running;
}

function updateTimeline(activeIndex = state.stepIndex) {
  const steps = $$(".timeline-step", appEls.timeline);
  steps.forEach((stepEl, index) => {
    stepEl.classList.toggle("active", index === activeIndex);
    stepEl.classList.toggle("done", index < activeIndex);
  });
}

function renderNode(key) {
  state.currentNode = key;
  appEls.treeNodes.forEach((node) => {
    const nodeKey = node.dataset.node;
    node.classList.toggle("active", nodeKey === key);
  });
  const selected = nodeInfo[key];
  if (selected) {
    appendLog("节点", `${selected.title}：${selected.body}`);
  }
}

function markNodeDone(key) {
  const node = findNode(key);
  if (!node) return;
  node.classList.remove("error", "active");
  node.classList.add("done");
}

function markNodeActive(key) {
  const node = findNode(key);
  if (!node) return;
  node.classList.remove("error");
  node.classList.add("active");
}

function markNodeError(key) {
  const node = findNode(key);
  if (!node) return;
  node.classList.remove("done", "active");
  node.classList.add("error");
}

function clearSimulationNodes() {
  appEls.treeNodes.forEach((node) => node.classList.remove("done", "active", "error"));
  renderNode("root");
}

function animateTreeSearch(bugHappens) {
  const searchNode = findNode("search");
  if (!searchNode) return;
  searchNode.classList.add("active");
  setTimeout(() => {
    if (!bugHappens) {
      markNodeDone("search");
      markNodeActive("tune");
    }
  }, 1200);
}

function pulseStep(stepKey) {
  const step = $(`.timeline-step[data-step="${stepKey}"]`, appEls.timeline);
  if (!step) return;
  step.animate(
    [
      { transform: "translateX(0)" },
      { transform: "translateX(5px)" },
      { transform: "translateX(0)" },
    ],
    {
      duration: 420,
      easing: "ease-out",
    },
  );
}

function fillPaperPreview(title, abstract, markdown, accepted, bugHappens) {
  appEls.paperTitle.textContent = accepted ? `接收倾向：${title}` : `负结果论文：${title}`;
  appEls.paperAbstract.textContent = abstract;
  appEls.paperBody.textContent = markdown + "\n\n" + (bugHappens ? "这次演示里有一个 bug，系统先修后写。" : "这次演示里没有明显 bug。");
}

function updateMetrics(data) {
  if (!data) {
    appEls.baselineMetric.textContent = "--";
    appEls.candidateMetric.textContent = "--";
    appEls.deltaMetric.textContent = "--";
    appEls.reviewMetric.textContent = "等待运行";
    return;
  }
  appEls.baselineMetric.textContent = data.baselineLoss.toFixed(3);
  appEls.candidateMetric.textContent = data.candidateLoss.toFixed(3);
  appEls.deltaMetric.textContent = `${data.delta > 0 ? "+" : ""}${data.delta.toFixed(3)}`;
  appEls.reviewMetric.textContent = data.accepted ? "接收" : "拒稿";
}

function appendLog(kind, message) {
  const template = appEls.logTemplate.content.firstElementChild.cloneNode(true);
  template.querySelector(".time").textContent = timeStamp();
  template.querySelector(".msg").textContent = `${kind}：${message}`;
  appEls.logStream.prepend(template);
}

function renderChart(baseline, candidate) {
  const svg = appEls.lossChart;
  if (!svg) return;
  const width = 520;
  const height = 220;
  const pad = { left: 40, right: 18, top: 16, bottom: 26 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const allValues = baseline.concat(candidate.length ? candidate : baseline);
  const min = Math.min(...allValues) - 0.04;
  const max = Math.max(...allValues) + 0.04;
  const scaleX = (i, total) => pad.left + (total <= 1 ? 0 : (i / (total - 1)) * plotW);
  const scaleY = (v) => pad.top + (1 - (v - min) / (max - min)) * plotH;
  const lineFor = (values) =>
    values
      .map((value, index) => `${index === 0 ? "M" : "L"} ${scaleX(index, values.length).toFixed(1)} ${scaleY(value).toFixed(1)}`)
      .join(" ");
  const areaFor = (values) => {
    if (!values.length) return "";
    const startX = scaleX(0, values.length).toFixed(1);
    const endX = scaleX(values.length - 1, values.length).toFixed(1);
    const baselineY = scaleY(min).toFixed(1);
    return `${lineFor(values)} L ${endX} ${baselineY} L ${startX} ${baselineY} Z`;
  };
  const axis = `
    <line class="chart-axis" x1="${pad.left}" y1="${pad.top}" x2="${pad.left}" y2="${pad.top + plotH}"></line>
    <line class="chart-axis" x1="${pad.left}" y1="${pad.top + plotH}" x2="${pad.left + plotW}" y2="${pad.top + plotH}"></line>
    <text x="${pad.left}" y="${height - 6}" fill="#a7b3ca" font-size="11">训练步数 →</text>
    <text x="10" y="${pad.top + 8}" fill="#a7b3ca" font-size="11">损失 ↓</text>
  `;
  const baselinePath = lineFor(baseline);
  const candidatePath = candidate.length ? lineFor(candidate) : "";
  const candidateFill = candidate.length ? areaFor(candidate) : "";
  svg.innerHTML = `
    <defs>
      <linearGradient id="candidateFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#7ce7d6" stop-opacity="0.4"></stop>
        <stop offset="100%" stop-color="#7ce7d6" stop-opacity="0"></stop>
      </linearGradient>
    </defs>
    ${axis}
    ${candidateFill ? `<path class="chart-fill" d="${candidateFill}" fill="url(#candidateFill)"></path>` : ""}
    <path class="chart-line baseline" d="${baselinePath}"></path>
    ${candidatePath ? `<path class="chart-line candidate" d="${candidatePath}"></path>` : ""}
    <g>
      <circle cx="${scaleX(0, baseline.length)}" cy="${scaleY(baseline[0])}" r="3.5" fill="#64b5ff"></circle>
      <circle cx="${scaleX(baseline.length - 1, baseline.length)}" cy="${scaleY(baseline[baseline.length - 1])}" r="3.5" fill="#64b5ff"></circle>
      ${candidate.length ? `<circle cx="${scaleX(candidate.length - 1, candidate.length)}" cy="${scaleY(candidate[candidate.length - 1])}" r="4" fill="#7ce7d6"></circle>` : ""}
    </g>
    <g transform="translate(${width - 160}, ${pad.top + 8})">
      <rect x="0" y="0" width="146" height="32" rx="12" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.08)"></rect>
      <circle cx="16" cy="16" r="5" fill="#64b5ff"></circle>
      <text x="30" y="20" fill="#eef4ff" font-size="12">基线</text>
      <circle cx="78" cy="16" r="5" fill="#7ce7d6"></circle>
      <text x="92" y="20" fill="#eef4ff" font-size="12">候选</text>
    </g>
  `;
}

function buildCandidateCurve(effect, bugHappens, progressCount) {
  const target = baselineCurve.map((base, index) => {
    const trend = effect * (index / (baselineCurve.length - 1)) * 0.9;
    const bump = bugHappens ? 0.05 + index * 0.004 : -0.03;
    const wobble = (index % 3 === 0 ? 0.01 : -0.01) * (bugHappens ? 1 : -1);
    return roundTo(base - trend + bump + wobble, 3);
  });
  const count = Math.max(2, Math.min(target.length, progressCount));
  return target.slice(0, count);
}

function findNode(key) {
  return appEls.treeNodes.find((node) => node.dataset.node === key);
}

function pickIdea() {
  const ideas = [
    {
      title: "更稳的学习率",
      effect: 0.14,
    },
    {
      title: "更长的上下文窗口",
      effect: 0.08,
    },
    {
      title: "更小的隐藏层",
      effect: -0.04,
    },
    {
      title: "更强的正则化",
      effect: 0.04,
    },
    {
      title: "加入注意力模块",
      effect: 0.18,
    },
  ];
  return ideas[Math.floor(state.rng() * ideas.length)];
}

function roundTo(value, digits) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function timeStamp() {
  const now = new Date();
  return now.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function sleep(ms) {
  return new Promise((resolve) => {
    state.timer = setTimeout(resolve, ms);
  });
}

function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function clearTimer(timerId) {
  clearTimeout(timerId);
}

window.addEventListener("beforeunload", () => {
  if (state.timer) {
    clearTimer(state.timer);
  }
});
