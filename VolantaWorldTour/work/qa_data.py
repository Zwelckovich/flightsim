import json,collections
from pathlib import Path
D=json.loads(Path('work/tour-data.json').read_text(encoding='utf8'))
print('WU airports',[(a['icao'],a['sceneryLabel']) for a in D['airports'].values() if a['scenery']=='wu'])
print('Short fields',[(a['icao'],a['runway'],a['width']) for a in D['airports'].values() if (a['runway'] or 0)<2000 or a['width']<40])
print('Country statuses',collections.Counter(c['status'] for c in D['countries']))
print('Briefings',len(json.loads(Path('work/briefings.json').read_text(encoding='utf8'))))
