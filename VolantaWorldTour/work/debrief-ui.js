// Confirmed reports are project data. Browser checkboxes never populate actual scenery.
const DB=JSON.parse($('#debriefData').textContent);
const debriefEntries=new Map(DB.entries.map(entry=>[entry.legId,entry]));
let debriefSelected=null;
function debriefRecord(l){return debriefEntries.get(String(l.id))}
function debriefStatus(l){
 const entry=debriefRecord(l);
 return entry?.status==='final'?'Final dokumentiert':entry?'Angaben offen':isJourneyDone(l)?'Debrief offen':'Noch nicht debrieft';
}
function debriefSceneryText(s){return s?.product?`${s.product}${s.version?' · Version '+s.version:''}`:'Noch nicht angegeben'}
function debriefPrompt(l){
 return `Debriefing · Flug ${String(l.sequence).padStart(3,'0')} · Leg-ID ${l.id}\n${l.from} → ${l.to}\n\nFlugdatum und tatsächlich verwendetes Flugzeug:\nAbflug ${l.from} – tatsächlich aktive Airport-Szenerie (Hersteller, Produkt, ggf. Version; auch Standard/WU ausdrücklich nennen):\nAnkunft ${l.to} – tatsächlich aktive Airport-Szenerie:\nZusätzliche Landschafts-/Stadt-Add-ons:\nAnflug, Landebahn/Landeplatz, Wetter und Tageszeit:\nWas war das Highlight?\nPerformance, Probleme oder Auffälligkeiten:\nFazit: hat sich die Szenerie gelohnt? Was nächstes Mal anders?\nVolanta-Wertung nach dem Flug geprüft (gutgeschrieben / nicht gutgeschrieben / offen):\n\nBitte im Projekt dokumentieren. Fehlende Angaben offen lassen; geplante Szenerien nicht als verwendet übernehmen.`;
}
function openDebrief(id){
 const leg=allJourney().find(l=>String(l.id)===String(id));if(!leg)return;
 debriefSelected=String(leg.id);$('#debriefSearch').value='';$('#debriefFilter').value='all';
 showView('debriefView');
 $('#debriefDetail').scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
}
function renderDebriefs(){
 const all=allJourney(),q=normalize($('#debriefSearch').value),filter=$('#debriefFilter').value||'pending';
 const pending=l=>debriefRecord(l)?.status!=='final'&&(isJourneyDone(l)||!!debriefRecord(l));
 const rows=all.filter(l=>{
  const entry=debriefRecord(l);
  return (filter==='all'||filter==='final'&&entry?.status==='final'||filter==='pending'&&pending(l))&&(!q||normalize([l.id,l.sequence,l.from,l.to,l.title,l.aircraft,entry?JSON.stringify(entry):''].join(' ')).includes(q));
 });
 const finals=DB.entries.filter(e=>e.status==='final').length;
 $('#debriefStats').innerHTML=[[finals,'Legs final dokumentiert'],[all.filter(pending).length,'Geflogen / berichtet · Debrief offen'],[all.length,'Legs mit Debriefing-Zuordnung']].map(([n,label])=>`<article><b>${n}</b><span>${label}</span></article>`).join('');
 if(!debriefSelected||!rows.some(l=>String(l.id)===debriefSelected))debriefSelected=rows.length?String(rows[0].id):null;
 $('#debriefRows').innerHTML=rows.map(l=>`<tr class="${String(l.id)===debriefSelected?'selected':''}"><td class="mono">${String(l.sequence).padStart(3,'0')}<div class="airport-name">Leg-ID ${esc(l.id)} · ${esc(l.profile)}</div></td><td><button data-debrief-select="${esc(l.id)}" aria-label="Debriefing für ${esc(l.from)} nach ${esc(l.to)}, Leg ${esc(l.id)} öffnen">${esc(l.from)} → ${esc(l.to)}</button><div class="airport-name">${esc(l.title)}</div></td><td><span class="tag ${debriefRecord(l)?.status==='final'?'owned':pending(l)?'warn':''}">${debriefStatus(l)}</span></td></tr>`).join('')||`<tr><td colspan="3" class="empty">${filter==='pending'&&!q?'Keine offenen Debriefings. Nach dem ersten Flug ein Häkchen setzen oder das Leg unter „Alle Legs anzeigen“ öffnen.':'Keine passenden Debriefings.'}</td></tr>`;
 $('#debriefCount').textContent=`${rows.length} von ${all.length} Legs · Flugnummer = gesamte Reihenfolge; Leg-ID = feste Zuordnung im Projekt.`;
 renderDebriefDetail(all.find(l=>String(l.id)===debriefSelected));
}
function renderDebriefDetail(l){
 if(!l){$('#debriefDetail').innerHTML='<div class="kicker">Bereit für deinen ersten Bericht</div><h3>Erst erleben.<br>Dann festhalten.</h3><p>Nach jedem Flug sammeln wir deine tatsächlich verwendeten Szenerien und deine Eindrücke. Wähle ein Leg, um die passende Vorlage für unser Gespräch zu öffnen.</p><p>Einzelne fehlende Angaben sind kein Hindernis: sie bleiben sichtbar offen.</p>';return}
 const entry=debriefRecord(l),scenery=entry?.actualScenery;
 const field=value=>esc(value||'Noch nicht angegeben');
 const volanta={open:'Noch nicht geprüft',credited:'Laut deinem Bericht gutgeschrieben',not_credited:'Laut deinem Bericht nicht gutgeschrieben'};
 const actual=side=>`<section><div class="kicker">${side==='departure'?'Abflug · '+esc(l.from):'Ankunft · '+esc(l.to)}</div><strong>${field(scenery?.[side]?.product)}</strong><small>Version: ${field(scenery?.[side]?.version)}</small></section>`;
 const fields=[['Flugdatum',entry?.flightDate],['Tatsächlich geflogenes Flugzeug',entry?.aircraft],['Zusätzliche Landschafts-/Stadt-Add-ons',scenery?.landscape],['Anflug, Landebahn / Landeplatz',entry?.approach],['Wetter und Tageszeit',entry?.conditions],['Dein Highlight',entry?.highlights],['Performance und Probleme',entry?.issues],['Dein Szenerie-Fazit',entry?.verdict],['Für das nächste Mal',entry?.nextTime]];
 $('#debriefDetail').innerHTML=`<div class="kicker">Flug ${String(l.sequence).padStart(3,'0')} · Leg-ID ${esc(l.id)} · ${esc(l.profile)}</div><h3 class="mono">${esc(l.from)} → ${esc(l.to)}</h3><p>${esc(l.title)}</p><div class="debrief-status"><span class="tag ${entry?.status==='final'?'owned':'warn'}">${debriefStatus(l)}</span>${entry?` <span class="small muted">Bearbeitet: ${esc(entry.updatedAt)}</span>`:''}</div><h4>Tatsächlich verwendete Airports</h4><div class="debrief-actual">${actual('departure')}${actual('arrival')}</div><dl>${fields.map(([label,value])=>`<dt>${label}</dt><dd>${field(value)}</dd>`).join('')}<dt>Volanta-Wertung</dt><dd>${esc(volanta[entry?.volanta||'open'])}</dd></dl><p class="small muted">Ein Finalbericht bestätigt die genannten Szenerien. Andere fehlende Angaben bleiben offen. Berichte bleiben auch beim Entfernen eines Flug-Häkchens erhalten.</p><details><summary>Geplante Empfehlungen zum Vergleich</summary><p><strong>${esc(l.from)}:</strong> ${esc(SC.airports[l.from]?.recommendation||'Keine Empfehlung hinterlegt')}</p><p><strong>${esc(l.to)}:</strong> ${esc(SC.airports[l.to]?.recommendation||'Keine Empfehlung hinterlegt')}</p><div class="backup-actions">${sceneryButton(l.from)}${sceneryButton(l.to)}</div></details><h4>Vorlage für unser Debriefing im Chat</h4><p>Du kannst frei erzählen oder diese Vorlage kopieren. Ich pflege den Bericht anschließend in die Projektdateien ein und aktualisiere die HTML.</p><label for="debriefPrompt" class="small muted">Gesprächsvorlage · nur zum Kopieren</label><textarea id="debriefPrompt" class="debrief-prompt" readonly></textarea><button id="debriefTemplateExport">Vorlage als Text herunterladen</button>`;
 $('#debriefPrompt').value=debriefPrompt(l);
 $('#debriefTemplateExport').onclick=()=>download(`Debriefing-${l.id}-${l.from}-${l.to}.txt`,debriefPrompt(l),'text/plain;charset=utf-8');
}
document.addEventListener('click',event=>{
 const open=event.target.closest('[data-debrief]');if(open)openDebrief(open.dataset.debrief);
 const select=event.target.closest('[data-debrief-select]');if(select){debriefSelected=select.dataset.debriefSelect;renderDebriefs()}
});
$('#debriefSearch').oninput=renderDebriefs;$('#debriefFilter').onchange=renderDebriefs;
$('#debriefShowAll').onclick=()=>{$('#debriefFilter').value='all';$('#debriefSearch').value='';renderDebriefs()};
$('#debriefArchiveExport').onclick=()=>download('Worldtour-EDLV-Debriefings.json',JSON.stringify(DB,null,2),'application/json');
