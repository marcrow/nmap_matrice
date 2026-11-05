// SegOWL — Flow Policy editor (ticket 05): Zone × Zone matrix + exceptions. Validation is the CLI's own (server).
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
async function api(path, body) {
  const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1", "Content-Type": "application/json"}, body: JSON.stringify(body)};
  const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
  if (!r.ok) { const e = new Error(j.error || r.statusText); e.status = r.status; throw e; }
  return j;
}
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3500); }
function status(text, cls = "") { const s = $("#st"); s.textContent = text; s.className = "status " + cls; }
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
// The report's Zone hues (render/common.py ZONE_COLORS, dark tone for white chip text), in Zone name order as
// the report assigns them; never red, amber or green, which belong to the Flow Policy.
const ZONE_COLORS = ["#174276", "#723555", "#0c535f", "#32266f", "#58381a"];
const zoneColor = z => ZONE_COLORS[Math.max(0, [...D.zones].sort().indexOf(z)) % ZONE_COLORS.length];
const zoneChip = z => `<span class="zonechip" style="background:${zoneColor(z)}">${esc(z)}</span>`;
const MARK = {allow: "✓", deny: "✕", "": "?"};

let D = null, dirty = false, saving = false, popCell = null, edits = 0;
const rule = (src, dst, ports, action, comment = "") => ({src, dst, ports, action, comment});
const inCell = (s, d) => D.rules.filter(r => r.src === s && r.dst === d);
const isCell = r => D.zones.includes(r.src) && D.zones.includes(r.dst);
const err = r => D.errors[D.rules.indexOf(r)] || "";

// ---------------------------------------------------------------- save
function changed() { edits++; dirty = true; D.errors = D.rules.map(() => ""); status("Unsaved changes…"); autosave(); draw(); }
const autosave = debounce(save, 700);
async function save() {
  if (saving) { autosave(); return; }
  saving = true; status("Saving…");
  const at = edits;
  try {
    const r = await api("/api/policy", {fp: D.fp, rules: D.rules});
    D.fp = r.fp;
    if (at !== edits) { saving = false; return; } // edited meanwhile: the queued save reports instead
    D.errors = D.rules.map((x, i) => r.errors[i] || "");
    const n = D.errors.filter(Boolean).length;
    if (n) status(`Not saved: ${n} rule(s) to fix`, "err"); else { dirty = false; status("Saved ✓", "ok"); }
    draw();
  } catch (e) { status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err"); }
  saving = false;
}
window.addEventListener("beforeunload", e => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });

// ---------------------------------------------------------------- matrix
function draw() {
  const Z = D.zones;
  $("#pm").innerHTML = `<thead><tr><th class="corner">from ↓ · to →</th>${Z.map(z => `<th>${zoneChip(z)}</th>`).join("")}</tr></thead><tbody>`
    + Z.map((s, i) => `<tr><th class="r">${zoneChip(s)}</th>${Z.map((d, j) => {
      const rs = inCell(s, d), acts = new Set(rs.map(r => r.action)), obs = D.observed[s + ";" + d];
      const cls = [acts.size > 1 ? "mixed" : acts.has("allow") ? "allow" : acts.has("deny") ? "deny" : acts.has("") ? "undecided" : "",
        s === d ? "self" : "", rs.some(err) ? "bad" : ""].join(" ");
      return `<td class="${cls}" data-i="${i}" data-j="${j}" tabindex="0">${rs.map(r => `<div class="lbl">${MARK[r.action] ?? "!"} ${esc(r.ports)}</div>`).join("")}${obs ? `<span class="obs" title="observed open: ${esc(obs)}">● ${esc(obs.length > 14 ? obs.slice(0, 13) + "…" : obs)}</span>` : ""}</td>`;
    }).join("")}</tr>`).join("") + "</tbody>";
  const ex = D.rules.filter(r => !isCell(r));
  $("#ex").innerHTML = ex.map(r => { const i = D.rules.indexOf(r);
    return `<div class="rule"><select data-f="src" data-i="${i}" style="max-width:130px">${ends(r.src)}</select>→<select data-f="dst" data-i="${i}" style="max-width:130px">${ends(r.dst)}</select>${ruleEditor(i)}</div>${err(r) ? `<div class="err small">${esc(err(r))}</div>` : ""}`; }).join("") || `<div class="muted small">none</div>`;
  const pending = Object.keys(D.observed).filter(k => { const [s, d] = k.split(";"); return !inCell(s, d).length; });
  $("#boot").disabled = !pending.length;
  $("#bootn").textContent = Object.keys(D.observed).length ? `${pending.length} observed Zone pair(s) without any rule` : "no Scan with open ports yet";
  if (popCell) pop(...popCell);
}
function ruleEditor(i) {
  const r = D.rules[i];
  return `<input type="text" list="pl" value="${esc(r.ports)}" data-f="ports" data-i="${i}" style="width:120px">`
    + `<select data-f="action" data-i="${i}">${["allow", "deny", ""].map(a => `<option value="${a}" ${a === r.action ? "selected" : ""}>${a || "undecided"}</option>`).join("")}</select>`
    + `<input type="text" value="${esc(r.comment)}" data-f="comment" data-i="${i}" placeholder="comment" style="flex:1;min-width:0">`
    + `<span class="x muted" data-rm="${i}" title="remove">✕</span>`;
}

// ---------------------------------------------------------------- cell popover
function pop(i, j) {
  const s = D.zones[i], d = D.zones[j], obs = D.observed[s + ";" + d];
  if (s === undefined || d === undefined) return closePop();
  popCell = [i, j];
  let el = $(".pop");
  if (!el) { el = document.createElement("div"); el.className = "pop"; document.body.appendChild(el); }
  const focus = document.activeElement && el.contains(document.activeElement) ? document.activeElement.dataset : null;
  el.innerHTML = `<h5>${zoneChip(s)} → ${zoneChip(d)}</h5>`
    + `<div class="small muted">${obs ? `● Observed open: <b>${esc(obs)}</b>` : "Nothing observed open."}</div>`
    + `<div style="margin:8px 0;display:flex;gap:6px;flex-wrap:wrap"><button class="btn sm" data-q="deny">Deny all</button>`
    + `${obs ? `<button class="btn sm" data-q="obs">Allow what's observed</button>` : ""}<button class="btn sm" data-q="clear">Undeclared</button></div>`
    + `<div class="rule"><span class="small">Only</span><input type="text" id="only" list="pl" placeholder="443 or @web" style="flex:1"><span class="small">then deny the rest</span><button class="btn sm" id="onlyb">Apply</button></div>`
    + `<div style="border-top:1px solid var(--line);margin-top:8px;padding-top:6px">`
    + (inCell(s, d).map(r => `<div class="rule">${ruleEditor(D.rules.indexOf(r))}</div>${err(r) ? `<div class="err small">${esc(err(r))}</div>` : ""}`).join("") || `<div class="small muted">No rule: undeclared.</div>`)
    + `<button class="btn sm" id="addr" style="margin-top:4px">+ rule</button></div>`
    + `<div style="text-align:right;margin-top:8px"><span class="small muted">Esc to close</span> <button class="btn sm pri" id="cl">Done</button></div>`;
  const td = $(`#pm td[data-i="${i}"][data-j="${j}"]`), b = td.getBoundingClientRect();
  el.style.left = Math.max(8, Math.min(b.left, innerWidth - 400)) + "px";
  el.style.top = Math.max(8, Math.min(b.bottom + 6, innerHeight - el.offsetHeight - 8)) + "px";
  const reset = () => { D.rules = D.rules.filter(r => !(r.src === s && r.dst === d)); };
  el.querySelectorAll("[data-q]").forEach(x => x.onclick = () => {
    reset();
    if (x.dataset.q === "deny") D.rules.push(rule(s, d, "*", "deny"));
    if (x.dataset.q === "obs") D.rules.push(rule(s, d, obs, "allow", "observed"));
    changed();
  });
  const only = () => { const p = $("#only", el).value.trim().replace(/\s+/g, ""); if (!p) return $("#only", el).focus();
    reset(); D.rules.push(rule(s, d, p, "allow"), rule(s, d, "*", "deny")); changed(); };
  $("#onlyb", el).onclick = only; $("#only", el).onkeydown = e => { if (e.key === "Enter") only(); };
  $("#addr", el).onclick = () => { D.rules.push(rule(s, d, "*", "allow")); changed(); };
  $("#cl", el).onclick = closePop;
  if (focus && focus.f) { const f = el.querySelector(`[data-f="${focus.f}"][data-i="${focus.i}"]`); if (f) f.focus(); }
}
function closePop() { const el = $(".pop"); if (el) el.remove(); const c = popCell; popCell = null; if (c) { const td = $(`#pm td[data-i="${c[0]}"][data-j="${c[1]}"]`); if (td) td.focus(); } }

// shared rule editors (popover and exceptions panel)
document.addEventListener("change", e => { const t = e.target, f = t.dataset.f;
  if (f && t.dataset.i !== undefined) { D.rules[+t.dataset.i][f] = f === "ports" ? t.value.trim().replace(/\s+/g, "") || "*" : t.value.trim(); changed(); } });
document.addEventListener("click", e => {
  const rm = e.target.dataset.rm; if (rm !== undefined) { D.rules.splice(+rm, 1); changed(); return; }
  const td = e.target.closest("#pm td[data-i]"); if (td) return pop(+td.dataset.i, +td.dataset.j);
  const p = $(".pop"); if (p && !p.contains(e.target) && e.target.isConnected) closePop();
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && popCell) return closePop();
  const td = e.target.closest && e.target.closest("#pm td[data-i]"); if (!td) return;
  const i = +td.dataset.i, j = +td.dataset.j, mv = {ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]}[e.key];
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pop(i, j); const f = $(".pop button"); if (f) f.focus(); }
  if (mv) { e.preventDefault(); const n = $(`#pm td[data-i="${i + mv[0]}"][data-j="${j + mv[1]}"]`); if (n) n.focus(); }
});

// ---------------------------------------------------------------- exceptions form, bootstrap
function ends(sel = "*") {
  const o = x => `<option ${x === sel ? "selected" : ""}>${esc(x)}</option>`, known = ["*", ...D.zones, ...D.machines].includes(sel);
  return `<option value="*">* (any)</option>${known ? "" : `<option selected>${esc(sel)}</option>`}<optgroup label="Zones">${D.zones.map(o).join("")}</optgroup>`
    + `<optgroup label="Machines">${D.machines.map(o).join("")}</optgroup>`;
}
let xa = "allow";
$("#xa").onclick = e => { const b = e.target.closest("button"); if (!b) return; xa = b.dataset.a; $("#xa").querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); };
$("#addx").onclick = () => {
  D.rules.push(rule($("#xs").value, $("#xd").value, $("#xp").value.trim().replace(/\s+/g, "") || "*", xa, $("#xc").value.trim()));
  $("#xc").value = ""; changed(); toast("Rule added");
};
$("#boot").onclick = () => {
  let n = 0;
  for (const [k, ports] of Object.entries(D.observed)) {
    const [s, d] = k.split(";");
    if (!inCell(s, d).length) { D.rules.push(rule(s, d, ports, "", "observed")); n++; }
  }
  changed(); toast(`${n} undecided rule(s) added from the observed flows: open each ? cell to allow or deny`);
};

(async () => {
  try { D = await api("/api/policy"); }
  catch (e) { status("Not loaded: " + e.message, "err"); return; }
  $("#pl").innerHTML = ["*", ...D.groups.map(g => "@" + g)].map(x => `<option value="${esc(x)}">`).join("");
  $("#xs").innerHTML = ends(); $("#xd").innerHTML = ends();
  if (!D.zones.length) $("#banner").innerHTML = `<div class="warn">No Zone yet: fill the <a href="/inventory">Inventory</a> first.</div>`;
  const n = D.errors.filter(Boolean).length;
  status(n ? `${n} rule(s) the report refuses: fix them` : "Saved ✓", n ? "err" : "ok");
  draw();
})();
