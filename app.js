(function(){
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ABBR={Alabama:'AL',Alaska:'AK',Arizona:'AZ',Arkansas:'AR',California:'CA',Colorado:'CO',Connecticut:'CT',Delaware:'DE','District of Columbia':'DC',Florida:'FL',Georgia:'GA',Hawaii:'HI',Idaho:'ID',Illinois:'IL',Indiana:'IN',Iowa:'IA',Kansas:'KS',Kentucky:'KY',Louisiana:'LA',Maine:'ME',Maryland:'MD',Massachusetts:'MA',Michigan:'MI',Minnesota:'MN',Mississippi:'MS',Missouri:'MO',Montana:'MT',Nebraska:'NE',Nevada:'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND',Ohio:'OH',Oklahoma:'OK',Oregon:'OR',Pennsylvania:'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD',Tennessee:'TN',Texas:'TX',Utah:'UT',Vermont:'VT',Virginia:'VA',Washington:'WA','West Virginia':'WV',Wisconsin:'WI',Wyoming:'WY'};
const NAME={};Object.keys(ABBR).forEach(n=>NAME[ABBR[n]]=n);
const SMALL=['VT','NH','MA','RI','CT','NJ','DE','MD','DC'];
const STEPS=['I','N','P','M','C','V'];
const FWN={};FW.forEach(f=>FWN[f.k]=f);

/* ---------- data ---------- */
const L=LAWS.map((r,i)=>{const fw={};(r[5]||'').split(' ').filter(Boolean).forEach(t=>fw[t[0]]=+t[1]);return{i,st:r[0],bill:r[1],title:r[2],cat:r[3],status:r[4],fw}});
const O=OUT.map((r,i)=>{const fw={};(r[8]||'').split(' ').filter(Boolean).forEach(t=>fw[t[0]]=+t[1]);return{i:'o'+i,st:r[0],bill:r[1],title:r[2],cat:r[3],status:r[4],note:r[5],conf:r[6],url:r[7],fw}});
const STATES=[...new Set(L.map(l=>l.st))].sort();
const byOut={};O.forEach(l=>(byOut[l.st]=byOut[l.st]||[]).push(l));
const ALL=L.concat(O);
const byAll={};ALL.forEach(l=>(byAll[l.st]=byAll[l.st]||[]).push(l));
const byState={};L.forEach(l=>(byState[l.st]=byState[l.st]||[]).push(l));
const lvlOf=(st,k)=>Math.max(0,...(byAll[st]||[]).filter(l=>l.status==='E'||l.status==='P').map(l=>l.fw[k]||0));
const cover=st=>STEPS.filter(k=>lvlOf(st,k)>0).length;
const SYM=['○','◐','●'];

/* ---------- stats ---------- */
(function(){
  const c=k=>ALL.filter(l=>l.status===k).length;
  const items=[[c('E'),'AI laws enacted in 2026 ('+L.filter(l=>l.status==='E').length+' in the report, '+O.filter(l=>l.status==='E').length+' more found'+')'],[c('P'),'passed, awaiting a governor'],[c('A'),'still alive in sessions that are open'],[c('V'),'vetoed'],[c('F'),'failed or died'],[0,'laws creating an inventory of government benefits ADS']];
  $('#stats').innerHTML=items.map(x=>`<div class="stat"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');
})();

/* ---------- map ---------- */
const status=a=>{const ls=byAll[a]||[];return ls.some(l=>l.status==='E')?'pass':ls.some(l=>l.status==='P'||l.status==='A')?'pend':ls.length?'fail':'none'};
const STAT_LABEL={pass:'Legislation passed',pend:'Pending or still in session',fail:'Failed or vetoed, none passed',none:'No bills found'};
const METRICS=[{id:'status',label:'Legislation status (passed / pending / failed / none)',val:s=>({pass:3,pend:2,fail:1,none:0})[status(s)],unit:'status'},{id:'outc',label:'Failed or vetoed bills found (count)',val:s=>(byAll[s]||[]).filter(l=>l.status==='F'||l.status==='V').length,unit:'bills'},{id:'cover',label:'Framework coverage (steps with a related law, 0 to 6)',val:s=>cover(s),max:6,unit:'of 6 steps'},
  {id:'count',label:'Total laws in the report',val:s=>(byState[s]||[]).length,unit:'laws'}]
  .concat(Object.keys(CATS).map(c=>({id:'c_'+c,label:'Topic: '+CATS[c],val:s=>(byState[s]||[]).filter(l=>l.cat===c).length,unit:'laws'})));
let metric=METRICS[0],selected=null;
$('#metric').innerHTML=METRICS.map(m=>`<option value="${m.id}">${esc(m.label)}</option>`).join('');
$('#metric').onchange=e=>{metric=METRICS.find(m=>m.id===e.target.value);drawMap()};

function bins(){
  const vals=Object.keys(NAME).map(a=>metric.val(a));const mx=Math.max(1,...vals);
  if(metric.id==='cover')return{f:v=>Math.min(5,v),n:6,labels:['0','1','2','3','4','5-6']};
  const step=Math.ceil(mx/5);
  return{f:v=>v===0?0:Math.min(5,Math.ceil(v/step)),n:6,labels:['0'].concat([1,2,3,4,5].map(i=>{const a=(i-1)*step+1,b=Math.min(i*step,mx);return a>=mx&&i>1&&a>b?'':(a===b?''+a:a+'-'+b)}))};
}
function drawMap(){
  const B=bins();
  const feats=topojson.feature(US_TOPO,US_TOPO.objects.states).features;
  const path=d3.geoPath();
  const cls=a=>metric.id==='status'?'s-'+status(a):'q'+B.f(metric.val(a));
  const aria=a=>metric.id==='status'?`${NAME[a]}: ${STAT_LABEL[status(a)]}`:`${NAME[a]}: ${metric.val(a)} ${metric.unit==='laws'?'laws':'of 6 steps'}`;
  const paths=feats.map(f=>{const a=ABBR[f.properties.name];if(!a)return'';return `<path class="st ${cls(a)}${a===selected?' sel':''}" d="${path(f)}" tabindex="0" role="button" data-s="${a}" aria-label="${esc(aria(a))}"></path>`}).join('');
  const boxes=SMALL.map((a,i)=>{const x=975+(i%2)*46,y=250+Math.floor(i/2)*44,c=cls(a);
    return `<g class="stbox"><rect class="st ${c}${a===selected?' sel':''}" x="${x}" y="${y}" width="40" height="34" rx="6" tabindex="0" role="button" data-s="${a}" aria-label="${esc(aria(a))}"></rect><text class="" x="${x+20}" y="${y+22}" text-anchor="middle">${a}</text></g>`}).join('');
  const adj={FL:[12,8],LA:[-12,0],MI:[10,12]};
  const labels=feats.map(f=>{const a=ABBR[f.properties.name];if(!a||SMALL.includes(a))return'';const c=path.centroid(f);if(isNaN(c[0]))return'';const o=adj[a]||[0,0];
    return `<text class="lb " x="${c[0]+o[0]}" y="${c[1]+o[1]+4}" text-anchor="middle">${a}</text>`}).join('');
  const cnt=k=>Object.keys(NAME).filter(a=>status(a)===k).length;
  const leg=metric.id==='status'?['pass','pend','fail','none'].map(k=>`<li><i class="sw s-${k}"></i>${STAT_LABEL[k]} (${cnt(k)})</li>`).join(''):B.labels.map((t,i)=>t===''&&i>0?'':`<li><i class="sw q${i}" style="background:var(--q${i})"></i>${esc(t)}</li>`).join('');
  $('#mapHost').innerHTML=`<div class="mapwrap"><svg viewBox="0 0 1075 610" role="group" aria-label="Map of the United States colored by ${esc(metric.label)}">${paths}${boxes}${labels}</svg><div class="maptip" id="maptip" hidden></div></div>
  <ul class="legend">${metric.id==='status'?'':`<li><b>${metric.id==='cover'?'Steps covered:':'Laws:'}</b></li>`}${leg}</ul>
  <p class="small">${metric.id==='status'?'Green: at least one 2026 law enacted. Yellow: no AI law passed yet, but bills are awaiting a governor or are still alive in a legislature that is in session. Red: no AI law passed and every bill found failed, was vetoed or died. A state with both passed and failed bills shows green; open the state for the full list. Gray: no AI bills found (Montana, Nevada and Texas had no regular 2026 session). ':''}${metric.id==='cover'?'Counts how many of the six framework steps (inventory, notice, pre-deployment assessment, monitoring, oversight body, vendor duties) have at least a loose analogue among that state\'s 2026 laws. Gray states had no entry in the report. ':''}Hover a state for a summary and click it for its laws. States without 2026 entries (such as Texas) are not necessarily without AI laws.</p>`;
  wireMap();
}
function tip(a){
  const ls=byState[a]||[];
  let h=`<b>${esc(NAME[a])}</b><br>`;
  if(metric.id==='status')h+=STAT_LABEL[status(a)]+'<br>';
  const os=byAll[a]||[];const nf=os.filter(l=>l.status==='F'||l.status==='V').length;
  if(!ls.length)return h+(os.length?`${os.length} AI bill${os.length>1?'s':''} found: ${nf} failed or vetoed`:'No AI bills found in the sources')+'<br><small>Click for details</small>';
  return h+`${ls.length} law${ls.length>1?'s':''} · ${cover(a)} of 6 framework steps${nf?`<br>${nf} failed or vetoed`:''}<br><small>Click for details</small>`;
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
function panel(a){
  const ls=byState[a]||[],host=$('#statePanel');
  const os=(byOut[a]||[]).slice().sort((x,y)=>'EPAVF'.indexOf(x.status)-'EPAVF'.indexOf(y.status));
  const outHtml=os.length?`<h4>Other AI bills found in LegiScan (${os.length})</h4><ul>${os.slice(0,40).map(l=>`<li><b>${esc(l.bill)}</b>: ${esc(l.title)} <span class="pill ${l.status}">${SL[l.status]}</span> <span class="small">${esc(l.note)}. <a href="${esc(l.url)}" target="_blank" rel="noopener">LegiScan</a></span> ${tagStr(l)}</li>`).join('')}</ul>${os.length>40?`<p class="small">${os.length-40} more are in the table below.</p>`:''}`:''
  if(!ls.length){host.innerHTML=`<h3>${esc(NAME[a])}</h3><p>${os.length?'No AI law from the report. Other bills found are below.':'No AI bills found in the report or the LegiScan files. That is not proof the state has none.'} See the <a href="#chart">framework chart</a> for benchmark material from the policy paper${BENCH[a]?' (this state has some)':''}.</p>${outHtml}`;return}
  const cats={};ls.forEach(l=>cats[l.cat]=(cats[l.cat]||0)+1);
  const mini=STEPS.map(k=>`<span title="${esc(FWN[k].d)}">${SYM[lvlOf(a,k)]} ${esc(FWN[k].n)}</span>`).join('');
  host.innerHTML=`<h3>${esc(NAME[a])}</h3>
  <p>${ls.length} law${ls.length>1?'s':''} in 2026: ${Object.keys(cats).map(c=>`${cats[c]} ${esc(CATS[c].toLowerCase())}`).join(', ')}.</p>
  <div class="mini" aria-label="Framework coverage">${mini}</div>
  <ul>${ls.map(l=>`<li><b>${esc(l.bill)}</b>: ${esc(l.title)} ${l.status==='P'?'<span class="pill P">awaiting signature</span>':''} ${tagStr(l)}</li>`).join('')}</ul>
  ${outHtml}
  ${ENF[a]?`<p class="small"><b>Enforcement:</b> ${esc(ENF[a].t)}</p>`:''}
  <p><a href="#chart" data-add="${a}">Add ${esc(NAME[a])} to the framework chart</a></p>`;
  host.querySelector('[data-add]').onclick=()=>{if(!cols.includes(a))cols.push(a);drawChart()};
  host.scrollIntoView({behavior:'smooth',block:'nearest'});
}
const tagStr=l=>Object.keys(l.fw).map(k=>`<span class="pill" title="${esc(FWN[k].n)}: ${l.fw[k]===2?'close':'loose'} analogue">${SYM[l.fw[k]]} ${esc(FWN[k].n)}</span>`).join(' ');

/* ---------- framework chart ---------- */
let cols=['TX','NY','CA','FED'];
const colName=c=>c==='FED'?'Federal':NAME[c];
function cell(c,k){
  const b=(BENCH[c]&&BENCH[c].cells[k])||null;
  const laws=c==='FED'?[]:(byAll[c]||[]).filter(l=>l.fw[k]&&(l.status==='E'||l.status==='P')).sort((a,b)=>b.fw[k]-a.fw[k]);
  let lvl=Math.max(b?b.lvl:0,...laws.map(l=>l.fw[k]),0);
  let enf=null;
  if(k==='E'&&c!=='FED'&&ENF[c]){enf=ENF[c];lvl=Math.max(lvl,enf.lvl)}
  if(c==='CO'&&k==='P'&&b)lvl=0;
  return{lvl,b,laws,enf};
}
function cellHtml(c,k,x){
  const short=[];
  if(x.b&&x.b.lvl>0)short.push(`${c==='FED'?'M-25-21':c==='NY'&&k!=='N'?'LOADinG Act':c==='TX'?'TRAIGA/AG':'Paper'}`);
  if(x.b&&x.b.lvl===0)short.push('Rolled back (SB 189)');
  x.laws.slice(0,2).forEach(l=>short.push(l.bill));
  if(x.laws.length>2)short.push(`+${x.laws.length-2} more`);
  if(x.enf&&!x.b)short.push(x.enf.lvl===2?'Penalty or private right':'Consumer-protection route');
  if(x.b&&x.b.src==='bg')short.push('<span class="bgtag">verify</span>');
  const has=x.lvl>0||short.length;
  return `<td class="f${x.lvl}"><button class="cell c${x.lvl}" data-c="${c}" data-k="${k}" aria-label="${esc(colName(c))}, ${esc(FWN[k].n)}: ${['none found','loose analogue','close analogue'][x.lvl]}"><span class="sym">${SYM[x.lvl]}</span>${has?short.join(', '):'<span class="more">None found</span>'}</button></td>`;
}
function drawChart(){
  const bar=$('#colBar');
  const avail=['FED','TX','CO'].filter(c=>!STATES.includes(c)||c==='CO').concat(STATES).filter((c,i,a)=>a.indexOf(c)===i);
  bar.innerHTML=`<div class="field"><label for="addCol">Add a column</label><select id="addCol"><option value="">Choose a state</option>${avail.filter(c=>!cols.includes(c)).sort((a,b)=>colName(a).localeCompare(colName(b))).map(c=>`<option value="${c}">${esc(colName(c))}</option>`).join('')}</select></div>
  <button id="colWhite">Whiteboard set (TX, NY, CA, Fed)</button><button id="colAll">All 30 states + Fed + TX</button><button id="colTop">Most framework coverage</button>`;
  $('#addCol').onchange=e=>{if(e.target.value){cols.push(e.target.value);drawChart()}};
  $('#colWhite').onclick=()=>{cols=['TX','NY','CA','FED'];drawChart()};
  $('#colAll').onclick=()=>{cols=['FED','TX'].concat(STATES.filter(s=>s!=='TX'));drawChart()};
  $('#colTop').onclick=()=>{cols=['FED'].concat(STATES.slice().sort((a,b)=>cover(b)-cover(a)||(byState[b].length-byState[a].length)).slice(0,7));drawChart()};
  const head=`<tr><th scope="col">Framework step</th>${cols.map(c=>`<th scope="col">${esc(colName(c))}${c==='FED'?'':`<button class="xbtn" data-x="${c}" aria-label="Remove ${esc(colName(c))}">x</button>`}${BENCH[c]&&c!=='FED'&&BENCH[c].name!==colName(c)?`<br><small class="small">${esc(BENCH[c].name)}</small>`:''}</th>`).join('')}</tr>`;
  const rows=FW.map(f=>`<tr><th scope="row" class="rowh"><b>${esc(f.n)}</b><small>${esc(f.s)}</small></th>${cols.map(c=>cellHtml(c,f.k,cell(c,f.k))).join('')}</tr>`).join('');
  const tot=`<tr><th scope="row" class="rowh"><b>Enacted or pending AI laws</b><small>All topics, report plus extras</small></th>${cols.map(c=>`<td style="text-align:center">${c==='FED'?'n/a':(byAll[c]||[]).filter(l=>l.status==='E'||l.status==='P').length}</td>`).join('')}</tr>`;
  $('#chartHost').innerHTML=`<table class="fwtable"><thead>${head}</thead><tbody>${rows}${tot}</tbody></table>`;
  document.querySelectorAll('.xbtn').forEach(b=>b.onclick=()=>{cols=cols.filter(c=>c!==b.dataset.x);drawChart()});
  document.querySelectorAll('.cell').forEach(b=>b.onclick=()=>openCell(b.dataset.c,b.dataset.k));
}
function openCell(c,k){
  const x=cell(c,k),f=FWN[k];
  let h=`<h3>${esc(colName(c))}: ${esc(f.n)}</h3><p class="small">${esc(f.d)}</p><p><b>${SYM[x.lvl]} ${['Nothing found in the sources','Loose analogue','Close analogue'][x.lvl]}</b></p>`;
  if(x.b)h+=`<p>${esc(x.b.t)} <span class="pill">${x.b.src==='paper'?'Source: policy paper':'Background knowledge, verify'}</span></p>`;
  if(x.enf)h+=`<p>${esc(x.enf.t)}</p>`;
  if(x.laws.length)h+=`<ul>${x.laws.map(l=>`<li><b>${esc(l.bill)}</b>: ${esc(l.title)} (${l.fw[k]===2?'close':'loose'} analogue${l.status==='P'?', awaiting signature':''})</li>`).join('')}</ul>`;
  if(!x.b&&!x.laws.length&&!x.enf)h+=`<p>No 2026 law in the report maps to this step for ${esc(colName(c))}${c==='TX'?' (Texas has no entry in the report)':''}.</p>`;
  if(k==='I'&&c!=='FED')h+=`<p class="small">No 2026 law creates an inventory of ADS used by benefits agencies. Entries tagged here are registries or public disclosures of a different kind.</p>`;
  $('#dlgBody').innerHTML=h;$('#dlg').showModal();
}

/* ---------- laws table ---------- */
$('#fs').innerHTML='<option value="">All states</option>'+STATES.map(s=>`<option value="${s}">${esc(NAME[s])}</option>`).join('');
$('#fc').innerHTML='<option value="">All topics</option>'+Object.keys(CATS).map(c=>`<option value="${c}">${esc(CATS[c])}</option>`).join('');
$('#fst').innerHTML='<option value="">All outcomes</option><option value="E">Enacted</option><option value="P">Awaiting signature</option><option value="V">Vetoed</option><option value="A">Still in session</option><option value="F">Failed or died</option>';
$('#ff').innerHTML='<option value="">Any / none</option>'+STEPS.map(k=>`<option value="${k}">${esc(FWN[k].n)}</option>`).join('');
const SL={E:'Enacted',P:'Awaiting signature',A:'Still in session',V:'Vetoed',F:'Failed or died'};
let rows=ALL,shown=100;
function drawLaws(reset){
  if(reset!==false)shown=100;
  const q=$('#q').value.toLowerCase(),s=$('#fs').value,c=$('#fc').value,f=$('#ff').value,u=$('#fst').value;
  rows=ALL.filter(l=>(!u||l.status===u)&&(!s||l.st===s)&&(!c||l.cat===c)&&(!f||l.fw[f])&&(!q||(l.bill+' '+l.title+' '+NAME[l.st]+' '+CATS[l.cat]).toLowerCase().includes(q)));
  $('#lawCount').textContent=`${Math.min(shown,rows.length)} shown of ${rows.length} matching (${ALL.length} total)`;
  $('#lawTable tbody').innerHTML=rows.slice(0,shown).map(l=>`<tr><td>${esc(NAME[l.st])}</td><td>${esc(l.bill)}</td><td>${esc(l.title)}</td><td>${esc(CATS[l.cat])}</td><td><span class="pill ${l.status}">${SL[l.status]}</span></td><td>${l.note?`${tagStr(l)} <span class="small">${esc(l.note)}. <a href="${esc(l.url)}" target="_blank" rel="noopener">LegiScan</a></span>`:(tagStr(l)||'<span class="small">None</span>')}</td></tr>`).join('')||'<tr><td colspan="6">No laws match.</td></tr>';
}
['#q','#fs','#fc','#ff','#fst'].forEach(id=>$(id).addEventListener('input',()=>drawLaws()));
$('#more').onclick=()=>{shown+=200;drawLaws(false)};
$('#csv').onclick=()=>{
  const q=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const lines=[['state','bill','title','topic','status','inventory','notice','pre_deployment','monitoring','commission','vendor','note','source']].concat(rows.map(l=>[NAME[l.st],l.bill,l.title,CATS[l.cat],SL[l.status]].concat(STEPS.map(k=>['none','loose','close'][l.fw[k]||0])).concat([l.note||'',l.url||''])));
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.map(r=>r.map(q).join(',')).join('\n')],{type:'text/csv'}));a.download='state-ai-laws-2026.csv';a.click();
};

/* ---------- nav ---------- */
$('#menuBtn').onclick=()=>{const n=$('#nav');const o=n.classList.toggle('open');$('#menuBtn').setAttribute('aria-expanded',o)};
$('#nav').addEventListener('click',()=>$('#nav').classList.remove('open'));
const secs=['overview','map','chart','laws','about'].map(id=>document.getElementById(id));
addEventListener('scroll',()=>{let cur=secs[0].id;secs.forEach(s=>{if(s.getBoundingClientRect().top<120)cur=s.id});document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+cur))},{passive:true});

drawMap();drawChart();drawLaws();
window.__check={laws:L.length,out:O.length,states:STATES.length};
})();
