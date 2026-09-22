"""Apply the user's H160-first preference while retaining routes and progress IDs."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
E=json.loads((R/'excursions.json').read_text(encoding='utf8'))
before=[(e['id'], e['route'], [l['id'] for l in e['legs']]) for e in E['excursions']]
airbus='https://www.airbus.com/en/products-services/helicopters/civil-helicopters/h160/h160-technical-information'
for e in E['excursions']:
    e['highlightCard']=e.get('highlightCard', e['profile']=='DHC6')
    if e['country']=='AQ':
        e['aircraftReason']='Twin Otter bleibt erforderlich für diese feste Direktstrecke: Ushuaia–SCRM misst rund 528 NM, mehr als die von Airbus angegebene maximale H160-Reichweite von 480 NM mit Standardtanks, noch ohne Reserve. Keine sichere H160-Zwischenlandung ist auf dieser Route vorgesehen. Auch die Twin-Otter-Etappe bleibt von individueller Verbrauchs-/Reserveplanung und vorbereiteter Betankung in SCRM abhängig.'
        continue
    was_twin=e['profile']=='DHC6'
    e.update(profile='H160',aircraft='Airbus H160',cruiseKt=138)
    for l in e['legs']:
        l['airMin']=max(12,round(12+l['nm']*1.1/138*60))
        if e['target']=='NZMF':l['airMin']=45
        l['over2h']=l['airMin']>120
    e['sources']=[s for s in e.get('sources',[]) if 'DHC-6' not in s[0]]
    if not any(s[1]==airbus for s in e['sources']):e['sources'].append(['Airbus: H160 Leistung und Reichweite',airbus])
    e['aircraftReason']='H160 bevorzugt: Die Entfernungen dieser Schleife erfordern keine Twin Otter. Nutzlast, Wind, Reserve und geeignete Landefläche bleiben vor jedem Simulatorflug zu prüfen.'
    if was_twin:
        e['fuelNote']='Am A320-Ausgangspunkt für Hin- und Rückflug sowie Reserven tanken. Eine Betankung am Ausflugsziel wird nicht vorausgesetzt. Verbrauch und Reserven im HPG-EFB prüfen; Landschaftsrunden zusätzlich berücksichtigen.'
    if e['target']=='EGLC':
        e['briefing']='Kurzer H160-Abstecher von Heathrow entlang einer bewusst geplanten Sichtflugstrecke in den Raum Docklands, mit fiktiver Simulatorlandung am vorhandenen UK2000-Airport EGLC, dann zurück nach Heathrow. Die Kartenlinie ist keine freigegebene Londoner Helikopterroute. EGLC ist hier kein regulär zugelassener H160-Zielplatz; reale Hubschrauberoperationen werden nicht behauptet.'
        e['timing']='Klares Tageslicht für Themse, Canary Wharf und Royal Docks. Hindernisse und geeignete Landefläche im Simulator prüfen. Kein Steilanflug mit der Twin Otter vorgesehen.'
        e['aircraftReason']='Nur rund 19 NM je Richtung: H160 statt Twin Otter. Die Landung in EGLC bleibt eine ausdrücklich fiktive Simulatoroperation.'
        e['sources'].append(['CAA: London helicopter operations','https://www.caa.co.uk/Data-and-analysis/Airspace-and-environment/Airspace/London-helicopter-operations'])
    if e['target']=='KSEZ':
        e['briefing']='Von Phoenix mit dem H160 nach Sedona und zurück. Die roten Felsen und die Mesa aus geeigneter Höhe betrachten, anschließend an einer geeigneten Fläche des Flughafens in deiner XCodr-Szenerie landen. Keine zusätzliche Flugzeugübernahme erforderlich.'
        e['timing']='Frühes Morgenlicht oder spätes Nachmittagslicht. Hitze, Dichtehöhe, Wind an der Mesa und H160-Leistungsreserve beim Anflug prüfen.'
    if e['target']=='NZMF':
        e['experience']='Von Queenstown über vorbereitete alpine Täler und Pässe zum Milford Sound: Fjordwände und Wasserfälle sind mit dem H160 das Hauptmotiv. Die vorhandene Blinn-Szenerie bleibt der feste Zielstopp.'
        e['briefing']='Queenstown–Milford Sound–Queenstown mit dem H160. Die Großkreislinie ist keine durchfliegbare Talroute. Wettergerechte Täler und Pässe anhand Gelände und CAA-Briefing vorbereiten; geeignete Hubschrauber-Landefläche am Airport nutzen. Als Planwert bleiben 45 Minuten je Richtung, zusätzliche Fotokreise kommen dazu.'
    if e['country']=='BL':
        e['briefing']='Vom A320-Stopp Sint Maarten mit dem H160 nach St. Barth und zurück. Hügelkante, Bucht und Küste aus passender Höhe betrachten, dann eine geeignete Landefläche am Airport TFFJ nutzen. Die kurze Piste allein erfordert keinen Wechsel zur Twin Otter.'
        e['experience']='Hügelkante über der Straße, die Bucht von St. Jean und Gustavia prägen den Ausflug. Mit dem H160 kannst du die Umgebung betrachten; der berühmte starre Pistenanflug ist kein vorgeschriebenes Helikopterverfahren.'
        e['timing']='Gute Sicht und passender Wind. Hindernisse am Hügel, Straßenverkehr und Platzverkehr berücksichtigen; kein erzwungener Tiefflug über den Sattel.'
    if e['country']=='MS':
        e['briefing']='Antigua–Montserrat–Antigua mit dem H160. Die Küstenkante bei John A. Osborne und die grünen Inselhänge sind die Hauptmotive. Geeignete Landefläche am Airport prüfen; Vulkanregion nur mit Abstand als optionalen POI betrachten.'
        e['experience']='Die kurze Flughafenplattform liegt an der Steilküste. Der H160 ermöglicht den Blick auf Küste und Inselhänge; die Twin Otter ist für die rund 31 NM je Richtung nicht nötig.'
    if e['country']=='TV':
        e['briefing']='Die feste H160-Inselkette lautet Nadi–Yasawa–Rotuma–Funafuti und zurück über dieselben Stopps. Die Zwischenlandungen teilen die Strecke in 61, 258 und 269 NM. Vier Legs bleiben trotz Zwischenstopps über zwei Stunden; die maximal 269 NM je Etappe liegen unter der veröffentlichten H160-Maximalreichweite, ersetzen aber keine Reserveberechnung.'
        e['experience']='Riffe, Lagune und der schmale Landstreifen von Funafuti sind das Motiv. Yasawa und Rotuma ergänzen die Küstenblicke und ermöglichen vorbereitete Tankstopps mit dem H160.'
        e['fuelNote']='Simulierte Betankung in Yasawa, Rotuma und Funafuti ist zwingende Planannahme; reguläre Jet-A-1-Versorgung wurde nicht bestätigt. Vor jedem Leg Verbrauch, Wind, Nutzlast und Reserve im HPG-EFB prüfen. Das Zeitmodell ergibt etwa 2:15 h für 258 NM und 2:21 h für 269 NM. Hin- und Rückflug Rotuma–Funafuti ohne Betankung ist nicht eingeplant. Keine Tanklandung mitten im Ozean angenommen.'
        e['aircraftReason']='H160 mit den vorhandenen Zwischenstopps: längstes Leg 269 NM. Die bisherige Twin Otter war eine Erlebniswahl, keine Reichweitennotwendigkeit. Die Tankstopps bleiben Voraussetzung.'
E['version']=3
E['h160Source']=airbus
E['fleetNote']='18 H160-Ausflüge und eine Twin-Otter-Expedition zur Antarktis. London City, Sedona, Milford Sound, St. Barth, Montserrat und Tuvalu werden mit dem H160 geflogen. Alle 449 Legs und ihre Fortschrittskennungen bleiben erhalten.'
E['formula']='Flugzeit ≈ 12 min + Großkreisdistanz × 1,10 / Reisegeschwindigkeit × 60. H160: 138 kt; Twin Otter nur Antarktis: 140 kt. Milford Sound: 45 min je Richtung als Ansatz für Gelände und Anflug. Ohne Live-Wind oder zusätzliche POI-Runden; keine Kraftstoffberechnung. H160-Maximalreichweite laut Airbus: 480 NM, nicht als nutzbare Planreichweite mit Reserve behandeln.'
assert before==[(e['id'],e['route'],[l['id'] for l in e['legs']]) for e in E['excursions']]
(R/'excursions.json').write_text(json.dumps(E,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(E['fleetNote'])
