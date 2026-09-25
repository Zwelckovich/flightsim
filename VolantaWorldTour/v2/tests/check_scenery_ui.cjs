// Rendering checks without a browser, real progress, or network access.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert/strict');
const base = path.resolve(__dirname, '..');
const src = fs.readFileSync(path.join(base, 'app.js'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(base, 'tour-v2.json'), 'utf8'));
function fn(name) {
  const start = src.search(new RegExp('  function ' + name + '\\('));
  const end = src.indexOf('\n  }', start);
  assert(start >= 0 && end > start, name);
  return src.slice(start, end + 4);
}
const panel = {};
const ctx = vm.createContext({ input: data, panel });
let code = `const D=input, AP=D.airports, LEGS=D.legs, CH=D.chapters, XC=D.excursions;
const legIdx=new Map(LEGS.map((l,i)=>[l.id,i]));
const CATN=Object.fromEntries(D.cats.map(c=>[c.code,c.name]));
const $=()=>panel;
const nf=n=>Number(n).toLocaleString('de-DE');
const cityOf=a=>a.c||a.n;
const fmtDate=iso=>String(iso||'').split('-').reverse().join('.');
`;
code += src.slice(src.indexOf('  const esc ='), src.indexOf('\n', src.indexOf('  const esc ='))) + '\n';
code += src.slice(src.indexOf('  const BADGE ='), src.indexOf('  function simbrief'));
code += ['installationNotes', 'simCheckNote', 'scnLine', 'aptCard', 'renderScn'].map(fn).join('\n');
code += '\nglobalThis.ui={installationNotes,simCheckNote,scnLine,aptCard,renderScn};';
vm.runInContext(code, ctx);
const fixture = { status: 'freeware', product: 'Fixture Airport', dev: 'Test', url: 'https://example.test/airport',
  dependencies: [{ product: 'Base & Library', url: 'https://example.test/base', required: true },
    { product: 'Optional objects', url: 'https://example.test/optional', required: false }],
  installNote: 'Terrain <patch> check', why: 'Fixture only' };
const notes = ctx.ui.installationNotes(fixture);
assert(notes.includes('Zusätzlich erforderlich')); assert(notes.includes('Optionaler Zusatz'));
assert(notes.includes('Base &amp; Library')); assert(notes.includes('Terrain &lt;patch&gt; check'));
assert(ctx.ui.scnLine(fixture).includes('https://example.test/base'));
const candidate = { status: 'candidate', product: 'Candidate fixture', dev: 'Test', why: 'Unconfirmed', url: 'https://example.test/candidate' };
const airport = data.airports.EDLV;
airport.sc.items.push(fixture, candidate);
airport.simCheck = { status: 'unconfirmed', note: 'Check runway exists', sources: ['https://example.test/source'] };
data.airports.FMZJ.simCheck = { status: 'unconfirmed', note: 'Fallback strip check', sources: ['https://example.test/fallback'] };
assert(ctx.ui.aptCard(airport, 'Abflug', false, data.legs[0]).includes('Sim-Prüfung offen'));
ctx.ui.renderScn();
const all = panel.innerHTML;
assert(all.includes('Freeware zum Prüfen')); assert(all.includes('Candidate fixture'));
assert(all.includes('Angebot recherchiert')); assert(!all.includes('Standard bewusst empfohlen'));
const checklist = all.slice(all.indexOf('Download-Checkliste pro Kapitel'));
assert(checklist.includes('https://example.test/base'));
assert(checklist.includes('Terrain &lt;patch&gt; check'));
assert(checklist.includes('Check runway exists'));
assert(checklist.includes('https://example.test/source'));
assert(checklist.includes('FMZJ · Ausweichziel'));
assert(checklist.includes('https://example.test/fallback'));
assert(!checklist.includes('https://example.test/candidate'));
console.log('PASS scenery rendering: dependency links, required/optional labels, escaped notes, candidates outside download checklist, visible simulator checks');
