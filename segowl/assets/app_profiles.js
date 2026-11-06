// SegOWL — scan builder on the Scans page (app-navigation 06; editor from local-app 04). It edits a DRAFT of a
// Scan Profile: nothing is saved until "Save as a new profile version", "Update" or "Discard". Commands are
// computed by the server (/api/profiles/preview). window.SegDraft tells the Sources grid which profile is modified.
"use strict";

// ---------------------------------------------------------------- option metadata (help texts, not policy)
const TCP = [["-sS", "SYN", "TCP SYN scan (needs root)"], ["-sT", "Connect", "TCP connect scan (no root, works through SOCKS)"], ["-sA", "ACK", "ACK scan: maps filtering (unfiltered = REACHABLE)"], ["", "none", "No TCP scan type given: nmap picks SYN as root, connect otherwise"]];
const FLAGS = {"-n": "n", "--reason": "reason", "-sV": "sV", "-O": "O", "-sC": "sC"};
const QUICK = [["-Pn", "skip host discovery", o => o.pn = true], ["-sS", "TCP SYN scan", o => o.tcp = "-sS"], ["-sT", "TCP connect scan", o => o.tcp = "-sT"], ["-sA", "TCP ACK scan", o => o.tcp = "-sA"],
  ["-n", "no DNS resolution", o => o.n = true], ["--reason", "why a port is in its state", o => o.reason = true], ["-sV", "service versions", o => o.sV = true], ["-O", "OS detection", o => o.O = true], ["-sC", "default NSE scripts", o => o.sC = true],
  ...[2, 3, 4, 5].map(n => ["-T" + n, "timing template " + n, o => o.T = n]), ["--max-retries 2", "retransmissions cap", o => o.mr = "2"], ["--min-rate 500", "at least N packets/s", o => o.minrate = "500"], ["--host-timeout 30m", "give up on a slow target", o => o.hto = "30m"]];
const MORE = [
  ["--max-rate", "Send at most N packets/s (fragile networks)", "pkt/s"], ["--scan-delay", "Wait between probes (IDS-sensitive targets)", "e.g. 50ms"], ["--max-scan-delay", "Cap the adaptive delay", "e.g. 20ms"],
  ["--max-parallelism", "Cap concurrent probes", "N"], ["--min-parallelism", "At least N probes in flight", "N"], ["--min-hostgroup", "Scan at least N hosts in parallel", "N"], ["--max-hostgroup", "Scan at most N hosts in parallel", "N"],
  ["--initial-rtt-timeout", "Starting probe timeout", "e.g. 200ms"], ["--max-rtt-timeout", "Max probe timeout", "e.g. 500ms"], ["--min-rtt-timeout", "Min probe timeout", "e.g. 50ms"],
  ["--defeat-rst-ratelimit", "Faster when RST is rate-limited (may misreport closed ports)"], ["--defeat-icmp-ratelimit", "Faster UDP when ICMP is rate-limited"],
  ["--version-intensity", "-sV probe intensity 0-9", "0-9"], ["--version-light", "Faster, less thorough -sV"], ["--version-all", "Try every -sV probe"], ["--allports", "Do not exclude any port from -sV"],
  ["--osscan-limit", "OS detection only on promising hosts"], ["--traceroute", "Trace the hop path to each host"], ["-6", "IPv6 scanning"],
  ["--ttl", "Set IP time-to-live", "N"], ["--mtu", "Fragment packets with this MTU (filter testing)", "multiple of 8"], ["-f", "Fragment packets (filter testing)"], ["--data-length", "Append random data to packets", "bytes"],
  ["--source-port", "Use this source port (e.g. 53, to test lax firewall rules)", "port"], ["--badsum", "Bogus checksums (firewall detection)"], ["-sN", "TCP Null scan"], ["-sF", "TCP FIN scan"], ["-sX", "TCP Xmas scan"], ["-sW", "TCP Window scan"],
  ["-sY", "SCTP INIT scan"], ["-sO", "IP protocol scan"], ["-sU", "UDP scan (added automatically for UDP ports)"], ["-PE", "ICMP echo discovery"], ["-PS", "TCP SYN discovery on ports", "ports"], ["-PA", "TCP ACK discovery on ports", "ports"],
  ["-PU", "UDP discovery on ports", "ports"], ["-PR", "ARP discovery (local LAN)"], ["--disable-arp-ping", "No ARP/ND discovery on local LAN"], ["--send-ip", "Raw IP rather than Ethernet frames"],
  ["--privileged", "Assume full privileges"], ["--unprivileged", "Assume no raw socket privileges"], ["--stats-every", "Print progress periodically", "e.g. 1m"], ["-v", "Verbose output"], ["-d", "Debug output"],
  ["--packet-trace", "Show every packet"], ["-r", "Scan ports in order (not randomised)"],
].map(([f, h, arg]) => ({f, h, arg}));
const NSE = [["ssl-cert", "default,safe", "Certificate subject, issuer, validity"], ["ssl-enum-ciphers", "discovery,intrusive", "TLS versions and ciphers"], ["smb-os-discovery", "default,safe", "OS, domain, NetBIOS name via SMB"], ["smb2-security-mode", "default,safe", "SMB signing required or not"], ["smb-security-mode", "default,safe", "SMBv1 security level"], ["smb-protocols", "safe", "Supported SMB dialects (SMBv1?)"], ["rdp-ntlm-info", "default,safe", "Domain and host names via RDP NTLM"], ["rdp-enum-encryption", "safe", "RDP security layers"], ["http-title", "default,safe", "Web page title"], ["http-headers", "safe", "HTTP response headers"], ["http-methods", "default,safe", "Allowed HTTP methods"], ["ldap-rootdse", "safe", "LDAP root DSE (domain, naming contexts)"], ["ssh-hostkey", "default,safe", "SSH host keys"], ["ssh2-enum-algos", "safe", "SSH algorithms"], ["ssh-auth-methods", "auth,intrusive", "SSH auth methods offered"], ["snmp-info", "default,safe", "SNMP engine info"], ["snmp-sysdescr", "default,safe", "SNMP system description"], ["banner", "discovery,safe", "Grab service banners"], ["vnc-info", "default,safe", "VNC protocol and security"], ["ms-sql-info", "default,safe", "MSSQL instance info"], ["mysql-info", "default,safe", "MySQL server info"], ["nbstat", "default,safe", "NetBIOS names"], ["ntp-info", "default,safe", "NTP server info"], ["ipmi-version", "discovery,safe", "IPMI version (BMC: iLO, iDRAC)"], ["ipmi-cipher-zero", "vuln,safe", "IPMI cipher 0 auth bypass"], ["krb5-enum-users", "auth,intrusive", "Kerberos user enumeration"], ["dns-nsid", "discovery,safe", "DNS server identity"], ["tls-alpn", "safe", "TLS ALPN protocols"]];

// ---------------------------------------------------------------- profile <-> editor state
function parseOpts(str) {
  const t = str.match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) || [];
  const o = {tcp: "", pn: false, T: 3, mr: "", minrate: "", hto: "", n: false, reason: false, sV: false, O: false, sC: false, scripts: [], extra: []};
  for (let i = 0; i < t.length; i++) {
    const f = t[i], nx = t[i + 1];
    if (["-sS", "-sT", "-sA"].includes(f)) o.tcp = f;
    else if (f === "-Pn") o.pn = true;
    else if (/^-T[0-5]$/.test(f)) o.T = +f[2];
    else if (f === "--max-retries" && nx) { o.mr = nx; i++; }
    else if (f === "--min-rate" && nx) { o.minrate = nx; i++; }
    else if (f === "--host-timeout" && nx) { o.hto = nx; i++; }
    else if (FLAGS[f]) o[FLAGS[f]] = true;
    else if (f === "--script" && nx) { o.scripts = nx.split(","); i++; }
    else { const m = MORE.find(x => x.f === f); if ((m && m.arg) || (!m && nx && !nx.startsWith("-"))) { o.extra.push({f, v: nx || ""}); i++; } else o.extra.push({f, v: ""}); }
  }
  return o;
}
function optStr(o) {
  return [o.tcp, o.pn ? "-Pn" : "", o.T !== 3 ? "-T" + o.T : "", o.mr !== "" ? "--max-retries " + o.mr : "", o.minrate ? "--min-rate " + o.minrate : "", o.hto ? "--host-timeout " + o.hto : "",
    ...Object.entries(FLAGS).filter(([, k]) => o[k]).map(([f]) => f), o.scripts.length ? "--script " + o.scripts.join(",") : "",
    ...o.extra.map(e => e.f + (e.v ? " " + e.v : ""))].filter(Boolean).join(" ");
}
const portList = s => s.split(",").map(x => x.trim()).filter(Boolean);

let D = null, cur = 0, P = null, o = null, saved = null, mode = null, saving = false;
const NEW_OPTIONS = "-sS -Pn -T4 --max-retries 2 -n --reason";
const uniq = base => { let n = base, k = 2; while (D.profiles.some(p => p.name === n)) n = `${base}-${k++}`; return n; };
function load(i) { // i = -1: a new profile, not in the kit yet
  cur = i; mode = null;
  saved = i >= 0 ? D.profiles[i] : {name: uniq("new-profile"), ports: "", options: NEW_OPTIONS, description: "", imported: 0};
  P = {name: saved.name, ports: portList(saved.ports)}; o = parseOpts(saved.options); render();
}
const draft = () => ({name: saved.name, ports: P.ports.join(","), options: optStr(o)});
function changes() {
  const was = portList(saved.ports);
  return {add: P.ports.filter(x => !was.includes(x)), rem: was.filter(x => !P.ports.includes(x)), opts: optStr(o) !== optStr(parseOpts(saved.options))};
}
const modified = () => { if (cur < 0) return true; const c = changes(); return !!(c.add.length || c.rem.length || c.opts); };
function commit() { drawMod(); preview(); }
async function saveList(list, done) {
  if (saving) return; saving = true; status("Saving…");
  try { const r = await api("/api/profiles", {fp: D.fp, profiles: list}); D = await api("/api/profiles"); status("Saved ✓", "ok"); done(); window.dispatchEvent(new Event("profiles-saved")); }
  catch (e) { status(e.status === 409 ? "Modified elsewhere: reload" : "Not saved: " + e.message, "err"); }
  saving = false;
}
window.addEventListener("beforeunload", e => { if (modified()) { e.preventDefault(); e.returnValue = ""; } });

// ---- the "modified" bar: save as a new version, update the profile, or discard
function drawMod() {
  const mod = modified(), c = changes(), name = saved.name;
  window.SegDraft = {name: cur >= 0 ? name : "", modified: mod}; window.dispatchEvent(new Event("draftchange"));
  $("#pf").disabled = mod; $("#pf").title = mod ? "Save or discard the changes first" : "";
  if (!mod) { $("#modbar").innerHTML = ""; return; }
  const pills = cur < 0 ? `<b>New profile</b> <span class="small muted">not in the kit yet</span>` : `<b>Modified from ${esc(name)}</b> ${c.add.map(x => `<span class="pill" style="background:#e6f7ec">+ ${esc(x)}</span>`).join("")}${c.rem.map(x => `<span class="pill" style="background:#fde8e8;text-decoration:line-through">${esc(x)}</span>`).join("")}${c.opts ? `<span class="pill" style="background:#fff3d6">options: ${esc(optStr(o))}</span>` : ""}`;
  const descr = cur < 0 ? "" : `Variant of ${name}: ${[...c.add.map(x => "+" + x), ...c.rem.map(x => "−" + x), ...(c.opts ? ["options changed"] : [])].join(" ")}`;
  const form = `<div class="toolbar" style="margin:6px 0 0"><input type="text" id="nv-name" value="${esc(cur < 0 ? name : uniq(name + "-v2"))}" style="width:170px" title="Profile name: letters, digits, . _ -">
    <input type="text" id="nv-desc" value="${esc(descr)}" placeholder="what it is for" style="flex:1;min-width:220px"><button class="btn sm pri" id="nv-ok">Save ${cur < 0 ? "the profile" : "the new version"}</button><button class="btn sm" data-mb="cancel">Cancel</button></div>`;
  const upd = `<div class="small" style="margin-top:6px">${saved.imported} Source(s) already hold Scans made with the previous version of ${esc(name)}; they keep the same name. Update it anyway? <button class="btn sm pri" data-mb="updok">Update ${esc(name)}</button> <button class="btn sm" data-mb="cancel">Cancel</button></div>`;
  $("#modbar").innerHTML = `<div class="modbar"><span>✎</span><div style="flex:1">${pills}
      <div class="small muted">Scans are tracked by profile name: save the changes to download the scripts.</div>${mode === "newver" ? form : mode === "update" ? upd : ""}</div>
    ${mode ? "" : `<button class="btn sm pri" data-mb="newver">${cur < 0 ? "Save as a new profile…" : "Save as a new profile version…"}</button>${cur < 0 ? "" : `<button class="btn sm" data-mb="update">Update ${esc(name)}</button>`}<button class="btn sm" data-mb="discard">Discard</button>`}</div>`;
  $("#modbar").querySelectorAll("[data-mb]").forEach(b => b.onclick = () => {
    const a = b.dataset.mb;
    if (a === "newver") mode = "newver";
    if (a === "update" || a === "updok") {
      if (a === "update" && saved.imported) mode = "update";
      else return saveList(D.profiles.map((p, i) => i === cur ? {...p, ...draft()} : p), () => { toast(`${name} updated`); load(cur); });
    }
    if (a === "cancel") mode = null;
    if (a === "discard") { toast("Changes discarded"); return load(cur >= 0 ? cur : D.profiles.length ? 0 : -1); }
    drawMod(); if (mode === "newver") $("#nv-name").select();
  });
  if ($("#nv-ok")) {
    const ok = () => {
      const n = $("#nv-name").value.trim();
      if (!/^[A-Za-z0-9][A-Za-z0-9_.-]*$/.test(n) || D.profiles.some(p => p.name === n)) { $("#nv-name").style.borderColor = "#dc2626"; toast(`${n}: name taken or invalid (letters, digits, . _ -)`); return; }
      saveList([...D.profiles, {...draft(), name: n, description: $("#nv-desc").value.trim()}], () => {
        toast(cur < 0 ? `${n} saved in the kit` : `Saved as ${n} in the kit; ${name} is unchanged`); load(D.profiles.findIndex(p => p.name === n));
      });
    };
    $("#nv-ok").onclick = ok; $("#modbar").onkeydown = e => { if (e.key === "Enter" && e.target.tagName === "INPUT") ok(); if (e.key === "Escape") { mode = null; drawMod(); } };
  }
}

// ---------------------------------------------------------------- preview (server)
const preview = debounce(async () => {
  if (!P) return;
  const r = await api("/api/profiles/preview", {...draft(), src: $("#src").value}).catch(e => ({errors: [e.message], commands: [], warnings: []}));
  $("#warns").innerHTML = r.errors.map(e => `<div class="err">${esc(e)}</div>`).join("") + r.warnings.map(w => `<div class="warn">${esc(w)}</div>`).join("");
  $("#cmd").innerHTML = r.commands.map((c, i) => `<div class="small muted" style="margin-top:6px">${r.commands.length > 1 ? `Scan ${i + 1}/${r.commands.length} · ` : ""}${esc(c.label)}${r.commands.length > 1 && i === 0 ? " — nmap would intersect --top-ports with -p, so they run separately; SegOWL merges both into the Source View" : ""}</div><pre class="cmd">${esc(c.cmd)}</pre>`).join("");
  const c = r.counts || {};
  $("#cnt").textContent = c.targets !== undefined ? `${c.top ? "top " + c.top + " + " : ""}${c.tcp} TCP · ${c.udp} UDP` : "";
  $("#tcount").textContent = c.targets !== undefined ? `${c.targets} targets (inventory minus Self)` : "";
  $("#udph").innerHTML = c.udp ? `-sU added automatically for the <b>${c.udp}</b> UDP port(s)` : `<span class="muted">no UDP port selected</span>`;
}, 250);

// ---------------------------------------------------------------- rendering
function refreshList() {
  $("#pf").innerHTML = D.profiles.map((p, i) => `<option value="${i}" ${i === cur ? "selected" : ""}>${esc(p.name)}</option>`).join("") + (cur < 0 ? `<option value="-1" selected>${esc(saved.name)} (new)</option>` : "");
  $("#pdesc").innerHTML = saved.description ? esc(saved.description) : `<span class="muted">No description yet: <a href="/kit/profiles">Auditor Kit › Scan Profiles</a>.</span>`;
}
function render() {
  refreshList();
  $("#grps").innerHTML = Object.entries(D.groups).map(([g, spec]) => `<label class="pill grp" style="cursor:pointer" title="${esc(spec)}"><input type="checkbox" data-g="${esc(g)}" ${P.ports.includes("@" + g) ? "checked" : ""}> ${esc(g)} <span class="muted">${spec.split(",").length}</span></label>`).join("");
  const top = (P.ports.find(k => k.startsWith("top:")) || "top:none").slice(4);
  $("#top").innerHTML = ["none", "100", "1000", "5000"].map(v => `<button data-v="${v}" class="${v === top ? "on" : ""}">${v}</button>`).join("");
  $("#topc").value = ["none", "100", "1000", "5000"].includes(top) ? "" : top;
  $("#tcp").innerHTML = TCP.map(([f, l]) => `<button data-f="${f}" class="${f === o.tcp ? "on" : ""}">${l} <span class="muted">${f}</span></button>`).join("");
  $("#tcph").textContent = TCP.find(x => x[0] === o.tcp)[2];
  $("#opn").checked = o.pn; $("#tm").innerHTML = [2, 3, 4, 5].map(n => `<button data-n="${n}" class="${n === o.T ? "on" : ""}">T${n}</button>`).join("");
  ["mr", "minrate", "hto"].forEach(k => $("#" + k).value = o[k]); Object.values(FLAGS).forEach(k => $("#" + k).checked = o[k]);
  $("#chips").innerHTML = P.ports.map((k, i) => `<span class="pill ${k.startsWith("@") ? "grp" : ""} ${k.startsWith("udp:") ? "udp" : ""}">${esc(k)}<span class="x" data-i="${i}">✕</span></span>`).join("") || `<span class="muted small">none yet</span>`;
  $("#schips").innerHTML = o.scripts.map((s, i) => `<span class="pill">${esc(s)}<span class="x" data-i="${i}">✕</span></span>`).join("");
  $("#extra").innerHTML = o.extra.map((e, i) => { const m = MORE.find(x => x.f === e.f) || {h: "custom option"};
    return `<div class="opt"><label class="t">${esc(e.f)}</label><div>${m.arg || e.v ? `<input type="text" data-i="${i}" value="${esc(e.v)}" placeholder="${esc(m.arg || "")}" style="width:110px"> ` : ""}<button class="btn sm" data-rm="${i}">remove</button></div><div class="h">${esc(m.h)}</div></div>`; }).join("");
  drawTokens(); commit();
}
const set = fn => { fn(); render(); };

// ---- token line
function tokens() {
  const t = [];
  P.ports.forEach((k, i) => t.push({c: "port", v: k.startsWith("top:") ? "--top-ports " + k.slice(4) : k, rm: () => P.ports.splice(i, 1)}));
  if (o.tcp) t.push({c: "opt", v: o.tcp, rm: () => o.tcp = ""});
  if (o.pn) t.push({c: "opt", v: "-Pn", rm: () => o.pn = false});
  if (o.T !== 3) t.push({c: "opt", v: "-T" + o.T, rm: () => o.T = 3});
  if (o.mr !== "") t.push({c: "opt", v: "--max-retries " + o.mr, rm: () => o.mr = ""});
  if (o.minrate) t.push({c: "opt", v: "--min-rate " + o.minrate, rm: () => o.minrate = ""});
  if (o.hto) t.push({c: "opt", v: "--host-timeout " + o.hto, rm: () => o.hto = ""});
  Object.entries(FLAGS).forEach(([f, k]) => { if (o[k]) t.push({c: "opt", v: f, rm: () => o[k] = false}); });
  o.scripts.forEach((x, i) => t.push({c: "opt", v: "--script " + x, rm: () => o.scripts.splice(i, 1)}));
  o.extra.forEach((e, i) => t.push({c: "opt", v: e.f + (e.v ? " " + e.v : ""), rm: () => o.extra.splice(i, 1)}));
  return t;
}
let thl = 0, titems = [];
function drawTokens() {
  $("#tl").innerHTML = `<span class="tok fixed">nmap</span>` + tokens().map((k, i) => `<span class="tok ${k.c}">${esc(k.v)}<span class="x" data-i="${i}">✕</span></span>`).join("")
    + `<input id="ti" placeholder="add: veeam, top 1000, -sV, ssl-cert, rate…" autocomplete="off"><span class="tok fixed">-iL &lt;targets&gt; -oA scans/&lt;source&gt;/${esc(P.name)}</span>`;
  $("#tl").querySelectorAll(".x").forEach(x => x.onclick = () => { const t = tokens()[+x.dataset.i]; set(t.rm); $("#ti").focus(); });
  const ti = $("#ti"); ti.oninput = debounce(tpal, 120); ti.onblur = () => setTimeout(() => $("#pd").hidden = true, 150);
  ti.onkeydown = e => {
    if (e.key === "Backspace" && !ti.value) { const t = tokens(); if (t.length) { set(t.at(-1).rm); $("#ti").focus(); } return; }
    if (e.key === "ArrowDown") thl = Math.min(thl + 1, titems.length - 1); else if (e.key === "ArrowUp") thl = Math.max(thl - 1, 0);
    else if (e.key === "Enter" || e.key === "Tab") { if (titems[thl]) { e.preventDefault(); tpick(titems[thl]); } return; }
    else if (e.key === "Escape") { $("#pd").hidden = true; return; } else return;
    e.preventDefault(); $("#pd").querySelectorAll(".res").forEach((r, i) => r.classList.toggle("hl", i === thl));
  };
}
async function tpal() {
  const q = $("#ti").value.trim().toLowerCase(); thl = 0; if (!q) { $("#pd").hidden = true; return; }
  const ports = await api("/api/ports?q=" + encodeURIComponent(q));
  titems = [...ports.map(p => ({...p, kind: "port"})),
    ...QUICK.filter(([f, h]) => f.toLowerCase().includes(q) || h.includes(q)).sort((a, b) => (b[0].toLowerCase() === q) - (a[0].toLowerCase() === q)).map(([f, h, fn]) => ({kind: "flag", key: f, label: h, src: "option", fn})),
    ...MORE.filter(x => x.f.toLowerCase().includes(q) || x.h.toLowerCase().includes(q)).map(x => ({kind: "flag", key: x.f, label: x.h, src: "option", fn: o => o.extra.push({f: x.f, v: ""})})),
    ...NSE.filter(([n, , h]) => n.includes(q) || h.toLowerCase().includes(q)).map(([n, c, h]) => ({kind: "flag", key: "--script " + n, label: h, src: "NSE " + c, fn: o => { if (!o.scripts.includes(n)) o.scripts.push(n); }})),
    ...Object.entries(D.denied).filter(([f]) => f.toLowerCase().includes(q)).map(([f, why]) => ({deny: 1, key: f, label: "not allowed: " + why, src: "refused"}))].slice(0, Math.max(40, ports.length)); // every listed port, then options up to 40
  const pd = $("#pd"); pd.hidden = false;
  pd.innerHTML = titems.map((it, i) => `<div class="res ${i === thl ? "hl" : ""}" data-i="${i}" ${it.deny ? 'style="opacity:.6;cursor:not-allowed"' : ""}><span class="p">${esc(it.src === "search" ? "all" : it.many ? "#" + q : it.key)}</span><span>${esc(it.label)}${it.tags ? " " + it.tags.split(",").map(t => `<span class="pill">${esc(t)}</span>`).join("") : ""}</span><span class="src">${esc(it.src)}</span></div>`).join("") || `<div class="res muted">no match</div>`;
  pd.querySelectorAll(".res[data-i]").forEach(r => r.onmousedown = e => { e.preventDefault(); tpick(titems[+r.dataset.i]); });
}
function addPort(it) {
  (it.many || [it.key]).forEach(k => { if (k.startsWith("top:")) P.ports = P.ports.filter(x => !x.startsWith("top:")); if (!P.ports.includes(k)) P.ports.push(k); });
  toast("Added " + (it.many ? (it.ports ?? it.many.length) + " ports" : it.key));
}
function tpick(it) {
  if (it.deny) { toast("Refused: " + it.label); return; }
  set(() => it.kind === "port" ? addPort(it) : it.fn(o)); $("#pd").hidden = true; $("#ti").focus();
}

// ---- port search panel, option and script pickers
let hl = 0, items = [];
const showRes = debounce(async () => {
  const q = $("#q").value; items = q.trim() ? await api("/api/ports?q=" + encodeURIComponent(q)) : []; hl = 0;
  $("#res").innerHTML = items.map((it, i) => `<div class="res ${i === hl ? "hl" : ""}" data-i="${i}"><span class="p">${esc(it.src === "search" ? "all" : it.many ? "#" + q : it.key)}</span><span>${esc(it.label)}${it.tags ? " " + it.tags.split(",").map(t => `<span class="pill">${esc(t)}</span>`).join("") : ""}</span><span class="src">${esc(it.src)}</span></div>`).join("") || `<div class="res muted">No match. Type a port number to add it as is.</div>`;
  $("#res").querySelectorAll(".res[data-i]").forEach(r => r.onclick = () => set(() => addPort(items[+r.dataset.i])));
  // a typed port nobody labelled yet: offer to label it, in this Mission (same form as Auditor Kit › Port Labels)
  const typed = q.trim().toLowerCase().replace(/^tcp:/, "");
  if (Ports.tokOk(typed) && !items.some(it => it.src === "Port Label" && it.key === typed)) {
    $("#res").insertAdjacentHTML("beforeend", `<div class="res" id="lbl1"><span class="p">${esc(typed)}</span><span><b>+ label this port</b> <span class="muted">no Port Label yet: say what runs on it</span></span></div>`);
    $("#lbl1").onclick = () => Ports.labelForm($("#lfbox"), {port: typed, onAdded: L => { const r = L.mission.at(-1); toast(`Port Label ${r[0]} · ${r[1]} added to this Mission`); showRes(); }});
  }
}, 120);
function dropList(inp, drop, list, pick) {
  inp.oninput = () => {
    const q = inp.value.toLowerCase(), l = list(q); drop.hidden = !q;
    drop.innerHTML = l.map((x, i) => `<div class="res" data-i="${i}" ${x.deny ? 'style="opacity:.65;cursor:not-allowed"' : ""}><span class="p">${esc(x.f)}</span><span>${x.deny ? `<span style="color:#8a1a1a">not allowed: ${esc(x.h)}</span>` : esc(x.h)}</span>${x.cat ? `<span class="src">${esc(x.cat)}</span>` : ""}</div>`).join("") || `<div class="res muted">no match</div>`;
    drop.querySelectorAll(".res[data-i]").forEach(r => r.onmousedown = e => { e.preventDefault(); const x = l[+r.dataset.i]; if (x.deny) { toast("Refused: " + x.h); return; } set(() => pick(x)); inp.value = ""; drop.hidden = true; });
  };
  inp.onblur = () => setTimeout(() => drop.hidden = true, 150);
}

function wire() {
  $("#pf").onchange = e => { load(+e.target.value); history.replaceState(null, "", "?profile=" + encodeURIComponent(saved.name)); };
  $("#grps").onchange = e => { const k = "@" + e.target.dataset.g; set(() => P.ports = e.target.checked ? [...P.ports, k] : P.ports.filter(x => x !== k)); };
  const setTop = v => set(() => { P.ports = P.ports.filter(x => !x.startsWith("top:")); if (v && v !== "none") P.ports.unshift("top:" + v); });
  $("#top").onclick = e => { const b = e.target.closest("button"); if (b) setTop(b.dataset.v); };
  $("#topc").onchange = e => setTop(e.target.value);
  $("#chips").onclick = e => { if (e.target.dataset.i) set(() => P.ports.splice(+e.target.dataset.i, 1)); };
  $("#schips").onclick = e => { if (e.target.dataset.i) set(() => o.scripts.splice(+e.target.dataset.i, 1)); };
  $("#tcp").onclick = e => { const b = e.target.closest("button"); if (b) set(() => o.tcp = b.dataset.f); };
  $("#tm").onclick = e => { const b = e.target.closest("button"); if (b) set(() => o.T = +b.dataset.n); };
  $("#opn").onchange = e => set(() => o.pn = e.target.checked);
  ["mr", "minrate", "hto"].forEach(k => $("#" + k).onchange = e => set(() => o[k] = e.target.value.trim()));
  Object.values(FLAGS).forEach(k => $("#" + k).onchange = e => set(() => o[k] = e.target.checked));
  $("#extra").onchange = e => { if (e.target.dataset.i) set(() => o.extra[+e.target.dataset.i].v = e.target.value.trim()); };
  $("#extra").onclick = e => { if (e.target.dataset.rm) set(() => o.extra.splice(+e.target.dataset.rm, 1)); };
  $("#q").oninput = showRes;
  $("#q").onkeydown = e => {
    if (e.key === "ArrowDown") hl = Math.min(hl + 1, items.length - 1); else if (e.key === "ArrowUp") hl = Math.max(hl - 1, 0);
    else if (e.key === "Enter") { if (items[hl]) set(() => addPort(items[hl])); return; } else return;
    e.preventDefault(); $("#res").querySelectorAll(".res").forEach((r, i) => r.classList.toggle("hl", i === hl)); $("#res .hl")?.scrollIntoView({block: "nearest"});
  };
  dropList($("#oq"), $("#od"), q => [...MORE.filter(x => x.f.toLowerCase().includes(q) || x.h.toLowerCase().includes(q)),
    ...Object.entries(D.denied).filter(([f]) => f.toLowerCase().includes(q)).map(([f, h]) => ({f, h, deny: 1})),
    ...(q.startsWith("-") && !MORE.some(x => x.f === q) && !D.denied[q] ? [{f: q, h: "add as a custom option"}] : [])], x => o.extra.push({f: x.f, v: ""}));
  dropList($("#sq"), $("#sd"), q => [...NSE.filter(([n, , h]) => n.includes(q) || h.toLowerCase().includes(q)).map(([f, cat, h]) => ({f, cat, h})),
    ...(q && !NSE.some(([n]) => n === q) ? [{f: q, h: "add this script name as typed"}] : [])], x => { if (!o.scripts.includes(x.f)) o.scripts.push(x.f); });
  $("#src").onchange = preview;
}

(async () => {
  try { D = await api("/api/profiles"); } catch (e) { status("Cannot load: " + e.message, "err"); return; }
  $("#src").innerHTML = D.sources.map(s => `<option>${esc(s)}</option>`).join("") || `<option value="">no Source yet</option>`;
  const q = new URLSearchParams(location.search), i = D.profiles.findIndex(p => p.name === q.get("profile"));
  wire(); load(q.has("new") || !D.profiles.length ? -1 : Math.max(i, 0)); status("Loaded", "ok");
  if (q.has("profile") || q.has("new")) $("#build").scrollIntoView();
})();
