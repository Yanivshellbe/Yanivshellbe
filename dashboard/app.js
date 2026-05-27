const fmtUsd = (n) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);

async function loadState() {
  const res = await fetch("state.json?ts=" + Date.now());
  if (!res.ok) throw new Error("state.json not found");
  return res.json();
}

function renderHeader(s) {
  document.getElementById("equity").textContent = fmtUsd(s.account.current_equity_usd);
  document.getElementById("bp").textContent = fmtUsd(s.account.buying_power_usd);
  document.getElementById("broker").textContent = s.account.broker;
  document.getElementById("live").textContent = s.account.live_trading_enabled ? "ON" : "OFF (paper)";
  document.getElementById("phase").textContent = s.phase;
  document.getElementById("updated").textContent = "Updated: " + new Date(s.updated_at).toLocaleString();
}

function renderProgress(s) {
  const list = document.getElementById("progress");
  list.innerHTML = "";
  for (const step of s.build_progress) {
    const li = document.createElement("li");
    li.className = step.status;
    li.innerHTML = `<span class="badge">${step.status.replace("_", " ")}</span><span>${step.title}</span>`;
    list.appendChild(li);
  }
  document.getElementById("nextAction").textContent = "Next: " + s.next_action;
}

function renderList(id, items, emptyMsg, fmt) {
  const el = document.getElementById(id);
  if (!items || items.length === 0) {
    el.className = "empty";
    el.textContent = emptyMsg;
    return;
  }
  el.className = "";
  el.innerHTML = items.map(fmt).join("");
}

function renderLog(s) {
  const ul = document.getElementById("log");
  ul.innerHTML = s.log
    .slice()
    .reverse()
    .map(
      (e) =>
        `<li>${e.msg}<span class="ts">${new Date(e.ts).toLocaleTimeString()}</span></li>`
    )
    .join("");
}

async function main() {
  try {
    const s = await loadState();
    renderHeader(s);
    renderProgress(s);
    renderList("strategies", s.strategies, "— ממתינים לרעיונות —", (x) => `<div>${x.name}</div>`);
    renderList("positions", s.open_positions, "— אין פוזיציות פתוחות —", (x) => `<div>${x.symbol}</div>`);
    renderList("dreams", s.dream_scans, "— טרם הופעל —", (x) => `<div>${x.title}</div>`);
    renderList("backtests", s.backtests, "— אין הרצות —", (x) => `<div>${x.name}</div>`);
    renderLog(s);
  } catch (e) {
    document.body.insertAdjacentHTML(
      "afterbegin",
      `<div style="padding:16px;color:#ff6b81;background:#2a0e15;border-bottom:1px solid #6b1726">Error: ${e.message}. Open via local web server (e.g. <code>python3 -m http.server</code>) to load state.json.</div>`
    );
  }
}

main();
setInterval(main, 5000);
