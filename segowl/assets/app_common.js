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
