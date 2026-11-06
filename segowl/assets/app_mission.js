// SegOWL — Mission page: client zip import with a dry-run preview (ticket 03).
const imp=document.getElementById("imp"),res=document.getElementById("impres");let blob=null;
const show=(cls,pairs,extra)=>{res.innerHTML="";const box=document.createElement("div");box.className=cls;
  for(const [k,v] of pairs){const d=document.createElement("div"),b=document.createElement("b");b.textContent=k+": ";
    d.append(b,document.createTextNode(v));box.append(d)}res.append(box);if(extra)res.insertAdjacentHTML("beforeend",extra)};
const send=async apply=>{const r=await fetch("/api/import/client"+(apply?"":"?dry=1"),
    {method:"POST",headers:{"X-SegOWL":"1"},body:blob});const j=await r.json();
  if(!r.ok)return show("err",[["Import",j.error]]);
  const pairs=Object.entries(j.report);if(j.applied)pairs.push(["Done","the Mission now uses these files"]);
  show(j.ok?"ok":"err",pairs,j.ok&&!j.applied?'<div class="banner"><span class="small">These files will replace '+
    'the Mission\'s.</span><button class="btn pri sm" id="go">Replace</button><button class="btn sm" id="no">Cancel</button></div>':"");
  if(document.getElementById("go")){document.getElementById("go").onclick=()=>send(true);
    document.getElementById("no").onclick=()=>res.innerHTML=""}};
imp.onchange=()=>{blob=imp.files[0];imp.value="";if(blob)send(false)};
