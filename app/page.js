"use client";

const sources = [
  ["arXiv", "https://arxiv.org/abs/2511.08892"],
  ["项目页", "https://www.lumine-ai.org/"],
  ["PDF", "https://www.lumine-ai.org/Lumine.pdf"],
];

const trainingStages = [
  {
    title: "1. 行为预训练",
    value: "1731h",
    text: "从 2424 小时人类游玩记录中过滤静止与抖动片段，让模型先学会基础动作、镜头控制、战斗反应和移动习惯。",
  },
  {
    title: "2. 指令跟随",
    value: "200h",
    text: "把行为和自然语言目标对齐，让模型能理解“去找某个 NPC”“击败敌人并开宝箱”等短任务。",
  },
  {
    title: "3. 混合推理",
    value: "15h",
    text: "用人工标注的第一人称内心独白训练模型在关键节点思考，避免每一步都推理带来的延迟。",
  },
];

const abilities = [
  ["采集", "找物品、开宝箱、收集空中/墙面目标，需要空间定位和细粒度控制。"],
  ["战斗", "追踪敌人、切角色、释放组合技能、规避攻击，同时记得战后领取奖励。"],
  ["解谜", "识别机关、元素互动、限时挑战和环境依赖，要求观察、机制理解和执行精度。"],
  ["NPC/GUI", "在复杂人群里找指定 NPC，并能操作地图、传送、烹饪、武器界面等 2D GUI。"],
];

const comparisons = [
  ["蒙德 Act I", "56 分钟", "接近专家玩家，优于新手平均 78 分钟"],
  ["蒙德 Act II/III", "4.7 小时", "推理数据未覆盖，仍能完成长任务链"],
  ["鸣潮", "107 分钟", "零微调完成约 100 分钟主线任务"],
  ["崩坏：星穹铁道", "7 小时", "跨到回合制/箱庭环境，完成黑塔空间站章节"],
];

const limits = [
  "训练集中预训练主要限制在蒙德区域，推理数据只覆盖第一小时主线；跨区域和跨游戏仍需要更大规模数据验证。",
  "长期记忆目前较朴素：近期 20 帧作为短期上下文，最近推理作为长期线索；复杂任务需要更可靠的检索和压缩。",
  "模型仍有领域偏置和幻觉，例如把新游戏里的对象叫成原神术语，或误读屏幕按键提示。",
  "实时推理依赖多 GPU 加速，推理延迟仍是系统扩展、在线 RL 和真实交互部署的关键瓶颈。",
];

function FlowAnimation() {
  return (
    <div className="flowCard" aria-label="Lumine perception reasoning action animation">
      <div className="worldPanel">
        <div className="sky" />
        <div className="mountain m1" />
        <div className="mountain m2" />
        <div className="avatarDot" />
        <div className="targetDot" />
        <div className="scanLine" />
      </div>
      <div className="pipeline">
        <span>像素 5Hz</span>
        <i />
        <span>VLM</span>
        <i />
        <span>必要时思考</span>
        <i />
        <span>动作 30Hz</span>
      </div>
      <div className="keyboard">
        {["W", "Shift", "E", "Q", "F", "Mouse"].map((key) => (
          <b key={key}>{key}</b>
        ))}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <main className="luminePage">
      <section className="hero">
        <div className="heroText">
          <p className="eyebrow">ByteDance Seed · Lumine · 3D Open-World Agents</p>
          <h1>一篇论文说明白：Lumine 如何把大模型训练成会“玩开放世界”的通用智能体</h1>
          <p className="lead">
            Lumine 的核心贡献不是“AI 会玩原神”这个表面现象，而是一套可复用的工程配方：
            让视觉语言模型直接看像素、按语言目标行动、在关键节点推理，并在实时延迟约束下输出键鼠控制。
          </p>
          <div className="sourceRow">
            {sources.map(([label, href]) => (
              <a key={label} href={href} target="_blank" rel="noreferrer">
                {label}
              </a>
            ))}
          </div>
        </div>
        <FlowAnimation />
      </section>

      <section className="metricStrip" aria-label="关键指标">
        <div><strong>Qwen2-VL-7B</strong><span>底座模型</span></div>
        <div><strong>5 Hz</strong><span>像素观察</span></div>
        <div><strong>30 Hz</strong><span>键鼠动作</span></div>
        <div><strong>141</strong><span>语言条件任务</span></div>
      </section>

      <section className="section introGrid">
        <div>
          <p className="eyebrow">01 · 论文要解决什么</p>
          <h2>从封闭游戏智能体，走向开放世界通用智能体</h2>
          <p>
            过去很多游戏 AI 在规则清晰、奖励明确、环境封闭的任务中表现很强，但这种能力很难迁移。
            开放世界不同：任务链很长、目标经常变化、GUI 和 3D 场景混在一起、需要记忆路线、还要实时反应。
          </p>
          <p>
            Lumine 把问题重新定义为一个统一接口：输入屏幕像素和历史上下文，输出文本化的键盘鼠标动作。
            这使模型不需要游戏内部 API，也不需要额外动作头，更接近真实人类玩家的交互方式。
          </p>
        </div>
        <div className="challengeList">
          {["可扩展环境", "多模态感知", "高层规划", "低层控制", "长短期记忆", "实时推理"].map((item, index) => (
            <span style={{ "--delay": `${index * 0.12}s` }} key={item}>{item}</span>
          ))}
        </div>
      </section>

      <section className="section">
        <p className="eyebrow">02 · 模型怎么运转</p>
        <h2>感知、推理、行动，不是三套系统，而是一条自回归序列</h2>
        <div className="mechanism">
          <div className="pulseBox">
            <div className="clockRing"><span>200ms</span></div>
            <p>每 200ms 取一帧，也就是 5Hz 观察频率。这个频率接近人类视觉反应时间，同时控制计算成本。</p>
          </div>
          <div className="thoughtBox">
            <span className="token">{"<thought_start>"}</span>
            <p>我需要先击败敌人，再打开解锁的宝箱。</p>
            <span className="token">{"<action_start>"}</span>
            <p className="actionText">92 0 0 ; Shift W ; Shift W ; F W ; F</p>
          </div>
          <div className="pulseBox">
            <div className="actionWave">
              <i /><i /><i /><i /><i /><i />
            </div>
            <p>每一步输出 6 个动作块，每块约 33ms，形成 30Hz 键鼠控制，能表达长按、短按、连击和鼠标移动。</p>
          </div>
        </div>
      </section>

      <section className="section dark">
        <p className="eyebrow">03 · 训练配方</p>
        <h2>三阶段课程学习：先像人一样动，再听懂人话，最后学会在关键时刻思考</h2>
        <div className="stageRail">
          {trainingStages.map((stage, index) => (
            <article key={stage.title} className="stageCard" style={{ "--delay": `${index * 0.2}s` }}>
              <span>{stage.value}</span>
              <h3>{stage.title}</h3>
              <p>{stage.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section">
        <p className="eyebrow">04 · 评测结果</p>
        <h2>不是只看一段演示，而是用任务集和长剧情检验能力</h2>
        <div className="abilityGrid">
          {abilities.map(([title, text], index) => (
            <article key={title} className="abilityCard" style={{ "--delay": `${index * 0.1}s` }}>
              <div className="orb">{index + 1}</div>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
        <div className="comparison">
          {comparisons.map(([name, value, text]) => (
            <div key={name}>
              <strong>{value}</strong>
              <span>{name}</span>
              <p>{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section split">
        <div>
          <p className="eyebrow">05 · 为什么值得重视</p>
          <h2>Lumine 更像“具身 Agent 的工程样板”，不是单一游戏 bot</h2>
          <p>
            论文真正值得关注的是 recipe：如何选环境、采集数据、过滤轨迹、设计动作表示、加入语言目标、
            标注推理、管理上下文、压低延迟，并最终验证跨任务和跨游戏迁移。
          </p>
          <p>
            这对未来的 AI Agent 研究有直接启发：很多真实任务也不是一次性问答，而是长时间观察、操作 GUI、
            处理意外、修正计划和保持目标一致性。Lumine 把这些难点放到一个高复杂度虚拟环境中验证。
          </p>
        </div>
        <div className="transferMap">
          <span>原神</span>
          <i />
          <span>鸣潮</span>
          <i />
          <span>星穹铁道</span>
          <i />
          <span>更多 3D/GUI 任务</span>
        </div>
      </section>

      <section className="section limits">
        <p className="eyebrow">06 · 不能忽略的限制</p>
        <h2>结论要克制：它展示了路径，但还不是完全通用智能体</h2>
        {limits.map((item) => (
          <p key={item}>{item}</p>
        ))}
      </section>

      <section className="section takeaway">
        <p className="eyebrow">最终判断</p>
        <h2>如果把 Lumine 用一句话概括</h2>
        <p>
          Lumine 证明了：在足够复杂的 3D 开放世界里，只要把人类行为数据、语言指令、关键节点推理和实时动作表示组织成正确的训练配方，
          一个中等规模 VLM 可以从“看图说话”转向“看屏幕、想目标、按键鼠、完成长任务”。
        </p>
      </section>
    </main>
  );
}
