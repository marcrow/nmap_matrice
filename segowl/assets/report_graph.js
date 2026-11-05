// Network diagrams (ADR-0005): Cytoscape.js with layouts written for SegOWL. render/html.py emits each diagram
// as JSON in a div.graph; it is drawn the first time it is shown, and again when the Port Group changes.
// Shape of a diagram: a centre (the Source) and the Zone frames around it, each Zone holding its Interfaces.
const FONT = '-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif', NAVY = '#0B1F33', SLATE = '#6B7C93', INK = '#1c2430';
const COL = {deny: '#dc2626', undeclared: '#f59e0b', allow: '#16a34a'}, GREY = '#94a3b8', REACH_COL = '#64748b';
const RANK = {deny: 3, undeclared: 2, allow: 1};
const ICON = {deny: ['✕', '#dc2626', '#fff'], undeclared: ['?', '#f59e0b', '#3b2600'], allow: ['✓', '#16a34a', '#fff']};
const WORD = {deny: 'Finding: denied by the Flow Policy', undeclared: 'undeclared', allow: 'allowed'};
const ARR = {auto: 'auto', c1: 'one column', c2: 'two columns', r1: 'one row', r2: 'two rows'};
const LAYOUTS = {sides: 'Zones facing the Source', lr: 'Zones on both sides', ring: 'Zones around the Source'};
const gesc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const gctx = document.createElement('canvas').getContext('2d');
const tw = (t, size, w = 400) => (gctx.font = `${w} ${size}px ${FONT}`, gctx.measureText(t).width);
const svgUri = (W, H, body) => 'data:image/svg+xml;utf8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W * 3}" height="${H * 3}" viewBox="0 0 ${W} ${H}" font-family="${FONT}">${body}</svg>`);

// Options, the same for every diagram, remembered per viewer (browser storage, best effort).
const ODEF = {lay: 'sides', edges: 'iface', ports: 'nodes', mcol: true, mtie: false, arr: 'auto', open: false};
const O = {...ODEF};
try { Object.assign(O, JSON.parse(localStorage.getItem('segowl.graph') || '{}')); } catch (e) { /* defaults */ }
const saveO = () => { try { localStorage.setItem('segowl.graph', JSON.stringify(O)); } catch (e) { /* not stored */ } };
const GRAPHS = [];  // every drawn diagram: {el, D, cy, arr, pin, side, hidden}

// The nodes around the centre, each with its links (flows to the centre; one implicit link to the Source when a
// node is a target of it). The Port Group filter (report.js groupSet) keeps only the group's OPEN flows. A node
// shows what its links carry: every open port (worst Flow Policy status per port) and the most open verdict.
const VORDER = ['ALIVE', 'REACHABLE', 'OPEN'];
function viewNodes(D) {
  const set = groupSet(), out = [];
  for (const t of D.nodes) {
    let links = t.links || [{to: 'S', verdict: t.verdict, ports: t.ports, cross: t.cross}];
    if (set) links = links.flatMap(l => { if (l.keep) return [l]; const ports = l.verdict === 'OPEN' ? l.ports.filter(p => inRanges(p.l, set)) : [];
      return ports.length ? [{...l, ports}] : []; });
    if (!links.length) continue;
    const by = {};
    links.forEach(l => l.ports.forEach(p => { if (!by[p.l] || (RANK[p.st] || 0) > (RANK[by[p.l].st] || 0)) by[p.l] = p; }));
    out.push({...t, links, ports: Object.values(by), cross: links.some(l => l.cross && l.verdict === 'OPEN'),
      verdict: links.map(l => l.verdict).reduce((a, b) => VORDER.indexOf(b) > VORDER.indexOf(a) ? b : a)});
  }
  return out;
}
// Flow Policy status of a node or link: its worst port; without a Flow Policy every cross-zone OPEN flow is undeclared.
const status = t => t.ports.reduce((w, p) => (RANK[p.st] || 0) > (RANK[w] || 0) ? p.st : w, null)
  || (t.cross && t.verdict === 'OPEN' ? 'undeclared' : null);
const edgeCol = t => t.col || (t.verdict !== 'OPEN' ? REACH_COL : COL[status(t)] || GREY);
const portsIn = () => O.edges === 'zone' || O.ports === 'nodes';

// Port tokens wrapped to maxW: admin bold, denied red. Returns lines of [{t, x, b, c}] and the widest line.
function wrapPorts(t, size, maxW) {
  const ps = t.ports.slice(0, 14), toks = ps.map((p, i) => ({t: p.l + (i < ps.length - 1 || t.ports.length > 14 ? ',' : ''), b: p.admin, c: p.st === 'deny' ? COL.deny : INK}));
  if (t.ports.length > 14) toks.push({t: `+${t.ports.length - 14}`, b: false, c: SLATE});
  const lines = []; let line = [], x = 0, wmax = 0;
  for (const k of toks) {
    const w = tw(k.t, size, k.b ? 700 : 400);
    if (line.length && x + 4 + w > maxW) { lines.push(line); line = []; x = 0; }
    const at = line.length ? x + 4 : 0; line.push({...k, x: at}); x = at + w; wmax = Math.max(wmax, x);
  }
  if (line.length) lines.push(line);
  return {lines, wmax};
}
const portText = (lines, x0, y0, size, lh) => lines.map((l, i) => l.map(k =>
  `<text x="${x0 + k.x}" y="${y0 + i * lh}" font-size="${size}" font-weight="${k.b ? 700 : 400}" fill="${k.c}">${gesc(k.t)}</text>`).join('')).join('');

// An Interface drawn as an SVG image (a Cytoscape label is plain text: no bold or red inside one label).
function card(t, mcol) {
  const P = 7, B = mcol ? 4 : 0, ic = status(t), name = t.name || t.ip, sub = t.sub ?? (t.name ? t.ip : '');
  const w1 = (ic ? 17 : 0) + tw(name, 12.5, 600);
  const pp = portsIn() && t.ports.length ? wrapPorts(t, 11.5, 170) : {lines: [], wmax: 0};
  const word = t.note || {REACHABLE: 'reachable', ALIVE: 'alive'}[t.verdict] || '';
  const W = Math.ceil(Math.max(w1, sub ? tw(sub, 10.5) : 0, pp.wmax, word ? tw(word, 11, 700) : 0)) + 2 * P + B;
  const H = P * 2 + 14 + (sub ? 13 : 0) + pp.lines.length * 14 + (word ? 14 : 0);
  const x = P + B; let y = P + 11, s = mcol ? `<rect width="${W}" height="${H}" fill="${mcol}" opacity=".07"/><rect width="${B}" height="${H}" fill="${mcol}"/>` : '';
  if (ic) { const [g, bg, fg] = ICON[ic];
    s += `<circle cx="${x + 6}" cy="${y - 4}" r="6" fill="${bg}"/><text x="${x + 6}" y="${y - 0.8}" font-size="9" font-weight="800" fill="${fg}" text-anchor="middle">${g}</text>`; }
  s += `<text x="${x + (ic ? 17 : 0)}" y="${y}" font-size="12.5" font-weight="600" fill="${NAVY}">${gesc(name)}</text>`;
  if (sub) { y += 13; s += `<text x="${x}" y="${y}" font-size="10.5" fill="${SLATE}">${gesc(sub)}</text>`; }
  if (pp.lines.length) { s += portText(pp.lines, x, y + 14, 11.5, 14); y += pp.lines.length * 14; }
  if (word) s += `<text x="${x}" y="${y + 14}" font-size="11" ${t.note ? 'font-weight="700"' : 'font-style="italic"'} fill="${t.noteCol || SLATE}">${gesc(word)}</text>`;
  return {w: W, h: H, img: svgUri(W, H, s)};
}
// Ports on the edge, just before the target ("ports on the edges"): a small tag, same marks as in the node.
function tag(t, maxW) {
  const pp = wrapPorts(t, 11, maxW), W = Math.ceil(pp.wmax) + 10, H = pp.lines.length * 13 + 6;
  return {w: W, h: H, img: svgUri(W, H, portText(pp.lines, 5, 13, 11, 13))};
}
function sourceCard(S) {
  const name = S.name || S.ip, W = Math.ceil(Math.max(tw(name, 14, 700), tw(`${S.ip} · ${S.zone}`, 11), 60)) + 30, H = 58;
  const s = `<rect width="4" height="${H}" fill="#00C8FF"/><text x="16" y="17" font-size="9" font-weight="700" letter-spacing="1.4" fill="#00C8FF">SOURCE</text>`
    + `<text x="16" y="34" font-size="14" font-weight="700" fill="#fff">${gesc(name)}</text><text x="16" y="49" font-size="11" fill="#9fb3c8">${gesc(S.ip)} · ${gesc(S.zone)}</text>`;
  return {w: W, h: H, img: svgUri(W, H, s)};
}

// The centre: the Source card, or a Machine as a frame holding its Interfaces (bordered with their Zone colour).
function centre(D) {
  if (!D.center.ifaces) return [{data: {id: 'S', ...sourceCard(D.center)}, classes: 'source'}];
  return [{data: {id: 'S', label: D.center.machine}, classes: 'mframe'}].concat(D.center.ifaces.map(i =>
    ({data: {id: 'i:' + i.ip, parent: 'S', ...card({name: i.name || i.ip, ip: `${i.ip} · ${i.zone}`, ports: [], verdict: ''}), bc: D.zones[i.zone][1]}, classes: 'iface'})));
}
const linkEnd = to => to === 'S' ? 'S' : 'i:' + to;

function elements(g) {
  const D = g.D, rows = viewNodes(D), tags = !portsIn(), dir = D.inward ? ' in' : '';
  const els = centre(D);
  const zones = [...new Set(rows.map(t => t.zone))].sort();
  for (const z of zones) { const [f, s, c] = D.zones[z];
    els.push({data: {id: 'z:' + z, name: z, label: `${z} · ${rows.filter(t => t.zone === z).length}`, fill: f, stroke: s, text: c}, classes: 'zone'}); }
  for (const t of rows) {
    const m = O.mcol && t.multi ? D.machines[t.machine] : null, c = card(t, m), col = edgeCol(t);
    els.push({data: {id: t.ip, parent: 'z:' + t.zone, t, ...c, bc: m || '#c3cfdc'}, classes: 'tgt'});
    if (O.edges === 'zone') continue;
    for (const l of t.links) els.push({data: {id: `e:${t.ip}>${l.to}`, source: linkEnd(l.to), target: t.ip, col: edgeCol(l), z: RANK[status(l)] || 0},
      classes: (l.verdict === 'OPEN' && !l.dash ? 'flow' : 'flow dash') + ((l.inward ?? D.inward) ? ' in' : '')});
    if (tags && t.ports.length) { const lr = tag(t, 150), tb = tag(t, Math.max(c.w - 10, 110));  // beside the node / over or under it
      els.push({data: {id: 'p:' + t.ip, of: t.ip, zone: t.zone, col, lr, tb, ...lr}, classes: 'tag'}); }
  }
  if (O.edges === 'zone') for (const z of zones) {  // one edge per Zone: its worst Flow Policy status; the nodes carry the detail
    const ts = rows.filter(t => t.zone === z), open = ts.filter(t => t.verdict === 'OPEN');
    const st = ['deny', 'undeclared', 'allow'].find(k => open.some(t => status(t) === k));
    els.push({data: {id: 'ez:' + z, source: 'S', target: 'z:' + z, col: !open.length ? REACH_COL : COL[st] || GREY, z: RANK[st] || 0},
      classes: (open.length ? 'flow zedge' : 'flow zedge dash') + dir});
  }
  const byM = {};
  rows.filter(t => t.multi).forEach(t => (byM[t.machine] = byM[t.machine] || []).push(t.ip));
  for (const ips of Object.values(byM)) ips.slice(1).forEach((ip, i) => els.push({data: {id: `tie:${ips[i]}:${ip}`, source: ips[i], target: ip}, classes: 'tie'}));
  return els;
}

const STYLE = [
  {selector: 'node.source', style: {shape: 'round-rectangle', 'corner-radius': 4, width: 'data(w)', height: 'data(h)', 'background-color': NAVY,
    'border-width': 0, 'background-image': 'data(img)', 'background-fit': 'contain'}},
  {selector: 'node.zone', style: {shape: 'round-rectangle', 'corner-radius': 4, 'background-color': 'data(fill)', 'background-opacity': 1,
    'border-color': 'data(stroke)', 'border-width': 2, label: 'data(label)', color: 'data(text)', 'font-weight': 700, 'font-size': 12.5,
    'text-valign': 'top', 'text-halign': 'center', 'text-margin-y': -5, padding: 12, 'font-family': FONT,
    'text-background-color': 'data(stroke)', 'text-background-opacity': 0.14, 'text-background-padding': 4, 'text-background-shape': 'round-rectangle'}},
  {selector: 'node.mframe', style: {shape: 'round-rectangle', 'corner-radius': 6, 'background-color': '#f4f7fb', 'border-color': NAVY,
    'border-width': 2, label: 'data(label)', color: NAVY, 'font-weight': 700, 'font-size': 13, 'text-valign': 'top', 'text-halign': 'center',
    'text-margin-y': -5, padding: 12, 'font-family': FONT}},
  {selector: 'node.iface', style: {shape: 'round-rectangle', 'corner-radius': 3, width: 'data(w)', height: 'data(h)', 'background-color': '#ffffff',
    'border-color': 'data(bc)', 'border-width': 2, 'background-image': 'data(img)', 'background-fit': 'contain'}},
  {selector: 'node.tgt', style: {shape: 'round-rectangle', 'corner-radius': 3, width: 'data(w)', height: 'data(h)', 'background-color': '#ffffff',
    'border-color': 'data(bc)', 'border-width': 1, 'background-image': 'data(img)', 'background-fit': 'contain'}},
  {selector: 'node.tag', style: {shape: 'round-rectangle', 'corner-radius': 3, width: 'data(w)', height: 'data(h)', 'background-color': '#ffffff',
    'border-color': 'data(col)', 'border-width': 1, 'background-image': 'data(img)', 'background-fit': 'contain', events: 'no', 'z-index': 20}},
  {selector: 'edge.flow', style: {width: 1.2, 'line-color': 'data(col)', 'target-arrow-color': 'data(col)', 'target-arrow-shape': 'triangle',
    'arrow-scale': 0.6, 'z-index': 'data(z)'}},
  {selector: 'edge.zedge', style: {width: 2.2, 'arrow-scale': 0.9}},
  {selector: 'edge.in', style: {'target-arrow-shape': 'none', 'source-arrow-shape': 'triangle', 'source-arrow-color': 'data(col)'}},
  {selector: 'edge.dash', style: {'line-style': 'dashed', 'line-dash-pattern': [5, 4]}},
  {selector: 'edge.tie', style: {'curve-style': 'straight', width: 1.2, 'line-color': GREY, 'line-style': 'dotted'}},
  {selector: 'node.sib', style: {'underlay-color': '#00C8FF', 'underlay-padding': 5, 'underlay-opacity': 0.35, 'underlay-shape': 'round-rectangle'}},
  {selector: 'edge.hl', style: {width: 2.6, 'z-index': 30}},
  {selector: '.off', style: {display: 'none'}},
];

// ---- layouts: each Zone is a block of lines, columns beside the Source, rows above or below it ----
// Auto (density rule): columns 1 up to 8 Interfaces, 2 up to 16, 3 beyond; rows 1 up to 6, 2 up to 12, 3 beyond;
// with the ports on the edges always 1. A Zone's own choice (right-click) or the panel's overrides it.
const PAD = 12, TITLE = 20, G = 36;
const arrOf = (g, z) => g.arr[z.data('name')] || O.arr;
function linesFor(g, z, n, cols) {
  const a = arrOf(g, z);
  if (a !== 'auto') return +a[1];
  return !portsIn() ? 1 : cols ? (n <= 8 ? 1 : n <= 16 ? 2 : 3) : n <= 6 ? 1 : n <= 12 ? 2 : 3;
}
// dir = where the Zone sits seen from the Source: R, L (nodes in columns) or T, B (nodes in rows).
function block(g, z, dir) {
  const cy = g.cy, tagW = k => { const t = cy.$id('p:' + k.id()); return t.nonempty() ? t.data('tb').w : 0; };  // a row leaves room for its tags
  const v = dir === 'R' || dir === 'L', al = k => v ? k.data('h') : Math.max(k.data('w'), tagW(k)), ac = k => v ? k.data('w') : k.data('h');
  const key = n => { const t = n.data('t'); return (t.multi ? '0' + t.machine : '1') + '|' + t.ip.split('.').map(x => x.padStart(3, '0')).join('.'); };
  const kids = z.children().sort((a, b) => key(a).localeCompare(key(b))), lines = Math.min(linesFor(g, z, kids.length, v), kids.length);
  const ga = v ? 16 : 12, gc = v ? 26 : 18, lw = Math.max(...kids.map(ac));
  // Staggered lines: every node in one virtual line, shared out (node i -> line i % lines), so an edge to the far
  // line passes between two nodes of the near one.
  let acc = 0; const a = [], end = Array(lines).fill(-1e9);
  kids.forEach((k, i) => { const s = al(k), l = i % lines; let c = (acc + s / 2) / lines; acc += s + ga;
    c = Math.max(c, end[l] + ga + s / 2); a.push(c); end[l] = c + s / 2; });
  const start = Math.min(...kids.map((k, i) => a[i] - al(k) / 2)), len = Math.max(...end) - start, wid = lines * lw + (lines - 1) * gc;
  const W = v ? wid : len, H = v ? len : wid;
  const place = (pos, fx, fy) => {  // (fx, fy) = top-left corner of the frame; a B frame carries its title underneath
    const x0 = fx + PAD, y0 = fy + (dir === 'B' ? 0 : TITLE) + PAD;
    kids.forEach((k, i) => { const off = (i % lines) * (lw + gc), w = k.data('w'), h = k.data('h'), t = a[i] - start;
      pos[k.id()] = dir === 'R' ? {x: x0 + off + w / 2, y: y0 + t} : dir === 'L' ? {x: x0 + W - off - w / 2, y: y0 + t}
        : dir === 'T' ? {x: x0 + t, y: y0 + H - off - h / 2} : {x: x0 + t, y: y0 + off + h / 2}; });
  };
  return {z, dir, FW: W + 2 * PAD, FH: H + 2 * PAD + TITLE, place};
}
const visibleZones = g => g.cy.nodes('.zone').filter(z => !z.hasClass('off'));
const tagRoom = (g, k, d) => { let w = 0; g.cy.nodes('.tag').forEach(t => { if (!t.hasClass('off')) w = Math.max(w, t.data(k)[d]); }); return w ? w + 14 : 0; };
const midOrder = (bs, size) => { const o = []; [...bs].sort((p, q) => size(q) - size(p) || p.z.id().localeCompare(q.z.id()))
  .forEach((b, i) => i % 2 ? o.push(b) : o.unshift(b)); return o; };  // biggest in the middle

// Every Zone frame faces the Source with one side: stacks right / left, rows above / below (beyond the stacks, so
// no edge crosses a frame). Tries every assignment of Zones to sides, keeps the one that fills the canvas best.
// A Zone arranged in columns only goes beside the Source, in rows only above / below; a pinned Zone keeps its side.
function around(g, dirs) {
  const zs = visibleZones(g), S = g.cy.$id('S'), box = g.cy.container().getBoundingClientRect();
  const allowed = zs.map(z => { const n = z.data('name'), a = arrOf(g, z);
    const pin = (g.pin && g.pin[n]) || (g.D.sides && g.D.sides[n]);  // pinned by a right-click, or by the diagram
    if (pin && dirs.includes(pin) && (a === 'auto' || (a[0] === 'c') === 'RL'.includes(pin))) return [pin];
    const ok = [...dirs].filter(d => a === 'auto' || (a[0] === 'c') === 'RL'.includes(d));
    return ok.length ? ok : [...dirs]; });
  const B = zs.map((z, i) => Object.fromEntries(allowed[i].map(d => [d, block(g, z, d)])));
  const tv = tagRoom(g, 'tb', 'h'), dx = S.data('w') / 2 + 56 + tagRoom(g, 'lr', 'w'), dy = S.data('h') / 2 + 56 + tv;
  const geo = asg => {
    const st = {R: [], L: [], T: [], B: []}, fr = [];
    asg.forEach((d, i) => st[d].push(B[i][d]));
    const h = d => st[d].reduce((s, b) => s + b.FH, 0) + G * Math.max(0, st[d].length - 1), hs = Math.max(h('R'), h('L')) / 2;
    for (const d of 'RL') { let y = -h(d) / 2; for (const b of midOrder(st[d], b => b.FH)) { fr.push([b, d === 'R' ? dx : -dx - b.FW, y]); y += b.FH + G; } }
    for (const d of 'TB') {
      const w = st[d].reduce((s, b) => s + b.FW, 0) + G * Math.max(0, st[d].length - 1), edge = Math.max(hs + G + tv, dy);
      let x = -w / 2; for (const b of midOrder(st[d], b => b.FW)) { fr.push([b, x, d === 'T' ? -edge - b.FH : edge]); x += b.FW + G; }
    }
    const xs = fr.flatMap(([b, x]) => [x, x + b.FW]).concat([-S.data('w') / 2, S.data('w') / 2]), ys = fr.flatMap(([b, , y]) => [y, y + b.FH]).concat([-dy, dy]);
    return {fr, zoom: Math.min(box.width / (Math.max(...xs) - Math.min(...xs)), box.height / (Math.max(...ys) - Math.min(...ys)))};
  };
  let best = null, n = allowed.reduce((p, a) => p * a.length, 1);  // ponytail: brute force, 4^Zones assignments, fine up to ~8 Zones
  for (let m = 0; m < n; m++) {
    let r = m; const asg = allowed.map(a => { const d = a[r % a.length]; r = Math.floor(r / a.length); return d; });
    const gm = geo(asg);
    if (!best || gm.zoom > best.zoom + 1e-6) best = gm;
  }
  const pos = {S: {x: 0, y: 0}}, side = {};
  for (const [b, x, y] of (best ? best.fr : [])) { b.place(pos, x, y); side[b.z.id()] = b.dir; }
  return {pos, side};
}
// Zone frames on an ellipse around the Source: the smallest ring without overlap that fills the canvas best.
function ring(g) {
  const bs = visibleZones(g).map(z => block(g, z, arrOf(g, z)[0] === 'r' ? 'T' : 'R')), S = g.cy.$id('S');
  const SW = S.data('w') + 60, SH = S.data('h') + 60, box = g.cy.container().getBoundingClientRect();
  const place = (R, st, a0) => { let acc = 0; const tot = bs.reduce((x, b) => x + b.FW + b.FH, 0);
    return bs.map(b => { const mid = a0 + (acc + (b.FW + b.FH) / 2) / tot * 2 * Math.PI; acc += b.FW + b.FH;
      return {x: R * st * Math.cos(mid), y: R * Math.sin(mid), W: b.FW + 30, H: b.FH + 30}; }); };
  const clash = (p, q) => Math.abs(p.x - q.x) * 2 < p.W + q.W && Math.abs(p.y - q.y) * 2 < p.H + q.H;
  const ok = c => c.every((p, i) => !clash(p, {x: 0, y: 0, W: SW, H: SH}) && c.every((q, j) => j <= i || !clash(p, q)));
  let best = null;  // ponytail: brute force over stretch x start angle, fine for <10 Zones
  for (const st of [1, 1.25, 1.5, 1.8]) for (let k = 0; k < 24; k++) {
    const a0 = -Math.PI + k * Math.PI / 12; let lo = 0, hi = 6000;
    if (!ok(place(hi, st, a0))) continue;
    for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; ok(place(m, st, a0)) ? hi = m : lo = m; }
    const c = place(hi, st, a0), xs = c.flatMap(p => [p.x - p.W / 2, p.x + p.W / 2, -SW / 2, SW / 2]), ys = c.flatMap(p => [p.y - p.H / 2, p.y + p.H / 2, -SH / 2, SH / 2]);
    const zoom = Math.min(box.width / (Math.max(...xs) - Math.min(...xs)), box.height / (Math.max(...ys) - Math.min(...ys)));
    if (!best || zoom > best.zoom + 1e-6) best = {zoom, c};
  }
  const pos = {S: {x: 0, y: 0}};
  if (best) bs.forEach((b, i) => { const p = best.c[i]; b.place(pos, p.x - b.FW / 2, p.y - b.FH / 2); });
  return {pos, side: {}};
}
const LAYOUT = {sides: g => around(g, 'RLTB'), lr: g => around(g, 'RL'), ring};

// Edge geometry once the positions are known: leave / enter by the facing sides, at right angles. Beside the
// Source the turn is near it (one trunk); above / below it, just outside the target frame. Ring: straight.
const END = {R: ['50% 0%', '-50% 0%'], L: ['-50% 0%', '50% 0%'], T: ['0% -50%', '0% 50%'], B: ['0% 50%', '0% -50%']};
function shapeEdges(g, side) {
  const cy = g.cy, box = {}, sb = cy.$id('S').boundingBox();  // read the bounds before the batch: inside it they are stale
  cy.nodes('.zone').forEach(z => { box[z.id()] = z.boundingBox(); });
  // Edges towards a Machine come from several Sources: each Source gets its own trunk, so they stay apart.
  const lane = {};
  if (g.D.inward) for (const d of 'RLTB') cy.nodes('.tgt').filter(n => side[n.parent().id()] === d)
    .sort((a, b) => 'RL'.includes(d) ? a.position('y') - b.position('y') : a.position('x') - b.position('x')).forEach((n, i) => { lane[n.id()] = i * 10; });
  cy.batch(() => {
    cy.nodes('.zone').forEach(z => z.style(side[z.id()] === 'B' ? {'text-valign': 'bottom', 'text-margin-y': 5} : {'text-valign': 'top', 'text-margin-y': -5}));
    cy.edges('.flow').forEach(e => {
      const t = e.target(), z = t.hasClass('zone') ? t : t.parent(), d = side[z.id()] || '';
      e.data('side', d);
      const st = d ? {'source-endpoint': END[d][0], 'target-endpoint': END[d][1]} : {'source-endpoint': 'outside-to-node', 'target-endpoint': 'outside-to-node'};
      if (d) {
        const bb = box[z.id()], v = d === 'T' || d === 'B', p = e.source().position();  // with node-position, the turn counts from the centre end
        const hang = v ? Math.max(0, ...cy.nodes('.tag').filter(k => k.data('zone') === z.data('name')).map(k => k.data('tb').h + 7 - PAD)) : 0;
        const k = lane[e.target().id()] || 0;
        const turn = d === 'R' ? sb.x2 - p.x + 28 + k : d === 'L' ? p.x - sb.x1 + 28 + k : d === 'T' ? p.y - bb.y2 - 14 - hang - k : bb.y1 - p.y - 14 - hang - k;
        Object.assign(st, {'curve-style': 'round-taxi', 'edge-distances': 'node-position', 'taxi-direction': v ? 'vertical' : 'horizontal',
          'taxi-turn': turn, 'taxi-turn-min-distance': 4, 'taxi-radius': 6});
      } else st['curve-style'] = 'straight';
      e.style(st);
    });
  });
}
// Port tags sit on their edge, just before the target, on the side the edge comes in.
function placeTags(g) {
  const cy = g.cy, Sn = cy.$id('S'), S = Sn.position(), U = {R: [-1, 0], L: [1, 0], T: [0, 1], B: [0, -1]};
  cy.batch(() => cy.nodes('.tag').forEach(k => {
    const n = cy.$id(k.data('of')), d = n.connectedEdges('.flow').data('side'), p = n.position(), w = n.width() / 2, h = n.height() / 2;
    k.data(d === 'T' || d === 'B' ? k.data('tb') : k.data('lr'));
    let u;
    if (d) u = {x: U[d][0], y: U[d][1]};
    else { const dx = S.x - p.x, dy = S.y - p.y, m = Math.hypot(dx, dy) || 1; u = {x: dx / m, y: dy / m}; }
    const ext = (a, b) => Math.min(Math.abs(u.x) > 1e-6 ? a / Math.abs(u.x) : 1e9, Math.abs(u.y) > 1e-6 ? b / Math.abs(u.y) : 1e9);
    k.position({x: p.x + u.x * (ext(w, h) + 7 + ext(k.width() / 2, k.height() / 2)), y: p.y + u.y * (ext(w, h) + 7 + ext(k.width() / 2, k.height() / 2))});
  }));
}
// A Machine centre: its Interfaces in one column (edges leave them sideways, so the Zones go beside it).
function stackCentre(g) {
  const S = g.cy.$id('S'), kids = S.children(), pos = {};
  if (!kids.nonempty()) return pos;
  const H = kids.reduce((h, k) => h + k.data('h'), 0) + 12 * (kids.length - 1), W = Math.max(...kids.map(k => k.data('w')));
  let y = -H / 2 + TITLE / 2;
  kids.forEach(k => { pos[k.id()] = {x: 0, y: y + k.data('h') / 2}; y += k.data('h') + 12; });
  S.data({w: W + 2 * PAD, h: H + 2 * PAD + TITLE});
  return pos;
}
function runLayout(g) {
  const inner = stackCentre(g), lay = g.D.center.ifaces && O.lay === 'sides' ? 'lr' : O.lay;
  const {pos, side} = (LAYOUT[lay] || LAYOUT.sides)(g);
  Object.assign(pos, inner);
  if (g.D.center.ifaces) delete pos.S;  // a frame's position follows its Interfaces
  g.side = Object.fromEntries(Object.entries(side).map(([id, d]) => [id.slice(2), d]));
  g.cy.elements().not('.tie, .tag, .off').layout({name: 'preset', positions: n => pos[n.id()], fit: false}).run();
  shapeEdges(g, side); placeTags(g);
  g.cy.fit(g.cy.elements(':visible'), 24);
  if (g.cy.zoom() > 1.1) { g.cy.zoom(1.1); g.cy.center(g.cy.elements(':visible')); }  // a small diagram is not blown up
}

function hideZone(g, z, off) {
  const zn = g.cy.$id('z:' + z);
  zn.union(zn.children()).union(g.cy.nodes('.tag').filter(k => k.data('zone') === z)).union(g.cy.$id('ez:' + z)).toggleClass('off', off);
}
function drawGraph(g) {
  g.cy.elements().remove();
  g.cy.add(elements(g));
  const zones = g.cy.nodes('.zone').map(z => z.data('name'));
  zones.forEach(z => hideZone(g, z, g.hidden.has(z)));
  g.el.querySelector('.gzones').innerHTML = zones.length ? '<b>Zones</b>' + zones.map(z => { const [f, s] = g.D.zones[z];
    return `<label class="chk"><input type="checkbox" value="${gesc(z)}"${g.hidden.has(z) ? '' : ' checked'}><i class="sw" style="background:${f};border-color:${s}"></i>${gesc(z)}</label>`; }).join('')
    : '<span class="muted">Nothing reached' + (groupSet() ? ' on this Port Group.' : '.') + '</span>';
  g.cy.edges('.tie').toggleClass('off', !O.mtie);
  runLayout(g);
  g.dirty = false;
}

// Toolbar and options panel of a diagram (built here: one code path for every diagram).
function controls(g) {
  const radio = (name, v, label) => `<label><input type="radio" name="${name}" value="${v}"${O[name] === v ? ' checked' : ''}>${label}</label>`;
  const box = (name, label) => `<label><input type="checkbox" name="${name}"${O[name] ? ' checked' : ''}>${label}</label>`;
  g.el.insertAdjacentHTML('afterbegin',
    `<div class="gbar"><div class="gzones"></div><span class="gact"><label class="pick">Layout <select class="glay">${
      Object.entries(LAYOUTS).map(([k, l]) => `<option value="${k}"${O.lay === k ? ' selected' : ''}>${l}</option>`).join('')}</select></label>`
    + '<button class="btn greset">Reset layout</button><button class="btn gpng">Export PNG</button></span></div>'
    + `<details class="gopts"${O.open ? ' open' : ''}><summary>Options</summary><div class="ggroups">`
    + `<fieldset><legend>Edges</legend>${radio('edges', 'iface', 'one per Interface')}${radio('edges', 'zone', 'one per Zone')}</fieldset>`
    + `<fieldset><legend>Ports</legend>${radio('ports', 'nodes', 'in the nodes')}${radio('ports', 'edges', 'on the edges')}</fieldset>`
    + `<fieldset><legend>Zone arrangement</legend><select name="arr">${Object.entries(ARR).map(([k, l]) => `<option value="${k}"${O.arr === k ? ' selected' : ''}>${l}</option>`).join('')}</select>`
    + '<div class="hint">Auto: beside the Source 1 column up to 8 Interfaces, 2 up to 16, 3 beyond; above or below it 1 row up to 6, '
    + '2 up to 12, 3 beyond; ports on the edges, 1. Right-click a Zone to arrange it alone.</div></fieldset>'
    + `<fieldset><legend>Machine</legend>${box('mcol', 'colour bar')}${box('mtie', 'dotted link')}`
    + '<div class="hint">Hover an Interface: the other Interfaces of its Machine are ringed.</div></fieldset></div></details>');
  const q = s => g.el.querySelector(s), redrawAll = () => { saveO(); GRAPHS.forEach(x => { x.dirty = true; }); drawVisibleGraphs(document); };
  q('.glay').onchange = e => { O.lay = e.target.value; g.pin = null; redrawAll(); GRAPHS.forEach(x => { x.el.querySelector('.glay').value = O.lay; }); };
  q('.greset').onclick = () => { g.arr = {}; g.pin = null; runLayout(g); };
  q('.gpng').onclick = () => { const a = document.createElement('a');
    a.href = URL.createObjectURL(g.cy.png({full: true, scale: 2, bg: '#ffffff', output: 'blob'})); a.download = g.D.file + '.png'; a.click(); };
  q('.gopts').ontoggle = e => { O.open = e.target.open; saveO(); };
  q('.ggroups').onchange = e => { const i = e.target; O[i.name] = i.type === 'checkbox' ? i.checked : i.value;
    if (i.name === 'arr') { g.arr = {}; g.pin = null; }
    if (i.name === 'mtie') { saveO(); GRAPHS.forEach(x => x.cy && x.cy.edges('.tie').toggleClass('off', !O.mtie)); } else redrawAll(); };
  q('.gzones').onchange = e => { const z = e.target.value; e.target.checked ? g.hidden.delete(z) : g.hidden.add(z); hideZone(g, z, !e.target.checked); runLayout(g); };
}

// Right-click on a Zone frame: arrange that Zone alone; the other Zones keep their side.
function zoneMenu(g, z, ev) {
  document.querySelectorAll('.gmenu').forEach(m => m.remove());
  const m = document.createElement('div'), r = g.cy.container().getBoundingClientRect(), p = ev.renderedPosition;
  m.className = 'gmenu'; m.style.left = (r.left + window.scrollX + p.x) + 'px'; m.style.top = (r.top + window.scrollY + p.y) + 'px';
  m.innerHTML = `<b>${gesc(z)}</b>` + Object.entries(ARR).map(([k, l]) => `<button data-a="${k}"${arrOf(g, g.cy.$id('z:' + z)) === k ? ' class="on"' : ''}>${l}</button>`).join('');
  m.onclick = e => { const a = e.target.dataset.a; if (!a) return;
    g.pin = {...g.side}; delete g.pin[z]; g.arr[z] = a; m.remove(); runLayout(g); };
  document.body.appendChild(m);
  setTimeout(() => document.addEventListener('click', () => m.remove(), {once: true}));
}

function showTip(g, t, ev) {
  const tip = g.el.querySelector('.gtip'), st = status(t);
  if (t.tip) { tip.innerHTML = t.tip; } else {
  const pol = st ? `<i class="pg pg-${st}">${ICON[st][0]}</i>${WORD[st]}` : '<span class="k">no Flow Policy status</span>';
  const ports = t.ports.map(p => `<span style="${p.admin ? 'font-weight:700;' : ''}${p.st === 'deny' ? 'color:#dc2626' : ''}">${gesc(p.l)}</span>`).join(', ');
  const sib = g.cy.nodes('.tgt').filter(n => n.data('t').machine === t.machine).length;
  tip.innerHTML = `<h4>${gesc(t.name || t.ip)} · ${gesc(t.ip)}</h4><div><span class="k">Zone</span> ${gesc(t.zone)} · <span class="k">type</span> ${gesc(t.type)}</div>`
    + (t.multi ? `<div><span class="k">Machine</span> ${gesc(t.machine)}, ${sib} of its Interfaces here</div>` : '')
    + `<div><span class="k">verdict</span> <b>${t.verdict}</b></div>` + (t.ports.length ? `<div><span class="k">open ports</span> ${ports}</div>` : '')
    + `<div><span class="k">Flow Policy</span> ${pol}</div>`; }
  const r = g.cy.container().getBoundingClientRect(), {x, y} = ev.renderedPosition || ev.target.renderedPosition();
  tip.style.display = 'block'; tip.style.left = Math.min(x + 16, r.width - 350) + 'px'; tip.style.top = (y + 16) + 'px';
}

function initGraph(el) {
  const g = {el, D: JSON.parse(el.querySelector('script').textContent), arr: {}, pin: null, side: {}, hidden: new Set(), dirty: true};
  controls(g);
  el.insertAdjacentHTML('beforeend', '<div class="gwrap"><div class="gcy"></div><div class="gtip"></div></div>');
  g.cy = cytoscape({container: el.querySelector('.gcy'), style: STYLE, wheelSensitivity: 0.3, minZoom: 0.15, maxZoom: 4});
  const cy = g.cy, hide = () => { el.querySelector('.gtip').style.display = 'none'; };
  cy.on('drag', 'node', () => { placeTags(g); hide(); });
  cy.on('cxttap', 'node.zone', ev => zoneMenu(g, ev.target.data('name'), ev));
  cy.on('mouseover', 'node.tgt', ev => { const t = ev.target.data('t');
    if (t.multi) cy.nodes('.tgt').filter(n => n.data('t').machine === t.machine).addClass('sib');
    ev.target.connectedEdges('.flow').addClass('hl'); showTip(g, t, ev); });
  cy.on('mouseover', 'edge.flow', ev => { if (ev.target.target().hasClass('tgt')) { ev.target.addClass('hl'); showTip(g, ev.target.target().data('t'), ev); } });
  cy.on('mouseout', 'node, edge', () => { cy.elements().removeClass('sib hl'); hide(); });
  GRAPHS.push(g);
  el.graph = g;
  return g;
}
// Draws the diagrams of scope that are visible and not drawn yet (or changed since); Cytoscape needs a sized box.
function drawVisibleGraphs(scope) {
  if (typeof cytoscape === 'undefined') return;
  scope.querySelectorAll('.graph').forEach(el => {
    if (el.offsetParent === null) return;
    const g = el.graph || initGraph(el);
    if (g.dirty) drawGraph(g);
  });
}
// Port Group changed: every diagram is redrawn when next shown.
function graphsChanged() { GRAPHS.forEach(g => { g.dirty = true; }); }
