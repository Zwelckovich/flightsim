exec(open('work/h160_feasibility.py',encoding='utf-8-sig').read().split("for base in")[0])
for codes in [['NFFN','NFSW','NFNR','NGFU'],['NFFN','NFNL','NFNR','NGFU'],['FMNN','FMNM','FMMQ','FMZJ'],['FMNN','FMNM','FMMO','FMZJ']]:
 for x,y in zip(codes,codes[1:]):
  if x in a and y in a:print(x,y,round(dist(a[x],a[y])),a[y]['name'],a[y]['type'])
