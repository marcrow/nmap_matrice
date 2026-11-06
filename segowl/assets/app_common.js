// SegOWL — helpers shared by every app page (loaded first by app.py page()).
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
// GET without body, POST JSON (or `raw` bytes); an error carries the HTTP status and the server's `exists` flag
async function api(path, body, raw) {
  const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1"}, body: raw ? body : JSON.stringify(body)};
  if (body !== undefined && !raw) opt.headers["Content-Type"] = "application/json";
  const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
  if (!r.ok) throw Object.assign(new Error(j.error || r.statusText), {status: r.status, exists: j.exists});
  return j;
}
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3800); }
function status(text, cls = "") { const s = $("#st"); s.textContent = text; s.className = "status " + cls; }
// typing in a field or in a table cell being edited: Ctrl+Z, copy, paste and Delete are the browser's there
const isTyping = el => !!(el && el.closest && (el.closest(".tabulator-editing") || el.matches("input,textarea,select") || el.isContentEditable));
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
// The report's Zone hues (render/common.py ZONE_COLORS: pale fill, hue, dark text), in Zone name order as
// the report assigns them; never red, amber or green, which belong to the Flow Policy.
const ZONE_COLORS = [["#eff8ff", "#1565c0", "#0b3c75"], ["#fff3ee", "#8d6e63", "#51352c"], ["#f6f5ff", "#7c4dff", "#3c3072"],
  ["#eafafe", "#1597ad", "#00495e"], ["#f5f5ff", "#3d2a8a", "#3a3173"], ["#eafbfd", "#80deea", "#004954"],
  ["#eafbf9", "#0b5f5a", "#004944"], ["#f7f5ff", "#b9a6f2", "#432e6f"]];
// Undo / redo for an editor that saves automatically (policy-copy-cells): a snapshot of its state before each change, in
// memory only. get() returns the state (JSON-able); set(state) puts one back and saves it. Brings the bottom bar and
// Ctrl+Z / Ctrl+Y (inside a field being typed in, the browser's own undo applies). Call changed(label) after each change;
// clear() after a change undo must not cross (a rename the server applied to several files).
function undoable(get, set) {
  let hist = [], fut = [], last = JSON.stringify(get());
  const bar = document.createElement("div"); bar.id = "undobar";
  bar.innerHTML = `<span class="muted"></span><button class="btn sm">↶ Undo</button><button class="btn sm">↷ Redo</button>`;
  document.body.append(bar);
  const [lab, ub, rb] = bar.children;
  const ui = () => {
    const u = hist.at(-1), r = fut.at(-1);
    ub.disabled = !u; ub.title = u ? `Undo: ${u.label} (Ctrl+Z)` : "Nothing to undo";
    rb.disabled = !r; rb.title = r ? `Redo: ${r.label} (Ctrl+Y)` : "Nothing to redo";
    lab.textContent = u ? "Last change: " + u.label : r ? "Undone: " + r.label : "";
    bar.classList.toggle("on", !!(u || r));
  };
  const step = (from, to, undoing) => {
    if (!from.length) return toast(undoing ? "Nothing to undo" : "Nothing to redo");
    const h = from.pop(); to.push({state: last, label: h.label}); last = h.state;
    set(JSON.parse(h.state)); ui(); toast(`${undoing ? "Undone" : "Redone"}: ${h.label}`);
  };
  const undo = () => step(hist, fut, true), redo = () => step(fut, hist, false);
  ub.onclick = undo; rb.onclick = redo;
  document.addEventListener("keydown", e => {
    const k = (e.key || "").toLowerCase();
    if (!(e.ctrlKey || e.metaKey) || isTyping(e.target)) return;
    if (k === "z" && !e.shiftKey) { e.preventDefault(); undo(); }
    else if (k === "y" || (k === "z" && e.shiftKey)) { e.preventDefault(); redo(); }
  });
  return {
    changed(label = "Edit") { // false when nothing changed
      const now = JSON.stringify(get()); if (now === last) return false;
      hist.push({state: last, label}); if (hist.length > 200) hist.shift(); fut = []; last = now; ui(); return true;
    },
    clear() { hist = []; fut = []; last = JSON.stringify(get()); ui(); },
  };
}

// Names from Scans (inventory-names-from-scans): what the Scans propose for the inventory. One computation for the
// Inventory panel, the Scans line and the Flow Policy modal, so they always agree. rows: inventory rows {ip, zone, name};
// zones: Zone names; refs: Flow Policy references per name (GET /api/inventory); sn: GET /api/scan-names;
// mode: "short" | "fqdn"; choice: ip -> name picked for a conflict.
const shortName = f => f.split(".")[0];
// the resolved name a row's name stands for (its FQDN or short form), or null: the "⇄ DNS" badge
function namesDns(row, sn) {
  const ns = (sn && sn.names[row.ip]) || {};
  const f = row.name && Object.keys(ns).find(f => row.name === f || row.name === shortName(f));
  return f ? {fqdn: f, by: ns[f]} : null;
}
function namesProposal({rows, zones, refs, sn, mode = "short", choice = {}}) {
  const out = {fills: [], conflicts: [], skipped: [], kept: [], extra: []};
  if (!sn || !sn.scans) return out;
  const by = {}; // short name -> FQDNs: a short name two domains share keeps its FQDN
  Object.values(sn.names).forEach(ns => Object.keys(ns).forEach(f => (by[shortName(f)] ||= new Set()).add(f)));
  const shown = f => mode === "fqdn" || by[shortName(f)].size > 1 ? f : shortName(f);
  for (const r of rows) {
    const ns = sn.names[r.ip] || {}, cands = Object.keys(ns);
    if (!cands.length) continue;
    if (r.name && !namesDns(r, sn)) { out.kept.push(r); continue; } // the auditor's name: never touched
    let f = cands[0];
    if (cands.length > 1) { out.conflicts.push({r, ns}); if (!cands.includes(choice[r.ip])) continue; f = choice[r.ip]; }
    const target = shown(f);
    if (r.name === target) continue;
    if (zones.includes(target)) { out.skipped.push({r, target, fqdn: f, kind: "zone"}); continue; }
    out.fills.push({r, target, fqdn: f, keptFqdn: mode === "short" && target === f && f.includes(".")});
  }
  // a change that makes a Machine named by the Flow Policy disappear is skipped (the Flow Policy would not load)
  const after = new Map(rows.map(r => [r.ip, r.name || r.ip]));
  out.fills.forEach(x => after.set(x.r.ip, x.target));
  for (const m of Object.keys(refs || {}).filter(k => refs[k] > 0)) {
    if (!rows.some(r => (r.name || r.ip) === m) || [...after.values()].includes(m)) continue;
    out.fills.filter(x => (x.r.name || x.r.ip) === m).forEach(x => {
      out.fills.splice(out.fills.indexOf(x), 1); after.set(x.r.ip, m);
      out.skipped.push({...x, kind: "policy", machine: m});
    });
  }
  // merges: Interfaces sharing a name are one Machine
  const count = {}; after.forEach(n => count[n] = (count[n] || 0) + 1);
  out.fills.forEach(x => {
    const k = count[x.target]; if (k < 2) return;
    x.merge = rows.some(r => r.name === x.target && !out.fills.some(y => y.r === r)) ? `joins Machine ${x.target} · ${k} Interfaces` : `one Machine with ${k} Interfaces`;
  });
  const have = new Set(rows.map(r => r.ip));
  out.extra = Object.entries(sn.seen).filter(([ip]) => !have.has(ip)).map(([ip, s]) => {
    const ns = Object.keys(sn.names[ip] || {});
    return {ip, verdict: s.verdict, by: s.by, target: ns.length === 1 ? shown(ns[0]) : "", names: ns};
  });
  return out;
}
// the proposal as the Scans and Flow Policy pages see it: the inventory as saved, default mode
async function namesWaiting() {
  const [inv, sn] = await Promise.all([api("/api/inventory"), api("/api/scan-names")]);
  const rows = inv.rows.filter(r => r.ip), zones = [...new Set([...inv.zones.map(z => z.name), ...rows.map(r => r.zone).filter(Boolean)])];
  return {sn, rows, pending: namesPending(namesProposal({rows, zones, refs: inv.refs, sn}))};
}
// what still waits for the auditor (Scans line, Flow Policy modal): empty names and missing IPs only; a "⇄ DNS" name in
// the other form is a choice, not news, and conflicts alone do not count ("don't decide" is an answer)
function namesPending(p) {
  const fills = p.fills.filter(x => !x.r.name), conflicts = p.conflicts.filter(c => !c.r.name);
  return {fills, conflicts, extra: p.extra, keys: [...fills.map(x => `n:${x.r.ip}:${x.fqdn}`), ...conflicts.map(c => `c:${c.r.ip}`), ...p.extra.map(e => `a:${e.ip}`)], any: fills.length + p.extra.length > 0};
}
