import csv
A=list(csv.DictReader(open('work/airports.csv',encoding='utf8')))
for term in ['Varanasi','Kuwait','Khartoum','Juba','Tripoli','Rotorua','Dzaoudzi','Sumburgh']:
 print(term,[[x[k] for k in ['ident','icao_code','name','type']] for x in A if term.lower() in x['name'].lower()])
