from pathlib import Path
import json
R=Path(__file__).resolve().parent
p=R/'tour-template.html';s=p.read_text(encoding='utf8')
s=s.replace('16 Kategorien benötigen ein anderes Flugzeug oder bleiben ein Sonderfall.','Die 16 ergänzenden Ausflüge bringen den Plan auf 245 Kategorien; sie sind mit Hin- und Rückflug auf einer eigenen Karte eingetragen. * Szenerie und Volanta-Wertung bleiben vor Ort zu prüfen.')
s=s.replace('Offene Nachweise sind unten markiert.','Geschlossene Plätze und besondere Voraussetzungen sind unten markiert.')
p.write_text(s,encoding='utf8')
p=R/'excursions-ui.js';s=p.read_text(encoding='utf8')
s=s.replace("${e.conditional?'<span class=\"tag warn\">Volanta-Nachweis offen</span>':''}","${e.historical?'<span class=\"tag warn\">Geschlossen · fiktiver Besuch</span>':e.conditional?'<span class=\"tag warn\">Volanta-Nachweis offen</span>':''}")
s=s.replace("e.conditional?'Zielvorschlag · Nachweis offen':'Ausflug geplant'","e.historical?'Historischer Simulator-Ausflug':e.conditional?'Zielvorschlag · Nachweis offen':'Ausflug geplant'")
p.write_text(s,encoding='utf8')
# These are airport-detail UI observations, not claimed completed challenge visits.
p=R/'excursions.json';E=json.loads(p.read_text(encoding='utf8'))
for e in E['excursions']:
    if e['country']=='AD':e['verification']='Am 21.09.2026 direkt in Volantas Flughafenansicht geprüft: AD-ALV gehört dort zu Andorra (AD). Länderpunkt nach abgeschlossenem Flug kontrollieren.'
E['note']='Für jede der 245 Volanta-Kategorien liegt ein konkreter Zielvorschlag vor. Die Zuordnung von LLJR folgt ausdrücklich Volanta. Keine Garantie für automatische Länderwertung oder vollständige MSFS-2024-Szenerien.'
p.write_text(json.dumps(E,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Excursions finalized')
