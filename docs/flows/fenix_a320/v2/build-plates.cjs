const fs=require('node:fs');
const path=require('node:path');
const out=path.join(__dirname,'plates');fs.mkdirSync(out,{recursive:true});
const C={navy:'#123052',muted:'#526c7c',blue:'#087ee5',teal:'#007f92',amber:'#fff1c8',red:'#a63c31',line:'#d9e4ea',pale:'#edf5f7',green:'#19765b'};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function wrap(s,n=36){const words=String(s).split(' '),r=[];let l='';for(const w of words){if(l.length+w.length+1>n){r.push(l);l=w;}else l+=(l?' ':'')+w;}if(l)r.push(l);return r;}
function txt(x,y,s,size=20,fill=C.navy,weight=400,anchor='start'){return '<text x="'+x+'" y="'+y+'" font-size="'+size+'" fill="'+fill+'" font-weight="'+weight+'" text-anchor="'+anchor+'">'+esc(s)+'</text>';}
function lines(x,y,arr,size=20,fill=C.navy,weight=400,gap=28){return arr.map((s,i)=>txt(x,y+i*gap,s,size,fill,weight)).join('');}
function line(d,color=C.blue,width=5,dash='',arrow=false){return '<path d="'+d+'" fill="none" stroke="'+color+'" stroke-width="'+width+'" stroke-linecap="round" stroke-linejoin="round"'+(dash?' stroke-dasharray="'+dash+'"':'')+(arrow?' marker-end="url(#arr)"':'')+'/>';}
function rect(x,y,w,h,fill=C.pale,stroke=C.line,r=10){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+r+'" fill="'+fill+'" stroke="'+stroke+'"/>';}
function dot(x,y,n){return '<circle cx="'+x+'" cy="'+y+'" r="'+(n?16:8)+'" fill="#fff" stroke="'+C.blue+'" stroke-width="4"/>'+(n?txt(x,y+6,n,17,C.blue,700,'middle'):'');}
function leader(points){return '<polyline points="'+points+'" stroke="'+C.muted+'" stroke-width="1.8" fill="none"/>';}
function box(x,y,w,head,body=[],opts={}){const sz=opts.size||20,bs=body.flatMap(s=>wrap(s,Math.floor((w-32)/(sz*.53)))),hh=42,h=hh+18+bs.length*28;return (opts.leader?leader(opts.leader):'')+rect(x,y,w,h,opts.fill||C.amber,opts.color||C.teal,8)+'<path d="M'+(x+8)+' '+y+'H'+(x+w-8)+'Q'+(x+w)+' '+y+' '+(x+w)+' '+(y+8)+'V'+(y+hh)+'H'+x+'V'+(y+8)+'Q'+x+' '+y+' '+(x+8)+' '+y+'Z" fill="'+(opts.color||C.teal)+'"/>'+txt(x+16,y+28,head,20,'#fff',650)+lines(x+16,y+hh+29,bs,sz,C.navy,550);}
function runway(x,y,w=300,reverse=false){if(reverse)return '<g transform="translate('+(2*x+w+18)+' 0) scale(-1 1)">'+runway(x,y,w)+'</g>';return '<path d="M'+x+' '+y+'h'+w+'l18 35H'+(x+18)+'Z" fill="#78868c" stroke="#314956" stroke-width="2"/>'+[7,13,19,25].map(d=>line('M'+(x+16+d*.45)+' '+(y+d)+'h43','#fff',2)).join('')+line('M'+(x+90)+' '+(y+17)+'h'+(w-110),'#fff',2,'18 15');}
function section(x,y,w,title,body){return rect(x,y,w,Math.max(100,63+body.length*23),'#f1f7fa')+txt(x+20,y+33,title,21,C.teal,700)+lines(x+20,y+62,body,17,C.muted,400,23);}
function save(name,title,sub,body,source,h=1040,desc=title){
 const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="'+h+'" viewBox="0 0 1536 '+h+'" role="img" aria-labelledby="title desc"><title id="title">'+esc(title)+'</title><desc id="desc">'+esc(desc)+'</desc><defs><marker id="arr" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto-start-reverse"><path d="M0 0L5 2.5L0 5Z" fill="'+C.blue+'"/></marker><marker id="dim" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0 0L7 3.5L0 7Z" fill="'+C.muted+'"/></marker></defs><rect width="1536" height="'+h+'" fill="#fff"/><g font-family="Segoe UI,Arial,sans-serif">'+txt(56,47,'FENIX A320 · VISUAL LEARNING',14,C.teal,700)+txt(56,99,title,42,C.navy,750)+txt(56,131,sub,18,C.muted)+line('M56 152H1480',C.line,1)+body+line('M56 '+(h-78)+'H1480',C.line,1)+txt(56,h-48,source,15,C.muted)+txt(56,h-22,'Schematic · Not to scale · For simulation use only',14,C.muted)+'</g></svg>';
 fs.writeFileSync(path.join(out,name+'.svg'),svg);
}
// Same geometry for direct comparison; vertical gate is measured to runway elevation.
let b='';
for(const [y,label,early]of [[190,'01 · DECELERATED',false],[605,'02 · EARLY STABILIZED',true]]){
 b+=txt(70,y,label,23,C.teal,750)+txt(70,y+31,early?'VAPP und Landekonfiguration bereits am FDP':'Verzögerung und Konfiguration während des Endanflugs',19,C.muted);
 b+=line('M120 '+(y+163)+'H740L1320 '+(y+303))+runway(1320,y+303,130)+line('M120 '+(y+303)+'H1460',C.line,1,'8 7');
 b+=dot(early?220:390,y+163)+dot(740,y+163)+dot(1130,y+257);
 b+=txt(early?220:390,y+196,'D',19,C.teal,700,'middle')+txt(740,y+196,'FDP',18,C.teal,700,'middle');
 b+=box(76,y+40,300,early?'Früher konfigurieren':'APPR phase / DECEL',early?['Vor dem FDP verzögern','Landekonfig. erreichen']:['Managed speed','Green dot → S / F → VAPP'],{leader:(early?'220':'390')+','+(y+163)+' 300,'+(y+157)});
 b+=box(570,y+40,325,'Am Final Descent Point',early?['Landekonfiguration','VAPP']:['Meist CONF 1 / S speed','CONF 2 früher, wenn nötig'],{leader:'740,'+(y+163)+' 740,'+(y+155)});
 b+=box(1000,y+40,438,early?'Im Final beibehalten':'Stabilisierung im Planungsprofil',early?['Landekonfiguration und VAPP','Pfad, Schub und Stabilität überwachen']:['Landekonfiguration / VAPP','Spätestens 1000 ft über Flugplatz'],{leader:'1130,'+(y+257)+' 1160,'+(y+156)});
 if(!early)b+=line('M1130 '+(y+261)+'v42',C.muted,1.5)+txt(1114,y+292,'1000 ft*',15,C.muted,550,'end');
}
b+=txt(70,1002,'* Planungsbeispiel ohne CDA. Das tatsächlich anwendbare Stabilisierungskriterium bleibt maßgeblich.',17,C.muted);
save('approach-techniques','Zwei Wege zum stabilisierten Anflug','Gleicher Flugweg, unterschiedlicher Zeitpunkt für Verzögerung und Landekonfiguration.',b,'Airbus Safety First · Control your Speed… During Descent, Approach and Landing · figs. 18–19',1120);
// Engine-out: deliberately avoids assigning unresolved altitude / thrust duration.
b=section(56,178,1424,'Vor dem Start gemeinsam briefen',['EO routing · geplante und maximale EO ACC · Schubzeitlimit · ECAM/QRH für den tatsächlichen Fehler']);
b+=rect(641,342,480,465,'#fff8e8','#e6cb7d',10)+txt(665,376,'ACCELERATION WINDOW',17,'#8d640b',700);
b+=runway(75,810,200)+line('M185 810L655 550H1120L1450 420');
b+=line('M280 753l65 -36',C.blue,5,'',true)+line('M804 550h55',C.blue,5,'',true)+line('M1270 491l55 -22',C.blue,5,'',true);
b+=box(56,342,275,'Nach V1',['Start fortsetzen','SRS / Flugweg führen'],{});
b+=box(353,342,258,'Positive climb',['GEAR UP','Asymmetrie beherrschen'],{leader:'480,486 480,647'});
b+=box(62,550,298,'ECAM / QRH',['Passende Fehlerprozedur','Ausführung mit sicherem Flugweg koordinieren'],{});
b+=box(665,402,423,'Übergang zum Beschleunigen',['Engine securing, MAX EO ACC und Schubzeitlimit zusammen anwenden.'],{fill:'#fff3ce'});
b+=dot(655,550)+dot(795,550)+dot(940,550)+dot(1120,550)+dot(1290,483);
b+=box(652,608,206,'F speed',['FLAPS 1'],{leader:'795,550 752,608'});
b+=box(880,608,215,'S speed',['FLAPS 0'],{leader:'940,550 960,608'});
b+=box(1150,600,330,'Green dot / weiterer Steigflug',['Routing / Freigabe','MCT gemäß Verfahren'],{leader:'1240,503 1250,600'});
b+=section(56,837,1424,'Quellenkonflikt bleibt sichtbar',['Keine pauschale Warteanweisung „erst nach secured“ und kein universelles 10-Minuten-Limit.',
 'Diese Übersicht ersetzt nicht die noch fehlende, passende CFM-Sharklet-Verfahrensquelle.']);
save('engine-out-profile','Engine Failure after V1','Steigflug → Beschleunigung → weiterer Steigflug. Höhen und Zeiten bleiben flugspezifisch.',b,'V1 / FSLabs Engine Failure · V2 source review · Airbus Safety First: engine fire / climb speed',1040);
// Quick return top view; close path joins the same runway.
b=line('M930 790L1260 650Q1420 590 1370 350H385Q170 350 175 570Q180 655 365 710L770 790');
b+=runway(770,790,160)+line('M1140 706l60 -25',C.blue,5,'',true)+line('M1310 350h-50',C.blue,5,'',true)+line('M720 350h-50',C.blue,5,'',true)+line('M186 467l-4 46',C.blue,5,'',true)+line('M530 743l50 10',C.blue,5,'',true);
b+=line('M770 350V790',C.line,1.5,'7 7')+dot(770,350)+dot(930,790)+dot(1260,650)+dot(1230,350)+dot(385,350)+dot(184.2,602.8)+dot(365,710);
b+=box(830,493,415,'Nach dem Start / EO ACC',['Sicherer Flugweg','Level-off / selected S speed','Über F: CONF 1, falls T/O CONF > 1'],{leader:'1170,637 1260,650'});
b+=box(1110,178,365,'At S speed / Downwind',['CONF 1 und S beibehalten','APPR phase aktivieren','FCU speed PUSH'],{leader:'1230,350 1230,322'});
b+=box(630,224,285,'Abeam threshold',['STOPWATCH START'],{leader:'770,350 770,312'});
b+=box(227,205,295,'Turning base',['FLAPS 2'],{leader:'385,350 385,293'});
b+=box(390,450,310,'Bei CONF 2',['L/G DOWN'],{leader:'184.2,602.8 390,530'});
b+=box(408,584,298,'Fahrwerk ausgefahren',['Finale Landekonfiguration'],{leader:'365,710 408,672'});
b+=line('M385 385H770',C.muted,1.5)+txt(578,418,'45 s ± 1 s / kt Windkomponente',18,C.muted,600,'middle');
b+=section(56,850,1424,'Eigenständige Quick-return-Konfiguration',['Die dargestellte Variante bleibt in CONF 1. Nicht erst den vollständigen Clean-up aus dem anderen EO-Profil durchlaufen.']);
save('quick-return','Engine-out · Quick VMC Return','Draufsicht: Abflug, Rückkehr und Konfigurationspunkte in einem zusammenhängenden Flugweg.',b,'V1 · FSLabs A320 Engine Out Quick VMC Return · simulator training profile',1050);
// Circling: true plan view. 45-degree leg relative to horizontal instrument final.
b=runway(655,650,220,true)+line('M100 650H440L770 320H1190Q1390 320 1380 495Q1370 650 1110 668H875');
b+=line('M440 650H655',C.line,2,'8 7')+line('M520 570l50 -50',C.blue,5,'',true)+line('M970 320h50',C.blue,5,'',true)+line('M1380 463v37',C.blue,5,'',true)+line('M1090 668h-55',C.blue,5,'',true);
b+=dot(440,650)+dot(770,320)+dot(875,320)+dot(1190,320)+dot(1307.5,615.75)+line('M875 320V650',C.line,1.5,'6 7');
b+='<path d="M515 650A75 75 0 0 0 493 597" fill="none" stroke="'+C.muted+'" stroke-width="1.5"/>'+txt(532,625,'45°',20,C.teal,700);
b+=box(56,413,343,'Instrumentenanflug',['CONF 3 / L/G DOWN','Spoilers armed / F speed','Level-off an Circling MDA(H)'],{leader:'390,557 440,650'});
b+=box(405,197,336,'Offset zum Downwind',['30 s ab wings level','nach dem Ausdrehen'],{leader:'590,313 575,515'});
b+=box(783,183,302,'Abeam threshold',['STOPWATCH START'],{leader:'875,320 875,271'});
b+=box(1120,183,350,'Turning base',['Nach 3 s / 100 ft Höhe'],{leader:'1190,320 1220,271'});
b+=box(966,461,315,'Vor dem Sinkflug',['Schwelle identifiziert','Korrekter Sinkpfad','Dann Landekonfiguration'],{leader:'1281,590 1307.5,615.75'});
b+=section(56,752,695,'Instrumentenachse und Landebahn',['45° zeigt den seitlichen Versatz in der Draufsicht.',
'Die Zeichnung definiert weder Schutzraum noch Minima.']);
b+=section(775,752,705,'Während des Manövers',['Sichtreferenz, Charts und anwendbares Verfahren führen.',
'Verlust der Sichtreferenz: gebrieftes Missed-Approach-Verfahren.']);
save('circling','Circling Approach','Draufsicht mit eindeutigem Offset, Downwind, Base und Landebahn.',b,'Blackbox711 · Simple Circling Approach · source training profile',970);
// Touch-and-go plan with a large runway-detail strip.
b=line('M870 735L1275 615Q1390 563 1340 340H415Q210 340 205 520Q200 621 388 678L700 735')+runway(700,735,170);
b+=line('M1010 694l60 -18',C.blue,5,'',true)+line('M1230 340h-50',C.blue,5,'',true)+line('M780 340h-50',C.blue,5,'',true)+line('M211 472l-4 33',C.blue,5,'',true)+line('M514 701l45 8',C.blue,5,'',true);
b+=box(889,423,411,'Nach Gear up / im Steigflug',['CLB thrust / F/D OFF','500 ft AGL: Turn downwind','1000 ft AGL: Pitch 10° / thrust 75%'],{leader:'1170,567 1275,615',size:18});
b+=box(1114,178,355,'Pattern altitude',['CONF 2 / F + 20','Pitch ≈ 6° · thrust ≈ gross weight'],{leader:'1340,340 1290,294',size:18});
b+=box(697,178,360,'Downwind',['2 × Wind correction angle','APPR phase aktivieren'],{leader:'920,340 920,294'});
b+=box(367,192,288,'Abeam threshold',['Stopwatch / managed speed','≈ 45% thrust → F speed'],{leader:'570,340 570,308',size:18});
b+=box(435,390,385,'Zeit abgelaufen',['Turn / descend / L/G DOWN','F speed'],{leader:'415,340 435,390',size:18});
b+=box(435,530,435,'Base / Final',['Finale Flap-Konfiguration','Landing C/L: außer Spoilers','1000 ft AGL: stabilisiert / Vtgt'],{leader:'205,520 435,590',size:18});
for(const [x,y]of [[1275,615],[1340,340],[920,340],[570,340],[415,340],[205,520],[388,678]])b+=dot(x,y);
b+=txt(56,860,'DETAIL · AUF DER BAHN',21,C.teal,750);
const strip=[
 ['01','Centreline','Reverse geschlossen','Spoilers nicht aktiv'],
 ['02','CONF 2','N1 ≈ 50%','Quellenwert für CFM'],
 ['03','Trim prüfen','Grünes Band','vor TOGA'],
 ['04','TOGA → Rotate','Rotation bei Bug speed','gemäß Trainingsprofil']];
strip.forEach((v,i)=>{const x=56+i*362;b+=rect(x,887,338,142,i===2?'#fff1c8':C.pale);b+=txt(x+18,917,v[0],16,C.teal,750)+txt(x+18,950,v[1],23,C.navy,700)+lines(x+18,981,v.slice(2),18,C.muted,400,25);if(i<3)b+=line('M'+(x+342)+' 957h16',C.blue,2,'',true);});
save('touch-and-go','Touch and Go','Platzrunde plus vergrößerter Ablauf nach dem Aufsetzen. Zahlen aus dem Trainingsblatt.',b,'V1 · FSLabs A320 Touch and Go · N1 shown for the chosen CFM profile; no IAE EPR value',1140);
// Flap state chart with distinct commanded and automatic transitions, no interactive flight control.
b=section(56,180,1424,'Hebelstellung 1 kann zwei Oberflächenkonfigurationen bedeuten',['CONF 1: Slats ausgefahren · CONF 1+F: Slats und Flaps ausgefahren. Hebel und Oberflächen getrennt betrachten.']);
b+=box(58,344,314,'Hebel 0 → 1',['CAS ≤ 100 kt → 1+F','CAS > 100 kt → 1'],{fill:C.pale});
b+=box(1160,344,314,'Hebel 2 → 1',['CAS < 210 kt → 1+F','CAS ≥ 210 kt → 1'],{fill:C.pale});
b+=rect(477,345,225,157,'#e7f5f0','#78b39b')+txt(590,407,'1+F',47,C.green,750,'middle')+txt(590,448,'SLATS + FLAPS',18,C.green,650,'middle');
b+=rect(818,345,225,157,'#e8f2ff','#83b5dc')+txt(930,407,'1',47,C.blue,750,'middle')+txt(930,448,'SLATS',18,C.blue,650,'middle');
b+=line('M700 378H818',C.blue,3,'',true)+line('M820 470H702',C.blue,3,'',true);
b+=box(480,567,561,'Automatisch 1+F → 1',['IAS > 210 kt','Flaps fahren ein, Slats bleiben ausgefahren.'],{leader:'760,378 760,567'});
b+=box(480,774,561,'Automatisch 1 → 1+F',['CAS < 100 kt','Flaps fahren aus.'],{leader:'825,470 1104,470 1104,832 1041,832'});
b+=section(56,548,366,'Aus der Quellgrafik',['2 → 1 bei ≥ 210 kt liegt','oberhalb des dort genannten','CONF-2-VFE von 200 kt.']);
b+=lines(78,727,['Systemlogik erklären heißt nicht,','diese Geschwindigkeit anzufliegen.','Grenzwerte gelten unabhängig.'],18,C.red,600,26);
b+=section(1110,640,368,'Bei der normalen Retraktion',['F speed → Hebel 1','S speed → Hebel 0']);
b+=lines(1128,788,['Weitere Bedingungen wie','Alpha-/Speed-Lock stehen','in der Referenztabelle.'],18,C.muted);
save('flap-logic','Flap Movement Logic','Befehle des Piloten und automatische Übergänge getrennt und lesbar.',b,'V1 · Flap movement logic / FSLabs reference · thresholds retained as source values',1080);
// Cockpit: source image kept unchanged. Clean panel-zone abstraction is not a fabricated cockpit photograph.
const legacy=fs.readFileSync(path.resolve(__dirname,'../Fenix_A320_Flow.html'),'utf8');const legacyJs=legacy.match(/<script>([\s\S]*?)<\/script>/)[1];const legacyContext={};require('node:vm').runInNewContext(legacyJs.slice(0,legacyJs.indexOf('const FIELDS ='))+';globalThis.images=IMAGES;',legacyContext);const raw=legacyContext.images.flowpattern;
b+= ''; // next plate uses its own body
b=txt(58,196,'QUELLBILD · UNVERÄNDERT',19,C.teal,700)+rect(56,218,536,510,'#edf1f4');
b+='<image href="'+raw+'" x="73" y="240" width="502" height="445" preserveAspectRatio="xMidYMid meet"/>';
b+=lines(73,765,['Vorhandene V1-Aufnahme, keine neue Fenix-Aufnahme.','Grün: PF · Weiß: CAPT/FO laut Quelle.','Die Rollen sind keine PF/PM-Neuzuweisung.'],18,C.muted,400,28);
b+=txt(644,196,'LESBARE ZONENÜBERSICHT',19,C.teal,700);
b+=rect(799,224,450,145,C.pale)+txt(1024,310,'OVERHEAD',24,C.navy,700,'middle')+dot(1024,254,'1');
b+=rect(664,390,752,72,C.pale)+txt(1185,434,'GLARESHIELD',20,C.navy,650)+dot(1039,425,'5');
b+=rect(664,484,216,142,C.pale)+rect(894,484,293,142,C.pale)+rect(1201,484,216,142,C.pale);
b+=txt(772,556,'CAPT',21,C.navy,650,'middle')+dot(772,591,'6')+txt(1040,577,'CENTER',21,C.navy,650,'middle')+dot(1040,524,'2')+txt(1309,556,'FO',21,C.navy,650,'middle')+dot(1309,591,'6');
b+=rect(897,645,286,242,C.pale)+txt(1040,858,'PEDESTAL',21,C.navy,650,'middle')+dot(1040,784,'3')+dot(935,681,'4');
b+=line('M1000 281V242',C.blue,3,'',true)+line('M926 550H1160',C.blue,3,'',true)+line('M1007 720V824',C.blue,3,'',true)+line('M1080 720V824',C.blue,3,'',true)+line('M891 425H987',C.blue,3,'',true);
b+=txt(650,936,'Die Nummerierung erklärt die V1-Zonen; einzelne Schalter bleiben in den Flow-Schritten.',17,C.muted);
save('cockpit-flow','Cockpit Flow Pattern','Quellbild neben einer klaren räumlichen Zonenkarte. Für Orientierung und Reihenfolge.',b,'V1 · cockpit flow pattern, zones 1–6 · schematic panel zones, not a Fenix switch-location reference',1040);
console.log('Created 7 SVG plates in '+out);
