(function(){
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ABBR={Alabama:'AL',Alaska:'AK',Arizona:'AZ',Arkansas:'AR',California:'CA',Colorado:'CO',Connecticut:'CT',Delaware:'DE','District of Columbia':'DC',Florida:'FL',Georgia:'GA',Hawaii:'HI',Idaho:'ID',Illinois:'IL',Indiana:'IN',Iowa:'IA',Kansas:'KS',Kentucky:'KY',Louisiana:'LA',Maine:'ME',Maryland:'MD',Massachusetts:'MA',Michigan:'MI',Minnesota:'MN',Mississippi:'MS',Missouri:'MO',Montana:'MT',Nebraska:'NE',Nevada:'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND',Ohio:'OH',Oklahoma:'OK',Oregon:'OR',Pennsylvania:'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD',Tennessee:'TN',Texas:'TX',Utah:'UT',Vermont:'VT',Virginia:'VA',Washington:'WA','West Virginia':'WV',Wisconsin:'WI',Wyoming:'WY'};
const NAME={FED:'Federal'};Object.keys(ABBR).forEach(n=>NAME[ABBR[n]]=n);
const SMALL=['VT','NH','MA','RI','CT','NJ','DE','MD','DC'];

const FWP=[
 {k:'I',n:'Public inventory',s:'Step 1',d:'Agencies publish a machine-readable, regularly updated inventory of every automated decision system used in a covered decision (name, purpose, vendor, deployment date, last impact assessment, waivers).'},
 {k:'N',n:'Notice & explanation',s:'Step 2',d:'Each notice says whether an ADS was used, names it, and gives a plain-language explanation of any adverse decision, with a way to correct data and request review.'},
 {k:'A',n:'Impact assessment, testing & monitoring',s:'Step 3',d:'Published assessment before use (accuracy, error rates by protected group, proxy testing, edge cases), ongoing monitoring, re-testing when the model or vendor changes, and discontinuation of discriminatory systems.'},
 {k:'H',n:'Human review & appeal',s:'Step 4',d:'No adverse decision rests solely on automated output; timely, meaningful human review and an appeal, preserving existing fair-hearing rights.'},
 {k:'V',n:'Vendor & developer duties',s:'Step 5',d:'Contracts require documentation of intended uses, limits, validation and subgroup performance, cooperation with audits, tiered disclosure, and no trade-secret bar to applicant disclosure.'},
 {k:'O',n:'Oversight body & enforcement',s:'Design choice',d:'An independent office or commission, attorney-general enforcement, a private right of action, or none; penalties and cure periods.'}
];
const FWN={};FWP.forEach(f=>FWN[f.k]=f);
const SL={E:'Enacted',R:'Repealed before effect',A:'Still in session',V:'Vetoed',F:'Failed or died'};
const SC={ben:'Names benefits or eligibility',gov:'Government AI use (general)'};
const SYM=['○','◐','●'];

/* ---------- data ---------- */
const D=POL.map((r,i)=>{const fw={};(r[6]||'').split(' ').filter(Boolean).forEach(t=>fw[t[0]]=+t[1]);
  return{i,st:r[0],bill:r[1],title:r[2],year:r[3],status:r[4],scope:r[5],fw,desc:r[7],url:r[8],conf:r[9]}});
const STATES=[...new Set(D.filter(d=>d.st!=='FED').map(d=>d.st))].sort();
const by={};D.forEach(d=>(by[d.st]=by[d.st]||[]).push(d));
const enacted=d=>d.status==='E';
const lvlOf=(st,k)=>Math.max(0,...(by[st]||[]).filter(d=>enacted(d)).map(d=>d.fw[k]||0));
const cover=st=>FWP.filter(f=>lvlOf(st,f.k)>0).length;
const tagStr=l=>Object.keys(l.fw).filter(k=>l.fw[k]>0).map(k=>`<span class="pill" title="${esc(FWN[k].n)}: ${l.fw[k]===2?'close':'loose'} match">${SYM[l.fw[k]]} ${esc(FWN[k].n)}</span>`).join(' ');
const confTxt={H:'High',M:'Medium',L:'Low'};

/* ---------- stats ---------- */
(function(){
  const st=D.filter(d=>d.st!=='FED');
  const e=st.filter(enacted);
  const items=[[new Set(e.map(d=>d.st)).size,'states with an enacted law on government AI use'],
    [new Set(e.filter(d=>d.scope==='ben').map(d=>d.st)).size,'states with an enacted law that names benefits or Medicaid'],
    [e.filter(d=>d.fw.I===2).length,'enacted state laws creating an agency AI inventory'],
    [e.filter(d=>d.fw.N>=1).length,'enacted laws with any notice duty'],
    [st.filter(d=>d.status==='A').length,'bills still alive'],
    [st.filter(d=>d.status==='F').length,'bills failed or died']];
  $('#stats').innerHTML=items.map(x=>`<div class="stat"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');
})();

/* ---------- map ---------- */
const stat=(a,f)=>{const ls=(by[a]||[]).filter(f||(()=>true));
  return ls.some(enacted)?'pass':ls.some(d=>d.status==='A')?'pend':ls.length?'fail':'none'};
const STAT_LABEL={pass:'Enacted law',pend:'Bill still alive, none enacted',fail:'Bills failed, repealed or vetoed; none in force',none:'None found'};
const METRICS=[
 {id:'status',label:'Government AI law status (all entries)',kind:'status',f:null},
 {id:'ben',label:'Benefits-specific status (names Medicaid, SNAP or eligibility)',kind:'status',f:d=>d.scope==='ben'},
 {id:'cover',label:'Framework parts covered by enacted laws (0 to 6)',kind:'num',val:a=>cover(a)}];
let metric=METRICS[0],selected=null;
$('#metric').innerHTML=METRICS.map(m=>`<option value="${m.id}">${esc(m.label)}</option>`).join('');
$('#metric').onchange=e=>{metric=METRICS.find(m=>m.id===e.target.value);drawMap()};
function cls(a){return metric.kind==='status'?'s-'+stat(a,metric.f):'q'+Math.min(5,metric.val(a))}
function drawMap(){
  const feats=topojson.feature(US_TOPO,US_TOPO.objects.states).features,path=d3.geoPath();
  const lab=a=>metric.kind==='status'?`${NAME[a]}: ${STAT_LABEL[stat(a,metric.f)]}`:`${NAME[a]}: ${metric.val(a)} of 6 framework parts`;
  const paths=feats.map(f=>{const a=ABBR[f.properties.name];if(!a)return'';return `<path class="st ${cls(a)}${a===selected?' sel':''}" d="${path(f)}" tabindex="0" role="button" data-s="${a}" aria-label="${esc(lab(a))}"></path>`}).join('');
  const boxes=SMALL.map((a,i)=>{const x=975+(i%2)*46,y=250+Math.floor(i/2)*44;
    return `<g class="stbox"><rect class="st ${cls(a)}${a===selected?' sel':''}" x="${x}" y="${y}" width="40" height="34" rx="6" tabindex="0" role="button" data-s="${a}" aria-label="${esc(lab(a))}"></rect><text x="${x+20}" y="${y+22}" text-anchor="middle">${a}</text></g>`}).join('');
  const adj={FL:[12,8],LA:[-12,0],MI:[10,12]};
  const labels=feats.map(f=>{const a=ABBR[f.properties.name];if(!a||SMALL.includes(a))return'';const c=path.centroid(f);if(isNaN(c[0]))return'';const o=adj[a]||[0,0];
    return `<text class="lb" x="${c[0]+o[0]}" y="${c[1]+o[1]+4}" text-anchor="middle">${a}</text>`}).join('');
  let leg;
  if(metric.kind==='status'){const cnt=k=>Object.keys(NAME).filter(a=>a!=='FED'&&stat(a,metric.f)===k).length;
    leg=['pass','pend','fail','none'].map(k=>`<li><i class="sw s-${k}"></i>${STAT_LABEL[k]} (${cnt(k)})</li>`).join('')}
  else leg=[0,1,2,3,4,5].map(i=>`<li><i class="sw q${i}" style="background:var(--q${i})"></i>${i}</li>`).join('');
  $('#mapHost').innerHTML=`<div class="mapwrap"><svg viewBox="0 0 1075 610" role="group" aria-label="Map of the United States colored by ${esc(metric.label)}">${paths}${boxes}${labels}</svg><div class="maptip" id="maptip" hidden></div></div>
  <ul class="legend">${leg}</ul>
  <p class="small">${metric.kind==='status'?'Green: at least one enacted law (any year) regulating government use of AI or automated decision systems. Yellow: no enacted law, but a bill is still alive in a legislature that is in session. Red: no law in force; bills failed, died, or were repealed before taking effect. Gray: nothing found in the sources checked. ':'Counts which of the six framework parts have at least a loose match in an enacted law. '}Hover a state for a summary and click it for details. Federal rules appear in the chart.</p>`;
  wireMap();
}
function tip(a){
  const ls=by[a]||[];let h=`<b>${esc(NAME[a])}</b><br>`;
  if(!ls.length)return h+'No government AI law or bill found<br><small>Click for details</small>';
  const e=ls.filter(enacted).length;
  return h+`${e} enacted, ${ls.filter(d=>d.status==='A').length} alive, ${ls.filter(d=>d.status==='F'||d.status==='R'||d.status==='V').length} failed or repealed<br><small>Click for details</small>`;
}
function wireMap(){
  const t=$('#maptip'),wrap=t.parentElement;
  wrap.querySelectorAll('[data-s]').forEach(el=>{
    const show=(x,y)=>{t.innerHTML=tip(el.dataset.s);t.hidden=false;const r=wrap.getBoundingClientRect();let l=x-r.left+14;if(l>r.width-210)l=x-r.left-214;t.style.left=l+'px';t.style.top=(y-r.top+14)+'px'};
    el.addEventListener('pointermove',e=>show(e.clientX,e.clientY));
    el.addEventListener('pointerleave',()=>t.hidden=true);
    el.addEventListener('click',()=>pick(el.dataset.s));
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pick(el.dataset.s)}});
  });
}
function pick(a){selected=a;drawMap();panel(a)}
const order='EAVRF';
const item=l=>`<li><b>${esc(l.bill)}</b> (${l.year}): ${esc(l.title)} <span class="pill ${l.status}">${SL[l.status]}</span> ${tagStr(l)}<br><span class="small">${esc(l.desc)} Confidence: ${confTxt[l.conf]}. ${l.url?`<a href="${esc(l.url)}" target="_blank" rel="noopener">Source</a>`:''}</span></li>`;
function panel(a){
  const ls=(by[a]||[]).slice().sort((x,y)=>order.indexOf(x.status)-order.indexOf(y.status)),host=$('#statePanel');
  if(!ls.length){host.innerHTML=`<h3>${esc(NAME[a])}</h3><p>No law or bill on government use of AI or automated decision systems turned up in the sources checked. That is not proof none exists. Check the state legislature's own site.</p>`;return}
  const mini=FWP.map(f=>`<span title="${esc(f.d)}">${SYM[lvlOf(a,f.k)]} ${esc(f.n)}</span>`).join('');
  host.innerHTML=`<h3>${esc(NAME[a])}</h3>
  <p>${ls.filter(enacted).length} enacted, ${ls.filter(d=>d.status==='A').length} still alive, ${ls.filter(d=>d.status==='F'||d.status==='V'||d.status==='R').length} failed or repealed. Framework parts covered by enacted laws:</p>
  <div class="mini">${mini}</div><ul>${ls.map(item).join('')}</ul>
  <p><a href="#chart" id="addcol">Add ${esc(NAME[a])} to the framework chart</a></p>`;
  $('#addcol').onclick=()=>{if(!cols.includes(a))cols.push(a);drawChart()};
  host.scrollIntoView({behavior:'smooth',block:'nearest'});
}

/* ---------- framework chart ---------- */
const DEFAULT=['TX','NY','CA','CO','MD','OH','FED'];
let cols=DEFAULT.slice();
function cell(c,k){
  const ls=(by[c]||[]).filter(d=>k in d.fw);
  const en=ls.filter(enacted),rb=ls.filter(d=>d.status==='R'||(enacted(d)&&d.fw[k]===0));
  const lvl=Math.max(0,...en.map(d=>d.fw[k]));
  const other=ls.filter(d=>!enacted(d)&&d.fw[k]>0&&d.status!=='R');
  return{lvl,en:en.filter(d=>d.fw[k]>0),rb:rb.filter(d=>d.fw[k]>0||d.fw[k]===0),other,all:ls};
}
function cellHtml(c,k){
  const x=cell(c,k);let sym=SYM[x.lvl],c2='c'+x.lvl,txt=[];
  if(x.lvl===0&&x.rb.length){sym='✕';c2='c0'}
  x.en.slice(0,2).forEach(d=>txt.push(esc(d.bill.split(' (')[0])));
  if(x.en.length>2)txt.push(`+${x.en.length-2} more`);
  if(!x.en.length&&x.rb.length)txt.push(`Rolled back: ${esc(x.rb[0].bill.split(' (')[0])}`);
  if(!x.en.length&&!x.rb.length&&x.other.length){const o=x.other[0];txt.push(`${o.status==='A'?'Bill alive':'Bill failed'}: ${esc(o.bill)}`)}
  const low=x.en.length&&x.en.every(d=>d.conf==='L')?' <span class="bgtag">low confidence</span>':'';
  return `<td class="f${x.lvl}"><button class="cell ${c2}" data-c="${c}" data-k="${k}" aria-label="${esc(NAME[c])}, ${esc(FWN[k].n)}: ${x.lvl===2?'close match':x.lvl===1?'partial match':x.rb.length?'rolled back':'none found'}"><span class="sym">${sym}</span>${txt.length?txt.join(', '):'<span class="more">None found</span>'}${low}</button></td>`;
}
function drawChart(){
  const avail=['FED'].concat(STATES).filter(c=>!cols.includes(c));
  $('#colBar').innerHTML=`<div class="field"><label for="addCol">Add a column</label><select id="addCol"><option value="">Choose a state</option>${avail.map(c=>`<option value="${c}">${esc(NAME[c])}</option>`).join('')}</select></div>
  <button id="colWhite">Default set (TX, NY, CA, CO, MD, OH, Federal)</button><button id="colEn">States with an enacted law</button><button id="colBen">Names benefits</button>`;
  $('#addCol').onchange=e=>{if(e.target.value){cols.push(e.target.value);drawChart()}};
  $('#colWhite').onclick=()=>{cols=DEFAULT.slice();drawChart()};
  $('#colEn').onclick=()=>{cols=['FED'].concat(STATES.filter(s=>(by[s]||[]).some(enacted)));drawChart()};
  $('#colBen').onclick=()=>{cols=['FED'].concat(STATES.filter(s=>(by[s]||[]).some(d=>d.scope==='ben'&&(enacted(d)||d.status==='A'))));drawChart()};
  const head=`<tr><th scope="col">Framework part</th>${cols.map(c=>`<th scope="col">${esc(NAME[c])}${c==='FED'?'':`<button class="xbtn" data-x="${c}" aria-label="Remove ${esc(NAME[c])}">x</button>`}</th>`).join('')}</tr>`;
  const rows=FWP.map(f=>`<tr><th scope="row" class="rowh"><b>${esc(f.n)}</b><small>${esc(f.s)}</small></th>${cols.map(c=>cellHtml(c,f.k)).join('')}</tr>`).join('');
  const tot=`<tr><th scope="row" class="rowh"><b>Entries found</b><small>laws and bills</small></th>${cols.map(c=>`<td style="text-align:center">${(by[c]||[]).length}</td>`).join('')}</tr>`;
  $('#chartHost').innerHTML=`<table class="fwtable"><thead>${head}</thead><tbody>${rows}${tot}</tbody></table>`;
  document.querySelectorAll('.xbtn').forEach(b=>b.onclick=()=>{cols=cols.filter(c=>c!==b.dataset.x);drawChart()});
  document.querySelectorAll('.cell').forEach(b=>b.onclick=()=>openCell(b.dataset.c,b.dataset.k));
}
function openCell(c,k){
  const x=cell(c,k),f=FWN[k];
  let h=`<h3>${esc(NAME[c])}: ${esc(f.n)}</h3><p class="small">${esc(f.d)}</p><p><b>${x.lvl===2?'● Close match':x.lvl===1?'◐ Partial or loose match':x.rb.length?'✕ Rolled back':'○ None found'}</b></p>`;
  const list=x.all.slice().sort((a,b)=>order.indexOf(a.status)-order.indexOf(b.status));
  if(list.length)h+=`<ul>${list.map(item).join('')}</ul>`;
  else h+=`<p>No law or bill in the sources checked${c==='TX'?' touches this part in a way I could find':''}.</p>`;
  const others=(by[c]||[]).filter(d=>!(k in d.fw));
  if(others.length&&!list.length)h+=`<p class="small">${esc(NAME[c])} has other entries in the table, but none mapped to this part.</p>`;
  $('#dlgBody').innerHTML=h;$('#dlg').showModal();
}

/* ---------- table ---------- */
$('#fs').innerHTML='<option value="">All states</option>'+['FED'].concat(STATES).map(s=>`<option value="${s}">${esc(NAME[s])}</option>`).join('');
$('#fst').innerHTML='<option value="">All outcomes</option>'+Object.keys(SL).map(k=>`<option value="${k}">${SL[k]}</option>`).join('');
$('#fsc').innerHTML='<option value="">All</option>'+Object.keys(SC).map(k=>`<option value="${k}">${SC[k]}</option>`).join('');
$('#ff').innerHTML='<option value="">Any / none</option>'+FWP.map(f=>`<option value="${f.k}">${esc(f.n)}</option>`).join('');
let rows=D;
function drawTable(){
  const q=$('#q').value.toLowerCase(),s=$('#fs').value,u=$('#fst').value,c=$('#fsc').value,f=$('#ff').value;
  rows=D.filter(d=>(!u||d.status===u)&&(!s||d.st===s)&&(!c||d.scope===c)&&(!f||d.fw[f]>0)&&(!q||(d.bill+' '+d.title+' '+NAME[d.st]+' '+d.desc).toLowerCase().includes(q)));
  rows=rows.slice().sort((a,b)=>order.indexOf(a.status)-order.indexOf(b.status)||a.st.localeCompare(b.st));
  $('#lawCount').textContent=`${rows.length} of ${D.length} entries`;
  $('#lawTable tbody').innerHTML=rows.map(l=>`<tr><td>${esc(NAME[l.st])}</td><td>${l.url?`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.bill)}</a>`:esc(l.bill)}</td><td>${esc(l.title)}<br><span class="small">${esc(l.desc)}</span></td><td>${l.year}</td><td><span class="pill ${l.status}">${SL[l.status]}</span><br><span class="small">${SC[l.scope]}</span></td><td>${tagStr(l)||'<span class="small">None</span>'}</td><td>${confTxt[l.conf]}</td></tr>`).join('')||'<tr><td colspan="7">No entries match.</td></tr>';
}
['#q','#fs','#fst','#fsc','#ff'].forEach(id=>$(id).addEventListener('input',drawTable));
$('#csv').onclick=()=>{
  const q=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const lines=[['jurisdiction','bill','title','year','outcome','scope','inventory','notice','assessment','human_review','vendor','oversight','description','confidence','source']].concat(rows.map(l=>[NAME[l.st],l.bill,l.title,l.year,SL[l.status],SC[l.scope]].concat(FWP.map(f=>l.fw[f.k]===undefined?'none':['rolled back','loose','close'][l.fw[f.k]])).concat([l.desc,confTxt[l.conf],l.url||''])));
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.map(r=>r.map(q).join(',')).join('\n')],{type:'text/csv'}));a.download='gov-ai-benefits-policies.csv';a.click();
};

/* ---------- nav ---------- */
$('#menuBtn').onclick=()=>{const n=$('#nav');const o=n.classList.toggle('open');$('#menuBtn').setAttribute('aria-expanded',o)};
$('#nav').addEventListener('click',()=>$('#nav').classList.remove('open'));
const secs=['overview','map','chart','laws','about'].map(id=>document.getElementById(id));
addEventListener('scroll',()=>{let cur=secs[0].id;secs.forEach(s=>{if(s.getBoundingClientRect().top<120)cur=s.id});document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+cur))},{passive:true});

drawMap();drawChart();drawTable();
window.__check={entries:D.length,states:STATES.length};
})();
