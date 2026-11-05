let GROUP='';  // index of the selected Port Group, '' = all ports
// Draws the diagrams of scope that are shown (report_graph.js); Cytoscape needs a visible, sized box.
function renderVisible(scope){ if(scope) drawVisibleGraphs(scope); }
// Big tabs; the open tab is kept in the URL hash, so a reload (or a shared link) reopens it.
function showTab(id){
  const pane=document.getElementById('tab-'+id);
  if(!pane) return;
  document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('active', p===pane));
  document.querySelectorAll('.bigtabs a').forEach(t=>t.classList.toggle('on', t.dataset.tab===id));
  history.replaceState(null, '', '#'+id);
  freeze(pane);
  renderVisible(pane);
}
function showSource(key){
  document.querySelectorAll('.srcpane').forEach(p=>p.style.display='none');
  const el=document.getElementById(key);
  if(el){el.style.display='block'; renderVisible(el);}
}
// Port Group filter: keeps only the OPEN flows on the group's ports, in tables (data-p) and diagrams.
// Port label ('22' = tcp, 'udp:161') inside proto -> [[lo,hi]] ranges; mirrors ports.port_label/in_port_set.
function inRanges(label, byProto){
  const [proto, port]=label.includes(':')?label.split(':'):['tcp', label];
  return (byProto[proto]||[]).some(([lo,hi])=>+port>=lo && +port<=hi);
}
// Port Group chips: the active one is filled; the bar is underlined while a group filters.
function pickGroup(btn){
  document.querySelectorAll('.gchip').forEach(b=>b.classList.toggle('on', b===btn));
  setGroup(btn.dataset.g);
}
// Open ports of an element, admin ones bold, '+n' beyond cap. Mirrors html.py _ports_html.
function portsHtml(labels, admin, cap){
  const t=labels.map(l=>admin.includes(l)?'<b>'+l+'</b>':l);
  return cap && t.length>cap ? t.slice(0,cap).join(',')+' <small>+'+(t.length-cap)+'</small>' : t.join(',');
}
// Freezes the column widths of the visible matrices (measured unfiltered), so tiles never jump.
function freeze(scope){
  const todo=[...scope.querySelectorAll('table.mx:not([data-frozen])')].filter(t=>t.offsetWidth);
  if(!todo.length) return;
  const set=groupSet(); if(set) filterPorts(null);
  todo.forEach(t=>{ t.dataset.frozen=1; t.querySelectorAll('thead th').forEach(th=>th.style.minWidth=th.getBoundingClientRect().width+'px'); });
  if(set) filterPorts(set);
}
function groupSet(){ return GROUP===''?null:JSON.parse(document.getElementById('port-groups').textContent)[+GROUP]; }
// Changes only the port text of each element (data-p); the Flow Policy icon, bold and tile stay. A tile with no
// port of the group reads as unseen, as in the restricted matrices.
function filterPorts(set){
  document.querySelectorAll('[data-p]').forEach(el=>{
    if(el.dataset.orig===undefined){el.dataset.orig=el.innerHTML; el.dataset.cls=el.className;}
    el.innerHTML=el.dataset.orig; el.className=el.dataset.cls; el.style.display='';
    if(!set) return;
    const keep=el.dataset.p.split(',').filter(x=>x && inRanges(x, set)), pl=el.querySelector('.pl')||el;
    if(keep.length) pl.innerHTML=portsHtml(keep, (el.dataset.b||'').split(','), +el.dataset.cap||0);
    else if(/\bv-/.test(el.dataset.cls)){el.innerHTML='<span class="pl">–</span>'; el.className=el.dataset.cls.replace(/\b[vp]-\w+/g,'')+' v-none';}
    else{pl.textContent=''; if(el.tagName==='LI') el.style.display='none';}
  });
  document.querySelectorAll('[data-pr]').forEach(r=>{r.style.display=!set||inRanges(r.dataset.pr, set)?'':'none';});
  document.querySelectorAll('.card').forEach(c=>{
    const li=[...c.querySelectorAll('li[data-p]')];
    if(li.length) c.style.display=li.some(l=>l.style.display!=='none')?'':'none';
  });
}
function setGroup(g){
  freeze(document.querySelector('.pane.active'));
  GROUP=g;
  document.body.classList.toggle('grp', g!=='');
  filterPorts(groupSet());
  graphsChanged();
  renderVisible(document.querySelector('.pane.active'));
}
window.addEventListener('DOMContentLoaded',()=>{
  const h=location.hash.slice(1);
  if(document.getElementById('tab-'+h)) showTab(h); else renderVisible(document.querySelector('.pane.active'));
});
// Every table (matrices aside): one search field above it, sort on a header click (again: reverse). Plain
// <table>s stay copyable into an audit report. A detail row (tr.more) follows its row.
function rowGroups(t){
  const g=[];
  [...t.tBodies[0].rows].forEach(r=>{ if(r.classList.contains('more') && g.length) g[g.length-1].push(r); else g.push([r]); });
  return g;
}
function filterRows(inp){
  const q=inp.value.toLowerCase().trim();
  rowGroups(inp.nextElementSibling.querySelector('table')).forEach(([r, ...more])=>{
    const hit=r.textContent.toLowerCase().includes(q);
    r.style.display=hit?'':'none'; more.forEach(m=>m.style.display=hit?'':'none');
  });
}
function sortBy(th){
  const t=th.closest('table'), i=[...th.parentNode.children].indexOf(th), dir=th.dataset.s==='asc'?'desc':'asc';
  th.parentNode.querySelectorAll('th').forEach(x=>x.dataset.s=''); th.dataset.s=dir;
  const key=g=>(g[0].cells[i]?g[0].cells[i].textContent.replace(/^[▸▾] /,'').trim():'');
  const groups=rowGroups(t).sort((x,y)=>key(x).localeCompare(key(y),undefined,{numeric:true,sensitivity:'base'})*(dir==='asc'?1:-1));
  groups.forEach(g=>g.forEach(r=>t.tBodies[0].appendChild(r)));
}
function enhanceTables(scope){
  scope.querySelectorAll('.tablewrap>table:not(.mx)').forEach(t=>{
    if(t.dataset.ready || !t.tBodies[0] || t.tBodies[0].rows.length<2) return;
    t.dataset.ready=1;
    const inp=document.createElement('input');
    inp.type='search'; inp.className='filter'; inp.placeholder='Search this table…'; inp.oninput=()=>filterRows(inp);
    t.parentNode.before(inp);
    t.querySelectorAll('thead th').forEach(th=>{ th.dataset.s=''; th.onclick=()=>sortBy(th); });
  });
}
// Target details: a row with open ports unfolds what each Scan saw on each port.
function toggleMore(tr){
  const m=tr.nextElementSibling; m.hidden=!m.hidden;
  const th=tr.querySelector('th'); th.textContent=(m.hidden?'▸ ':'▾ ')+th.textContent.slice(2);
}
window.addEventListener('DOMContentLoaded',()=>enhanceTables(document));
// Scan Diff: compares the open ports of two observation sets (a Scan or a Source View) per target.
function esc(s){ return String(s).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]); }
function testedOn(cell, label){
  if(!cell) return false;            // target absent from that side's output
  if(cell.tested===null) return null; // non-XML Scan: unknown
  return inRanges(label, cell.tested);
}
function sideState(cell, label){
  if(cell && cell.open.includes(label)) return 'open';
  const t=testedOn(cell, label);
  return t===true?'not open':t===null?'unknown':'not tested';
}
const DIFF_ORDER=['added','removed','not comparable','unchanged'];
function runDiff(){
  const D=JSON.parse(document.getElementById('diff-data').textContent);
  const A=D.sets[+document.getElementById('diff-a').value], B=D.sets[+document.getElementById('diff-b').value];
  const name=ip=>D.targets[ip]?D.targets[ip].name:ip, zone=ip=>D.targets[ip]?D.targets[ip].zone:'';
  const rows=[], verdicts=[];
  for(const t of new Set([...Object.keys(A.cells), ...Object.keys(B.cells)])){
    const a=A.cells[t], b=B.cells[t], va=a?a.v:'UNSEEN', vb=b?b.v:'UNSEEN';
    if(a && b && va!==vb) verdicts.push([t, va, vb]);  // a target only one side scanned is not a change
    for(const p of new Set([...(a?a.open:[]), ...(b?b.open:[])])){
      const inA=a&&a.open.includes(p), inB=b&&b.open.includes(p);
      const kind=inA&&inB?'unchanged':inB?(testedOn(a,p)===true?'added':'not comparable')
                                          :(testedOn(b,p)===true?'removed':'not comparable');
      rows.push([kind, t, p, sideState(a,p), sideState(b,p)]);
    }
  }
  rows.sort((x,y)=>DIFF_ORDER.indexOf(x[0])-DIFF_ORDER.indexOf(y[0]) || name(x[1]).localeCompare(name(y[1])) || x[2].localeCompare(y[2], undefined, {numeric:true}));
  const count=k=>rows.filter(r=>r[0]===k).length;
  const summary=DIFF_ORDER.map(k=>`<span class="d-${k.replace(' ','-')}">${count(k)} ${k}</span>`).join('');
  const vt=verdicts.map(([t,va,vb])=>`<tr><th>${esc(name(t))}</th><td>${esc(zone(t))}</td><td>${va}</td><td>${vb}</td></tr>`).join('');
  const pt=rows.map(([k,t,p,sa,sb])=>`<tr><td class="d-${k.replace(' ','-')}">${k}</td><th>${esc(name(t))}</th><td>${esc(zone(t))}</td><td>${esc(p)}</td><td>${sa}</td><td>${sb}</td></tr>`).join('');
  document.getElementById('diff-out').innerHTML=
    `<p><b>A</b> ${esc(A.label)}<br><b>B</b> ${esc(B.label)}</p><div class="legend">${summary}</div>`+
    `<h3>Open ports</h3>`+
    `<div class="tablewrap"><table><thead><tr><th>change</th><th>target</th><th>zone</th><th>port</th><th>A</th><th>B</th></tr></thead><tbody>${pt||'<tr><td colspan="6">No open port on either side.</td></tr>'}</tbody></table></div>`+
    `<h3>Verdict changes</h3><p class="legend">Targets present in both outputs only.</p><div class="tablewrap"><table><thead><tr><th>target</th><th>zone</th><th>A</th><th>B</th></tr></thead><tbody>${vt||'<tr><td colspan="4">None.</td></tr>'}</tbody></table></div>`;
  enhanceTables(document.getElementById('diff-out'));
}
window.addEventListener('DOMContentLoaded',()=>{
  const a=document.getElementById('diff-a'), b=document.getElementById('diff-b');
  if(!a) return;
  b.selectedIndex=Math.min(1, b.options.length-1);
  runDiff();
});
// Per target: the search names a Machine (name · IPs · zones, from the datalist); show its pane, draw it then.
function pickTarget(v){
  const o=[...document.querySelectorAll('#tgtlist option')].find(o=>o.value===v); if(!o) return;
  document.querySelectorAll('.tgtpane').forEach(p=>p.style.display='none');
  const el=document.getElementById(o.dataset.k); el.style.display='block'; renderVisible(el);
}
// Copies open ports ready for nmap -p; where the clipboard API is missing or refused: textarea fallback.
function copyPorts(btn){
  const t=btn.dataset.ports, o=btn.textContent;
  const done=()=>{btn.textContent='Copied ✓'; btn.classList.add('ok'); setTimeout(()=>{btn.textContent=o; btn.classList.remove('ok');},1400);};
  const fallback=()=>{const a=document.createElement('textarea'); a.value=t; document.body.appendChild(a); a.select(); document.execCommand('copy'); a.remove(); done();};
  if(navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(t).then(done, fallback); else fallback();
}
