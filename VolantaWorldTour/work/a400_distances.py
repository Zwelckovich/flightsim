exec(open('work/h160_feasibility.py',encoding='utf-8-sig').read().split("for base in")[0])
for x,y in [('SAWH','SCGC'),('SCCI','SCGC'),('YMHB','YWKS'),('SAWH','SCRM'),('NFFN','NGFU')]:
 if x in a and y in a:
  d=dist(a[x],a[y]);t=18+d*1.07/360*60
  print(x,y,round(d),'NM;',round(t),'min')
