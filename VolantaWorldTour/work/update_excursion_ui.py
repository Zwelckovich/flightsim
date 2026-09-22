from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'excursions-ui.js'
s=p.read_text(encoding='utf8')
def replace(old,new):
    global s
    assert old in s, old[:110]
    s=s.replace(old,new)
start=s.index('state.xDone=new Set();')
end=s.index('function renderCoverage()',start)
s=s[:start]+'''const retiredIDs=new Set((X.retiredLegs||[]).map(l=>l.id));
state.xDone=new Set();state.retiredXDone=new Set();
function restoreXProgress(saved){state.xDone=new Set((saved.xDone||[]).filter(id=>xIDs.has(id)));state.retiredXDone=new Set([...(saved.xDone||[]),...(saved.retiredXDone||[])].filter(id=>retiredIDs.has(id)))}
try{restoreXProgress(JSON.parse(localStorage.getItem(storageKey)||'{}'))}catch(e){storageOK=false}
function saveAll(){try{localStorage.setItem(storageKey,JSON.stringify({done:[...state.done],xDone:[...state.xDone],retiredXDone:[...state.retiredXDone]}))}catch(e){storageOK=false}renderProgress();renderXProgress();renderJourney();for(const box of document.querySelectorAll('[data-xdone]'))box.checked=state.xDone.has(box.dataset.xdone)}
function renderXProgress(){if($('#xProgress'))$('#xProgress').textContent=`${state.xDone.size} / ${XL.length} Ausflugs-Legs lokal geflogen · keine automatische Volanta-Synchronisierung`}
function renderFleet(){
 $('#fleetStrip').innerHTML=[['HAUPTROUTE','Fenix A320',`${D.legs.length} Legs · CFM Sharklets · deine großen Verbindungen`],['HELIKOPTER','Airbus H160',`${X.excursions.filter(e=>e.profile==='H160').length} Ausflüge · Heliports, Küsten und Gebirgstäler`],['EXPEDITION & KURZE PISTEN','Twin Otter',`${X.excursions.filter(e=>e.profile==='DHC6').length} Ausflüge · St. Barth, Montserrat, Antarktis, Tuvalu`]].map(t=>`<article class="fleet-tile"><div class="kicker">${t[0]}</div><b>${t[1]}</b><p>${t[2]}</p></article>`).join('');
 $('#fleetLogistics').textContent=X.logistics;
}
''' + s[end:]
replace('Zusätzliche Kategorien mit Regionalflugzeug, Kleinflugzeug oder Helikopter.', 'Zusätzliche Kategorien mit vier Twin-Otter- und zwölf H160-Ausflügen.')
replace('<p>${esc(e.briefing)}</p><div class="xlegs">', '<p>${esc(e.briefing)}</p>${e.experience?`<p><strong>Anflug erleben:</strong> ${esc(e.experience)}</p><p class="small">${esc(e.timing)}</p>`:""}<div class="xlegs">')
replace('<p class="small xverify">${esc(e.verification)}</p>', '<p class="fuel-note"><strong>Treibstoff & Durchführung</strong><br>${esc(e.fuelNote)}</p><p class="small xverify">${esc(e.verification)}</p>')
replace('</details><div class="card-footer"><button data-xmap=', '</details>${e.sources?.length?`<div class="source-links">${e.sources.map(([title,url])=>`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title)} ↗</a>`).join("")}</div>`:""}<div class="card-footer"><button data-xmap=')
replace("$('#xFormula').textContent=X.formula;renderCountryRows();renderXProgress();", "$('#xFormula').textContent=X.formula;renderFleet();renderCountryRows();renderXProgress();")
start=s.index('function allJourney()')
s=s[:start]+r'''function allJourney(){
 const rows=[];
 for(const l of D.legs){
  const a=A[l.to];
  rows.push({...l,kind:'A320',profile:'A320',aircraft:D.meta.aircraft,country:a.countryName,title:a.name,note:[a.highlight?.join(': '),a.note,B?.[l.to]?.experience].filter(Boolean).join(' '),sources:[a.runwaySource||a.url].filter(Boolean).join(' | '),conditional:false});
  for(const e of X.excursions.filter(e=>e.afterLeg===l.id))for(const x of e.legs)rows.push({...x,kind:'Ausflug',profile:e.profile,aircraft:e.aircraft,excursion:e.id,afterLeg:e.afterLeg,country:XA[x.to].country===e.country?e.countryName:D.countries.find(c=>c.code===XA[x.to].country)?.name||XA[x.to].country,title:XA[x.to].name,note:[e.briefing,e.experience,e.fuelNote].filter(Boolean).join(' '),sources:[XA[x.to].url,...(e.sources||[]).map(s=>s[1])].join(' | '),conditional:e.conditional});
 }
 return rows.map((l,i)=>({...l,sequence:i+1}));
}
function isJourneyDone(l){return l.kind==='A320'?state.done.has(l.id):state.xDone.has(l.id)}
function renderJourney(){
 const all=allJourney(),q=normalize($('#journeySearch').value),fleet=$('#journeyFleet').value||'all',status=$('#journeyStatus').value||'all';
 const rows=all.filter(l=>(fleet==='all'||fleet===l.profile)&&(!q||normalize([l.from,l.to,l.title,l.country,l.note].join(' ')).includes(q))&&(status==='all'||status==='long'&&l.over2h||status==='done'&&isJourneyDone(l)||status==='open'&&!isJourneyDone(l)));
 $('#journeyRows').innerHTML=rows.map(l=>`<tr class="${l.kind==='Ausflug'?'side':''}"><td><input type="checkbox" class="table-check" data-journeyid="${l.id}" data-kind="${l.kind}" aria-label="Flug ${l.sequence} als geflogen markieren" ${isJourneyDone(l)?'checked':''}></td><td class="mono">${String(l.sequence).padStart(3,'0')}<div class="airport-name">${l.kind==='A320'?'A320 '+String(l.id).padStart(3,'0'):'Ausflug'}</div></td><td class="mono airport-pair">${esc(l.from)} → ${esc(l.to)}</td><td><span class="tag ${l.profile==='A320'?'owned':l.profile==='H160'?'base':'warn'}">${l.profile==='A320'?'Fenix A320':l.profile==='H160'?'H160':'Twin Otter'}</span></td><td>${esc(l.title)}<div class="airport-name">${esc(l.country)}</div></td><td class="mono ${l.over2h?'time-long':''}">${hm(l.airMin)} h<div class="airport-name">${l.nm} NM</div></td><td><button ${l.kind==='A320'?`data-mainleg="${l.id}"`:`data-xmap="${l.excursion}"`}>Briefing →</button></td></tr>`).join('')||'<tr><td colspan="7" class="empty">Keine passenden Legs.</td></tr>';
 $('#journeyTotals').textContent=`${all.length} verbundene Legs · ${state.done.size+state.xDone.size} lokal geflogen · EDLV → EDLV · ≈ ${hm(all.reduce((n,l)=>n+l.airMin,0))} h Flugzeit`;
 $('#journeyCount').textContent=`${rows.length} von ${all.length} Legs angezeigt. Filter behalten die ursprüngliche Flugreihenfolge bei.`;
 $('#retiredDetails').hidden=state.retiredXDone.size===0;
 $('#retiredRows').innerHTML=(X.retiredLegs||[]).filter(l=>state.retiredXDone.has(l.id)).map(l=>`<p>✓ ${esc(l.from)} → ${esc(l.to)} · ${esc(l.country)} · frühere Direktverbindung</p>`).join('');
}
for(const id of ['#journeySearch','#journeyFleet','#journeyStatus'])$(id).addEventListener(id==='#journeySearch'?'input':'change',renderJourney);
$('#journeyRows').addEventListener('change',e=>{const id=e.target.dataset.journeyid;if(!id)return;const main=e.target.dataset.kind==='A320',set=main?state.done:state.xDone,key=main?Number(id):id;if(e.target.checked)set.add(key);else set.delete(key);saveAll();renderRows();renderDetail()});
document.addEventListener('click',e=>{const b=e.target.closest('[data-mainleg]');if(!b)return;const l=D.legs[Number(b.dataset.mainleg)-1];showView('tourView');setChapter(l.chapter,false);selectLeg(l.id,true)});
function renderExpeditions(){
 $('#expeditionGrid').innerHTML=X.excursions.filter(e=>e.profile==='DHC6').map(e=>`<article class="highlight-card ${e.country==='AQ'?'featured':''}"><div class="kicker">TWIN OTTER · NACH A320-LEG ${String(e.afterLeg).padStart(3,'0')}</div><div class="bigcode">${e.target}</div><h3>${esc(e.title)}</h3><p>${esc(e.experience)}</p><h4>So lohnt sich der Anflug</h4><p>${esc(e.timing)}</p><h4>Die feste Route</h4><p class="mono">${e.route.join(' → ')}</p><p>${e.legs.length} Legs · zusammen ≈ ${hm(e.legs.reduce((n,l)=>n+l.airMin,0))} h</p>${e.country==='AQ'||e.country==='TV'?`<p class="fuel-note">${e.country==='AQ'?'Rund 4:21 h je Richtung. Vorbereitete Betankung in SCRM und individuelle Reichweitenprüfung gehören zum Plan.':'Tankstopps auf Yasawa, Rotuma und Funafuti als vorbereitete Simulatorversorgung. Vier Legs knapp über zwei Stunden.'}</p>`:''}<div class="card-footer"><span class="tag warn">${esc(e.countryName)}</span><button data-xmap="${e.id}">Ausflug & Briefing →</button></div></article>`).join('');
}
$('#fullCsvExport').onclick=()=>{
 const rows=[['Reihenfolge','Leg_ID','Art','Von','Nach','Flugzeug','Ziel','Kategorie_am_Ziel','NM','Flugzeit_Min','Blockzeit_Min_A320','Lokal_geflogen','Volanta_Wertung','Hinweise_Anflug_Treibstoff','Quellen'],...allJourney().map(l=>[l.sequence,l.id,l.kind,l.from,l.to,l.aircraft,l.title,l.country,l.nm,l.airMin,l.blockMin||'',isJourneyDone(l)?'Ja':'Nein','Nach Flug kontrollieren',l.note,l.sources])];
 download('Volanta-Worldtour-245-Komplette-Reihenfolge.csv','\ufeff'+rows.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\r\n'),'text/csv;charset=utf-8');toast('Alle Fluggeräte in fester Flugreihenfolge exportiert');
};
$('#journeyCsv').onclick=()=>$('#fullCsvExport').onclick();
$('#backupExport').onclick=()=>download('Worldtour-EDLV-Fortschritt.json',JSON.stringify({tour:'EDLV-2026-09-v1',routeVersion:2,total:D.legs.length,done:[...state.done],xDone:[...state.xDone],retiredXDone:[...state.retiredXDone],savedAt:new Date().toISOString()},null,2),'application/json');
$('#backupFile').onchange=async e=>{
 const f=e.target.files[0];if(!f)return;
 try{
  const s=JSON.parse(await f.text());
  if(s.tour!=='EDLV-2026-09-v1'||s.total!==D.legs.length||!Array.isArray(s.done)||!s.done.every(id=>Number.isInteger(id)&&id>0&&id<=D.legs.length)||(s.xDone!==undefined&&(!Array.isArray(s.xDone)||!s.xDone.every(id=>xIDs.has(id)||retiredIDs.has(id))))||(s.retiredXDone!==undefined&&(!Array.isArray(s.retiredXDone)||!s.retiredXDone.every(id=>retiredIDs.has(id)))))throw Error();
  state.done=new Set(s.done);restoreXProgress(s);saveAll();renderRows();renderDetail();renderCoverage();toast(state.retiredXDone.size?'Fortschritt geladen; frühere Direkt-Legs im Archiv erhalten':'Hauptroute und Ausflugsfortschritt geladen');
 }catch(err){toast('Diese Sicherung passt nicht zu dieser Tour.')}
 e.target.value='';
};
'''
p.write_text(s,encoding='utf8')
print('Excursion UI updated')
