// SegOWL — shared by the Auditor Kit editors and the scan builder: port autocomplete, tag input with
// suggestions derived from the data, and the "new Port Label" form. One global, Ports, so the page scripts
// keep their own $ / esc / api.
"use strict";
const Ports = (() => {
  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
  async function api(path, body) {
    const opt = body === undefined ? {} : {method: "POST", headers: {"X-SegOWL": "1", "Content-Type": "application/json"}, body: JSON.stringify(body)};
    const r = await fetch(path, opt), j = await r.json().catch(() => ({error: r.statusText}));
    if (!r.ok) { const e = new Error(j.error || r.statusText); e.status = r.status; throw e; }
    return j;
  }
  const tokOk = t => { const m = String(t).trim().match(/^(?:(udp|tcp|sctp):)?(\d+)(?:-(\d+))?$/i); if (!m) return false; const a = +m[2], b = m[3] ? +m[3] : a; return a >= 1 && b <= 65535 && a <= b; };
  const toks = s => String(s ?? "").split(",").map(x => x.trim()).filter(Boolean);
  const normTags = s => [...new Set(toks(s).map(t => t.toLowerCase().replace(/\s+/g, "-")))].join(",");

  function dropdown(input, minWidth) {
    const drop = document.createElement("div"); drop.className = "tagdrop"; drop.hidden = true; document.body.appendChild(drop);
    drop.place = () => { const b = input.getBoundingClientRect(); drop.style.left = b.left + "px"; drop.style.top = b.bottom + 2 + "px"; drop.style.minWidth = Math.max(minWidth, b.width) + "px"; };
    return drop;
  }

  // ---------------------------------------------------------------- ports: server search (Port Labels, IANA) + local Port Groups
  const cache = {};
  async function suggest(tok, groups) {
    const t = tok.trim().toLowerCase(); if (!t) return [];
    if (t.startsWith("@")) return groups ? Object.entries(groups()).filter(([n]) => n.toLowerCase().startsWith(t.slice(1)))
      .map(([n, p]) => ({v: p, k: "@" + n, d: `insert its ${toks(p).length} ports (a copy, not a link)`, src: "Port Group"})) : [];
    cache[t] ??= api("/api/ports?q=" + encodeURIComponent(t)).catch(() => []);
    const seen = new Set(), out = (await cache[t]).filter(h => (h.src === "Port Label" || h.src === "IANA") && !seen.has(h.key + h.label) && seen.add(h.key + h.label))
      .map(h => ({v: h.key, k: h.key, d: h.label, src: h.src}));
    if (/^\d+$/.test(t) && tokOk(t) && !out.some(o => o.v === "udp:" + t)) out.push({v: "udp:" + t, k: "udp:" + t, d: "the same port over UDP", src: ""});
    return out.slice(0, 10);
  }
  // A comma-separated ports input (or a single port with single: true). groups: () => {name: ports} enables @group.
  function attachPorts(input, {groups = null, single = false, onCommit = () => {}, onCancel = () => {}} = {}) {
    const drop = dropdown(input, 320);
    let items = [], hl = -1, closed = false, seq = 0;
    const parts = () => input.value.split(","), tok = () => single ? input.value.trim() : parts().pop().trim();
    const expand = v => toks(v).flatMap(t => t.startsWith("@") && groups && groups()[t.slice(1)] !== undefined ? toks(groups()[t.slice(1)]) : [t]);
    function pick(o) {
      if (single) { input.value = o.v; drop.hidden = true; return; }
      input.value = [...parts().slice(0, -1).map(x => x.trim()).filter(Boolean), o.v].join(",") + ","; hl = -1; update(); input.focus();
    }
    function draw() {
      const t = tok();
      let h = items.map((o, i) => `<div data-i="${i}" class="${i === hl ? "hl" : ""}"><b style="min-width:70px">${esc(o.k)}</b><span>${esc(o.d)}</span><span class="c">${esc(o.src)}</span></div>`).join("");
      if (t && !t.startsWith("@") && !tokOk(t) && !items.length) h = `<div class="new">not a port: 22 · 8000-8100 · udp:161${groups ? " · @group" : ""}</div>`;
      if (!t && !single) h = `<div class="new">type a port, a product (winbox, veeam…), udp:…${groups ? " or @group" : ""} · <span class="kbd">,</span> next port</div>`;
      drop.innerHTML = h; drop.hidden = !h || document.activeElement !== input; drop.place();
    }
    async function update() { const n = ++seq, r = await suggest(tok(), groups); if (n !== seq || closed) return; items = r; hl = Math.min(hl, items.length - 1); draw(); }
    function finish() {
      if (single) { drop.hidden = true; return; }
      if (closed) return; closed = true; drop.remove(); onCommit([...new Set(expand(input.value.replace(/\s+/g, "")))].join(","));
    }
    drop.addEventListener("mousedown", e => { const d = e.target.closest("[data-i]"); if (d) { e.preventDefault(); pick(items[+d.dataset.i]); } });
    input.addEventListener("input", () => { hl = -1; update(); });
    input.addEventListener("focus", update);
    input.addEventListener("keydown", e => {
      if (e.key === "ArrowDown") { hl = Math.min(hl + 1, items.length - 1); draw(); e.preventDefault(); }
      else if (e.key === "ArrowUp") { hl = Math.max(hl - 1, -1); draw(); e.preventDefault(); }
      else if (e.key === "Enter" && hl >= 0 && !drop.hidden) { pick(items[hl]); e.preventDefault(); } // Enter on a typed port keeps it as typed
      else if (e.key === "Enter" || (e.key === "Tab" && !single)) { if (!single) e.preventDefault(); finish(); }
      else if (e.key === "Escape") { if (single && drop.hidden) return; e.preventDefault(); if (single) { drop.hidden = true; return; } closed = true; drop.remove(); onCancel(); }
    });
    input.addEventListener("blur", () => setTimeout(() => { if (document.activeElement !== input) finish(); }, 120));
    if (document.activeElement === input) update();
  }

  // ---------------------------------------------------------------- tags: suggestions from the tags in use, new tags kept as typed
  function lev(a, b) {
    const d = Array.from({length: a.length + 1}, (_, i) => [i, ...Array(b.length).fill(0)]); for (let j = 1; j <= b.length; j++) d[0][j] = j;
    for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    return d[a.length][b.length];
  }
  // the closest tag in use (case, plural, small edit distance), for "did you mean"
  const near = (t, vocab) => Object.keys(vocab).filter(v => v !== t).map(v => [v, v === t + "s" || t === v + "s" ? 0 : lev(t, v)]).filter(([, d]) => d <= 2).sort((a, b) => a[1] - b[1])[0]?.[0];
  // vocab: () => {tag: count}
  function attachTags(input, vocab, {onCommit = () => {}, onCancel = () => {}, keepOpen = false} = {}) {
    const drop = dropdown(input, 220);
    let items = [], hl = 0, closed = false;
    const tok = () => input.value.split(",").pop().trim().toLowerCase().replace(/\s+/g, "-");
    const done = () => input.value.split(",").slice(0, -1).map(t => t.trim()).filter(Boolean);
    function pick(t) { input.value = [...done(), t].join(",") + ","; update(); input.focus(); }
    function update() {
      const t = tok(), v = vocab(), have = new Set(done());
      items = Object.keys(v).filter(x => !have.has(x) && (!t || x.includes(t))).sort((a, b) => (b.startsWith(t) - a.startsWith(t)) || v[b] - v[a]).slice(0, 8);
      hl = Math.min(hl, Math.max(0, items.length - 1));
      let h = items.map((x, i) => `<div data-t="${esc(x)}" class="${i === hl ? "hl" : ""}">${esc(x)}<span class="c">${v[x]}</span></div>`).join("");
      if (t && !v[t]) { const n = near(t, v); h += `<div class="new">new tag «${esc(t)}» · Enter keeps it</div>` + (n ? `<div class="sug" data-t="${esc(n)}">did you mean <b>${esc(n)}</b>?</div>` : ""); }
      drop.innerHTML = h; drop.hidden = !h || document.activeElement !== input; drop.place();
    }
    function finish() { drop.hidden = true; if (keepOpen) { input.value = normTags(input.value); onCommit(input.value); return; } if (closed) return; closed = true; drop.remove(); onCommit(normTags(input.value)); }
    drop.addEventListener("mousedown", e => { const d = e.target.closest("[data-t]"); if (d) { e.preventDefault(); pick(d.dataset.t); } });
    input.addEventListener("input", () => { hl = 0; update(); });
    input.addEventListener("focus", update);
    input.addEventListener("keydown", e => {
      if (e.key === "ArrowDown") { hl = Math.min(hl + 1, items.length - 1); update(); e.preventDefault(); }
      else if (e.key === "ArrowUp") { hl = Math.max(hl - 1, 0); update(); e.preventDefault(); }
      else if (e.key === "Enter" && tok() && !vocab()[tok()]) { finish(); e.preventDefault(); } // a new tag: keep it as typed
      else if (e.key === "Enter" && items.length && tok()) { pick(items[hl]); e.preventDefault(); }
      else if (e.key === "Enter" || e.key === "Tab") { finish(); if (e.key === "Enter") e.preventDefault(); }
      else if (e.key === "Escape" && !drop.hidden) { e.preventDefault(); drop.hidden = true; if (!keepOpen) { closed = true; drop.remove(); onCancel(); } }
    });
    input.addEventListener("blur", () => setTimeout(() => { if (document.activeElement !== input) finish(); }, 120));
    if (document.activeElement === input) update();
  }

  // ---------------------------------------------------------------- the "new Port Label" form: Port Labels page and the scan builder's port search
  let LABELS = null; // {shipped, mission} from /api/labels, for the tag and vendor suggestions
  const vocabOf = L => { const c = {}; [...L.shipped, ...L.mission].forEach(r => toks(r[2]).forEach(t => c[t] = (c[t] || 0) + 1)); return c; };
  const vendorsOf = L => [...new Set([...L.shipped, ...L.mission].map(r => r[3]).filter(Boolean))].sort();
  // Opens the form in `box`; onAdded(labels) gets the server's new {fp, shipped, mission}.
  async function labelForm(box, {port = "", product = "", onAdded = () => {}, onCancel = () => {}} = {}) {
    LABELS = LABELS || await api("/api/labels");
    box.innerHTML = `<div class="addlbl" id="lf"><b style="grid-column:1/-1">New Port Label for this Mission</b>
      <label>port</label><input type="text" id="lf-port" value="${esc(port)}" placeholder="3389 or udp:161 · type a product to find its port" autocomplete="off">
      <label>product</label><input type="text" id="lf-prod" value="${esc(product)}" placeholder="e.g. MikroTik Winbox">
      <label>tags</label><input type="text" id="lf-tags" placeholder="admin, network…" autocomplete="off">
      <label>vendor</label><input type="text" id="lf-vendor" list="lf-vendors" placeholder="optional"><datalist id="lf-vendors">${vendorsOf(LABELS).map(v => `<option value="${esc(v)}">`).join("")}</datalist>
      <label>cleartext</label><div class="seg" id="lf-clear"><button type="button" data-c="yes">yes</button><button type="button" data-c="no">no</button><button type="button" data-c="" class="on">unknown</button></div>
      <div class="row"><span class="small" id="lf-msg" style="margin-right:auto;color:#8a1a1a"></span><span class="small muted">Saved in this Mission's port_labels.csv · <span class="kbd">Enter</span> add · <span class="kbd">Esc</span> cancel</span>
        <button type="button" class="btn sm" id="lf-no">Cancel</button><button type="button" class="btn sm pri" id="lf-ok">Add label</button></div></div>`;
    let clear = "";
    $("#lf-clear", box).onclick = e => { const b = e.target.closest("button"); if (!b) return; clear = b.dataset.c; $("#lf-clear", box).querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); };
    attachTags($("#lf-tags", box), () => vocabOf(LABELS), {keepOpen: true});
    attachPorts($("#lf-port", box), {single: true});
    const close = () => { box.innerHTML = ""; onCancel(); };
    async function ok() {
      const p = $("#lf-port", box).value.trim().replace(/\s+/g, ""), prod = $("#lf-prod", box).value.trim(), msg = $("#lf-msg", box);
      if (!tokOk(p)) { msg.textContent = "not a port: 22 · 8000-8100 · udp:161"; $("#lf-port", box).focus(); return; }
      if (!prod) { msg.textContent = "the product is required"; $("#lf-prod", box).focus(); return; }
      try {
        LABELS = await api("/api/labels/add", {label: [p, prod, normTags($("#lf-tags", box).value), $("#lf-vendor", box).value.trim(), clear]});
        box.innerHTML = ""; onAdded(LABELS);
      } catch (e) { msg.textContent = e.message; }
    }
    $("#lf-ok", box).onclick = ok; $("#lf-no", box).onclick = close;
    $("#lf", box).addEventListener("keydown", e => {
      if (e.defaultPrevented) return;
      if (e.key === "Escape") close();
      if (e.key === "Enter" && e.target.tagName === "INPUT") { e.preventDefault(); ok(); }
    });
    $(port ? "#lf-prod" : "#lf-port", box).focus();
  }
  return {esc, api, tokOk, toks, normTags, near, attachPorts, attachTags, labelForm, vocabOf, vendorsOf, setLabels: L => { LABELS = L; }};
})();
