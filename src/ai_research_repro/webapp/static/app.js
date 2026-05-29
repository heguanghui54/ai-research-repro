(function () {
  const bootstrap = window.__BOOTSTRAP__ || null;
  const state = {
    user: bootstrap?.user || null,
    projects: [],
    runs: [],
    library: [],
    activeProject: null,
    activeRun: null,
    events: [],
    artifacts: [],
    eventSource: null,
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  async function api(path, options = {}) {
    const headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
    const response = await fetch(path, {
      credentials: "same-origin",
      ...options,
      headers,
    });
    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`;
      try {
        const body = await response.json();
        detail = body.detail || body.message || detail;
      } catch (_) {}
      throw new Error(detail);
    }
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return await response.json();
    }
    return await response.text();
  }

  function setMessage(text, kind = "") {
    const el = $("#auth-message") || $("#run-message");
    if (!el) return;
    el.textContent = text || "";
    el.className = `message ${kind}`.trim();
  }

  function esc(text) {
    return String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function formatPayload(payload) {
    if (!payload || typeof payload !== "object") return "";
    return JSON.stringify(payload, null, 2);
  }

  function renderProjects() {
    const root = $("#project-list");
    if (!root) return;
    if (!state.projects.length) {
      root.innerHTML = `<div class="project-item"><div class="title">No projects yet</div><div class="meta">Create a research project to begin.</div></div>`;
      return;
    }
    root.innerHTML = state.projects
      .map(
        (project) => `
        <button class="project-item ${state.activeProject?.id === project.id ? "active" : ""}" data-project-id="${project.id}">
          <div class="title">${esc(project.name)}</div>
          <div class="meta">${esc(project.topic.slice(0, 120))}</div>
          <div class="meta">${esc(project.model_name)} · ${esc(project.experiment_template)} · ${esc(project.compute_backend || "local-cpu")}</div>
        </button>
      `
      )
      .join("");
    $$(".project-item", root).forEach((button) => {
      button.addEventListener("click", () => selectProject(Number(button.dataset.projectId)));
    });
  }

  function renderArtifacts() {
    const root = $("#artifact-list");
    if (!root) return;
    if (!state.artifacts.length) {
      root.innerHTML = `<div class="artifact-card"><div class="title">No artifacts yet</div><p class="message">Artifacts will appear when a run finishes each stage.</p></div>`;
      return;
    }
    root.innerHTML = state.artifacts
      .map(
        (artifact) => `
        <div class="artifact-card">
          <div class="kind">${esc(artifact.kind)}</div>
          <div class="title">${esc(artifact.label)}</div>
          <p class="message">${esc(artifact.file_name)} · ${Math.round((artifact.size_bytes || 0) / 1024)} KB</p>
          <a href="/api/artifacts/${artifact.id}/download" target="_blank">Download</a>
        </div>
      `
      )
      .join("");
  }

  function renderRunHistory() {
    const root = $("#run-history");
    if (!root) return;
    if (!state.runs.length) {
      root.innerHTML = `<div class="artifact-card"><div class="title">No prior runs yet</div><p class="message">Historical runs will appear here for rewind and replay.</p></div>`;
      return;
    }
    root.innerHTML = state.runs
      .map(
        (run) => `
        <div class="artifact-card ${state.activeRun?.id === run.id ? "active" : ""}">
          <div class="kind">${esc(run.current_stage || run.status)}</div>
          <div class="title">${esc(run.label)}</div>
          <p class="message">${esc(run.status)} · ${run.progress || 0}% · ${esc(run.created_at || "")}</p>
          <div class="row">
            <button class="ghost" data-open-run="${run.id}">Open</button>
            <button class="ghost" data-replay-run="${run.id}">Rewind</button>
          </div>
        </div>
      `
      )
      .join("");
    $$("[data-open-run]", root).forEach((button) => {
      button.addEventListener("click", () => loadRun(Number(button.dataset.openRun)));
    });
    $$("[data-replay-run]", root).forEach((button) => {
      button.addEventListener("click", () => replayRun(Number(button.dataset.replayRun)));
    });
  }

  function renderLibrary() {
    const root = $("#library-list");
    if (!root) return;
    if (!state.library.length) {
      root.innerHTML = `<div class="artifact-card"><div class="title">No library files yet</div><p class="message">All artifacts across the account will collect here.</p></div>`;
      return;
    }
    root.innerHTML = state.library
      .slice(0, 24)
      .map(
        (artifact) => `
        <div class="artifact-card">
          <div class="kind">${esc(artifact.kind)}</div>
          <div class="title">${esc(artifact.label)}</div>
          <p class="message">${esc(artifact.file_name)} · run ${artifact.run_id}</p>
          <a href="/api/artifacts/${artifact.id}/download" target="_blank">Download</a>
        </div>
      `
      )
      .join("");
  }

  function renderEvents() {
    const root = $("#event-list");
    if (!root) return;
    if (!state.events.length) {
      root.innerHTML = `<div class="event-card"><div class="title">Waiting for a run</div><p class="message">The live timeline will stream ideation, search, execution, and writing events here.</p></div>`;
      return;
    }
    root.innerHTML = state.events
      .slice()
      .reverse()
      .slice(0, 40)
      .map(
        (event) => `
        <div class="event-card">
          <div class="kind">${esc(event.stage || event.kind)}</div>
          <div class="title">${esc(event.title || event.kind)}</div>
          <p class="message">${esc(event.message || "")}</p>
          ${event.payload && Object.keys(event.payload).length ? `<pre>${esc(formatPayload(event.payload))}</pre>` : ""}
        </div>
      `
      )
      .join("");
  }

  function findEvent(kind) {
    for (let i = state.events.length - 1; i >= 0; i -= 1) {
      if (state.events[i].kind === kind) return state.events[i];
    }
    return null;
  }

  function renderOutputs(run) {
    const root = $("#output-cards");
    if (!root) return;
    const ideas = findEvent("ideas.generated");
    const ranked = findEvent("ideas.ranked");
    const selected = findEvent("ideas.selected");
    const benchmark = findEvent("benchmark.selected");
    const plan = findEvent("experiment.plan");
    const summary = findEvent("evaluation.summary");
    const paper = findEvent("paper.pdf") || findEvent("run.completed");
    const selectedIdea = selected?.payload?.selected || ranked?.payload?.ranked?.[0] || ideas?.payload?.ideas?.[0] || null;
    const selectedBenchmark = benchmark?.payload?.benchmark || null;
    const paperTitle = run?.paper_html ? "Paper ready" : "Draft pending";

    const cards = [
      {
        kind: "Idea",
        title: selectedIdea ? selectedIdea.title : "No idea selected",
        message: selectedIdea ? selectedIdea.hypothesis || selectedIdea.expected_effect || "" : "Wait for ideation to complete.",
      },
      {
        kind: "Benchmark",
        title: selectedBenchmark ? selectedBenchmark.name : "No benchmark selected",
        message: selectedBenchmark ? `${selectedBenchmark.metric || ""} · confidence ${Math.round((selectedBenchmark.confidence || 0) * 100)}%` : "Benchmark discovery will appear here.",
      },
      {
        kind: "Plan",
        title: plan ? "Experiment plan ready" : "Plan pending",
        message: plan ? (plan.payload?.plan?.thesis || "Structured staged plan available") : "The experiment plan shows once planning finishes.",
      },
      {
        kind: "Selection",
        title: ranked ? "Ideas ranked" : "Ranking pending",
        message: selectedIdea ? `Selected: ${selectedIdea.title}` : "The ranking and selection step will be shown here.",
      },
      {
        kind: "Summary",
        title: summary ? "Evaluation summary ready" : "Summary pending",
        message: summary ? `Δ val loss: ${summary.payload?.delta_val_loss?.toFixed?.(4) ?? summary.payload?.delta_val_loss ?? ""}` : "The evaluation summary appears after execution.",
      },
      {
        kind: "Paper",
        title: paperTitle,
        message: run?.pdf_path ? "PDF is available to download." : "The manuscript will appear after writing.",
      },
    ];

    root.innerHTML = cards
      .map(
        (card) => `
        <div class="output-card">
          <div class="kind">${esc(card.kind)}</div>
          <div class="title">${esc(card.title)}</div>
          <p class="message">${esc(card.message)}</p>
        </div>
      `
      )
      .join("");
  }

  function updateStatus(run) {
    $("#run-status") && ($("#run-status").textContent = run?.status || "idle");
    $("#run-stage") && ($("#run-stage").textContent = run?.current_stage || "none");
    $("#run-progress") && ($("#run-progress").textContent = `${run?.progress || 0}%`);
    if ($("#pdf-link")) {
      if (run?.pdf_path) {
        $("#pdf-link").textContent = "Open PDF";
        $("#pdf-link").href = `/api/runs/${run.id}/pdf`;
      } else {
        $("#pdf-link").textContent = "-";
        $("#pdf-link").removeAttribute("href");
      }
    }
  }

  function syncRunUI(run) {
    state.activeRun = run;
    updateStatus(run);
    renderEvents();
    renderArtifacts();
    renderRunHistory();
    renderLibrary();
    renderOutputs(run);
    if (run?.status === "completed" || run?.status === "failed") {
      if (state.eventSource) {
        state.eventSource.close();
        state.eventSource = null;
      }
    }
  }

  async function loadProjects() {
    const data = await api("/api/projects");
    state.projects = data.projects || [];
    renderProjects();
    if (!state.activeProject && state.projects.length) {
      await loadProject(state.projects[0].id);
    }
  }

  async function loadProject(projectId) {
    const data = await api(`/api/projects/${projectId}`);
    state.activeProject = data.project;
    state.runs = data.runs || [];
    $("#active-project-title").textContent = data.project.name;
    $("#active-project-meta").textContent = `${data.project.topic} · ${data.project.experiment_template} · ${data.project.compute_backend || "local-cpu"}`;
    $("#start-run-btn").disabled = false;
    $("#clone-run-btn").disabled = !state.activeRun;
    state.projects = state.projects.map((p) => (p.id === data.project.id ? data.project : p));
    renderProjects();
    renderRunHistory();
    if (data.runs && data.runs.length) {
      await loadRun(data.runs[0].id);
    } else {
      state.events = [];
      state.artifacts = [];
      syncRunUI({ status: "idle", current_stage: "none", progress: 0 });
    }
  }

  async function selectProject(projectId, triggerLoad = true) {
    state.activeProject = state.projects.find((p) => p.id === projectId) || state.activeProject;
    renderProjects();
    if (triggerLoad) {
      await loadProject(projectId);
    }
  }

  async function loadRun(runId) {
    const data = await api(`/api/runs/${runId}`);
    state.events = data.events || [];
    state.artifacts = data.artifacts || [];
    syncRunUI(data.run);
    $("#clone-run-btn").disabled = false;
    renderProjects();
    renderRunHistory();
    openStream(runId);
  }

  function openStream(runId) {
    if (state.eventSource) {
      state.eventSource.close();
      state.eventSource = null;
    }
    const source = new EventSource(`/api/runs/${runId}/stream`);
    source.addEventListener("run-event", (event) => {
      const payload = JSON.parse(event.data);
      state.events.push(payload);
      renderEvents();
      renderOutputs(state.activeRun);
    });
    source.addEventListener("run-final", () => {
      if (state.eventSource) {
        state.eventSource.close();
        state.eventSource = null;
      }
      refreshCurrentRun();
    });
    source.onerror = () => {};
    state.eventSource = source;
  }

  async function refreshCurrentRun() {
    if (!state.activeRun) return;
    const data = await api(`/api/runs/${state.activeRun.id}`);
    state.events = data.events || [];
    state.artifacts = data.artifacts || [];
    syncRunUI(data.run);
    renderRunHistory();
  }

  async function loadAccountHistory() {
    const history = await api("/api/history");
    state.runs = history.runs || [];
    renderRunHistory();
  }

  async function loadLibrary() {
    const library = await api("/api/library");
    state.library = library.artifacts || [];
    renderLibrary();
  }

  async function createProject(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      const data = await api("/api/projects", { method: "POST", body: JSON.stringify(payload) });
      form.reset();
      $("#project-form select[name='compute_backend']").value = "local-cpu";
      $("#project-form textarea[name='compute_config_json']").value = "";
      $("#project-form select[name='experiment_template']").value = "sandbox";
      setMessage("Project created.", "success");
      await loadProjects();
      await selectProject(data.project.id);
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function startRun() {
    if (!state.activeProject) return;
    const label = $("#run-label").value.trim();
    const pausePoints = $("[name='pause_points']:checked")
      ? $$("[name='pause_points']:checked").map((el) => el.value)
      : [];
    const autoContinue = $("#auto-continue").checked;
    const payload = {
      label,
      pause_points: pausePoints,
      auto_continue: autoContinue,
    };
    try {
      const data = await api(`/api/projects/${state.activeProject.id}/runs`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage("Run started.", "success");
      await loadRun(data.run.id);
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function addNote() {
    if (!state.activeRun) return;
    const note = $("#user-note").value.trim();
    if (!note) return;
    try {
      await api(`/api/runs/${state.activeRun.id}/notes`, {
        method: "POST",
        body: JSON.stringify({ note }),
      });
      $("#user-note").value = "";
      setMessage("Note saved.", "success");
      await refreshCurrentRun();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function resumeRun() {
    if (!state.activeRun) return;
    try {
      await api(`/api/runs/${state.activeRun.id}/resume`, { method: "POST", body: "{}" });
      setMessage("Run resumed.", "success");
      await refreshCurrentRun();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function cloneRun() {
    if (!state.activeRun) return;
    try {
      const data = await api(`/api/runs/${state.activeRun.id}/clone`, { method: "POST", body: "{}" });
      setMessage("Rewind run started.", "success");
      await loadRun(data.run.id);
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function replayRun(runId) {
    try {
      const data = await api(`/api/runs/${runId}/clone`, { method: "POST", body: "{}" });
      setMessage("Rewind run started.", "success");
      await loadRun(data.run.id);
      await loadAccountHistory();
      await loadLibrary();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function refreshAll() {
    await loadProjects();
    if (state.activeRun) {
      await refreshCurrentRun();
    }
    await loadAccountHistory();
    await loadLibrary();
  }

  async function logout() {
    await api("/api/auth/logout", { method: "POST", body: "{}" });
    window.location.href = "/login";
  }

  function wireAuthPage() {
    const tabs = $$(".tab");
    const loginForm = $("#login-form");
    const registerForm = $("#register-form");
    if (!loginForm || !registerForm) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const mode = tab.dataset.tab;
        loginForm.classList.toggle("hidden", mode !== "login");
        registerForm.classList.toggle("hidden", mode !== "register");
      });
    });

    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(loginForm).entries());
      try {
        await api("/api/auth/login", { method: "POST", body: JSON.stringify(payload) });
        window.location.href = "/dashboard";
      } catch (error) {
        setMessage(error.message, "error");
      }
    });

    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(registerForm).entries());
      try {
        await api("/api/auth/register", { method: "POST", body: JSON.stringify(payload) });
        await api("/api/auth/login", { method: "POST", body: JSON.stringify(payload) });
        window.location.href = "/dashboard";
      } catch (error) {
        setMessage(error.message, "error");
      }
    });
  }

  function wireDashboardPage() {
    const form = $("#project-form");
    if (!form) return;
    form.addEventListener("submit", createProject);
    $("#start-run-btn").addEventListener("click", startRun);
    $("#add-note-btn").addEventListener("click", addNote);
    $("#resume-btn").addEventListener("click", resumeRun);
    $("#clone-run-btn").addEventListener("click", cloneRun);
    $("#refresh-all").addEventListener("click", refreshAll);
    $("#logout-btn").addEventListener("click", logout);
    $("#auto-continue").addEventListener("change", (event) => {
      const pauseInputs = $$("[name='pause_points']");
      pauseInputs.forEach((input) => {
        input.disabled = event.target.checked;
        if (event.target.checked) input.checked = false;
      });
    });
    $("#project-form select[name='compute_backend']").addEventListener("change", (event) => {
      const config = $("#project-form textarea[name='compute_config_json']");
      if (!config) return;
      const backend = event.target.value;
      if (backend === "ssh-remote-gpu") {
        config.placeholder = JSON.stringify(
          {
            host: "1.2.3.4",
            user: "ubuntu",
            identity_file: "~/.ssh/id_ed25519",
            remote_workdir: "/home/ubuntu/research",
            remote_python: "python3",
            env: { HF_TOKEN: "..." },
          },
          null,
          2
        );
      } else if (backend === "hf-job") {
        config.placeholder = JSON.stringify(
          {
            image: "python:3.11-slim",
            flavor: "a10g-small",
            command: [
              "python3",
              "-c",
              "from ai_research_repro.templates.nanogpt_lite import default_config, train_and_evaluate; print('===AI_RESEARCH_RESULT_JSON_START==='); print('{}'); print('===AI_RESEARCH_RESULT_JSON_END===')",
            ],
            env: { HF_TOKEN: "..." },
          },
          null,
          2
        );
      } else {
        config.placeholder = 'Optional backend config JSON. Example: {"host":"1.2.3.4","user":"ubuntu"}';
      }
    });

    Promise.all([loadProjects(), loadAccountHistory(), loadLibrary()]).catch((error) => setMessage(error.message, "error"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    wireAuthPage();
    wireDashboardPage();
  });
})();
