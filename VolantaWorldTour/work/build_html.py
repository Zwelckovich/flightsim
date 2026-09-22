from pathlib import Path
import json
from debrief_data import read_archive, write_journal
root=Path(__file__).resolve().parent
archive=read_archive(root.parent)
s=(root/'tour-template.html').read_text(encoding='utf8')
for marker,name in [('/*__D3__*/','d3.min.js'),('/*__TOPOJSON__*/','topojson.min.js'),('__DATA__','tour-data.json'),('__WORLD__','world.json'),('__BRIEFINGS__','briefings.json'),('__EXCURSIONS__','excursions.json'),('/*__EXCURSION_UI__*/','excursions-ui.js'),('__SCENERY__','scenery-guide.json'),('/*__SCENERY_UI__*/','scenery-ui.js'),('/*__SCENERY_CSS__*/','scenery-style.css'),('<!--__SCENERY_VIEW__-->','scenery-view.html'),('__DEBRIEFS__','../debriefings.json'),('/*__DEBRIEF_UI__*/','debrief-ui.js'),('/*__DEBRIEF_CSS__*/','debrief-style.css'),('<!--__DEBRIEF_VIEW__-->','debrief-view.html'),('/*__RESET_UI__*/','reset-ui.js'),('/*__RESET_CSS__*/','reset-style.css'),('<!--__RESET_VIEW__-->','reset-view.html'),('<!--__RESET_DIALOG__-->','reset-dialog.html')]:
    text=(root/name).read_text(encoding='utf8')
    if name.endswith('.json'):text=text.replace('<','\\u003c')
    s=s.replace(marker,text)
s=s.replace('</style>',(root/'comparison-style.css').read_text(encoding='utf8')+'\n</style>',1)
out=root.parent/'outputs'/'Volanta-Worldtour-EDLV.html'
out.write_text(s,encoding='utf8')
write_journal(root.parent,archive)
print(str(out),out.stat().st_size,'bytes')
