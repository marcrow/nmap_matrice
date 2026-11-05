// SegOWL — Scans page, step 2 (local-app 04): Sources × Scan Profiles progress, scripts, upload, exclude.
// Own scope: the scan builder (app_profiles.js) shares the page.
"use strict";
(() => {
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
async function api(path, body, raw) {
  const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1"}, body: raw ? body : JSON.stringify(body)};
  if (body !== undefined && !raw) opt.headers["Content-Type"] = "application/json";
  const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.style.opacity = 1; clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 3500); }
const msg = (text, cls) => { $("#msg").innerHTML = text ? `<div class="${cls}"></div>` : ""; if (text) $("#msg").firstChild.textContent = text; };
let D = null;
const candLabel = c => [c.ip, c.name, c.zone].filter(Boolean).join(" · ");

function render() {
  const has = (src, base) => src.files.some(f => !f.excluded && f.name.replace(/\.(xml|gnmap|nmap)$/i, "") === base);
  $("#candl").innerHTML = D.candidates.map(c => `<option value="${esc(c.ip)}" label="${esc(candLabel(c))}"></option>`).join("");
  $("#cand").placeholder = D.candidates.length ? "Add a Source: type an IP, a name or a Zone" : "every inventory IP is already a Source";
  const picked = $("#zp").value;  // render() runs on its own change: keep the pick, the rebuild would reset it
  $("#zp").innerHTML = D.profiles.map(p => `<option>${esc(p.name)}</option>`).join("") || `<option value="">no Scan Profile yet</option>`;
  if (D.profiles.some(p => p.name === picked)) $("#zp").value = picked;
  $("#zip").href = D.profiles.length && D.sources.length ? "/api/scripts.zip?profile=" + encodeURIComponent($("#zp").value) : "#";
  if (!D.sources.length) { $("#grid").innerHTML = `<tr><td class="muted" style="padding:16px">No Source yet: add one above (the IPs you will scan from).</td></tr>`; return; }
  $("#grid").innerHTML = `<tr><th>Source</th>${D.profiles.map(p => `<th title="expects ${esc(p.expected.join(", "))}">${esc(p.name)}</th>`).join("")}<th>Scans in the folder</th></tr>`
    + D.sources.map(s => `<tr data-src="${esc(s.ip)}"><td><b>${esc(s.ip)}</b>${s.name ? " · " + esc(s.name) : ""}<div class="small muted">${esc(s.zone)}${s.known ? "" : '<span style="color:#8a1a1a">not in the inventory: ignored by the report</span>'}</div>`
      + (s.files.length ? "" : `<button class="btn sm" data-rm="${esc(s.ip)}" style="margin-top:4px">Remove</button>`) + `</td>`
      + D.profiles.map(p => { const got = p.expected.filter(b => has(s, b)), done = p.expected.length && got.length === p.expected.length;
        const missing = p.expected.filter(b => !has(s, b)), state = done ? "✓ done" : got.length ? `${got.length}/${p.expected.length} Scans` : "not run";
        if (window.SegDraft?.modified && window.SegDraft.name === p.name) return `<td class="${done ? "done" : "todo"}" title="${esc(p.name)} is modified above: save or discard the changes to download its script">${done ? "✓" : got.length ? `${got.length}/${p.expected.length}` : "—"} · <i>modified</i></td>`;
        return `<td class="${done ? "done" : "todo"}"><div title="${done ? "every expected Scan is in the folder" : "missing: " + esc(missing.join(", "))}">${state}</div><a class="btn sm" href="/api/script?src=${encodeURIComponent(s.ip)}&profile=${encodeURIComponent(p.name)}" title="the script to run on ${esc(s.ip)}">⬇ Script</a></td>`; }).join("")
      + `<td><div class="files">${s.files.map(f => `<div><span class="${f.excluded ? "ex" : ""}">${esc(f.name)}</span><button class="btn sm" data-src="${esc(s.ip)}" data-name="${esc(f.name)}" data-ex="${f.excluded ? "" : "1"}">${f.excluded ? "re-include" : "exclude"}</button></div>`).join("")}</div>`
      + `<label class="btn sm" style="margin-top:4px">Add files…<input type="file" multiple accept=".xml,.gnmap,.nmap" hidden></label> <span class="small muted">or drop them on the row</span></td></tr>`).join("");
  $("#grid").querySelectorAll("button[data-name]").forEach(b => b.onclick = async () => {
    try { D = await api("/api/scans/move", {src: b.dataset.src, name: b.dataset.name, exclude: !!b.dataset.ex}); render(); toast(b.dataset.ex ? "Excluded: kept in excluded/, no longer read" : "Re-included"); }
    catch (e) { msg(e.message, "err"); }
  });
  $("#grid").querySelectorAll("button[data-rm]").forEach(b => b.onclick = async () => {
    try { D = await api("/api/scans/source/remove", {ip: b.dataset.rm}); render(); toast(`Source ${b.dataset.rm} removed`); msg(""); }
    catch (e) { msg(e.message, "err"); }
  });
  $("#grid").querySelectorAll("tr[data-src]").forEach(tr => {
    // "dropping", not "drop": .drop is the dropdown class (position:absolute) and pulled the rows out of the table
    tr.ondragover = e => { e.preventDefault(); tr.classList.add("dropping"); };
    tr.ondragleave = e => { if (!tr.contains(e.relatedTarget)) tr.classList.remove("dropping"); };
    tr.ondrop = e => { e.preventDefault(); tr.classList.remove("dropping"); upload(tr.dataset.src, e.dataTransfer.files); };
    const input = tr.querySelector("input[type=file]");
    input.onchange = () => upload(tr.dataset.src, input.files);
  });
}
async function upload(src, files) {
  for (const f of files) {
    try { D = await api(`/api/scans/upload?src=${encodeURIComponent(src)}&name=${encodeURIComponent(f.name)}`, f, true); toast(`${f.name} stored for ${src}`); msg(""); }
    catch (err) { msg(`${f.name}: ${err.message}`, "err"); }
  }
  render();
}
$("#adds").onclick = async () => {
  const q = $("#cand").value.trim().toLowerCase();
  if (!q) return;
  // an exact IP, or the one candidate whose IP · name · Zone contains what was typed
  const hits = D.candidates.filter(c => c.ip === q || candLabel(c).toLowerCase().includes(q));
  const c = hits.find(c => c.ip === q) || (hits.length === 1 && hits[0]);
  if (!c) { msg(hits.length ? `${hits.length} Sources match "${q}": pick one in the list` : `no inventory IP matches "${q}"`, "err"); return; }
  try { D = await api("/api/scans/source", {ip: c.ip}); $("#cand").value = ""; msg(""); render(); toast(`Source ${c.ip} added: scans/${c.ip}/`); } catch (e) { msg(e.message, "err"); }
};
$("#cand").onkeydown = e => { if (e.key === "Enter") $("#adds").click(); };
$("#zp").onchange = render;
$("#zip").onclick = e => {
  if (window.SegDraft?.modified && window.SegDraft.name === $("#zp").value) { e.preventDefault(); toast(`${$("#zp").value} is modified above: save or discard the changes first`); return; }
  if ($("#zip").getAttribute("href") === "#") { e.preventDefault(); toast("Add a Source and a Scan Profile first"); }
};
window.addEventListener("draftchange", () => D && render());
window.addEventListener("profiles-saved", async () => { try { D = await api("/api/scans"); render(); } catch (e) { msg(e.message, "err"); } });
(async () => { try { D = await api("/api/scans"); render(); } catch (e) { msg(e.message, "err"); } })();
})();
