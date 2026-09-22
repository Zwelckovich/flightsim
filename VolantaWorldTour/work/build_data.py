import csv,json,math,pathlib,collections,heapq
from route_source import CHAPTERS,ALIASES,EXCEPTIONS,SPECIAL,HIGHLIGHTS
ROOT=pathlib.Path(__file__).resolve().parent
def read(name):
    return list(csv.DictReader((ROOT/name).open(encoding='utf-8-sig')))
A={a['ident']:a for a in read('airports.csv')}
for a in list(A.values()):
    if a['icao_code'] and a['icao_code'] not in A:A[a['icao_code']]=a
RW=collections.defaultdict(list)
for r in read('runways.csv'):
    if r['closed']=='0' and r['length_ft'] and r['surface'].upper().startswith(('ASP','CON','PEM','BIT')):
        RW[r['airport_ident']].append(r)
C={c['code']:c['name'] for c in read('countries.csv') if c['code'] not in ['GS','HM','PN','TK','XP','ZZ']}
C.update({'AX':'Åland Islands','SJ':'Svalbard','BN':'Brunei Darussalam','BQ':'Bonaire, Sint Eustatius and Saba','CG':'Congo','CZ':'Czechia','EH':'Western Sahara','FK':'Falkland Islands (Malvinas)','FM':'Micronesia, Federated States of','IR':'Iran (Islamic Republic of)','KP':"Korea, Democratic People's Republic of",'KR':'Korea, Republic of','LA':"Lao People's Democratic Republic",'MD':'Republic of Moldova','PS':'Palestine','RE':'Reunion','SH':'Saint Helena','SY':'Syrian Arab Republic','TF':'French Southern Territories','TR':'Türkiye','TZ':'United Republic of Tanzania','VA':'Holy See (Vatican City)','VI':'United States Virgin Islands','VN':'Viet Nam','WF':'Wallis and Futuna Islands','CI':"Cote d'Ivoire"})
assert len(C)==245,len(C)
C['ST']='Sao Tome and Principe'
ADD={r['ICAO'].strip():r for r in csv.DictReader(open(ROOT.parent/'MSFS Airports - Addons.csv',encoding='utf-8-sig'))}

SOURCES={
 'oa':('OurAirports – Koordinaten und Pisten','https://ourairports.com/data/'),
 'volanta':('Volanta – 245 Kategorien, angemeldete Übersicht','https://fly.volanta.app/activities/countries'),
 'airbus':('Airbus – A320 Airport and Maintenance Planning','https://www.aircraft.airbus.com/en/customer-care/fleet-wide-care/airport-operations-and-aircraft-characteristics/aircraft-characteristics'),
 'map':('Natural Earth via World Atlas 2.0.2','https://github.com/topojson/world-atlas'),
 'wu4':('World Update IV – France & Benelux','https://www.flightsimulator.com/release-notes-1-15-7-0-world-update-iv-france-benelux-now-available/'),
 'wu5':('World Update V – Nordics','https://www.flightsimulator.com/release-notes-1-17-3-0-world-update-v-nordics-now-available/'),
 'wu8':('World Update VIII – Iberia','https://www.flightsimulator.com/release-notes-1-24-5-0-world-update-viii-iberia-now-available/'),
 'wu9':('World Update IX – Italy & Malta','https://www.flightsimulator.com/release-notes-1-25-9-0-world-update-ix-italy-now-available/'),
 'wu12':('World Update XII – New Zealand','https://www.flightsimulator.com/world-update-xii-new-zealand-now-available/'),
 'wu13':('World Update XIII – Oceania','https://www.flightsimulator.com/world-update-xiii-oceania-now-available/'),
 'wu14':('World Update XIV – Central Eastern Europe','https://www.flightsimulator.com/microsoft-flight-simulator-releases-world-update-xiv-central-eastern-europe/'),
 'wu15':('World Update XV – Nordics & Greenland','https://forums.flightsimulator.com/t/release-world-update-xv-nordics-greenland-is-now-available/615641'),
 'wu16':('World Update XVI – Caribbean','https://www.flightsimulator.com/world-update-xvi-caribbean/'),
 'wu17':('World Update XVII – UK & Ireland','https://www.flightsimulator.com/world-update-xvii-united-kingdom-ireland/'),
 'wu18':('World Update XVIII – DACH','https://www.flightsimulator.com/world-update-xviii-germany-austria-and-switzerland/'),
 'wu19':('World Update XIX – Brazil & Guyanas','https://www.flightsimulator.com/world-update-19/'),
 'wu20':('World Update 20 – Japan','https://www.flightsimulator.com/world-update-20/'),
 'wu21':('World Update 21 – Australia','https://www.flightsimulator.com/world-update-21/'),
 'base':('Microsoft – handgefertigte Basis-Airports (2020-Herkunft)','https://flightsimulator.zendesk.com/hc/en-us/articles/360017706059-Microsoft-Flight-Simulator-FAQ')
}
SOURCES.update({
 'wu1':('World Update I – Japan','https://www.flightsimulator.com/september-24th-2020-development-update/'),
 'wu3':('World Update III – United Kingdom','https://forums.flightsimulator.com/t/release-release-notes-1-13-16-0-world-update-iii-united-kingdom-now-available/365854'),
 'wu11':('World Update XI – Canada','https://forums.flightsimulator.com/t/release-world-update-xi-canada-now-available/545758')
})
WU={}
for n,codes in {4:'LFMN EHRD',5:'EKRN ESSA EFVA ENSB',8:'LPFR LECO LPPI',9:'LICJ',12:'NZRO NZMF',13:'SCIP PHKO PTPN WAHQ NTTB NTTM NCAI',14:'LKKV LZTT LDRI',15:'EFIV BIAR ESNQ',16:'MDPP MKJS TTCP MYEH',17:'EGSS EICK EGPB EGFF',18:'LOWS EDDM',19:'SBFI SBFN SBSN SBRJ',20:'RJFR RJER',21:'YBRM YBHI YCBP'}.items():
    for code in codes.split(): WU[code]=n
WU.update({'RJFU':1,'RJCK':1,'RORS':1,'EGGP':3,'CYFB':11})
BASE=set('KASE WX53 SPGL LFLJ EIDL HUEN LPMA LXGB LOWI KLAX VNLK KEB KJFK KMCO LFPG VQPR NZQN SEQM SBGL TNCS TFFJ KSEA KSEZ MRSN CZST YSSY KTEX RJTT MHTG CYTZ EHAM HECA FACT KORD LEMD KDEN OMDB EDDF EGLL KSFO'.split())
# These have known bespoke origin, separate from World Updates. Verify edition in MSFS.


def airport(code):
    a=A[code]; rr=sorted(RW[a['ident']],key=lambda r:float(r['length_ft']),reverse=True)
    r=rr[0] if rr else {}
    cc={'EFMA':'AX','ENSB':'SJ'}.get(code,a['iso_country'])
    owned=ADD.get(code)
    result={'icao':code,'name':a['name'],'city':a['municipality'] or a['name'],'country':cc,'countryName':C.get(cc,cc),
      'lat':round(float(a['latitude_deg']),5),'lon':round(float(a['longitude_deg']),5),'elevation':round(float(a['elevation_ft'] or 0)),
      'runway':round(float(r.get('length_ft',0))*0.3048),'width':round(float(r.get('width_ft') or 0)*0.3048),'surface':r.get('surface','unbekannt'),
      'runwayId':r.get('le_ident','')+'/'+r.get('he_ident',''),
      'scenery':'owned' if owned else 'wu' if code in WU else 'base' if code in BASE else 'default',
      'sceneryLabel':('Add-on · '+owned['Hersteller'].strip()) if owned else ('World Update '+str(WU[code])) if code in WU else 'Handcrafted · Basis/Edition' if code in BASE else 'Standard / Szenerie prüfen',
      'scenerySource': None if owned else 'wu'+str(WU[code]) if code in WU else 'base' if code in BASE else 'oa',
      'url':f'https://ourairports.com/airports/{a["ident"]}/',
      'note':SPECIAL.get(code,''),'highlight':HIGHLIGHTS.get(code),
      'special':code in ['PMDY','PWAK','FHAW','FJDG'],
      'sourceName':owned['Name'] if owned else None}
    if code=='FMCZ':
        result.update(runway=1934,width=45,runwayId='16/34',note='Mayotte: 1.934 × 45 m laut französischer AIP, abweichend vom alten OurAirports-Eintrag. LDA kann kürzer sein; Performance und Bahnschwellen prüfen.',runwaySource='https://www.sia.aviation-civile.gouv.fr/media/dvd/eAIP_06_AUG_2026/RUN/AIRAC-2026-08-06/html/eAIP/FR-AD-2.FMCZ-fr-FR.html')
    if code=='NZRO':
        result.update(runway=None,note='Rotorua: Der OurAirports-Pisteneintrag (1.622 m) ist veraltet. Der Airport-Masterplan bestätigt die Erweiterung für größere Jets. Aktuelle Bahnlänge, LDA und Fenix-Leistung vor diesem Stopp anhand der AIP und deiner WU-XII-Szenerie prüfen.',runwaySource='https://www.rotorua-airport.co.nz/site_files/21129/upload_files/221111_RRAMasterPlanFINAL.pdf?dl=1')
    return result

def dist(a,b):
    la1,lo1,la2,lo2=map(math.radians,[a['lat'],a['lon'],b['lat'],b['lon']])
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 3440.065*2*math.asin(min(1,math.sqrt(h)))
def minutes(d):return max(25,round(18+d*1.07/430*60))

stops=[]
for chap,title,desc,seq in CHAPTERS:
    for code in seq.split():
        code=ALIASES.get(code,code)
        if code=='GEML':continue
        if code not in A:
            print('MISSING AIRPORT',code)
        else:stops.append({'icao':code,'chapter':chap,'bridge':False})
AP={s['icao']:airport(s['icao']) for s in stops}
covered={a['country'] for a in AP.values()}
print('INITIAL',len(stops)-1,'legs',len(AP),'airports',len(covered),'categories')
print('MISSING COUNTRIES',[(c,C[c]) for c in C if c not in covered and c not in EXCEPTIONS])
print('SHORT/NARROW',[(a['icao'],a['runway'],a['width']) for a in AP.values() if (a['runway'] or 0)<1800 or a['width']<30])

# Add carefully screened civil airports only when they split a long leg efficiently.
# Candidate chain <= 4 legs, max 20% geographic detour; avoids low/short-field airports.
candidates={}
for code,a in A.items():
    if a['type'] not in ['large_airport','medium_airport'] or a['scheduled_service']!='yes':continue
    if a['iso_country'] in EXCEPTIONS:continue
    if float(a['elevation_ft'] or 0)>6500:continue
    if code in ['CYBG','WAVV','DN57','ZMMN']:continue
    if code!=a['ident']:continue
    r=max(RW[a['ident']],key=lambda r:float(r['length_ft']),default=None)
    if not r or float(r['length_ft'])<7000 or float(r['width_ft'] or 0)<130:continue
    if any(w in a['name'].lower() for w in ['air base','airbase','military','air force']):continue
    candidates[code]=airport(code)

def bridge(start,end):
    direct=dist(start,end)
    if minutes(direct)<=120:return []
    # Geographic corridor and bounded search. The resulting inserted stops are reviewed.
    eligible={c:a for c,a in candidates.items() if c not in [start['icao'],end['icao']] and dist(start,a)+dist(a,end)<direct*1.20 and dist(start,a)>65 and dist(a,end)>65}
    nodes={start['icao']:start,end['icao']:end,**eligible}
    q=[(0,0,[start['icao']])]; best={}
    while q:
        cost,length,path=heapq.heappop(q); cur=path[-1]
        if cur==end['icao']:return path[1:-1]
        if len(path)>=5:continue
        for c,a in nodes.items():
            if c in path:continue
            d=dist(nodes[cur],a)
            if minutes(d)>120 or length+d>direct*1.20:continue
            # Small preference for existing add-ons / verified World Updates.
            score=cost+d+150-(30 if a['scenery'] in ['owned','wu'] else 0)
            key=(c,len(path))
            if score>=best.get(key,1e10):continue
            best[key]=score
            heapq.heappush(q,(score,length+d,path+[c]))
    return []

expanded=[stops[0]]
inserted=[]
for s in stops[1:]:
    p=expanded[-1]
    mids=bridge(AP[p['icao']],AP[s['icao']])
    if mids:
        inserted.append((p['icao'],s['icao'],mids))
        for m in mids:
            AP[m]=candidates[m];expanded.append({'icao':m,'chapter':s['chapter'],'bridge':True})
    expanded.append(s)
stops=expanded
print('INSERTED',inserted)
legs=[]; seen={AP[stops[0]['icao']]['country']}
for i,(p,s) in enumerate(zip(stops,stops[1:]),1):
    a,b=AP[p['icao']],AP[s['icao']];d=dist(a,b);t=minutes(d)
    legs.append({'id':i,'from':p['icao'],'to':s['icao'],'chapter':s['chapter'],'nm':round(d),'airMin':t,'blockMin':t+20,'over2h':t>120,'bridge':s['bridge'],'newCountry':b['country'] not in seen})
    seen.add(b['country'])

countryRows=[]
for c,name in C.items():
    matched=[a['icao'] for a in AP.values() if a['country']==c]
    ex=EXCEPTIONS.get(c)
    countryRows.append({'code':c,'name':name,'airports':matched,'status':'special' if matched and all(AP[m]['special'] for m in matched) else 'main' if matched else 'exception','exception':ex})
for c in countryRows:
    assert c['airports'] or c['exception'],c
print('TOTAL',len(legs),'legs',len(AP),'airports',len(seen),'categories',sum(l['over2h'] for l in legs),'long')
print('LONG',[(l['id'],l['from'],l['to'],l['nm'],l['airMin']) for l in legs if l['over2h']])
print('OWNED',len(set(AP)&set(ADD)),len(ADD),'unused',sorted(set(ADD)-set(AP)))
out={'meta':{'date':'2026-09-21','start':'EDLV','aircraft':'Fenix A320 · CFM · Sharklets','volantaTotal':245,'inventoryTotal':len(ADD),'formula':'Flugzeit ≈ 18 min + Großkreisdistanz × 1,07 / 430 kt × 60; mindestens 25 min. Blockzeit zusätzlich 20 min. Wind, SID/STAR, ATC und Halten nicht live berechnet.'},'chapters':[{'id':c,'title':t,'description':d} for c,t,d,_ in CHAPTERS],'airports':AP,'stops':stops,'legs':legs,'countries':countryRows,'sources':SOURCES,'inventory':[{'icao':c,'manufacturer':r['Hersteller'].strip(),'inRoute':c in AP,'reason':'Für den Fenix A320 ungeeignet' if c in ['EGLC','KSEZ','NZMF'] else 'Zusätzlicher Inlandsstopp ohne neue Kategorie; zugunsten der Gesamtroute ausgelassen'} for c,r in ADD.items()]}
(ROOT/'tour-data.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf8')
