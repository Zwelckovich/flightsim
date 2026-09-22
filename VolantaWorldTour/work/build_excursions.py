"""Mixed-aircraft loops; preserve the original 403 main-leg IDs and progress."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parent
D=json.loads((R/'tour-data.json').read_text(encoding='utf8'))
A={a['ident']:a for a in csv.DictReader((R/'airports.csv').open(encoding='utf8'))}
for a in list(A.values()):
    if a['icao_code']:A[a['icao_code']]=a
A['LLJR']={**A['IL-0023'],'iso_country':'PS'} # Volanta UI: Palestine (PS); closed historical airport.
RW=list(csv.DictReader((R/'runways.csv').open(encoding='utf8')))
# country, route, aircraft, assumed cruise kt, theme, briefing
S=[
('GG','EGJJ EGJB EGJJ','ATR 42',250,'Kanalinseln im Tiefflug','Kurzer Inselwechsel über den Ärmelkanal. Anflug über die Küste; böiger Seewind und die relativ kurze Bahn verlangen eine saubere Landekonfiguration.'),
('VG','TIST TUPJ TIST','ATR 42',250,'Inseln der Sir Francis Drake Channel','Buchten und Inselketten auf dem Weg nach Beef Island. Die Bahn liegt am Wasser, das Gelände steigt westlich an. Anflug und Landemasse vorab prüfen.'),
('AI','TNCM TQPF TNCM','ATR 42',250,'Zwei Inseln, zwei Kategorien','Kurzer Sprung über den Anguilla Channel. Küste und Riffe sind bei klarer Mittagssonne am besten sichtbar. Der Besuch auf Anguilla ergänzt einen eigenen Länderpunkt.'),
('BL','TNCM TFFJ TNCM','DHC-6 Twin Otter',150,'Über den Hügel von Saint-Barth','Der bekannte Anflug auf Bahn 10 führt über den Hügel und die Straße, danach zur kurzen Piste an der Bucht. Nur nach eigenem Sichtanflugbriefing; lieber durchstarten als eine zu schnelle Landung erzwingen.'),
('MF','TNCM TFFG TNCM','DHC-6 Twin Otter',150,'Grand Case & die französische Inselhälfte','Anflug über Küste und türkisfarbenes Wasser, Berge im Hinterland. Der Transfer liefert einen eigenen Saint-Martin-Besuch; Princess Juliana auf der niederländischen Seite allein deckt ihn nicht ab.'),
('MS','TAPA TRPG TAPA','DHC-6 Twin Otter',150,'Montserrat: Klippen und Vulkaninsel','Kurze Bahn direkt an der Steilküste. Für eine optionale Landschaftsrunde den Vulkan nur mit großzügigem Abstand betrachten; reale Sperrzonen und im Simulator passende Verfahren berücksichtigen.'),
('DM','TFFR TDPD TFFR','ATR 42',250,'Grüne Berge, Flussmündung, Küstenanflug','Douglas-Charles liegt zwischen bewaldeten Höhenzügen und Meer. Gerade der Übergang vom Wasser zur schmal wirkenden Bahn macht diesen Abstecher reizvoll. Aktuelle Pistenlänge und Verfahren im Simulator prüfen.'),
('AQ','SAWH SCRM SAWH','DHC-6 Twin Otter',150,'Expedition über die Drake-Passage','King George Island: karge Küste, Eis, Stationen und Schotterpiste. Südlichen Sommer und klares Tageslicht wählen. Die Überwasserstrecke ist bewusst eine lange Ausnahme; Nutzlast, Reichweite mit Reserven, Wetter und Betankung am Expeditionsziel separat planen. Keine real verfügbare Treibstoffversorgung zugesichert.'),
('TV','NFFN NGFU NFFN','ATR 42',250,'Eine Landebahn mitten im Atoll','Funafuti ist ein schmales Atoll: Meer auf der einen, Lagune auf der anderen Seite. Die Perspektive im Endanflug ist das Highlight. Auf der langen Überwasserverbindung sind Wind, Reichweite und Reserven besonders relevant.'),
('PS','LLBG LLJR LLBG','Cessna 172',110,'Historischer Flug nach Jerusalem/Atarot','Volanta führt LLJR/Jerusalem als Palestine (PS). Der Platz ist geschlossen: Dieser Ausflug ist ausdrücklich fiktiv und setzt eine passende historische oder selbst ergänzte Simulator-Landestelle voraus. Im Anflug steigt das Gelände von der Küstenebene zum Bergland an. Die Kategorie folgt hier Volantas Zuordnung; sie ist keine geopolitische Einordnung des Karten-Datensatzes.'),
('TF','FMNN FMNM FMZJ FMNM FMNN','DHC-6 Twin Otter',150,'Juan de Nova: Riffinsel im Mosambikkanal','Über Mahajanga/Amborovy als Versorgungsstopp zur abgelegenen Insel Juan de Nova. Lagon, Korallenriff und isolierte Landebahn. Die Insel gehört zu den TAAF; FMNM teilt die Strecke in kurze Flüge. Pistenoberfläche, nutzbare Länge und Treibstoffversorgung sind vor dem Expeditionsflug zu prüfen.'),
('SM','LIRF LIKD LIRF','Cessna 172',110,'Torraccia & der Monte Titano','Vom Raum Rom über das Hügelland nach Torraccia. Kurze Grasbahn und abwechslungsreiche Topografie; Leistung und Bodenzustand passend zur gewählten C172 planen. Ein optionaler Rundflug zeigt die Silhouette des Monte Titano.'),
('VA','LIRF VA-0001 LIRF','Airbus H125',115,'Rom & die Vatikanischen Gärten','Kurzer Helikopterflug zum tatsächlichen Vatikan-Heliport in den Gärten. Petersdom und Stadtpanorama sind POIs für eine optionale Runde, kein behauptetes offizielles Anflugverfahren. Szenerieposition und Hindernisse vor der Landung prüfen.'),
('MC','LFMN LNMC LFMN','Airbus H125',115,'Die Côte d’Azur entlang nach Monaco','Küstenflug mit Cap Ferrat, Eze und der dichten Bebauung Monacos. Der Heliport liegt direkt am Meer; Küstenwind, Hindernisse und Abbruchmöglichkeit im Anflug berücksichtigen.'),
('AD','LEBL AD-ALV LEBL','Airbus H125',115,'Vom Mittelmeer in die Pyrenäen','Andorra la Vella liegt im engen Gebirgstal. Den Talverlauf nutzen; die Kartenlinie ist nur eine Verbindung der Orte. Wolkenuntergrenzen, Bergwind, Leistung in der Höhe und Hindernisse am Heliport machen diesen kurzen Flug anspruchsvoll.'),
('LI','LSZH LSXB LSZH','Airbus H125',115,'Walensee, Rheintal & Burg Gutenberg','Über Walensee und das Alpenrheintal nach Balzers. Burg Gutenberg ist ein guter POI nahe dem Ziel. Tiefe Wolken und Föhn können den Talflug erschweren; POI-Schleifen verlängern die Schätzung.'),
]

def point(code):
    if code in D['airports']:
        a=D['airports'][code]
        return {**a,'ident':code,'type':'airport'}
    a=A[code]
    rs=[r for r in RW if r['airport_ident']==a['ident'] and r['closed']=='0' and r['length_ft']]
    r=max(rs,key=lambda r:float(r['length_ft']),default={})
    return {'ident':code,'icao':code,'name':a['name'],'city':a['municipality'],'country':a['iso_country'],'lat':float(a['latitude_deg']),'lon':float(a['longitude_deg']),'type':a['type'],'elevation':round(float(a['elevation_ft'] or 0)),'runway':round(float(r['length_ft'])*.3048) if r else None,'surface':r.get('surface') or 'unbekannt','url':f"https://ourairports.com/airports/{a['ident']}/",'sceneryLabel':'Szenerie / Basisdarstellung in MSFS 2024 prüfen'}
def distance(a,b):
    p,q=map(math.radians,[a['lat'],b['lat']]);dl=math.radians(b['lon']-a['lon'])
    return 3440.065*2*math.asin(math.sqrt(math.sin((q-p)/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2))
points={c:point(c) for s in S for c in s[1].split()}
excursions=[]
for code,route,aircraft,kt,title,brief in S:
    seq=route.split();anchor=seq[0];after=next(l for l in D['legs'] if l['to']==anchor)
    ls=[]
    for i,(x,y) in enumerate(zip(seq,seq[1:]),1):
        nm=round(distance(points[x],points[y]));t=max(12,round(12+nm*1.10/kt*60))
        ls.append({'id':f'X-{code}-{i}','from':x,'to':y,'nm':nm,'airMin':t,'over2h':t>120})
    excursions.append({'id':code,'country':code,'countryName':next(c['name'] for c in D['countries'] if c['code']==code),'route':seq,'aircraft':aircraft,'cruiseKt':kt,'title':title,'briefing':brief,'anchor':anchor,'afterLeg':after['id'],'chapter':after['chapter'],'target':next(c for c in seq if points[c]['country']==code),'legs':ls,'verification':'Geografisch zugeordnet; Wertung nach abgeschlossenem Flug prüfen.','conditional':False,'scenery':'Kein zusätzliches Add-on zugesichert. Landeplatz in deiner MSFS-2024-Weltkarte und Szenerie prüfen; Kennungen können abweichen.'})
    e=excursions[-1]
    if code in ['PS','VA','TF','AD']:
        e['verification']=f"Am 21.09.2026 direkt in Volantas Flughafenansicht geprüft: {e['target']} gehört dort zu {e['countryName']}. Länderpunkt nach abgeschlossenem Flug kontrollieren."
    if code=='PS':
        e['historical']=True
        e['scenery']='Geschlossener historischer Platz. Kein funktionierendes MSFS-2024-Add-on verifiziert. Vor dem Tourabschnitt eine landbare historische/fiktive Darstellung von LLJR und ihre Erkennung durch Volanta testen. Kennung und Position müssen zusammenpassen.'
excursions.sort(key=lambda x:x['afterLeg'])
E={'version':1,'points':points,'excursions':excursions,'formula':'Flugzeit ≈ 12 min + Großkreisdistanz × 1,10 / typbezogene Reisegeschwindigkeit × 60; mindestens 12 min. Ohne Wind, Geländeumwege und POI-Runden. Keine Blockzeitberechnung.','verificationDate':'2026-09-21','note':'Alle 245 Kategorien haben einen geografischen Zielvorschlag. Das ist keine Garantie für die Volanta-Wertung oder für einen vollständig modellierten Landeplatz in MSFS 2024.'}
(R/'excursions.json').write_text(json.dumps(E,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Excursions',len(excursions),'legs',sum(len(e['legs']) for e in excursions),'hours',round(sum(l['airMin'] for e in excursions for l in e['legs'])/60,1))
for e in excursions:print(e['country'],e['afterLeg'],' > '.join(e['route']),[l['airMin'] for l in e['legs']])
