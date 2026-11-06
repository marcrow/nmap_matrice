// Network diagrams (ADR-0005): Cytoscape.js with layouts written for SegOWL. render/html.py emits each diagram
// as JSON in a div.graph; it is drawn the first time it is shown, and again when the Port Group changes.
// Shape of a diagram: a centre (the Source) and the Zone frames around it, each Zone holding its Interfaces.
const FONT = '-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif', NAVY = '#0B1F33', SLATE = '#6B7C93', INK = '#1c2430';
const COL = {deny: '#dc2626', undeclared: '#f59e0b', allow: '#16a34a'}, GREY = '#94a3b8', REACH_COL = '#64748b';
const RANK = {deny: 3, undeclared: 2, allow: 1};
const ICON = {deny: ['✕', '#dc2626', '#fff'], undeclared: ['?', '#f59e0b', '#3b2600'], allow: ['✓', '#16a34a', '#fff']};
const WORD = {deny: 'Finding: denied by the Flow Policy', undeclared: 'undeclared', allow: 'allowed'};
const ARR = {auto: 'auto', c1: 'one column', c2: 'two columns', r1: 'one row', r2: 'two rows', sq: 'square', ci: 'circle', arc: 'half moon'};
const FREE = ['auto', 'sq', 'ci', 'arc'];  // arrangements that fit beside the Source as well as above or below it
// Snap-layout style icons of the right-click menu (34 x 24).
const SR = (x, y, w, h) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="1.5"/>`;
const ARR_ICON = {auto: SR(3, 3, 28, 18) + '<text x="17" y="15.5" font-size="8" font-weight="700" text-anchor="middle" stroke="none">auto</text>',
  c1: SR(13, 3, 8, 18), c2: SR(8, 3, 8, 18) + SR(18, 3, 8, 18), r1: SR(3, 8, 28, 8), r2: SR(3, 4, 28, 7) + SR(3, 13, 28, 7),
  sq: SR(9, 3, 7, 7) + SR(18, 3, 7, 7) + SR(9, 13, 7, 7) + SR(18, 13, 7, 7), ci: '<circle cx="17" cy="12" r="9"/>',
  arc: '<path d="M11 3a12 9 0 0 1 0 18" fill="none" stroke-width="5" stroke-linecap="round"/>', col: SR(13, 3, 8, 18), row: SR(3, 8, 28, 8)};
const MARR = {col: 'one column', row: 'one row'};  // a Machine in the centre
const LAYOUTS = {sides: 'Zones facing the Source', lr: 'Zones on both sides', ring: 'Zones around the Source'};
const SRC = '<rect x="13.5" y="9.5" width="7" height="5" rx="1" class="src"/>';
const LAY_ICON = {sides: SR(11, 1.5, 12, 5) + SR(11, 17.5, 12, 5) + SR(2, 7, 7, 10) + SR(25, 7, 7, 10) + SRC,
  lr: SR(2, 3, 8, 18) + SR(24, 3, 8, 18) + SRC,
  ring: [0, 60, 120, 180, 240, 300].map(d => SR(15 + 12 * Math.cos(d * Math.PI / 180), 10 + 8.5 * Math.sin(d * Math.PI / 180), 4, 4)).join('') + SRC};
// Icon tiles (snap-layout style): one per choice, the current one marked; data-k names the option.
const tiles = (k, choices, icons, cur) => `<div class="gsnap" data-k="${k}">` + Object.entries(choices).map(([v, l]) =>
  `<button type="button" data-v="${v}" title="${l}"${cur === v ? ' class="on"' : ''}><svg viewBox="0 0 34 24" width="34" height="24">${icons[v]}</svg><span>${l}</span></button>`).join('') + '</div>';
const gesc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const gctx = document.createElement('canvas').getContext('2d');
const tw = (t, size, w = 400) => (gctx.font = `${w} ${size}px ${FONT}`, gctx.measureText(t).width);
const svgUri = (W, H, body) => 'data:image/svg+xml;utf8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W * 3}" height="${H * 3}" viewBox="0 0 ${W} ${H}" font-family="${FONT}">${body}</svg>`);

// Options, the same for every diagram, remembered per viewer (browser storage, best effort).
const ODEF = {lay: 'sides', edges: 'iface', ports: 'nodes', mcol: true, mtie: false, arr: 'auto', open: false};
const O = {...ODEF};
try { Object.assign(O, JSON.parse(localStorage.getItem('segowl.graph') || '{}'), {arr: 'auto'}); } catch (e) { /* defaults */ }
// The Zone arrangement is not remembered: every load starts on auto.
const saveO = () => { try { localStorage.setItem('segowl.graph', JSON.stringify({...O, arr: undefined})); } catch (e) { /* not stored */ } };
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
// A card listing who reaches one Interface (Pivot Machines, "Reached from"): per Source Zone its Flow Policy
// icon, its name in the Zone's tone, and the ports it reaches (admin bold, denied red).
function rowsCard(t) {
  const P = 7, X = P + 17, rows = t.links.map(l => ({l, st: status(l), pp: wrapPorts(l, 11.5, 150)}));
  const NW = Math.max(...rows.map(r => tw(r.l.from, 12, 700))) + 8;  // the ports line up in a column
  const W = Math.ceil(X + NW + Math.max(0, ...rows.map(r => r.pp.wmax))) + P;
  let y = P, s = '';
  for (const r of rows) {
    y += 11;
    if (r.st) { const [g, bg, fg] = ICON[r.st];
      s += `<circle cx="${P + 6}" cy="${y - 4}" r="6" fill="${bg}"/><text x="${P + 6}" y="${y - 0.8}" font-size="9" font-weight="800" fill="${fg}" text-anchor="middle">${g}</text>`; }
    s += `<text x="${X}" y="${y}" font-size="12" font-weight="700" fill="${r.l.fc || NAVY}">${gesc(r.l.from)}</text>`;
    s += portText(r.pp.lines, X + NW, y, 11.5, 14); y += Math.max(0, r.pp.lines.length - 1) * 14 + 6;
  }
  const H = y + P - 2;
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
// Links merged per centre end (one edge each): every port, the most open verdict.
function oneEach(links) {
  const by = {};
  links.forEach(l => { const m = by[l.to];
    by[l.to] = !m ? l : {...m, ports: m.ports.concat(l.ports), cross: m.cross || l.cross,
      verdict: VORDER.indexOf(l.verdict) > VORDER.indexOf(m.verdict) ? l.verdict : m.verdict}; });
  return Object.values(by);
}

function elements(g) {
  const D = g.D, rows = viewNodes(D), tags = !portsIn();
  const els = centre(D), at = {};
  // A Machine in the centre: each node sorts by the mean rank of the Interfaces it links to, so fewer edges cross.
  (D.center.ifaces || []).forEach((i, k) => { at[i.ip] = k; });
  if (D.center.ifaces) at.S = (D.center.ifaces.length - 1) / 2;  // a link to the Machine itself: its middle
  if (D.center.ifaces) rows.forEach(t => { const ks = t.links.map(l => at[l.to]).filter(k => k !== undefined);
    t.ord = ks.length ? ks.reduce((a, b) => a + b, 0) / ks.length : 0; });
  const sideRank = z => ({L: 0, T: 0, R: 1, B: 1}[(D.sides || {})[z]] || 0);  // pinned sides read left to right
  const zones = [...new Set(rows.map(t => t.zone))].sort((a, b) => sideRank(a) - sideRank(b) || a.localeCompare(b));
  for (const z of zones) { const [f, s, c] = D.zones[z];
    els.push({data: {id: 'z:' + z, name: z, label: `${z} · ${rows.filter(t => t.zone === z).length}`, fill: f, stroke: s, text: c}, classes: 'zone'}); }
  for (const t of rows) {
    const m = O.mcol && t.multi ? D.machines[t.machine] : null, c = t.rows ? rowsCard(t) : card(t, t.bar || m), col = edgeCol(t);
    els.push({data: {id: t.ip, parent: 'z:' + t.zone, t, ...c, bc: m || '#c3cfdc'}, classes: 'tgt'});
    if (O.edges === 'zone') continue;
    for (const l of oneEach(t.links)) els.push({data: {id: `e:${t.ip}>${l.to}`, source: linkEnd(l.to), target: t.ip, col: edgeCol(l), z: RANK[status(l)] || 0, label: l.label || ''},
      classes: (l.verdict === 'OPEN' && !l.dash ? 'flow' : 'flow dash') + ((l.inward ?? D.inward) ? ' in' : '') + (l.kind ? ' k-' + l.kind : '') + (l.label ? ' lab' : '')});
    if (tags && t.ports.length && !t.rows) {  // a rows card keeps its ports (they differ per Source Zone)
      const lr = tag(t, 100), tb = tag(t, Math.max(c.w - 10, 110));  // beside the node / over or under it
      els.push({data: {id: 'p:' + t.ip, of: t.ip, zone: t.zone, col, lr, tb, ...lr}, classes: 'tag'}); }
  }
  // One edge per Zone (per Zone and Interface around a Machine): its worst Flow Policy status; the nodes carry the detail.
  if (O.edges === 'zone') for (const z of zones) for (const l of oneEach(rows.filter(t => t.zone === z).flatMap(t => t.links))) {
    const st = status(l), open = l.verdict === 'OPEN';
    els.push({data: {id: `ez:${z}>${l.to}`, zone: z, source: linkEnd(l.to), target: 'z:' + z, col: l.col || (!open ? REACH_COL : COL[st] || GREY), z: RANK[st] || 0},
      classes: (open && !l.dash ? 'flow zedge' : 'flow zedge dash') + ((l.inward ?? D.inward) ? ' in' : '')});
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
  {selector: 'edge.lab', style: {label: 'data(label)', 'font-size': 11, 'font-weight': 700, color: '#7a4a00', 'font-family': FONT,
    'text-background-color': '#fff', 'text-background-opacity': 1, 'text-background-padding': 2, 'text-background-shape': 'round-rectangle'}},
  {selector: 'edge.k-gain', style: {width: 2}},
  {selector: 'edge.k-bypass', style: {width: 3.4, 'arrow-scale': 0.8}},
  {selector: 'edge.k-none', style: {width: 1, 'line-style': 'dotted'}},
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
  if (a === 'sq' || a === 'ci') return Math.ceil(Math.sqrt(n));
  if (a !== 'auto') return +a[1];
  return !portsIn() ? 1 : cols ? (n <= 8 ? 1 : n <= 16 ? 2 : 3) : n <= 6 ? 1 : n <= 12 ? 2 : 3;
}
// dir = where the Zone sits seen from the Source: R, L (nodes in columns) or T, B (nodes in rows).
function block(g, z, dir) {
  const cy = g.cy, tagW = k => { const t = cy.$id('p:' + k.id()); return t.nonempty() ? t.data('tb').w : 0; };  // a row leaves room for its tags
  const v = dir === 'R' || dir === 'L', al = k => v ? k.data('h') : Math.max(k.data('w'), tagW(k)), ac = k => v ? k.data('w') : k.data('h');
  const key = n => { const t = n.data('t'); return (t.multi ? '0' + t.machine : '1') + '|' + t.ip.split('.').map(x => x.padStart(3, '0')).join('.'); };
  const cmp = (a, b) => { const p = a.data('t'), q = b.data('t');
    return p.ord !== undefined && q.ord !== undefined && p.ord !== q.ord ? p.ord - q.ord : key(a).localeCompare(key(b)); };
  const kids = z.children().sort(cmp);
  if (arrOf(g, z) === 'arc') return arcBlock(g, z, dir, kids);
  const lines = Math.min(linesFor(g, z, kids.length, v), kids.length);
  // Each line as wide as its widest node; the gap before a line holds that line's port tags ("ports on the
  // edges"), beside its nodes or under them: no wider than they need.
  const ga = v ? 16 : 12, gc = v ? 26 : 18, ofLine = l => kids.filter((k, i) => i % lines === l);
  const tagOf = k => { const t = cy.$id('p:' + k.id()); return t.nonempty() ? (v ? t.data('lr').w : t.data('tb').h) + 14 : 0; };
  const offs = []; let wid = 0;
  for (let l = 0; l < lines; l++) { const ks = ofLine(l); if (l) wid += gc + Math.max(0, ...ks.map(tagOf)); offs.push(wid); wid += Math.max(...ks.map(ac)); }
  // Staggered lines: every node in one virtual line, shared out (node i -> line i % lines), so an edge to the far
  // line passes between two nodes of the near one.
  let acc = 0; const a = [], end = Array(lines).fill(-1e9);
  kids.forEach((k, i) => { const s = al(k), l = i % lines; let c = (acc + s / 2) / lines; acc += s + ga;
    c = Math.max(c, end[l] + ga + s / 2); a.push(c); end[l] = c + s / 2; });
  const start = Math.min(...kids.map((k, i) => a[i] - al(k) / 2)), len = Math.max(...end) - start;
  const W = v ? wid : len, H = v ? len : wid;
  // Round ("cloud"): the same nodes in a frame rounded to an oval; the margin keeps the corner nodes inside it
  // (a box W x H fits a stadium of radius r when the margin is >= (sqrt(2) - 1) / 2 of its short side).
  const round = arrOf(g, z) === 'ci', P = round ? PAD + 0.22 * Math.min(W, H) : PAD;
  const place = (pos, fx, fy) => {  // (fx, fy) = top-left corner of the frame; a B frame carries its title underneath
    z.style({padding: P, 'corner-radius': round ? Math.min(W, H) / 2 + P : 4});  // when the side is chosen, not while tried
    const x0 = fx + P, y0 = fy + (dir === 'B' ? 0 : TITLE) + P;
    kids.forEach((k, i) => { const off = offs[i % lines], w = k.data('w'), h = k.data('h'), t = a[i] - start;
      pos[k.id()] = dir === 'R' ? {x: x0 + off + w / 2, y: y0 + t} : dir === 'L' ? {x: x0 + W - off - w / 2, y: y0 + t}
        : dir === 'T' ? {x: x0 + t, y: y0 + H - off - h / 2} : {x: x0 + t, y: y0 + off + h / 2}; });
  };
  return {z, dir, FW: W + 2 * P, FH: H + 2 * P + TITLE, place};
}
// Half moon: the nodes on an arc bulging away from the Source, one per height (one per column above or below it),
// in an oval frame around the arc only: edges come in at right angles and cross no node.
function arcBlock(g, z, dir, kids) {
  const n = kids.length, v = dir === 'R' || dir === 'L', gap = v ? 12 : 16;
  const tagOf = k => { const t = g.cy.$id('p:' + k.id()); return t.nonempty() ? (v ? t.data('lr').w : t.data('tb').h) + 14 : 0; };
  const mw = Math.max(...kids.map(k => k.data('w'))), mh = Math.max(...kids.map(k => k.data('h')));
  const Ra = n * ((v ? mh : mw) + gap) / 2, depth = n < 3 ? 0 : Math.max(40, Ra * 0.5) + Math.max(0, ...kids.map(tagOf));
  const W = v ? depth + mw : 2 * Ra, H = v ? 2 * Ra : depth + mh, P = PAD + 0.22 * Math.min(W, H), far = dir === 'R' || dir === 'B' ? 1 : -1;
  const place = (pos, fx, fy) => {
    z.style({padding: P, 'corner-radius': Math.min(W, H) / 2 + P});
    const x0 = fx + P, y0 = fy + (dir === 'B' ? 0 : TITLE) + P;
    kids.forEach((k, i) => { const u = -1 + 2 * (i + 0.5) / n, d = depth * Math.sqrt(1 - u * u), w = k.data('w'), h = k.data('h');
      pos[k.id()] = v ? {x: far > 0 ? x0 + w / 2 + d : x0 + W - w / 2 - d, y: y0 + Ra + u * (Ra - (mh + gap) / 2)}
        : {x: x0 + Ra + u * (Ra - (mw + gap) / 2), y: far > 0 ? y0 + h / 2 + d : y0 + H - h / 2 - d}; });
  };
  return {z, dir, FW: W + 2 * P, FH: H + 2 * P + TITLE, place};
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
    // A diagram's own sides (Pivot Machines: Reached from on the left, Leads to on the right; above / below a row)
    // always hold, whatever the arrangement; a right-click pin holds when the arrangement allows it.
    const fixed = g.D.sides && g.D.sides[n];
    if (fixed) return [dirs.includes(fixed) ? fixed : {L: 'T', R: 'B', T: 'L', B: 'R'}[fixed]];
    let pin = g.pin && g.pin[n];
    if (pin && !dirs.includes(pin)) pin = {L: 'T', R: 'B', T: 'L', B: 'R'}[pin];
    if (pin && dirs.includes(pin) && (FREE.includes(a) || (a[0] === 'c') === 'RL'.includes(pin))) return [pin];
    const ok = [...dirs].filter(d => FREE.includes(a) || (a[0] === 'c') === 'RL'.includes(d));
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
const LAYOUT = {sides: g => around(g, 'RLTB'), lr: g => around(g, 'RL'), tb: g => around(g, 'TB'), ring};

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
  // A Machine centre: the edges leaving one Interface (or the Machine) on one side start apart (in the order of their other end),
  // so two edges never share a segment.
  const off = {};
  if (g.D.center.ifaces) cy.nodes('.iface, .mframe').forEach(i => { const by = {};
    i.connectedEdges('.flow').forEach(e => { const d = side[(e.target().hasClass('zone') ? e.target() : e.target().parent()).id()];
      if (d) (by[d] = by[d] || []).push(e); });
    for (const [d, es] of Object.entries(by)) { const v = 'TB'.includes(d), ax = v ? 'x' : 'y', room = (v ? i.width() : i.height()) - 10;
      const step = Math.min(10, room / Math.max(1, es.length - 1));
      es.sort((a, b) => a.target().position(ax) - b.target().position(ax)).forEach((e, k) => { off[e.id()] = (k - (es.length - 1) / 2) * step; }); } });
  cy.batch(() => {
    cy.nodes('.zone').forEach(z => z.style(side[z.id()] === 'B' ? {'text-valign': 'bottom', 'text-margin-y': 5} : {'text-valign': 'top', 'text-margin-y': -5}));
    cy.edges('.flow').forEach(e => {
      const t = e.target(), z = t.hasClass('zone') ? t : t.parent(), d = side[z.id()] || '';
      e.data('side', d);
      const st = d ? {'source-endpoint': END[d][0], 'target-endpoint': END[d][1]} : {'source-endpoint': 'outside-to-node', 'target-endpoint': 'outside-to-node'};
      const o = off[e.id()];
      if (d && o) st['source-endpoint'] = 'TB'.includes(d) ? `${o}px ${END[d][0].split(' ')[1]}` : `${END[d][0].split(' ')[0]} ${o}px`;
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
// A Machine centre: its Interfaces in one column (edges leave them sideways, so the Zones go beside it) or, by a
// right-click on the Machine, in one row (the Zones go above and below it).
function stackCentre(g) {
  const S = g.cy.$id('S'), kids = S.children(), pos = {};
  if (!kids.nonempty()) return pos;
  const row = g.marr === 'row', gap = row ? 16 : 12, al = k => k.data(row ? 'w' : 'h');
  const L = kids.reduce((h, k) => h + al(k), 0) + gap * (kids.length - 1), C = Math.max(...kids.map(k => k.data(row ? 'h' : 'w')));
  let a = -L / 2;
  kids.forEach(k => { pos[k.id()] = row ? {x: a + al(k) / 2, y: TITLE / 2} : {x: 0, y: a + TITLE / 2 + al(k) / 2}; a += al(k) + gap; });
  S.data(row ? {w: L + 2 * PAD, h: C + 2 * PAD + TITLE} : {w: C + 2 * PAD, h: L + 2 * PAD + TITLE});
  S.style(row ? {'text-valign': 'center', 'text-halign': 'left', 'text-margin-x': -6, 'text-margin-y': 0}  // edges come in above and below
    : {'text-valign': 'top', 'text-halign': 'center', 'text-margin-x': 0, 'text-margin-y': -5});
  return pos;
}
// The layout a diagram really uses: a Machine centre has its Zones on both sides of its column (or above and
// below its row); a diagram that pins its Zones (Pivot Machines) ignores the ring.
function layoutOf(g) {
  if (!g.D.center.ifaces) return O.lay;
  if (g.marr === 'row') return 'tb';
  return O.lay === 'ring' && !g.D.sides ? 'ring' : 'lr';
}
function runLayout(g) {
  const inner = stackCentre(g), lay = layoutOf(g);
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
  zn.union(zn.children()).union(g.cy.nodes('.tag').filter(k => k.data('zone') === z)).union(g.cy.edges('.zedge').filter(e => e.data('zone') === z)).toggleClass('off', off);
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
  // Radio names are per diagram (one name for the page would make every diagram's radios one group: only one
  // checked); data-k is the option.
  const n = GRAPHS.indexOf(g), radio = (k, v, label) => `<label><input type="radio" name="${k}${n}" data-k="${k}" value="${v}"${O[k] === v ? ' checked' : ''}>${label}</label>`;
  const box = (k, label) => `<label><input type="checkbox" data-k="${k}"${O[k] ? ' checked' : ''}>${label}</label>`;
  // Only the layouts that change this diagram: a Machine centre has no "facing" layout, Pivot Machines pin theirs.
  const lays = g.D.sides ? {} : g.D.center.ifaces ? {lr: LAYOUTS.lr, ring: LAYOUTS.ring} : LAYOUTS;
  const pick = Object.keys(lays).length ? `<span class="pick">Layout ${tiles('lay', lays, LAY_ICON, layoutOf(g))}</span>` : '';
  g.el.insertAdjacentHTML('afterbegin',
    `<div class="gbar"><div class="gzones"></div><span class="gact">${pick}`
    + '<button class="btn greset">Reset layout</button><button class="btn gpng">Export PNG</button></span></div>'
    + `<details class="gopts"${O.open ? ' open' : ''}><summary>Options</summary><div class="ggroups">`
    + `<fieldset><legend>Edges</legend>${radio('edges', 'iface', 'one per Interface')}${radio('edges', 'zone', 'one per Zone')}</fieldset>`
    + `<fieldset><legend>Ports</legend>${radio('ports', 'nodes', 'in the nodes')}${radio('ports', 'edges', 'on the edges')}</fieldset>`
    + `<fieldset><legend>Zone arrangement</legend>${tiles('arr', ARR, ARR_ICON, O.arr)}`
    + '<div class="hint">Auto: beside the Source 1 column up to 8 Interfaces, 2 up to 16, 3 beyond; above or below it 1 row up to 6, '
    + '2 up to 12, 3 beyond; ports on the edges, 1. Right-click a Zone to arrange it alone'
    + (g.D.center.ifaces ? ', the Machine to put its Interfaces in a row or a column.' : '.') + '</div></fieldset>'
    + `<fieldset><legend>Machine</legend>${box('mcol', 'colour bar')}${box('mtie', 'dotted link')}`
    + '<div class="hint">Hover an Interface: the other Interfaces of its Machine are ringed.</div></fieldset></div></details>');
  const q = s => g.el.querySelector(s), redrawAll = () => { saveO(); syncPanels(); GRAPHS.forEach(x => { x.dirty = true; }); drawVisibleGraphs(document); };
  g.el.querySelectorAll('.gsnap[data-k]').forEach(t => { t.onclick = e => { const b = e.target.closest('button'); if (!b) return;
    O[t.dataset.k] = b.dataset.v;
    if (t.dataset.k === 'lay') g.pin = null; else GRAPHS.forEach(x => { x.arr = {}; x.pin = null; });
    redrawAll(); }; });
  q('.greset').onclick = () => { g.arr = {}; g.pin = null; g.marr = 'col'; runLayout(g); };
  q('.gpng').onclick = () => { const a = document.createElement('a');
    a.href = URL.createObjectURL(g.cy.png({full: true, scale: 2, bg: '#ffffff', output: 'blob'})); a.download = g.D.file + '.png'; a.click(); };
  q('.gopts').ontoggle = e => { O.open = e.target.open; saveO(); };
  q('.ggroups').onchange = e => { const i = e.target, k = i.dataset.k; O[k] = i.type === 'checkbox' ? i.checked : i.value;
    // one edge per Zone has no edge per node to carry ports: they go into the nodes, and back the other way
    if (k === 'edges' && O.edges === 'zone') O.ports = 'nodes';
    if (k === 'ports' && O.ports === 'edges') O.edges = 'iface';
    if (k === 'arr') GRAPHS.forEach(x => { x.arr = {}; x.pin = null; });
    if (k === 'mtie') { saveO(); syncPanels(); GRAPHS.forEach(x => x.cy && x.cy.edges('.tie').toggleClass('off', !O.mtie)); } else redrawAll(); };
  q('.gzones').onchange = e => { const z = e.target.value; e.target.checked ? g.hidden.delete(z) : g.hidden.add(z); hideZone(g, z, !e.target.checked); runLayout(g); };
}

// The options are the same for every diagram: each panel shows the current ones.
function syncPanels() {
  document.querySelectorAll('.ggroups input[data-k]').forEach(i => { const v = O[i.dataset.k]; i.checked = i.type === 'radio' ? i.value === v : !!v; });
  GRAPHS.forEach(g => g.el.querySelectorAll('.gsnap[data-k]').forEach(t => { const v = t.dataset.k === 'lay' ? layoutOf(g) : O[t.dataset.k];
    t.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.v === v)); }));
}
// Right-click menu at the pointer: a title, one button per choice (the current one marked).
function menu(g, ev, title, choices, cur, pick) {
  document.querySelectorAll('.gmenu').forEach(m => m.remove());
  const m = document.createElement('div'), r = g.cy.container().getBoundingClientRect(), p = ev.renderedPosition;
  m.className = 'gmenu'; m.style.left = (r.left + window.scrollX + p.x) + 'px'; m.style.top = (r.top + window.scrollY + p.y) + 'px';
  m.innerHTML = `<b>${gesc(title)}</b><div class="gsnap">` + Object.entries(choices).map(([k, l]) => `<button data-a="${k}" title="${l}"${cur === k ? ' class="on"' : ''}>`
    + `<svg viewBox="0 0 34 24" width="34" height="24">${ARR_ICON[k]}</svg><span>${l}</span></button>`).join('') + '</div>';
  m.onclick = e => { const b = e.target.closest('button'); if (!b) return; m.remove(); pick(b.dataset.a); runLayout(g); };
  document.body.appendChild(m);
  setTimeout(() => document.addEventListener('click', () => m.remove(), {once: true}));
}
// Right-click anywhere on a Zone (its frame or a node in it): arrange that Zone alone, the other Zones keep their
// side. On a Machine in the centre (its frame or an Interface): its Interfaces in a column or a row.
function rightClick(g, ev) {
  const n = ev.target;
  if (n === g.cy || !n.isNode()) return;
  if (n.hasClass('mframe') || n.hasClass('iface')) { menu(g, ev, g.D.center.machine + ' · Interfaces', MARR, g.marr || 'col', a => { g.marr = a; g.pin = null; }); return; }
  const z = n.hasClass('zone') ? n : n.parent();
  if (!z.nonempty() || !z.hasClass('zone')) return;
  const name = z.data('name');
  menu(g, ev, name, ARR, arrOf(g, z), a => { g.pin = {...g.side}; delete g.pin[name]; g.arr[name] = a; });
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

// Cytoscape keeps the position of its box: when the page moves under a diagram (a fold opens above it), clicks
// land off the pointer. It re-reads the box each time the pointer comes in.
function sync(g) { g.el.querySelector('.gwrap').addEventListener('mouseenter', () => g.cy.resize()); crisp(g.cy); }
// Cytoscape caches each node and each label as a bitmap per zoom level (a power of 2) and builds a level by shrinking
// the one above: after a zoom in and out, card text (SVG images) and labels (Zone titles, "+3") go soft. Our diagrams are small (< 100 nodes):
// every node is drawn straight from its SVG at the current zoom.
// ponytail: patches the renderer's private texture caches (Cytoscape 3.34); on an upgrade check they still exist.
function crisp(cy) {
  try { const d = cy.renderer().data; d.lyrTxrCache.getLayers = () => null;
    for (const k of ['eleTxrCache', 'lblTxrCache', 'slbTxrCache', 'tlbTxrCache']) d[k].getElement = () => null;  // nodes, then labels
  } catch (e) { /* cached, soft */ }
}
function initGraph(el) {
  const g = {el, D: JSON.parse(el.querySelector('script').textContent), arr: {}, pin: null, side: {}, hidden: new Set(), dirty: true, draw: drawGraph};
  GRAPHS.push(g);
  el.graph = g;
  if (g.D.zonegraph) { initZones(el, g); return g; }
  controls(g);
  el.insertAdjacentHTML('beforeend', '<div class="gwrap"><div class="gcy"></div><div class="gtip"></div></div>');
  g.cy = cytoscape({container: el.querySelector('.gcy'), style: STYLE, wheelSensitivity: 0.3, minZoom: 0.15, maxZoom: 4});
  sync(g);
  const cy = g.cy, hide = () => { el.querySelector('.gtip').style.display = 'none'; };
  cy.on('drag', 'node', () => { placeTags(g); hide(); });
  cy.on('cxttap', ev => rightClick(g, ev));
  cy.on('mouseover', 'node.tgt', ev => { const t = ev.target.data('t');
    if (t.multi) cy.nodes('.tgt').filter(n => n.data('t').machine === t.machine).addClass('sib');
    ev.target.connectedEdges('.flow').addClass('hl'); showTip(g, t, ev); });
  cy.on('mouseover', 'edge.flow', ev => { if (ev.target.target().hasClass('tgt')) { ev.target.addClass('hl'); showTip(g, ev.target.target().data('t'), ev); } });
  cy.on('mouseout', 'node, edge', () => { cy.elements().removeClass('sib hl'); hide(); });
  return g;
}
// Draws the diagrams of scope that are visible and not drawn yet (or changed since); Cytoscape needs a sized box.
function drawVisibleGraphs(scope) {
  if (typeof cytoscape === 'undefined') return;
  scope.querySelectorAll('.graph').forEach(el => {
    if (el.offsetParent === null) return;
    const g = el.graph || initGraph(el);
    if (g.dirty) g.draw(g);
  });
}
// Port Group changed: every diagram is redrawn when next shown.
function graphsChanged() { GRAPHS.forEach(g => { g.dirty = true; }); }

// ---- the Global view: Zone -> Zone. Zones on a circle (deterministic), one edge per Zone pair (a loop inside a
// Zone), its ports in a tag on the edge (admin bold, denied red) ----
function zoneLinks(D) {
  const set = groupSet();
  return D.links.flatMap(l => { if (!set) return [l];
    const ports = l.verdict === 'OPEN' ? l.ports.filter(p => inRanges(p.l, set)) : [];
    return ports.length ? [{...l, ports}] : []; });
}
function zoneElements(g) {
  const D = g.D, links = zoneLinks(D);
  const els = D.nodes.map(z => { const [f, s, c] = D.zones[z.zone];
    return {data: {id: 'z:' + z.zone, name: z.zone, label: `${z.zone}\n${z.n} Interface(s)`, fill: f, stroke: s, text: c}, classes: 'znode'}; });
  for (const l of links) {
    const id = `e:${l.from}>${l.to}`, open = l.verdict === 'OPEN';
    els.push({data: {id, source: 'z:' + l.from, target: 'z:' + l.to, col: edgeCol(l), z: RANK[status(l)] || 0, l,
      label: open ? '' : l.word}, classes: 'flow zflow' + (open ? '' : ' dash') + (l.from === l.to ? ' loop' : '')});
    if (open) els.push({data: {id: 'p:' + id, of: id, col: edgeCol(l), ...tag(l, 170)}, classes: 'tag'});
  }
  return els;
}
const ZSTYLE = STYLE.concat([
  {selector: 'node.znode', style: {shape: 'round-rectangle', 'corner-radius': 6, 'background-color': 'data(fill)', 'border-color': 'data(stroke)',
    'border-width': 2, label: 'data(label)', color: 'data(text)', 'font-weight': 700, 'font-size': 14, 'font-family': FONT, 'text-wrap': 'wrap',
    'text-valign': 'center', 'text-halign': 'center', width: 'label', height: 'label', padding: 14, 'line-height': 1.4}},
  {selector: 'edge.zflow', style: {'curve-style': 'bezier', 'control-point-step-size': 46, width: 1.8, 'arrow-scale': 0.9, label: 'data(label)',
    'font-size': 10.5, color: SLATE, 'font-family': FONT, 'text-background-color': '#fff', 'text-background-opacity': 1, 'text-background-padding': 2}},
  {selector: 'edge.loop', style: {'loop-direction': '0deg', 'loop-sweep': '-50deg', 'control-point-step-size': 70}},
]);
function drawZones(g) {
  const cy = g.cy;
  cy.elements().remove();
  cy.add(zoneElements(g));
  const n = cy.nodes('.znode').length;
  cy.nodes('.znode').layout({name: 'circle', fit: false, radius: Math.max(200, n * 62), startAngle: -Math.PI / 2,
    sort: (a, b) => a.id().localeCompare(b.id())}).run();
  // loops point away from the centre of the circle
  const c = cy.nodes('.znode').boundingBox(), cx = (c.x1 + c.x2) / 2, cyy = (c.y1 + c.y2) / 2;
  cy.edges('.loop').forEach(e => { const p = e.source().position();
    e.style('loop-direction', (Math.atan2(p.x - cx, cyy - p.y) * 180 / Math.PI) + 'deg'); });
  placeZoneTags(g);
  cy.fit(cy.elements(), 24);
  if (cy.zoom() > 1.1) { cy.zoom(1.1); cy.center(); }
  g.dirty = false;
}
// A port tag sits on its edge, past the middle towards the target: the two edges of a pair keep theirs apart.
function placeZoneTags(g) {
  g.cy.nodes('.tag').forEach(k => { const e = g.cy.$id(k.data('of')), m = e.midpoint(), s = e.source().position(), t = e.target().position();
    if (e.isLoop()) { k.position(m); return; }
    const L = Math.hypot(t.x - s.x, t.y - s.y) || 1, n = e.target(), room = (Math.max(k.width(), k.height()) + Math.max(n.width(), n.height())) / 2 + 8;
    const d = Math.max(0, Math.min(0.2 * L, L / 2 - room));  // past the middle, never onto the target
    k.position({x: m.x + (t.x - s.x) / L * d, y: m.y + (t.y - s.y) / L * d}); });
}
function zoneTip(g, l, ev) {
  const tip = g.el.querySelector('.gtip'), st = status(l), D = g.D;
  const ports = l.ports.map(p => `<span style="${p.admin ? 'font-weight:700;' : ''}${p.st === 'deny' ? 'color:#dc2626' : ''}">${gesc(p.l)}</span>`).join(', ');
  tip.innerHTML = `<h4>${gesc(l.from)} → ${gesc(l.to)}</h4><div><span class="k">verdict</span> <b>${l.verdict}</b> · ${gesc(l.pairs)} Interface pairs</div>`
    + (ports ? `<div><span class="k">open ports</span> ${ports}</div>` : '')
    + (st ? `<div><span class="k">Flow Policy</span> <i class="pg pg-${st}">${ICON[st][0]}</i>${WORD[st]}</div>` : '');
  const {x, y} = ev.renderedPosition; tip.style.display = 'block'; tip.style.left = (x + 16) + 'px'; tip.style.top = (y + 16) + 'px';
}
function initZones(el, g) {
  el.insertAdjacentHTML('afterbegin', '<div class="gbar"><span class="gact"><button class="btn greset">Reset layout</button>'
    + '<button class="btn gpng">Export PNG</button></span></div>');
  el.insertAdjacentHTML('beforeend', '<div class="gwrap"><div class="gcy"></div><div class="gtip"></div></div>');
  g.cy = cytoscape({container: el.querySelector('.gcy'), style: ZSTYLE, wheelSensitivity: 0.3, minZoom: 0.15, maxZoom: 4});
  sync(g);
  el.querySelector('.greset').onclick = () => drawZones(g);
  el.querySelector('.gpng').onclick = () => { const a = document.createElement('a');
    a.href = URL.createObjectURL(g.cy.png({full: true, scale: 2, bg: '#ffffff', output: 'blob'})); a.download = g.D.file + '.png'; a.click(); };
  g.cy.on('drag', 'node.znode', () => placeZoneTags(g));
  g.cy.on('mouseover', 'edge.zflow', ev => { ev.target.addClass('hl'); zoneTip(g, ev.target.data('l'), ev); });
  g.cy.on('mouseout', 'edge', ev => { ev.target.removeClass('hl'); el.querySelector('.gtip').style.display = 'none'; });
  g.draw = drawZones;
}
