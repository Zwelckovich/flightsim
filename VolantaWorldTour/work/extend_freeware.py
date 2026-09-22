"""Curated decisions from the captured author pages and compatibility comments."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text(encoding='utf8'))
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
F=read('freeware-research.json');P={}
for f in R.glob('research-freeware-pages-*.json'):P.update(read(f.name))
discover=read('freeware-discovery.json')
def page(id):
 t=re.sub(r'L\d+: ?', ' ',P[id]['raw']);t=re.sub(r'\ue200[^\u2020\ue201]*\u2020([^\ue201]+)\ue201',lambda m:m[1].split('\u2020')[0],t)
 t=re.sub(r'\s+',' ',t)
 dm=re.search(r'Downloads (\d+(?:\.\d+)?)([KM]?)\b',t);rm=re.search(r'User Reviews (\d\.\d) (\d+) reviews',t)
 return dict(downloads=int(float(dm[1])*({'K':1000,'M':1000000}.get(dm[2],1))) if dm else None,rating=float(rm[1]) if rm else None,reviews=int(rm[2]) if rm else None,url=P[id]['url'],readable='### Description' in t,raw=t)
def select(code,id,developer,name,headline,version,updated,reason,compatibility,dependencies,caveat,links=None):
 p=page(id)
 F['selected'][code]=dict(developer=developer,name=name,headline=headline,downloads=p['downloads'],rating=p['rating'],reviews=p['reviews'],version=version,updated=updated,reason=reason,compatibility=compatibility,dependencies=dependencies,caveat=caveat,fallback='Die MSFS-Basis bleibt die Alternative ohne zusätzliche Installation.',links=[['Flightsim.to · Download, Bewertungen & Hinweise',p['url']]]+(links or []))
select('LROP','102093','rekinowy','Bucharest Henri Coandă International','Bukarest: starke aktuelle Freeware.','0.8.5','28.08.2026',
 'Individuelle Gebäude, überarbeitete Vorfelder und ein laut Autor an Juli 2026 angeglichenes Layout. Die breite, ausgezeichnete Resonanz und die fortlaufende Pflege tragen eine klare kostenlose Empfehlung.',
 'Der Autor nennt ausdrücklich MSFS 2020 und 2024. Keine eigene Prüfung im Fenix.',
 'Archivinhalt in den Community-Ordner; das verlinkte GSX-Profil ist optional.',
 'Militärvorfeld, eigene Bodenfahrzeuge und weitere Umgebungsgebäude sind noch auf der Entwicklungsliste. Kein vollständig ausmodellierter Endzustand behauptet.')
select('EYVI','7118','Ch3rka','Vilnius International','Eigenständiger Charakter in Vilnius.','1.7.1','23.09.2024',
 'Eigene Airportgebäude, Bodenmarkierungen und angepasste Pistenneigung geben dem Stopp deutlich mehr Charakter. Gute Bewertungsbreite und mehrere positive 2024-Rückmeldungen machen die Freeware zur bevorzugten Ergänzung.',
 'Mehrere Nutzer bestätigen ausdrücklich die Funktion in MSFS 2024. Ältere 2020-Veröffentlichung, keine native Neuentwicklung.',
 'Den eigentlichen Szenerieordner in Community legen, nicht den darüberliegenden Archivordner. Vorhandene konkurrierende EYVI-Pakete vermeiden.',
 'Das neueste reale Terminal ist nicht sicher abgedeckt. Einzelne Nutzer melden eingeschränkte GSX-Jetway-Anbindung; Version 1.7.1 enthält eine ILS-Ausrichtungskorrektur.')
select('YPKG','1886','NZA Simulations','Kalgoorlie-Boulder + Super Pit','Eine Goldmine neben dem Airport.','1.0.1','14.02.2022',
 'Eigene Terminal- und Vorfeldobjekte sowie die Super-Pit-Goldmine verbinden den Airport mit einem auffälligen Landschaftsziel. Rund 12.000 Downloads und 4,9/5 aus 25 Bewertungen passen zu deinem Qualitätsanspruch.',
 'NZA bestätigt in seinen MSFS-2024-Kompatibilitätsnachrichten ausdrücklich, dass die ältere Kalgoorlie-Freeware in 2024 funktioniert.',
 'Beide mitgelieferten Pakete installieren: Der getrennte Windsack-Fix ist laut Autor erforderlich. Aktuelle Installationshinweise auf der NZA-Seite beachten.',
 'Alte Veröffentlichung, nicht mit einer nativ neu gebauten 2024-Ausgabe verwechseln. Eigene Performance-Messung fehlt.',
 [['NZA · Produktumfang','https://nzasimulations.com/product/ypkg-kalgoorlie-boulder/'],['NZA · ausdrückliche 2024-Kompatibilität','https://nzasimulations.com/news/']])
select('VOCI','36258','martin.j','Cochin International · T3 update','Kochi mit markantem Terminal.','1.1.0','24.03.2024',
 'Das überarbeitete Terminal 3, lokale Vorfelddetails und Solar-Parkplatzdächer verbessern den Wiedererkennungswert. Sehr gute Resonanz und mehrere positive 2024-Berichte sprechen für diese kostenlose Ergänzung.',
 'Mehrere Nutzer bestätigen MSFS 2024; ein Bericht nennt ausdrücklich einen funktionierenden ILS-Z-Anflug auf RWY 09. Dies ersetzt keine eigene Prüfung mit Fenix und aktuellen Navdaten.',
 'Japan Airports Model Library KRC ist erforderlich. Das verlinkte GSX-Profil ist optional.',
 'WIP: weitere Terminalteile sind nicht vollständig neu modelliert. Ältere Kommentare nennen vereinzelte Bodenobjekt- und Performance-Probleme; zuerst einen kurzen Stand- und Rolltest machen.')

# Each reason is based on the actual page, not only its search snippet.
reviews={
 '68384':('SBBR','Sehr starke Resonanz. Für 2024 verweist der Autor auf die Photogrammetry-ON-Datei; nur eine Fassung installieren. Modelle bilden jedoch 2015 ab, Aktualisierung ist nicht geplant; zusätzlich Glasflimmern und versionsabhängige Höhenprobleme gemeldet. Daher ein interessanter Kandidat, aber keine uneingeschränkte Spitzenempfehlung.'),
 '63131':('SBBR','Trotz hoher Sternezahl ausdrücklich nicht mit MSFS 2024 kompatibel; Downloads auf der Seite gestoppt. Diese Ausgabe nicht empfehlen.'),
 '10471':('VOMM','Sehr gute Gesamtbewertung, aber ein konkreter 2024-Bericht nennt grasüberdeckte Taxiways. Der Autor nennt außerdem schwebende Brückenteile und Texturflimmern. Für deine strenge Qualitätsauswahl zurückgestellt.'),
 '3279':('OKKK','Große Nutzerbasis; aktuelle 2024-Nutzung hängt laut Autor von EICK-Objekten und einer experimentellen Discord-Fassung ab. Meldungen zu fehlenden Jetways bleiben relevant. Keine unkompliziert belegte Spitzenempfehlung.'),
 '9290':('OERK','2024 funktioniert laut mehreren Nutzern. Der Autor führt aber untexturierte Gebäude, Modellfehler an Terminal 5 und fehlende Gebäude als bekannte Einschränkungen. Gute Freeware, für die gewünschte enge Spitzenauswahl zurückgestellt.'),
 '51064':('RJOO','Ausgezeichnete Gesamtresonanz. In 2024 fehlen laut Rückmeldungen jedoch gerade die Circling-Anfluglichter; weitere Meldungen betreffen Jetways und Terrain. Das ist für deinen Schwerpunkt Anflug-Highlights ein wichtiger Vorbehalt.'),
 '47179':('VGHS','Der Änderungsverlauf berücksichtigt 2024. Die Rückmeldungen zu ILS/LOC widersprechen sich; zusätzlich bestehen Abhängigkeiten von City-Update-Objekten. Für Fenix-Anflüge vorerst keine uneingeschränkte Empfehlung.'),
 '5919':('EGNS','Sehr gute Resonanz, aber der letzte Stand ist von 2021; auf der gelesenen Seite bleibt die konkrete 2024-Frage unbeantwortet. Ein weiterer Bericht nennt störende Objekte am Vorfeld. Kompatibilität nicht allein aus dem Plattform-Badge ableiten.'),
 '7510':('NZQN','Die enthaltene handgefertigte Fassung bleibt die erste Wahl. Der ältere kostenlose Ersatz erreicht gute Werte, aber ein belastbarer zusätzlicher 2024-Mehrwert gegenüber dem enthaltenen Airport ist nicht belegt.'),
 '77425':('EPKK','Gute Resonanz, aber der Autor beschreibt den 2024-Betrieb nur als eingeschränkt nutzbar und nennt verschobene Bodentexturen. Deshalb keine Spitzenempfehlung.'),
 '3175':('EGGP','Den enthaltenen handgefertigten World-Update-Airport behalten. Der Freeware-Autor selbst beschreibt seine ältere Fassung nach dem UK-Update hauptsächlich als historische Alternative.'),
 '59837':('SBGL','Die Freeware-Downloads wurden gestoppt; der Autor verweist auf Zugang über eine kostenpflichtige Kanalmitgliedschaft. Zusätzlich bestehen Brückenmeldungen. Deshalb bei der enthaltenen Fassung bleiben.'),
 '14259':('RPVP','Gute, noch kleinere Bewertungsbasis, aber der Autor antwortet auf die 2024-Frage ausdrücklich, dass die Anpassung noch nicht erfolgt sei. Mehrere Objektbibliotheken sind erforderlich. Keine aktuelle 2024-Spitzenempfehlung.'),
 '2763':('VTBS','Beliebte ältere Modellumsetzung, Stand 2020. Kein belastbarer aktueller 2024-Nachweis und keine Bestätigung des heutigen Airportlayouts in der gelesenen Quelle.'),
 '8718':('LJLJ','Weiter gepflegtes Projekt, aber 4,7/5 und Meldungen zu fehlenden Anfluglichtern. Die 2024-Lage ist nicht ausreichend eindeutig; keine Spitzenempfehlung für diese Auswahl.'),
 '41863':('LYBE','2024-Nutzung wird bestätigt. Die Fassung von 2022 bildet jedoch den aktuellen Ausbau nicht ab; Nutzer melden fehlende Verfahren und verschobene Objekte. Deshalb trotz guter Sterne vorerst zurückgestellt.'),
 '4802':('ENTC','Kleine funktionale Verbesserung aus 2020, keine umfassende aktuelle Szenerie. 4,7/5 aus 11 Bewertungen und kein konkreter 2024-Nachweis reichen hier nicht für die Spitzenauswahl.'),
 '19483':('OAKB','2024-Rückmeldungen sind positiv. Allerdings nur neun Bewertungen; außerdem fehlen laut Kommentaren Beleuchtung bzw. Jetways. Als Kandidat sichtbar, aber keine belegte Spitzenempfehlung.'),
 '95345':('WIII','Der Autor bestätigt 2024, nennt aber fehlende nächtliche Glastexturen. 4,2/5 aus fünf Bewertungen trägt keine Spitzenempfehlung.'),
 '82173':('FMCZ','Sehr gute kleine Bewertungsbasis. Aktuelle Nutzer melden überhohe Bäume im Anflug; mehrere Bibliotheken und World Update Oceania sind erforderlich. Für deinen Anflug-Schwerpunkt zurückgestellt.'),
 '81837':('EFMA','Nur fünf Bewertungen; die Seite belegt keine ausreichend eindeutige 2024-Konfiguration. Enthält zwar auch Stadtobjekte, bleibt aber unter der gewünschten Belegstärke.'),
 '30333':('FSIA','Überwiegend Korrektur von Taxiways und Vorfeldern, keine vollständige eigene 3D-Umsetzung. Nur zwei Bewertungen mit 4,0/5 und Verfahrensmeldungen; keine Spitzenempfehlung.'),
 '44599':('TBPB','2024-Nutzung ist belegt, aber Nutzer melden fehlende beziehungsweise schwebende Anflug- und Pistenlichter. Mit 13 Bewertungen und diesen für dich relevanten Vorbehalten vorerst zurückgestellt.'),
 '17191':('TIST','Ein Nutzer bestätigt 2024. Der Autor weist weiter auf ältere Absturzprobleme hin; eine erforderliche Personenbibliothek ist laut Kommentaren nicht einfach verfügbar. Keine ausreichend belastbare unkomplizierte Empfehlung.'),
 '60881':('EGYP','Positive 2024-Berichte, aber laut Autor nur als 2020-Ausgabe getestet und auf begrenzte Bildreferenzen gestützt. Benötigt RAF Lossiemouth; elf Bewertungen reichen für deine strenge Spitzenauswahl noch nicht.'),
 '16969':('RORS','Eine eigene 2024-Fassung ist vorhanden und verbessert auch Küstengelände. Nur drei Bewertungen; der Autor nennt weiterhin ein abweichendes Terminalmodell. Deshalb zuerst den enthaltenen WU-I-Airport nutzen.'),
 '27331':('VRMM','Nur 3,7/5 aus zehn Bewertungen. Älteres generisches Layout; Nutzer melden auf die alte Piste ausgerichtetes ILS. Für den Fenix-Anflug nicht empfohlen.'),
 '364':('FHAW','Nutzer bestätigt 2024, aber kleine Bewertungsbasis und vom Autor beschriebene Höhenkompromisse. Interessanter Ausbau mit optionalem Luftbild, noch keine ausreichend belegte Spitzenempfehlung.'),
 '9036':('TKPK','Älterer Stand, 4,7/5 aus 14 Bewertungen und keine konkrete 2024-Bestätigung in den gelesenen Daten. Keine Spitzenempfehlung.'),
 '4808':('TFFF','Gute Resonanz, jedoch vor allem Wasser-/Grunddarstellungskorrektur mit ausgewiesener 2020-Version. Ein aktueller Mehrwert samt 2024-Nutzbarkeit ist nicht belegt.'),
 '54935':('MBPV','Vielversprechend: 4,9/5 aus 20 Bewertungen, etwa 8.000 Downloads und positive 2024-Rückmeldungen. Noch unter dem gewählten engen Downloadmaßstab; zusätzliche Bibliotheken und eine laut Autor schwer weiterzuentwickelnde ältere Fassung. Als geprüfte Alternative behalten.'),
 '49601':('PHNL','Sehr gute Resonanz und positive 2024-Meldung. Deine vorhandene iniBuilds-Szenerie hat Vorrang; es gibt keinen belegten Grund, sie durch diese kostenlose Teilüberarbeitung zu ersetzen.'),
 '29995':('PHKO','Gute Resonanz, aber die 2024-Frage bleibt offen. Zuerst die enthaltene handgefertigte World-Update-XIII-Fassung verwenden; auch der Autor weist auf deren Qualität hin.'),
 '46265':('PGUM','2024-Bericht positiv, jedoch nur acht Bewertungen und zahlreiche verwendete Standardbibliotheksobjekte. Kein ausreichend belegtes Spitzenprodukt; deshalb vorerst Basis.'),
 '42879':('NSTU','Eigene 2024-Neufassung mit positiven Rückmeldungen vorhanden. Nur acht Bewertungen und rund 4.000 Downloads; daher geprüfter Kandidat statt Spitzenempfehlung.'),
 '62629':('NSFA','2024-Rückmeldung positiv, aber nur drei Bewertungen und umfangreiche Bibliotheksabhängigkeiten. Keine ausreichend breit belegte Qualitätsfreigabe.'),
 '35138':('NVVV','2024-Ausgabe und zusätzliche Circling-Lichter sind besonders interessant; dafür EDHK-Bibliothek nötig. Nur fünf Bewertungen, deshalb geprüfter Kandidat mit Potenzial statt Spitzenempfehlung.'),
 '31874':('YBCS','3,9/5 aus acht Bewertungen; kein ausreichender Qualitätsbeleg für deine enge Freeware-Auswahl.'),
 '25405':('VTSP','Nur 4,0/5 aus sechs Bewertungen; fehlende Gates und weitere Vorbehalte dokumentiert. Ein 2024-Zusatzpatch existiert, macht daraus aber noch keine belegte Spitzenempfehlung.'),
 '37122':('VYYY','4,8/5, aber nur neun Bewertungen, älterer Stand und keine konkrete 2024-Bestätigung in den gelesenen Belegen.'),
 '15167':('VVTS','4,4/5 aus zwölf Bewertungen; bekannte Jetway-Texturfehler und offene 2024-Frage. Keine Spitzenempfehlung.'),
 '41754':('VVCR','Positive 2024-Rückmeldungen, aber nur sieben Bewertungen. Zusätzliches Luftbild ist erforderlich. Als guter Kandidat vermerkt, Belegstärke für die Spitzenauswahl noch zu klein.'),
 '19516':('VLLB','Der Autor nennt nicht nutzbare Jetways; älterer Stand und elf Bewertungen. Die aktuelle 2024-Qualität ist nicht ausreichend belegt.'),
 '11495':('VABB','4,7/5 aus 24 Bewertungen. Nutzer melden Beleuchtungs- und ILS-Probleme; die konkrete 2024-Frage bleibt offen. Für den Fenix nicht als Spitzenempfehlung ausgewählt.'),
 '37640':('OOMS','Starke Gesamtresonanz, aber widersprüchliche 2024-Rückmeldungen einschließlich erheblicher FPS-Probleme bei der GSX-Fassung. Zusätzlich ist das dargestellte Bahnlayout veraltet. Deshalb vorerst zurückgestellt.'),
 '39738':('FMNN','Nur eine Bewertung und eine ausdrücklich unfertige frühe Umsetzung. Keine belegte Spitzenempfehlung.'),
 '65986':('FAOR','3,0/5 aus drei Bewertungen. Diese Resonanz und die geringe Datenbasis genügen dem gewünschten Qualitätsmaßstab nicht.'),
 '86442':('FZAA','Positiver Eindruck und 5,0/5 aus elf Bewertungen; rund 4.000 Downloads. Noch keine ausreichend breite und konkrete 2024-Beleglage für die enge Empfehlungsliste.'),
 '76438':('GBYD','Rund 1.000 Downloads, keine belastbare Bewertungsbasis verifiziert. Funktionale Verbesserung, aber keine belegte Spitzenszenerie.'),
 '23253':('GQNO','4,0/5 aus drei Bewertungen; Nutzer meldet Doppelung mit dem 2024-Luftbild und seitlich versetztes ILS. Keine Empfehlung für den Fenix-Anflug.'),
 '17668':('DAAG','Nur drei Bewertungen, Stand 2021 und primär Korrektur von Vorfeldern und Taxiways. Aktuelle 2024-Spitzenqualität nicht belegt.'),
 '52070':('LDDU','Etwa 1.000 Downloads, keine belastbare Bewertungsbasis verifiziert. Der Autor kündigt eine neue Fassung separat an. Keine Empfehlung aus den vorhandenen Belegen.'),
 '7336':('LRCL','4,3/5 aus neun Bewertungen; eigene Verfahren wurden laut Autor nur mit Standardflugzeugen getestet. Keine belastbare 2024-/Fenix-Empfehlung.'),
 '99067':('EGPE','Aktive native 2024-Pflege und SU6-Anpassung sind positiv. Nur sechs Bewertungen und rund 3.000 Downloads; deshalb als aussichtsreicher Kandidat sichtbar, noch keine breit belegte Spitzenempfehlung.'),
 '2862':('SCRM','Gute Paketbewertung, aber die vom Autor aufgeführten 20 Flugplätze enthalten SCRM nicht. Dieses Paket löst die konkret geplante Antarktis-Landestelle daher nicht.'),
 '1221':('SAZB','Der Autor beschreibt funktionale Verbesserungen mit Standardobjekten, keine originalgetreuen eigenen Gebäude. Dazu ein 2024-Absturzbericht. Keine pauschale Empfehlung für die Argentinien-Stopps.'),
 '53291':('DFFD DRRN','Gute Paketresonanz, aber sehr viele Bibliotheken, teils generische Nachbildungen und uneinheitliche 2024-Berichte. Nutzer bestätigen insbesondere Ouagadougou/Niamey; das belegt keine durchgängig exzellente 2024-Qualität aller enthaltenen Airports.')
}
existing={r['url']:r for r in F['considered']}
reviewed={}
S=read('scenery-guide.json')
for id,(codes,reason) in reviews.items():
 p=page(id);codes=[c for c in codes.split() if c in S['airports']]
 assert codes and p['readable'],(id,codes)
 title=discover.get(id,{}).get('title',P[id]['raw'].split(' (https:')[0].split(' - Airports for')[0])
 if p['rating'] is not None:metrics='ca. '+f"{p['downloads']:,}".replace(',','.')+' Downloads · '+f"{p['rating']:.1f}".replace('.',',')+f"/5 · {p['reviews']} Bewertungen"
 else:metrics=f"ca. {p['downloads'] or '?'} Downloads · Bewertungsbasis nicht verifiziert"
 row=dict(codes=codes,name=title,metrics=metrics,reason=reason,url=p['url'])
 existing[p['url']]=row;reviewed[id]={**row,**{k:p[k] for k in ['downloads','rating','reviews']}}
F['considered']=list(existing.values())
F['metricsNote']='Gerundete, kumulierte Plattformwerte aus den gelesenen Produktseiten; ältere Versionen können in Bewertungen enthalten sein. Recherche am 21.09.2026; Suchindex und Seitenstände können zeitlich abweichen. Keine eigenen Simulator-Messungen.'
write('freeware-research.json',F);write('research-reviewed.json',reviewed)
print('Selected',list(F['selected']),'considered',len(F['considered']),'new page decisions',len(reviewed))
