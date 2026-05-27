// ============== Money Machine Control Tower — Dashboard ==============

const ENDPOINTS = {
  state: "state.json",
  analysts: "data/analysts.json",
  ideas: "data/ideas.json",
  prompts: "data/prompts.json",
};

const fmtUsd0 = (n) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);

async function fetchJson(url) {
  const r = await fetch(url + "?ts=" + Date.now());
  if (!r.ok) throw new Error("Failed: " + url);
  return r.json();
}

let CACHE = { state: null, analysts: null, ideas: null, prompts: null };

// ---------- Header & KPIs ----------
function renderHeader(s) {
  document.getElementById("systemStatus").textContent = s.system_status;
  document.getElementById("equity").textContent = fmtUsd0(s.account.current_equity_usd);
  document.getElementById("bp").textContent = fmtUsd0(s.account.buying_power_usd);
  document.getElementById("dtbp").textContent = s.account.dtbp_status;
  document.getElementById("liveStatus").textContent = s.account.live_trading_enabled ? "ON ⚠" : "OFF · paper";
  document.getElementById("openCount").textContent = (s.open_positions || []).length;
  document.getElementById("stratCount").textContent = (s.strategies || []).filter(x => x.status === "active").length;
  document.getElementById("phasePill").textContent = "Phase " + s.phase;
  document.getElementById("updated").textContent = new Date(s.updated_at).toLocaleString();
  document.getElementById("ver").textContent = s.version;
}

// ---------- Progress ----------
function renderProgress(s) {
  const list = document.getElementById("progress");
  list.innerHTML = s.build_progress
    .map(
      (st) => `
      <li class="${st.status}">
        <span class="badge">${st.status.replace(/_/g, " ")}</span>
        <span>${st.title}</span>
      </li>`
    )
    .join("");
  document.getElementById("nextAction").textContent = s.next_action || "";
}

// ---------- Strategies ----------
function renderStrategies(s, ideas) {
  const tbody = document.getElementById("strategyRows");
  if (!ideas || ideas.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty">— הזרקת הרעיונות הסתיימה, אסטרטגיות יבנו בשלב הבא —</td></tr>`;
    return;
  }
  const approved = ideas.filter((i) => i.status.startsWith("approved"));
  tbody.innerHTML = approved
    .map((idea, i) => {
      const riskTag =
        idea.category === "Latency Arb"
          ? '<span class="tag warn">high · decaying</span>'
          : idea.category === "News-Driven"
          ? '<span class="tag warn">event · spiky</span>'
          : idea.category === "Vol"
          ? '<span class="tag bad">tail-risk</span>'
          : '<span class="tag ok">core</span>';
      return `
        <tr>
          <td><span class="rank">${i + 1}</span></td>
          <td><strong>${idea.title}</strong></td>
          <td><span class="tag info">${idea.category}</span></td>
          <td><span class="tag">${idea.status.replace(/_/g, " ")}</span></td>
          <td style="max-width:280px">${idea.edge}</td>
          <td>${riskTag}</td>
          <td class="num">—</td>
          <td class="num">$0</td>
          <td><button class="btn-mini" data-idea="${idea.id}">Details</button></td>
        </tr>`;
    })
    .join("");
  tbody.querySelectorAll("button[data-idea]").forEach((b) =>
    b.addEventListener("click", () => openIdeaDrawer(b.dataset.idea))
  );
}

// ---------- Analysts grid ----------
function renderAnalysts(personas, filter) {
  const grid = document.getElementById("analystGrid");
  const filtered = filter === "all" ? personas : personas.filter((p) => p.team === filter);
  grid.innerHTML = filtered
    .map(
      (p) => `
      <div class="analyst" data-id="${p.id}" style="--accent-bar:${p.color}">
        <div class="firm">${p.firm}</div>
        <div class="title">${p.title}</div>
        <div class="tag-row">
          <span class="tag info">${p.team}</span>
          <span class="tag">${p.schedule}</span>
        </div>
        <div class="tagline">${p.tagline}</div>
      </div>`
    )
    .join("");
  grid.querySelectorAll(".analyst").forEach((el) =>
    el.addEventListener("click", () => openAnalystDrawer(el.dataset.id))
  );
}

// ---------- Ideas ----------
function renderIdeas(ideas) {
  const wrap = document.getElementById("ideaList");
  wrap.innerHTML = ideas
    .map((idea) => {
      const statusTag =
        idea.status === "rejected_for_now"
          ? `<span class="tag bad">rejected · ${idea.rejection_reason || ""}</span>`
          : idea.status.includes("approved")
          ? '<span class="tag ok">approved · paper research</span>'
          : `<span class="tag warn">${idea.status}</span>`;
      return `
        <div class="idea">
          <div>
            <div class="meta">
              <span class="tag info">${idea.category}</span>
              ${statusTag}
            </div>
            <h3>${idea.title}</h3>
          </div>
          <p class="summary">${idea.summary}</p>
          <div class="edge">⚡ ${idea.edge}</div>
          <details class="red-team">
            <summary>Red Team (${idea.red_team.length})</summary>
            <ul>${idea.red_team.map((r) => `<li>${r}</li>`).join("")}</ul>
          </details>
        </div>`;
    })
    .join("");
}

// ---------- Log / Backtests / Dreams ----------
function renderLists(s) {
  const log = document.getElementById("logList");
  log.innerHTML = (s.log || [])
    .slice()
    .reverse()
    .map(
      (e) =>
        `<li><span class="ts">${new Date(e.ts).toLocaleTimeString()}</span><span class="msg">${e.msg}</span></li>`
    )
    .join("");

  const bt = document.getElementById("backtestList");
  if ((s.backtests || []).length === 0) {
    bt.className = "empty";
    bt.textContent = "— אין הרצות עדיין —";
  } else {
    bt.className = "";
    bt.innerHTML = s.backtests.map((b) => `<div>${b.name}</div>`).join("");
  }

  const dm = document.getElementById("dreamList");
  if ((s.dream_scans || []).length === 0) {
    dm.className = "empty";
    dm.textContent = "— טרם הופעל —";
  } else {
    dm.className = "";
    dm.innerHTML = s.dream_scans.map((d) => `<div>${d.title}</div>`).join("");
  }
}

// ---------- Drawer ----------
const drawer = document.getElementById("drawer");
function openDrawer() { drawer.setAttribute("aria-hidden", "false"); }
function closeDrawer() { drawer.setAttribute("aria-hidden", "true"); }
document.getElementById("drawerClose").addEventListener("click", closeDrawer);
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDrawer(); });

function openAnalystDrawer(id) {
  const persona = CACHE.analysts.personas.find((p) => p.id === id);
  if (!persona) return;
  const template = (CACHE.prompts.templates || {})[id] || "(no template registered)";
  document.getElementById("drawerTitle").textContent = `${persona.firm} · ${persona.title}`;
  document.getElementById("drawerBody").innerHTML = `
    <dl class="kv">
      <dt>Team</dt><dd>${persona.team}</dd>
      <dt>Schedule</dt><dd>${persona.schedule}</dd>
      <dt>Inputs</dt><dd>${persona.inputs.join(", ")}</dd>
      <dt>Output</dt><dd>${persona.output}</dd>
    </dl>
    <p class="muted" style="margin:0 0 8px">Prompt template (LTR):</p>
    <pre>${escapeHtml(template)}</pre>
  `;
  openDrawer();
}

function openIdeaDrawer(id) {
  const idea = CACHE.ideas.ideas.find((i) => i.id === id);
  if (!idea) return;
  document.getElementById("drawerTitle").textContent = idea.title;
  document.getElementById("drawerBody").innerHTML = `
    <dl class="kv">
      <dt>Category</dt><dd>${idea.category}</dd>
      <dt>Status</dt><dd>${idea.status}</dd>
      <dt>Module</dt><dd>${idea.owner_module || "—"}</dd>
      ${idea.expected_per_trade_pct ? `<dt>Per trade %</dt><dd>${idea.expected_per_trade_pct.join(" – ")}</dd>` : ""}
      ${idea.decay_window_days ? `<dt>Decay window</dt><dd>~${idea.decay_window_days} days</dd>` : ""}
    </dl>
    <p>${idea.summary}</p>
    <p class="edge" style="color:#5cf2a0">⚡ ${idea.edge}</p>
    <h4 style="color:#ffcc66;margin-top:18px">Red Team</h4>
    <ul style="padding-right:20px;line-height:1.6">${idea.red_team.map((r) => `<li>${r}</li>`).join("")}</ul>
  `;
  openDrawer();
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- Filters ----------
document.querySelectorAll(".analyst-filters .chip").forEach((chip) =>
  chip.addEventListener("click", () => {
    document.querySelectorAll(".analyst-filters .chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    renderAnalysts(CACHE.analysts.personas, chip.dataset.team);
  })
);

// ---------- Boot ----------
async function boot() {
  try {
    const [state, analysts, ideas, prompts] = await Promise.all([
      fetchJson(ENDPOINTS.state),
      fetchJson(ENDPOINTS.analysts),
      fetchJson(ENDPOINTS.ideas),
      fetchJson(ENDPOINTS.prompts),
    ]);
    CACHE = { state, analysts, ideas, prompts };
    renderHeader(state);
    renderProgress(state);
    renderStrategies(state, ideas.ideas);
    renderAnalysts(analysts.personas, "all");
    renderIdeas(ideas.ideas);
    renderLists(state);
  } catch (e) {
    document.body.insertAdjacentHTML(
      "afterbegin",
      `<div style="padding:16px;color:#ff6b81;background:#2a0e15;border-bottom:1px solid #6b1726;direction:ltr;font-family:monospace">
       Cannot load JSON via file://. Serve the folder: <code>cd dashboard && python3 -m http.server 8080</code> then open http://localhost:8080.
       <br>${e.message}
       </div>`
    );
  }
}

boot();
setInterval(boot, 8000);
