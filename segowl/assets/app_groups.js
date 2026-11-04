// SegOWL — Port Groups editor (app-navigation ticket 04). Validation and file writes are the server's.
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
async function api(path, body) {
  const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1", "Content-Type": "application/json"}, body: JSON.stringify(body)};
  const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
  if (!r.ok) { const e = new Error(j.error || r.statusText); e.status = r.status; throw e; }
  return j;
}
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3800); }
function status(text, cls = "") { const s = $("#st"); s.textContent = text; s.className = "status " + cls; }

// ---------------------------------------------------------------- ports helpers (shared shape with the prototype)
const tokOk = t => { const m = t.trim().match(/^(?:(udp|tcp|sctp):)?(\d+)(?:-(\d+))?$/i); if (!m) return false; const a = +m[2], b = m[3] ? +m[3] : a; return a >= 1 && b <= 65535 && a <= b; };
const toks = s => String(s).split(",").map(x => x.trim()).filter(Boolean);
const portsOk = s => toks(s).length > 0 && toks(s).every(tokOk);
function countPorts(s) { const c = {tcp: 0, udp: 0}; toks(s).forEach(x => { const m = x.match(/^(?:(udp|tcp|sctp):)?(\d+)(?:-(\d+))?$/i); if (m) c[m[1] === "udp" ? "udp" : "tcp"] += m[3] ? +m[3] - +m[2] + 1 : 1; }); return c; }
const ORD = {shipped: 0, override: 1, mission: 2};
const badge = o => ({shipped: `<span class="badge shipped">shipped</span>`, mission: `<span class="badge b-mission">Mission</span>`,
  override: `<span class="badge override" title="this Mission's group replaces the shipped one">Mission · replaces</span>`}[o]);

// ---------------------------------------------------------------- state
let D = null, table = null;
const EXP = new Set(); // groups whose long port list is expanded
const spec = n => D.mission[n] ?? D.shipped[n];
const allNames = () => [...new Set([...Object.keys(D.shipped), ...Object.keys(D.mission)])];
const used = n => D.used[n] || {rules: [], profiles: []};
function rows() {
  return allNames().map(n => ({id: n, name: n, ports: spec(n), shippedPorts: D.shipped[n] || "",
    origin: !(n in D.mission) ? "shipped" : n in D.shipped ? "override" : "mission"}));
}
const expand = v => toks(v).flatMap(t => t.startsWith("@") && spec(t.slice(1)) !== undefined ? toks(spec(t.slice(1))) : [t]);

async function load() { D = await api("/api/groups"); table.replaceData(rows()); status("Loaded"); }
async function save() {
  const bad = Object.entries(D.mission).filter(([, p]) => !portsOk(p)).map(([n]) => "@" + n);
  if (bad.length) { status(`Not saved: fix the ports of ${bad.join(", ")}`, "err"); return; }
  status("Saving…");
  try {
    const r = await api("/api/groups", {fp: D.fp["port_groups.csv"], groups: Object.entries(D.mission).map(([name, ports]) => ({name, ports}))});
    D.fp["port_groups.csv"] = r.fp; status("Saved ✓", "ok");
  } catch (e) { status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err"); }
}

// ---------------------------------------------------------------- ports autocomplete: server search (Port Labels, IANA) + local groups
const cache = {};
async function suggest(tok) {
  const t = tok.trim().toLowerCase(); if (!t) return [];
  if (t.startsWith("@")) return allNames().filter(n => n.toLowerCase().startsWith(t.slice(1)))
    .map(n => ({v: spec(n), k: "@" + n, d: `insert its ${toks(spec(n)).length} ports (a copy, not a link)`, src: "Port Group"}));
  cache[t] ??= api("/api/ports?q=" + encodeURIComponent(t)).catch(() => []);
  const out = (await cache[t]).filter(h => h.src === "Port Label" || h.src === "IANA").map(h => ({v: h.key, k: h.key, d: h.label, src: h.src}));
  const seen = new Set(), uniq = out.filter(o => !seen.has(o.k + o.d) && seen.add(o.k + o.d));
  if (/^\d+$/.test(t) && tokOk(t) && !uniq.some(o => o.v === "udp:" + t)) uniq.push({v: "udp:" + t, k: "udp:" + t, d: "the same port over UDP", src: ""});
  return uniq.slice(0, 10);
}
function attachPorts(input, onCommit, onCancel) {
  const drop = document.createElement("div"); drop.className = "tagdrop"; document.body.appendChild(drop);
  let items = [], hl = -1, closed = false, seq = 0;
  const place = () => { const b = input.getBoundingClientRect(); drop.style.left = b.left + "px"; drop.style.top = b.bottom + 2 + "px"; drop.style.minWidth = Math.max(320, b.width) + "px"; };
  const parts = () => input.value.split(","), tok = () => parts().pop().trim();
  function pick(o) { input.value = [...parts().slice(0, -1).map(x => x.trim()).filter(Boolean), o.v].join(",") + ","; hl = -1; update(); input.focus(); }
  function draw() {
    const t = tok();
    let h = items.map((o, i) => `<div data-i="${i}" class="${i === hl ? "hl" : ""}"><b style="min-width:70px">${esc(o.k)}</b><span>${esc(o.d)}</span><span class="c">${esc(o.src)}</span></div>`).join("");
    if (t && !t.startsWith("@") && !tokOk(t) && !items.length) h = `<div class="new">not a port: 22 · 8000-8100 · udp:161 · @group</div>`;
    if (!t) h = `<div class="new">type a port, a product (winbox, veeam…), udp:… or @group · <span class="kbd">,</span> next port</div>`;
    drop.innerHTML = h; drop.hidden = !h; place();
  }
  async function update() { const n = ++seq, r = await suggest(tok()); if (n !== seq || closed) return; items = r; hl = Math.min(hl, items.length - 1); draw(); }
  drop.addEventListener("mousedown", e => { const d = e.target.closest("[data-i]"); if (d) { e.preventDefault(); pick(items[+d.dataset.i]); } });
  input.addEventListener("input", () => { hl = -1; update(); });
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { hl = Math.min(hl + 1, items.length - 1); draw(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { hl = Math.max(hl - 1, -1); draw(); e.preventDefault(); }
    else if (e.key === "Enter" && hl >= 0) { pick(items[hl]); e.preventDefault(); } // Enter on a typed port keeps it as typed
    else if (e.key === "Enter" || e.key === "Tab") { finish(); e.preventDefault(); }
    else if (e.key === "Escape") { closed = true; drop.remove(); onCancel(); }
  });
  input.addEventListener("blur", () => setTimeout(() => { if (document.activeElement !== input) finish(); }, 120));
  function finish() { if (closed) return; closed = true; drop.remove(); onCommit([...new Set(expand(input.value.replace(/\s+/g, "")))].join(",")); }
  update();
}
function portsEditor(cell, onRendered, success, cancel) {
  const input = document.createElement("input"); input.type = "text"; input.value = cell.getValue() || ""; input.style.cssText = "width:100%;padding:3px 6px;box-sizing:border-box";
  onRendered(() => { input.focus(); input.setSelectionRange(input.value.length, input.value.length); attachPorts(input, success, cancel); });
  return input;
}
function portChips(v, id) {
  const t = toks(v); if (!t.length) return `<span style="color:#8a1a1a">— empty —</span>`;
  const long = t.length > 10, show = long && !EXP.has(id) ? t.slice(0, 8) : t;
  return show.map(x => `<span class="pill ${x.startsWith("udp:") ? "udp" : ""} ${tokOk(x) ? "" : "badtok"}">${esc(x)}</span>`).join("")
    + (long ? `<span class="pill more" data-more="${esc(id)}">${EXP.has(id) ? "show less ▴" : `+${t.length - 8} more ▾`}</span>` : "");
}

// ---------------------------------------------------------------- grid
table = new Tabulator("#grid", {data: [], index: "id", layout: "fitColumns", height: "calc(100vh - 330px)", editTriggerEvent: "dblclick",
  rowFormatter: r => r.getElement().classList.toggle("shipped", r.getData().origin === "shipped"),
  columns: [
    {title: "source", field: "origin", width: 150, formatter: c => badge(c.getValue()), sorter: (a, b) => ORD[a] - ORD[b]},
    {title: "group", field: "name", width: 150, editor: "input", editable: c => c.getRow().getData().origin === "mission", formatter: c => `<b>@${esc(c.getValue())}</b>`,
      tooltip: (e, c) => c.getRow().getData().origin === "mission" ? "click to rename (rewrites the Flow Policy and the Scan Profiles)" : "a shipped group keeps its name"},
    {title: "ports", field: "ports", editor: portsEditor, formatter: c => { const d = c.getRow().getData(); c.getElement().classList.toggle("bad", !portsOk(c.getValue()));
      return portChips(c.getValue(), d.id) + (d.origin === "override" ? `<div class="small muted" title="${esc(d.shippedPorts)}">shipped: ${toks(d.shippedPorts).length} ports</div>` : ""); }},
    {title: "count", field: "count", width: 110, headerSort: false, formatter: c => { const n = countPorts(c.getRow().getData().ports); return `${n.tcp} TCP${n.udp ? ` · ${n.udp} UDP` : ""}`; }},
    {title: "used by", field: "usedby", width: 220, headerSort: false, formatter: c => { const u = used(c.getRow().getData().name);
      return u.rules.length || u.profiles.length ? `<span class="uses">${u.rules.length ? `<span class="small" style="border-bottom:1px dotted">${u.rules.length} rule(s)</span>` : ""}${u.profiles.map(x => `<span class="pill">${esc(x)}</span>`).join("")}</span>` : `<span class="muted">unused</span>`; },
      tooltip: (e, c) => { const u = used(c.getRow().getData().name); return [...u.rules.map(x => "rule  " + x), ...u.profiles.map(x => "Scan Profile  " + x)].join("\n") || "unused"; }},
    {title: "", field: "act", width: 140, headerSort: false, formatter: c => { const d = c.getRow().getData(), u = used(d.name), n = u.rules.length + u.profiles.length;
      return d.origin === "override" ? `<button class="btn sm" data-act="reset">Reset to shipped</button>`
        : d.origin === "mission" ? `<button class="btn sm" data-act="del" ${n ? `disabled title="used by ${u.rules.length} rule(s), ${u.profiles.length} Scan Profile(s)"` : ""}>Delete</button>` : ""; }},
  ]});
table.on("cellClick", (e, c) => {
  const more = e.target.closest("[data-more]"); if (more) { const id = more.dataset.more; EXP.has(id) ? EXP.delete(id) : EXP.add(id); c.getRow().reformat(); return; }
  const a = e.target.dataset?.act; if (a) { if (e.target.disabled) return; const n = c.getRow().getData().name; delete D.mission[n];
    toast(a === "reset" ? `@${n}: back to the shipped ports` : `@${n} deleted`); table.replaceData(rows()); save(); return; }
  if (c.getColumn().getDefinition().editor && (c.getField() !== "name" || c.getRow().getData().origin === "mission")) c.edit();
});
table.on("cellEdited", async c => {
  const d = c.getRow().getData(), f = c.getField();
  if (f === "name") {
    const old = c.getOldValue(), nw = String(c.getValue()).trim().replace(/^@/, "");
    if (nw === old) return;
    if (!/^[A-Za-z0-9._-]+$/.test(nw) || allNames().includes(nw)) { toast(`@${nw}: name taken or invalid (letters, digits, . _ -)`); table.replaceData(rows()); return; }
    const u = used(old);
    if (u.rules.length || u.profiles.length) { // rewrite the files naming it, on the server, all at once
      try { const r = await api("/api/groups/rename", {old, new: nw, fp: D.fp}); toast(r.message); await load(); }
      catch (e) { toast(e.status === 409 ? "Modified elsewhere: reload" : e.message); table.replaceData(rows()); }
      return;
    }
    D.mission = Object.fromEntries(Object.entries(D.mission).map(([k, v]) => [k === old ? nw : k, v]));
    toast(`Renamed @${old} → @${nw}`);
  } else if (f === "ports") {
    const v = String(c.getValue()).replace(/\s+/g, "");
    if (d.origin === "shipped") toast(`@${d.name} now replaced in this Mission (Reset brings the shipped one back)`);
    D.mission[d.name] = v;
  }
  table.replaceData(rows()); save();
});
$("#gq").oninput = () => { const q = $("#gq").value.trim().toLowerCase(); table.setFilter(d => !q || d.name.toLowerCase().includes(q) || toks(d.ports).includes(q)); };
$("#gadd").onclick = () => { let n = "new-group", i = 2; while (allNames().includes(n)) n = "new-group-" + i++; D.mission[n] = "";
  table.replaceData(rows()).then(() => { table.scrollToRow(n); table.getRow(n).getCell("ports").edit(); }); status("New group: type its ports, double-click its name to rename"); };
table.on("tableBuilt", () => load().catch(e => status("Not loaded: " + e.message, "err")));
