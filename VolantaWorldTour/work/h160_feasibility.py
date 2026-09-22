import csv,math
from pathlib import Path
R=Path(r'C:\Users\zwelc\Documents\Codex\2026-09-21\ich\work')
a={r['ident']:r for r in csv.DictReader((R/'airports.csv').open(encoding='utf8'))}
def dist(x,y):
 p,q=map(math.radians,[float(x['latitude_deg']),float(y['latitude_deg'])]);dl=math.radians(float(y['longitude_deg'])-float(x['longitude_deg']));return 3440.065*2*math.asin(math.sqrt(math.sin((p-q)/2)**2+math.cos(p)*math.cos(q)*math.sin(dl/2)**2))
for base in ['NGFU','SCRM']:
 b=a[base]
 print('CLOSE TO',base)
 rows=[x for x in a.values() if x['iso_country']!=b['iso_country'] and x['type']!='closed']
 for x in sorted(rows,key=lambda x:dist(x,b))[:15]:print(x['ident'],x['name'],x['type'],x['iso_country'],round(dist(x,b)))
for code in ['NFNR','NFNL','NFFN','NGFU','SCGC']:
 if code in a:print(code,a[code]['name'],a[code]['latitude_deg'],a[code]['longitude_deg'])
