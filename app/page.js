"use client";

import { useEffect, useMemo, useRef, useState } from "react";

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

const voiceScript = [
  "欢迎收听这期中文语音博客。今天我们解读 ByteDance Seed 的论文 Lumine：一个面向三维开放世界的通用智能体训练配方。",
  "这篇论文的重点，不是简单地做一个游戏脚本。Lumine 试图回答一个更基础的问题：视觉语言模型能不能像人类玩家一样，看屏幕、理解目标、规划路线，并用键盘鼠标完成连续数小时的复杂任务。",
  "Lumine 的底座是 Qwen2-VL-7B。它每两百毫秒读取一帧屏幕，也就是五赫兹的视觉输入；同时输出三十赫兹的键鼠动作，覆盖移动、点击、长按、角色切换和界面操作。",
  "论文最关键的设计是混合推理。模型不是每一步都长篇思考，而是在任务完成、目标变化、环境突发变化、路线丢失这类关键节点，才生成类似人类内心独白的推理，然后继续输出动作。",
  "训练配方分三步。第一步，用一千七百三十一小时人类游玩数据做行为预训练，让模型掌握基础动作和环境反应。第二步，用两百小时指令跟随数据，把动作和自然语言目标对齐。第三步，用十五小时人工标注的推理数据，让模型学会在长任务中主动思考和修正计划。",
  "评测也不是只看演示视频。论文构建了一百四十一个语言条件任务，覆盖采集、战斗、NPC 交互和解谜。Lumine 在简单任务上达到超过八成成功率，并能完成蒙德主线第一幕。",
  "更值得注意的是跨游戏泛化。Lumine 只用原神数据训练，却能零微调迁移到鸣潮和崩坏：星穹铁道。它会犯错，比如误读按键提示，或者把新游戏角色叫成原神里的名字，但仍然展示了可迁移的三维导航、GUI 操作和任务执行能力。",
  "这篇论文的研究价值在于，它给出了一个完整工程样板：环境选择、数据采集、轨迹过滤、动作表示、语言对齐、推理标注、上下文管理和实时推理优化。这些环节组合起来，比单个模型结构创新更重要。",
  "但结论也要克制。Lumine 还不是完全通用智能体。它的预训练主要集中在蒙德区域，长期记忆机制仍然简单，实时推理依赖多 GPU 加速，并且仍存在领域偏置和幻觉。",
  "如果用一句话总结：Lumine 证明了，一个中等规模视觉语言模型，只要训练配方设计得足够完整，就有可能从看图说话，走向看屏幕、想目标、按键鼠、完成长任务。这对未来具身智能体和通用 GUI Agent 都有直接启发。",
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

function VoiceBlog() {
  const [supported, setSupported] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [rate, setRate] = useState(0.92);
  const cancelRef = useRef(false);

  const progress = useMemo(() => Math.round(((current + (playing ? 1 : 0)) / voiceScript.length) * 100), [current, playing]);

  useEffect(() => {
    setSupported(typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window);
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function pickChineseVoice() {
    const voices = window.speechSynthesis.getVoices();
    return voices.find((voice) => voice.lang?.toLowerCase().startsWith("zh")) || voices.find((voice) => /chinese|mandarin|中文/i.test(voice.name)) || null;
  }

  function speakFrom(index) {
    if (!supported) return;
    window.speechSynthesis.cancel();
    cancelRef.current = false;
    setPlaying(true);
    setCurrent(index);

    const speakNext = (nextIndex) => {
      if (cancelRef.current || nextIndex >= voiceScript.length) {
        setPlaying(false);
        setCurrent(Math.min(nextIndex, voiceScript.length - 1));
        return;
      }
      setCurrent(nextIndex);
      const utterance = new SpeechSynthesisUtterance(voiceScript[nextIndex]);
      utterance.lang = "zh-CN";
      utterance.rate = rate;
      utterance.pitch = 1;
      utterance.volume = 1;
      const voice = pickChineseVoice();
      if (voice) utterance.voice = voice;
      utterance.onend = () => speakNext(nextIndex + 1);
      utterance.onerror = () => {
        setPlaying(false);
      };
      window.speechSynthesis.speak(utterance);
    };

    speakNext(index);
  }

  function pause() {
    if (!supported) return;
    window.speechSynthesis.pause();
    setPlaying(false);
  }

  function resume() {
    if (!supported) return;
    window.speechSynthesis.resume();
    setPlaying(true);
  }

  function stop() {
    if (!supported) return;
    cancelRef.current = true;
    window.speechSynthesis.cancel();
    setPlaying(false);
    setCurrent(0);
  }

  return (
    <section className="section voiceBlog" id="voice-blog">
      <div className="voiceHeader">
        <div>
          <p className="eyebrow">中文语音博客 · Browser TTS</p>
          <h2>点击播放，用中文听完这篇论文的核心逻辑</h2>
          <p>
            这里集成的是浏览器内置中文 TTS。它不需要服务器端语音模型或 API key，移动端也能播放；不同设备会使用各自系统可用的中文声音。
          </p>
        </div>
        <div className="voiceMeter" aria-label={`播放进度 ${progress}%`}>
          <span>{progress}%</span>
          <i style={{ "--progress": `${progress}%` }} />
        </div>
      </div>

      <div className="voiceControls">
        <button type="button" onClick={() => speakFrom(0)} disabled={!supported}>
          从头播放
        </button>
        <button type="button" onClick={playing ? pause : resume} disabled={!supported}>
          {playing ? "暂停" : "继续"}
        </button>
        <button type="button" onClick={stop} disabled={!supported}>
          停止
        </button>
        <label>
          语速
          <input
            aria-label="语速"
            type="range"
            min="0.75"
            max="1.2"
            step="0.05"
            value={rate}
            onChange={(event) => setRate(Number(event.target.value))}
          />
          <span>{rate.toFixed(2)}x</span>
        </label>
      </div>

      {!supported && <p className="ttsWarning">当前浏览器不支持 Web Speech TTS。建议使用 Chrome、Safari 或 Edge 打开。</p>}

      <div className="scriptList">
        {voiceScript.map((line, index) => (
          <button
            type="button"
            className={index === current ? "active" : ""}
            key={line}
            onClick={() => speakFrom(index)}
            disabled={!supported}
          >
            <span>{String(index + 1).padStart(2, "0")}</span>
            {line}
          </button>
        ))}
      </div>
    </section>
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

      <VoiceBlog />

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
