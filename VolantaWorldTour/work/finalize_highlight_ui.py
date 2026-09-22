from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'tour-template.html';s=p.read_text(encoding='utf8')
s=s.replace('Die 16 Ausflüge sind in die Gesamtfolge eingefügt.', 'Die 19 Ausflüge sind in die Gesamtfolge eingefügt: 16 ergänzen Kategorien, drei erschließen eigene Highlight-Szenerien.')
s=s.replace('Vier besondere Twin-Otter-Ausflüge','Sieben besondere Twin-Otter-Ausflüge')
s=s.replace('A320-Welttour + 16 verbundene Ausflüge','A320-Welttour + 19 verbundene Ausflüge')
s=s.replace('16 Ausflüge. In deiner Flugreihenfolge.','19 Ausflüge. In deiner Flugreihenfolge.')
s=s.replace('36 deiner 44 Add-on-Airports sind enthalten.', '39 deiner 44 Add-on-Airports sind enthalten: 36 auf der A320-Hauptroute, London City, Sedona und Milford Sound als Twin-Otter-Ausflüge.')
s=s.replace('<b class="teal">36<em>', '<b class="teal">${36+(X.bonusOwnedAirports?.length||0)}<em>')
s=s.replace('<strong>Blockzeit</strong> enthält zusätzlich pauschal 20 Minuten für Rollen.', '<strong>Blockzeit</strong> enthält beim A320 zusätzlich pauschal 20 Minuten für Rollen; für Ausflüge wird nur die Flugzeit angegeben.')
s=s.replace('<button class="primary" id="fullCsvExport">', '<button id="xBriefing">Briefing zum ausgewählten Ausflug ↓</button><button class="primary" id="fullCsvExport" style="margin-top:10px">')
# The inventory is rendered after excursion data initialization so it can include bonus loops.
start=s.index("$('#inventory').innerHTML=");end=s.index('\nfunction download',start)
s=s[:start]+s[end:]
s=s.replace('renderCoverage();renderJourney();renderProgress();','renderCoverage();renderJourney();renderInventory();renderProgress();')
s=s.replace('<span><i class="inactive"></i>Gesamttour</span>','<span><i class="inactive"></i>Gesamttour</span><span><i style="background:var(--purple)"></i>Ausflüge</span>')
p.write_text(s,encoding='utf8')
p=R/'excursions-ui.js';s=p.read_text(encoding='utf8')
s=s.replace('St. Barth, Montserrat, Antarktis, Tuvalu`','inklusive drei eigener Highlight-Szenerien`')
s=s.replace('${X.excursions.length} = 245','${X.excursions.filter(e=>e.categoryVisit!==false).length} = 245')
s=s.replace('Jeder Ausflug kehrt zum A320 zurück. Offene Nachweise sind unten markiert.', 'Drei weitere Ausflüge nutzen eigene Szenerien in bereits abgedeckten Ländern. Jeder Ausflug kehrt zum A320 zurück.')
s=s.replace('${esc(e.countryName)} · ${e.anchor}</option>', '${esc(e.displayName||e.countryName)} · ${e.anchor}</option>')
s=s.replace('<h3>${esc(e.countryName)}</h3><p class="side-trip', '<h3>${esc(e.displayName||e.countryName)}</h3><p class="side-trip')
s=s.replace('${e.historical?', '${e.categoryVisit===false?\'<span class="tag owned">Eigene Szenerie · Highlight-Ausflug</span>\':\'\'}${e.historical?',1)
s += '''
$('#xBriefing').onclick=()=>document.getElementById('excursion-'+xSelected).scrollIntoView({block:'start',behavior:'smooth'});
function renderInventory(){
 $('#inventory').innerHTML=D.inventory.map(i=>{const side=(X.bonusOwnedAirports||[]).includes(i.icao),used=i.inRoute||side;return `<div title="${esc(i.inRoute?'In der A320-Hauptroute':side?'Twin-Otter-Ausflug':i.reason)}"><span class="mono" style="color:${used?'var(--teal)':'var(--gold)'}">${used?'✓':'◇'} ${i.icao}</span><small>${esc(i.manufacturer)}</small>${side?'<small>Im Twin-Otter-Ausflug</small>':i.inRoute?'':`<small style="margin-top:5px">${esc(i.reason)}</small>`}</div>`}).join('');
}
$('#sources').innerHTML+=`<a href="${X.h160Source}" target="_blank" rel="noopener noreferrer">Airbus: H160 technische Daten ↗</a><a href="${X.h160ImplementationSource}" target="_blank" rel="noopener noreferrer">HPG: H160 im Simulator ↗</a><a href="https://www.flightsimulator.com/aircraft-manuals/" target="_blank" rel="noopener noreferrer">MSFS: Flugzeughandbücher ↗</a>`;
'''
p.write_text(s,encoding='utf8')
print('Final fleet and owned-scenery UI updated')
