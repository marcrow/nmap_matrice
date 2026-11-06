// SegOWL — Inventory & Zones editor (ticket 03). Data: GET/POST /api/inventory, autosave with fingerprints.
"use strict";
const BASE = ["ip", "zone", "type", "name"];


// ---------------------------------------------------------------- state
let D = null, table = null, filterZone = null, dirty = false, saving = false, again = false, timer = null, hold = false, H = null;
let dupSet = new Set(), nameCount = {};
const rows = () => table.getData();
const zoneNames = () => { const s = [...D.zones.map(z => z.name)]; rows().forEach(r => { if (r.zone && !s.includes(r.zone)) s.push(r.zone); }); return s; };
// ponytail: zoneNames() scans the rows on every chip; cache the sorted list if a large inventory feels slow
const zoneColor = z => ZONE_COLORS[Math.max(0, [...zoneNames()].sort().indexOf(z)) % ZONE_COLORS.length];
const zoneChip = z => { const [f, s, t] = zoneColor(z); return `<span class="zonechip" style="background:${f};border-color:${s};color:${t}">${esc(z)}</span>`; };
const machineNames = () => [...new Set(rows().map(r => r.name).filter(Boolean))].sort();
const ipOk = v => /^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$/.test(v) || (v.includes(":") && /^[0-9a-fA-F:.]+$/.test(v));
const zoneUse = z => ({ifs: rows().filter(r => r.zone === z).length, rules: D.refs[z] || 0});

// ---------------------------------------------------------------- save
function changed(label) { H?.changed(label); persist(); }
function persist() { analyse(); refreshSide(); dirty = true; status("Unsaved changes…"); clearTimeout(timer); if (!hold) timer = setTimeout(save, 1000); }
// undo / redo (undoable, app_common.js): rows, Zones and extra columns as they were before each change
const state = () => ({rows: rows(), zones: D.zones, columns: D.columns});
function restore(s) { D.zones = s.zones; D.columns = s.columns; table.setColumns(columns()); table.replaceData(s.rows).then(() => { table.redraw(true); persist(); }); }
function localError() {
  if (dupSet.size) return `duplicate IP ${[...dupSet][0]}`;
  const bad = rows().find(r => Object.values(r).some(v => v) && !ipOk(String(r.ip || "")));
  return bad ? `invalid IP "${bad.ip || ""}"` : "";
}
async function save() {
  clearTimeout(timer);
  if (saving) { again = true; return; }
  const err = localError();
  if (err) { status("Not saved: " + err, "err"); return; }
  saving = true; status("Saving…");
  try {
    const r = await api("/api/inventory", {fp: D.fp, columns: D.columns, rows: rows(), zones: D.zones});
    D.fp = {...D.fp, ...r.fp}; dirty = false; status("Saved ✓", "ok");
  } catch (e) {
    if (e.status === 409) { status("Modified elsewhere since you loaded it", "err"); banner(`${esc(e.message)}`, [["Reload", () => location.reload(), "pri"]]); }
    else status("Not saved: " + e.message, "err");
  }
  saving = false;
  if (again) { again = false; save(); }
}
async function flush() { if (dirty) await save(); if (dirty) throw new Error("Fix the unsaved changes first"); }
window.addEventListener("beforeunload", e => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });

// ---------------------------------------------------------------- banner (inline confirmations, never a popup)
function banner(html, actions = []) {
  const b = $("#banner");
  b.innerHTML = actions.length || html ? `<div class="warn banner"><span>${html}</span></div>` : "";
  const box = b.firstChild;
  actions.forEach(([label, fn, cls]) => { const btn = document.createElement("button"); btn.className = "btn sm " + (cls || ""); btn.textContent = label; btn.onclick = () => { b.innerHTML = ""; fn(); }; box.append(btn); });
}

// ---------------------------------------------------------------- validation / counts
function analyse() {
  const c = {}; nameCount = {};
  rows().forEach(r => { if (r.ip) c[r.ip] = (c[r.ip] || 0) + 1; if (r.name) nameCount[r.name] = (nameCount[r.name] || 0) + 1; });
  dupSet = new Set(Object.keys(c).filter(k => c[k] > 1));
  const bad = rows().filter(r => Object.values(r).some(v => v) && !ipOk(String(r.ip || ""))).length;
  const nz = rows().filter(r => r.ip && !r.zone).length;
  $("#val").innerHTML = (dupSet.size ? `<div class="err">Duplicate IP: ${[...dupSet].slice(0, 10).map(esc).join(", ")}. Not saved until fixed.</div>` : "")
    + (bad ? `<div class="err">${bad} row(s) with an invalid or missing IP. Not saved until fixed.</div>` : "")
    + (nz ? `<div class="warn">${nz} row(s) without Zone</div>` : "");
  $("#cnt").textContent = `${rows().filter(r => r.ip).length} Interfaces · ${Object.keys(nameCount).length} named Machines`;
}

// ---------------------------------------------------------------- zones sidebar
function refreshSide() {
  $("#zl").innerHTML = `<li class="${filterZone ? "" : "on"}" data-z=""><span class="dot" style="background:#c3cad6"></span>All Zones<span class="n">${rows().length}</span></li>`
    + zoneNames().map(z => { const u = zoneUse(z), d = (D.zones.find(x => x.name === z) || {}).desc || "";
      return `<li class="${filterZone === z ? "on" : ""}" data-z="${esc(z)}" title="${esc(d)}${u.rules ? ` · ${u.rules} Flow Policy reference(s)` : ""}"><span class="dot" style="background:${zoneColor(z)[1]}"></span><span class="zn">${esc(z)}</span><span class="n">${u.ifs}</span>${u.ifs || u.rules ? "" : `<span class="x muted" data-del="${esc(z)}" title="Delete (unused)">✕</span>`}</li>`; }).join("");
  $("#fz").innerHTML = filterZone ? `<span class="pill">Zone: ${esc(filterZone)} <span class="x" id="fzx">✕</span></span>` : "";
  if ($("#fzx")) $("#fzx").onclick = () => { filterZone = null; applyFilter(); refreshSide(); };
  $("#zl").querySelectorAll("li").forEach(li => {
    li.onclick = e => {
      if (e.target.dataset.del) { D.zones = D.zones.filter(z => z.name !== e.target.dataset.del); changed(`Zone ${e.target.dataset.del} deleted`); toast("Zone deleted"); return; }
      filterZone = li.dataset.z || null; applyFilter(); refreshSide();
    };
    li.ondblclick = () => {
      const z = li.dataset.z; if (!z) return;
      const span = li.querySelector(".zn"); span.innerHTML = `<input type="text" value="${esc(z)}">`;
      const i = span.firstChild; i.focus(); i.select(); let done = false;
      const end = ok => { if (done) return; done = true; if (ok && i.value.trim() && i.value.trim() !== z) renameEverywhere("zone", z, i.value.trim()); else refreshSide(); };
      i.onkeydown = e => { if (e.key === "Enter") end(true); if (e.key === "Escape") end(false); };
      i.onblur = () => end(true);
    };
  });
}
async function renameEverywhere(kind, old, nw) {
  if (kind === "zone" && zoneNames().includes(nw)) { toast(`Zone ${nw} already exists`); refreshSide(); return; }
  try {
    await flush();
    const r = await api("/api/rename", {kind, old, new: nw, fp: D.fp});
    D.fp = r.fp;
    const field = kind === "zone" ? "zone" : "name";
    table.getRows().forEach(row => { if (row.getData()[field] === old) row.update({[field]: nw}); });
    if (kind === "zone") { D.zones.forEach(z => { if (z.name === old) z.name = nw; }); if (filterZone === old) filterZone = nw; }
    if (D.refs[old]) { D.refs[nw] = (D.refs[nw] || 0) + D.refs[old]; delete D.refs[old]; }
    analyse(); refreshSide(); dirty = false; H.clear(); status("Saved ✓", "ok"); toast(r.message); // the server rewrote several files: undo stops here
  } catch (e) { toast("Rename refused: " + e.message); refreshSide(); }
}

// ---------------------------------------------------------------- grid
const suggest = {zone: () => zoneNames(), type: () => [...new Set(rows().map(r => r.type).filter(Boolean))].sort(), name: () => machineNames()};
function columns() {
  const ac = f => ({editor: "list", editorParams: {valuesLookup: suggest[f], autocomplete: true, freetext: true, allowEmpty: true, listOnEmpty: true}});
  return [
    {title: "ip", field: "ip", width: 140, editor: "input", formatter: c => { const v = String(c.getValue() || ""), row = c.getRow().getData();
      c.getElement().classList.toggle("bad", dupSet.has(v) || (Object.values(row).some(x => x) && !ipOk(v))); return esc(v); }},
    {title: "zone", field: "zone", width: 150, ...ac("zone"), formatter: c => c.getValue() ? zoneChip(c.getValue()) : (c.getRow().getData().ip ? `<span style="color:#dc2626">— missing —</span>` : "")},
    {title: "type", field: "type", width: 120, ...ac("type")},
    {title: "name", field: "name", width: 160, ...ac("name"), formatter: c => { const n = c.getValue(), k = nameCount[n] || 0; return esc(n) + (k > 1 ? ` <span class="pill" title="${k} Interfaces">${k} ifs</span>` : ""); }},
    ...D.columns.map(f => ({title: f, field: f, editor: "input", width: 130})),
  ];
}
const selCells = () => (table.getRanges() || []).flatMap(r => r.getCells().flat()).filter(c => c.getColumn().getField());
const applyFilter = () => { const q = $("#q").value.toLowerCase(); table.setFilter(r => (!filterZone || r.zone === filterZone) && (!q || Object.values(r).some(v => String(v).toLowerCase().includes(q)))); };
const blank = () => Object.fromEntries([...BASE, ...D.columns].map(c => [c, c === "zone" ? (filterZone || "") : ""]));

function series(vals, n) { // Excel-like: a trailing number increments (vm-01 → vm-02, 10.0.0.1 → 10.0.0.2), else repeat
  const m = vals.map(v => String(v ?? "").match(/^(.*?)(\d+)$/));
  if (vals.length && m.every(Boolean) && m.every(x => x[1] === m[0][1])) {
    const nums = m.map(x => +x[2]), step = nums.length > 1 ? nums.at(-1) - nums.at(-2) : 1, w = m.at(-1)[2].length, pad = m.at(-1)[2].startsWith("0");
    let last = nums.at(-1);
    return Array.from({length: n}, () => { last += step; return m[0][1] + (pad ? String(last).padStart(w, "0") : last); });
  }
  return Array.from({length: n}, (_, i) => vals[i % vals.length]);
}
function cidrHosts(c) {
  const m = c.trim().match(/^(\d+\.\d+\.\d+\.\d+)\/(\d+)$/); if (!m || !ipOk(m[1])) return null;
  const bits = +m[2]; if (bits < 16 || bits > 32) return null;
  const n = m[1].split(".").reduce((a, b) => a * 256 + +b, 0), size = 2 ** (32 - bits), base = n - (n % size), out = [];
  for (let i = size > 2 ? 1 : 0; i < (size > 2 ? size - 1 : size); i++) { const v = base + i; out.push([v >>> 24, (v >> 16) & 255, (v >> 8) & 255, v & 255].join(".")); }
  return out;
}

function buildGrid() {
  table = new Tabulator("#grid", {
    data: D.rows.length ? D.rows : [blank()], height: "64vh", layout: "fitColumns",
    selectableRange: true, selectableRangeColumns: true, selectableRangeRows: true, selectableRangeClearCells: true,
    editTriggerEvent: "dblclick",
    clipboard: "copy", clipboardCopyStyled: false, clipboardCopyConfig: {rowHeaders: false, columnHeaders: false}, clipboardCopyRowRange: "range",
    rowHeader: {resizable: false, frozen: true, width: 50, hozAlign: "center", formatter: "rownum", cssClass: "range-header-col", editor: false},
    columnDefaults: {headerSort: true, headerSortClickElement: "icon", headerHozAlign: "left", resizable: "header"},
    columns: columns(),
  });
  table.on("tableBuilt", () => { H = undoable(state, restore); analyse(); refreshSide(); status("Loaded", "ok"); });
  table.on("cellEdited", cell => {
    if (cell.getField() === "name") machineRenamePrompt(cell);
    changed(`${cell.getField()} edited`); table.redraw(true);
  });
  table.on("cellClick", (e, cell) => { if (e.ctrlKey || e.metaKey || e.shiftKey || !cell.getField() || selCells().length > 1) return; cell.edit(true); });
  table.on("rangeChanged", () => setTimeout(placeHandle)); table.on("rangeAdded", () => setTimeout(placeHandle));
  table.on("scrollVertical", placeHandle); table.on("dataFiltered", () => setTimeout(placeHandle));
}

function machineRenamePrompt(cell) {
  const old = cell.getOldValue(), nw = cell.getValue();
  if (!old || !nw || old === nw) return;
  const others = rows().filter(r => r.name === old).length, refs = D.refs[old] || 0;
  if (!others && !refs) return;
  hold = true;
  const what = [others && `${others} other Interface(s)`, refs && `${refs} Flow Policy reference(s)`].filter(Boolean).join(" and ");
  banner(`Machine <b>${esc(old)}</b> → <b>${esc(nw)}</b>: rename it everywhere (${what})?`, [
    ["Rename everywhere", () => { hold = false; cell.getRow().update({name: old}); dirty = true; renameEverywhere("machine", old, nw); }, "pri"],
    ["Only this row", () => { hold = false; changed("name edited"); }],
  ]);
}

// ---- type-to-fill, Ctrl+D, paste
const fill = document.createElement("input"); fill.className = "fillin"; fill.setAttribute("list", "filldl");
const dl = document.createElement("datalist"); dl.id = "filldl"; document.body.append(fill, dl);
let fillCells = [];
function openFill(key) {
  fillCells = selCells();
  const act = document.querySelector("#grid .tabulator-range-cell-active") || fillCells[0].getElement(), r = act.getBoundingClientRect();
  const f = fillCells[0].getColumn().getField();
  dl.innerHTML = (suggest[f] ? suggest[f]() : []).slice(0, 300).map(v => `<option value="${esc(v)}">`).join("");
  Object.assign(fill.style, {left: r.left + "px", top: r.top + "px", display: "block"});
  fill.value = key; fill.placeholder = `fill ${fillCells.length} cells`; fill.focus();
}
fill.onkeydown = e => {
  if (e.key === "Escape") { fill.style.display = "none"; return; }
  if (e.key !== "Enter") return;
  const v = fill.value; fillCells.forEach(c => c.getRow().update({[c.getColumn().getField()]: v}));
  fill.style.display = "none"; toast(`${fillCells.length} cells ← "${v}"`); table.redraw(true); changed(`${fillCells.length} cells filled`);
};
fill.onblur = () => fill.style.display = "none";
const typing = () => { const a = document.activeElement; return a && (a.closest(".tabulator-editing") || (["INPUT", "TEXTAREA", "SELECT"].includes(a.tagName) && !a.closest("#grid"))); };
document.addEventListener("keydown", e => {
  if (!table || typing() || document.activeElement === fill) return;
  const cells = selCells(); if (!cells.length) return;
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "d") {
    e.preventDefault();
    (table.getRanges() || []).forEach(rg => { const rs = rg.getRows(); rg.getColumns().forEach(col => { const f = col.getField(); if (!f) return; const v = rs[0].getData()[f]; rs.slice(1).forEach(r => r.update({[f]: v})); }); });
    table.redraw(true); changed("Filled down"); toast("Filled down"); return;
  }
  if (e.ctrlKey || e.metaKey || e.altKey || e.key.length !== 1) return;
  if (cells.length > 1) { e.preventDefault(); e.stopPropagation(); openFill(e.key); } else cells[0].edit(true);
}, true);
document.addEventListener("paste", e => {
  if (!table || typing()) return;
  const text = e.clipboardData.getData("text/plain"); if (!text) return;
  e.preventDefault();
  const lines = text.replace(/\r/g, "").replace(/\n$/, "").split("\n").map(l => l.split("\t"));
  const cols = table.getColumns().map(c => c.getField()).filter(Boolean);
  const rg = (table.getRanges() || []).at(-1), cell = rg && rg.getCells().flat().find(c => c.getField()), active = table.getRows("active");
  let r0 = cell ? active.findIndex(r => r.getElement() === cell.getRow().getElement()) : active.length, c0 = cell ? cols.indexOf(cell.getField()) : 0;
  if (c0 === 0 && lines.length > 1 && !ipOk(lines[0][0].trim()) && ipOk(lines[1][0].trim())) lines.shift(); // a header line
  const need = r0 + lines.length - active.length;
  const added = need > 0 ? Array.from({length: need}, blank) : [];
  const go = async () => {
    if (added.length) await table.addData(added, false);
    const rs = table.getRows("active");
    let extra = 0;
    lines.forEach((vals, i) => { const upd = {}; vals.forEach((v, j) => { const f = cols[c0 + j]; if (f) upd[f] = v.trim(); else extra++; }); rs[r0 + i].update(upd); });
    table.redraw(true); changed(`Pasted ${lines.length} row(s)`);
    toast(`Pasted ${lines.length} row(s)${added.length ? `, ${added.length} added` : ""}${extra ? ` · ${extra} cell(s) beyond the last column ignored: add columns first` : ""}`);
  };
  go();
});

// ---- fill handle
const handle = document.createElement("div"); handle.className = "fillh"; handle.title = "Drag down to fill (series)"; document.body.append(handle);
function placeHandle() {
  const a = document.querySelector("#grid .tabulator-range.tabulator-range-active"), h = document.querySelector("#grid .tabulator-tableholder");
  if (!a || !h) { handle.style.display = "none"; return; }
  const r = a.getBoundingClientRect(), g = h.getBoundingClientRect();
  if (r.bottom < g.top || r.bottom > g.bottom + 2) { handle.style.display = "none"; return; }
  Object.assign(handle.style, {display: "block", left: (r.right - 5) + "px", top: (r.bottom - 5) + "px"});
}
let drag = null;
const clearPrev = () => document.querySelectorAll("#grid .fillprev").forEach(x => x.classList.remove("fillprev"));
handle.onmousedown = e => { e.preventDefault(); const rg = (table.getRanges() || []).at(-1); if (rg) drag = {rows: rg.getRows(), cols: rg.getColumns().filter(c => c.getField()), to: []}; };
document.addEventListener("mousemove", e => {
  if (!drag) return;
  const holder = document.querySelector("#grid .tabulator-tableholder"), g = holder.getBoundingClientRect();
  if (e.clientY > g.bottom - 20) holder.scrollTop += 24;
  const el = document.elementFromPoint(e.clientX, Math.min(e.clientY, g.bottom - 4))?.closest(".tabulator-row"); if (!el) return;
  const rs = table.getRows("active"), idx = rs.findIndex(r => r.getElement() === el), last = rs.findIndex(r => r.getElement() === drag.rows.at(-1).getElement());
  clearPrev(); drag.to = idx > last ? rs.slice(last + 1, idx + 1) : [];
  drag.to.forEach(r => drag.cols.forEach(c => r.getCell(c).getElement().classList.add("fillprev")));
  handle.style.top = (e.clientY - 4) + "px";
});
document.addEventListener("mouseup", () => {
  if (!drag) return; clearPrev(); const d = drag; drag = null;
  if (!d.to.length) { placeHandle(); return; }
  d.cols.forEach(c => { const f = c.getField(), vals = series(d.rows.map(r => r.getData()[f]), d.to.length); d.to.forEach((r, i) => r.update({[f]: vals[i]})); });
  toast(`Filled ${d.to.length} row(s) × ${d.cols.length} column(s)`); table.redraw(true); changed(`Filled ${d.to.length} row(s)`); setTimeout(placeHandle, 50);
});

// ---------------------------------------------------------------- toolbar
function wireToolbar() {
  $("#q").oninput = applyFilter;
  $("#delr").onclick = () => {
    const rs = [...new Set(selCells().map(c => c.getRow()))];
    if (!rs.length) { toast("Select cells in the rows to delete first"); return; }
    banner(`Delete ${rs.length} row(s)?`, [["Delete", () => { rs.forEach(r => r.delete()); changed(`${rs.length} row(s) deleted`); toast(`${rs.length} row(s) deleted`); }, "pri"], ["Cancel", () => {}]]);
  };
  $("#addr").onclick = () => { table.addRow(blank(), true).then(() => changed("Row added")); };
  $("#cidrb").onclick = () => {
    const h = cidrHosts($("#cidr").value); if (!h) { toast("Give a CIDR between /16 and /32, e.g. 10.0.2.0/24"); return; }
    const have = new Set(rows().map(r => r.ip)), nw = h.filter(ip => !have.has(ip)).map(ip => ({...blank(), ip}));
    table.addData(nw, true).then(() => { changed(`${nw.length} row(s) added from ${$("#cidr").value}`); toast(`${nw.length} row(s) added at the top (${h.length - nw.length} already present). Select their type cells and type "vm".`); });
  };
  $("#addc").onclick = () => { $("#addcp").hidden = false; $("#addcn").value = ""; $("#addcn").focus(); };
  $("#addcn").onkeydown = e => {
    if (e.key === "Escape") { $("#addcp").hidden = true; return; }
    if (e.key !== "Enter") return;
    const n = $("#addcn").value.trim().replace(/[\s;]+/g, "_").toLowerCase();
    if (!n || D.columns.includes(n) || BASE.includes(n)) { toast("Name taken or empty"); return; }
    D.columns.push(n); table.setColumns(columns()); $("#addcp").hidden = true; changed(`Column ${n} added`); toast(`Column "${n}" added`);
  };
  $("#addcn").onblur = () => setTimeout(() => $("#addcp").hidden = true, 150);
  $("#nzb").onclick = () => { const n = $("#nz").value.trim(); if (!n || zoneNames().includes(n)) return; D.zones.push({name: n, desc: ""}); $("#nz").value = ""; changed(`Zone ${n} created`); toast(`Zone ${n} created`); };
  $("#nz").onkeydown = e => { if (e.key === "Enter") $("#nzb").click(); };
  $("#dl").onclick = async e => { if (dirty) { e.preventDefault(); try { await flush(); location.href = "/api/file/inventory.csv"; } catch (err) { toast(err.message); } } };
  $("#izf").onchange = async () => {
    const f = $("#izf").files[0]; $("#izf").value = ""; if (!f) return;
    const p = await api("/api/parse/inventory", await f.text(), true);
    const add = [...new Set(p.rows.map(r => r.zone).filter(Boolean))].filter(z => !zoneNames().includes(z));
    add.forEach(z => D.zones.push({name: z, desc: ""}));
    if (add.length) changed(`${add.length} Zone(s) imported`);
    toast(add.length ? `Imported ${add.length} Zone(s), no Interfaces: ${add.join(", ")}` : "No new Zone in that file");
  };
  $("#upf").onchange = async () => {
    const f = $("#upf").files[0]; $("#upf").value = ""; if (!f) return;
    const p = await api("/api/parse/inventory", await f.text(), true);
    banner(`Replace the ${rows().length} current row(s) with the ${p.rows.length} row(s) of <b>${esc(f.name)}</b>?`, [
      ["Replace", () => { p.columns.forEach(c => { if (!D.columns.includes(c)) D.columns.push(c); }); table.setColumns(columns()); table.replaceData(p.rows).then(() => changed(`Replaced by ${f.name}`)); }, "pri"],
      ["Cancel", () => {}],
    ]);
  };
}

// ---------------------------------------------------------------- boot
(async () => {
  try { D = await api("/api/inventory"); } catch (e) { status("Cannot load: " + e.message, "err"); return; }
  buildGrid(); wireToolbar();
})();
