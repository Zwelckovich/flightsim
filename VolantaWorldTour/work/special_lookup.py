import csv
A=list(csv.DictReader(open('work/airports.csv',encoding='utf8')))
for cc in 'AD VA LI MC SM TF PS'.split():
 print(cc, [{k:a[k] for k in ['ident','icao_code','gps_code','name','latitude_deg','longitude_deg','type']} for a in A if a['iso_country']==cc])
