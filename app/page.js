"use client";

import { useEffect, useMemo, useState } from "react";

const fieldGroups = [
  {
    title: "身体与动作",
    fields: [
      ["dominant_frame", "主导身体框架"],
      ["body_visibility", "身体可见性"],
      ["body_count", "出镜人数"],
      ["movement_tempo", "动作节奏"],
      ["camera_relation", "镜头关系"],
      ["text_occlusion", "文字遮挡"],
      ["origin_reference", "来源/正统性引用"],
    ],
  },
  {
    title: "身体经验线索",
    fields: [
      ["breath_cue", "呼吸提示"],
      ["mind_cue", "意念/放松提示"],
      ["qi_meridian_cue", "气/经络提示"],
      ["risk_cue", "风险/禁忌提示"],
      ["call_to_action", "行动号召"],
      ["platform_trace", "平台踪迹"],
    ],
  },
  {
    title: "平台传播机制",
    fields: [
      ["supplement_mode", "平台补充方式"],
      ["binary_reversal", "二元反转/张力结构"],
      ["recontextualization_scene", "再语境化场景"],
      ["visibility_centrality", "可视性中心化"],
      ["tempo_discipline", "节奏规训"],
    ],
  },
  {
    title: "意义延异变量",
    fields: [
      ["efficacy_tagging", "功效标签化"],
      ["image_trace_strength", "影像痕迹强度"],
      ["media_temporality", "媒介时间性"],
      ["cyber_wellness_symbol", "赛博养生符号"],
      ["meme_density", "玩梗密度"],
      ["embodied_dissolution", "具身消解"],
    ],
  },
];

const options = {
  dominant_frame: [
    ["instructional_body", "教学身体"],
    ["therapeutic_body", "疗愈/健康身体"],
    ["cultural_body", "文化身体"],
    ["spectacular_body", "景观/表演身体"],
    ["social_body", "社交身体"],
    ["commercial_body", "商业身体"],
    ["unclear", "无法判断"],
  ],
  body_visibility: [
    ["full_body", "全身可见"],
    ["upper_body", "上半身为主"],
    ["partial", "局部/遮挡"],
    ["close_up", "特写/口播为主"],
    ["unclear", "无法判断"],
  ],
  body_count: [["single", "单人"], ["two_three", "2-3人"], ["group", "多人/群体"], ["unclear", "无法判断"]],
  movement_tempo: [
    ["slow_continuous", "慢速连续跟练"],
    ["segmented_teaching", "分段教学"],
    ["fast_montage", "快速剪辑/加速"],
    ["mixed", "混合"],
    ["unclear", "无法判断"],
  ],
  camera_relation: [
    ["frontal_teaching", "正面教学/跟练"],
    ["side_demo", "侧面示范"],
    ["group_panorama", "群体全景"],
    ["cinematic", "审美/表演镜头"],
    ["talking_head", "口播/头肩画面"],
    ["mixed", "混合"],
    ["unclear", "无法判断"],
  ],
  text_occlusion: [["none", "无"], ["low", "低"], ["medium", "中"], ["high", "高"], ["unclear", "无法判断"]],
  breath_cue: [["0", "无"], ["1", "有"]],
  mind_cue: [["0", "无"], ["1", "有"]],
  qi_meridian_cue: [["0", "无"], ["1", "有"]],
  risk_cue: [["0", "无"], ["1", "有"]],
  call_to_action: [
    ["none", "无"],
    ["follow_along", "跟练"],
    ["check_in", "打卡"],
    ["buy_course", "购买课程/引流"],
    ["share_collect", "分享/收藏"],
    ["unclear", "无法判断"],
  ],
  platform_trace: [
    ["none", "无"],
    ["hashtag", "标签话题"],
    ["hot_music", "热门音乐"],
    ["bullet_comment", "弹幕/评论可见"],
    ["duet_remix", "合拍/混剪/二创"],
    ["live_stream", "直播"],
    ["unclear", "无法判断"],
  ],
  origin_reference: [
    ["none", "无明显来源"],
    ["official_routine", "官方套路/标准功法"],
    ["master_teacher", "名师/师承"],
    ["ancient_tradition", "古法/传统"],
    ["national_culture", "民族/国家文化"],
    ["medical_health", "医学/健康话语"],
    ["unclear", "无法判断"],
  ],
  supplement_mode: [
    ["none", "无明显补充"],
    ["caption", "字幕补充"],
    ["slow_motion", "慢动作/分解"],
    ["split_screen", "分屏对照"],
    ["comment_checkin", "评论/打卡互动"],
    ["hashtag_topic", "标签话题再语境化"],
    ["commercial_link", "商业链接/引流"],
    ["ai_filter", "AI滤镜/特效"],
    ["music_edit", "音乐剪辑再语境化"],
    ["mixed", "混合"],
    ["unclear", "无法判断"],
  ],
  binary_reversal: [
    ["none", "无明显反转"],
    ["teaching_performance", "教学/表演反转"],
    ["tradition_modern", "传统/现代反转"],
    ["inner_outer", "内在气感/外在形态反转"],
    ["health_traffic", "健康/流量反转"],
    ["master_influencer", "师承/网红反转"],
    ["slow_fast", "慢练/快节奏反转"],
    ["unclear", "无法判断"],
  ],
  recontextualization_scene: [
    ["home_fitness", "居家健身"],
    ["public_square", "广场/公共空间"],
    ["scenic_spot", "景区/自然空间"],
    ["classroom", "课堂/教学场"],
    ["studio", "工作室/棚拍"],
    ["commerce", "商业/课程场景"],
    ["challenge", "挑战/热点场景"],
    ["unclear", "无法判断"],
  ],
  visibility_centrality: [["low", "低"], ["medium", "中"], ["high", "高"], ["unclear", "无法判断"]],
  tempo_discipline: [["slow_media", "慢媒体/慢教学"], ["balanced", "相对均衡"], ["accelerated", "加速"], ["montage", "剪辑化"], ["unclear", "无法判断"]],
  efficacy_tagging: [["none", "无"], ["mild_health", "温和养生"], ["strong_health", "强功效健康"], ["medicalized", "医学化/治疗化"], ["anxiety_marketing", "焦虑营销"], ["unclear", "无法判断"]],
  image_trace_strength: [["none", "无"], ["weak", "弱"], ["moderate", "中等"], ["strong", "强"], ["unclear", "无法判断"]],
  media_temporality: [["continuous", "连续"], ["fragmented", "碎片化"], ["looped", "循环"], ["hot_trend", "热点/挑战"], ["live_stream", "直播"], ["mixed", "混合"], ["unclear", "无法判断"]],
  cyber_wellness_symbol: [["0", "无"], ["1", "有"]],
  meme_density: [["none", "无"], ["low", "低"], ["medium", "中"], ["high", "高"], ["unclear", "无法判断"]],
  embodied_dissolution: [["none", "无"], ["weak", "弱"], ["moderate", "中等"], ["strong", "强"], ["unclear", "无法判断"]],
};

const blankForm = {
  dominant_frame: "",
  secondary_frames: "",
  body_visibility: "",
  body_count: "",
  movement_tempo: "",
  camera_relation: "",
  text_occlusion: "",
  breath_cue: "",
  mind_cue: "",
  qi_meridian_cue: "",
  risk_cue: "",
  call_to_action: "",
  platform_trace: "",
  origin_reference: "",
  supplement_mode: "",
  binary_reversal: "",
  recontextualization_scene: "",
  visibility_centrality: "",
  tempo_discipline: "",
  efficacy_tagging: "",
  image_trace_strength: "",
  media_temporality: "",
  cyber_wellness_symbol: "",
  meme_density: "",
  embodied_dissolution: "",
  trace_markers: "",
  notes: "",
  watched: false,
  video_access_status: "opened",
};

const studentCodes = Array.from({ length: 10 }, (_, i) => `STU${String(i + 1).padStart(2, "0")}`);

export default function Page() {
  const [session, setSession] = useState(null);
  const [login, setLogin] = useState({ student_name: "", student_code: "STU01", access_code: "" });
  const [tasks, setTasks] = useState([]);
  const [activeId, setActiveId] = useState("");
  const [form, setForm] = useState(blankForm);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const raw = localStorage.getItem("qigongCodingSession");
    if (raw) setSession(JSON.parse(raw));
  }, []);

  useEffect(() => {
    if (!session) return;
    fetchTasks(session);
  }, [session]);

  const activeTask = useMemo(() => tasks.find((task) => task.video_id === activeId), [tasks, activeId]);
  const completed = tasks.filter((task) => task.my_submission).length;

  async function submitLogin(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(login),
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) {
      setMessage(data.error || "登录失败");
      return;
    }
    localStorage.setItem("qigongCodingSession", JSON.stringify(data.session));
    setSession(data.session);
  }

  async function fetchTasks(currentSession) {
    setLoading(true);
    const res = await fetch(`/api/tasks?student_code=${encodeURIComponent(currentSession.student_code)}`, {
      headers: { "x-student-token": currentSession.token },
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) {
      setMessage(data.error || "任务加载失败");
      return;
    }
    setTasks(data.tasks);
    const first = data.tasks.find((task) => !task.my_submission) || data.tasks[0];
    if (first) selectTask(first);
  }

  function selectTask(task) {
    setActiveId(task.video_id);
    setForm({ ...blankForm, ...(task.my_submission || {}) });
  }

  async function saveSubmission(event) {
    event.preventDefault();
    if (!activeTask || !session) return;
    setLoading(true);
    setMessage("");
    const res = await fetch("/api/submissions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-student-token": session.token },
      body: JSON.stringify({
        student_code: session.student_code,
        student_name: session.student_name,
        video_id: activeTask.video_id,
        task_role: activeTask.task_role,
        ...form,
      }),
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) {
      setMessage(data.error || "提交失败");
      return;
    }
    setMessage("已保存。可以继续下一条。");
    await fetchTasks(session);
  }

  function logout() {
    localStorage.removeItem("qigongCodingSession");
    setSession(null);
    setTasks([]);
    setActiveId("");
  }

  if (!session) {
    return (
      <main className="loginPage">
        <section className="loginPanel">
          <p className="eyebrow">西南科技大学体育学院 · 健身气功短视频研究</p>
          <h1>人工编码登录</h1>
          <p className="lead">请输入姓名、学生编号和老师提供的访问口令。系统会自动分配你需要观看和编码的视频任务。</p>
          <form className="loginForm" onSubmit={submitLogin}>
            <label>
              姓名
              <input value={login.student_name} onChange={(e) => setLogin({ ...login, student_name: e.target.value })} required />
            </label>
            <label>
              学生编号
              <select value={login.student_code} onChange={(e) => setLogin({ ...login, student_code: e.target.value })}>
                {studentCodes.map((code) => <option key={code}>{code}</option>)}
              </select>
            </label>
            <label>
              访问口令
              <input type="password" value={login.access_code} onChange={(e) => setLogin({ ...login, access_code: e.target.value })} required />
            </label>
            <button disabled={loading}>{loading ? "登录中..." : "进入编码平台"}</button>
            {message && <p className="error">{message}</p>}
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <p className="eyebrow">健身气功短视频</p>
          <h1>人工编码平台</h1>
        </div>
        <div className="studentBox">
          <strong>{session.student_name}</strong>
          <span>{session.student_code}</span>
          <button onClick={logout}>退出</button>
        </div>
        <div className="progressBox">
          <span>我的进度</span>
          <strong>{completed} / {tasks.length}</strong>
        </div>
        <div className="taskList">
          {tasks.map((task) => (
            <button key={task.video_id} className={task.video_id === activeId ? "active" : ""} onClick={() => selectTask(task)}>
              <span>{task.priority}. {task.video_id}</span>
              <small>{task.platform} · {task.keyword} {task.my_submission ? "· 已填" : ""}</small>
            </button>
          ))}
        </div>
      </aside>

      <section className="content">
        <section className="instructions">
          <h2>填报说明</h2>
          <ol>
            <li>先点击“打开视频”，至少看完能判断动作、字幕、口令、剪辑节奏和标题标签的部分。</li>
            <li>LLM 建议只能作参考，最终编码以你的人工观看判断为准。</li>
            <li>看不到视频或证据不足时填“无法判断”，不要凭标题硬猜。</li>
            <li>备注只写匿名化证据短语，例如“口令跟练;呼吸提示”“热歌快剪;全身可见”。</li>
          </ol>
        </section>

        {activeTask ? (
          <form className="codingForm" onSubmit={saveSubmission}>
            <section className="videoHeader">
              <div>
                <p className="eyebrow">{activeTask.platform} · {activeTask.keyword} · {activeTask.task_role}</p>
                <h2>{activeTask.title}</h2>
                <p>{activeTask.hashtags}</p>
              </div>
              {activeTask.video_url ? (
                <a className="videoButton" href={activeTask.video_url} target="_blank" rel="noreferrer" onClick={() => setForm({ ...form, watched: true })}>打开视频</a>
              ) : (
                <span className="missingLink">缺视频链接，暂缓编码</span>
              )}
            </section>

            <section className="suggestionBox">
              <strong>辅助建议</strong>
              <p>{activeTask.llm_rationale || "无"}</p>
            </section>

            <label className="checkboxLine">
              <input type="checkbox" checked={Boolean(form.watched)} onChange={(e) => setForm({ ...form, watched: e.target.checked })} />
              我已经打开并观看/核验了该视频
            </label>

            {fieldGroups.map((group) => (
              <section className="fieldGroup" key={group.title}>
                <h3>{group.title}</h3>
                <div className="fieldGrid">
                  {group.fields.map(([name, label]) => (
                    <label key={name}>
                      {label}
                      <select value={form[name] || ""} onChange={(e) => setForm({ ...form, [name]: e.target.value })} required>
                        <option value="">请选择</option>
                        {(options[name] || []).map(([value, text]) => <option value={value} key={value}>{text}（{value}）</option>)}
                      </select>
                    </label>
                  ))}
                </div>
              </section>
            ))}

            <section className="fieldGroup">
              <h3>证据记录</h3>
              <div className="textGrid">
                <label>
                  次要身体框架
                  <input value={form.secondary_frames || ""} onChange={(e) => setForm({ ...form, secondary_frames: e.target.value })} placeholder="可选，如：therapeutic_body;cultural_body" />
                </label>
                <label>
                  证据标记
                  <textarea value={form.trace_markers || ""} onChange={(e) => setForm({ ...form, trace_markers: e.target.value })} placeholder="如：口令跟练;呼吸提示" />
                </label>
                <label>
                  备注
                  <textarea value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="如：热歌快剪;全身可见" />
                </label>
              </div>
            </section>

            <div className="actions">
              <button type="submit" disabled={loading || !activeTask.video_url}>{loading ? "保存中..." : "保存本条编码"}</button>
              {message && <span>{message}</span>}
            </div>
          </form>
        ) : (
          <p>正在加载任务...</p>
        )}
      </section>
    </main>
  );
}
