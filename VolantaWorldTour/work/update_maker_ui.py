from pathlib import Path
R=Path(__file__).resolve().parent
def edit(file,pairs):
 p=R/file;s=p.read_text(encoding='utf8')
 for old,new in pairs:
  assert old in s,(file,old[:100])
  s=s.replace(old,new)
 p.write_text(s,encoding='utf8')
edit('scenery-view.html',[
 ('Ein Kauf kommt nur in die engere Auswahl, wenn er gegenüber diesen Alternativen außergewöhnlich viel zum Anflug oder zur Landschaft beiträgt.','Ein Kauf kommt nur in die engere Auswahl, wenn er gegenüber diesen Alternativen außergewöhnlich viel zum Flugerlebnis beiträgt: durch herausragende Airportqualität, den Anflug, Gelände oder POIs.'),
 ('Drei optionale Kauf-Ausnahmen','Optionale Highlight-Käufe'),
 ('Cusco, Saint Barth und Hongkong: ausgewählt für ihren zusätzlichen Anflug- oder Landschaftswert.','Ausgewählt für herausragende Airportqualität und besonderen Anflug- oder Landschaftswert. Jeder Kauf bleibt optional.'),
 ('<div class="scenery-picks" id="sceneryShortlist"></div>','<div class="scenery-picks" id="sceneryShortlist"></div>\n <details class="scenery-method" open><summary>Deine bevorzugten Hersteller · konkreter Tour-Abgleich</summary><p id="manufacturerPolicy"></p><div class="table-wrap"><table class="manufacturer-table"><thead><tr><th>Hersteller</th><th>Zugeordnete Tour-Airports</th><th>Ergebnis</th></tr></thead><tbody id="manufacturerRows"></tbody></table></div><p class="small muted">Gezielt recherchierte Überschneidungen und Kaufkandidaten. Die Tabelle ist keine vollständige Qualitätsprüfung aller Produkte dieser Hersteller. Die genaue Prüftiefe steht weiterhin je Airport.</p></details>'),
 ('Auswahlmaßstab & bewusst nicht empfohlene Käufe','Weitere Kaufkandidaten · Abwägung und offene Fragen')
])
edit('scenery-ui.js',[
 ('${esc(p.developer)} · ${esc(p.name)}</strong><span class="comparison-stage','${p.developer?esc(p.developer)+\' · \':\'\'}${esc(p.name)}</strong><span class="comparison-stage'),
 ('<a href="${esc(p.url)}" target="_blank" rel="noopener noreferrer">Quelle ↗</a></div>','${p.verdict?`<p>${esc(p.verdict)}</p>`:\'\'}${p.compatibility?`<p class="small">${esc(p.compatibility)}</p>`:\'\'}${p.links?sceneryLinks(p.links):`<a href="${esc(p.url)}" target="_blank" rel="noopener noreferrer">Quelle ↗</a>`}</div>'),
 ('FSAddonCompare war für diesen Ort nicht auslesbar. Der ergänzende Web-Suchabgleich wurde durchgeführt; die Angebotsliste kann unvollständig sein.','Die FSAddonCompare-ICAO-Suche lieferte für diesen Ort keine auswertbare Antwort. Einzelprodukte können über andere Quellen erfasst sein; die Angebotsliste kann unvollständig sein.'),
 ('<span>Freeware-Projekte mit Entscheidung</span></div><p>','<span>Freeware-Projekte mit Entscheidung</span></div><div><b>${a.reviewedPaywareAirports}</b><span>Orte mit gezielter Kaufabwägung</span></div><p>'),
 ('Von 405 FSAddonCompare-Seiten waren ${a.fsacReadable} auslesbar, ${a.fsacUnavailable} nicht.','Von 405 FSAddonCompare-ICAO-Suchen lieferten ${a.fsacReadable} auswertbare Antworten, ${a.fsacUnavailable} blieben ohne auswertbares Ergebnis. Auch die auslesbaren Listen ersetzen keinen vollständigen Produktvergleich.'),
 ('renderScenery();\n}', '''$('#manufacturerPolicy').textContent=SC.manufacturerPolicy;
 $('#manufacturerRows').innerHTML=SC.manufacturers.map(m=>`<tr><td><a href="${esc(m.url)}" target="_blank" rel="noopener noreferrer"><strong>${esc(m.name)} ↗</strong></a></td><td>${m.codes.map(code=>`<button class="scenery-link mono" data-scenery="${code}">${code}</button>`).join(' ')}</td><td><p>${esc(m.note)}</p></td></tr>`).join('');
 renderScenery();
}'''),
 ("'Payware_Katalogtreffer'","'Payware_Kandidaten_und_Urteil'"),
 ("x.name+' ['+x.stage+'] '+x.url","x.name+' ['+x.stage+'] '+(x.verdict||'Nicht vertieft bewertet.')+' '+(x.compatibility||'')+' '+x.url"),
 ("a.fsacReadable?'ja':'nein; Web-Suchabgleich ergänzt'","a.fsacReadable?'ja':'keine auswertbare ICAO-Antwort; weitere Quellen ergänzt'")
])
p=R/'comparison-style.css';s=p.read_text(encoding='utf8');s+='\n.manufacturer-table{min-width:660px;width:100%}.manufacturer-table td{vertical-align:top;padding:14px}.manufacturer-table td:first-child{width:20%}.manufacturer-table td:nth-child(2){width:28%}.manufacturer-table p{margin:0;line-height:1.6}.manufacturer-table .scenery-link{padding:3px 5px}.comparison-summary{grid-template-columns:repeat(4,minmax(0,1fr))}@media(max-width:850px){.comparison-summary{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:450px){.comparison-summary{grid-template-columns:1fr}}\n';p.write_text(s,encoding='utf8')
print('Manufacturer policy, comparison verdicts, source links, and dynamic purchase section updated.')
