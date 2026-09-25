// User-facing search and keyboard regressions, using real app functions and isolated data.
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
class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.listeners = {}; this.attrs = {}; this.value = ''; }
  addEventListener(type, cb) { this.listeners[type] = cb; }
  setAttribute(key, value) { this.attrs[key] = value; }
  focus() { this.focused = true; element('document').activeElement = this; }
  getBoundingClientRect() { return { top: 100, height: 60 }; }
  remove() { this.removed = true; }
  closest(selector) {
    if (this.dataset.tab && (selector === '.tab' || selector.includes('[role="tab"]'))) return this;
    return null;
  }
}
const elements = new Map();
const element = s => { if (!elements.has(s)) elements.set(s, new Element()); return elements.get(s); };
const tabs = ['plan', 'hl', 'scn', 'cat', 'new', 'data'].map(tab => new Element({ tab }));
let planCheckboxes = [];
const ctx = vm.createContext({ input: data, console, setTimeout, clearTimeout,
  document: element('document'), window: element('window'),
  getComputedStyle: () => ({ position: 'sticky' }),
  one: element, many: s => s === '.tab' ? tabs : s === '#plan input[data-done]' ? planCheckboxes : [], moves: [], toggles: [] });
element('window').scrollY = 0;
element('window').scrollTo = options => { element('window').lastScroll = options; };
element('window').matchMedia = () => ({ matches: true });
const searchLine = src.split('\n').find(line => line.includes('const searchText ='));
vm.runInContext(`
const D=input, AP=D.airports, LEGS=D.legs, CH=D.chapters, XC=D.excursions;
const CATN=Object.fromEntries(D.cats.map(c=>[c.code,c.name]));
${src.slice(src.indexOf('  const CAT_SEARCH'), src.indexOf('  const legIdx'))}
const legIdx=new Map(LEGS.map((l,i)=>[l.id,i])), chIdx=new Map(CH.map((c,i)=>[c.id,i]));
const state={idx:0,tab:'plan',q:'',flt:'all',ch:'all',flown:new Map()};
const $=one, $$=many, cur=()=>LEGS[state.idx], cityOf=a=>a.c||a.n;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const rowHtml=l=>'<tr data-leg="'+l.id+'"></tr>';
function select(i){moves.push(i);state.idx=Math.max(0,Math.min(LEGS.length-1,i));updateNav();}
function toggleFlown(id){toggles.push(id);}
function saveLocal(){} function renderHL(){} function renderScn(){} function renderCat(){}
function renderNew(){} function renderData(){}
${searchLine}
${['passFilter','renderPlan','showTab','updateNav','reveal','stepLeg','openBriefing','findLeg','restorePlanFocus','wire'].map(fn).join('\n')}
function selectId(id){if(legIdx.has(id))select(legIdx.get(id));}
wire(); globalThis.ui={state,renderPlan,showTab,updateNav,restorePlanFocus,openBriefing};`, ctx);
const ui = ctx.ui;
const ids = () => [...element('#plan tbody').innerHTML.matchAll(/data-leg="([^"]+)"/g)].map(m => m[1]);
ui.state.q = 'eDlV EHAM'; ui.renderPlan();
assert.deepEqual(ids(), ['L001'], 'search terms combine across route fields');
ui.state.q = 'reykjavik'; ui.renderPlan();
assert(ids().includes('L012'), 'unaccented query finds Reykjavík');
ui.state.q = 'Deutschland'; ui.renderPlan();
assert(ids().includes('L001') && ids().includes('L388'), 'German country names find the same Volanta categories');
ui.state.q = 'h160'; ui.renderPlan(); assert.equal(ids().length, 34);
ui.state.ch = '01'; ui.renderPlan(); assert.deepEqual(ids(), ['X-GG-1','X-GG-2']);
ui.state.flt = 'done'; ui.renderPlan(); assert.equal(ids().length, 0);
assert(element('#plan tbody').innerHTML.includes('Keine passenden Legs'));
assert.equal(element('#clear-filters').hidden, false);
element('#clear-filters').listeners.click();
assert.equal(ids().length, 422); assert.equal(element('#clear-filters').hidden, true);
assert(element('#q').focused);
console.log('PASS search: combined terms, accents, H160, chapter/status combination, empty results, reset');

function key(target, key, extras = {}) {
  return { target, key, defaultPrevented:false, preventDefault(){this.defaultPrevented=true;}, ...extras };
}
ui.showTab('plan');
for (const [from, keyName, expected] of [[0,'ArrowRight','hl'],[1,'End','data'],[5,'Home','plan'],[0,'ArrowLeft','data']]) {
  const event = key(tabs[from], keyName);
  element('.tabs').listeners.keydown(event);
  element('document').listeners.keydown(event);
  assert.equal(ui.state.tab, expected);
  assert.equal(tabs.filter(t => t.tabIndex === 0).length, 1);
}
assert.equal(ctx.moves.length, 0, 'tab arrows must never select another flight');
element('document').listeners.keydown(key(tabs[5], 'g'));
assert.equal(ctx.toggles.length, 0, 'typing on a tab must not mark a flight');
const briefing = new Element();
briefing.closest = selector => selector === '.grid' ? briefing : null;
element('document').listeners.keydown(key(briefing, 'ArrowRight'));
assert.equal(ctx.moves.length, 1);
element('document').listeners.keydown(key(briefing, 'g', {repeat:true}));
assert.equal(ctx.toggles.length, 0, 'holding G must not repeatedly toggle progress');
console.log('PASS keyboard: tab arrows/Home/End, single tab stop, no accidental leg/progress changes, briefing arrows');

ui.state.idx = 0; ui.updateNav(); assert.equal(element('#prev').disabled, true);
assert.equal(element('#next').disabled, false); assert.equal(element('#resume').disabled, false);
ui.state.idx = data.legs.length - 1; ui.updateNav();
assert.equal(element('#next').disabled, true); assert.equal(element('#jump').value, 'L388');
for (const l of data.legs) ui.state.flown.set(l.id, '2026-09-24');
ui.updateNav(); assert.equal(element('#resume').disabled, true);
assert.equal(element('#resume').textContent, 'Alle Legs geflogen');
console.log('PASS navigation: first/last boundaries, current selection, complete-tour state');

const jump = element('#jump'), next = element('#next');
jump.focus(); jump.value = 'L010'; jump.listeners.change({target:jump});
assert.equal(element('document').activeElement, jump, 'changing the select must keep focus in the select');
next.focus(); next.listeners.click(); next.listeners.click();
assert.equal(data.legs[ui.state.idx].id, 'L012');
assert.equal(element('document').activeElement, next, 'repeated next-button activation keeps its focus');
ui.state.idx = data.legs.length - 2; next.listeners.click();
assert.equal(element('document').activeElement, jump, 'a newly disabled navigation button hands focus to the select');
ui.openBriefing('L010');
assert.equal(element('document').activeElement, element('.grid'), 'a table route jump focuses its briefing');

const briefButton = new Element();
briefButton.closest = selector => selector === '.grid' ? briefing : selector.split(', ').includes('button') ? briefButton : null;
const moveCount = ctx.moves.length;
element('document').listeners.keydown(key(briefButton, 'ArrowRight'));
assert.equal(ctx.moves.length, moveCount + 1, 'briefing buttons allow flight shortcuts');
const briefInput = new Element();
briefInput.closest = selector => selector === '.grid' ? briefing : selector.split(', ').includes('input') ? briefInput : null;
element('document').listeners.keydown(key(briefInput, 'ArrowRight'));
assert.equal(ctx.moves.length, moveCount + 1, 'editing a field must not navigate');
console.log('PASS focus: native select, repeated next, disabled boundary, route jump and briefing-button shortcuts');

const boxes = ['L001','L002','L003'].map(done => new Element({done}));
planCheckboxes = [boxes[0], boxes[2]];
ui.restorePlanFocus('L002', ['L001','L002','L003']);
assert.equal(element('document').activeElement, boxes[2], 'removed filtered row moves focus to the following result');
planCheckboxes = [boxes[0]];
ui.restorePlanFocus('L003', ['L001','L003']);
assert.equal(element('document').activeElement, boxes[0], 'last removed row moves focus to the previous result');
planCheckboxes = [];
ui.restorePlanFocus('L001', ['L001']);
assert.equal(element('document').activeElement, element('#clear-filters'), 'empty results focus the reset action, not the keyboard-opening search field');
console.log('PASS filtered-list focus: following row, previous row, empty result reset');
