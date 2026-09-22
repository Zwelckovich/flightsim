from pathlib import Path
R=Path(__file__).resolve().parent
def replace(s, old, new, n=1):
    assert s.count(old)==n, (old[:120],s.count(old),n)
    return s.replace(old,new)

t=(R/'tour-template.html').read_text(encoding='utf8')
if '__SCENERY_UI__' not in t:
    t=replace(t,'</style></head>','/*__SCENERY_CSS__*/</style></head>')
    t=replace(t,'<button data-view="methodView">','<button data-view="sceneryView">Szenerien</button><button data-view="methodView">')
    t=replace(t,'<section class="view" id="methodView">','<!--__SCENERY_VIEW__-->\n<section class="view" id="methodView">')
    t=replace(t,'<script id="excursionData" type="application/json">__EXCURSIONS__</script>','<script id="excursionData" type="application/json">__EXCURSIONS__</script><script id="sceneryData" type="application/json">__SCENERY__</script>')
    t=replace(t,'/*__EXCURSION_UI__*/','/*__EXCURSION_UI__*/\n/*__SCENERY_UI__*/')
    t=replace(t,'renderStats();renderHighlights();','renderSceneryOverview();renderStats();renderHighlights();')
    t=replace(t,"if(id==='journeyView')renderJourney();","if(id==='journeyView')renderJourney();if(id==='sceneryView')renderScenery();")
    t=replace(t,'<div class="airport-facts">','${sceneryCard(b.icao)}<div class="airport-facts">')
    t=replace(t,'<summary>Abflug ${a.icao}: Piste & Szenerie</summary><p>${sceneTag(a)}</p>','<summary>Abflug ${a.icao}: Piste & Szenerie</summary><p>${sceneTag(a)}</p>${sceneryCard(a.icao)}')
    t=replace(t,'<td>${sceneTag(b)}</td>','<td>${sceneTag(b)}<br>${sceneryButton(b.icao)}</td>')
    t=replace(t,"$('#legRows').addEventListener('click',e=>{","$('#legRows').addEventListener('click',e=>{if(e.target.closest('[data-scenery]'))return;")
    t=replace(t,"$('#legRows').addEventListener('keydown',e=>{","$('#legRows').addEventListener('keydown',e=>{if(e.target.closest('[data-scenery]'))return;")
    t=replace(t,'${sceneTag(a)}<button data-jump=','${sceneTag(a)}${sceneryButton(a.icao)}<button data-jump=',n=2)
    t=replace(t,'<th>Flugzeit ≈</th><th>Details</th>','<th>Flugzeit ≈</th><th>Szenerie am Ziel</th><th>Details</th>')
    t=replace(t,"'Ziel_Szenerie','Highlight'","'Ziel_Szenerie','Szenerie_Empfehlung','Empfohlenes_Produkt_Basis','Highlight'")
    t=replace(t,"a.sceneryLabel,a.highlight?.join(': ')","a.sceneryLabel,sceneryLabel(l.to),SC.airports[l.to].recommendation,a.highlight?.join(': ')")
    (R/'tour-template.html').write_text(t,encoding='utf8')

x=(R/'excursions-ui.js').read_text(encoding='utf8')
if 'sceneryCard(e.target)' not in x:
    x=replace(x,'<details><summary>Szenerie & Landeplatz</summary>','${sceneryCard(e.target)}<div class="x-scenery-links">${[...new Set(e.route)].map(code=>`<button class="scenery-link" data-scenery="${code}">${code} · Szenerie →</button>`).join(\'\')}</div><details><summary>Weitere Hinweise zum Landeplatz</summary>')
    x=replace(x,'${l.nm} NM</div></td><td><button','${l.nm} NM</div></td><td>${sceneryButton(l.to)}</td><td><button')
    x=replace(x,'<td colspan="7" class="empty">','<td colspan="8" class="empty">')
    x=replace(x,'<div class="card-footer"><span class="tag warn">${esc(e.countryName)}</span>','<div class="card-footer"><span class="tag warn">${esc(e.countryName)}</span>${sceneryButton(e.target)}')
    x=replace(x,"'Hinweise_Anflug_Treibstoff','Quellen'","'Hinweise_Anflug_Treibstoff','Quellen','Szenerie_Empfehlung','Empfohlenes_Produkt_Basis','Szenerie_Begruendung','Szenerie_Quellen'")
    x=replace(x,"l.note,l.sources])","l.note,l.sources,sceneryLabel(l.to),SC.airports[l.to].recommendation,SC.airports[l.to].reason,SC.airports[l.to].links.map(s=>s[1]).join(' | ')])")
    (R/'excursions-ui.js').write_text(x,encoding='utf8')

# Keep future data regeneration consistent without regenerating or reordering the route.
p=R/'build_data.py';s=p.read_text(encoding='utf8')
s=s.replace("BASE=set('LPMA LXGB LOWI KLAX HUEN RJTT YSSY NZQN YAYE SBGL VQPR LFPG TNCM'.split())", "BASE=set('KASE WX53 SPGL LFLJ EIDL HUEN LPMA LXGB LOWI KLAX VNLK KEB KJFK KMCO LFPG VQPR NZQN SEQM SBGL TNCS TFFJ KSEA KSEZ MRSN CZST YSSY KTEX RJTT MHTG CYTZ EHAM HECA FACT KORD LEMD KDEN OMDB EDDF EGLL KSFO'.split())")
s=s.replace("BASE-=set('VQPR TNCM'.split())",'')
p.write_text(s,encoding='utf8')
print('Scenery UI integrated; flight routes and progress schema unchanged.')
