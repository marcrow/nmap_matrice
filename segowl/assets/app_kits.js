// SegOWL — Auditor Kits page (ticket 06). The server does every file operation (segowl/kits.py).
"use strict";
const SHORT = {"port_groups.csv": "Port Groups", "scan_profiles.csv": "Scan Profiles", "port_labels.csv": "Port Labels"};
const rows = text => text.split(/\r?\n/).slice(1).filter(l => l.trim() && !l.startsWith("#")).length;

let D = null, open = null, zip = null;
function draw() {
  $("#kl").innerHTML = `<tr><th>Kit</th><th>Folder</th><th>Contents</th><th></th></tr>` + D.kits.map((k, i) => `<tr>
    <td><b>${esc(k.name)}</b> ${k.shipped ? `<span class="pill">shipped · read-only</span>` : ""}</td>
    <td class="small muted">${esc(k.dir)}</td>
    <td>${Object.keys(SHORT).map(n => k.files[n] !== undefined ? `<span class="pill grp" title="${esc(k.files[n])}">${SHORT[n]} ${rows(k.files[n])}</span>` : `<span class="pill" title="not in the kit: applying it leaves the Mission's file as it is">${SHORT[n]}: —</span>`).join("")}</td>
    <td style="white-space:nowrap"><button class="btn sm" data-apply="${i}">Apply to this Mission…</button>
      <a class="btn sm" href="/api/kits/export?dir=${encodeURIComponent(k.dir)}&name=${encodeURIComponent(k.name)}">Export .zip</a></td></tr>
    ${open && open.i === i ? `<tr><td colspan="4">${preview(open)}</td></tr>` : ""}`).join("")
    || `<tr><td class="muted">No kit yet.</td></tr>`;
  const dirs = D.dirs.map(d => `<option>${esc(d)}</option>`).join("");
  document.querySelectorAll(".kd").forEach(s => { const v = s.value; s.innerHTML = dirs || `<option value="">add a kit folder first</option>`; if (D.dirs.includes(v)) s.value = v; });
  $("#mfiles").innerHTML = "This Mission has: " + (D.mission.map(n => `<code>${n}</code>`).join(", ") || "none of the three files (it uses the shipped defaults)");
  $("#dl").innerHTML = D.dirs.map((d, i) => `<div class="rule"><code style="flex:1">${esc(d)}</code><span class="x muted" data-rmdir="${i}" title="Forget this folder (its files stay)">✕</span></div>`).join("")
    || `<div class="small muted">None yet: add one to save or import kits.</div>`;
}
// ---------------------------------------------------------------- apply: pick files, row-level diff
const fmt = v => esc(v).replace(/;/g, ` <span class="muted">·</span> `);
function preview(o) {
  const n = o.files.size;
  return `<div class="kitdiff"><b>Pick the kit files to apply.</b> <span class="small muted">A ticked file replaces the Mission's;
    a file left unticked, or that the kit lacks, stays as it is. <span class="kbd">+</span> row the kit adds ·
    <span class="kbd">−</span> Mission row the kit drops · <span class="kbd">~</span> row the kit changes.</span>
    ${Object.entries(o.diff).map(([f, d]) => fileBlock(f, d, o.files.has(f))).join("")}
    ${o.errors.map(e => `<div class="err">${esc(e)}</div>`).join("")}
    <div class="banner" style="margin-top:8px"><button class="btn pri sm" id="go" ${!n || o.errors.length ? "disabled" : ""}>Apply ${n} file${n === 1 ? "" : "s"}</button>
    <button class="btn sm" id="no">Cancel</button></div></div>`;
}
function fileBlock(f, d, on) {
  if (d.status === "absent") return `<div class="kf"><span class="muted">—</span> <b>${SHORT[f]}</b> <span class="small muted">not in the kit: the Mission's file is kept</span></div>`;
  const lines = [...d.added.map(([k, v]) => `<tr class="add"><td>+</td><td>${esc(k)}</td><td>${fmt(v)}</td></tr>`),
    ...d.removed.map(([k, v]) => `<tr class="del"><td>−</td><td>${esc(k)}</td><td>${fmt(v)}</td></tr>`),
    ...d.changed.map(([k, a, b]) => `<tr class="chg"><td>~</td><td>${esc(k)}</td><td><span class="old">${fmt(a)}</span> → ${fmt(b)}</td></tr>`)];
  const sum = d.status === "same" ? "identical to the Mission's" : `${d.status === "new" ? "the Mission has none yet · " : ""}+${d.added.length} −${d.removed.length} ~${d.changed.length}`;
  const body = lines.length ? `<details ${lines.length <= 30 ? "open" : ""}><summary class="small">${lines.length} row(s) differ</summary><table class="diff">${lines.join("")}</table></details>`
    : d.status === "changed" ? `<div class="small muted">Only comments or formatting differ.</div>` : "";
  return `<div class="kf"><label><input type="checkbox" data-pick="${f}" ${on ? "checked" : ""} ${d.status === "same" ? "disabled" : ""}> <b>${SHORT[f]}</b></label>
    <span class="small muted">${sum}</span>${body}</div>`;
}
async function openApply(i) { // ticks by default every kit file that would change the Mission
  const k = D.kits[i], r = await api("/api/kits/preview", {dir: k.dir, name: k.name});
  open = {i, files: new Set(Object.keys(r.diff).filter(f => ["new", "changed"].includes(r.diff[f].status)))};
  await repreview();
  $("#kl .kitdiff").scrollIntoView({block: "nearest", behavior: "smooth"});
}
async function repreview() { // the errors depend on the files picked (a profile may need the kit's groups)
  const k = D.kits[open.i], r = await api("/api/kits/preview", {dir: k.dir, name: k.name, files: [...open.files]});
  Object.assign(open, {diff: r.diff, errors: r.errors, fp: r.fp}); draw();
}
document.addEventListener("change", e => {
  const f = e.target.dataset.pick; if (!f || !open) return;
  if (e.target.checked) open.files.add(f); else open.files.delete(f);
  repreview().catch(err => { $("#msg").innerHTML = `<div class="err">${esc(err.message)}</div>`; });
});
function result(el, cls, text, retry) {
  $(el).innerHTML = `<div class="${cls}">${esc(text)}${retry ? ` <button class="btn sm" id="ow">Overwrite</button>` : ""}</div>`;
  if (retry) $("#ow", $(el)).onclick = retry;
}

document.addEventListener("click", async e => {
  const t = e.target;
  try {
    if (t.dataset.apply !== undefined) await openApply(+t.dataset.apply);
    else if (t.id === "go") {
      const k = D.kits[open.i], picked = [...open.files];
      D = await api("/api/kits/apply", {dir: k.dir, name: k.name, fp: open.fp, files: picked}); open = null; draw();
      toast(`${picked.map(f => SHORT[f]).join(", ")} of kit ${k.name} applied: the report is regenerated with them`);
    } else if (t.id === "no") { open = null; draw(); }
    else if (t.dataset.rmdir !== undefined) { D = await api("/api/kits/dirs", {dirs: D.dirs.filter((_, i) => i !== +t.dataset.rmdir)}); draw(); }
  } catch (err) { $("#msg").innerHTML = `<div class="err">${esc(err.message)}</div>`; }
});

$("#ndb").onclick = async () => {
  const d = $("#nd").value.trim(); if (!d) return $("#nd").focus();
  try { D = await api("/api/kits/dirs", {dirs: [...D.dirs, d]}); $("#nd").value = ""; draw(); toast("Kit folder added"); }
  catch (err) { $("#msg").innerHTML = `<div class="err">${esc(err.message)}</div>`; }
};
$("#nd").onkeydown = e => { if (e.key === "Enter") $("#ndb").click(); };

async function saveKit(overwrite = false) {
  const name = $("#sn").value.trim(); if (!name) return $("#sn").focus();
  try { D = await api("/api/kits/save", {dir: $("#sd").value, name, overwrite}); draw(); result("#sres", "ok", D.message); }
  catch (err) { result("#sres", "err", err.message, err.exists && (() => saveKit(true))); }
}
$("#sb").onclick = () => saveKit(); $("#sn").onkeydown = e => { if (e.key === "Enter") saveKit(); };

$("#izf").onchange = () => { zip = $("#izf").files[0]; $("#izf").value = ""; if (!zip) return;
  $("#in").value = zip.name.replace(/\.zip$/i, "").replace(/[^A-Za-z0-9_.-]/g, "-"); $("#ib").disabled = false; $("#ib").textContent = "Import " + zip.name; };
async function importKit(overwrite = false) {
  const q = new URLSearchParams({dir: $("#id").value, name: $("#in").value.trim(), overwrite: overwrite ? "1" : ""});
  try {
    D = await api("/api/kits/import?" + q, zip, true); draw(); zip = null; $("#ib").disabled = true; $("#ib").textContent = "Import";
    result("#ires", "ok", D.message + ": its diff with this Mission is open above, pick what to apply");
    const same = k => !k.shipped && k.name === q.get("name"), mine = D.kits.filter(same);
    const i = D.kits.indexOf(mine.length === 1 ? mine[0] : mine.find(k => k.dir === $("#id").value.replace(/\/+$/, "")));
    if (i >= 0) await openApply(i);
  }
  catch (err) { result("#ires", "err", err.message, err.exists && (() => importKit(true))); }
}
$("#ib").onclick = () => importKit();

(async () => { try { D = await api("/api/kits"); draw(); } catch (err) { $("#msg").innerHTML = `<div class="err">Not loaded: ${esc(err.message)}</div>`; } })();
