from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
S=json.loads((R/'scenery-guide.json').read_text(encoding='utf8'))
def clean(t):
 t=re.sub(r'L\d+: ?', '\n', t)
 t=re.sub(r'\ue200[^\u2020\ue201]*\u2020([^\ue201]+)\ue201',lambda m:m[1].split('\u2020')[0],t)
 return t
out={}
for f in sorted(R.glob('research-fsac-*.json')):
 for group in json.loads(f.read_text(encoding='utf8')).values():
  for part in group.get('raw','').split('-'*80):
   m=re.search(r'Source: open\(\{"ref_id":"https://www.fsaddoncompare.com/search/([^"]+)"',part)
   if not m:continue
   code=m[1];t=clean(part);found=[]
   for seg in re.split(r'(?m)^## ',t)[1:]:
    title=seg.splitlines()[0].strip()
    if not (re.search(r'\b'+re.escape(code)+r'\b',title) or re.search(r'(?m)^\s*\* '+re.escape(code)+r'\s*$',seg[:500])) or not re.search(r'\* Airport\b|\* Scenery\b',seg[:500]):continue
    if re.search(r'Schedules|Night3D|Night Enhanced|Static|Liveries|Livery|historic|1935|1936|Navaids|Landing Analysis|STAR Training|SID Training|A320 Flights|Gsx|GSX|Runway Status',title,re.I):continue
    dev=re.search(r'by\s+([^\n]+)',seg)
    if dev and dev[1].strip()==code:continue
    rating=re.search(r'\* (\d\.\d+) \((\d+)\)',seg)
    found.append(dict(name=title.replace(' On Sale','').strip(),developer=dev[1].strip() if dev else '',platforms=list(dict.fromkeys(re.findall(r'MSFS20(?:20|24)',seg[:500]))),rating=float(rating[1]) if rating else None,reviews=int(rating[2]) if rating else None,url='https://www.fsaddoncompare.com/search/'+code))
   out[code]={'readable':bool(re.search(r'Found: \d+',t)), 'candidates':found, 'url':'https://www.fsaddoncompare.com/search/'+code}
(R/'payware-discovery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('FSAC',len(out),'readable',sum(x['readable'] for x in out.values()),'with products',sum(bool(x['candidates']) for x in out.values()))
for code,a in out.items():
 if a['candidates'] and S['airports'][code]['mode'] not in ['owned','included']:print(code,' | '.join(x['developer']+': '+x['name'] for x in a['candidates'][:4]))
