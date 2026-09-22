from pathlib import Path
import json
R=Path(__file__).resolve().parent
# Keep the checked airport-country assignment visible in the main route as well.
p=R/'tour-data.json';D=json.loads(p.read_text(encoding='utf8'))
note='Ascension: RAF-Flugplatz mit langer Piste, als fiktiver Simulator-Sonderbetrieb geplant. Am 21.09.2026 in Volantas Flughafenansicht direkt geprüft: FHAW gehört zur Kategorie Saint Helena (SH). Kein Besuch der Insel St Helena selbst; Länderpunkt nach dem Flug kontrollieren.'
D['airports']['FHAW']['note']=note
p.write_text(json.dumps(D,ensure_ascii=False,separators=(',',':')),encoding='utf8')
p=R/'route_source.py';s=p.read_text(encoding='utf8');old="'FHAW':'Ascension: RAF-Flugzplatz" # Replace the complete known entry below.
lines=s.splitlines()
for i,l in enumerate(lines):
    if l.startswith(" 'FHAW':"):lines[i]=" 'FHAW':"+repr(note)+','
p.write_text('\n'.join(lines)+'\n',encoding='utf8')
p=R/'tour-template.html';s=p.read_text(encoding='utf8')
needle="mapGroup.append('g').selectAll('path').data(D.legs)"
assert needle in s
overlay="""const xTrips=X.excursions.filter(e=>state.map==='world'||state.map==='chapter'&&e.chapter===state.chapter||state.map==='leg'&&e.afterLeg===chosen.id);mapGroup.append('g').selectAll('path').data(xTrips.flatMap(e=>e.legs)).join('path').attr('d',l=>path({type:'LineString',coordinates:[point(XA[l.from]),point(XA[l.to])]})).attr('fill','none').attr('stroke','#c5acf6').attr('stroke-width',1.4).attr('stroke-dasharray','4 3').attr('vector-effect','non-scaling-stroke');const xpins=mapGroup.append('g').selectAll('circle').data(xTrips).join('circle').attr('class','background-pin').attr('cx',e=>proj(point(XA[e.target]))[0]).attr('cy',e=>proj(point(XA[e.target]))[1]).attr('r',3).attr('fill','#c5acf6').style('cursor','pointer').on('click',(ev,e)=>{ev.stopPropagation();openExcursion(e.id)});xpins.append('title').text(e=>`${e.countryName} · ${e.target} · ${e.aircraft}`);"""
s=s.replace(needle,overlay+needle)
s=s.replace('`${D.legs.length} LEGS · EDLV → EDLV`','`${D.legs.length} A320 + ${XL.length} AUSFLUGS-LEGS · EDLV → EDLV`')
s=s.replace('<i class="inactive"></i>','<i class="inactive"></i>',1)
# Add links exactly at the point where the Fenix is parked for each excursion.
needle='<button class="complete-btn ${done?'
pos=s.index(needle)
s=s[:pos]+'''${X.excursions.some(e=>e.afterLeg===l.id)?`<h3>Nach der Landung: Ausflüge</h3><p class="small muted">Fenix bei ${b.icao} abstellen, Ausflug fliegen und hier zur Hauptroute zurückkehren.</p><div class="backup-actions">${X.excursions.filter(e=>e.afterLeg===l.id).map(e=>`<button data-xmap="${e.id}" style="font-size:12px">${esc(e.countryName)} · ${e.target} →</button>`).join('')}</div>`:''}'''+s[pos:]
s=s.replace('Offline-Karte & Routendaten · Externe Quellenlinks benötigen Internet','Violett gestrichelt: Ausflüge · Offline-Karten · Quellenlinks benötigen Internet')
p.write_text(s,encoding='utf8')
# Persist UI verification in the generator, so a rebuild does not lose it.
p=R/'build_excursions.py';s=p.read_text(encoding='utf8').replace("['PS','VA','TF']","['PS','VA','TF','AD']");p.write_text(s,encoding='utf8')
print('Connected excursions to main map and arrival briefings')
