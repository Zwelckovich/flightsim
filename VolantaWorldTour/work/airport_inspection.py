import csv
c=list(csv.DictReader(open('work/countries.csv',encoding='utf-8')))
print(len(c));print([(x['code'],x['name']) for x in c])
a={x['ident']:x for x in csv.DictReader(open('work/airports.csv',encoding='utf-8'))}
r=list(csv.DictReader(open('work/runways.csv',encoding='utf-8')))
for code in ['BGGH','FIMP','FHAW','FHSH','TVSV','TFFG','TQPF','TUPJ','NGFU','EGJB','EFMA','LZTT','NFTF','NWWW','NIUE']:
 x=a.get(code)
 print(code, None if x is None else [x[k] for k in ['name','iso_country','latitude_deg','longitude_deg']],[ [z[k] for k in ['length_ft','width_ft','surface','closed']] for z in r if z['airport_ident']==code])
