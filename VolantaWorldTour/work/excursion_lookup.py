import csv,math
from pathlib import Path
R=Path('work');a={r['ident']:r for r in csv.DictReader((R/'airports.csv').open(encoding='utf8'))}
for x in list(a.values()):
 if x['icao_code']:a[x['icao_code']]=x
for code in ['SCRM','FMZJ','FMNM','FMNN','FMCZ','NGFU','NFFN','LIKD','TQPF','TDPD','EGJB','TUPJ']:
 x=a[code];rs=[r for r in csv.DictReader((R/'runways.csv').open(encoding='utf8')) if r['airport_ident']==x['ident'] and r['closed']=='0'];print(code,x['name'],x['iso_country'],[(round(float(r['length_ft'] or 0)*.3048),r['surface']) for r in rs])
def d(x,y):
 p,q=a[x],a[y];lat1,lat2=map(math.radians,[float(p['latitude_deg']),float(q['latitude_deg'])]);dl=math.radians(float(q['longitude_deg'])-float(p['longitude_deg']));return round(3440.065*2*math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2)))
for x,y in [('FMCZ','FMZJ'),('FMNN','FMNM'),('FMNM','FMZJ'),('SAWH','SCRM'),('NFFN','NGFU'),('LEBL','AD-ALV')]:print(x,y,d(x,y))
