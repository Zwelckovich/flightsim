const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = path.resolve(__dirname, '../Fenix_A320_Flow.html');
const original = fs.readFileSync(source, 'utf8');
const fingerprint = require('node:crypto').createHash('sha256').update(fs.readFileSync(source)).digest('hex');
if(fingerprint !== '7a5b022db07b9bfbb972ea8dc944c4783202014d2d6ee3719433f7d7f50b3941') throw Error('V1 baseline changed. Review ID mapping before rebuilding.');
const script = original.match(/<script>([\s\S]*?)<\/script>/)[1];
const context = {};
vm.runInNewContext(script.slice(0,script.indexOf('const FIELDS ='))+';globalThis.result={DATA,IMAGES,MAP}',context);
const {DATA,IMAGES,MAP} = context.result;
const phase = id => DATA.find(p=>p.id===id);
for (const p of DATA) for (const [i,it] of p.items.entries()) if(Array.isArray(it)) {
  it[3] = {...it[3], id:`${p.id}.v1-${String(i).padStart(3,'0')}`};
  if(it[3].m) it[3].history = it[3].m;
  delete it[3].m;
}
function item(p,title){const it=phase(p).items.find(i=>Array.isArray(i)&&i[0]===title); if(!it)throw Error(p+' / '+title);return it}
function patch(p,title,action,detail,extra={}) {const it=item(p,title);if(action!==null)it[1]=action;if(detail!==null)it[3].d=detail;Object.assign(it[3],{revision:'V2'},extra);return it;}
function add(p,id,title,action,detail,extra={}){phase(p).items.push([title,action,'chk',{id,revision:'V2',d:detail,...extra}]);}
function tableReplace(from,to){let found=false;for(const p of DATA)for(const raw of p.items)if(raw.tbl)for(const row of raw.tbl)if(row[0]===from){row[1]=to;found=true}if(!found)throw Error('Missing table '+from);}

patch('n1','Fenix Variant','A320 CEO · CFM56-5B · SHARKLETS','V2 is prepared for the aircraft chosen for your world tour. Confirm the installed Fenix variant, livery and payload against the EFB. Airline fleet totals from V1 are not a setup requirement.',{s:'FENIX',w:'',ref:'scope'});
phase('n1').items.find(i=>i.sub==='SIM SETUP — EUROWINGS').sub='SIM SETUP — YOUR WORLD TOUR';
patch('n1','BAT Voltage (BAT pb OFF)','> 25.5 V',null,{ref:'tap',status:'secondary'});
patch('n2','EFB Mass & Balance','FINAL LOADSHEET / LOAD','Load the planned payload and fuel in the Fenix EFB. Use the final loadsheet: MACZFW is ZFWCG; MACTOW is takeoff CG. Check that the aircraft has finished loading. Never substitute a default CG when the actual value is missing.',{ref:'fenix-acars',s:'FENIX'});
patch('n5','FCU — Initial CLB ALT','SET {{clearedAlt}}','Set the initial altitude or flight level from the applicable departure clearance and chart. This is independent of PERF thrust-reduction and acceleration altitudes. Enter the reference explicitly, e.g. 5000 ft QNH or FL070.',{ref:'v2-logic',s:'V2'});
patch('n8','PERF TO — THR RED / ACC','{{thr}} / {{acc}} ft QNH','Use the planned departure/noise-abatement procedure and the applicable performance data. These fields are the QNH-referenced altitudes entered in PERF, not a height above the aerodrome. If a chart supplies AAL heights, account for aerodrome elevation. Do not use a universal 1000/3000-ft default.',{ref:'v2-logic',s:'V2'});
patch('n8','PERF TO — Flap / THS','CONF {{toConf}} / {{trim}}',null);
add('n8','n8.eo-acc','PERF TO — ENG OUT ACC','{{eoAcc}} ft QNH','Record the flight-specific engine-out acceleration altitude and brief the maximum permissible acceleration altitude and thrust time limit from the applicable data.',{ref:'eo-review',s:'V2'});
const eoText='Continue the takeoff and establish a safe flight path. The source briefing postpones ECAM actions until at least 400 ft AGL, apart from gear retraction and silencing warnings. Brief the engine-securing actions, planned and maximum engine-out acceleration altitudes, applicable thrust time limit and routing together. Do not let the phrase “only after secured” override the maximum acceleration altitude. Apply the aircraft-appropriate ECAM/QRH sequence; the legacy FSLabs chart alone is not a validated Fenix procedure.';
patch('n9','Failure after V1','CONTINUE · BRIEF EO PLAN',eoText,{ref:'eo-review',w:'Engine-out sources differ. Use the same flight-specific procedure and altitude limits for this briefing and the Special Procedure card.'});
patch('s2','Acceleration Height','PLANNED / MAX EO ALT',eoText,{ref:'eo-review',w:'Resolve engine securing, maximum acceleration altitude and thrust time limits together. No fixed 1500-ft default and no unlimited wait for “secured”.'});
patch('s2','Thrust','CONSIDER TOGA','Check the applicable thrust rating and time limitation for the selected aircraft and failure case. The legacy ten-minute statement is from an engine-out training sheet and is not a general all-engines TOGA limit.',{ref:'eo-review',w:'Confirm the applicable limit before using this card for engine-out training.'});
phase('s2').review='Engine-out: source conflict remains. This card organizes the briefing; aircraft-specific ECAM/QRH conditions and performance must be confirmed before training.';
phase('s2').diagram='engine-out';
patch('s3','E/O Recovery','ESTABLISH SAFE FLIGHT PATH','This is an alternative quick-return configuration strategy at acceleration altitude. Do not first clean up to CONF 0 and then follow a sequence that assumes CONF 1.',{ref:'eo-review'});
phase('s3').review='Training technique from a legacy simulator sheet. Choose either the normal clean-up or this return strategy in the briefing; confirm its applicability.';
phase('s3').diagram='quick-return';
phase('n13').note='Use a taxi speed appropriate to the surface, visibility, turn radius, traffic and local/operator limits. The V1 combination “20 kt straight” and “accelerate to 30 kt” has been removed. Brake techniques must remain within the chosen taxi limit.';
patch('n16','Transition Altitude','AT {{ta}} ft QNH — SET STD','Set STD at the applicable transition altitude and cross-check both sides. Pressure altitude, Mode S selected altitude and barometric pressure setting are distinct data. The former “transponder based on last QNH” sentence was too broad.',{ref:'eurocontrol'});
phase('n16').note='Perform the after-takeoff flow, monitor the FMA and review the E/WD memo. Checklist structure varies by operator and document revision; the supplied 2016 QRH still contains After Takeoff / Climb. Use one consistent checklist standard for this simulator profile.';
patch('n17','E — Enroute Alternates','DIVERSION / ETP','Review suitable alternates, terrain, weather, fuel and the applicable engine-out performance. A fixed 350 NM does not define single-engine range without fuel, time, mass and flight conditions.',{ref:'v2-logic'});
patch('n17','F — Fuel','WAYPOINT / ≤ 30 MIN','At the same waypoint compare actual FOB and fuel used with the OFP/SimBrief plan. Check FOB + total fuel used against the initial fuel quantity, using the applicable tolerances. Review destination/alternate predictions separately. A future-waypoint prediction must not be compared directly with the present tank quantity.',{ref:'airbus-fuel'});
phase('n17').diagram='fuel';
patch('n20','APPR pb','WHEN CLEARED / INTERCEPT','For the ILS approach, confirm clearance and an appropriate intercept path before arming. Monitor expected FMA modes.',{ref:'tap'});
patch('n20','AP','AS BRIEFED','Select the appropriate autopilot configuration for the planned ILS category, landing mode and aircraft capability. For autoland, complete the applicable dual-AP checks and limitations.',{ref:'tap'});
patch('n20','LOC / GS','ARMED / CAPTURED','Monitor LOC and G/S armed and capture modes and the intended intercept from below. G/S interception from above is a separate supplementary case; do not use an unbriefed V/S recipe during normal capture.',{ref:'tap'});
patch('n20','GS *','SET {{gaAlt}}','After confirmed glide-slope capture, set and cross-check the charted/cleared missed-approach altitude. Use the correct altitude/flight-level reference.',{ref:'v2-logic'});
patch('n20','When Gear Down','FLAPS 3','Confirm down-and-locked indications for nose, left main and right main gear. On the WHEEL page this means at least one green triangle for each gear, with the applicable landing-gear memo. Check the brake triple indicator for residual pressure.',{ref:'airbus-gear'});
patch('n20','When Flaps 3','FLAPS FULL — TARGET SPD',null,{condition:{landing:'FULL'}});
add('n20','n20.conf3-speed','Landing CONF 3','CONFIRM · VAPP {{vapp}}','Confirm the selected landing configuration and applicable VAPP from landing performance. Retain CONF 3 for the planned CONF 3 landing.',{condition:{landing:'3'},ref:'v2-logic'});
const conf3Item=phase('n20').items.pop();phase('n20').items.splice(phase('n20').items.indexOf(item('n20','Landing Memo')),0,conf3Item);
item('n16','F Speed')[3].condition={takeoff:['2','3']};
patch('n20','AP Disconnect','AT BRIEFED {{apOff}}','Set the planned manual-disconnect height against the actual approach mode, aircraft limitation, chart and chosen simulator SOP. The old blanket “160 ft for every non-autoland approach” has been removed. Autoland is a separate case.',{ref:'applicability',w:'',condition:{landingMode:'manual'}});
patch('s5','Transponder','7700 — CONSIDER','The supplied QRH uses “consider”; squawk 7700 unless otherwise specified by ATC. Preserve the condition instead of turning it into an unconditional action.',{ref:'qrh-emer'});
phase('s5').diagram='emergency-descent';
phase('s6').diagram='circling';phase('s7').diagram='visual';phase('s8').diagram='touch-go';
const tg=phase('s8').items;const a=tg.indexOf(item('s8','At 500 ft AGL'));const b=tg.indexOf(item('s8','At 1000 ft AGL'));[tg[a],tg[b]]=[tg[b],tg[a]];
phase('s8').review='Legacy simulator training pattern. In V2 the 500-ft turn now precedes the 1000-ft action, matching the diagram. Performance and local circuit rules still need a suitable training briefing.';
phase('s9').review='Performance applicability unresolved: the embedded overweight table is unidentified. The supplied March 2016 QRH is for EC-MLE, A320-232 (IAE), and has different figures. Neither table is established as the correct CFM Sharklet table.';
patch('s9','Max Landing Weight','USE APPLICABLE PERFORMANCE','Use performance for the exact aircraft, engine, configuration and conditions. The original table is retained only in the learning archive. Do not substitute the separate Vueling A320-232 QRH table.',{ref:'overweight-review',w:phase('s9').review});
phase('s9').items.find(i=>i.img==='owlanding').archiveOnly=true;
phase('s9').note='Overweight landing requires aircraft-specific performance and the applicable abnormal procedure. This source-derived card is a study reference until those requirements are confirmed.';

for(const p of DATA)for(const raw of p.items){if(Array.isArray(raw)){
  const o=raw[3]; if(raw[0]==='Idle — IAE V2500')o.condition={engine:'IAE'};
  if(raw[0]==='Idle — CFM56'||/^N2 (16|22|50)%$/.test(raw[0]))o.condition={engine:'CFM'};
  if(p.id==='c4')raw[1]=raw[1].replaceAll('{{qnh}}','{{qnhArr}}');
  else raw[1]=raw[1].replaceAll('{{qnh}}','{{qnhDep}}');
  if(p.id==='n5'&&(raw[0].includes('Baro Ref')||raw[0].includes('ISIS')))raw[1]='SET {{qnhDep}} hPa';
  if(p.id==='n19'&&raw[0]==='Transition Level')raw[1]='SET {{qnhArr}} hPa';
  if(p.id==='c5'&&raw[0]==='GO AROUND ALT')raw[1]='{{gaAlt}} SET';
  if(p.id==='c3'&&raw[0]==='FLAP SETTING')raw[1]='CONF {{toConf}} (BOTH)';
  if(raw[0]==='LANDING C/L')o.link='c5';
  if(raw[0]==='APPROACH C/L')o.link='c4';
  if(raw[0]==='BEFORE START C/L')o.link='c1';
  if(raw[0]==='AFTER START C/L')o.link='c2';
  if(raw[0]==='TAXI C/L'||raw[0]==='LINE-UP C/L'){o.link='c3';o.d=(o.d||'')+' Use Before Takeoff, '+(raw[0]==='LINE-UP C/L'?'AT LINE-UP section.':'before the AT LINE-UP section.');}
}}
let wind=null;for(const it of phase('n15').items){if(it.sub){wind=it.sub.startsWith('X-WIND <')?'normal':it.sub.startsWith('X-WIND >')?'strong':null;if(wind==='normal')it.sub='STANDARD WIND TECHNIQUE — selected in flight profile';if(wind==='strong')it.sub='STRONG CROSSWIND / TAILWIND TECHNIQUE — selected in flight profile';if(wind)it.condition={wind};}else if(Array.isArray(it)&&wind)it[3].condition={wind};}
const strongStart=phase('n15').items.findIndex(it=>Array.isArray(it)&&it[3].condition?.wind==='strong');
phase('n15').items.splice(strongStart,0,
 ['Thrust — stabilise','N1 50%','act',{id:'n15.strong-stabilise',revision:'V2',condition:{wind:'strong'},ref:'tap',d:'Stabilise the engines before the subsequent increase in the selected wind-technique branch.'}],
 ['Brakes','RELEASE','act',{id:'n15.strong-brakes',revision:'V2',condition:{wind:'strong'},ref:'v2-logic',d:'Retained in both alternative takeoff branches so branch filtering cannot remove the brake-release step.'}]);
phase('n15').note='Select the wind-technique branch in your flight profile using the applicable SOP and conditions. Only the selected branch counts toward progress. Captain keeps a hand on the thrust levers until V1.';
item('n15','Thrust')[1]='N1 50% — STABILISE';
item('n11','Idle — CFM56')[3].d='Approximate ISA sea-level CFM56 values for recognition, not hard limits: N1 20%, N2 60%, EGT 400 °C, FF 300 kg/h. Confirm normal indications for the actual conditions.';
patch('n3','ENG Page — Oil Quantity','CHECK CFM QUANTITY','Use the applicable CFM56-5B oil-quantity requirement, flight duration and conditions. V1 cited >9.5 qt + 0.5 qt/h from a secondary source; its exact airframe applicability has not been independently established.',{ref:'applicability',status:'secondary'});
tableReplace('Straight taxiway','Adapt to conditions and chosen local/operator limit');
tableReplace('Technique','Brake within the selected taxi limit; no 20/30-kt contradiction');
tableReplace('Thrust reduction altitude','Flight-specific PERF altitude, ft QNH; no universal default');
tableReplace('Acceleration altitude','Flight-specific PERF altitude, ft QNH; separate from FCU clearance');
tableReplace('Max TOGA thrust duration','Aircraft / rating / failure dependent — verify applicable limit');
tableReplace('AP off — non-autoland (limitation)','Brief for the selected approach mode and applicable limitation');
tableReplace('Min AP height, FINAL APP / V/S / FPA','Verify the limit for the actual guidance mode and aircraft standard');
for(const p of DATA)for(const it of p.items)if(it.tbl)for(const row of it.tbl){if(/single.engine.*(range|distance)/i.test(row[0]))row[1]='No fixed 350-NM range; use flight-specific performance';if(/minimum oil|oil quantity/i.test(row[0]))row[1]='Use the applicable engine-specific requirement';}
phase('r1').note='Legacy reference values retain their source context. V2 has corrected the identified conflicts; remaining numerical limits are not a complete validation for every Fenix aircraft standard.';
phase('r4').items=phase('r4').items.filter(i=>i.img);
phase('r4').n='Sources & V2 Review';phase('r4').note='Exact references, review scope and known applicability gaps. Source quality and aircraft applicability are separate from whether a line changed in V2.';
phase('r4').sourceCatalog=true;
phase('r5').note=(phase('r5').note||'')+' Airline/network facts are retained from V1 as background and were not refreshed by this technical review.';

const refs={
 'scope':{title:'V2 scope',detail:'Personal simulator profile: Fenix A320 CEO, CFM56-5B, Sharklets. No claim to represent a specific airline SOP.'},
 'v2-logic':{title:'V2 correction',detail:'Data separation or internal-consistency correction. No new universal aircraft limit is introduced.'},
 'tap':{title:'TheAirlinePilots — A320 Normal Procedures',url:'https://www.theairlinepilots.com/forumarchive/a320/a320-normal-procedures.pdf',detail:'V1 cites 15 JUL 2024. The retrieved online revision is 20 MAR 2026. The exact 2024 source is still unavailable; this is a secondary, operator-influenced compilation.'},
 'fenix-acars':{title:'Fenix — ACARS Overview',url:'https://support.fenixsim.com/hc/en-us/articles/12374778266127-ACARS-Overview',detail:'MACZFW is ZFWCG; MACTOW is takeoff CG. Reviewed 22 SEP 2026.'},
 'airbus-fuel':{title:'Airbus — Fuel Monitoring on A320 Family Aircraft',url:'https://safetyfirst.airbus.com/fuel-monitoring-on-a320-family-aircraft/?airbus-iframe=true&airbus-post=2147',detail:'FOB + fuel used versus initial fuel; actual versus planned fuel at the same waypoint. Also supported by local SOP/6_A320-Cruise.pdf, PDF p.7.'},
 'airbus-gear':{title:'Airbus Safety First 10 — Landing Gear Indications',url:'https://safetyfirst.airbus.com/app/themes/mh_newsdesk/pdf/safety_first_10.pdf',detail:'AUG 2010, printed p.17: at least one green triangle for EACH gear strut on WHEEL page.'},
 'eurocontrol':{title:'EUROCONTROL — DAP/ADD Handbook',url:'https://www.eurocontrol.int/publication/dap-add-handbook',detail:'25 NOV 2024. Distinguishes pressure altitude, selected altitude and barometric pressure setting.'},
 'eo-review':{title:'Engine-out source comparison',file:'M:/Downloads/docs/A320/FSLabs A320 Engine Failure.pdf',detail:'One-page FSLabs-only training sheet compared with V1 briefing. Engine-securing condition and maximum acceleration altitude conflict remains pending aircraft-specific reconciliation. V2 removes the unconditional contradiction.'},
 'overweight-review':{title:'Overweight table applicability',file:'M:/Downloads/docs/A320/Overweight Landing.pdf',detail:'Unidentified one-page table differs from 313562828-QRH-A320.pdf, PDF p.114 / 80.07A (22 MAR 2016), EC-MLE A320-232. No validated CFM Sharklet performance table supplied.'},
 'qrh-emer':{title:'QRH EC-MLE — Emergency Descent',file:'M:/Downloads/docs/A320/313562828-QRH-A320.pdf',detail:'22 MAR 2016; A320-232, MSN 7109; PDF p.112 / 80.05A. Confirms conditional squawk 7700 wording. Not a universal CFM performance authority.'},
 'applicability':{title:'Aircraft applicability not fully established',detail:'Retain as study context. A secondary source or a different simulator/engine standard does not establish an exact limit for your CFM Sharklet aircraft.'},
 'go-around':{title:'Airbus — Flying a Go-Around: Managing Energy',url:'https://safetyfirst.airbus.com/flying-a-go-around-managing-energy/?airbus-iframe=true&airbus-post=2161',detail:'TOGA selection and energy-management conditions; supports the distinction between go-around and discontinued approach.'},
 'touch-go':{title:'Touch-and-go training sheet',file:'M:/Downloads/docs/A320/FSLabs A320 Touch and Go.pdf',detail:'One-page simulator diagram. V2 corrects the transcribed 500/1000-ft order; no new performance validation.'}
};
phase('s4').diagram='go-around';phase('s4').reference='go-around';
let cancel=false;for(const it of phase('s4').items){if(it.sub?.startsWith('DISCONTINUED'))cancel=true;if(Array.isArray(it))it[3].condition={goAround:cancel?'discontinued':'full'};}
const inventory=JSON.parse(fs.readFileSync(path.join(__dirname,'source-inventory.json'),'utf8'));
IMAGES.visappV2='data:image/svg+xml;base64,'+fs.readFileSync(path.join(__dirname,'visual-approach-v2.svg')).toString('base64');

const plates=JSON.parse(fs.readFileSync(path.join(__dirname,'plates.json'),'utf8'));
for(const [key,plate] of Object.entries(plates))if(plate.file){
 plate.image='plate-'+key;IMAGES[plate.image]='data:image/svg+xml;base64,'+fs.readFileSync(path.resolve(__dirname,'plates',plate.file)).toString('base64');
}
phase('n4').diagram='cockpit';phase('r4').diagram='cockpit';
phase('n20').diagram='approach-techniques';phase('r2').diagram='flap-logic';phase('s9').diagram='overweight';
phase('n20').items.unshift({img:'apptypes',cap:'V1 approach techniques — original Blackbox711 sheet; see updated side-by-side profiles and Airbus reference above.'});
phase('s5').note='Memory items first, followed by the applicable ECAM/QRH procedure. The old descent-rate, time and distance figures are source examples, not guaranteed descent performance.';
phase('s2').review='Profilgrafik überarbeitet. Engine securing / MAX EO ACC / Schubzeitlimit bleiben flugzeugspezifisch abzugleichen.';
phase('s9').review='Lesbare Quellentabelle ergänzt. Ihre Eignung für den Fenix CFM-Sharklet ist weiterhin nicht belegt.';
refs['airbus-approach']={title:'Airbus — Anflugtechniken und Stabilisierung',url:'https://safetyfirst.airbus.com/control-your-speed-during-descent-approach-and-landing/?airbus-iframe=true&airbus-post=2130',detail:'Vergleich von decelerated und early stabilized ohne CDA; Zeitpunkt von VAPP und Landekonfiguration am Stabilisierungspunkt beziehungsweise FDP. Grafiken 18–19. Abgleich am 22 SEP 2026.'};
refs['airbus-climb']={title:'Airbus — Control your Speed During Climb',url:'https://safetyfirst.airbus.com/control-your-speed-during-climb/?airbus-iframe=true&airbus-post=2145',detail:'F-/S-Speed und Green Dot im Zusammenhang mit Konfiguration und Steigleistung. Liefert keine vollständige Lösung des lokalen Engine-securing-/MAX-EO-ACC-Konflikts.'};
refs['airbus-fire']={title:'Airbus — Engine Fire Procedure',url:'https://safetyfirst.airbus.com/do-not-wait-to-apply-the-engine-fire-procedure/?airbus-iframe=true&airbus-post=2080',detail:'Engine-fire-Prozedur ohne vermeidbare Verzögerung anwenden. Keine Gleichsetzung von Engine Failure und Engine Fire; kein pauschales Wartegebot aus der Grafik ableiten.'};
const legacyOverweight=[
['< 10',85,84,83,81,77,71,66],
[15,85,83,83,81,77,70,64],
[20,85,83,83,81,75,67,61],
[25,85,83,83,79,72,64,58],
[30,84,83,81,77,69,null,null],
[35,84,83,79,73,66,null,null],
[40,84,81,73,69,null,null,null],
[45,82,76,70,null,null,null,null],
[50,78,72,null,null,null,null,null]
];

const payload={plates,legacyOverweight,version:2,reviewDate:'2026-09-22',DATA,IMAGES,MAP,refs,inventory:inventory.map(r=>({name:r.name,path:r.source,pages:r.pages,textExtractable:r.chars>0}))};
const out=__dirname;fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'data-v2.json'),JSON.stringify(payload,null,2));
let html=fs.readFileSync(path.join(__dirname,'v2-template.html'),'utf8');
let hero='';const heroPath=path.join(out,'cockpit-v2.png');if(fs.existsSync(heroPath))hero='data:image/png;base64,'+fs.readFileSync(heroPath).toString('base64');
html=html.replace('/*__PAYLOAD__*/','const PAYLOAD = '+JSON.stringify(payload).replace(/</g,'\\u003c')+';').replace('__HERO__',hero);
fs.writeFileSync(path.resolve(out,'../Fenix_A320_Flow_V2.html'),html);
console.log(JSON.stringify({output:path.resolve(out,'../Fenix_A320_Flow_V2.html'),phases:DATA.length,steps:DATA.reduce((n,p)=>n+p.items.filter(Array.isArray).length,0),sources:inventory.length,hero:!!hero}));
