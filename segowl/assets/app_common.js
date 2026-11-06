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
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
// The report's Zone hues (render/common.py ZONE_COLORS: pale fill, hue, dark text), in Zone name order as
// the report assigns them; never red, amber or green, which belong to the Flow Policy.
const ZONE_COLORS = [["#eff8ff", "#1565c0", "#0b3c75"], ["#fff3ee", "#8d6e63", "#51352c"], ["#f6f5ff", "#7c4dff", "#3c3072"],
  ["#eafafe", "#1597ad", "#00495e"], ["#f5f5ff", "#3d2a8a", "#3a3173"], ["#eafbfd", "#80deea", "#004954"],
  ["#eafbf9", "#0b5f5a", "#004944"], ["#f7f5ff", "#b9a6f2", "#432e6f"]];
