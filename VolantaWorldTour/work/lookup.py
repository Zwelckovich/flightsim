import csv
A={x['ident']:x for x in csv.DictReader(open('work/airports.csv',encoding='utf8'))}
for cc in ['VC','KH','AX','SJ','XK','BT','KP','TF','PS']:
 print(cc,[(x['ident'],x['name'],x['type']) for x in A.values() if x['iso_country']==cc and x['type'] in ['large_airport','medium_airport']])
