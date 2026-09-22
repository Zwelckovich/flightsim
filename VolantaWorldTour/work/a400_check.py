import csv,json
from pathlib import Path
r=Path('work');a={x['ident']:x for x in csv.DictReader((r/'airports.csv').open(encoding='utf8'))}
for c in ['SAWH','SCCI','SCRM','NGFU']:
 x=a[c];print(c,x['name'],x['latitude_deg'],x['longitude_deg'],x['elevation_ft'])
 for rw in csv.DictReader((r/'runways.csv').open(encoding='utf8')):
  if rw['airport_ident']==c:print({k:rw[k] for k in ['length_ft','width_ft','surface','closed','le_ident','he_ident']})
