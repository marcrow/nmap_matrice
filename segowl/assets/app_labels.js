// SegOWL — Port Labels editor (app-navigation ticket 05). The server checks and normalises every row.
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const {esc, api, tokOk, toks, normTags} = Ports;
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3800); }
function status(text, cls = "") { const s = $("#st"); s.textContent = text; s.className = "status " + cls; }
const ORD = {shipped: 0, override: 1, mission: 2};
const badge = o => ({shipped: `<span class="badge shipped">shipped</span>`, mission: `<span class="badge b-mission">Mission</span>`,
  override: `<span class="badge override" title="completes the shipped label of the same port + product">Mission · replaces</span>`}[o]);
const key = r => (r[0] + "|" + r[1]).toLowerCase();

let D = null, table = null, shippedTags = new Set();
const vocab = () => Ports.vocabOf(D);
function rows() {
  const mk = new Set(D.mission.map(key)), sk = new Set(D.shipped.map(key));
  const pn = p => +String(p).replace(/^\D+:/, "").split("-")[0];
  const mk1 = (r, origin, i) => ({id: origin === "shipped" ? "s" + key(r) : "m" + i, mi: i, port: r[0], product: r[1], tags: r[2], vendor: r[3], cleartext: r[4], origin});
  return [...D.shipped.filter(r => !mk.has(key(r))).map(r => mk1(r, "shipped")), ...D.mission.map((r, i) => mk1(r, sk.has(key(r)) ? "override" : "mission", i))]
    .sort((a, b) => pn(a.port) - pn(b.port) || a.port.localeCompare(b.port) || a.product.localeCompare(b.product));
}
const tagPills = s => toks(s).map(t => `<span class="pill ${shippedTags.has(t) ? "" : "newtag"}" title="${shippedTags.has(t) ? "" : "tag only used by this Mission"}">${esc(t)}</span>`).join("");
const clearPill = v => v === "yes" ? `<span class="pill clear">cleartext</span>` : v === "no" ? `<span class="pill enc">encrypted</span>` : `<span class="muted">—</span>`;

function setData(d) {
  D = d; shippedTags = new Set(D.shipped.flatMap(r => toks(r[2])));
  const keep = (id, opts) => { const v = $(id).value; $(id).innerHTML = $(id).options[0].outerHTML + opts.map(o => `<option>${esc(o)}</option>`).join(""); $(id).value = v; };
  keep("#lt", Object.keys(vocab()).sort()); keep("#lv", Ports.vendorsOf(D));
  return table.replaceData(rows()).then(count);
}
function count() { $("#lcount").textContent = `${table.getDataCount("active")} shown · ${table.getDataCount()} labels · ${D.mission.length} from this Mission`; }
async function save(msg) {
  status("Saving…");
  try { D.fp = (await api("/api/labels", {fp: D.fp, labels: D.mission})).fp; status("Saved ✓", "ok"); if (msg) toast(msg); }
  catch (e) {
    status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err");
    if (e.status !== 409) setData(await api("/api/labels")); // back to what the file holds
  }
}

function tagEditor(cell, onRendered, success, cancel) {
  const input = document.createElement("input"); input.type = "text"; input.value = cell.getValue() || ""; input.style.cssText = "width:100%;padding:3px 6px;box-sizing:border-box";
  onRendered(() => { input.focus(); input.setSelectionRange(input.value.length, input.value.length); Ports.attachTags(input, vocab, {onCommit: success, onCancel: cancel}); });
  return input;
}
const mine = c => c.getRow().getData().origin !== "shipped", own = c => c.getRow().getData().origin === "mission";
table = new Tabulator("#grid", {data: [], index: "id", layout: "fitColumns", height: "calc(100vh - 340px)",
  rowFormatter: r => r.getElement().classList.toggle("shipped", r.getData().origin === "shipped"),
  columns: [
    {title: "source", field: "origin", width: 150, formatter: c => badge(c.getValue()), sorter: (a, b) => ORD[a] - ORD[b]},
    {title: "port", field: "port", width: 110, editor: "input", editable: own, sorter: (a, b) => +a.replace(/^\D+:/, "").split("-")[0] - +b.replace(/^\D+:/, "").split("-")[0],
      formatter: c => { c.getElement().classList.toggle("bad", !tokOk(c.getValue())); return `<b>${esc(c.getValue())}</b>`; }},
    {title: "product", field: "product", minWidth: 200, editor: "input", editable: own, formatter: c => { c.getElement().classList.toggle("bad", !c.getValue()); return esc(c.getValue()); }},
    {title: "tags", field: "tags", minWidth: 170, editor: tagEditor, editable: mine, formatter: c => tagPills(c.getValue())},
    {title: "vendor", field: "vendor", width: 150, editor: "list", editable: mine, editorParams: {valuesLookup: () => Ports.vendorsOf(D), autocomplete: true, freetext: true, allowEmpty: true, listOnEmpty: true}},
    {title: "cleartext", field: "cleartext", width: 115, editor: "list", editable: mine, editorParams: {values: {"yes": "yes: cleartext", "no": "no: encrypted", "": "unknown / mixed"}}, formatter: c => clearPill(c.getValue())},
    {title: "", field: "act", width: 105, headerSort: false, formatter: c => ({shipped: `<button class="btn sm" data-act="complete">Complete</button>`, override: `<button class="btn sm" data-act="reset">Reset</button>`, mission: `<button class="btn sm" data-act="del">Delete</button>`}[c.getRow().getData().origin]),
      cellClick: (e, c) => {
        const a = e.target.dataset?.act, d = c.getRow().getData(); if (!a) return;
        if (a === "complete") {
          D.mission.push([d.port, d.product, d.tags, d.vendor, d.cleartext]); const i = D.mission.length - 1;
          setData(D).then(() => table.getRow("m" + i)?.getCell("vendor").edit());
          save(`${d.port} · ${d.product} copied into this Mission: complete it, it replaces the shipped label`);
        } else {
          D.mission.splice(d.mi, 1); setData(D);
          save(a === "reset" ? `${d.port} · ${d.product}: back to the shipped label` : `${d.port} · ${d.product} deleted`);
        }
      }},
  ]});
table.on("cellEdited", c => {
  const d = c.getRow().getData(), i = {port: 0, product: 1, tags: 2, vendor: 3, cleartext: 4}[c.getField()];
  let v = String(c.getValue() ?? "").trim(); if (c.getField() === "tags") v = normTags(v);
  if (D.mission[d.mi][i] === v) return;
  D.mission[d.mi][i] = v;
  const nt = c.getField() === "tags" ? toks(v).filter(t => !shippedTags.has(t) && vocab()[t] === 1) : [];
  setData(D); save(nt.length ? `New tag ${nt.join(", ")}: kept, only used by this Mission` : "");
});
function filt() {
  const q = $("#lq").value.trim().toLowerCase(), t = $("#lt").value, v = $("#lv").value, m = $("#lm").checked;
  table.setFilter(d => (!q || d.port.includes(q) || d.product.toLowerCase().includes(q) || d.vendor.toLowerCase().includes(q))
    && (!t || toks(d.tags).includes(t)) && (!v || d.vendor === v) && (!m || d.origin !== "shipped"));
}
["lq", "lt", "lv", "lm"].forEach(id => $("#" + id).addEventListener(id === "lq" ? "input" : "change", filt));
table.on("dataFiltered", () => setTimeout(count));
$("#ladd").onclick = () => {
  $("#ladd").disabled = true;
  Ports.labelForm($("#lfbox"), {
    onCancel: () => { $("#ladd").disabled = false; },
    onAdded: L => {
      $("#ladd").disabled = false; const i = L.mission.length - 1, r = L.mission[i];
      toast(`Port Label ${r[0]} · ${r[1]} added to this Mission`); status("Saved ✓", "ok");
      setData(L).then(() => { const id = "m" + i; table.scrollToRow(id, "center", false); const el = table.getRow(id)?.getElement(); if (el) { el.style.outline = "2px solid #00C8FF"; setTimeout(() => el.style.outline = "", 2500); } });
    }});
};
table.on("tableBuilt", () => api("/api/labels").then(d => { Ports.setLabels(d); return setData(d); }).then(() => status("Loaded")).catch(e => status("Not loaded: " + e.message, "err")));
