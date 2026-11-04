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

function render() {
  const has = (src, base) => src.files.some(f => !f.excluded && f.name.replace(/\.(xml|gnmap|nmap)$/i, "") === base);
  $("#cand").innerHTML = D.candidates.length ? D.candidates.map(c => `<option value="${esc(c.ip)}">${esc(c.ip)}${c.name ? " · " + esc(c.name) : ""}${c.zone ? " · " + esc(c.zone) : ""}</option>`).join("") : `<option value="">every inventory IP is already a Source</option>`;
  $("#zp").innerHTML = D.profiles.map(p => `<option>${esc(p.name)}</option>`).join("") || `<option value="">no Scan Profile yet</option>`;
  $("#zip").href = D.profiles.length && D.sources.length ? "/api/scripts.zip?profile=" + encodeURIComponent($("#zp").value) : "#";
  if (!D.sources.length) { $("#grid").innerHTML = `<tr><td class="muted" style="padding:16px">No Source yet: add one above (the IPs you will scan from).</td></tr>`; return; }
  $("#grid").innerHTML = `<tr><th>Source</th>${D.profiles.map(p => `<th title="expects ${esc(p.expected.join(", "))}">${esc(p.name)}</th>`).join("")}<th>Scans in the folder</th></tr>`
    + D.sources.map(s => `<tr data-src="${esc(s.ip)}"><td><b>${esc(s.ip)}</b>${s.name ? " · " + esc(s.name) : ""}<div class="small muted">${esc(s.zone)}${s.known ? "" : '<span style="color:#8a1a1a">not in the inventory: ignored by the report</span>'}</div></td>`
      + D.profiles.map(p => { const got = p.expected.filter(b => has(s, b)), done = p.expected.length && got.length === p.expected.length;
        const missing = p.expected.filter(b => !has(s, b)), label = done ? "✓" : got.length ? `${got.length}/${p.expected.length} · script` : "— script";
        if (window.SegDraft?.modified && window.SegDraft.name === p.name) return `<td class="${done ? "done" : "todo"}" title="${esc(p.name)} is modified above: save or discard the changes to download its script">${done ? "✓" : got.length ? `${got.length}/${p.expected.length}` : "—"} · <i>modified</i></td>`;
        return `<td class="${done ? "done" : "todo"}"><a href="/api/script?src=${encodeURIComponent(s.ip)}&profile=${encodeURIComponent(p.name)}" title="${done ? "done" : "missing: " + esc(missing.join(", "))} · click to download the script">${label}</a></td>`; }).join("")
      + `<td><div class="files">${s.files.map(f => `<div><span class="${f.excluded ? "ex" : ""}">${esc(f.name)}</span><button class="btn sm" data-src="${esc(s.ip)}" data-name="${esc(f.name)}" data-ex="${f.excluded ? "" : "1"}">${f.excluded ? "re-include" : "exclude"}</button></div>`).join("") || '<span class="muted">drop nmap files here</span>'}</div></td></tr>`).join("");
  $("#grid").querySelectorAll("button[data-name]").forEach(b => b.onclick = async () => {
    try { D = await api("/api/scans/move", {src: b.dataset.src, name: b.dataset.name, exclude: !!b.dataset.ex}); render(); toast(b.dataset.ex ? "Excluded: kept in excluded/, no longer read" : "Re-included"); }
    catch (e) { msg(e.message, "err"); }
  });
  $("#grid").querySelectorAll("tr[data-src]").forEach(tr => {
    tr.ondragover = e => { e.preventDefault(); tr.classList.add("drop"); };
    tr.ondragleave = () => tr.classList.remove("drop");
    tr.ondrop = async e => {
      e.preventDefault(); tr.classList.remove("drop");
      for (const f of e.dataTransfer.files) {
        try { D = await api(`/api/scans/upload?src=${encodeURIComponent(tr.dataset.src)}&name=${encodeURIComponent(f.name)}`, f, true); toast(`${f.name} stored for ${tr.dataset.src}`); msg(""); }
        catch (err) { msg(`${f.name}: ${err.message}`, "err"); }
      }
      render();
    };
  });
}
$("#adds").onclick = async () => { const ip = $("#cand").value; if (!ip) return; try { D = await api("/api/scans/source", {ip}); render(); toast(`Source ${ip} added: scans/${ip}/`); } catch (e) { msg(e.message, "err"); } };
$("#zp").onchange = render;
$("#zip").onclick = e => {
  if (window.SegDraft?.modified && window.SegDraft.name === $("#zp").value) { e.preventDefault(); toast(`${$("#zp").value} is modified above: save or discard the changes first`); return; }
  if ($("#zip").getAttribute("href") === "#") { e.preventDefault(); toast("Add a Source and a Scan Profile first"); }
};
window.addEventListener("draftchange", () => D && render());
window.addEventListener("profiles-saved", async () => { try { D = await api("/api/scans"); render(); } catch (e) { msg(e.message, "err"); } });
(async () => { try { D = await api("/api/scans"); render(); } catch (e) { msg(e.message, "err"); } })();
})();
