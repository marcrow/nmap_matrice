// SegOWL — Port Groups editor (app-navigation ticket 04). Validation and file writes are the server's.
"use strict";

// ---------------------------------------------------------------- ports helpers (shared shape with the prototype)
const {tok, tokOk, toks} = Ports;
const portsOk = s => toks(s).length > 0 && toks(s).every(tokOk);
function countPorts(s) { const c = {tcp: 0, udp: 0, sctp: 0}; toks(s).map(tok).filter(Boolean).forEach(t => { c[t.proto] += t.hi - t.lo + 1; }); return c; }
const ORD = {shipped: 0, override: 1, mission: 2};
const badge = o => ({shipped: `<span class="badge shipped">shipped</span>`, mission: `<span class="badge b-mission">Mission</span>`,
  override: `<span class="badge override" title="this Mission's group replaces the shipped one">Mission · replaces</span>`}[o]);

// ---------------------------------------------------------------- state
let D = null, table = null, H = null; // H: undo / redo of this Mission's groups (undoable, app_common.js)
const EXP = new Set(); // groups whose long port list is expanded
const spec = n => D.mission[n] ?? D.shipped[n];
const allNames = () => [...new Set([...Object.keys(D.shipped), ...Object.keys(D.mission)])];
const used = n => D.used[n] || {rules: [], profiles: []};
function rows() {
  return allNames().map(n => ({id: n, name: n, ports: spec(n), shippedPorts: D.shipped[n] || "",
    origin: !(n in D.mission) ? "shipped" : n in D.shipped ? "override" : "mission"}));
}

async function load() { D = await api("/api/groups"); table.replaceData(rows()); status("Loaded"); }
function restore(mission) { D.mission = mission; table.replaceData(rows()); save(); }
async function save() {
  // a group with no port yet (just added) is not saved until it gets one; one with a bad port blocks the save
  const bad = Object.entries(D.mission).filter(([, p]) => toks(p).length && !portsOk(p)).map(([n]) => "@" + n);
  if (bad.length) { status(`Not saved: fix the ports of ${bad.join(", ")}`, "err"); return; }
  const empty = Object.keys(D.mission).filter(n => !toks(D.mission[n]).length);
  status("Saving…");
  try {
    const groups = Object.entries(D.mission).filter(([n]) => !empty.includes(n)).map(([name, ports]) => ({name, ports}));
    D.fp["port_groups.csv"] = (await api("/api/groups", {fp: D.fp["port_groups.csv"], groups})).fp;
    status(empty.length ? `Saved ✓ · ${empty.map(n => "@" + n).join(", ")} kept until it has ports` : "Saved ✓", "ok");
  } catch (e) { status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err"); }
}

function portsEditor(cell, onRendered, success, cancel) {
  const input = document.createElement("input"); input.type = "text"; input.value = cell.getValue() || ""; input.style.cssText = "width:100%;padding:3px 6px;box-sizing:border-box";
  onRendered(() => { input.focus(); input.setSelectionRange(input.value.length, input.value.length);
    Ports.attachPorts(input, {groups: () => Object.fromEntries(allNames().map(n => [n, spec(n)])), onCommit: success, onCancel: cancel}); });
  return input;
}
const portChips = (v, id) => Ports.portChips(v, id, EXP);

// ---------------------------------------------------------------- grid
table = new Tabulator("#grid", {data: [], index: "id", layout: "fitColumns", height: "calc(100vh - 330px)", editTriggerEvent: "dblclick",
  rowFormatter: r => r.getElement().classList.toggle("shipped", r.getData().origin === "shipped"),
  columns: [
    {title: "source", field: "origin", width: 150, formatter: c => badge(c.getValue()), sorter: (a, b) => ORD[a] - ORD[b]},
    {title: "group", field: "name", width: 150, editor: "input", editable: c => c.getRow().getData().origin === "mission", formatter: c => `<b>@${esc(c.getValue())}</b>`,
      tooltip: (e, c) => c.getRow().getData().origin === "mission" ? "click to rename (rewrites the Flow Policy and the Scan Profiles)" : "a shipped group keeps its name"},
    {title: "ports", field: "ports", editor: portsEditor, formatter: c => { const d = c.getRow().getData(); c.getElement().classList.toggle("bad", !portsOk(c.getValue()));
      return portChips(c.getValue(), d.id) + (d.origin === "override" ? `<div class="small muted" title="${esc(d.shippedPorts)}">shipped: ${toks(d.shippedPorts).length} ports</div>` : ""); }},
    {title: "count", field: "count", width: 110, headerSort: false, formatter: c => { const n = countPorts(c.getRow().getData().ports); return `${n.tcp} TCP${n.udp ? ` · ${n.udp} UDP` : ""}${n.sctp ? ` · ${n.sctp} SCTP` : ""}`; }},
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
    toast(a === "reset" ? `@${n}: back to the shipped ports` : `@${n} deleted`); H.changed(a === "reset" ? `@${n} reset` : `@${n} deleted`); table.replaceData(rows()); save(); return; }
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
      try { const r = await api("/api/groups/rename", {old, new: nw, fp: D.fp}); toast(r.message); await load(); H.clear(); } // three files rewritten: undo stops here
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
  H.changed(f === "name" ? `@${c.getOldValue()} renamed` : `@${d.name} ports edited`); table.replaceData(rows()); save();
});
$("#gq").oninput = () => { const q = $("#gq").value.trim().toLowerCase(); table.setFilter(d => !q || d.name.toLowerCase().includes(q) || toks(d.ports).includes(q)); };
$("#gadd").onclick = () => { let n = "new-group", i = 2; while (allNames().includes(n)) n = "new-group-" + i++; D.mission[n] = ""; H.changed(`@${n} added`);
  table.replaceData(rows()).then(() => { table.scrollToRow(n); table.getRow(n).getCell("ports").edit(); }); status("New group: type its ports, double-click its name to rename"); };
table.on("tableBuilt", () => load().then(() => { H = undoable(() => D.mission, restore); }).catch(e => status("Not loaded: " + e.message, "err")));
