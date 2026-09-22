import csv,collections
A=list(csv.DictReader(open('work/airports.csv',encoding='utf8')));R=list(csv.DictReader(open('work/runways.csv',encoding='utf8')))
for code in 'SPJC WAHQ VIBN UCFM OKBK HSSS HSSJ FLKK HLLT'.split():
 print(code,[[x[k] for k in ['ident','icao_code','gps_code','name']] for x in A if code in [x['icao_code'],x['gps_code']]])
print('surface',collections.Counter(x['surface'] for x in R).most_common(20))
for code in 'PHNL SBEG WIMM DRRN EGPB NZRO FMCZ'.split():
 print(code,[[x[k] for k in ['length_ft','width_ft','surface','closed']] for x in R if x['airport_ident']==code])
