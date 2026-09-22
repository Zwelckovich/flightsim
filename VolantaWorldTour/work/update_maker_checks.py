from pathlib import Path
import json
R=Path(__file__).resolve().parent
p=R/'check_excursions.cjs';s=p.read_text(encoding='utf8')
s=s.replace("['SPZO','TFFJ','VHHH']","['LMML','NZAA','NZWN','SPZO','TFFJ','VHHH']")
s=s.replace('productReviewedAirports,74','productReviewedAirports,81')
s=s.replace("data-scenery-row=/g)||[]).length,74)","data-scenery-row=/g)||[]).length,81)")
s=s.replace("data-scenery-row=/g)||[]).length,331)","data-scenery-row=/g)||[]).length,324)")
s=s.replace("data-scenery-row=/g)||[]).length,3)","data-scenery-row=/g)||[]).length,6)")
s=s.replace("node('#sceneryShortlist').innerHTML.match(/<article /g)||[]).length,3)","node('#sceneryShortlist').innerHTML.match(/<article /g)||[]).length,6)")
s=s.replace('74 locations with product review','81 locations with product review').replace('three unowned optional purchases','six unowned optional purchases')
marker="assert(node('#comparisonSummary').innerHTML.includes('405 / 405'));"
s=s.replace(marker,marker+"\nassert.equal(S.auditSummary.reviewedPaywareAirports,21);\nassert.equal(S.auditSummary.fsacReadable,164);\nassert.equal(S.auditSummary.fsacUnavailable,241);\nassert.equal((node('#manufacturerRows').innerHTML.match(/<tr>/g)||[]).length,7);\nassert(node('#manufacturerRows').innerHTML.includes('Captain7'));\nassert(S.airports.EDDK.recommendation.includes('Jo Erlend'));\nassert(S.airports.FACT.comparison.payware.some(p=>p.verdict&&p.verdict.includes('12-Meter')));\nassert(!S.considered.NZWN);\nassert(S.products.LMML.caveat.includes('World Update IX'));\nassert(S.manufacturers.every(m=>m.codes.every(code=>S.airports[code])));")
s=s.replace("assert(exported.body.includes('Freeware_Kandidaten_und_Urteil'));","assert(exported.body.includes('Payware_Kandidaten_und_Urteil'));assert(exported.body.includes('Photogrammetrie'));assert(exported.body.includes('Moa Point'));assert(exported.body.includes('Freeware_Kandidaten_und_Urteil'));")
p.write_text(s,encoding='utf8')
p=R/'scenery-ui.js';s=p.read_text(encoding='utf8');s=s.replace('Object.entries(SC.products).map(',"Object.entries(SC.products).sort(([a],[b])=>SC.airports[a].order-SC.airports[b].order).map(");p.write_text(s,encoding='utf8')
p=R/'research-method.json';j=json.loads(p.read_text(encoding='utf8'));j.update(manufacturerPolicy=json.loads((R/'maker-review.json').read_text(encoding='utf8'))['policy'],fsacReadable=164,fsacUnavailable=241,productReviewedAirports=81,paywareReviewedAirports=21,limits='405 ICAO-Suchen versucht; 28 gekürzte Antworten einzeln nachgelesen. 40 weitere erfolglose Abrufe erneut versucht, ohne auswertbare Antwort. Entwicklerkataloge und Hersteller-/Reviewquellen ergänzen den Abgleich, schließen aber keine vollständige Prüfung aller Produkte ein.');p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
print('Updated expected recommendations and validated research coverage; added maker and product-verdict regression checks.')
