(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const D = JSON.parse($('#tour-data').textContent);
  const AP = D.airports;
  const LEGS = D.legs;
  const CH = D.chapters;
  const XC = D.excursions;
  const CATN = Object.fromEntries(D.cats.map(c => [c.code, c.name]));
  // Volanta-Namen bleiben sichtbar; die Suche versteht zusätzlich deutsche Ländernamen.
  const CAT_SEARCH = { ...CATN };
  try {
    const regions = new Intl.DisplayNames(['de'], { type: 'region' });
    for (const c of D.cats) CAT_SEARCH[c.code] += ' ' + regions.of(c.code);
  } catch (e) { /* Ältere Browser suchen weiterhin nach den Volanta-Namen. */ }
  const legIdx = new Map(LEGS.map((l, i) => [l.id, i]));
  const chIdx = new Map(CH.map((c, i) => [c.id, i]));
  const A320_TOTAL = D.stats.a320.legs;
  const TOTAL_AIR = D.stats.air;
  const LS_KEY = 'weltreise-edlv-v2';
  const IS_ARTIFACT = D.meta.mode === 'artifact';
  const hasRuntime = !!(window.claude && typeof window.claude.use === 'function');

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nf = n => Number(n).toLocaleString('de-DE');
  const hm = m => `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')}`;
  const pad3 = n => String(n).padStart(3, '0');
  const today = () => new Date().toISOString().slice(0, 10);
  const fmtDate = iso => String(iso || '').split('-').reverse().join('.');
  const cityOf = a => a.c || a.n;
  const isIcao = s => /^[A-Z][A-Z0-9]{3}$/.test(s);
  const legLabel = l => (l.k === 'h' ? l.id.slice(2) : pad3(l.n));
  const searchText = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss').toLowerCase();

  // ---------- Zustand ----------
  // marks: pro Leg {on, at, t}. Auch entfernte Häkchen bleiben als {on:false} mit Zeitstempel
  // erhalten, damit Geräte beim Abgleich wissen, welche Änderung neuer ist.
  // epochs: Reset-Zeitpunkte – ältere Einträge gelten danach als zurückgesetzt.
  const state = {
    idx: 0,
    view: 'chapter',
    tab: 'plan',
    marks: new Map(),
    vstates: new Map(),
    epochs: { progress: 0, volanta: 0 },
    flown: new Map(),
    debriefs: new Map(Object.entries(D.debriefs || {})),
    q: '', flt: 'all', ch: 'all', cat: 'all',
  };

  const stamp = lastSeen => Math.max(Date.now(), lastSeen + 1);
  // Bei identischen Zeitstempeln müssen alle Geräte dieselbe Entscheidung treffen.
  // Ein entferntes Häkchen gewinnt; das Datum löst verbleibende Gleichstände auf.
  const compareText = (a, b) => a === b ? 0 : a > b ? 1 : -1;
  const compareMark = (a, b) => a.t - b.t || Number(b.on) - Number(a.on) || compareText(a.at, b.at);
  const compareVol = (a, b) => a.t - b.t || compareText(a.s, b.s);
  const eventKey = (kind, id, t) => `${kind}_${id}_${t}_${typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)}`;
  function rebuildFlown() {
    const m = new Map();
    for (const [id, mk] of state.marks) if (mk.on && mk.t > state.epochs.progress) m.set(id, mk.at || '');
    state.flown = m;
  }
  // Einträge ohne Zeitstempel (erste V2-Fassung) gelten als sehr alt: Sie zählen, solange es keinen
  // späteren Reset gibt, und ein späterer Reset setzt sie zurück.
  const legacyT = v => { const t = Number(v); return Number.isFinite(t) && t > 0 ? t : 1; };
  function cleanMark(v) {
    if (!v || typeof v !== 'object') return null;
    return { on: v.on !== false, at: typeof v.at === 'string' ? v.at : '', t: legacyT(v.t) };
  }

  function loadLocal() {
    try {
      const o = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
      if (o.marks && typeof o.marks === 'object') {
        for (const [k, v] of Object.entries(o.marks)) { const m = cleanMark(v); if (m && legIdx.has(k)) state.marks.set(k, m); }
      } else if (o.flown && typeof o.flown === 'object') {
        // älteres V2-Format: {flown: {legId: datum}}
        for (const [k, v] of Object.entries(o.flown)) if (legIdx.has(k)) state.marks.set(k, { on: true, at: String(v || ''), t: 1 });
      }
      if (o.vstates && typeof o.vstates === 'object') {
        for (const [k, v] of Object.entries(o.vstates)) if (CATN[k] && v && typeof v === 'object') state.vstates.set(k, { s: String(v.s || 'open'), t: legacyT(v.t) });
      }
      if (o.epochs && typeof o.epochs === 'object') {
        state.epochs.progress = Number(o.epochs.progress) || 0;
        state.epochs.volanta = Number(o.epochs.volanta) || 0;
      }
      if (['leg', 'chapter', 'world', 'globe'].includes(o.view)) state.view = o.view;
      if (['plan', 'hl', 'scn', 'cat', 'new', 'data'].includes(o.tab)) state.tab = o.tab;
    } catch (e) { /* Browser-Speicher nicht verfügbar */ }
    rebuildFlown();
  }
  function saveLocal() {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({
        v: 3, marks: Object.fromEntries(state.marks), vstates: Object.fromEntries(state.vstates),
        epochs: state.epochs, view: state.view, tab: state.tab,
      }));
    } catch (e) { /* ignorieren */ }
  }

  // ---------- Toast ----------
  let toastTimer = 0;
  function toast(msg) {
    let t = $('#toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'toast';
      t.className = 'toast';
      t.setAttribute('role', 'status');
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { t.hidden = true; }, 3000);
  }

  // ---------- Cloud-Sync über die Artifact-Datenbank ----------
  let db = null;
  let syncMode = 'local';
  const chains = new Map();
  const pendingWrites = new Map();
  const confirmedWrites = new Map();
  function queue(key, job, version) {
    if (version !== undefined && confirmedWrites.get(key)?.has(version)) return Promise.resolve();
    const pending = pendingWrites.get(key) || new Map();
    if (version !== undefined && pending.has(version)) return pending.get(version);
    const token = version === undefined ? Symbol() : version;
    const next = (chains.get(key) || Promise.resolve()).then(job, job)
      .then(() => {
        if (version !== undefined) {
          const confirmed = confirmedWrites.get(key) || new Set();
          confirmed.add(version);
          confirmedWrites.set(key, confirmed);
        }
      })
      .catch(() => toast('Cloud-Sync fehlgeschlagen – der Stand bleibt lokal gespeichert.'))
      .finally(() => {
        pending.delete(token);
        if (!pending.size) pendingWrites.delete(key);
      });
    pending.set(token, next);
    pendingWrites.set(key, pending);
    chains.set(key, next);
    return next;
  }
  function setSync(mode) {
    syncMode = mode;
    const el = $('#sync');
    el.className = 'chip' + (mode === 'cloud' ? ' cloud' : mode === 'pending' ? ' pending' : '');
    el.lastElementChild.textContent = mode === 'cloud' ? 'Cloud-Sync' : mode === 'pending' ? 'Verbinde …' : 'Lokal';
    el.title = mode === 'cloud'
      ? 'Fortschritt liegt in der Artifact-Datenbank und ist auf allen Geräten gleich.'
      : 'Fortschritt liegt nur in diesem Browser. Unter „Daten & Reset“ sichern.';
    if (state.tab === 'data') renderData();
  }
  function pushMark(id) {
    if (!db) return;
    const m = state.marks.get(id);
    if (!m || m.t <= state.epochs.progress) return; // vor dem letzten Reset – nicht mehr relevant
    const l = LEGS[legIdx.get(id)];
    // Neue Änderungen überschreiben keinen früheren Cloud-Eintrag. Damit bleibt
    // der Gewinner auch erhalten, wenn sein ursprüngliches Gerät geschlossen ist.
    const key = eventKey('f', id, m.t);
    const value = { legId: id, on: m.on, at: m.at, t: m.t, from: l.f, to: l.t };
    queue('f:' + id, () => db.collection('flown').doc(key).set(value), JSON.stringify(value));
  }
  function pushVol(code) {
    if (!db) return;
    const v = state.vstates.get(code);
    if (!v || v.t <= state.epochs.volanta) return;
    const key = eventKey('v', code, v.t);
    const value = { code, s: v.s, t: v.t };
    queue('v:' + code, () => db.collection('volanta').doc(key).set(value), JSON.stringify(value));
  }
  function pushEpochs() {
    if (!db) return;
    const value = { progress: state.epochs.progress, volanta: state.epochs.volanta };
    // Derselbe Epochensatz hat denselben Schlüssel; verschiedene Resets bleiben erhalten.
    const key = `p${value.progress}_v${value.volanta}`;
    queue('epochs', () => db.collection('resets').doc(key).set(value), key);
  }
  function mergeMarks(docs) {
    const remote = new Map();
    docs.forEach(d => {
      if (!d.exists) return;
      const value = d.data();
      const id = value && legIdx.has(value.legId) ? value.legId : d.id;
      if (!legIdx.has(id)) return;
      const m = cleanMark(value);
      const prior = remote.get(id);
      if (m && (!prior || compareMark(m, prior) > 0)) remote.set(id, m);
    });
    for (const [id, r] of remote) {
      const l = state.marks.get(id);
      if (!l || compareMark(r, l) > 0) state.marks.set(id, r);
    }
    // Auch nach dem ersten Snapshot abgleichen: Ein verspäteter Schreibzugriff eines
    // anderen Geräts darf den neueren Stand nicht dauerhaft in der Cloud ersetzen.
    for (const [id, l] of state.marks) {
      const r = remote.get(id);
      if (!r || compareMark(l, r) > 0) pushMark(id);
    }
  }
  function mergeVol(docs) {
    const remote = new Map();
    docs.forEach(d => {
      if (!d.exists) return;
      const v = d.data() || {};
      const code = CATN[v.code] ? v.code : d.id;
      if (!CATN[code]) return;
      const value = { s: String(v.s || 'open'), t: legacyT(v.t) };
      const prior = remote.get(code);
      if (!prior || compareVol(value, prior) > 0) remote.set(code, value);
    });
    for (const [code, r] of remote) {
      const l = state.vstates.get(code);
      if (!l || compareVol(r, l) > 0) state.vstates.set(code, r);
    }
    for (const [code, l] of state.vstates) {
      const r = remote.get(code);
      if (!r || compareVol(l, r) > 0) pushVol(code);
    }
  }
  async function initCloud() {
    if (!hasRuntime) return;
    setSync('pending');
    try { db = await window.claude.use('db'); } catch (e) { db = null; }
    if (!db) { setSync('local'); return; }
    const lost = () => { db = null; setSync('local'); };
    const applyEpochs = r => {
      const rp = Number(r.progress) || 0;
      const rv = Number(r.volanta) || 0;
      state.epochs.progress = Math.max(state.epochs.progress, rp);
      state.epochs.volanta = Math.max(state.epochs.volanta, rv);
      // Einträge von vor dem Reset lokal aufräumen
      for (const [id, m] of state.marks) if (m.t <= state.epochs.progress) state.marks.delete(id);
      for (const [c, v] of state.vstates) if (v.t <= state.epochs.volanta) state.vstates.delete(c);
      rebuildFlown();
      saveLocal();
      refreshProgress();
    };
    // Das alte Reset-Dokument bleibt lesbar und wird beim Empfang ins Journal übernommen.
    db.doc('meta/reset').onSnapshot(snap => {
      const before = { ...state.epochs };
      applyEpochs(snap.exists ? (snap.data() || {}) : {});
      if (state.epochs.progress > before.progress || state.epochs.volanta > before.volanta) pushEpochs();
    }, lost);
    db.collection('resets').onSnapshot(snap => {
      const r = { progress: 0, volanta: 0 };
      snap.docs.forEach(d => {
        if (!d.exists) return;
        const v = d.data() || {};
        r.progress = Math.max(r.progress, Number(v.progress) || 0);
        r.volanta = Math.max(r.volanta, Number(v.volanta) || 0);
      });
      const localNewer = state.epochs.progress > r.progress || state.epochs.volanta > r.volanta;
      applyEpochs(r);
      if (localNewer) pushEpochs();
    }, lost);
    db.collection('flown').onSnapshot(snap => {
      mergeMarks(snap.docs);
      rebuildFlown();
      saveLocal();
      setSync('cloud');
      refreshProgress();
    }, lost);
    db.collection('volanta').onSnapshot(snap => {
      mergeVol(snap.docs);
      saveLocal();
      refreshProgress();
    }, lost);
    db.collection('debriefs').onSnapshot(snap => {
      const m = new Map(Object.entries(D.debriefs || {}));
      snap.docs.forEach(d => { if (d.exists) m.set(d.id, d.data()); });
      state.debriefs = m;
      renderProse();
      renderTracks();
      if (state.tab === 'cat') renderCat();
    }, () => { /* Debriefings bleiben, wie sie sind */ });
  }

  function setFlown(id, on) {
    const prev = state.marks.get(id);
    const prevOn = prev && prev.on && prev.t > state.epochs.progress;
    state.marks.set(id, { on, at: on ? (prevOn && prev.at) || today() : (prev ? prev.at : ''), t: stamp(Math.max(state.epochs.progress, prev ? prev.t : 0)) });
    rebuildFlown();
    saveLocal();
    pushMark(id);
    refreshProgress();
  }
  const toggleFlown = id => setFlown(id, !state.flown.has(id));

  function setVol(code, s) {
    const prev = state.vstates.get(code);
    state.vstates.set(code, { s, t: stamp(Math.max(state.epochs.volanta, prev ? prev.t : 0)) });
    saveLocal();
    pushVol(code);
    refreshProgress();
  }

  // ---------- Hilfen ----------
  const cur = () => LEGS[state.idx];
  const chapterOf = l => CH[chIdx.get(l.ch)];
  function flownCats() {
    const s = new Set();
    for (const id of state.flown.keys()) {
      const l = LEGS[legIdx.get(id)];
      s.add(AP[l.f].cc); s.add(AP[l.t].cc);
    }
    return s;
  }
  // Volanta: "laut Flugplan erreicht" (Häkchen) getrennt von "in Volanta bestätigt" bzw. "nicht gewertet".
  // Zeitpunkt einer Volanta-Angabe im Debriefing: genau (volantaAt) oder ersatzweise Tagesbeginn von updatedAt.
  function debriefTs(d) {
    const p = Date.parse(d.volantaAt || (d.updatedAt ? `${d.updatedAt}T00:00:00Z` : ''));
    return Number.isFinite(p) && p > 0 ? p : 1;
  }
  function volanta() {
    const reached = flownCats();
    const ok = new Set();
    const no = new Set();
    for (const [lid, d] of state.debriefs) {
      const i = legIdx.get(lid);
      if (i === undefined || !d) continue;
      if (!(debriefTs(d) > state.epochs.volanta)) continue; // vor dem letzten Volanta-Reset erfasst
      const l = LEGS[i];
      if (d.volanta === 'credited') { ok.add(AP[l.f].cc); ok.add(AP[l.t].cc); }
      else if (d.volanta === 'not_credited') no.add(AP[l.t].cc);
    }
    ok.forEach(c => no.delete(c));
    for (const [code, v] of state.vstates) {
      if (!(v.t > state.epochs.volanta)) continue;
      if (v.s === 'credited') { ok.add(code); no.delete(code); }
      else if (v.s === 'not_credited') { no.add(code); ok.delete(code); }
      else { ok.delete(code); no.delete(code); }
    }
    return { reached, ok, no };
  }
  function nextNewCat(done) {
    for (const l of LEGS) {
      if (state.flown.has(l.id)) continue;
      const cc = AP[l.t].cc;
      if (!done.has(cc)) return { id: l.id, cc };
    }
    return null;
  }
  const BADGE = {
    owned: 'Eigene', buy: 'Kauf-Tipp', freeware: 'Freeware', hand: 'Handgefertigt', optional: 'Optional',
    stdok: 'Angebot recherchiert', candidate: 'Freeware · prüfen', unrated: 'Ungeprüft', addon: 'Freeware-Fix',
  };
  function stOf(it) { return it.status === 'freeware' && it.addon ? 'addon' : it.status; }
  function badge(st, label) {
    const cls = st === 'addon' ? 'freeware' : st;
    return `<span class="badge ${cls}">${esc(label || BADGE[st] || st)}</span>`;
  }
  const itemBadge = it => badge(stOf(it), it.required ? 'Freeware · Pflicht' : undefined);
  const primaryBadge = a => itemBadge(a.sc.items[0]);
  // ungeprüft = kein Urteil über den Standard, auch wenn eine Payware-Option daneben steht
  const isUnrated = a => a.sc.items.some(it => it.status === 'unrated');
  function simbrief(l) {
    if (l.k !== 'a' || !isIcao(l.f) || !isIcao(l.t)) return '';
    return `https://www.simbrief.com/system/dispatch.php?type=A320&orig=${l.f}&dest=${l.t}`;
  }
  function excursionsAfter(i) {
    const out = [];
    for (let j = i + 1; j < LEGS.length && LEGS[j].k === 'h'; j++) {
      if (!out.includes(LEGS[j].x)) out.push(LEGS[j].x);
    }
    return out;
  }

  // ---------- Prosa (linke Spalte) ----------
  function autoClaim(l) {
    const b = AP[l.t];
    if (l.nc) return `Neue Kategorie: ${CATN[l.nc[0]]}.`;
    const own = b.sc.items.find(x => x.status === 'owned');
    if (own) return `${cityOf(b)} mit deiner ${own.dev}-Szenerie.`;
    return `Weiter nach ${cityOf(b)} · ${CATN[b.cc]}.`;
  }
  function debriefHtml(d) {
    if (!d) return '';
    const sc = d.actualScenery || {};
    const vol = { credited: 'gutgeschrieben', not_credited: 'nicht gutgeschrieben', open: 'offen' }[d.volanta] || d.volanta;
    const rows = [
      ['Datum', d.flightDate], ['Flugzeug', d.aircraft],
      ['Szenerie Abflug', sc.departure && sc.departure.product], ['Szenerie Ankunft', sc.arrival && sc.arrival.product],
      ['Landschaft', sc.landscape], ['Anflug', d.approach], ['Bedingungen', d.conditions],
      ['Highlight', d.highlights], ['Probleme', d.issues], ['Fazit', d.verdict], ['Nächstes Mal', d.nextTime], ['Volanta', vol],
    ].filter(r => r[1]);
    return `<div class="debrief"><h3>Debriefing${d.status === 'final' ? ' · final' : ' · Entwurf'}</h3><dl>${rows.map(r => `<dt>${esc(r[0])}</dt><dd>${esc(r[1])}</dd>`).join('')}</dl></div>`;
  }
  function debriefTemplate(l) {
    return [
      `Debriefing ${l.id}: ${l.f} → ${l.t}`,
      'Flugdatum: ',
      `Flugzeug: ${l.k === 'h' ? 'Airbus H160' : 'Fenix A320'}`,
      `Szenerie ${l.f} (Hersteller, Produkt, Version): `,
      `Szenerie ${l.t} (Hersteller, Produkt, Version): `,
      'Landschafts-Add-ons (oder „keine“): ',
      'Anflug, Bahn, Wetter, Tageszeit: ',
      'Highlight: ',
      'Performance und Probleme: ',
      'Szenerie-Fazit: ',
      'Nächstes Mal anders: ',
      'Volanta gutgeschrieben? ',
    ].join('\n');
  }
  function trialHtml(l) {
    if (!l.trial) return '';
    const tr = AP[l.trial].trial;
    const what = l.t === l.trial ? 'Landung' : 'Start';
    return `<div class="trial"><h3>${esc(tr.title)} · ${what} erst testen</h3><p>${esc(tr.why)}</p>
      <ul>${tr.checks.map(c => `<li>${esc(c)}</li>`).join('')}</ul>
      <p class="fb"><b>Ausweichplan:</b> ${esc(tr.fallback)}</p></div>`;
  }

  function renderProse() {
    const l = cur();
    const a = AP[l.f];
    const b = AP[l.t];
    const ch = chapterOf(l);
    const isH = l.k === 'h';
    const x = isH ? XC[l.x] : null;
    const outbound = isH && l.t === x.target;
    const done = state.flown.has(l.id);
    const meta = [];
    if (isH) meta.push(`<span class="heli">${esc(l.id)} · H160 · ${x.kind === 'bonus' ? 'Bonus-Ausflug' : 'Kategorie-Ausflug'}</span>`);
    else meta.push(`LEG ${pad3(l.n)} / ${A320_TOTAL} · A320`);
    if (l.nc) meta.push(`<span class="new">neue Kategorie: ${esc(CATN[l.nc[0]])}</span>`);
    if (done) meta.push(`<span class="new">geflogen ${esc(state.flown.get(l.id))}</span>`);

    let claim;
    let body = '';
    let tips = [];
    if (isH) {
      claim = outbound ? `${x.title} – ${x.tag}` : `Zurück zum A320 in ${cityOf(b)}.`;
      if (outbound) {
        body = x.brief;
        if (x.fallback) body += ` Ausweichziel: ${x.fallback.anchor} → ${x.fallback.target}.`;
      }
    } else {
      claim = b.hl || autoClaim(l);
      body = b.brief || '';
      tips = b.tips || [];
    }
    const rw = b.rw ? `<span>RWY ${esc(b.rw.id)} · <b>${nf(b.rw.m)} m</b>${b.rw.w ? ' × ' + b.rw.w + ' m' : ''}</span>` : `<span>${b.type === 'heliport' ? 'Heliport' : 'Landeplatz'}</span>`;
    const kicker = [
      `<span><b>${nf(l.nm)}</b> NM</span>`,
      `<span>Flug <b>${hm(l.air)}</b></span>`,
      l.blk ? `<span>Block ${hm(l.blk)}</span>` : '',
      l.o2 ? '<span class="warn">über 2 h</span>' : '',
      l.trial ? '<span class="warn">Sonderetappe</span>' : '',
      rw,
      b.el != null ? `<span>${nf(b.el)} ft</span>` : '',
    ].join('');
    const sb = simbrief(l);
    const x2 = !isH ? excursionsAfter(state.idx) : [];
    $('#prose').innerHTML = `
      <div class="eyebrow">Kapitel ${esc(ch.id)} · ${esc(ch.title)}</div>
      <div class="legmeta">${meta.join('')}</div>
      <h2 class="route-title"><span>${esc(l.f)}</span><span class="arrow" aria-hidden="true">→</span><span>${esc(l.t)}</span></h2>
      <div class="route-cities">${esc(cityOf(a))} → ${esc(cityOf(b))} · ${esc(CATN[b.cc])}</div>
      <p class="claim${isH ? ' heli' : ''}">${esc(claim)}</p>
      ${body ? `<p class="body">${esc(body)}</p>` : ''}
      ${tips.length ? `<ul class="tips">${tips.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
      ${x2.length ? `<p class="body">Danach: H160-Ausflug${x2.length > 1 ? 'e' : ''} ${x2.map(id => esc(XC[id].title)).join(', ')} – unten bei der Karte.</p>` : ''}
      ${trialHtml(l)}
      <div class="kicker">${kicker}</div>
      <div class="actions">
        <button type="button" class="btn ${done ? 'done' : 'primary'}" id="flownbtn" aria-pressed="${done}">${done ? '✓ Geflogen' : 'Als geflogen markieren'}</button>
        ${sb ? `<a class="btn" href="${sb}" target="_blank" rel="noopener">SimBrief ↗</a>` : ''}
        <button type="button" class="btn" id="dbtpl">Debrief-Vorlage</button>
      </div>
      <div id="dbhost">${debriefHtml(state.debriefs.get(l.id))}</div>`;
  }

  // ---------- Airport-Panels ----------
  function installationNotes(it) {
    const deps = Array.isArray(it.dependencies) ? it.dependencies.filter(d => d && d.product) : [];
    const list = deps.length ? `<ul class="dependencies">${deps.map(d => `<li><b>${d.required ? 'Zusätzlich erforderlich' : 'Optionaler Zusatz'}:</b> ${d.url ? `<a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.product)}${d.dev ? ` · ${esc(d.dev)}` : ''} ↗</a>` : esc(d.product)}${d.note ? ` — ${esc(d.note)}` : ''}</li>`).join('')}</ul>` : '';
    return list + (it.installNote ? `<p class="installation-note">${esc(it.installNote)}</p>` : '');
  }
  function simCheckNote(a) {
    const sources = (a.simCheck && Array.isArray(a.simCheck.sources) ? a.simCheck.sources : [])
      .map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">Quelle ${i + 1} ↗</a>`).join(' · ');
    return a.simCheck && a.simCheck.status === 'unconfirmed'
      ? `<div class="sim-check"><b>Sim-Prüfung offen</b><p>${esc(a.simCheck.note)}</p>${sources ? `<p>${sources}</p>` : ''}</div>` : '';
  }
  function scnLine(it) {
    const st = stOf(it);
    if (st === 'owned') {
      return `<div class="line">${badge('owned')}<span>Deine Szenerie · ${esc(it.dev)}</span></div>${it.note ? `<div class="why">${esc(it.note)}</div>` : ''}${installationNotes(it)}`;
    }
    if (st === 'hand') return `<div class="line">${badge('hand')}<span>${esc(it.product)}</span></div>${installationNotes(it)}`;
    if (st === 'stdok') return `<div class="line">${badge('stdok')}<span>MSFS-Standard · keine feste Add-on-Empfehlung</span></div><div class="why">${esc(it.why || '')}</div>${installationNotes(it)}`;
    if (st === 'unrated') return `<div class="line">${badge('unrated')}<span>Keine eigene Recherche – MSFS-Standard</span></div>`;
    const name = `${esc(it.product)} · ${esc(it.dev)}`;
    const link = it.url ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">${name} ↗</a>` : name;
    const meta = [it.rating && `★ ${esc(it.rating)}`, it.price && esc(it.price)].filter(Boolean).join(' · ');
    const alt = it.alt ? ` Alternative: <a href="${esc(it.alt.url)}" target="_blank" rel="noopener">${esc(it.alt.name)} ↗</a>` : '';
    return `<div class="line">${itemBadge(it)}<span>${link}</span></div><div class="why">${esc(it.why || '')}${meta ? ` <span class="mono">${meta}</span>` : ''}${alt}</div>${installationNotes(it)}`;
  }
  function aptCard(a, role, isTo, l) {
    const rw = a.rw ? `RWY ${esc(a.rw.id)} · ${nf(a.rw.m)} m${a.rw.w ? ' × ' + a.rw.w : ''}${a.rw.s ? ' ' + esc(a.rw.s) : ''}` : (a.type === 'heliport' ? 'Heliport' : 'Landeplatz');
    const isNew = isTo && l.nc;
    return `<article class="apt${isTo ? ' to' : ''}">
      <div class="role"><span>${role}</span>${primaryBadge(a)}</div>
      <div class="icao">${esc(a.i)}</div>
      <div class="aname">${esc(cityOf(a))}${a.c && a.n !== a.c ? ' · ' + esc(a.n) : ''}</div>
      <div class="facts"><span${isNew ? ' class="new"' : ''}>${esc(CATN[a.cc])}${isNew ? ' · neu' : ''}</span><span>${rw}</span>${a.el != null ? `<span>${nf(a.el)} ft</span>` : ''}</div>
      ${simCheckNote(a)}
      <div class="scn">${a.sc.items.map(scnLine).join('')}</div>
    </article>`;
  }
  function renderPanels() {
    const l = cur();
    $('#apts').innerHTML = aptCard(AP[l.f], 'Abflug', false, l) + aptCard(AP[l.t], 'Ziel', true, l);
  }

  function renderXcards() {
    const l = cur();
    const ids = l.k === 'h' ? [l.x] : excursionsAfter(state.idx);
    $('#xcards').innerHTML = ids.map(id => {
      const x = XC[id];
      const tgt = AP[x.target];
      const fallback = x.fallback && AP[x.fallback.target];
      const kind = x.kind === 'bonus' ? 'Bonus' : `Kategorie ${CATN[tgt.cc]}`;
      const chips = x.legs.map(lid => {
        const lg = LEGS[legIdx.get(lid)];
        const cls = (state.flown.has(lid) ? ' done' : '') + (lid === l.id ? ' now' : '');
        return `<button type="button" class="xleg${cls}" data-leg="${lid}">${state.flown.has(lid) ? '✓ ' : ''}${esc(lg.f)} → ${esc(lg.t)} · ${hm(lg.air)}</button>`;
      }).join('');
      return `<article class="xcard"><div class="xh"><b>${esc(x.title)}</b><span>H160 · ${esc(kind)} · ${esc(x.tag)}</span></div>
        <p>${esc(x.brief)}</p>${fallback && fallback.simCheck ? `<b>Ausweichziel ${esc(fallback.i)}</b>${simCheckNote(fallback)}` : ''}<div class="xlegs">${chips}</div></article>`;
    }).join('');
  }

  // ---------- Tracks & Kopfzeile ----------
  function track(name, st, val, frac, note, ok, live) {
    const w = (Math.max(0, Math.min(1, frac)) * 100).toFixed(1);
    return `<div class="track${live ? ' live' : ''}"><div class="name">${esc(name)}</div><div class="state">${esc(st)}</div>
      <div class="val">${val}</div><div class="bar${ok ? ' ok' : ''}"><i style="width:${w}%"></i></div><div class="note">${esc(note)}</div></div>`;
  }
  function renderTracks() {
    const flown = LEGS.filter(l => state.flown.has(l.id));
    const nA = flown.filter(l => l.k === 'a').length;
    const v = volanta();
    const air = flown.reduce((s, l) => s + l.air, 0);
    const l = cur();
    const ch = chapterOf(l);
    const chDone = ch.legs.filter(id => state.flown.has(id)).length;
    const next = nextNewCat(v.reached);
    $('#tracks').innerHTML = [
      track('Fortschritt', 'Legs geflogen', `${flown.length}<small> / ${LEGS.length}</small>`, flown.length / LEGS.length,
        `A320 ${nA}/${A320_TOTAL} · H160 ${flown.length - nA}/${D.stats.h160.legs}`, false, false),
      track('Kategorien', 'laut Flugplan erreicht', `${v.reached.size}<small> / 245</small>`, v.reached.size / 245,
        `In Volanta bestätigt: ${v.ok.size} · nicht gewertet: ${v.no.size}${next ? ` · nächste neue: ${CATN[next.cc]}` : ''}`, true, false),
      track('Flugzeit', 'Stunden in der Luft', `${nf(Math.round(air / 60))}<small> / ${nf(Math.round(TOTAL_AIR / 60))} h</small>`, air / TOTAL_AIR,
        `Noch rund ${nf(Math.round((TOTAL_AIR - air) / 60))} h`, false, false),
      track(`Kapitel ${ch.id}`, ch.title, `${chDone}<small> / ${ch.legs.length}</small>`, chDone / ch.legs.length, ch.season, false, true),
    ].join('');
    $('#count').innerHTML = `<b>${flown.length}</b>/${LEGS.length} Legs · <b>${v.reached.size}</b>/245 Kategorien · <b>${v.ok.size}</b> bestätigt`;
  }

  // ---------- Leg-Leiste ----------
  const pipEl = new Map();
  function renderRail() {
    $('#rail').innerHTML = CH.map(c => {
      const pips = c.legs.map(id => {
        const l = LEGS[legIdx.get(id)];
        const cls = `pip${l.k === 'h' ? ' heli' : ''}${l.o2 ? ' long' : ''}`;
        return `<button type="button" class="${cls}" data-leg="${id}" tabindex="-1" title="${esc(id)} · ${esc(l.f)} → ${esc(l.t)}" aria-label="${esc(id)} ${esc(l.f)} nach ${esc(l.t)}"><span class="pip-label">${esc(legLabel(l))}</span></button>`;
      }).join('');
      return `<div class="act" data-ch="${c.id}"><button type="button" class="chapter-link lbl" data-go="${c.legs[0]}"><b>${c.id}</b>${esc(c.title)} <b class="cnt"></b></button><div class="pips">${pips}</div></div>`;
    }).join('');
    $$('#rail .pip').forEach(p => pipEl.set(p.dataset.leg, p));
  }
  function updateRail(scroll) {
    const l = cur();
    for (const [id, p] of pipEl) {
      p.classList.toggle('done', state.flown.has(id));
      p.classList.toggle('now', id === l.id);
      p.tabIndex = id === l.id ? 0 : -1;
      if (id === l.id) p.setAttribute('aria-current', 'step');
      else p.removeAttribute('aria-current');
      const leg = LEGS[legIdx.get(id)];
      p.setAttribute('aria-label', `${id} ${leg.f} nach ${leg.t}${state.flown.has(id) ? ', geflogen' : ', offen'}`);
    }
    $$('#rail .act').forEach(act => {
      const c = CH[chIdx.get(act.dataset.ch)];
      act.classList.toggle('here', c.id === l.ch);
      act.querySelector('.cnt').textContent = `${c.legs.filter(id => state.flown.has(id)).length}/${c.legs.length}`;
    });
    if (scroll) {
      const p = pipEl.get(l.id);
      const rail = $('#rail');
      if (p && rail) {
        const r = p.getBoundingClientRect();
        const rr = rail.getBoundingClientRect();
        if (r.left < rr.left + 40 || r.right > rr.right - 40) rail.scrollLeft += (r.left - rr.left) - rr.width / 2;
      }
    }
  }

  // ---------- Karte ----------
  const Chart = (() => {
    const host = $('#map');
    if (!window.d3 || !window.topojson) {
      host.classList.add('nomap-box');
      host.innerHTML = '<div class="nomap">Die Karte konnte nicht geladen werden. Alle anderen Funktionen stehen zur Verfügung.</div>';
      return { draw() {}, styleLegs() {}, recenter() {}, zoomBy() {}, zoomReset() {} };
    }
    const d3 = window.d3;
    const W = 960;
    const H = 540;
    const world = JSON.parse($('#world-data').textContent);
    const land = window.topojson.feature(world, world.objects.land);
    const borders = window.topojson.mesh(world, world.objects.countries, (a, b) => a !== b);
    const grat = d3.geoGraticule10();
    const svg = d3.select(host).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Routenkarte');
    const filt = svg.append('defs').append('filter').attr('id', 'glow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%');
    filt.append('feGaussianBlur').attr('stdDeviation', 2.6).attr('result', 'b');
    const merge = filt.append('feMerge');
    merge.append('feMergeNode').attr('in', 'b');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');
    const sphere = svg.append('path').attr('class', 'm-sphere');
    const gratP = svg.append('path').attr('class', 'm-grat');
    const landP = svg.append('path').attr('class', 'm-land');
    const bordP = svg.append('path').attr('class', 'm-border');
    const gRings = svg.append('g');
    const gLegs = svg.append('g');
    const gHit = svg.append('g');
    const actP = svg.append('path').attr('class', 'm-act');
    const flowP = svg.append('path').attr('class', 'm-flow');
    const gApt = svg.append('g');
    const gLbl = svg.append('g');
    const plane = svg.append('path').attr('class', 'm-plane').attr('d', 'M0,-10 L6,7 L0,3.5 L-6,7 Z');
    const hud = d3.select(host).append('div').attr('class', 'maphud');
    // Zoom-Bedienung: Knöpfe oben rechts, Hinweis bei Mausrad ohne Strg
    const icon = d => `<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`;
    const ctl = d3.select(host).append('div').attr('class', 'zoomctl').attr('role', 'group').attr('aria-label', 'Kartenzoom');
    const zIn = ctl.append('button').attr('type', 'button').attr('aria-label', 'Karte vergrößern').attr('title', 'Vergrößern (+)').html(icon('M8 3v10M3 8h10'));
    const zOut = ctl.append('button').attr('type', 'button').attr('aria-label', 'Karte verkleinern').attr('title', 'Verkleinern (−)').html(icon('M3 8h10'));
    const zFit = ctl.append('button').attr('type', 'button').attr('aria-label', 'Zoom zurücksetzen').attr('title', 'Ganze Ansicht (0)')
      .html(icon('M2.5 6V2.5H6M13.5 6V2.5H10M2.5 10v3.5H6M13.5 10v3.5H10'));
    const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');
    const hint = d3.select(host).append('div').attr('class', 'zoomhint').attr('aria-hidden', 'true')
      .text(`${isMac ? '⌘' : 'Strg'} + Mausrad zum Zoomen · auf dem Tablet mit zwei Fingern`);

    const geo = LEGS.map(l => ({ type: 'LineString', coordinates: [[AP[l.f].lon, AP[l.f].lat], [AP[l.t].lon, AP[l.t].lat]] }));
    const legSel = gLegs.selectAll('path').data(LEGS).join('path').attr('class', 'm-leg');
    const hitSel = gHit.selectAll('path').data(LEGS).join('path').attr('class', 'm-hit').on('click', (ev, d) => selectId(d.id));
    hitSel.append('title').text(d => `${d.id} · ${d.f} → ${d.t}`);
    const apts = Object.values(AP);
    const aptSel = gApt.selectAll('circle').data(apts).join('circle').attr('class', 'm-apt').attr('r', 2)
      .on('click', (ev, d) => {
        const own = LEGS.findIndex(l => l.t === d.i && l.ch === cur().ch);
        const any = own >= 0 ? own : LEGS.findIndex(l => l.t === d.i);
        if (any >= 0) select(any);
      });
    aptSel.append('title').text(d => `${d.i} · ${cityOf(d)}`);

    let proj = null;
    let center = [0, 0];
    let clipDeg = 180;
    let globeCenter = null;
    let raf = 0;
    let zoomKey = '';
    let pinching = false;
    const circles = new Map();
    const schedule = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; draw(); }); };

    function chapterCircle(ch) {
      if (circles.has(ch.id)) return circles.get(ch.id);
      const pts = [...new Set(ch.route)].map(i => [AP[i].lon, AP[i].lat]);
      ch.legs.forEach(id => {
        const l = LEGS[legIdx.get(id)];
        if (l.k === 'h') pts.push([AP[l.t].lon, AP[l.t].lat]);
      });
      const c = d3.geoCentroid({ type: 'MultiPoint', coordinates: pts });
      let r = 0;
      pts.forEach(p => { r = Math.max(r, d3.geoDistance(c, p) * 180 / Math.PI); });
      const res = { center: c, radius: Math.max(r * 1.1 + 1.5, 4) };
      circles.set(ch.id, res);
      return res;
    }
    const visible = p => clipDeg >= 180 || d3.geoDistance(center, p) < clipDeg * Math.PI / 180 - 1e-6;

    function styleLegs() {
      const chId = cur().ch;
      legSel.attr('class', d => `m-leg${d.k === 'h' ? ' heli' : ''}${d.ch === chId ? ' ch' : ''}${state.flown.has(d.id) ? ' done' : ''}`);
    }

    function draw() {
      const l = cur();
      const ch = chapterOf(l);
      const A = geo[state.idx].coordinates[0];
      const B = geo[state.idx].coordinates[1];
      const view = state.view;
      const ext = [[16, 16], [W - 16, H - 16]];
      if (view === 'world') {
        const c = chapterCircle(ch).center;
        center = [c[0], 0];
        clipDeg = 180;
        proj = d3.geoNaturalEarth1().rotate([-c[0], 0]).fitExtent(ext, { type: 'Sphere' });
      } else if (view === 'globe') {
        const c = globeCenter || d3.geoInterpolate(A, B)(0.5);
        center = c;
        clipDeg = 90;
        proj = d3.geoOrthographic().rotate([-c[0], -c[1]]).clipAngle(90).fitExtent(ext, { type: 'Sphere' });
      } else if (view === 'chapter') {
        const cc = chapterCircle(ch);
        center = cc.center;
        clipDeg = Math.min(175, cc.radius * 1.9 + 25);
        proj = d3.geoAzimuthalEqualArea().rotate([-center[0], -center[1]]).clipAngle(clipDeg)
          .fitExtent(ext, d3.geoCircle().center(center).radius(cc.radius)());
      } else {
        const mid = d3.geoInterpolate(A, B)(0.5);
        const dist = d3.geoDistance(A, B) * 180 / Math.PI;
        const r = Math.max(dist * 0.62, 0.9);
        center = mid;
        clipDeg = Math.min(175, r * 3 + 12);
        proj = d3.geoAzimuthalEquidistant().rotate([-mid[0], -mid[1]]).clipAngle(clipDeg)
          .fitExtent(ext, d3.geoCircle().center(mid).radius(r)());
      }
      // Zoom wirkt auf die Projektion, nicht auf das Bild: Linien, Punkte und Beschriftungen bleiben
      // scharf und gleich groß. Neue Ansicht, neues Kapitel oder (in der Leg-Ansicht) neues Leg = neuer Ausschnitt.
      const key = view === 'globe' ? 'globe' : view === 'leg' ? `leg:${l.id}` : `${view}:${ch.id}`;
      if (key !== zoomKey) { zoomKey = key; svg.property('__zoom', d3.zoomIdentity); }
      const zt = d3.zoomTransform(svg.node());
      if (zt.k !== 1 || zt.x || zt.y) {
        const s0 = proj.scale();
        const t0 = proj.translate();
        if (view === 'globe') proj.scale(s0 * zt.k);
        else proj.scale(s0 * zt.k).translate([zt.x + zt.k * t0[0], zt.y + zt.k * t0[1]]);
      }
      const path = d3.geoPath(proj);
      sphere.attr('d', path({ type: 'Sphere' }));
      gratP.attr('d', path(grat));
      landP.attr('d', path(land));
      bordP.attr('d', path(borders));
      legSel.attr('d', (d, i) => path(geo[i]) || '');
      hitSel.attr('d', (d, i) => path(geo[i]) || '');
      styleLegs();
      const act = path(geo[state.idx]) || '';
      actP.attr('d', act).classed('heli', l.k === 'h');
      flowP.attr('d', act);

      gRings.selectAll('*').remove();
      if (view === 'leg' && l.nm > 0) {
        const dist = d3.geoDistance(A, B) * 180 / Math.PI;
        [0.5, 1].forEach(fr => {
          const r = dist * fr;
          gRings.append('path').attr('class', 'm-ring').attr('d', path(d3.geoCircle().center(A).radius(r)()) || '');
          const top = [A[0], Math.min(89.5, A[1] + r)];
          const p = visible(top) ? proj(top) : null;
          if (p) gRings.append('text').attr('class', 'm-ringlbl').attr('x', p[0] + 4).attr('y', p[1] - 4).text(`${nf(Math.round(l.nm * fr))} NM`);
        });
      }

      const chApts = new Set(ch.route);
      ch.legs.forEach(id => { const lg = LEGS[legIdx.get(id)]; chApts.add(lg.f); chApts.add(lg.t); });
      aptSel.each(function (d) {
        const s = d3.select(this);
        const p = visible([d.lon, d.lat]) ? proj([d.lon, d.lat]) : null;
        if (!p) { s.attr('display', 'none'); return; }
        const end = d.i === l.f || d.i === l.t;
        const inCh = chApts.has(d.i);
        s.attr('display', null).attr('cx', p[0]).attr('cy', p[1]).attr('r', end ? 5.2 : inCh ? 3.4 : 2.1)
          .attr('class', `m-apt${inCh ? ' ch' : ''}${d.sc.p === 'owned' ? ' own' : ''}${d.level === 2 ? ' hl2' : ''}${end ? ' end' : ''}`);
      });

      // Welt und Globus zeigen sonst nur Start und Ziel; hineingezoomt auch die Flughäfen des Kapitels
      const lbl = (view === 'world' || view === 'globe') && zt.k < 2.5 ? [l.f, l.t] : [...chApts];
      const data = [...new Set(lbl)].map(i => AP[i]).filter(a => visible([a.lon, a.lat]));
      gLbl.selectAll('text').data(data, d => d.i).join('text')
        .attr('class', d => `m-lbl${d.i === l.f || d.i === l.t ? ' end' : ''}`)
        .attr('x', d => proj([d.lon, d.lat])[0] + 7)
        .attr('y', d => proj([d.lon, d.lat])[1] - 7)
        .text(d => d.i);

      const pa = d3.geoInterpolate(A, B)(0.55);
      const pb = d3.geoInterpolate(A, B)(0.6);
      const qa = visible(pa) ? proj(pa) : null;
      const qb = visible(pb) ? proj(pb) : null;
      if (qa && qb && l.nm > 30) {
        const ang = Math.atan2(qb[1] - qa[1], qb[0] - qa[0]) * 180 / Math.PI + 90;
        plane.attr('display', null).attr('transform', `translate(${qa[0].toFixed(1)},${qa[1].toFixed(1)}) rotate(${ang.toFixed(1)})`);
      } else plane.attr('display', 'none');

      const titles = {
        leg: `Leg ${l.id} · ${nf(l.nm)} NM`,
        chapter: `Kapitel ${ch.id} · ${ch.title}`,
        world: `Ganze Reise · ${nf(D.stats.a320.nm + D.stats.h160.nm)} NM`,
        globe: 'Globus',
      };
      $('#maptitle').textContent = titles[view];
      host.classList.toggle('globe', view === 'globe');
      zoomUi();
    }

    function zoomUi() {
      const k = d3.zoomTransform(svg.node()).k;
      const zoomed = k > 1.001;
      zOut.property('disabled', !zoomed);
      zFit.property('disabled', !zoomed);
      zIn.property('disabled', k >= 15.99);
      host.classList.toggle('zoomed', zoomed);
      const base = state.view === 'globe' ? 'Ziehen zum Drehen' : state.view === 'leg' ? 'Ringe: halbe und volle Leg-Distanz' : '';
      hud.text([base, zoomed ? `Zoom ${nf(Math.round(k * 10) / 10)}×` : ''].filter(Boolean).join(' · '));
    }

    // Maus: Strg/⌘ + Mausrad oder Trackpad-Geste zoomt, Ziehen verschiebt, Doppelklick vergrößert (mit Umschalt: verkleinert).
    // Das Mausrad allein scrollt weiter die Seite. Touch: ein Finger scrollt die Seite, zwei Finger zoomen und verschieben.
    // Globus: Zoom ändert nur die Größe, Ziehen dreht ihn wie bisher.
    const zoom = d3.zoom()
      .scaleExtent([1, 16])
      .extent([[0, 0], [W, H]])
      .translateExtent([[0, 0], [W, H]])
      .filter(ev => {
        if (ev.type === 'wheel') return ev.ctrlKey || ev.metaKey;
        if (ev.type.startsWith('touch')) return !!ev.touches && ev.touches.length >= 2;
        if (ev.type === 'mousedown') return state.view !== 'globe' && !ev.button;
        return !ev.button;
      })
      // Trackpad-Gesten liefern kleine Werte mit Strg, ein Mausrad-Raster rund 100: beides soll sich gleich anfühlen
      .wheelDelta(ev => -ev.deltaY * (ev.deltaMode === 1 ? 0.05 : ev.deltaMode ? 1 : 0.003) * (ev.deltaMode === 0 && Math.abs(ev.deltaY) < 40 ? 5 : 1))
      .on('start', ev => { pinching = !!(ev.sourceEvent && ev.sourceEvent.touches && ev.sourceEvent.touches.length > 1); })
      .on('zoom', () => { schedule(); zoomUi(); })
      .on('end', () => { pinching = false; });
    svg.call(zoom);
    const motion = () => (window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 250);
    const zoomBy = f => svg.transition().duration(motion()).call(zoom.scaleBy, f);
    const zoomReset = () => svg.transition().duration(motion()).call(zoom.transform, d3.zoomIdentity);
    zIn.on('click', () => zoomBy(1.6));
    zOut.on('click', () => zoomBy(1 / 1.6));
    zFit.on('click', zoomReset);
    let hintTimer = 0;
    svg.on('wheel.hint', ev => {
      if (ev.ctrlKey || ev.metaKey) return;
      hint.classed('show', true);
      clearTimeout(hintTimer);
      hintTimer = setTimeout(() => hint.classed('show', false), 1400);
    }, { passive: true });

    svg.call(d3.drag()
      .filter(ev => state.view === 'globe' && !ev.button && !(ev.touches && ev.touches.length > 1))
      .on('drag', ev => {
        if (pinching) return;
        const k = 180 / Math.PI / proj.scale();
        globeCenter = [center[0] - ev.dx * k, Math.max(-85, Math.min(85, center[1] + ev.dy * k))];
        schedule();
      }));

    return { draw, styleLegs, recenter() { globeCenter = null; }, zoomBy, zoomReset };
  })();

  // ---------- Auswahl ----------
  function updateNav() {
    $('#prev').disabled = state.idx === 0;
    $('#next').disabled = state.idx === LEGS.length - 1;
    const sel = $('#jump');
    if (sel.value !== cur().id) sel.value = cur().id;
    $('#nav-position').textContent = `Etappe ${state.idx + 1} von ${LEGS.length} · ${cur().k === 'h' ? 'H160' : 'A320'}`;
    $('#resume').disabled = LEGS.every(l => state.flown.has(l.id));
    $('#resume').textContent = $('#resume').disabled ? 'Alle Legs geflogen' : 'Erstes offenes Leg';
  }
  function reveal(el, { focus = true, anchor = el } = {}) {
    if (focus) el.focus({ preventScroll: true });
    const bar = $('.stepbar');
    const offset = getComputedStyle(bar).position === 'sticky' ? bar.getBoundingClientRect().height : 0;
    const top = anchor.getBoundingClientRect().top + window.scrollY - offset - 16;
    window.scrollTo({ top: Math.max(0, top), behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
  function stepLeg(delta) {
    const control = document.activeElement;
    select(state.idx + delta);
    if (control && control.disabled) $('#jump').focus({ preventScroll: true });
    reveal($('.grid'), { focus: false });
  }
  function openBriefing(id) {
    selectId(id);
    reveal($('.grid'));
  }
  function findLeg() {
    showTab('plan');
    reveal($('#q'), { anchor: $('#book') });
  }
  function markPlanSel() {
    $$('#plan tbody tr.sel').forEach(r => r.classList.remove('sel'));
    const row = $(`#plan tbody tr[data-leg="${CSS.escape(cur().id)}"]`);
    if (row) row.classList.add('sel');
  }
  function select(i, scrollRail = true) {
    state.idx = Math.max(0, Math.min(LEGS.length - 1, i));
    try { history.replaceState(null, '', '#' + cur().id); } catch (e) { /* ignorieren */ }
    Chart.recenter();
    renderProse();
    renderPanels();
    renderXcards();
    updateRail(scrollRail);
    Chart.draw();
    renderTracks();
    markPlanSel();
    updateNav();
  }
  function selectId(id) { if (legIdx.has(id)) select(legIdx.get(id)); }

  function refreshProgress() {
    const focused = document.activeElement;
    const restoreFlownFocus = focused && focused.id === 'flownbtn';
    const restoreDoneFocus = focused && focused.dataset && focused.dataset.done;
    const previousDoneIds = restoreDoneFocus ? $$('#plan input[data-done]').map(cb => cb.dataset.done) : [];
    updateRail(false);
    renderTracks();
    renderProse();
    renderXcards();
    Chart.styleLegs();
    $$('#plan input[data-done]').forEach(cb => { cb.checked = state.flown.has(cb.dataset.done); });
    if (state.flt === 'open' || state.flt === 'done') renderPlan();
    if (state.tab === 'hl') renderHL();
    if (state.tab === 'cat') renderCat();
    if (state.tab === 'data') renderData();
    updateNav();
    if (restoreFlownFocus) $('#flownbtn').focus({ preventScroll: true });
    if (restoreDoneFocus) restorePlanFocus(restoreDoneFocus, previousDoneIds);
  }
  function restorePlanFocus(id, previousIds) {
    const remaining = new Map($$('#plan input[data-done]').map(cb => [cb.dataset.done, cb]));
    const index = previousIds.indexOf(id);
    const candidates = [id, ...previousIds.slice(index + 1), ...previousIds.slice(0, index).reverse()];
    const target = candidates.map(key => remaining.get(key)).find(Boolean) || $('#clear-filters');
    target.focus({ preventScroll: remaining.has(id) });
  }

  // ---------- Flugplan ----------
  function passFilter(l) {
    const b = AP[l.t];
    switch (state.flt) {
      case 'open': return !state.flown.has(l.id);
      case 'done': return state.flown.has(l.id);
      case 'hl': return (b.level || 0) >= 1 && !(l.k === 'h' && l.t === XC[l.x].anchor);
      case 'owned': return b.sc.items.some(i => i.status === 'owned');
      case 'buy': return b.sc.items.some(i => i.status === 'buy');
      case 'freeware': return b.sc.items.some(i => i.status === 'freeware');
      case 'long': return l.o2;
      case 'heli': return l.k === 'h';
      case 'new': return !!l.nc;
      case 'trial': return !!l.trial;
      case 'unrated': return isUnrated(b);
      default: return true;
    }
  }
  function rowHtml(l) {
    const b = AP[l.t];
    const a = AP[l.f];
    const isH = l.k === 'h';
    const tag = isH ? (l.t === XC[l.x].target ? XC[l.x].tag : '') : (b.tag || '');
    return `<tr data-leg="${l.id}" class="${isH ? 'hx' : ''}${l.id === cur().id ? ' sel' : ''}">
      <td><label class="check-hit"><input type="checkbox" data-done="${l.id}"${state.flown.has(l.id) ? ' checked' : ''} aria-label="${esc(l.id)} als geflogen markieren"><span class="visually-hidden">${esc(l.id)} geflogen</span></label></td>
      <td class="num lft">${esc(legLabel(l))}</td>
      <td class="mono"><button type="button" class="route-link" data-go="${l.id}" aria-label="Briefing ${esc(l.id)}: ${esc(l.f)} nach ${esc(l.t)}">${esc(l.f)} → ${esc(l.t)}</button></td>
      <td><span class="dest">${esc(cityOf(b))}</span> <span class="cat${l.nc ? ' new' : ''}">${esc(CATN[b.cc])}${l.nc ? ' · neu' : ''}</span>${isH ? ` <span class="cat">ab ${esc(cityOf(a))}</span>` : ''}</td>
      <td class="num">${nf(l.nm)}</td>
      <td class="num${l.o2 ? ' long' : ''}">${hm(l.air)}</td>
      <td>${primaryBadge(b)}</td>
      <td>${l.trial ? '<span class="tag trial">Sonderetappe</span> ' : ''}${tag ? `<span class="tag">${esc(tag)}</span>` : ''}${isH ? ' <span class="cat">H160</span>' : ''}</td>
    </tr>`;
  }
  function renderPlan() {
    const terms = searchText(state.q).trim().split(/\s+/).filter(Boolean);
    const rows = [];
    let last = null;
    let n = 0;
    for (const l of LEGS) {
      if (state.ch !== 'all' && l.ch !== state.ch) continue;
      if (!passFilter(l)) continue;
      if (terms.length) {
        const a = AP[l.f];
        const b = AP[l.t];
        const hay = searchText(`${l.id} ${l.f} ${l.t} ${a.n} ${b.n} ${cityOf(a)} ${cityOf(b)} ${CAT_SEARCH[a.cc]} ${CAT_SEARCH[b.cc]} ${CH[chIdx.get(l.ch)].title} ${l.k === 'h' ? 'H160' : 'A320'}`);
        if (!terms.every(term => hay.includes(term))) continue;
      }
      if (l.ch !== last) {
        last = l.ch;
        const c = CH[chIdx.get(l.ch)];
        rows.push(`<tr class="grp"><td colspan="8"><b>${c.id}</b> · ${esc(c.title)} — ${esc(c.sub)}</td></tr>`);
      }
      rows.push(rowHtml(l));
      n++;
    }
    $('#plan tbody').innerHTML = rows.join('') || '<tr class="empty-row"><td colspan="8"><strong>Keine passenden Legs</strong><p>Suchbegriff ändern oder die Filter zurücksetzen, um wieder alle Etappen zu sehen.</p></td></tr>';
    const filtered = terms.length > 0 || state.flt !== 'all' || state.ch !== 'all';
    $('#planinfo').textContent = `${n} von ${LEGS.length} Legs${filtered ? ' · Filter aktiv' : ''}`;
    $('#clear-filters').hidden = !filtered;
  }

  // ---------- Highlights ----------
  function renderHL() {
    const seen = new Set();
    const cards = [];
    for (const l of LEGS) {
      if (l.k === 'a') {
        const b = AP[l.t];
        if (b.level !== 2 || seen.has(b.i)) continue;
        seen.add(b.i);
        const done = state.flown.has(l.id);
        cards.push(`<article class="hcard${done ? ' done' : ''}"><div class="ht"><span>Kapitel ${l.ch} · ${l.id}</span><span class="tagc">${b.trial ? 'Sonderetappe' : esc(b.tag || '')}</span></div>
          <h3>${esc(cityOf(b))}<small>${esc(b.i)}</small></h3><p>${esc(b.hl)}</p>
          <div class="foot">${primaryBadge(b)}<button type="button" class="btn small" data-go="${l.id}">${done ? '✓ geflogen' : 'Zum Leg →'}</button></div></article>`);
      } else {
        const x = XC[l.x];
        if (x.kind !== 'bonus' || l.t !== x.target || seen.has('x' + x.id)) continue;
        seen.add('x' + x.id);
        const done = state.flown.has(l.id);
        const t = AP[x.target];
        cards.push(`<article class="hcard heli${done ? ' done' : ''}"><div class="ht"><span>Kapitel ${l.ch} · H160-Bonus</span><span class="tagc">${esc(x.tag)}</span></div>
          <h3>${esc(x.title)}<small>${esc(t.i)}</small></h3><p>${esc(x.brief)}</p>
          <div class="foot">${primaryBadge(t)}<button type="button" class="btn small" data-go="${l.id}">${done ? '✓ geflogen' : 'Zum Ausflug →'}</button></div></article>`);
      }
    }
    $('#panel-hl').innerHTML = `<h2>Die Anflüge, für die sich die Reise lohnt</h2>
      <p class="lede">${cards.length} Top-Highlights in Flugreihenfolge – mit dem Grund, warum sie auf der Route sind, und der passenden Szenerie. Drei davon sind Sonderetappen, die du vorher im Fenix testest.</p>
      <div class="cards">${cards.join('')}</div>`;
  }

  // ---------- Szenerien ----------
  function renderScn() {
    const order = [];
    const seen = new Set();
    const push = (i, lid) => { if (!seen.has(i)) { seen.add(i); order.push([i, lid]); } };
    push(LEGS[0].f, LEGS[0].id);
    LEGS.forEach(l => push(l.t, l.id));
    const buy = [];
    const req = [];
    const free = [];
    const opt = [];
    const candidates = [];
    const hand = [];
    const stdok = [];
    let unrated = 0;
    for (const [i, lid] of order) {
      const a = AP[i];
      if (isUnrated(a)) unrated++;
      for (const it of a.sc.items) {
        if (it.status === 'buy') buy.push([a, it, lid]);
        else if (it.status === 'freeware') (it.required ? req : free).push([a, it, lid]);
        else if (it.status === 'optional') opt.push([a, it, lid]);
        else if (it.status === 'candidate') candidates.push([a, it, lid]);
        else if (it.status === 'hand') hand.push([a, it, lid]);
        else if (it.status === 'stdok') stdok.push([a, it, lid]);
      }
    }
    const link = it => it.url ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">${esc(it.product)} ↗</a>` : esc(it.product);
    const scard = ([a, it, lid]) => `<article class="scard"><div class="sh"><b>${esc(a.i)}</b><span>${esc(cityOf(a))} · ${lid}</span></div>
      <h3>${link(it)}</h3><div class="meta"><span>${esc(it.dev)}</span>${it.rating ? `<span>★ ${esc(it.rating)}</span>` : ''}${it.price ? `<span>${esc(it.price)}</span>` : ''}</div>
      <p>${esc(it.why || '')}</p>${it.alt ? `<p>Alternative: <a href="${esc(it.alt.url)}" target="_blank" rel="noopener">${esc(it.alt.name)} ↗</a></p>` : ''}${installationNotes(it)}
      <div><button type="button" class="btn small" data-go="${lid}">Zum Leg →</button></div></article>`;
    const rows = list => `<div class="scroll"><table><thead><tr><th>ICAO</th><th>Ort</th><th>Produkt</th><th>Entwickler</th><th>Bewertung</th><th>Begründung</th><th>Leg</th></tr></thead><tbody>${list.map(([a, it, lid]) =>
      `<tr data-go="${lid}"><td class="mono">${esc(a.i)}</td><td>${esc(cityOf(a))}</td><td>${link(it)}</td><td>${esc(it.dev)}</td><td class="mono">${esc(it.rating || '')}</td><td>${esc(it.why || '')}${it.alt ? ` Alternative: <a href="${esc(it.alt.url)}" target="_blank" rel="noopener">${esc(it.alt.name)} ↗</a>` : ''}${installationNotes(it)}</td><td class="mono"><button type="button" class="route-link" data-go="${lid}" aria-label="Briefing ${lid} öffnen">${lid}</button></td></tr>`).join('')}</tbody></table></div>`;

    const owned = D.owned.map(o => {
      const lid = LEGS.find(l => l.t === o.icao || l.f === o.icao);
      return `<tr${lid ? ` data-go="${lid.id}"` : ''}><td class="mono">${esc(o.icao)}</td><td>${esc(o.name)}</td><td>${esc(o.dev)}</td><td>${o.used ? (lid ? `<button type="button" class="route-link" data-go="${lid.id}" aria-label="Briefing ${lid.id} öffnen">${lid.id}</button>` : '✓') : '<span class="long">nicht in der Tour</span>'}</td><td>${esc(o.note || '')}</td></tr>`;
    }).join('');
    const usedN = D.owned.filter(o => o.used).length;
    const openChecks = Object.values(AP).filter(a => a.simCheck && a.simCheck.status === 'unconfirmed');

    const checklist = CH.map(c => {
      const idents = new Set();
      const fallbackIdents = new Set();
      c.legs.forEach(id => {
        const l = LEGS[legIdx.get(id)]; idents.add(l.f); idents.add(l.t);
        const fallback = l.x && XC[l.x] && XC[l.x].fallback;
        if (fallback) [fallback.anchor, fallback.target].forEach(i => { if (AP[i]) fallbackIdents.add(i); });
      });
      const items = [];
      const preparation = [];
      idents.forEach(i => {
        AP[i].sc.items.forEach(it => {
          if (['owned', 'buy', 'freeware'].includes(it.status)) {
            const label = it.status === 'owned' ? `Eigene: ${it.dev}` : `${BADGE[stOf(it)]}${it.required ? ' (Pflicht)' : ''}: ${it.product} · ${it.dev}`;
            items.push(`<li><span class="mono">${esc(i)}</span> – ${it.url ? `<a href="${esc(it.url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>` : esc(label)}${installationNotes(it)}</li>`);
          } else if (['hand', 'stdok'].includes(it.status) && (it.dependencies?.length || it.installNote)) {
            preparation.push(`<li><span class="mono">${esc(i)}</span> – Vorbereitung${installationNotes(it)}</li>`);
          }
        });
      });
      const nNew = items.filter(s => !s.includes('Eigene:')).length;
      const simChecks = Array.from(new Set([...idents, ...fallbackIdents])).filter(i => AP[i].simCheck && AP[i].simCheck.status === 'unconfirmed');
      return `<details class="chk"><summary><b>${c.id}</b><span>${esc(c.title)}</span><em>${items.length ? `${items.length} Hauptpakete · ${nNew} zusätzliche Empfehlungen` : 'keine empfohlenen Downloads'}${simChecks.length ? ` · ${simChecks.length} Sim-Prüfung(en) offen` : ''}</em></summary>${items.length ? `<ul>${items.join('')}</ul>` : ''}${preparation.length ? `<ul>${preparation.join('')}</ul>` : ''}${simChecks.map(i => `<div class="check-airport"><b>${esc(i)}${!idents.has(i) ? ' · Ausweichziel' : ''}</b>${simCheckNote(AP[i])}</div>`).join('')}</details>`;
    }).join('');

    $('#panel-scn').innerHTML = `<h2>Szenerien: wenig kaufen, gezielt installieren</h2>
      <p class="lede">Priorität wie gewünscht: deine Sammlung, dann handgefertigte Airports aus Basis-Sim und World Updates, dann starke Freeware. Gekauft wird nur, wo ein Add-on einen besonderen Anflug spürbar besser macht. ${unrated ? `Für ${unrated} Airports ließ sich keine belastbare Quelle prüfen – sie bleiben als „ungeprüft“ markiert, nicht als „Standard reicht“.` : 'Jeder Airport der Tour ist recherchiert.'}</p>
      ${D.research ? `<p class="lede small">Recherche vom ${esc(fmtDate(D.research.date))} über FSAddonCompare und flightsim.to. ${esc(D.research.rules)} „Angebot recherchiert“ beschreibt den Add-on-Vergleich; eine eigene Prüfung der Standardszenerie im Simulator ist damit nicht verbunden.</p>` : ''}
      ${openChecks.length ? `<h3 class="sect">Offene Simulatorprüfungen <small>${openChecks.length} Airports einschließlich Ausweichziele</small></h3>${openChecks.map(a => `<div class="check-airport"><b>${esc(a.i)} · ${esc(cityOf(a))}</b>${simCheckNote(a)}</div>`).join('')}` : ''}
      <h3 class="sect">Kauf-Tipps <small>${buy.length} Produkte · rund 80–90 € zusammen</small></h3>
      <div class="sgrid">${buy.map(scard).join('')}</div>
      <h3 class="sect">Pflicht-Freeware <small>ohne diese Pakete fehlen Bahn oder Navdaten</small></h3>
      ${rows(req)}
      <h3 class="sect">Empfohlene Freeware <small>${free.length} Pakete</small></h3>
      ${rows(free)}
      <h3 class="sect">Freeware zum Prüfen <small>${candidates.length} Kandidaten · noch keine feste Empfehlung</small></h3>
      ${rows(candidates)}
      <h3 class="sect">Kaufoptionen &amp; beobachten <small>${opt.length} Produkte · Begründung und Einschränkungen beachten</small></h3>
      ${rows(opt)}
      <h3 class="sect">Angebot recherchiert <small>${stdok.length} Airports · keine feste Add-on-Empfehlung</small></h3>
      <details class="chk"><summary><b>${stdok.length}</b><span>Begründungen anzeigen</span><em>FSAddonCompare und flightsim.to je Airport recherchiert</em></summary>
      <div class="scroll"><table><thead><tr><th>ICAO</th><th>Ort</th><th>Begründung</th><th>Leg</th></tr></thead><tbody>${stdok.map(([a, it, lid]) =>
        `<tr data-go="${lid}"><td class="mono">${esc(a.i)}</td><td>${esc(cityOf(a))}</td><td>${esc(it.why)}</td><td class="mono"><button type="button" class="route-link" data-go="${lid}" aria-label="Briefing ${lid} öffnen">${lid}</button></td></tr>`).join('')}</tbody></table></div></details>
      <h3 class="sect">Deine Sammlung <small>${usedN} von ${D.owned.length} in der Tour</small></h3>
      <div class="scroll"><table><thead><tr><th>ICAO</th><th>Airport</th><th>Hersteller</th><th>Leg</th><th>Hinweis</th></tr></thead><tbody>${owned}</tbody></table></div>
      <h3 class="sect">Handgefertigt in MSFS 2024 <small>${hand.length} Airports – kein Add-on nötig</small></h3>
      <div class="chips">${hand.map(([a, it, lid]) => `<button type="button" class="xleg" data-go="${lid}">${esc(a.i)} · ${esc(it.product)}</button>`).join('')}</div>
      <h3 class="sect">Download-Checkliste pro Kapitel <small>vor dem Kapitel installieren</small></h3>
      ${checklist}`;
  }

  // ---------- Kategorien ----------
  const VOL_NEXT = { open: 'credited', credited: 'not_credited', not_credited: 'open' };
  const manualVol = code => {
    const m = state.vstates.get(code);
    return m && m.t > state.epochs.volanta ? m.s : 'open';
  };
  function renderCat() {
    const v = volanta();
    const stateOf = c => (v.ok.has(c.code) ? 'ok' : v.no.has(c.code) ? 'no' : v.reached.has(c.code) ? 'reached' : 'open');
    const list = D.cats.filter(c => state.cat === 'all' || stateOf(c) === state.cat);
    const btn = (val, t) => `<button type="button" class="btn small${state.cat === val ? ' primary' : ''}" data-catf="${val}">${t}</button>`;
    $('#panel-cat').innerHTML = `<h2>245 Volanta-Kategorien</h2>
      <p class="lede">Laut Flugplan erreicht: ${v.reached.size}. In Volanta bestätigt: ${v.ok.size}, nicht gewertet: ${v.no.size}. Ein Häkchen am Leg heißt nur „geflogen“ – ob Volanta die Kategorie anerkennt, trägst du rechts an der Kachel ein, oder es kommt aus dem Debriefing.</p>
      <div class="toolbar">${btn('all', 'Alle')}${btn('open', 'Offen')}${btn('reached', 'Erreicht, unbestätigt')}${btn('ok', 'Bestätigt')}${btn('no', 'Nicht gewertet')}</div>
      <div class="catgrid">${list.map(c => {
        const m = manualVol(c.code);
        const lbl = m === 'credited' ? 'Volanta ✓' : m === 'not_credited' ? 'Volanta ✗' : 'Volanta ?';
        return `<div class="catc ${stateOf(c)}">
          <button type="button" class="catgo" data-go="${c.first}"><b>${c.code}</b><span>${esc(c.name)}</span>
            <small>${esc(c.apts.slice(0, 3).join(' · '))}${c.via === 'h' ? ' · H160' : ''} · ${c.first}</small></button>
          <button type="button" class="vstat${m === 'credited' ? ' ok' : m === 'not_credited' ? ' no' : ''}" data-vol="${c.code}" title="Volanta-Status von Hand setzen: ? → ✓ → ✗" aria-label="Volanta-Status ${esc(c.name)}">${lbl}</button>
        </div>`;
      }).join('')}</div>`;
  }

  // ---------- Neu in V2 ----------
  function renderNew() {
    const s = D.stats;
    const v = s.v1;
    const row = (k, a, b) => `<tr><td>${esc(k)}</td><td>${a}</td><td>${b}</td></tr>`;
    $('#panel-new').innerHTML = `<h2>Was sich gegenüber V1 geändert hat</h2>
      <p class="lede">Gleiche Aufgabe, bessere Route: alle 245 Kategorien, weniger Leerlauf, mehr Anflug-Highlights, keine Twin Otter und nur Flughäfen im Betrieb. Drei Stopps sind Sonderetappen, die du vorher im Fenix testest – mit Ausweichplan.</p>
      <div class="scroll"><table class="cmp"><thead><tr><th>Kennzahl</th><th>V1</th><th>V2</th></tr></thead><tbody>
        ${row('Legs gesamt', nf(v.legs), nf(s.legs))}
        ${row('davon A320', nf(v.a320), nf(s.a320.legs))}
        ${row('davon H160', nf(v.h160legs), nf(s.h160.legs))}
        ${row('davon Twin Otter', nf(v.twinOtter), '0')}
        ${row('Flugzeit gesamt', `${nf(Math.round(v.air / 60))} h`, `${nf(Math.round(s.air / 60))} h`)}
        ${row('Legs über 2 Stunden', nf(v.over2h), nf(s.over2h))}
        ${row('Eigene Szenerien in der Hauptroute', `${v.ownedMain}`, `${s.ownedMain}`)}
        ${row('Eigene Szenerien inkl. Bonus-Ausflüge', `${v.ownedUsed} / 44`, `${s.ownedUsed} / ${s.ownedTotal}`)}
        ${row('Szenerie ohne eigene Recherche', `${v.default} (als „prüfen“)`, s.unrated ? `${s.unrated} (klar „ungeprüft“)` : '0 – jeder Airport recherchiert')}
        ${row('Sonderetappen mit Testcheckliste', '–', `${s.trials.length}`)}
        ${row('Geschlossene Flughäfen', '1 (Atarot)', '0')}
      </tbody></table></div>
      <div class="chg">${D.changes.map(c => `<article><div class="area">${esc(c.area)}</div><h3>${esc(c.title)}</h3><p>${esc(c.text)}</p><div class="eff">${esc(c.effect)}</div></article>`).join('')}</div>`;
  }

  // ---------- Daten & Reset ----------
  function renderData() {
    const where = syncMode === 'cloud'
      ? 'Dein Fortschritt liegt in der Datenbank der Online-Version und ist auf allen Geräten gleich. Dieser Browser hält zusätzlich eine Kopie.'
      : IS_ARTIFACT
        ? 'Die Cloud-Synchronisierung ist gerade nicht verbunden – Änderungen landen vorerst nur in diesem Browser und werden beim nächsten Verbinden zusammengeführt.'
        : 'Diese lokale Datei speichert deinen Fortschritt nur in diesem Browser. Für die Synchronisierung zwischen Geräten die Online-Version nutzen; hier kannst du sichern und wieder einlesen.';
    $('#data-where').textContent = `${where} Aktuell: ${state.flown.size} Legs geflogen.`;
    const dbx = $('#rs-debriefs');
    dbx.disabled = syncMode !== 'cloud';
    if (dbx.disabled) dbx.checked = false;
  }
  function exportJson() {
    return JSON.stringify({
      app: 'weltreise-edlv', version: 3, exported: today(),
      marks: Object.fromEntries(state.marks), vstates: Object.fromEntries(state.vstates), epochs: state.epochs,
    }, null, 1);
  }
  async function doReset() {
    const progress = $('#rs-progress').checked;
    const vol = $('#rs-volanta').checked;
    const deb = $('#rs-debriefs').checked && !!db;
    if (!progress && !vol && !deb) { toast('Nichts ausgewählt.'); return; }
    const now = Date.now();
    if (progress) {
      state.epochs.progress = Math.max(now, state.epochs.progress + 1, ...Array.from(state.marks.values(), m => m.t));
      for (const [id, m] of state.marks) if (m.t <= state.epochs.progress) state.marks.delete(id);
    }
    if (vol) {
      state.epochs.volanta = Math.max(now, state.epochs.volanta + 1, ...Array.from(state.vstates.values(), m => m.t));
      for (const [c, m] of state.vstates) if (m.t <= state.epochs.volanta) state.vstates.delete(c);
    }
    rebuildFlown();
    saveLocal();
    if (progress || vol) pushEpochs();
    if (deb) {
      try {
        const snap = await db.collection('debriefs').get();
        for (const d of snap.docs) await db.collection('debriefs').doc(d.id).delete();
      } catch (e) { toast('Debriefings in der Cloud konnten nicht gelöscht werden.'); }
    }
    refreshProgress();
    renderPlan();
    toast('Zurückgesetzt.');
  }

  function showTab(tab) {
    state.tab = tab;
    saveLocal();
    $$('.tab').forEach(t => {
      t.setAttribute('aria-selected', String(t.dataset.tab === tab));
      t.tabIndex = t.dataset.tab === tab ? 0 : -1;
    });
    $$('.panel').forEach(p => { p.hidden = p.id !== `panel-${tab}`; });
    if (tab === 'plan') renderPlan();
    if (tab === 'hl') renderHL();
    if (tab === 'scn') renderScn();
    if (tab === 'cat') renderCat();
    if (tab === 'new') renderNew();
    if (tab === 'data') renderData();
  }

  // ---------- Export / Import ----------
  let downloads = null;
  async function offerFile(name, text, mime) {
    if (hasRuntime) {
      if (downloads === null) {
        try { downloads = (await window.claude.use('downloads')) || false; } catch (e) { downloads = false; }
      }
      if (downloads) {
        try { await downloads.save({ filename: name, data: text }); toast('Datei übergeben.'); } catch (e) {
          if (!e || e.code !== 'declined') toast('Download ist hier gerade nicht möglich.');
        }
        return;
      }
      toast('Download ist in dieser Ansicht nicht verfügbar.');
      return;
    }
    const url = URL.createObjectURL(new Blob([text], { type: mime }));
    const a = document.createElement('a');
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function csv() {
    const head = ['Leg', 'Kapitel', 'Typ', 'Von', 'Nach', 'Ziel', 'Kategorie', 'Neue Kategorie', 'NM', 'Flugzeit', 'Blockzeit', 'Szenerie', 'Produkt', 'Sonderetappe', 'Geflogen'];
    const q = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const lines = LEGS.map(l => {
      const b = AP[l.t];
      const it = b.sc.items[0];
      return [l.id, l.ch, l.k === 'h' ? 'H160' : 'A320', l.f, l.t, cityOf(b), CATN[b.cc], l.nc ? 'ja' : '', l.nm, hm(l.air), l.blk ? hm(l.blk) : '',
        BADGE[stOf(it)], it.product ? `${it.product}${it.dev ? ' · ' + it.dev : ''}` : (it.dev || ''), l.trial ? 'ja' : '', state.flown.get(l.id) || ''].map(q).join(';');
    });
    return '﻿' + [head.map(q).join(';'), ...lines].join('\r\n');
  }
  function applyImport(o) {
    let n = 0;
    let nv = 0;
    const mark = (id, at) => {
      if (state.flown.has(id)) return;
      const prev = state.marks.get(id);
      state.marks.set(id, { on: true, at: at || today(), t: stamp(Math.max(state.epochs.progress, prev ? prev.t : 0)) });
      pushMark(id);
      n++;
    };
    if (o && o.marks && typeof o.marks === 'object') {
      // Wiederherstellung: Was in der Sicherung wirksam geflogen bzw. bestätigt war, wird als neue Änderung
      // übernommen – auch nach einem Reset. Bereits geflogene Legs bleiben (die Sicherung ergänzt nur).
      const bp = Number(o.epochs && o.epochs.progress) || 0;
      const bv = Number(o.epochs && o.epochs.volanta) || 0;
      for (const [k, v] of Object.entries(o.marks)) {
        const m = cleanMark(v);
        if (m && legIdx.has(k) && m.on && m.t > bp) mark(k, m.at);
      }
      if (o.vstates && typeof o.vstates === 'object') {
        for (const [k, v] of Object.entries(o.vstates)) {
          if (!CATN[k] || !v || typeof v !== 'object' || !(legacyT(v.t) > bv)) continue;
          const st = ['credited', 'not_credited'].includes(v.s) ? v.s : 'open';
          if (manualVol(k) === st) continue;
          const prev = state.vstates.get(k);
          state.vstates.set(k, { s: st, t: stamp(Math.max(state.epochs.volanta, prev ? prev.t : 0)) });
          pushVol(k);
          nv++;
        }
      }
    } else if (o && o.flown && typeof o.flown === 'object' && !Array.isArray(o.flown)) {
      for (const [k, v] of Object.entries(o.flown)) if (legIdx.has(k)) mark(k, String(v || ''));
    } else if (o && (Array.isArray(o.done) || Array.isArray(o.xDone))) {
      // V1-Sicherung: über Start und Ziel den passenden V2-Leg finden
      const pairs = [...(o.done || []).map(String), ...(o.xDone || []).map(String)].map(id => D.v1pairs[id]).filter(Boolean);
      for (const p of pairs) {
        const [f, to] = p.split('>');
        const l = LEGS.find(x => x.f === f && x.t === to && !state.flown.has(x.id));
        if (l) mark(l.id);
      }
    }
    rebuildFlown();
    saveLocal();
    refreshProgress();
    renderPlan();
    const parts = [];
    if (n) parts.push(`${n} ${n === 1 ? 'Leg' : 'Legs'} als geflogen`);
    if (nv) parts.push(`${nv} Volanta-${nv === 1 ? 'Status' : 'Status'}`);
    toast(parts.length ? `Übernommen: ${parts.join(' und ')}.` : 'Die Sicherung enthält nichts, was noch fehlt.');
  }

  // ---------- Ereignisse ----------
  function wire() {
    document.addEventListener('click', ev => {
      const t = ev.target;
      const pip = t.closest('.pip, .xleg[data-leg]');
      if (pip) { selectId(pip.dataset.leg); return; }
      const vol = t.closest('[data-vol]');
      if (vol) { setVol(vol.dataset.vol, VOL_NEXT[manualVol(vol.dataset.vol)] || 'credited'); return; }
      const go = t.closest('[data-go]');
      if (go && !t.closest('a')) {
        openBriefing(go.dataset.go);
        return;
      }
      const catf = t.closest('[data-catf]');
      if (catf) { state.cat = catf.dataset.catf; renderCat(); return; }
      if (t.closest('#flownbtn')) { toggleFlown(cur().id); return; }
      if (t.closest('#dbtpl')) {
        const text = debriefTemplate(cur());
        const host = $('#dbhost');
        const fallback = () => {
          const ta = document.createElement('textarea');
          ta.className = 'copyarea';
          ta.rows = 10;
          ta.readOnly = true;
          ta.value = text;
          host.appendChild(ta);
          ta.focus();
          ta.select();
          toast('Vorlage markiert – mit Strg+C kopieren.');
        };
        try {
          navigator.clipboard.writeText(text).then(() => toast('Vorlage kopiert – im Chat einfügen.'), fallback);
        } catch (e) { fallback(); }
      }
    });
    $$('.seg button').forEach(b => b.addEventListener('click', () => {
      state.view = b.dataset.view;
      saveLocal();
      $$('.seg button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      Chart.recenter();
      Chart.draw();
    }));
    $$('.tab').forEach(t => t.addEventListener('click', () => showTab(t.dataset.tab)));
    $('.tabs').addEventListener('keydown', ev => {
      const tabs = $$('.tab');
      const current = tabs.indexOf(ev.target.closest('.tab'));
      if (current < 0 || ev.altKey || ev.ctrlKey || ev.metaKey) return;
      let next;
      if (ev.key === 'ArrowRight') next = (current + 1) % tabs.length;
      else if (ev.key === 'ArrowLeft') next = (current + tabs.length - 1) % tabs.length;
      else if (ev.key === 'Home') next = 0;
      else if (ev.key === 'End') next = tabs.length - 1;
      else return;
      ev.preventDefault();
      showTab(tabs[next].dataset.tab);
      tabs[next].focus();
    });
    $('#rail').addEventListener('keydown', ev => {
      const pip = ev.target.closest('.pip');
      if (!pip || ev.altKey || ev.ctrlKey || ev.metaKey) return;
      const current = legIdx.get(pip.dataset.leg);
      let next;
      if (ev.key === 'ArrowRight') next = current + 1;
      else if (ev.key === 'ArrowLeft') next = current - 1;
      else if (ev.key === 'Home') next = 0;
      else if (ev.key === 'End') next = LEGS.length - 1;
      else return;
      ev.preventDefault();
      select(next);
      pipEl.get(cur().id).focus({ preventScroll: true });
    });
    $('.route-overview').addEventListener('toggle', () => {
      if ($('.route-overview').open) updateRail(true);
    });
    $('#plan tbody').addEventListener('click', ev => {
      const cb = ev.target.closest('input[data-done]');
      if (cb) { setFlown(cb.dataset.done, cb.checked); return; }
      const tr = ev.target.closest('tr[data-leg]');
      if (tr && !ev.target.closest('a, button, .check-hit, td:first-child')) openBriefing(tr.dataset.leg);
    });
    let qTimer = 0;
    $('#q').addEventListener('input', ev => {
      clearTimeout(qTimer);
      qTimer = setTimeout(() => { state.q = ev.target.value; renderPlan(); }, 150);
    });
    $('#clear-filters').addEventListener('click', () => {
      clearTimeout(qTimer);
      state.q = ''; state.flt = 'all'; state.ch = 'all';
      $('#q').value = ''; $('#flt').value = 'all'; $('#chsel').value = 'all';
      renderPlan();
      $('#q').focus();
    });
    // Filter „Szenerie ungeprüft“ nur anbieten, solange es ungeprüfte Airports gibt
    if (!D.stats.unrated) $('#flt option[value="unrated"]')?.remove();
    $('#flt').addEventListener('change', ev => { state.flt = ev.target.value; renderPlan(); });
    $('#chsel').addEventListener('change', ev => { state.ch = ev.target.value; renderPlan(); });
    $('#csv').addEventListener('click', () => offerFile('Weltreise-EDLV-V2-Flugplan.csv', csv(), 'text/csv'));
    const backup = () => offerFile(`Weltreise-EDLV-V2-Fortschritt-${today()}.json`, exportJson(), 'application/json');
    $('#backup').addEventListener('click', backup);
    $('#rs-backup').addEventListener('click', backup);
    $('#restore').addEventListener('change', async ev => {
      const f = ev.target.files && ev.target.files[0];
      if (!f) return;
      try { applyImport(JSON.parse(await f.text())); } catch (e) { toast('Die Datei konnte nicht gelesen werden.'); }
      ev.target.value = '';
    });
    const step = second => { $('#rs-step1').hidden = second; $('#rs-step2').hidden = !second; };
    $('#rs-go').addEventListener('click', () => step(true));
    $('#rs-no').addEventListener('click', () => step(false));
    $('#rs-yes').addEventListener('click', async () => { step(false); await doReset(); });
    $('#prev').addEventListener('click', () => stepLeg(-1));
    $('#next').addEventListener('click', () => stepLeg(1));
    $('#jump').addEventListener('change', ev => { selectId(ev.target.value); reveal($('.grid'), { focus: false }); });
    $('#resume').addEventListener('click', () => {
      const next = LEGS.find(l => !state.flown.has(l.id));
      if (next) openBriefing(next.id);
    });
    $('#find-leg').addEventListener('click', findLeg);
    $('.skip-link').addEventListener('click', ev => { ev.preventDefault(); findLeg(); });
    window.addEventListener('hashchange', () => {
      try {
        const id = decodeURIComponent(location.hash.slice(1));
        if (legIdx.has(id)) selectId(id);
      } catch (e) { /* Unvollständige URL-Kodierung ändert die Auswahl nicht. */ }
    });
    document.addEventListener('keydown', ev => {
      if (ev.defaultPrevented || ev.repeat || ev.altKey || ev.ctrlKey || ev.metaKey) return;
      if (ev.target.closest && ev.target.closest('input, select, textarea, summary, [contenteditable]:not([contenteditable="false"]), [role="tab"]')) return;
      if (ev.target !== document.body && !(ev.target.closest && ev.target.closest('.grid'))) return;
      if (ev.key === 'ArrowLeft') { select(state.idx - 1); ev.preventDefault(); }
      else if (ev.key === 'ArrowRight') { select(state.idx + 1); ev.preventDefault(); }
      else if (ev.key === 'g' || ev.key === 'G') toggleFlown(cur().id);
      else if (ev.key === '+' || ev.key === '=') { Chart.zoomBy(1.6); ev.preventDefault(); }
      else if (ev.key === '-' || ev.key === '_') { Chart.zoomBy(1 / 1.6); ev.preventDefault(); }
      else if (ev.key === '0') { Chart.zoomReset(); ev.preventDefault(); }
    });
  }

  function fillSelects() {
    $('#chsel').innerHTML = '<option value="all">Alle Kapitel</option>' + CH.map(c => `<option value="${c.id}">${c.id} · ${esc(c.title)}</option>`).join('');
    $('#jump').innerHTML = CH.map(c => `<optgroup label="${c.id} · ${esc(c.title)}">${c.legs.map(id => {
      const l = LEGS[legIdx.get(id)];
      return `<option value="${id}">${esc(legLabel(l))} · ${esc(l.f)} → ${esc(l.t)} · ${esc(cityOf(AP[l.t]))}${l.k === 'h' ? ' (H160)' : ''}</option>`;
    }).join('')}</optgroup>`).join('');
    $('#credits').textContent = `Stand ${D.meta.built} · ${D.meta.aircraft} + ${D.meta.heli} · Daten: OurAirports, Natural Earth · Flugzeiten sind Schätzungen ohne Wind.`;
    $('#sub').textContent = `V2 · ${nf(D.stats.legs)} Legs · ${nf(Math.round(D.stats.air / 60))} h · alle 245 Volanta-Kategorien · Fenix A320 + H160`;
    $('#time-formula').textContent = `A320: ${D.meta.formula.a320}; H160: ${D.meta.formula.h160}. Ohne Wind; keine verbindlichen Flugzeiten.`;
  }

  // ---------- Start ----------
  loadLocal();
  renderRail();
  fillSelects();
  $$('.seg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === state.view)));
  wire();
  let fromHash = '';
  try { fromHash = decodeURIComponent((location.hash || '').slice(1)); } catch (e) { /* Ungültiger Link: erstes offenes Leg verwenden. */ }
  const firstOpen = LEGS.findIndex(l => !state.flown.has(l.id));
  select(legIdx.has(fromHash) ? legIdx.get(fromHash) : Math.max(0, firstOpen));
  showTab(state.tab);
  setSync('local');
  initCloud();
})();
