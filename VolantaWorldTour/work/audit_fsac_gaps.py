import json,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parent
P=json.loads((R/'payware-discovery.json').read_text(encoding='utf8'))
out=[]
for f in R.glob('research-fsac-*.json'):
 for g in json.loads(f.read_text(encoding='utf8')).values():
  out.extend([(m[1],int(m[2])) for m in re.finditer(r'Source: open\(\{"ref_id":"https://www.fsaddoncompare.com/search/([^"]+)"[^\n]+Total lines: (\d+)',g.get('raw',''))])
print(Counter('read' if P[c]['readable'] else 'truncated' if n>1 else 'empty' for c,n in out))
gaps=[dict(code=c,lines=n) for c,n in out if not P[c]['readable']]
(R/'fsac-gaps.json').write_text(json.dumps(gaps),encoding='utf8')
print(gaps[:25])
