const HAS_MM = typeof mermaid !== 'undefined';
if(HAS_MM) mermaid.initialize({startOnLoad:false, securityLevel:'loose', theme:'default', flowchart:{htmlLabels:true}});
let idc=0;
async function renderVisible(scope){
  if(!scope) return;
  for(const el of [...scope.querySelectorAll('.mermaid:not([data-done])')]){
    if(el.offsetParent===null) continue;
    el.setAttribute('data-done','1');
    if(!HAS_MM){el.innerHTML='<b class="err">mermaid.js not loaded (offline? seg_matrix/assets/mermaid.min.js missing); diagram source:</b><br>'+el.innerHTML; continue;}
    el.dataset.src=el.textContent;
    try{const {svg}=await mermaid.render('mm'+(idc++), el.textContent); el.innerHTML=svg;}
    catch(e){el.innerHTML='<pre class="err">'+String(e)+'</pre>';}
  }
}
function showTab(id){
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  document.querySelector('.tab[data-tab="'+id+'"]').classList.add('active');
  renderVisible(document.getElementById('tab-'+id));
}
function showSource(key){
  document.querySelectorAll('.srcpane').forEach(p=>p.style.display='none');
  const el=document.getElementById(key);
  if(el){el.style.display='block'; renderVisible(el);}
}
// Removes from the Mermaid source the subgraphs of unchecked zones (off = Set of Z_* ids), their edges,
// and renumbers the linkStyle lines (index = order of edges in the source).
function filterZones(src, off){
  const lines=src.split('\n'), drop=new Set(), out=[], styles=[], keep=[];
  let cur=null;
  const sub=l=>(l.match(/^\s*subgraph (\w+)\[/)||[])[1], isEnd=l=>/^\s*end\s*$/.test(l);
  for(const l of lines){
    if(sub(l)){cur=sub(l);continue;} if(isEnd(l)){cur=null;continue;}
    const n=l.match(/^\s*(H_\w+)\(/); if(n && off.has(cur)) drop.add(n[1]);
  }
  cur=null;
  for(const l of lines){
    if(sub(l)) cur=sub(l);
    const skip=cur!==null && off.has(cur);
    if(isEnd(l)) cur=null;
    if(skip) continue;
    const st=l.match(/^\s*style (\w+)/); if(st && off.has(st[1])) continue;
    if(/^\s*linkStyle /.test(l)){styles.push(l);continue;}
    if(/(==>|-\.-)/.test(l)){
      const p=l.trim().split(/\s+/), ok=!drop.has(p[0]) && !drop.has(p[p.length-1]);
      keep.push(ok); if(ok) out.push(l); continue;
    }
    out.push(l);
  }
  let k=0;
  styles.forEach((s,i)=>{ if(keep[i]) out.push(s.replace(/linkStyle \d+/, 'linkStyle '+(k++))); });
  return out.join('\n');
}
async function refilter(cb){
  const pane=cb.closest('.srcpane'), el=pane.querySelector('.mermaid');
  if(!HAS_MM || !el.dataset.src) return;
  const off=new Set([...pane.querySelectorAll('.srcbar input:not(:checked)')].map(i=>i.value));
  try{const {svg}=await mermaid.render('mm'+(idc++), filterZones(el.dataset.src, off)); el.innerHTML=svg;}
  catch(e){el.innerHTML='<pre class="err">'+String(e)+'</pre>';}
}
function dl(name, url){const a=document.createElement('a'); a.href=url; a.download=name; a.click();}
// Exports the displayed (thus filtered) diagram; fully local, no network.
function exportImg(btn, fmt){
  const bar=btn.closest('.srcbar'), s=bar.closest('.srcpane').querySelector('.mermaid svg');
  if(!s) return;
  const zs=[...bar.querySelectorAll('input:checked')].map(i=>i.parentNode.textContent.trim());
  const all=bar.querySelectorAll('input').length===zs.length;
  const name=(bar.dataset.name+(all?'':'_'+zs.join('-'))).replace(/[^\w.-]+/g,'_');
  const vb=s.viewBox.baseVal, w=Math.ceil(vb.width), h=Math.ceil(vb.height);
  const c=s.cloneNode(true);
  c.setAttribute('xmlns','http://www.w3.org/2000/svg');
  c.setAttribute('width',w); c.setAttribute('height',h);
  c.setAttribute('style','font-family:'+getComputedStyle(document.body).fontFamily+';background:#fff');
  const x=new XMLSerializer().serializeToString(c);
  if(fmt==='svg'){dl(name+'.svg', URL.createObjectURL(new Blob([x],{type:'image/svg+xml'}))); return;}
  const img=new Image();
  img.onload=()=>{
    const k=2, cv=document.createElement('canvas'); cv.width=w*k; cv.height=h*k;
    const g=cv.getContext('2d'); g.fillStyle='#fff'; g.fillRect(0,0,cv.width,cv.height);
    g.scale(k,k); g.drawImage(img,0,0,w,h);
    try{cv.toBlob(b=>dl(name+'.png', URL.createObjectURL(b)));}
    catch(e){alert('PNG refused by this browser (HTML labels): use the SVG export.');}
  };
  img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(x);
}
window.addEventListener('DOMContentLoaded',()=>renderVisible(document.getElementById('tab-global')));
// Hides the rows of the table following the filter box that do not contain its text.
function filterRows(inp){
  const q=inp.value.toLowerCase(), rows=inp.nextElementSibling.querySelectorAll('tbody tr');
  rows.forEach(r=>{r.style.display=r.textContent.toLowerCase().includes(q)?'':'none';});
}
