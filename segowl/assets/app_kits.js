// SegOWL — Auditor Kits page (ticket 06). The server does every file operation (segowl/kits.py).
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
async function api(path, body, raw) {
  const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1", "Content-Type": raw ? "application/zip" : "application/json"}, body: raw ? body : JSON.stringify(body)};
  const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
  if (!r.ok) { const e = new Error(j.error || r.statusText); e.exists = j.exists; throw e; }
  return j;
}
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3500); }
const SHORT = {"port_groups.csv": "Port Groups", "scan_profiles.csv": "Scan Profiles", "port_labels.csv": "Port Labels"};
const rows = text => text.split(/\r?\n/).slice(1).filter(l => l.trim() && !l.startsWith("#")).length;

let D = null, open = null, zip = null;
function draw() {
  $("#kl").innerHTML = `<tr><th>Kit</th><th>Folder</th><th>Contents</th><th></th></tr>` + D.kits.map((k, i) => `<tr>
    <td><b>${esc(k.name)}</b> ${k.shipped ? `<span class="pill">shipped · read-only</span>` : ""}</td>
    <td class="small muted">${esc(k.dir)}</td>
    <td>${Object.keys(SHORT).map(n => k.files[n] !== undefined ? `<span class="pill grp" title="${esc(k.files[n])}">${SHORT[n]} ${rows(k.files[n])}</span>` : `<span class="pill" title="not in the kit: shipped defaults">${SHORT[n]}: defaults</span>`).join("")}</td>
    <td style="white-space:nowrap"><button class="btn sm" data-apply="${i}">Apply to this Mission…</button>
      <a class="btn sm" href="/api/kits/export?dir=${encodeURIComponent(k.dir)}&name=${encodeURIComponent(k.name)}">Export .zip</a></td></tr>
    ${open && open.i === i ? `<tr><td colspan="4">${preview(open.report)}</td></tr>` : ""}`).join("")
    || `<tr><td class="muted">No kit yet.</td></tr>`;
  const dirs = D.dirs.map(d => `<option>${esc(d)}</option>`).join("");
  document.querySelectorAll(".kd").forEach(s => { const v = s.value; s.innerHTML = dirs || `<option value="">add a kit folder first</option>`; if (D.dirs.includes(v)) s.value = v; });
  $("#mfiles").innerHTML = "This Mission has: " + (D.mission.map(n => `<code>${n}</code>`).join(", ") || "none of the three files (it uses the shipped defaults)");
  $("#dl").innerHTML = D.dirs.map((d, i) => `<div class="rule"><code style="flex:1">${esc(d)}</code><span class="x muted" data-rmdir="${i}" title="Forget this folder (its files stay)">✕</span></div>`).join("")
    || `<div class="small muted">None yet: add one to save or import kits.</div>`;
}
function preview(report) {
  return `<div class="warn"><b>Applying replaces the Mission's files:</b>${Object.entries(report).map(([n, v]) => `<div><code>${n}</code>: ${esc(v)}</div>`).join("")}
    <div class="banner" style="margin-top:6px"><button class="btn pri sm" id="go">Apply</button><button class="btn sm" id="no">Cancel</button></div></div>`;
}
function result(el, cls, text, retry) {
  $(el).innerHTML = `<div class="${cls}">${esc(text)}${retry ? ` <button class="btn sm" id="ow">Overwrite</button>` : ""}</div>`;
  if (retry) $("#ow", $(el)).onclick = retry;
}

document.addEventListener("click", async e => {
  const t = e.target;
  try {
    if (t.dataset.apply !== undefined) {
      const k = D.kits[+t.dataset.apply];
      const r = await api("/api/kits/preview", {dir: k.dir, name: k.name});
      open = {i: +t.dataset.apply, report: r.report, fp: r.fp}; draw();
    } else if (t.id === "go") {
      const k = D.kits[open.i]; D = await api("/api/kits/apply", {dir: k.dir, name: k.name, fp: open.fp}); open = null; draw();
      toast(`Kit ${k.name} applied: the report is regenerated with it`);
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
  try { D = await api("/api/kits/import?" + q, zip, true); draw(); result("#ires", "ok", D.message); zip = null; $("#ib").disabled = true; $("#ib").textContent = "Import"; }
  catch (err) { result("#ires", "err", err.message, err.exists && (() => importKit(true))); }
}
$("#ib").onclick = () => importKit();

(async () => { try { D = await api("/api/kits"); draw(); } catch (err) { $("#msg").innerHTML = `<div class="err">Not loaded: ${esc(err.message)}</div>`; } })();
