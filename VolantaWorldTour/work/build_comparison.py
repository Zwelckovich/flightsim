"""Attach a traceable discovery ledger, keeping search coverage separate from review depth."""
from pathlib import Path
import json,re,csv,io
from urllib.parse import urlparse
from collections import Counter
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text(encoding='utf8'))
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
S=read('scenery-guide.json');F=read('freeware-research.json');P=read('payware-discovery.json');FD=read('freeware-discovery.json');M=read('maker-review.json')
S['manufacturerPolicy']=M['policy']
S['manufacturers']=M['manufacturers']
raw={}
for p in [R/'research-screenings.json',*sorted(R.glob('research-batch-*.json'))]:raw.update(read(p.name))
assert set(raw)==set(S['order'])
def headers(t):
 return [(m[1],m[2]) for m in re.finditer(r'(?m)^([^\n]+) \((https?://[^\n]+)\)\n',t)]
def fid(url):
 m=re.search(r'/(?:addon|file)/(\d+)/',url);return m[1] if m else None
exclude=re.compile(r'GSX|FSLTL|Static Aircraft|Static AI|Livery|Liveries|Paint Job|Pilot2ATC|Flight Plan|Landing Challenge|User Content|Utilities for MSFS|Miscellaneous for MSFS|lighting-add-on|airports-lights|night lighting|Navaids',re.I)
# Never promote unrelated recommendation cards, liveries, or search-index review snippets to a product review.
for code,g in S['airports'].items():
 free={}
 for id,p in FD.items():
  if code not in p['matchingCodes'] or exclude.search(p['title']+' '+p['url']):continue
  free[id]={'name':p['title'],'url':p['url'],'stage':'Suchtreffer','verdict':'Qualität und konkrete 2024-Nutzbarkeit dieses Treffers nicht vertieft bestätigt. Keine Empfehlung allein aus dem Suchergebnis.'}
 for r in F['considered']:
  if code in r['codes']:
   id=fid(r['url'])
   free[id]={'name':r['name'],'url':r['url'],'stage':'Produktseite geprüft','metrics':r['metrics'],'verdict':r['reason']}
 if code in F['selected']:
  f=F['selected'][code];id=fid(f['links'][0][1])
  free[id]={'name':f['developer']+' · '+f['name'],'url':f['links'][0][1],'stage':'Empfohlen','metrics':f"{f['rating']:.1f}/5 · {f['reviews']} Bewertungen · ca. {f['downloads']:,} Downloads",'verdict':f['reason']+' '+f['caveat']}
 free=list(free.values());free.sort(key=lambda x:({'Empfohlen':0,'Produktseite geprüft':1,'Suchtreffer':2}[x['stage']],x['name']))
 paid=[];seen=set()
 for p in P[code]['candidates']:
  key=(p['developer'],p['name'].casefold())
  if key in seen:continue
  seen.add(key);paid.append({**p,'stage':'Katalogtreffer'})
 if g['mode']=='buy':
  p=S['products'][code]
  paid.insert(0,{'name':p['name'],'developer':p['developer'],'url':p['links'][0][1],'platforms':['MSFS2024'],'stage':'Optional empfohlen','rating':None,'reviews':None,'verdict':p['reason'],'compatibility':p['compatibility'],'links':p['links']})
 if code in S['considered']:
  c=S['considered'][code]
  paid.insert(0,{'name':c['candidate'],'developer':'','url':c['links'][0][1],'platforms':[],'stage':'Produktangaben geprüft','rating':None,'reviews':None,'verdict':c['reason'],'links':c['links']})
 extra=[]
 for title,url in headers(raw[code]['raw']):
  host=urlparse(url).hostname or ''
  if not re.search(r'\b'+re.escape(code)+r'\b',title,re.I):continue
  if exclude.search(title):continue
  if any(bad in host for bad in ['sceneryaddons','fsxchina','allflightmods','vaughangeorge','reddit','x-plane','flightgear','fsx.org']):continue
  if 'flightsim.to' in host and '/addon/' in url:continue
  if any(x in host for x in ['fsdg-online.com','justflight.com','aerosoft.com','orbxdirect.com','secure.simmarket.com','flightbeam','mmsimulations','inibuilds','flightsimulator.com','flightsim.to','fsaddoncompare.com','contrail.shop','msfsmarket.place']):extra.append([title,url])
 extra=list(dict.fromkeys(tuple(x) for x in extra))[:6]
 reviewed=sum(x['stage']!='Suchtreffer' for x in free)
 deep=reviewed>0 or code in S['products'] or code in S['considered']
 if free:
  free_verdict=(f"{reviewed} konkrete Freeware-Seite(n) mit Entscheidung; weitere Treffer bleiben als solche gekennzeichnet." if reviewed else 'Konkrete Freeware-Treffer gefunden, aber noch kein ausreichend belegtes Spitzenprodukt für diese Auswahl.')
 else:free_verdict='Im ICAO-/Namens-Suchabgleich kein ausreichend passender und belegter Freeware-Kandidat identifiziert. Das ist kein Nachweis, dass keine Erweiterung existiert.'
 if code in F['selected']:free_verdict='Bevorzugte kostenlose Erweiterung ausgewählt; Version, Abhängigkeiten und Einschränkungen stehen in der Empfehlung.'
 if g['mode']=='owned':paid_verdict='Vorhandene Szenerie hat Vorrang. Die gefundenen Alternativen begründen keinen zusätzlichen Kauf für denselben Airport.'
 elif code in S['considered']:paid_verdict=S['considered'][code]['reason']
 elif g['mode']=='included':paid_verdict='Enthaltene handgefertigte Fassung hat Vorrang; ein außergewöhnlicher zusätzlicher Kaufnutzen wurde nicht belegt.'
 elif g['mode']=='freeware':paid_verdict='Die ausgewählte Freeware ist die Empfehlung. Ein außergewöhnlicher zusätzlicher Nutzen eines Kaufs ist nicht belegt.'
 elif g['mode']=='buy':paid_verdict='Begründete optionale Kauf-Ausnahme; Produktumfang, Alternativen und Einschränkungen stehen oben.'
 elif code in S['considered']:paid_verdict=S['considered'][code]['reason']
 else:paid_verdict='Kein Kauf ausgewählt: Ein katalogisierter oder im Web gefundener Airport allein belegt noch keinen außergewöhnlichen Mehrwert. Nicht alle einzelnen Angebote sind vertieft bewertet.'
 audit=dict(searched=True,date='2026-09-21',depth='Produktprüfung' if deep else 'Suchabgleich',reviewedFreeware=reviewed,freeware=free,payware=paid,freewareConclusion=free_verdict,paywareConclusion=paid_verdict,fsacReadable=P[code]['readable'],sources=extra,queries=raw[code].get('queries',[]),fsacUrl=P[code]['url'])
 g['comparison']=audit
 if g['mode']=='default':g['note']='Flightsim.to und kommerzielle Angebote wurden in den Suchabgleich einbezogen. Die konkrete Prüftiefe und gefundene Kandidaten stehen unten; kein eigener Simulator-Test.'
S['auditSummary']={'screenedAirports':len(raw),'productReviewedAirports':sum(g['comparison']['depth']=='Produktprüfung' for g in S['airports'].values()),'reviewedFreewareProducts':len({fid(r['url']) for r in F['considered']}|{fid(f['links'][0][1]) for f in F['selected'].values()}),'freewareCandidateAirports':sum(bool(g['comparison']['freeware']) for g in S['airports'].values()),'fsacReadable':sum(p['readable'] for p in P.values()),'fsacUnavailable':sum(not p['readable'] for p in P.values()),'date':'2026-09-21'}
S['auditSummary']['reviewedPaywareAirports']=len(set(S['products'])|set(S['considered']))
S['auditSummary']['method']='Alle 405 Landestellen wurden nach Freeware und kommerziellen Alternativen durchsucht; vorhandene/inbegriffene Airports wurden abgeglichen. Produktprüfungen bedeuten gelesene Angaben und verfügbare Versionshinweise oder Nutzerberichte, keine eigenen Simulator-Tests. Suchtreffer sind keine Qualitätsfreigabe. Zusätzlich erfolgte ein gezielter Abgleich der genannten Hersteller. Nicht alle Angebote wurden einzeln beurteilt. FSAddonCompare liefert teils leere oder nicht abrufbare Antworten; die verbleibenden Lücken sind sichtbar.'
write('scenery-guide.json',S)
# Snapshot the previously delivered route before replacing its HTML. Only endpoints/IDs matter for progress continuity.
baseline=R/'route-baseline.json'
if not baseline.exists():
 old=(R.parent/'outputs'/'Volanta-Worldtour-EDLV.html').read_text(encoding='utf8')
 def embedded(id):
  m=re.search(r'<script[^>]*id="'+id+r'"[^>]*>(.*?)</script>',old,re.S);return json.loads(m[1])
 d,x=embedded('tourData'),embedded('excursionData')
 write('route-baseline.json',{'main':[[l['id'],l['from'],l['to']] for l in d['legs']],'side':[[e['id'],e['afterLeg'],e['route'],[[l['id'],l['from'],l['to']] for l in e['legs']]] for e in x['excursions']]})
print('COMPARISON',S['auditSummary'])
