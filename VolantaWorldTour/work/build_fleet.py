"""Build the accepted A320 / H160 / Twin Otter tour without renumbering flown legs."""
from pathlib import Path
import csv, json, math

R = Path(__file__).resolve().parent
legacy = R / 'excursions-v1-source.json'
if not legacy.exists():
    legacy.write_text((R / 'excursions.json').read_text(encoding='utf8'), encoding='utf8')
old = json.loads(legacy.read_text(encoding='utf8'))
E = json.loads((R / 'h160-plan-pending.json').read_text(encoding='utf8'))
runways = list(csv.DictReader((R / 'runways.csv').open(encoding='utf8')))
manual = 'https://flightsimulator.azureedge.net/wp-content/uploads/2024/11/MSFS2024_DHC-6_TWIN_OTTER_AOM.pdf'

for code in ['NFSW', 'NFNR', 'FMMO']:
    rs = [r for r in runways if r['airport_ident'] == code and r['closed'] == '0' and r['length_ft']]
    rw = max(rs, key=lambda r: float(r['length_ft']), default={})
    E['points'][code].update(runway=round(float(rw['length_ft']) * .3048) if rw else None, surface=rw.get('surface', 'unbekannt'))
E['points']['SCRM'].update(runway=1292, width=39, surface='Schotter', runwaySource='https://ftp2.dgac.gob.cl/designador/SCRM')

for e in E['excursions']:
    code = e['country']
    previous = next(x for x in old['excursions'] if x['country'] == code)
    e.pop('decisionPending', None)
    e['profile'] = 'DHC6' if code in ['BL', 'MS', 'AQ', 'TV'] else 'H160'
    e['aircraft'] = 'DHC-6-300 Twin Otter · Räder' if e['profile'] == 'DHC6' else 'Airbus H160'
    e['cruiseKt'] = (140 if code == 'AQ' else 150) if e['profile'] == 'DHC6' else 138
    e['sources'] = []
    if e['profile'] == 'DHC6':
        e['sources'].append(['MSFS 2024: DHC-6-300 Handbuch', manual])
        e['fuelNote'] = 'Am Ausgangspunkt tanken. Masse, Verbrauch und Reserven anhand der installierten DHC-6-300 prüfen; das Zeitmodell ist keine Reichweitenfreigabe.'
    if code in ['BL', 'MS']:
        e['briefing'] = previous['briefing']
    if code == 'BL':
        e['experience'] = 'Der Wechsel von Meer und Hügelkante zur Piste in der Bucht ist der Höhepunkt. Mit der Twin Otter erlebst du den eigentlichen Pistenanflug und den kurzen Ausrollweg.'
        e['timing'] = 'Bei Tageslicht und guter Sicht; Bahn 10 nur bei passendem Wind. Das Motiv rechtfertigt keinen Rückenwindanflug.'
    if code == 'MS':
        e['experience'] = 'Die Piste von John A. Osborne sitzt an der Steilküste. Den Gegensatz aus blauer See, grünem Inselhang und kurzer Bahn bewusst im Anflug erleben; Soufrière Hills bleibt ein optionaler ferner POI.'
        e['timing'] = 'Klares Tageslicht; Vulkan und Sperrgebiete mit Abstand. Eine Landschaftsrunde gehört zusätzlich ins Zeit- und Treibstoffbudget.'
    if code == 'AQ':
        e['title'] = 'King George Island: die große Südpolar-Etappe'
        e['briefing'] = 'Ab Ushuaia über die Drake-Passage nach King George Island und anschließend zurück zum geparkten A320. Die Küste der Fildes-Halbinsel, Forschungsstationen und die Schotterbahn von SCRM bilden den Expeditions-Höhepunkt. Die Strecke ist ein kuratierter Simulatorflug, kein behaupteter Linienflug.'
        e['experience'] = 'Bei der Ankunft auf die Fildes-Halbinsel und die Buchten um das Stationsgebiet achten. Collins-Gletscher und Frei/Bellingshausen sind mögliche POIs in der Umgebung. Sichtbarkeit und Detailgrad hängen von deiner Szenerie ab; eine gesonderte Runde nur nach Betankung und mit eigenem Budget.'
        e['timing'] = 'Südlicher Sommer, etwa Dezember bis Februar, klares Tageslicht und moderater Wind. Der Ozeanabschnitt wird in Reiseflughöhe geplant; die landschaftlichen Höhepunkte liegen an den Enden.'
        e['fuelNote'] = 'Lange Ausnahme: rund 528 NM und 4:21 h je Richtung im Modell mit 140 kt. Vorbereitete simulierte Betankung in SCRM ist zwingende Planannahme; eine reguläre Tankstelle ist nicht bestätigt. Sparsame Reiseleistung, tatsächliche nutzbare Tanks einschließlich Flügeltank-Transfer, Wind und Reserve mit dem MSFS-Handbuch prüfen. Bei unzureichender Reserve die Etappe auf besseres Wetter verschieben. Hin- und Rückflug ohne Betankung sind nicht eingeplant.'
        e['scenery'] = 'SCRM vorab in der MSFS-2024-Weltkarte laden und Bahn, Oberfläche sowie Stationsumgebung prüfen. Die DGAC führt die Bahn 11/29 mit 1.292 × 39 m Schotter. Geplant ist die Radversion der Twin Otter. Kein kostenpflichtiges Add-on und kein vollständig modelliertes Stationsgebiet sind zugesichert.'
        e['sources'] += [['DGAC: SCRM und Pistenabmessungen', 'https://ftp2.dgac.gob.cl/designador/SCRM'], ['Australian Antarctic Program: Twin Otter im Antarktiseinsatz', 'https://www.antarctica.gov.au/antarctic-operations/travel-and-logistics/aviation/intracontinental-operations/dhc-6-twin-otter/'], ['Polar Geospatial Center: King George Island, Karte 2025', 'https://data.pgc.umn.edu/maps/antarctica/pgc/07/pdf/king%20george%20island%202025.pdf']]
    if code == 'TV':
        e['briefing'] = 'Die feste Inselkette lautet Nadi – Yasawa – Rotuma – Funafuti, zurück auf demselben Weg. Die Twin Otter macht daraus eine Folge von Pistenanflügen zwischen Inseln und offenem Pazifik. Yasawa und Rotuma teilen die Überwasserstrecke; die zwei längeren Abschnitte je Richtung bleiben knapp über zwei Stunden.'
        e['experience'] = 'In Funafuti liegt die Landebahn auf einem schmalen Landstreifen zwischen Ozean und Lagune. Der Endanflug entlang des Atolls ist das eigentliche Highlight; Yasawa ergänzt eine kleine Inselpiste und Rotuma einen abgelegenen Zwischenstopp.'
        e['timing'] = 'Gute Sicht und helles Tageslicht für die Riff- und Lagunenfarben. Jede Zwischenlandung einschließlich Wende und Startstrecke separat vorbereiten.'
        e['fuelNote'] = 'Vorbereitete simulierte Treibstoffversorgung in Yasawa, Rotuma und Funafuti einplanen; reguläres Jet A-1 ist dort nicht verifiziert. Die feste Route enthält Landungen an allen drei Plätzen. Rotuma–Funafuti–Rotuma nicht als unbetankten Rundflug behandeln. DHC-6-Masse, Wind, Grasbahnzustand auf Yasawa und Reserven vorab prüfen.'
    if code == 'SM':
        e['briefing'] = 'Vom Raum Rom über das Hügelland nach Torraccia. Mit der H160 an einer geeigneten Fläche des Flugplatzes LIKD landen; Grasfläche, Hindernisse und Leistung vorab prüfen. Ein optionaler Rundflug zeigt die Silhouette des Monte Titano.'
    if code == 'GG':
        e['title'] = 'Kanalinseln aus der Helikopterperspektive'
        e['briefing'] = 'Von Jersey zur Küste Guernseys und zum Flughafen. Die geringe Reiseflughöhe bei geeignetem Wetter lässt Buchten und Küstenformen wirken. Auf einer geeigneten Fläche innerhalb von EGJB landen und Volantas Erkennung nach dem Flug prüfen.'
    if code in ['VG', 'AI', 'DM', 'MF']:
        e['briefing'] += ' Für diesen Ausflug ist die H160 vorgesehen: passende Landefläche am genannten Flughafen sowie Hindernisse und Wind prüfen.'
    e['legs'] = []
    previous_ids = {(l['from'], l['to']): l['id'] for l in previous['legs']}
    for i, (a, b) in enumerate(zip(e['route'], e['route'][1:]), 1):
        pa, pb = E['points'][a], E['points'][b]
        p, q = map(math.radians, [pa['lat'], pb['lat']])
        dl = math.radians(pb['lon'] - pa['lon'])
        nm = round(3440.065 * 2 * math.asin(math.sqrt(math.sin((q-p)/2)**2 + math.cos(p)*math.cos(q)*math.sin(dl/2)**2)))
        minutes = max(12, round(12 + nm * 1.1 / e['cruiseKt'] * 60))
        leg_id = previous_ids.get((a, b), f'X-{code}-v2-{i}')
        e['legs'].append({'id':leg_id, 'from':a, 'to':b, 'nm':nm, 'airMin':minutes, 'over2h':minutes > 120})

active = {l['id'] for e in E['excursions'] for l in e['legs']}
E['retiredLegs'] = [dict(l, country=e['countryName']) for e in old['excursions'] for l in e['legs'] if l['id'] not in active]
E['version'] = 2
E['formula'] = 'Flugzeit ≈ 12 min + Großkreisdistanz × 1,10 / Reisegeschwindigkeit × 60. H160: 138 kt; Twin Otter: 150 kt, Antarktis konservativer mit 140 kt. Ohne Live-Wind, zusätzliche Geländeumwege oder POI-Runden. Keine Kraftstoff- oder Blockzeitberechnung.'
E['logistics'] = 'H160 und Twin Otter stehen als regional bereitgestellte Maschinen am jeweiligen A320-Stopp zur Verfügung. Du fliegst jede Ausflugsschleife vollständig und steigst danach am selben Ort wieder in den Fenix. Überführungen dieser Zusatzmaschinen zwischen den Regionen gehören nicht zur Tour.'
E['fleetNote'] = 'Vier Twin-Otter-Ausflüge: St. Barth, Montserrat, Antarktis und Tuvalu. Zwölf H160-Ausflüge ergänzen die übrigen Kategorien. Die 403 A320-Legs bleiben in ihrer Reihenfolge und Nummerierung erhalten.'
(R/'excursions.json').write_text(json.dumps(E, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
print('Fleet finalized:', len(E['excursions']), 'loops;', sum(len(e['legs']) for e in E['excursions']), 'side legs')
print('Retired IDs:', [l['id'] for l in E['retiredLegs']])
for e in E['excursions']:
    print(e['country'], e['profile'], [(l['nm'], l['airMin']) for l in e['legs']])
