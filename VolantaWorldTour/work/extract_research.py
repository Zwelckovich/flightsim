from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
S=json.loads((R/'scenery-guide.json').read_text(encoding='utf8'))
raw={}
for p in [R/'research-screenings.json',*sorted(R.glob('research-batch-*.json'))]:raw.update(json.loads(p.read_text(encoding='utf8')))
def chunks(text):
    starts=list(re.finditer(r'(?m)^([^\n]+) \((https?://[^\n]+)\)\n(?:[\ue200-\uf8ff]|L0:)',text))
    out=[]
    for i,m in enumerate(starts):
        body=text[m.start():starts[i+1].start() if i+1<len(starts) else len(text)]
        url=m[2]; title=m[1]
        if not re.search(r'flightsim\.to/(?:addon|file)/',url):continue
        if re.search(r'GSX|liver(?:y|ies)|Pilot2ATC|Flight Plan|Paint Jobs|Checklists|User Content|Aircraft for MSFS|Utilities for MSFS|Miscellaneous for MSFS|airports-lights|lighting-add-on',title+' '+url,re.I):continue
        m_id=re.search(r'/(?:addon|file)/(\d+)/([^/?&]+)',url)
        if not m_id:continue
        url='https://flightsim.to/addon/'+m_id[1]+'/'+m_id[2].split('%26')[0]
        dm=re.search(r'Downloads\s+([\d.]+)([KM]?)\b',body)
        rm=re.search(r'User Reviews\s+([\d.]+)\s+(\d+)\s+reviews',body)
        out.append(dict(id=m_id[1],title=title.split(' - Airports for MSFS')[0].split(' - Scenery Enhancements for MSFS')[0],url=url,downloads=round(float(dm[1])*({'K':1000,'M':1000000}.get(dm[2],1))) if dm else None,rating=float(rm[1]) if rm else None,reviews=int(rm[2]) if rm else None,body=body))
    return out
products={}
for code,v in raw.items():
    for p in chunks(v['raw']):
        if p['id'] not in products:products[p['id']]={**p,'searchCodes':[]}
        old=products[p['id']]
        old['searchCodes'].append(code)
        if old['rating'] is None and p['rating'] is not None:old.update({k:p[k] for k in ['rating','reviews','downloads']})
for p in products.values():
    p['matchingCodes']=[c for c in S['order'] if re.search(r'\b'+re.escape(c)+r'\b',p['title'],re.I)]
    p['searchCodes']=list(dict.fromkeys(p['searchCodes']))
(R/'freeware-discovery.json').write_text(json.dumps(products,ensure_ascii=False,indent=2),encoding='utf8')
print('SEARCHED',len(raw),'MISSING',[c for c in S['order'] if c not in raw])
print('STRONG METRICS / INDIVIDUAL TITLE MATCH')
for p in products.values():
    if (p['rating'] or 0)>=4.8 and (p['reviews'] or 0)>=15 and (p['downloads'] or 0)>=8000:
        print(p['id'],p['title'],p['downloads'],p['rating'],p['reviews'],p['matchingCodes'])
print('TITLE MATCH WITH MISSING METRICS')
for p in products.values():
    if p['matchingCodes'] and p['rating'] is None and ((p['downloads'] or 0)>=7000 or p['downloads'] is None):print(p['id'],p['title'],p['downloads'],p['matchingCodes'])
