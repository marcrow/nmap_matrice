// SegOWL — Flow Policy editor (ticket 05): Zone × Zone matrix + exceptions. Validation is the CLI's own (server).
// policy-copy-cells 02: spreadsheet selection, copy / paste of cell decisions, undo / redo of every change.
"use strict";
const zoneColor = z => ZONE_COLORS[Math.max(0, [...D.zones].sort().indexOf(z)) % ZONE_COLORS.length];
const zoneChip = z => { const [f, s, t] = zoneColor(z); return `<span class="zonechip" style="background:${f};border-color:${s};color:${t}">${esc(z)}</span>`; };
const MARK = {allow: "✓", deny: "✕", "": "?"};

let D = null, dirty = false, saving = false, popCell = null, edits = 0;
const rule = (src, dst, ports, action, comment = "") => ({src, dst, ports, action, comment});
const inCell = (s, d) => D.rules.filter(r => r.src === s && r.dst === d);
const isCell = r => D.zones.includes(r.src) && D.zones.includes(r.dst);
const err = r => D.errors[D.rules.indexOf(r)] || "";
const pair = (i, j) => `${D.zones[i]} → ${D.zones[j]}`;

// ---------------------------------------------------------------- history (undoable, app_common.js): the rules before each change
let H = null;
function changed(label = "Edit") { H.changed(label); persist(); }
function persist() { edits++; dirty = true; D.errors = D.rules.map(() => ""); status("Unsaved changes…"); autosave(); draw(); }
function restore(rules) { const before = D.rules; D.rules = rules; persist(); flash(diffCells(before, D.rules)); }

// ---------------------------------------------------------------- save
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
  const Z = D.zones, keep = document.activeElement && document.activeElement.closest && document.activeElement.closest("#pm");
  $("#pm").innerHTML = `<thead><tr><th class="corner" title="select every cell">from ↓ · to →</th>${Z.map((z, j) => `<th data-col="${j}" title="select the column (Ctrl: add it)">${zoneChip(z)}</th>`).join("")}</tr></thead><tbody>`
    + Z.map((s, i) => `<tr><th class="r" data-row="${i}" title="select the row (Ctrl: add it)">${zoneChip(s)}</th>${Z.map((d, j) => {
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
  drawSel();
  if (keep && act) cellEl(...act)?.focus();
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
  const n = selCount();
  el.innerHTML = `<h5>${zoneChip(s)} → ${zoneChip(d)}</h5>`
    + `<div class="small muted">${obs ? `● Observed open: <b>${esc(obs)}</b>` : "Nothing observed open."}</div>`
    + `<div style="margin:8px 0;display:flex;gap:6px;flex-wrap:wrap"><button class="btn sm" data-q="deny">Deny all</button>`
    + `${obs ? `<button class="btn sm" data-q="obs">Allow what's observed</button>` : ""}<button class="btn sm" data-q="clear">Undeclared</button>`
    + `<span style="margin-left:auto"></span><button class="btn sm" id="pcopy" title="Ctrl+C">Copy</button>`
    + `<button class="btn sm" id="ppaste" title="Ctrl+V" ${clip ? "" : "disabled"}>Paste here${n > 1 ? ` (${n} cells)` : ""}</button></div>`
    + `<div class="rule"><span class="small">Only</span><input type="text" id="only" list="pl" placeholder="443 or @web" style="flex:1"><span class="small">then deny the rest</span><button class="btn sm" id="onlyb">Apply</button></div>`
    + `<div style="border-top:1px solid var(--line);margin-top:8px;padding-top:6px">`
    + (inCell(s, d).map(r => `<div class="rule">${ruleEditor(D.rules.indexOf(r))}</div>${err(r) ? `<div class="err small">${esc(err(r))}</div>` : ""}`).join("") || `<div class="small muted">No rule: undeclared.</div>`)
    + `<button class="btn sm" id="addr" style="margin-top:4px">+ rule</button></div>`
    + `<div style="text-align:right;margin-top:8px"><span class="small muted">Esc to close</span> <button class="btn sm pri" id="cl">Done</button></div>`;
  const td = cellEl(i, j), b = td.getBoundingClientRect();
  el.style.left = Math.max(8, Math.min(b.left, innerWidth - 400)) + "px";
  el.style.top = Math.max(8, Math.min(b.bottom + 6, innerHeight - el.offsetHeight - 8)) + "px";
  const reset = () => { D.rules = D.rules.filter(r => !(r.src === s && r.dst === d)); };
  el.querySelectorAll("[data-q]").forEach(x => x.onclick = () => {
    reset();
    if (x.dataset.q === "deny") D.rules.push(rule(s, d, "*", "deny"));
    if (x.dataset.q === "obs") D.rules.push(rule(s, d, obs, "allow", "observed"));
    changed({deny: "Deny all", obs: "Allow what's observed", clear: "Undeclared"}[x.dataset.q] + " on " + pair(i, j));
  });
  const only = () => { const p = $("#only", el).value.trim().replace(/\s+/g, ""); if (!p) return $("#only", el).focus();
    reset(); D.rules.push(rule(s, d, p, "allow"), rule(s, d, "*", "deny")); changed(`Only ${p} on ${pair(i, j)}`); };
  $("#onlyb", el).onclick = only; $("#only", el).onkeydown = e => { if (e.key === "Enter") only(); };
  $("#addr", el).onclick = () => { D.rules.push(rule(s, d, "*", "allow")); changed("Rule added on " + pair(i, j)); };
  $("#pcopy", el).onclick = () => { if (!inSel(i, j)) select([i, j]); copySel(); };
  $("#ppaste", el).onclick = () => { if (!inSel(i, j)) select([i, j]); pasteClip(clip); };
  $("#cl", el).onclick = closePop;
  if (focus && focus.f) { const f = el.querySelector(`[data-f="${focus.f}"][data-i="${focus.i}"]`); if (f) f.focus(); }
}
function closePop() { // the focus goes back to the cell only from inside the popover: a Ctrl+click elsewhere keeps its selection
  const el = $(".pop"), back = el && el.contains(document.activeElement); if (el) el.remove();
  const c = popCell; popCell = null; if (c && back) cellEl(...c)?.focus();
}

// ---------------------------------------------------------------- selection: one or more ranges (Ctrl+click adds one)
let ranges = [], act = null; // range = {a: [i, j], b: [i, j]}; act = the cell holding the focus
const cellEl = (i, j) => $(`#pm td[data-i="${i}"][data-j="${j}"]`);
const box = g => ({r0: Math.min(g.a[0], g.b[0]), r1: Math.max(g.a[0], g.b[0]), c0: Math.min(g.a[1], g.b[1]), c1: Math.max(g.a[1], g.b[1])});
const rect = () => ranges.length === 1 ? box(ranges[0]) : null; // copying takes one rectangle
const inBox = (R, i, j) => i >= R.r0 && i <= R.r1 && j >= R.c0 && j <= R.c1;
const inSel = (i, j) => ranges.some(g => inBox(box(g), i, j));
function selCells() {
  const m = new Map();
  for (const g of ranges) { const R = box(g); for (let i = R.r0; i <= R.r1; i++) for (let j = R.c0; j <= R.c1; j++) m.set(i + "," + j, [i, j]); }
  return [...m.values()];
}
const selCount = () => selCells().length;
const clampC = ([i, j]) => { const n = D.zones.length - 1; return [Math.max(0, Math.min(n, i)), Math.max(0, Math.min(n, j))]; };
function select(a, b = a, add = false) { // a new range; add (Ctrl) keeps the others, and Ctrl+click on a picked cell drops it
  if (!D.zones.length) return;
  a = clampC(a); b = clampC(b);
  const same = g => g.a[0] === a[0] && g.a[1] === a[1] && g.b[0] === b[0] && g.b[1] === b[1];
  if (add && ranges.length > 1 && ranges.some(same)) ranges = ranges.filter(g => !same(g));
  else ranges = add ? [...ranges, {a, b}] : [{a, b}];
  focusAct(ranges.at(-1).b);
}
function extend(b) { if (!ranges.length) return select(b); ranges.at(-1).b = clampC(b); focusAct(ranges.at(-1).b); }
function focusAct(c) { act = c; cellEl(...c)?.focus(); drawSel(); }
function boxOver(el, R) {
  const a = R && cellEl(R.r0, R.c0), b = R && cellEl(R.r1, R.c1);
  if (!a || !b) { el.style.display = "none"; return; }
  const host = $("#pmbox"), o = host.getBoundingClientRect(), A = a.getBoundingClientRect(), B = b.getBoundingClientRect();
  Object.assign(el.style, {display: "block", left: A.left - o.left - host.clientLeft + host.scrollLeft - 3 + "px",
    top: A.top - o.top - host.clientTop + host.scrollTop - 3 + "px", width: B.right - A.left + 6 + "px", height: B.bottom - A.top + 6 + "px"});
}
function drawSel() {
  if (!D) return;
  document.querySelectorAll("#pm td[data-i]").forEach(td => td.classList.toggle("act", !!act && act[0] === +td.dataset.i && act[1] === +td.dataset.j));
  const host = $("#pmbox"); host.querySelectorAll(".selbox").forEach(x => x.remove());
  if (selCount() > 1) ranges.forEach(g => { const el = document.createElement("div"); el.className = "selbox"; host.appendChild(el); boxOver(el, box(g)); });
  boxOver($("#copybox"), copied);
}

// ---------------------------------------------------------------- copy / paste / empty
// The clipboard text: one cell = `ports;action;comment` lines; a block = flow_policy.csv lines under a header naming its rows and columns.
let clip = null, clipText = null, copied = null; // clip = {h, w, rows, cols, cells[r][c] = [{ports, action, comment}]}
const line3 = r => [r.ports, r.action, r.comment].join(";");
function toText(c) {
  if (c.h === 1 && c.w === 1) return c.cells[0][0].map(line3).join("\n") || "# undeclared";
  const out = [`# SegOWL Flow Policy cells · rows: ${c.rows.join(",")} · columns: ${c.cols.join(",")}`];
  c.cells.forEach((row, r) => row.forEach((x, k) => x.forEach(y => out.push([c.rows[r], c.cols[k], y.ports, y.action, y.comment].join(";")))));
  return out.join("\n");
}
function copySel() {
  const R = rect(); if (!R) { toast("Copy takes one cell or one rectangle; Ctrl+click picks the cells to paste into"); return; }
  const rows = D.zones.slice(R.r0, R.r1 + 1), cols = D.zones.slice(R.c0, R.c1 + 1);
  clip = {h: rows.length, w: cols.length, rows, cols, cells: rows.map(s => cols.map(d => inCell(s, d).map(r => ({ports: r.ports, action: r.action, comment: r.comment}))))};
  clipText = toText(clip); copied = R; drawSel();
  if (navigator.clipboard) navigator.clipboard.writeText(clipText).catch(() => {}); // the popover button has no copy event
  toast(`Copied ${clip.h * clip.w > 1 ? clip.h * clip.w + " cells" : pair(R.r0, R.c0)} · select the target cells, then Ctrl+V`);
  if (popCell) pop(...popCell);
}
// one rule from text fields; throws, with the line number, on what the editor cannot take (the server checks the rest)
function chk(ports, action, comment, n) {
  action = String(action ?? "").trim().toLowerCase(); if (action === "undecided") action = "";
  if (!["allow", "deny", ""].includes(action)) throw new Error(`line ${n}: the action must be allow, deny or empty, not “${action}”`);
  ports = String(ports ?? "").replace(/\s+/g, "") || "*";
  for (const t of ports.split(",")) if (!(t === "*" || (t.startsWith("@") && D.groups.includes(t.slice(1))) || Ports.tokOk(t)))
    throw new Error(`line ${n}: “${t}” is not a port, * or a known @group`);
  return {ports, action, comment: String(comment ?? "").trim()};
}
function parseText(text) {
  const lines = text.replace(/\r/g, "").split("\n");
  if (!lines.some(l => l.trim())) throw new Error("the clipboard is empty");
  const head = lines.find(l => /^#\s*SegOWL Flow Policy cells/i.test(l.trim()));
  const body = lines.map((l, k) => [l.trim(), k + 1]).filter(([l]) => l && !l.startsWith("#"));
  if (!body.length) { if (head) throw new Error("no rule under the header"); return {h: 1, w: 1, cells: [[[]]]}; } // "# undeclared"
  const f0 = body[0][0].split(";");
  const one = !head && f0.length >= 2 && (() => { try { chk(f0[0], f0[1], "", 1); return true; } catch (e) { return false; } })();
  if (one) return {h: 1, w: 1, cells: [[body.map(([l, n]) => { const f = l.split(";"); return chk(f[0], f[1], f.slice(2).join(";"), n); })]]};
  // a block: src;dst;ports;action;comment, placed by the header's rows and columns, or by order of appearance (lines from a flow_policy.csv)
  let rows = [], cols = [];
  const m = head && head.match(/rows:\s*([^·]*)·\s*columns:\s*(.*)$/i);
  if (m) { rows = m[1].split(",").map(x => x.trim()).filter(Boolean); cols = m[2].split(",").map(x => x.trim()).filter(Boolean); }
  const recs = body.map(([l, n]) => {
    const f = l.split(";").map(x => x.trim());
    if (f.length < 4) throw new Error(`line ${n}: expected ports;action;comment or src;dst;ports;action;comment`);
    if (/^src$/i.test(f[0])) return null; // the csv header line
    if (!m) { if (!rows.includes(f[0])) rows.push(f[0]); if (!cols.includes(f[1])) cols.push(f[1]); }
    const r = rows.indexOf(f[0]), c = cols.indexOf(f[1]);
    if (r < 0 || c < 0) throw new Error(`line ${n}: ${f[0]} → ${f[1]} is not in the rows / columns of the header`);
    return [r, c, chk(f[2], f[3], f.slice(4).join(";"), n)];
  }).filter(Boolean);
  const cells = rows.map(() => cols.map(() => []));
  recs.forEach(([r, c, x]) => cells[r][c].push(x));
  return {h: rows.length, w: cols.length, cells};
}
function writeCells(targets, label) { // targets: [[i, j, rules]]; each target cell's rules are replaced
  const keys = new Set(targets.map(([i, j]) => D.zones[i] + ";" + D.zones[j]));
  D.rules = D.rules.filter(r => !keys.has(r.src + ";" + r.dst));
  for (const [i, j, rs] of targets) rs.forEach(r => D.rules.push(rule(D.zones[i], D.zones[j], r.ports, r.action, r.comment)));
  changed(label); flash(keys);
}
const nCells = n => `${n} cell${n > 1 ? "s" : ""}`;
function pasteClip(c) {
  if (!ranges.length || !c) return;
  const n = D.zones.length, t = new Map(); let out = 0;
  if (c.h === 1 && c.w === 1) selCells().forEach(([i, j]) => t.set(i + "," + j, [i, j, c.cells[0][0]])); // one cell fills every selected cell
  else ranges.forEach(g => { const R = box(g); // a block lands once at the top left of each range (each Ctrl+clicked cell)
    c.cells.forEach((row, r) => row.forEach((x, k) => { const i = R.r0 + r, j = R.c0 + k; if (i < n && j < n) t.set(i + "," + j, [i, j, x]); else out++; })); });
  const T = [...t.values()];
  writeCells(T, "Pasted into " + nCells(T.length));
  toast(`Pasted into ${nCells(T.length)}${out ? ` (${out} outside the matrix dropped)` : ""} · Ctrl+Z to undo`);
}
function pasteText(text) {
  let c;
  try { c = text === clipText ? clip : parseText(text); }
  catch (e) { toast("Not pasted: " + e.message + ". Nothing changed."); return; }
  pasteClip(c);
}
function emptySel() {
  const t = selCells().filter(([i, j]) => inCell(D.zones[i], D.zones[j]).length).map(([i, j]) => [i, j, []]);
  if (!t.length) return toast("Already undeclared");
  writeCells(t, "Emptied " + nCells(t.length)); toast(`Emptied ${nCells(t.length)} · Ctrl+Z to undo`);
}
function flash(keys) {
  const K = new Set(keys);
  document.querySelectorAll("#pm td[data-i]").forEach(td => {
    if (K.has(D.zones[td.dataset.i] + ";" + D.zones[td.dataset.j])) { td.classList.remove("flash"); void td.offsetWidth; td.classList.add("flash"); } });
}
function diffCells(a, b) { // the Zone pairs whose rules differ between two rule lists
  const by = rs => { const m = {}; rs.filter(isCell).forEach(r => { (m[r.src + ";" + r.dst] ||= []).push(line3(r)); }); return m; };
  const A = by(a), B = by(b);
  return [...new Set([...Object.keys(A), ...Object.keys(B)])].filter(k => (A[k] || []).join("\n") !== (B[k] || []).join("\n"));
}

// ---------------------------------------------------------------- events
const typing = el => el && el.matches && (el.matches("input,textarea,select") || el.isContentEditable);
// shared rule editors (popover and exceptions panel)
document.addEventListener("change", e => { const t = e.target, f = t.dataset.f;
  if (f && t.dataset.i !== undefined) { D.rules[+t.dataset.i][f] = f === "ports" ? t.value.trim().replace(/\s+/g, "") || "*" : t.value.trim(); changed("Rule edited"); } });
document.addEventListener("click", e => {
  const rm = e.target.dataset.rm; if (rm !== undefined) { D.rules.splice(+rm, 1); changed("Rule removed"); return; }
  const add = e.ctrlKey || e.metaKey;
  const td = e.target.closest("#pm td[data-i]");
  if (td) { const i = +td.dataset.i, j = +td.dataset.j;
    if (e.shiftKey) { extend([i, j]); return closePop(); }
    if (add) { select([i, j], [i, j], true); return closePop(); }
    select([i, j]); return pop(i, j); }
  const th = e.target.closest("#pm th");
  if (th) { const n = D.zones.length - 1; closePop();
    if (th.dataset.row !== undefined) return select([+th.dataset.row, 0], [+th.dataset.row, n], add);
    if (th.dataset.col !== undefined) return select([0, +th.dataset.col], [n, +th.dataset.col], add);
    return select([0, 0], [n, n]); }
  const p = $(".pop"); if (p && !p.contains(e.target) && e.target.isConnected) closePop();
});
// Shift / Ctrl+click must not move the focus first (that would reset the selection)
document.addEventListener("mousedown", e => { if ((e.shiftKey || e.ctrlKey || e.metaKey) && e.target.closest("#pm td[data-i]")) e.preventDefault(); });
document.addEventListener("keydown", e => {
  const k = e.key.toLowerCase(), mod = e.ctrlKey || e.metaKey;
  if (e.key === "Escape") { if (popCell) return closePop(); if (copied) { copied = null; drawSel(); } return; }
  if (["Control", "Meta", "Shift"].includes(e.key) && !typing(e.target)) document.body.classList.add("picking");
  if (typing(e.target)) return; // inside a field the browser's own undo / copy / delete apply
  const td = e.target.closest && e.target.closest("#pm td[data-i]");
  if (mod && k === "a" && td) { e.preventDefault(); const n = D.zones.length - 1; return select([0, 0], [n, n]); }
  if ((e.key === "Delete" || e.key === "Backspace") && ranges.length && (td || popCell)) { e.preventDefault(); return emptySel(); }
  if (!td) return;
  const i = +td.dataset.i, j = +td.dataset.j, mv = {ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]}[e.key];
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pop(i, j); const f = $(".pop button"); if (f) f.focus(); }
  if (mv) { e.preventDefault(); if (e.shiftKey) extend([i + mv[0], j + mv[1]]); else select([i + mv[0], j + mv[1]]); }
});
// while Ctrl / Shift is held the popover lets clicks through to the cells it covers
document.addEventListener("keyup", e => { if (["Control", "Meta", "Shift"].includes(e.key)) document.body.classList.remove("picking"); });
window.addEventListener("blur", () => document.body.classList.remove("picking"));
document.addEventListener("focusin", e => { const td = e.target.closest && e.target.closest("#pm td[data-i]");
  if (td && !(act && act[0] === +td.dataset.i && act[1] === +td.dataset.j)) select([+td.dataset.i, +td.dataset.j]); });
const onMatrix = e => !typing(e.target) && ranges.length && (e.target.closest("#pm") || $(".pop")?.contains(e.target) || e.target === document.body);
document.addEventListener("copy", e => { if (!onMatrix(e)) return; e.preventDefault(); copySel(); if (clipText !== null) e.clipboardData.setData("text/plain", clipText); });
document.addEventListener("paste", e => { if (!onMatrix(e)) return; e.preventDefault(); pasteText(e.clipboardData.getData("text/plain")); });
$("#pmbox").addEventListener("scroll", drawSel); window.addEventListener("resize", drawSel);

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
  $("#xc").value = ""; changed("Exception added"); toast("Rule added");
};
$("#boot").onclick = () => {
  let n = 0;
  for (const [k, ports] of Object.entries(D.observed)) {
    const [s, d] = k.split(";");
    if (!inCell(s, d).length) { D.rules.push(rule(s, d, ports, "", "observed")); n++; }
  }
  changed(`Bootstrap (${n} undecided rules)`); toast(`${n} undecided rule(s) added from the observed flows: open each ? cell to allow or deny`);
};

(async () => {
  try { D = await api("/api/policy"); }
  catch (e) { status("Not loaded: " + e.message, "err"); return; }
  H = undoable(() => D.rules, restore);
  $("#pl").innerHTML = ["*", ...D.groups.map(g => "@" + g)].map(x => `<option value="${esc(x)}">`).join("");
  $("#xs").innerHTML = ends(); $("#xd").innerHTML = ends();
  if (!D.zones.length) $("#banner").innerHTML = `<div class="warn">No Zone yet: fill the <a href="/inventory">Inventory</a> first.</div>`;
  const n = D.errors.filter(Boolean).length;
  status(n ? `${n} rule(s) the report refuses: fix them` : "Saved ✓", n ? "err" : "ok");
  draw();
})();
