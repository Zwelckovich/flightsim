import json,csv,re,math
from pathlib import Path
R=Path(__file__).resolve().parent
D=json.loads((R/'tour-data.json').read_text(encoding='utf8'))
actual=set(json.loads((R/'volanta-names.json').read_text(encoding='utf8')))
planned={c['name'] for c in D['countries']}
assert len(actual)==len(D['countries'])==245
print('Name differences',actual-planned,planned-actual)
assert actual==planned
legs=D['legs'];A=D['airports']
assert legs[0]['from']==legs[-1]['to']=='EDLV'
assert all(a['to']==b['from'] for a,b in zip(legs,legs[1:]))
assert [l['id'] for l in legs]==list(range(1,len(legs)+1))
assert all(-90<=a['lat']<=90 and -180<=a['lon']<=180 for a in A.values())
assert all(l['from']!=l['to'] and 0<l['nm']<3000 for l in legs)
assert all(l['over2h']==(l['airMin']>120) and l['blockMin']==l['airMin']+20 for l in legs)
assert all(c['airports'] or c['exception'] for c in D['countries'])
assert all(A[code]['country']==c['code'] for c in D['countries'] for code in c['airports'])
assert set(A)==set(x for l in legs for x in (l['from'],l['to']))
assert A['EFMA']['country']=='AX' and A['ENSB']['country']=='SJ' and A['TNCM']['country']=='SX'
assert not any(code in A for code in ['EGLC','KSEZ','NZMF','TFFJ','TFFG','NGFU'])
assert A['BGGH']['runway']>2100 and A['FMCZ']['width']==45
owned={r['ICAO'].strip() for r in csv.DictReader(open(R.parent/'MSFS Airports - Addons.csv',encoding='utf8'))}
assert {a['icao'] for a in A.values() if a['scenery']=='owned'}==owned&set(A)
assert sum(a['scenery']=='owned' for a in A.values())==36
assert all(a['runway'] is None or a['runway']>=1700 for a in A.values())
s=(R.parent/'outputs'/'Volanta-Worldtour-EDLV.html').read_text(encoding='utf8')
assert not re.search(r'<script[^>]+src=',s)
assert not re.search(r'__(?:DATA|WORLD|DEBRIEFS|DEBRIEF_UI|DEBRIEF_CSS|DEBRIEF_VIEW|RESET_UI|RESET_CSS|RESET_VIEW|RESET_DIALOG)__',s)
assert '\ufffd' not in s
scripts=re.findall(r'<script>(.*?)</script>',s,re.S)
(R/'app-check.js').write_text(scripts[-1],encoding='utf8')
print('PASS: continuous closed route, all 245 exact Volanta names, scenery joins, coordinate bounds, times, airport exclusions and fully embedded HTML')
print('SUMMARY',len(legs),'legs;',sum(l['over2h'] for l in legs),'over 2h;',sum(a['scenery']=='wu' for a in A.values()),'WU airports;',sum(a['highlight'] is not None for a in A.values()),'highlight airports')
