const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname,read=name=>fs.readFileSync(path.join(root,name),'utf8');
const app=read('app-check.js'),html=read('../outputs/Volanta-Worldtour-EDLV.html');
const D=JSON.parse(read('tour-data.json')),X=JSON.parse(read('excursions.json'));
const progressKey='volanta-worldtour-edlv-2026-09-v1';
const archive=entries=>({schemaVersion:1,tour:'EDLV-2026-09-v1',entries});
const fixture=[{legId:'1',from:D.legs[0].from,to:D.legs[0].to,status:'final',updatedAt:'2026-09-22',flightDate:null,actualScenery:{departure:{product:'Departure actually used',version:null},arrival:{product:'Arrival actually used',version:null},landscape:null},volanta:'open'}];
function boot(entries=fixture,progress={done:[1,2],xDone:[X.excursions[0].legs[0].id],retiredXDone:['X-TV-1']},existingMemory){
 const nodes=new Map(),memory=existingMemory||new Map([[progressKey,JSON.stringify(progress)],['another-app','keep me']]),control={denyWrite:false};
 const node=s=>{if(!nodes.has(s))nodes.set(s,{innerHTML:'',textContent:'',value:({'#countryFilter':'all','#filter':'all','#scope':'chapter','#debriefFilter':'pending'})[s]||'',style:{},clientWidth:0,clientHeight:0,events:{},addEventListener(name,fn){this.events[name]=fn},scrollIntoView(){},showModal(){this.open=true},close(){this.open=false},classList:{contains(){return false},toggle(){}}});return nodes.get(s)};
 for(const [id,file] of [['tourData','tour-data.json'],['worldData','world.json'],['briefingData','briefings.json'],['excursionData','excursions.json'],['sceneryData','scenery-guide.json']])node('#'+id).textContent=read(file);
 node('#debriefData').textContent=JSON.stringify(archive(entries));
 const c={document:{getElementById:id=>node('#'+id),querySelector:node,querySelectorAll:()=>[],addEventListener(){}},localStorage:{getItem:k=>memory.get(k),setItem(k,v){if(control.denyWrite)throw Error('Storage blocked');memory.set(k,v)}},ResizeObserver:class{observe(){}},setTimeout(){},clearTimeout(){},window:{scrollTo(){},showDirectoryPicker:async()=>{throw {name:'AbortError'}}},TextDecoder,Uint8Array,crypto:{randomUUID:()=> 'test-uuid'},requestAnimationFrame(){},matchMedia(){return {matches:true}}};
 vm.createContext(c);vm.runInContext(read('d3.min.js'),c);vm.runInContext(read('topojson.min.js'),c);vm.runInContext(app,c);
 return {node,c,memory,control,run:code=>vm.runInContext(code,c)};
}
function embeddedEntries(text){return JSON.parse(text.match(/<script id="debriefData" type="application\/json">([\s\S]*?)<\/script>/)[1]).entries}
function project(entries=fixture,options={}){
 const embedded=html.replace(/(<script id="debriefData" type="application\/json">)[\s\S]*?(<\/script>)/,(_,open,close)=>open+JSON.stringify(archive(entries))+close);
 const files=new Map(Object.entries({'work/build_html.py':'project marker','debriefings.json':JSON.stringify(archive(entries)),'Volanta-Worldtour-EDLV.html':embedded,'outputs/Volanta-Worldtour-EDLV.html':embedded,'outputs/Debriefings.md':'Existing journal with reported flights'}).map(([name,value])=>[name,Buffer.from(value)]));
 const original=new Map([...files].map(([name,value])=>[name,Buffer.from(value)])),directories=new Set(['','work','outputs']),writes=[];
 let failed=false;
 const directory=prefix=>({
  async getDirectoryHandle(name,{create=false}={}){const key=prefix?prefix+'/'+name:name;if(!directories.has(key)){if(!create)throw Error('Missing directory '+key);directories.add(key)}return directory(key)},
  async getFileHandle(name,{create=false}={}){
   const key=prefix?prefix+'/'+name:name;if(!files.has(key)){if(!create)throw Error('Missing file '+key);files.set(key,Buffer.alloc(0))}
   return {
    async getFile(){const content=Buffer.from(files.get(key));return {arrayBuffer:async()=>content.buffer.slice(content.byteOffset,content.byteOffset+content.byteLength)}},
    async createWritable(){let pending;return {
     async write(contents){pending=Buffer.from(contents)},
     async close(){
      if(options.failBackup&&key.startsWith('backups/'))throw Error('Backup permission denied');
      files.set(key,pending);writes.push(key);options.afterWrite?.(key,files);
      if(options.failWrite===key&&!failed){failed=true;throw Error('Simulated partial commit failure')}
     },async abort(){}
    }}
   };
  }
 });
 return {directory:directory(''),files,original,writes};
}
function unchanged(p){for(const [name,contents] of p.original)assert.deepEqual(p.files.get(name),contents,name+' changed unexpectedly')}
async function confirmDebriefs(b,p){b.c.window.showDirectoryPicker=async()=>p.directory;b.node('#resetDebriefsOpen').onclick();await b.node('#resetConfirm').onclick()}

(async()=>{
 const b=boot();let exported;
 b.c.download=(name,body)=>{exported={name,body}};
 b.node('#resetProgressOpen').onclick();assert(b.node('#resetDialog').open);assert(b.node('#resetDialogDescription').textContent.includes('2 A320-Häkchen'));
 b.node('#resetCancel').onclick();assert(!b.node('#resetDialog').open);assert.equal(b.run('state.done.size'),2);
 b.node('#resetProgressOpen').onclick();b.node('#resetBackup').onclick();
 const backup=JSON.parse(exported.body);assert.deepEqual(backup.done,[1,2]);assert.deepEqual(backup.retiredXDone,['X-TV-1']);
 await b.node('#resetConfirm').onclick();
 assert.equal(b.run('state.done.size+state.xDone.size+state.retiredXDone.size'),0);
 assert.equal(b.run('DB.entries.length'),1);assert.equal(b.memory.get('another-app'),'keep me');
 assert.deepEqual(JSON.parse(b.memory.get(progressKey)),{done:[],xDone:[],retiredXDone:[]});
 assert(b.node('#xProgress').textContent.startsWith('0 / 46'));assert(b.node('#retiredDetails').hidden);
 assert.equal(boot(fixture,{},b.memory).run('state.done.size+state.xDone.size'),0,'Reset must survive reload.');
 await b.node('#backupFile').onchange({target:{files:[{text:async()=>JSON.stringify(backup)}],value:'restore.json'}});
 assert.equal(b.run('state.done.size+state.xDone.size+state.retiredXDone.size'),4,'Downloaded progress backup must restore all three sets.');
 const blocked=boot();const before=blocked.memory.get(progressKey);blocked.control.denyWrite=true;
 blocked.node('#resetProgressOpen').onclick();await blocked.node('#resetConfirm').onclick();
 assert.equal(blocked.run('state.done.size'),2);assert.equal(blocked.memory.get(progressKey),before);
 assert(blocked.node('#resetDialogError').textContent.includes('nicht verändert'));
 const empty=boot([],{done:[],xDone:[]});empty.node('#resetProgressOpen').onclick();assert(empty.node('#resetConfirm').disabled);empty.node('#resetCancel').onclick();empty.node('#resetDebriefsOpen').onclick();assert(empty.node('#resetConfirm').disabled);

 const success=boot(),p=project();const progressBefore=success.memory.get(progressKey);
 await confirmDebriefs(success,p);
 assert(!success.node('#resetDialog').open,success.node('#resetDialogError').textContent);assert.equal(success.run('DB.entries.length'),0);assert.equal(success.run('debriefEntries.size'),0);
 assert.equal(success.memory.get(progressKey),progressBefore,'Debriefing reset must preserve progress.');
 assert.deepEqual(JSON.parse(p.files.get('debriefings.json')).entries,[]);
 for(const name of ['Volanta-Worldtour-EDLV.html','outputs/Volanta-Worldtour-EDLV.html'])assert.deepEqual(embeddedEntries(p.files.get(name).toString()),[]);
 assert(p.files.get('outputs/Debriefings.md').toString().includes('0 final dokumentiert · 0 mit offenen Angaben.'));
 assert(p.files.get('outputs/Debriefings.md').toString().includes('Noch kein Flug debrieft.'));
 assert(!p.files.get('outputs/Debriefings.md').toString().includes('Existing journal'));
 const backupFiles=p.writes.filter(name=>name.startsWith('backups/'));
 assert.equal(backupFiles.length,4);assert(p.writes.slice(0,4).every(name=>name.startsWith('backups/')),'All originals must be backed up before first project write.');
 for(const name of backupFiles){const source=name.split('/').slice(2).join('/');assert.deepEqual(p.files.get(name),p.original.get(source))}
 assert.equal(boot(embeddedEntries(p.files.get('Volanta-Worldtour-EDLV.html').toString()),{},success.memory).run('DB.entries.length'),0);

 const cancelled=boot();cancelled.node('#resetDebriefsOpen').onclick();await cancelled.node('#resetConfirm').onclick();assert.equal(cancelled.run('DB.entries.length'),1);assert(cancelled.node('#resetDialogError').textContent.includes('abgebrochen'));
 const unsupported=boot();delete unsupported.c.window.showDirectoryPicker;unsupported.node('#resetDebriefsOpen').onclick();assert(unsupported.node('#resetConfirm').disabled);assert.equal(unsupported.run('DB.entries.length'),1);
 const badArchive=project([]),stale=boot();await confirmDebriefs(stale,badArchive);unchanged(badArchive);assert.equal(badArchive.writes.length,0);assert(stale.node('#resetDialogError').textContent.includes('unterscheidet'));
 const badHtml=project();badHtml.files.set('outputs/Volanta-Worldtour-EDLV.html',Buffer.from(html));badHtml.original.set('outputs/Volanta-Worldtour-EDLV.html',Buffer.from(html));const mismatch=boot();await confirmDebriefs(mismatch,badHtml);unchanged(badHtml);assert.equal(badHtml.writes.length,0);
 const noBackup=project(fixture,{failBackup:true}),denied=boot();await confirmDebriefs(denied,noBackup);unchanged(noBackup);assert.equal(denied.run('DB.entries.length'),1);
 const partial=project(fixture,{failWrite:'outputs/Volanta-Worldtour-EDLV.html'}),recovered=boot();await confirmDebriefs(recovered,partial);unchanged(partial);assert.equal(recovered.run('DB.entries.length'),1);assert(recovered.node('#resetDialogError').textContent.includes('zurückgenommen'));
 let raced=false;const concurrent=project(fixture,{afterWrite(name,files){if(!raced&&name.startsWith('backups/')){raced=true;files.set('debriefings.json',Buffer.from('newer report written externally'))}}}),race=boot();await confirmDebriefs(race,concurrent);
 assert.equal(concurrent.files.get('debriefings.json').toString(),'newer report written externally');assert(concurrent.writes.every(name=>name.startsWith('backups/')));assert.equal(race.run('DB.entries.length'),1);
 const missing=project();missing.files.delete('work/build_html.py');const wrongFolder=boot();await confirmDebriefs(wrongFolder,missing);assert.equal(missing.writes.length,0);
 assert(!app.includes('localStorage.clear('));
 console.log('PASS: separate reset confirmations/cancel, progress backup/restore/reload, unrelated storage preserved, blocked storage, actual project archive/HTML/journal reset, byte-exact backups before writes, unsupported browser/cancel, wrong project/stale data, backup failure, partial-write rollback and concurrent-edit protection. File API tested with simulated handles; no real flight data reset.');
})().catch(error=>{console.error(error);process.exitCode=1});
