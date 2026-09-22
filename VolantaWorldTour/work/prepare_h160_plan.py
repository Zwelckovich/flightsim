"""Prepare the independent H160 loops; Antarctic choice remains pending."""
from pathlib import Path
import csv,json,math,copy
R=Path(__file__).resolve().parent
E=json.loads((R/'excursions.json').read_text(encoding='utf8'))
A={a['ident']:a for a in csv.DictReader((R/'airports.csv').open(encoding='utf8'))}
def point(c):
 a=A[c]
 return {'ident':c,'icao':c,'name':a['name'],'city':a['municipality'],'country':a['iso_country'],'lat':float(a['latitude_deg']),'lon':float(a['longitude_deg']),'type':a['type'],'elevation':round(float(a['elevation_ft'] or 0)),'runway':None,'surface':'prüfen','url':f'https://ourairports.com/airports/{c}/','sceneryLabel':'MSFS-2024-Darstellung vorab prüfen'}
def distance(a,b):
 p,q=map(math.radians,[a['lat'],b['lat']]);dl=math.radians(b['lon']-a['lon'])
 return 3440.065*2*math.asin(math.sqrt(math.sin((q-p)/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2))
for c in ['NFSW','NFNR','FMMO']:E['points'][c]=point(c)
for e in E['excursions']:
 if e['country']=='AQ':
  e['decisionPending']=True
  continue
 e['aircraft']='Airbus H160';e['cruiseKt']=138
 e['fuelNote']='Am Ausgangspunkt tanken; jeder Start setzt eine eigene Prüfung von Masse, Wetter, Reserven und HPG-Verbrauch voraus.'
 if e['country']=='TV':
  e['route']='NFFN NFSW NFNR NGFU NFNR NFSW NFFN'.split()
  e['fuelNote']='Simulierte vorbereitete Treibstoffversorgung auf Yasawa, Rotuma und Funafuti erforderlich. Regulär verfügbares Jet A-1 vor Ort ist damit nicht bestätigt. Nicht versuchen, Rotuma–Funafuti–Rotuma ohne Betankung in Funafuti zu fliegen.'
  e['briefing']='Ab Nadi über die Yasawa-Inseln und Rotuma nach Funafuti. Zwei längere Abschnitte je Richtung bleiben mit etwa 2:15 bis 2:21 h über dem Wunschwert. Die Lagune und das schmale Atoll belohnen die Überwasseretappen. Landung an der zu NGFU gehörenden geeigneten Fläche; tatsächliche Erkennung in Volanta nach dem Besuch prüfen.'
 if e['country']=='TF':
  e['route']='FMNN FMNM FMMO FMZJ FMMO FMNM FMNN'.split()
  e['fuelNote']='Versorgung in Amborovy und ein vorbereitetes simuliertes Treibstoffdepot in Maintirano einplanen. Maintirano–Juan de Nova–Maintirano umfasst etwa 192 NM Großkreis; damit muss keine Betankung auf Juan de Nova angenommen werden. Wetter, Umwege, Reserve und konkreten HPG-Verbrauch trotzdem vorab prüfen.'
  e['briefing']='Entlang Madagaskars über Mahajanga und Maintirano zur abgelegenen Riffinsel Juan de Nova. Maintirano verkürzt den Inselabstecher auf rund 96 NM je Richtung. Inselanflug über den Mosambikkanal, Lagune und Korallenriff; am tatsächlichen FMZJ landen, damit die zuvor geprüfte Volanta-Zuordnung genutzt wird.'
 e['legs']=[]
 for i,(a,b) in enumerate(zip(e['route'],e['route'][1:]),1):
  nm=round(distance(E['points'][a],E['points'][b]));t=max(12,round(12+nm*1.1/138*60))
  e['legs'].append({'id':f'H-{e["country"]}-{i}','from':a,'to':b,'nm':nm,'airMin':t,'over2h':t>120})
E['formula']='H160-Flugzeit ≈ 12 min + Großkreisdistanz × 1,10 / 138 kt × 60; mindestens 12 min. Wind, Reserve, Schwebeflug und POI-Runden separat planen.'
E['h160Source']='https://www.airbus.com/en/products-services/helicopters/civil-helicopters/h160/h160-technical-information'
E['h160ImplementationSource']='https://www.hypeperformancegroup.com/products/hpg-h160'
E['logistics']='Die H160 wird als regional bereitgestellter Helikopter angenommen. Ihr Transfer zwischen A320-Basen wird nicht als selbst geflogene Strecke dargestellt. Die persönliche Reiseroute bleibt durch Hin-/Rückflüge zusammenhängend; der A320 bleibt für die Ausflüge geparkt.'
(R/'h160-plan-pending.json').write_text(json.dumps(E,ensure_ascii=False,indent=2),encoding='utf8')
ready=[e for e in E['excursions'] if not e.get('decisionPending')]
print('Prepared',len(ready),'H160 loops;',sum(len(e['legs']) for e in ready),'legs; Antarctica decision pending')
for e in ready:
 if e['country'] in ['TV','TF']:print(e['country'],' > '.join(e['route']),[(l['nm'],l['airMin']) for l in e['legs']])
assert len(ready)==15
assert all(l['nm']<300 for e in ready for l in e['legs'])
assert all(e['route'][0]==e['route'][-1]==e['anchor'] for e in ready)
