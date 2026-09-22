// The browser owns progress; the project owns reports. Never clear unrelated storage.
let resetMode=null,resetBusy=false;
const resetProjectFiles=['debriefings.json','Volanta-Worldtour-EDLV.html','outputs/Volanta-Worldtour-EDLV.html','outputs/Debriefings.md'];
const emptyDebriefJournal='# Worldtour · Debriefings\n\nAus den berichteten Flügen in `debriefings.json` erzeugt. Empfehlungen und Flug-Häkchen sind keine Nutzungsnachweise.\n\n0 final dokumentiert · 0 mit offenen Angaben.\n\nNoch kein Flug debrieft. Nach dem ersten Flug halten wir die tatsächlich verwendeten Szenerien und deine Eindrücke fest.\n';
function showResetResult(message){$('#resetResult').textContent=message;$('#debriefResetResult').textContent=message}
function openReset(mode){
 if(resetBusy||!['progress','debriefs'].includes(mode))return;
 resetMode=mode;$('#resetDialogError').textContent='';
 const progress=mode==='progress',count=progress?state.done.size+state.xDone.size+state.retiredXDone.size:DB.entries.length;
 $('#resetDialogTitle').textContent=progress?'Flugfortschritt zurücksetzen?':'Debriefings im Projekt leeren?';
 $('#resetDialogDescription').textContent=progress?`${state.done.size} A320-Häkchen, ${state.xDone.size} Ausflugs-Häkchen und ${state.retiredXDone.size} archivierte Häkchen werden in diesem Browser entfernt.\nDie Debriefings bleiben erhalten.`:`${count} Debriefings werden aus dem aktiven Projektarchiv, beiden HTML-Dateien und dem Tourtagebuch entfernt.\nDeine Flug-Häkchen bleiben erhalten. Wähle gleich den Ordner VolantaWorldTour, in dem debriefings.json und work liegen.`;
 $('#resetDialogBackupNote').textContent=progress?'Du kannst vorher eine JSON-Sicherung herunterladen und später unter „Planung & Quellen“ wieder laden.':'Vor Änderungen werden die vier betroffenen Dateien unter backups im gewählten Projekt gesichert. Die Sicherung enthält weiterhin die bisherigen Berichte.';
 $('#resetConfirm').textContent=progress?'Flugfortschritt jetzt zurücksetzen':'Projektordner wählen & leeren';
 $('#resetConfirm').disabled=count===0||!progress&&typeof window.showDirectoryPicker!=='function';
 $('#resetBackup').disabled=false;$('#resetCancel').disabled=false;
 if(count===0)$('#resetDialogError').textContent=progress?'Der Flugfortschritt ist bereits leer.':'Es sind noch keine Debriefings gespeichert.';
 else if(!progress&&typeof window.showDirectoryPicker!=='function')$('#resetDialogError').textContent='Dieser Browser bietet keinen schreibenden Ordnerzugriff. Öffne die HTML für diesen Reset in Microsoft Edge oder Google Chrome. Es wurde nichts verändert.';
 $('#resetDialog').showModal();
}
function refreshAfterReset(){
 renderProgress();renderXProgress();renderRows();renderDetail();renderCoverage();renderJourney();renderDebriefs();
}
function resetFlightProgress(){
 // Persist first: a blocked/quota-exhausted storage must not leave a false success in the UI.
 localStorage.setItem(storageKey,JSON.stringify({done:[],xDone:[],retiredXDone:[]}));
 state.done.clear();state.xDone.clear();state.retiredXDone.clear();storageOK=true;
 refreshAfterReset();
 return 'Flugfortschritt zurückgesetzt. Die Debriefings sind erhalten.';
}
function canonicalResetJson(value){
 if(value===null||typeof value!=='object')return JSON.stringify(value);
 if(Array.isArray(value))return '['+value.map(canonicalResetJson).join(',')+']';
 return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonicalResetJson(value[key])).join(',')+'}';
}
function clearedDebriefHtml(html,archive){
 const pattern=/<script id="debriefData" type="application\/json">([\s\S]*?)<\/script>/g;
 const matches=[...html.matchAll(pattern)];
 if(matches.length!==1||canonicalResetJson(JSON.parse(matches[0][1]))!==canonicalResetJson(archive))throw Error('Eine HTML-Datei enthält einen anderen Debriefing-Stand. Projekt neu bauen und die aktuelle HTML öffnen; nichts wurde geleert.');
 const json=JSON.stringify({...archive,entries:[]},null,2).replaceAll('<','\\u003c');
 return html.replace(pattern,()=>'<'+'script id="debriefData" type="application/json">'+json+'<'+'/script>');
}
async function resetFileHandle(directory,relative,create=false){
 const parts=relative.split('/');let parent=directory;
 for(const part of parts.slice(0,-1))parent=await parent.getDirectoryHandle(part,{create});
 return parent.getFileHandle(parts.at(-1),{create});
}
async function writeResetFile(handle,contents){
 const writable=await handle.createWritable();
 try{await writable.write(contents);await writable.close()}
 catch(error){try{await writable.abort()}catch{}throw error}
}
async function resetProjectDebriefs(directory){
 // Read and validate everything before creating backups or touching project content.
 await resetFileHandle(directory,'work/build_html.py');
 const files=[];
 for(const relative of resetProjectFiles){
  const handle=await resetFileHandle(directory,relative),file=await handle.getFile(),before=await file.arrayBuffer();
  files.push({relative,handle,before,text:new TextDecoder().decode(before)});
 }
 const archive=JSON.parse(files[0].text);
 if(archive.tour!==DB.tour||archive.schemaVersion!==DB.schemaVersion||canonicalResetJson(archive)!==canonicalResetJson(DB))throw Error('Das Projektarchiv unterscheidet sich von dieser geöffneten HTML. Projekt neu bauen und die aktuelle HTML öffnen; nichts wurde geleert.');
 const cleared={...archive,entries:[]};
 files[0].after=JSON.stringify(cleared,null,2)+'\n';
 files[1].after=clearedDebriefHtml(files[1].text,archive);
 files[2].after=clearedDebriefHtml(files[2].text,archive);
 files[3].after=emptyDebriefJournal;
 const backupName='debrief-reset-'+new Date().toISOString().replace(/[:.]/g,'-')+'-'+crypto.randomUUID();
 const backupPath='backups/'+backupName;
 const backups=await directory.getDirectoryHandle('backups',{create:true});
 const backup=await backups.getDirectoryHandle(backupName,{create:true});
 for(const file of files)await writeResetFile(await resetFileHandle(backup,file.relative,true),file.before);
 // A user may edit a report while the permission/backup dialogs are open.
 for(const file of files){
  const current=new Uint8Array(await (await file.handle.getFile()).arrayBuffer()),before=new Uint8Array(file.before);
  if(current.length!==before.length||current.some((byte,index)=>byte!==before[index]))throw Error('Eine Projektdatei wurde während der Sicherung geändert. Reset abgebrochen; keine Projektdatei überschrieben. Sicherung: '+backupPath);
 }
 const touched=[];
 try{
  for(const file of files){touched.push(file);await writeResetFile(file.handle,file.after)}
 }catch(error){
  const failed=[];
  for(const file of touched.reverse()){try{await writeResetFile(file.handle,file.before)}catch{failed.push(file.relative)}}
  throw Error(failed.length?'Reset unvollständig; Wiederherstellung fehlgeschlagen für '+failed.join(', ')+'. Originaldateien liegen in '+backupPath+'. Bitte aus dieser Sicherung wiederherstellen.':'Reset fehlgeschlagen. Alle begonnenen Änderungen wurden zurückgenommen. Sicherung: '+backupPath);
 }
 DB.entries.length=0;debriefEntries.clear();debriefSelected=null;
 $('#debriefData').textContent=JSON.stringify(cleared);
 refreshAfterReset();
 return 'Debriefings im Projekt und in beiden HTML-Dateien geleert. Flug-Häkchen erhalten. Sicherung: '+backupPath;
}
$('#debriefResetShortcut').onclick=()=>openReset('debriefs');
window.addEventListener?.('beforeunload',event=>{if(resetBusy){event.preventDefault();event.returnValue=''}});
$('#resetProgressOpen').onclick=()=>openReset('progress');
$('#resetDebriefsOpen').onclick=()=>openReset('debriefs');
$('#resetBackup').onclick=()=>{if(resetMode==='progress')$('#backupExport').onclick();else $('#debriefArchiveExport').onclick()};
$('#resetCancel').onclick=()=>{if(!resetBusy)$('#resetDialog').close()};
$('#resetDialog').addEventListener('cancel',event=>{if(resetBusy)event.preventDefault()});
$('#resetConfirm').onclick=async()=>{
 if(resetBusy||$('#resetConfirm').disabled)return;
 resetBusy=true;$('#resetConfirm').disabled=true;$('#resetCancel').disabled=true;$('#resetBackup').disabled=true;$('#resetDialogError').textContent='';
 try{
  let result;
  if(resetMode==='progress')result=resetFlightProgress();
  else{
   // Call the picker directly in the click handler, before other asynchronous work.
   const directory=await window.showDirectoryPicker({id:'volanta-worldtour-project',mode:'readwrite'});
   $('#resetDialogError').textContent='Sicherung und Reset laufen. Dieses Fenster bitte geöffnet lassen.';
   result=await resetProjectDebriefs(directory);
  }
  $('#resetDialog').close();showResetResult(result);toast('Reset abgeschlossen');
 }catch(error){
  if(error.name==='AbortError')$('#resetDialogError').textContent='Ordnerauswahl abgebrochen. Es wurde nichts verändert.';
  else if(resetMode==='progress')$('#resetDialogError').textContent='Der Browser konnte den leeren Fortschritt nicht speichern. Deine Häkchen wurden nicht verändert. Bitte zuerst eine Sicherung herunterladen.';
  else $('#resetDialogError').textContent=error.message||'Projektzugriff fehlgeschlagen. Bitte Ordner und Schreibfreigabe prüfen.';
 }finally{resetBusy=false;$('#resetConfirm').disabled=false;$('#resetCancel').disabled=false;$('#resetBackup').disabled=false}
};
$('#resetBrowserSupport').textContent=typeof window.showDirectoryPicker==='function'?'Beim Debriefing-Reset erteilst du dieser HTML Zugriff auf den ausgewählten Projektordner.':'Für das Leeren der Projektdateien diese HTML in Microsoft Edge oder Google Chrome öffnen. Der Flugfortschritt lässt sich auch hier zurücksetzen.';
