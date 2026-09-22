from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parent
P={}
for f in R.glob('research-freeware-pages-*.json'):P.update(json.loads(f.read_text(encoding='utf8')))
for key in sys.argv[1:]:
 p=P[key];t=p['raw'];t=re.sub(r'L\d+: ?', '',t);t=re.sub(r'\ue200.*?\ue202\d+\u2020([^\ue201]*)\ue201',r'\1',t)
 print('\nPAGE',key,p['url'])
 for token in ['User Reviews','Downloads','Recent Changelog','Known issues','Known Issues','2024','dependencies','Dependencies']:
  for m in list(re.finditer(re.escape(token),t))[:16]:print(t[max(0,m.start()-80):m.start()+430].replace('\n',' '))
