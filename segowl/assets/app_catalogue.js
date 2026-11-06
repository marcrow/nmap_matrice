// SegOWL — Auditor Kit › Scan Profiles: the kit's catalogue (app-navigation 06). Building a scan is on /scans.
"use strict";

let D = null, descEdit = null, delRow = null;
const EXP = new Set();
const uniq = base => { let n = base, k = 2; while (D.profiles.some(p => p.name === n)) n = `${base}-${k++}`; return n; };
const portChips = (v, id) => Ports.portChips(v, id, EXP);
async function save(list, msg) {
  status("Saving…");
  try { await api("/api/profiles", {fp: D.fp, profiles: list}); D = await api("/api/profiles"); status("Saved ✓", "ok"); toast(msg); }
  catch (e) { status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err"); }
  draw();
}
function draw() {
  const q = $("#pq").value.trim().toLowerCase();
  $("#pt").innerHTML = `<tr><th>profile</th><th style="width:34%">what it is for</th><th>ports</th><th>options</th><th>Scans</th><th></th></tr>`
    + D.profiles.map((p, i) => [p, i]).filter(([p]) => !q || [p.name, p.description, p.options, p.ports].join(" ").toLowerCase().includes(q)).map(([p, i]) => `<tr>
      <td><b>${esc(p.name)}</b></td>
      <td class="pdesc" data-desc="${i}">${descEdit === i ? `<textarea id="dedit" rows="3" style="width:100%">${esc(p.description)}</textarea><div class="small muted">Enter save · Esc cancel</div>` : p.description ? esc(p.description) : `<span class="muted">+ say what this profile is for</span>`}</td>
      <td>${portChips(p.ports, "p" + i)}</td><td><code class="small">${esc(p.options)}</code></td>
      <td class="small">${p.imported ? `${p.imported} Source(s)` : `<span class="muted">none yet</span>`}</td>
      <td style="white-space:nowrap">${delRow === i ? `<span class="small">Delete ${esc(p.name)}?${p.imported ? " Its Scans stay." : ""} </span><button class="btn sm pri" data-pa="delok" data-i="${i}">Delete</button> <button class="btn sm" data-pa="delno">Cancel</button>`
        : `<a class="btn sm pri" href="/scans?profile=${encodeURIComponent(p.name)}">Open in Scans</a> <button class="btn sm" data-pa="dup" data-i="${i}">Duplicate</button> <button class="btn sm" data-pa="del" data-i="${i}">Delete</button>`}</td></tr>`).join("")
    + (D.profiles.length ? "" : `<tr><td colspan="6" class="muted" style="padding:16px">No Scan Profile yet: <a href="/scans?new=1">build one</a>, or apply a kit (Auditor Kit › Kits).</td></tr>`);
  const d = $("#dedit"); if (!d) return;
  d.focus(); d.setSelectionRange(d.value.length, d.value.length);
  d.onkeydown = e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); const i = descEdit; descEdit = null; save(D.profiles.map((p, k) => k === i ? {...p, description: d.value.trim()} : p), "Description saved"); }
    if (e.key === "Escape") { descEdit = null; draw(); }
  };
}
$("#pt").onclick = e => {
  const more = e.target.closest("[data-more]"); if (more) { const id = more.dataset.more; EXP.has(id) ? EXP.delete(id) : EXP.add(id); draw(); return; }
  const dc = e.target.closest("[data-desc]"); if (dc && descEdit === null) { descEdit = +dc.dataset.desc; draw(); return; }
  const b = e.target.closest("[data-pa]"); if (!b) return; const i = +b.dataset.i, a = b.dataset.pa;
  if (a === "dup") { const p = D.profiles[i], n = uniq(p.name + "-copy"); return save([...D.profiles.slice(0, i + 1), {...p, name: n}, ...D.profiles.slice(i + 1)], `Duplicated ${p.name} as ${n}`); }
  if (a === "del") delRow = i; if (a === "delno") delRow = null;
  if (a === "delok") { const n = D.profiles[i].name; delRow = null; return save(D.profiles.filter((_, k) => k !== i), `${n} deleted`); }
  draw();
};
$("#pq").oninput = draw;
(async () => { try { D = await api("/api/profiles"); status("Loaded", "ok"); draw(); } catch (e) { status("Cannot load: " + e.message, "err"); } })();
