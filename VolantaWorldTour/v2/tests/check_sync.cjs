// Real V2 functions with isolated storage and a controllable cloud transport.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const path = require('path');
const base = path.resolve(__dirname, '..');
const src = fs.readFileSync(process.argv[2] || path.join(base, 'app.js'), 'utf8');
const D = JSON.parse(fs.readFileSync(path.join(base, 'tour-v2.json'), 'utf8'));
function fn(name) {
  const start = src.search(new RegExp('  (?:async )?function ' + name + '\\('));
  const end = src.indexOf('\n  }', start);
  if (start < 0 || end < 0) throw Error(name);
  return src.slice(start, end + 4);
}
function setup() {
  const controls = {
    '#rs-progress': { checked: true }, '#rs-volanta': { checked: true },
    '#rs-debriefs': { checked: false }, '#sync': { lastElementChild: {} }
  };
  const clock = { now: Date.parse('2026-09-24T12:00:00Z') };
  const RealDate = Date;
  class TestDate extends RealDate { static now() { return clock.now; } }
  const ctx = vm.createContext({
    input: D, Date: TestDate, console, window: {},
    document: { querySelector: s => controls[s], querySelectorAll: () => [] },
    localStorage: { getItem: () => null, setItem: () => {} }, log: [], callbacks: {}, holdWrites: false, releases: [], failWrites: 0
  });
  const db = {
    doc(path) { return {
      onSnapshot(cb) { ctx.callbacks[path] = cb; },
      set: async data => ctx.log.push(['meta', data])
    }; },
    collection(name) { return {
      onSnapshot(cb) { ctx.callbacks[name] = cb; },
      doc(id) { return {
        set: async data => {
          ctx.log.push([name, id, data]);
          if (ctx.failWrites > 0) { ctx.failWrites--; throw new Error('simulated network failure'); }
          if (ctx.holdWrites) await new Promise(resolve => ctx.releases.push(resolve));
        }, delete: async () => {}
      }; },
      get: async () => ({ docs: [] })
    }; }
  };
  ctx.window.claude = { use: async () => db };
  let prefix = src.slice(0, src.indexOf('  // ---------- Prosa'));
  prefix = prefix.replace("JSON.parse($('#tour-data').textContent)", 'input')
    .replace(fn('toast'), '  function toast(s) { log.push(["toast", s]); }');
  prefix += '\nfunction refreshProgress(){} function renderData(){} function renderPlan(){} function renderProse(){} function renderTracks(){} function renderCat(){}\n';
  const m = src.indexOf('  const manualVol =');
  prefix += src.slice(m, src.indexOf('\n  };', m) + 5) + '\n';
  prefix += [fn('exportJson'), fn('doReset'), fn('applyImport')].join('\n');
  prefix += '\nglobalThis.review={state,mergeMarks,rebuildFlown,setFlown,setVol,volanta,doReset,exportJson,applyImport,initCloud};})();';
  vm.runInContext(prefix, ctx);
  return { ctx, r: ctx.review, clock, controls };
}
const docs = o => Object.entries(o).map(([id, d]) => ({ id, exists: true, data: () => d }));
const ids = a => [...a.r.state.flown.keys()].sort();
const flush = () => new Promise(resolve => setImmediate(resolve));
const mark = (on, t) => ({ on, t, at: '2026-09-24' });
async function connect(a, records = {}, epoch = {}) {
  await a.r.initCloud();
  a.ctx.callbacks['meta/reset']({ exists: true, data: () => epoch });
  if (a.ctx.callbacks.resets) a.ctx.callbacks.resets({ docs: [] });
  a.ctx.callbacks.flown({ docs: docs(records) });
  await flush();
}
(async () => {
  {
    const a = setup();
    a.r.setFlown('L001', true); a.r.setVol('DE', 'credited');
    const backup = JSON.parse(a.r.exportJson()); a.clock.now += 1000;
    await a.r.doReset(); assert.equal(a.r.state.flown.size, 0);
    a.r.applyImport(backup); assert.deepEqual(ids(a), ['L001']);
    assert(a.r.volanta().ok.has('DE')); console.log('PASS backup after reset');
  }
  {
    const a = setup();
    a.r.state.debriefs.set('L001', { volanta: 'credited', updatedAt: '2026-09-20' });
    assert.equal(a.r.volanta().ok.size, 2); await a.r.doReset();
    assert.equal(a.r.volanta().ok.size, 0);
    a.r.state.debriefs.set('L002', { volanta: 'credited', volantaAt: new Date(a.clock.now + 1000).toISOString() });
    assert.equal(a.r.volanta().ok.size, 2); console.log('PASS debrief confirmation after Volanta reset');
  }
  for (const epoch of [0, 5000]) {
    const a = setup(); await connect(a, { L005: { at: '2026-09-20' } }, { progress: epoch });
    assert.equal(a.r.state.flown.has('L005'), !epoch);
    console.log('PASS legacy cloud records, reset=' + epoch);
  }
  {
    const a = setup();
    for (const [id, t] of [['L001', 1000], ['L002', 2000], ['L003', 3000]]) a.r.state.marks.set(id, mark(true, t));
    await connect(a, { L001: mark(true, 1000), L003: mark(false, 5000) });
    assert.deepEqual(ids(a), ['L001', 'L002']);
    assert.deepEqual(a.ctx.log.filter(x => x[0] === 'flown').map(x => x[2].legId), ['L002']);
    console.log('PASS local/cloud merge, exactly one necessary upload');
  }
  {
    const a = setup();
    for (const [id, t] of [['L001', 1000], ['L002', 2000], ['L010', 6000]]) a.r.state.marks.set(id, mark(true, t));
    await connect(a, {}, { progress: 4000 });
    assert.deepEqual(ids(a), ['L010']);
    assert.deepEqual(a.ctx.log.filter(x => x[0] === 'flown').map(x => x[2].legId), ['L010']);
    console.log('PASS old second device after reset');
  }
  {
    const a = setup(), b = setup();
    await connect(a); await connect(b);
    b.clock.now = 1000; b.r.setFlown('L001', true); await flush();
    const olderWrite = b.ctx.log.find(x => x[0] === 'flown')[2];
    a.clock.now = 2000; a.r.setFlown('L001', false); await flush();
    const newerWrite = a.ctx.log.find(x => x[0] === 'flown')[2];
    // Unconditional document writes can arrive out of order across devices.
    for (const row of [newerWrite, olderWrite]) {
      for (const device of [a, b]) device.ctx.callbacks.flown({ docs: docs({ L001: row }) });
      await flush();
    }
    assert.equal(a.r.state.flown.has('L001'), false);
    assert.equal(b.r.state.flown.has('L001'), false);
    const repairs = [a, b].map(device => device.ctx.log.filter(x => x[0] === 'flown').at(-1)[2]);
    for (const repair of repairs) {
      assert.equal(repair.t, newerWrite.t);
      assert.equal(repair.on, false);
    }
    // Deliver corrective writes and their echoes. Equal values must not loop.
    const counts = [a.ctx.log.length, b.ctx.log.length];
    for (const device of [a, b]) device.ctx.callbacks.flown({ docs: docs({ L001: repairs[0] }) });
    await flush(); assert.deepEqual([a.ctx.log.length, b.ctx.log.length], counts);
    const c = setup(); await connect(c, { L001: repairs[0] });
    assert.equal(c.r.state.flown.has('L001'), false);
    console.log('PASS late older cloud write repaired; new device correct; no echo loop');
  }
  {
    const a = setup(); await connect(a);
    a.r.state.vstates.set('DE', { s: 'credited', t: 2000 });
    a.ctx.callbacks.volanta({ docs: docs({ DE: { s: 'credited', t: 2000 } }) });
    a.ctx.callbacks.volanta({ docs: docs({ DE: { s: 'not_credited', t: 1000 } }) });
    await flush();
    const repair = a.ctx.log.filter(x => x[0] === 'volanta').at(-1);
    assert.equal(repair[2].s, 'credited'); assert.equal(repair[2].t, 2000);
    console.log('PASS late older Volanta write repaired');
  }
  {
    const a = setup(); await connect(a, {}, { progress: 1000, volanta: 2000 });
    // A delayed reset from another device carries an older value for one field.
    a.ctx.callbacks['meta/reset']({ exists: true, data: () => ({ progress: 3000, volanta: 0 }) });
    await flush();
    const repair = a.ctx.log.filter(x => x[0] === 'resets').at(-1)[2];
    assert.equal(repair.progress, 3000); assert.equal(repair.volanta, 2000);
    console.log('PASS concurrent independent resets preserve both epochs');
  }
  {
    const a = setup(), b = setup();
    a.r.state.marks.set('L001', mark(true, 1000));
    b.r.state.marks.set('L001', mark(false, 1000));
    await connect(a, { L001: mark(false, 1000) });
    await connect(b, { L001: mark(true, 1000) });
    assert.equal(a.r.state.flown.has('L001'), false);
    assert.equal(b.r.state.flown.has('L001'), false);
    assert.equal(b.ctx.log.filter(x => x[0] === 'flown').at(-1)[2].on, false);
    console.log('PASS equal-time conflicting marks converge');
  }
  {
    const a = setup(); a.clock.now = 1000;
    a.r.state.marks.set('L001', mark(true, 5000));
    a.r.setFlown('L001', false); assert.equal(a.r.state.marks.get('L001').t, 5001);
    a.r.setFlown('L001', true); assert.equal(a.r.state.marks.get('L001').t, 5002);
    a.r.state.vstates.set('DE', { s: 'credited', t: 6000 });
    a.r.setVol('DE', 'not_credited'); assert.equal(a.r.state.vstates.get('DE').t, 6001);
    await a.r.doReset(); assert.equal(a.r.state.flown.size, 0);
    assert.equal(a.r.volanta().ok.size, 0); assert.equal(a.r.volanta().no.size, 0);
    console.log('PASS local edits and resets respect already observed future timestamps');
  }
  {
    const a = setup(), b = setup(); await connect(a); await connect(b);
    b.clock.now = 1000; b.r.setFlown('L001', true); b.r.setVol('DE', 'not_credited'); await flush();
    a.clock.now = 2000; a.r.setFlown('L001', false); a.r.setVol('DE', 'credited'); await flush();
    const cloud = { flown: {}, volanta: {} };
    // Newer writes arrive first. Device A closes before B's delayed writes arrive.
    for (const device of [a, b]) for (const [collection, id, value] of device.ctx.log) {
      if (cloud[collection]) cloud[collection][id] = value;
    }
    assert.equal(Object.keys(cloud.flown).length, 2);
    const c = setup(); await connect(c, cloud.flown);
    c.ctx.callbacks.volanta({ docs: docs(cloud.volanta) });
    assert.equal(c.r.state.flown.has('L001'), false);
    assert.equal(c.r.volanta().ok.has('DE'), true);
    // Snapshot order must not affect the winner.
    const d = setup(); await connect(d, Object.fromEntries(Object.entries(cloud.flown).reverse()));
    assert.equal(d.r.state.flown.has('L001'), false);
    console.log('PASS latest device closed: immutable progress/Volanta events retain the winner');
  }
  {
    const a = setup(); await connect(a);
    a.ctx.callbacks.resets({ docs: docs({ first: { progress: 5000, volanta: 0 }, second: { progress: 0, volanta: 6000 } }) });
    a.ctx.callbacks.flown({ docs: docs({ legacy: { legId: 'L001', on: true, t: 1000 } }) });
    a.ctx.callbacks.volanta({ docs: docs({ legacy: { code: 'DE', s: 'credited', t: 1000 } }) });
    assert.equal(a.r.state.flown.size, 0); assert.equal(a.r.volanta().ok.size, 0);
    assert.equal(a.r.state.epochs.progress, 5000); assert.equal(a.r.state.epochs.volanta, 6000);
    console.log('PASS reset events survive opposite arrival order and suppress legacy data');
  }
  {
    const a = setup(); a.ctx.holdWrites = true;
    a.r.state.marks.set('L001', mark(true, 1000)); a.r.state.marks.set('L002', mark(true, 2000));
    await connect(a);
    for (let i = 0; i < 4; i++) a.ctx.callbacks.flown({ docs: [] });
    a.ctx.holdWrites = false; a.ctx.releases.forEach(release => release());
    await flush(); await flush();
    assert.equal(a.ctx.log.filter(x => x[0] === 'flown').length, 2);
    console.log('PASS repeated partial snapshots do not duplicate pending uploads');
  }
  {
    const a = setup(); a.r.state.marks.set('L001', mark(true, 1000));
    await connect(a); // set() has resolved, but its document has not appeared in a snapshot yet.
    for (let i = 0; i < 5; i++) { a.ctx.callbacks.flown({ docs: [] }); await flush(); }
    assert.equal(a.ctx.log.filter(x => x[0] === 'flown').length, 1);
    console.log('PASS acknowledged writes are not repeated while snapshots lag');
  }
  {
    const a = setup(); a.r.state.marks.set('L001', mark(true, 1000)); a.ctx.failWrites = 1;
    await connect(a);
    a.ctx.callbacks.flown({ docs: [] }); await flush();
    assert.equal(a.ctx.log.filter(x => x[0] === 'flown').length, 2);
    assert.equal(a.r.state.flown.has('L001'), true);
    a.ctx.callbacks.flown({ docs: [] }); await flush();
    assert.equal(a.ctx.log.filter(x => x[0] === 'flown').length, 2);
    console.log('PASS failed writes may retry; confirmed retry is deduplicated');
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
