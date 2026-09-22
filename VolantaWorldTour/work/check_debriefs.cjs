// Exercise the actual embedded app with independent browser progress and repo reports.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname,read=name=>fs.readFileSync(path.join(root,name),'utf8');
const app=read('app-check.js'),D=JSON.parse(read('tour-data.json')),X=JSON.parse(read('excursions.json'));
function boot(entries=[],progress={done:[],xDone:[]}){
 const nodes=new Map(),events=new Map(),memory=new Map([['volanta-worldtour-edlv-2026-09-v1',JSON.stringify(progress)]]);
 const node=s=>{if(!nodes.has(s))nodes.set(s,{innerHTML:'',textContent:'',value:({'#countryFilter':'all','#filter':'all','#scope':'chapter','#debriefFilter':'pending'})[s]||'',style:{},clientWidth:0,clientHeight:0,addEventListener(){},scrollIntoView(){},classList:{contains(){return false},toggle(){}}});return nodes.get(s)};
 for(const [id,file] of [['tourData','tour-data.json'],['worldData','world.json'],['briefingData','briefings.json'],['excursionData','excursions.json'],['sceneryData','scenery-guide.json']])node('#'+id).textContent=read(file);
 node('#debriefData').textContent=JSON.stringify({schemaVersion:1,tour:'EDLV-2026-09-v1',entries});
 const c={document:{getElementById:id=>node('#'+id),querySelector:node,querySelectorAll:()=>[],addEventListener(name,fn){if(!events.has(name))events.set(name,[]);events.get(name).push(fn)}},localStorage:{getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)},ResizeObserver:class{observe(){}},setTimeout(){},clearTimeout(){},window:{scrollTo(){}},requestAnimationFrame(){},matchMedia(){return {matches:true}}};
 vm.createContext(c);vm.runInContext(read('d3.min.js'),c);vm.runInContext(read('topojson.min.js'),c);vm.runInContext(app,c);
 return {node,memory,c,run:code=>vm.runInContext(code,c),click:dataset=>{for(const handler of events.get('click')||[])handler({target:{closest:selector=>selector===`[${dataset.attr}]`?{dataset:dataset.value}:null}})}};
}
const empty=boot();
assert(empty.node('#debriefDetail').innerHTML.includes('Bereit für deinen ersten Bericht'));
assert(empty.node('#debriefRows').innerHTML.includes('Keine offenen Debriefings'));
assert.equal((empty.node('#journeyRows').innerHTML.match(/data-debrief=/g)||[]).length,449);
assert(empty.node('#detail').innerHTML.includes('data-debrief="1"'));
empty.node('#debriefShowAll').onclick();
assert.equal((empty.node('#debriefRows').innerHTML.match(/data-debrief-select=/g)||[]).length,449);
empty.click({attr:'data-debrief',value:{debrief:'1'}});
assert(empty.node('#debriefDetail').innerHTML.includes('Tatsächlich verwendete Airports'));
assert(empty.node('#debriefDetail').innerHTML.includes('Noch nicht angegeben'));
assert(empty.node('#debriefPrompt').value.includes('Leg-ID 1'));
assert(!empty.node('#debriefPrompt').value.includes('Explicitly reported'));
empty.run('toggleDone(1)');
assert(empty.run('debriefStatus(allJourney()[0])')==='Debrief offen');
assert.equal(empty.run('DB.entries.length'),0,'Checkbox must never create a record.');
empty.node('#debriefFilter').value='pending';empty.node('#debriefFilter').onchange();
assert.equal((empty.node('#debriefRows').innerHTML.match(/data-debrief-select=/g)||[]).length,1);
const side=X.excursions.find(e=>e.profile==='H160').legs[0],otter=X.excursions.find(e=>e.profile==='DHC6').legs[0];
for(const leg of [side,otter]){empty.run(`openDebrief(${JSON.stringify(leg.id)})`);assert(empty.node('#debriefPrompt').value.includes(leg.from+' → '+leg.to));}
let download;empty.c.download=(name,body,type)=>{download={name,body,type}};
empty.node('#debriefTemplateExport').onclick();assert(download.name.includes(otter.id));assert(download.body.includes('Volanta-Wertung'));

const make=(l,status='final')=>({legId:String(l.id),from:l.from,to:l.to,status,updatedAt:'2026-09-22',flightDate:null,aircraft:null,actualScenery:{departure:{product:'Actually used departure <b>literal</b>',version:'1.0'},arrival:{product:'Actually used arrival',version:null},landscape:null},highlights:'Ridge <script>alert(1)</script>',volanta:'open'});
const draft=make(D.legs[1],'draft');draft.actualScenery.arrival.product=null;
const reports=boot([make(D.legs[0]),make(side),draft]);
reports.node('#debriefFilter').value='final';reports.node('#debriefFilter').onchange();
assert.equal((reports.node('#debriefRows').innerHTML.match(/data-debrief-select=/g)||[]).length,2);
reports.run('openDebrief(1)');
let detail=reports.node('#debriefDetail').innerHTML;
assert(detail.includes('Actually used departure &lt;b&gt;literal&lt;/b&gt;'));
assert(!detail.includes('<script>'));assert(detail.includes('&lt;script&gt;'));
assert(detail.includes('Noch nicht geprüft'));assert(detail.includes('Final dokumentiert'));
assert(detail.includes('Geplante Empfehlungen zum Vergleich'));
reports.run('toggleDone(1);toggleDone(1)');
assert.equal(reports.run('debriefStatus(allJourney()[0])'),'Final dokumentiert');
assert.equal(reports.run('DB.entries.length'),3,'Removing a checkbox must preserve reports.');
reports.node('#debriefSearch').value='Actually used arrival';reports.node('#debriefSearch').oninput();
assert.equal((reports.node('#debriefRows').innerHTML.match(/data-debrief-select=/g)||[]).length,2);
reports.node('#debriefSearch').value='';reports.node('#debriefFilter').value='pending';reports.node('#debriefFilter').onchange();
assert.equal((reports.node('#debriefRows').innerHTML.match(/data-debrief-select=/g)||[]).length,1);
reports.c.download=(name,body,type)=>{download={name,body,type}};
reports.node('#debriefArchiveExport').onclick();assert.equal(JSON.parse(download.body).entries.length,3);
reports.node('#journeyCsv').onclick();assert(download.body.includes('Tatsaechliche_Szenerie_Abflug'));assert(download.body.includes('Actually used arrival'));
(async()=>{
 await reports.node('#backupFile').onchange({target:{files:[{text:async()=>JSON.stringify({tour:'EDLV-2026-09-v1',total:403,done:[],xDone:[]})}],value:'legacy.json'}});
 assert.equal(reports.run('DB.entries.length'),3,'Legacy progress restore must not delete the archive.');
 assert.equal(reports.run('state.done.size'),0);
 assert.equal(JSON.parse(reports.memory.get('volanta-worldtour-edlv-2026-09-v1')).done.length,0);
 console.log('PASS: debriefing links for all 449 legs, A320/H160/Twin Otter selection, independent progress/archive, pending/final/search filters, unknown facts, HTML escaping, template/JSON/CSV exports and legacy backup restore. No visual browser test.');
})().catch(error=>{console.error(error);process.exitCode=1});
