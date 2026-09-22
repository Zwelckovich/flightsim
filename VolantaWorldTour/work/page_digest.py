from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parent
P={}
for f in R.glob('research-freeware-pages-*.json'):P.update(json.loads(f.read_text(encoding='utf8')))
for key in sys.argv[1:]:
 t=P[key]['raw'];t=re.sub(r'L\d+: ?', '',t);t=re.sub(r'\ue200[^\u2020\ue201]*\u2020([^\ue201]+)\ue201',lambda m:m[1].split('\u2020')[0],t)
 print('\nPAGE',key,P[key]['url'])
 for rx in [r'### Description',r'### Dependencies',r'### User Reviews',r'Downloads\s',r'Known [Ii]ssues',r'### Version History']:
  m=re.search(rx,t)
  if m:print(t[m.start():m.start()+350].replace('\n',' '))
 c=t.split('### Comments')[1].split('### User Reviews')[0] if '### Comments' in t else t
 c=c.split('MSFS 2020 MSFS 2024')[0]
 for m in list(re.finditer(r'2024',c))[:3]:
  if 'addon platform' not in c[max(0,m.start()-160):m.start()+100]:print(c[max(0,m.start()-100):m.start()+350].replace('\n',' '))
