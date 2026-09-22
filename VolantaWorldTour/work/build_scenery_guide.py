"""Scenery overlay only: preserve the fixed route and all progress identifiers."""
import json
from pathlib import Path
from collections import Counter

R = Path(__file__).resolve().parent
def read(name):
    return json.loads((R/name).read_text(encoding='utf8'))
def write(name, value):
    (R/name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf8')

D, X, B = read('tour-data.json'), read('excursions.json'), read('briefings.json')
F = read('freeware-research.json')
route_before = json.dumps([D['legs'], X['excursions']], sort_keys=True)
owned = {a['icao']: a['manufacturer'] for a in D['inventory']}
base_standard = set('KASE WX53 SPGL LFLJ EIDL HUEN LPMA LXGB LOWI KLAX VNLK KEB KJFK KMCO LFPG VQPR NZQN SEQM SBGL TNCS TFFJ KSEA KSEZ MRSN CZST YSSY KTEX RJTT MHTG CYTZ TNCM'.split())
base_deluxe = set('EHAM HECA FACT KORD LEMD'.split())
base_premium = set('KDEN OMDB EDDF EGLL KSFO'.split())
base_all = base_standard | base_deluxe | base_premium
base_source = D['sources']['base']
base_2024 = ['MSFS-Team: handgefertigte Airports in MSFS 2024', 'https://forums.flightsimulator.com/t/what-will-the-handcrafted-airports-be-in-2024/655446']
for code, a in D['airports'].items():
    if code == 'YAYE' and a['scenery'] == 'base':
        a.update(scenery='default', sceneryLabel='Standard / Szenerie prüfen', scenerySource='oa')
    if code in base_all and a['scenery'] == 'default':
        a.update(scenery='base', sceneryLabel='Handcrafted · Basis/Edition', scenerySource='base')
for code, a in X['points'].items():
    if code in D['airports']:
        a.update({k:D['airports'][code][k] for k in ['scenery', 'sceneryLabel', 'scenerySource']})
    elif code in owned:
        a.update(scenery='owned', sceneryLabel='Eigene Szenerie · '+owned[code], scenerySource='inventory')
    elif code in base_all:
        a.update(scenery='base', sceneryLabel='Handcrafted · Basis/Edition', scenerySource='base')
for b in B.values():
    for k in ['purchase', 'buyUrl', 'buyReason']:
        b.pop(k, None)

products = {
 'SPZO': {
    'developer':'FSDG', 'name':'Cusco · MSFS 2020/2024', 'airport':'SPZO',
    'headline':'Der Anflug, die Hanglage und die Stadt.',
    'reason':'Eigene Geländedaten, die markante geneigte Piste und zusätzliche Stadtobjekte greifen genau die Besonderheiten dieses Anden-Anflugs auf. Gegenüber der Basis und den gefundenen punktuellen Freeware-Ergänzungen ist hier ein außergewöhnlicher szenischer Mehrwert plausibel: meine dritte optionale Kauf-Ausnahme.',
    'evidence':'Etablierter Entwickler. Produktumfang und 2024-Ausgabe sind belegt; FSAddonCompare listet 4,58/5 aus 40 Bewertungen. Verifizierte Käufer loben insbesondere Airport, Stadt und Anflug. Die Wertung umfasst auch ältere Versionen und ist kein eigener A/B-Test.',
    'caveat':'Ältere Ursprungsszenerie. Frühere Berichte zu statischen Flugzeugen und fehlenden Jetways stehen späteren Korrekturmeldungen gegenüber. Aktuelle 2024-Ausgabe installieren und Navdaten/Pistenprofil im Fenix vor dem Tourflug prüfen; keine Garantie für jede Add-on-Kombination.',
    'baseline':'Optional. Ohne Kauf die MSFS-Basis nutzen; der anspruchsvolle geografische Anflug bleibt auch dann erhalten.',
    'compatibility':'2024-Version laut FSDG-Versionsliste ab 1.6. Je nach Shop Installation über Aerosoft One.',
    'links':[
      ['Produktumfang & Plattformen','https://www.justflight.com/product/fsdg-cusco-msfs'],
      ['FSDG · aktueller Versionsstand','https://fsdg-online.com/Version-History-Addon-list%3A_%3A16.html'],
      ['Verifizierte Käuferberichte','https://secure.simmarket.com/fsdg-cusco-msfs.phtml'],
      ['FSDG-Support · Hinweis auf korrigierte 2024-Jetways','https://forum.flightsimdevelopmentgroup.com/viewtopic.php?t=3660'],
      ['FSAddonCompare · Angebote & Bewertungen','https://www.fsaddoncompare.com/search/SPZO']
    ]
 },
 'TFFJ': {
    'developer':'SLH Sim Designs', 'name':'Saint Barths · MSFS 2024', 'airport':'TFFJ',
    'headline':'Der Sattel wird Teil des Erlebnisses.',
    'reason':'Überarbeitete Hügelneigung und Geländehöhen betreffen genau den berühmten Endanflug. Dazu kommen die Straße mit Verkehr, Spotter, Strände sowie Gustavia und Eden Rock. Der Mehrwert liegt für deinen H160-Ausflug in der Landschaft rund um den Airport; der berühmte Pistenanflug ist kein H160-Pflichtprogramm.',
    'evidence':'Bewusste Ausnahme für einen kleineren Hersteller: sehr begeistertes ausführliches Nutzerreview im MSFS-Forum und weitere positive Besitzerstimmen. FSAddonCompare zeigt 5,0/5 bei 9 Bewertungen (21.09.2026); die Stichprobe ist klein.',
    'caveat':'Der Nutzerreview berichtet trotz starker Hardware von gelegentlichem Stottern. Empfehlung nur mit ausreichender Leistungsreserve; keine eigene Performance-Messung. Der Reviewautor bietet zudem einen Rabattcode an.',
    'baseline':'Enthaltenes handgefertigtes TFFJ zuerst ansehen; das Add-on bleibt optional.',
    'compatibility':'Die ausdrücklich als MSFS 2024 angebotene Ausgabe wählen.',
    'links':[
      ['Hersteller · Funktionen & 2024-Ausgabe','https://www.slhsimdesigns.com/products/saintbarths24'],
      ['Ausführlicher Nutzerreview','https://forums.flightsimulator.com/t/review-slh-sim-designs-st-barts-gustaf-iii-tffj-fs2024/745550'],
      ['FSAddonCompare · Preise & Bewertungen','https://www.fsaddoncompare.com/product/12222/TFFJ-SAINT-BARTHS']
    ]
 },
 'VHHH': {
    'developer':'iniBuilds', 'name':'Hong Kong + City Landmarks · MSFS 2024', 'airport':'VHHH',
    'headline':'Ein Flughafen mit einer ganzen Stadtkulisse.',
    'reason':'Die Kombination aus aktuellem Flughafenlayout und City Landmarks macht dieses Paket interessant. Der zusätzliche Wert liegt in den markanten Stadtansichten rund um Victoria Harbour und der Umgebung des Airports, die einen Hongkong-Besuch prägen können.',
    'evidence':'Namhafter Hersteller, ausdrücklich für MSFS 2024. Besitzerberichte loben Detailgrad und Leistung im Verhältnis zur Größe. Das ist Nutzerfeedback, kein eigener Vergleichstest; eine belastbare aggregierte Bewertung der iniBuilds-Ausgabe liegt hier nicht vor.',
    'caveat':'Die Skyline liegt nicht auf jedem VHHH-Anflug. Besonders empfehlenswert, wenn du auch die Stadtkulisse ansehen möchtest; für einen reinen Airport-Turnaround kein notwendiger Kauf. Berichte nennen außerdem weiterhin Autogen in Teilen der Umgebung.',
    'baseline':'Ohne Neukauf die MSFS-Basis verwenden. City Landmarks sind laut Hersteller beim Airport-Kauf enthalten; Einlösebedingungen im Shop beachten und nicht zusätzlich bezahlen.',
    'compatibility':'Native MSFS-2024-Ausgabe. Airport und City Landmarks sind getrennte Installationspakete.',
    'links':[
      ['Hersteller · Airport & enthaltenes City-Paket','https://inibuilds.com/products/inibuilds-hong-kong-vhhh-msfs-2024'],
      ['Hersteller · City Landmarks','https://inibuilds.com/products/inibuilds-hong-kong-city-landmarks-msfs-2024'],
      ['Besitzerberichte zum Airport','https://forums.flightsimulator.com/t/released-inibuilds-hong-kong-vhhh-fs2024/758460?page=2'],
      ['Weitere Rückmeldungen zur Umgebung','https://forums.flightsimulator.com/t/released-inibuilds-hong-kong-vhhh-fs2024/758460'],
      ['FSAddonCompare · aktueller Preisvergleich','https://www.fsaddoncompare.com/product/13397/Hong-Kong-VHHH']
    ]
 }
}

considered = {
 'EKVG': {
   'candidate':'MK-STUDIOS Vágar v2 · MSFS 2024',
   'reason':'Kein Neukauf empfohlen. Die gut bewertete Freeware von superspud ist jetzt die bevorzugte Erweiterung. Ein außergewöhnlicher Mehrwert der MK-STUDIOS-Ausgabe gegenüber dieser kostenlosen Alternative ist hier nicht ausreichend belegt.',
   'links':[['Geprüfter Produktumfang','https://orbxdirect.com/product/mkstudios-ekvg-msfs2024'],D['sources']['wu15']]
 },
 'VQPR': {
   'candidate':'FSDG Paro · MSFS',
   'reason':'Kein Neukauf empfohlen. Das gut bewertete Remake von kychungdotcom ergänzt Paro kostenlos; die enthaltene handgefertigte Fassung bleibt eine einfache Alternative. Ein außergewöhnlicher Mehrwert des FSDG-Kaufs ist hier nicht ausreichend belegt.',
   'links':[['Geprüfter Produktumfang & Plattformen','https://www.justflight.com/product/fsdg-paro-msfs'],base_source,base_2024]
 },
 'ENSB': {
   'candidate':'iniBuilds Svalbard · MSFS 2024',
   'reason':'Den handgefertigten Airport aus World Update V verwenden. Eine weitere Umsetzung von Terminal und lokalen Objekten rechtfertigt für diesen Tour-Stopp noch keinen zusätzlichen Kauf nach deinem strengen Mehrwert-Kriterium.',
   'links':[D['sources']['wu5'],['iniBuilds · Svalbard-Produktumfang','https://forum.inibuilds.com/topic/34027-inibuilds-svalbard-longyear-ensb-for-microsoft-flight-simulator-2024-released/']]
 },
 'FSIA': {
   'candidate':'FSDG Seychelles · MSFS',
   'reason':'Vorerst Basis. Die aktuelle FSDG-Fassung 1.6 enthält ausdrücklich eine 2024-Ausgabe; ältere Terrainberichte sind deshalb kein belastbarer Ausschlussgrund für diese Version. Das Paket mit Inseln, Riffen und weiteren Pisten ist thematisch stark, sein erheblicher Zusatzumfang wird durch den einzelnen FSIA-Stopp aber nur teilweise genutzt. Keine ausreichend belegte zusätzliche Kauf-Ausnahme für die feste Route.',
   'links':[['FSDG · Umfang und 2024-Ausgabe','https://fsdg-online.com/Sceneries/MSFS/MSFS-Full/Seychelles-MSFS%3A%3A64.html'],['FSDG · Versionsübersicht','https://fsdg-online.com/Version-History-Addon-list%3A_%3A16.html']]
 },
 'VRMM': {
   'candidate':'FSDG Maldives · Airport und Malé-Atolle',
   'reason':'Das regionale Paket ist ein interessanter Kandidat, aber kein weiterer Kauf ausgewählt. Die gelesenen Paketbewertungen streuen; die aktuelle Versionsliste meldet 2024-Texturkorrekturen. Für den festen A320-Stopp ist der zusätzliche Nutzen der vielen Resorts nicht hinreichend belegt. Frühere Fehlerberichte werden nicht als Nachweis gegen die korrigierte Ausgabe behandelt.',
   'links':[['Hersteller · Gesamtpaket','https://fsdg-online.com/Sceneries/MSFS/MSFS-Full/Maldives-VRMM-The-Male-Atolls-Big-Bundle-MSFS%3A%3A97.html'],['Aktuelle Fassungen & Korrekturen','https://fsdg-online.com/Version-History-Addon-list%3A_%3A16.html'],['Getrennte Produktbewertungen','https://www.fsaddoncompare.com/search/VRMM']]
 },
 'NZWN': {
   'candidate':'Flightbeam Wellington',
   'reason':'Namhafter Hersteller und sehr positive Käuferstimmen. Der belegte Umfang konzentriert sich auf die detaillierte Airportumsetzung. Ein außergewöhnlicher zusätzlicher Landschafts-/Anfluggewinn, der deinen strengen Kaufmaßstab sicher erfüllt, ist daraus noch nicht abzuleiten. Deshalb keine weitere Kaufempfehlung.',
   'links':[['Flightbeam · Produkt und Käuferberichte','https://shop.flightbeam.net/products/flightbeam-nzwn-msfs']]
 },
 'SCRM': {
   'candidate':'Antarktis-Pakete mit anderer Abdeckung',
   'reason':'Die konkrete SCRM-Landestelle vorab in MSFS 2024 prüfen. Aerosoft Antarctica Vol. 1 mit Rothera, Fossil Bluff und Sky Blu deckt das hier benötigte SCRM nicht ab. Deshalb keine Kaufempfehlung allein wegen des Namens „Antarktis“. Eine geeignete SCRM-Payware ist für diese Auswahl nicht verifiziert.',
   'links':[['Aerosoft · tatsächliche Abdeckung von Vol. 1','https://www.aerosoft.com/en/shop/flight/microsoft-flight-simulator/msfs-2020/msfs-sceneries/msfs-antarctica/3573/aerosoft-antarctica-vol.-1-british-rothera-and-beyond']]
 }
}

M = read('maker-review.json')
products.update(M['products'])
considered.update(M['considered'])
for code in products:
    considered.pop(code, None)
products['SPZO']['reason'] = products['SPZO']['reason'].replace(': meine dritte optionale Kauf-Ausnahme', '')

points = {**X['points'], **D['airports']}
order = ['EDLV']
for leg in D['legs']:
    order.extend([leg['from'],leg['to']])
    for ex in X['excursions']:
        if ex['afterLeg'] == leg['id']:
            order.extend(ex['route'])
order = list(dict.fromkeys(order))
assert set(order) == set(points)
verify = {
 'LLJR':'Geschlossener Flughafen: eine passende historische oder fiktive Darstellung ist erforderlich. Keine konkret verifizierte Szenerie-Kaufempfehlung; Landestelle und Volanta-Erkennung bleiben vorab zu prüfen.',
 'SCRM':'SCRM muss in deiner MSFS-2024-Installation als nutzbare Piste vorhanden sein. Darstellung und Untergrund vor dem langen Antarktisflug prüfen.',
 'FMZJ':'Abgelegene Inselpiste: Darstellung, Vegetation und nutzbare Landefläche in MSFS 2024 vorab prüfen.',
 'NFSW':'Kleine Inselpiste: nutzbare Landefläche und Darstellung vor dem Tuvalu-Ausflug in MSFS 2024 prüfen.',
 'NFNR':'Abgelegener Tankstopp: nutzbare Piste vor dem Tuvalu-Ausflug in MSFS 2024 prüfen.',
 'FMMO':'Vorgesehener Zwischenstopp: Piste und Darstellung für den H160-Ausflug vorab prüfen.',
 'LIKD':'Kleiner Flugplatz: tatsächliche MSFS-2024-Landefläche vor dem H160-Ausflug prüfen.',
 'VA-0001':'Die exakt geplante Heliport-Position in MSFS 2024 prüfen. Ein Stadt- oder Rom-Paket belegt noch keinen nutzbaren Vatikan-Heliport.',
 'LNMC':'Heliport und seine Landeflächen vorab in MSFS 2024 prüfen. Kein Kauf nur für eine schönere Stadtfassade empfohlen.',
 'AD-ALV':'Die exakt geplante Heliport-Position prüfen; eine Andorra-Landschaft allein belegt keine passende Landefläche.',
 'LSXB':'Den vorgesehenen Heliport und seine Landefläche vorab in MSFS 2024 prüfen.'
}
guide = {}
for i, code in enumerate(order):
    a=points[code]
    baseline=a.get('scenery','default')
    links=[]
    if code in owned:
        mode='owned';name=f"{owned[code]} · {code} (vorhanden)"
        reason='Deine vorhandene Szenerie verwenden. Kein weiteres Produkt für denselben Airport empfohlen.'
        note='Besitz laut deiner CSV; installierte Ausgabe, Updates und MSFS-2024-Kompatibilität sind dadurch nicht bestätigt.'
        evidence='Bestandsabgleich'
    elif baseline=='wu':
        mode='included';name=a['sceneryLabel']
        reason='Den handgefertigten World-Update-Airport verwenden. Kein zusätzlicher Airport-Kauf ausgewählt.'
        note='Das zugehörige kostenlose Update im MSFS-2024-Inhaltsmanager aktivieren bzw. bereitstellen.'
        evidence='Offizielle Airport-Liste';links=[D['sources'][a['scenerySource']]]
    elif baseline=='base' or code in base_all:
        mode='included';name='MSFS · handgefertigter Basis-/Edition-Airport'
        reason='Zuerst die enthaltene handgefertigte Fassung verwenden. Kein zusätzlicher Airport-Kauf ausgewählt.'
        edition='Deluxe oder höher' if code in base_deluxe else 'Premium Deluxe oder höher' if code in base_premium else 'Basis-Inhalt'
        note=f'{edition}; Verfügbarkeit und Aktivierung in deiner konkreten MSFS-2024-Edition prüfen.'
        evidence='Offizielle Basis-Liste & 2024-Übernahme';links=[base_source,base_2024]
    else:
        mode='default';name='MSFS 2024 · Basisdarstellung'
        reason='Die Basisdarstellung zuerst verwenden. Für diesen Stopp ist kein Neukauf mit belegtem außergewöhnlichem Mehrwert ausgewählt.'
        note='Keine vertiefte Einzelbewertung aller erhältlichen Add-ons. Das bedeutet nicht, dass es keine guten Erweiterungen gibt.'
        evidence='Konservative Auswahlregel'
    if code in verify:
        mode='verify';name='MSFS-Landestelle vorab prüfen';reason=verify[code]
        note='Keine konkret verifizierte Kaufempfehlung; Verfügbarkeit der nötigen Darstellung bleibt offen.'
        evidence='Darstellung noch zu prüfen'
    if code == 'TNCM':
        name='MSFS · handgefertigtes TNCM (40th Anniversary)'
        reason='Die bereits enthaltene handgefertigte Fassung nutzen. Für den Maho-Anflug ist deshalb kein zusätzlicher Airport-Kauf nötig.'
        note='In MSFS 2024 in der Bibliothek nach Princess suchen und das TNCM-Basispaket aktivieren; World Update Caribbean allein ersetzt dieses Paket nicht.'
        evidence='Offizielle SU11-Liste & 2024-MSFS-Team-Bestätigung'
        links=[['MSFS · 40th Anniversary','https://www.flightsimulator.com/release-notes-for-40th-anniversary-edition-sim-update-11-1-29-27-0-now-available/'],['MSFS-Team · TNCM in 2024','https://forums.flightsimulator.com/t/what-happened-to-tncm/739561']]
    if code in considered:
        reason=considered[code]['reason'];links+=considered[code]['links'];evidence='Kaufkandidat gezielt geprüft'
    if code in products:
        mode='buy';name=products[code]['developer']+' · '+products[code]['name']
        reason=products[code]['reason'];note=products[code]['baseline'];links=products[code]['links'];evidence='Begründete optionale Ausnahme'
    if code in F['selected']:
        f=F['selected'][code]
        assert code not in owned and code not in products
        assert f['rating']>=4.8 and f['reviews']>=20 and f['downloads']>=10000
        mode='freeware';name=f['developer']+' · '+f['name']
        reason=f['reason'];note=f['fallback'];links=f['links'];evidence='Freeware · Resonanz und 2024-Belege geprüft'
    guide[code]={'code':code,'name':a['name'],'country':next((c['name'] for c in D['countries'] if c['code']==a['country']),a['country']),'order':i,'mode':mode,'recommendation':name,'reason':reason,'note':note,'evidence':evidence,'links':list(dict.fromkeys(tuple(l) for l in links)),'baseline':baseline,'product':code if code in products else None,'freeware':code if code in F['selected'] else None}

for code, p in M['provenance'].items():
    g = guide[code]
    g['recommendation'] = p['developer']+' · '+code+' (vorhanden)'
    g['note'] += ' Herstellerzuordnung geprüft: '+p['developer']+'. Aktuell gelisteter Produktstand '+p['version']+'; das bestätigt nicht deine installierte Version.'
    g['links'].append(['Hersteller · Entwickler und Version',p['url']])

assert len(guide)==405
assert Counter(g['mode'] for g in guide.values())['owned']==39
assert not (set(products)&set(owned))
assert json.dumps([D['legs'], X['excursions']], sort_keys=True)==route_before
write('tour-data.json',D);write('excursions.json',X);write('briefings.json',B)
write('scenery-guide.json', {'date':'2026-09-21','airports':guide,'products':products,'freeware':F['selected'],'freewareConsidered':F['considered'],'freewarePolicy':F['policy'],'freewareMetricsNote':F['metricsNote'],'considered':considered,'order':order,'counts':Counter(g['mode'] for g in guide.values())})
print('Scenery guide:',len(guide),'airports;',dict(Counter(g['mode'] for g in guide.values())))
