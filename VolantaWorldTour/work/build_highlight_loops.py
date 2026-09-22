"""Use the three owned scenery highlights that the A320 cannot serve."""
from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parent
E=json.loads((R/'excursions.json').read_text(encoding='utf8'))
D=json.loads((R/'tour-data.json').read_text(encoding='utf8'))
A={a['ident']:a for a in csv.DictReader((R/'airports.csv').open(encoding='utf8'))}
RW=list(csv.DictReader((R/'runways.csv').open(encoding='utf8')))
E['excursions']=[e for e in E['excursions'] if e.get('categoryVisit',True)]
manual='https://flightsimulator.azureedge.net/wp-content/uploads/2024/11/MSFS2024_DHC-6_TWIN_OTTER_AOM.pdf'
S=[
 dict(target='EGLC',anchor='EGLL',displayName='London City',title='Zwischen Skyline und Royal Docks',experience='Die schmale Flughafeninsel in den Royal Docks, das Wasser neben der Bahn und die Stadtkulisse machen deinen UK2000-Airport zu einem eigenständigen Highlight.',timing='Bei Tageslicht und klarer Sicht. Die London-City-Verfahren vorab lesen; bei passendem Wetter einen vorbereiteten Simulator-Sichtanflug fliegen. Es wird keine reale Steilanflugzulassung der Twin Otter behauptet.',briefing='Kurzer Abstecher von Heathrow nach London City und zurück. Die direkte Kartenlinie führt über Stadtgebiet; sie ist weder eine freigegebene VFR-Strecke noch ein Instrumentenanflug. Höhe, Hindernisse und Anflugweg bewusst vorbereiten.',source=['London City: Anforderungen an zugelassene Flugzeuge','https://privatejetcentre.londoncityairport.com/services/approved-aircraft/application-process/']),
 dict(target='KSEZ',anchor='KPHX',displayName='Sedona',title='Auf dem Tafelberg zwischen roten Felsen',experience='Aus der Wüstenlandschaft Arizonas hinauf zum auf einer Mesa gelegenen Flugplatz. Der Anflug auf die erhöhte Bahn und die roten Felsformationen ringsum sind das Motiv für deine XCodr-Szenerie.',timing='Frühes Morgenlicht oder spätes Nachmittagslicht bei guter Sicht. Bei großer Hitze die Dichtehöhe berücksichtigen; Wind an der Mesa und Leistungswerte der Twin Otter prüfen.',briefing='Von Phoenix nach Sedona und zurück. Für den Landschaftseindruck zählt der Übergang vom Tal zum hoch gelegenen Flugplatz. Keine knappe Landung erzwingen: aktuelle Platzdaten und Start-/Landemasse gehören ins Briefing.',source=['Sedona Airport: Lage auf der Mesa','https://sedonaairport.org/']),
 dict(target='NZMF',anchor='NZQN',displayName='Milford Sound',title='Fjordwände, Wasserfälle und die kurze Bahn',experience='Queenstown, alpine Täler und schließlich der Fjord zwischen steilen Felswänden: Milford Sound ist einer der stärksten Landschaftsstopps dieser Reise. Deine Blinn-Szenerie bekommt einen festen Besuch mit der Twin Otter.',timing='Nur mit klaren Bergkämmen und ausreichend Sicht im Tal. Berge und Fjord begrenzen den Anflug; CAA-Milford-Briefing und aktuelle Platzverfahren lesen. Ein klarer Tag ist hier wertvoller als dramatisch tiefe Wolken.',briefing='Von Queenstown nach Milford Sound und zurück. Die Großkreislinie ist ausdrücklich keine durchfliegbare Talroute. Den Weg über geeignete Täler/Pässe selbst anhand Gelände, Wetter und Verfahren vorbereiten. Die Flugzeitschätzung wurde auf 45 Minuten je Richtung angehoben; POI-Runden können länger dauern.',source=['CAA New Zealand: In, out and around Milford','https://www.aviation.govt.nz/assets/publications/gaps/gap-in-out-and-around-milford-web.pdf'])
]
for spec in S:
 target,anchor=spec['target'],spec['anchor']
 a=A[target];rs=[r for r in RW if r['airport_ident']==target and r['closed']=='0' and r['length_ft']]
 rw=max(rs,key=lambda r:float(r['length_ft']),default={})
 item=next(i for i in D['inventory'] if i['icao']==target)
 E['points'][target]={'ident':target,'icao':target,'name':a['name'],'city':a['municipality'],'country':a['iso_country'],'lat':float(a['latitude_deg']),'lon':float(a['longitude_deg']),'type':a['type'],'elevation':round(float(a['elevation_ft'] or 0)),'runway':round(float(rw['length_ft'])*.3048) if rw else None,'surface':rw.get('surface','unbekannt'),'url':f'https://ourairports.com/airports/{target}/','sceneryLabel':f'Eigenes Add-on · {item["manufacturer"]}'}
 E['points'][anchor]={**D['airports'][anchor],'ident':anchor,'type':'airport'}
 after=next(l for l in D['legs'] if l['to']==anchor)
 e={**spec,'id':'BONUS-'+target,'country':a['iso_country'],'countryName':next(c['name'] for c in D['countries'] if c['code']==a['iso_country']),'route':[anchor,target,anchor],'aircraft':'DHC-6-300 Twin Otter · Räder','profile':'DHC6','cruiseKt':150,'afterLeg':after['id'],'chapter':after['chapter'],'categoryVisit':False,'conditional':False,'scenery':f'Dein vorhandenes Add-on: {item["manufacturer"]}, aus MSFS Airports - Addons.csv. Installation und MSFS-2024-Kompatibilität vor dem Besuch prüfen.','verification':'Zusätzlicher Highlight-Stopp in einer bereits durch den A320 abgedeckten Volanta-Kategorie.','fuelNote':'Am A320-Ausgangspunkt für Hin- und Rückflug plus Reserven tanken. Eine Betankung am Ausflugsziel wird nicht vorausgesetzt. Nutzlast, Wetter und tatsächlichen Verbrauch separat prüfen.','sources':[['MSFS 2024: DHC-6-300 Handbuch',manual],spec['source']]}
 e.pop('source')
 e['legs']=[]
 for i,(x,y) in enumerate(zip(e['route'],e['route'][1:]),1):
  p,q=map(math.radians,[E['points'][x]['lat'],E['points'][y]['lat']]);dl=math.radians(E['points'][y]['lon']-E['points'][x]['lon'])
  nm=round(3440.065*2*math.asin(math.sqrt(math.sin((q-p)/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2)))
  t=45 if target=='NZMF' else max(12,round(12+nm*1.1/150*60))
  e['legs'].append({'id':f'X-BONUS-{target}-{i}','from':x,'to':y,'nm':nm,'airMin':t,'over2h':t>120})
 E['excursions'].append(e)
E['excursions'].sort(key=lambda e:e['afterLeg'])
E['bonusOwnedAirports']=[e['target'] for e in S]
E['fleetNote']='Sieben Twin-Otter-Ausflüge und zwölf H160-Ausflüge: 16 ergänzen fehlende Kategorien, drei erschließen deine vorhandenen Szenerien London City, Sedona und Milford Sound. Die 403 A320-Legs behalten ihre Nummerierung.'
if 'Milford Sound' not in E['formula']:E['formula']+=' Milford Sound: redaktioneller Ansatz von 45 min je Richtung wegen Gelände und Anflugweg.'
(R/'excursions.json').write_text(json.dumps(E,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Fixed tour:',len(D['legs'])+sum(len(e['legs']) for e in E['excursions']),'legs;',len(E['excursions']),'loops; owned scenery',36+len(E['bonusOwnedAirports']))
