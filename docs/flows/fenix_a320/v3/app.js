/* Fenix A320 Flow · V3 – App-Logik (ohne Bibliotheken, offline).
   Daten: <script id="flow-data"> aus flow-v3.json. Speicher: localStorage „fenix-a320-flow-v3“. */
(() => {
  'use strict';
  const D = JSON.parse(document.getElementById('flow-data').textContent);
  const LS_KEY = 'fenix-a320-flow-v3';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const cssq = s => (window.CSS && CSS.escape ? CSS.escape(s) : String(s).replace(/["\\]/g, '\\$&'));
  const pad2 = n => String(n).padStart(2, '0');
  const today = () => new Date().toISOString().slice(0, 10);
  const smooth = () => (matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth');

  // ---------- Indizes ----------
  const PH = new Map(D.phases.map(p => [p.id, p]));
  const byKind = k => D.phases.filter(p => p.kind === k);
  const FLOW = byKind('flow');
  const SPEC = byKind('special');
  const CLS = byKind('checklist');
  const REF = byKind('reference');
  const ITEM = new Map();
  D.phases.forEach(p => p.items.forEach(it => { if (it.id) ITEM.set(it.id, { p, it }); }));
  const FIELD = new Map(D.fields.map(f => [f.id, f]));
  const PROF = new Map(D.profile.map(f => [f.id, f]));
  const STAGE_OF = new Map();
  D.stages.forEach(s => s.phases.forEach(id => STAGE_OF.set(id, s)));
  const SRC = D.sources;
  const listOf = p => (p.kind === 'flow' ? FLOW : SPEC);
  const isView = id => PH.has(id) && ['flow', 'special'].includes(PH.get(id).kind);

  // ---------- Zustand & Speicher ----------
  const fresh = () => ({
    v: 1, view: FLOW[0].id, lastFlow: FLOW[0].id, mode: 'flight', tab: 'all', dim: false,
    checks: {}, data: {}, profile: Object.fromEntries(D.profile.map(f => [f.id, f.default])),
  });
  function sanitize(o) {
    if (!o || typeof o !== 'object' || o.v !== 1) return null;
    const s = fresh();
    let dropped = 0;
    for (const [id, st] of Object.entries(o.checks || {})) {
      if (ITEM.has(id) && (st === 'done' || st === 'na')) s.checks[id] = st; else dropped++;
    }
    for (const [k, v] of Object.entries(o.data || {})) {
      if (FIELD.has(k) && typeof v === 'string' && v.trim()) s.data[k] = v.slice(0, 16); else dropped++;
    }
    for (const [k, v] of Object.entries(o.profile || {})) {
      const f = PROF.get(k);
      if (f && f.options.some(op => op[0] === v)) s.profile[k] = v; else dropped++;
    }
    if (isView(o.view)) s.view = o.view;
    if (PH.has(o.lastFlow) && PH.get(o.lastFlow).kind === 'flow') s.lastFlow = o.lastFlow;
    if (o.mode === 'learn') s.mode = 'learn';
    if (['all', 'spec', 'cl', 'ref', 'new', 'data'].includes(o.tab)) s.tab = o.tab;
    s.dim = o.dim === true;
    Object.defineProperty(s, 'dropped', { value: dropped, enumerable: false });
    return s;
  }
  let S = fresh();
  let storeState = 'saved';
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) S = sanitize(JSON.parse(raw)) || fresh();
  } catch { storeState = 'session'; }
  let saveTimer = 0;
  function save() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      try { localStorage.setItem(LS_KEY, JSON.stringify(S)); storeState = 'saved'; } catch { storeState = 'session'; }
      renderStore();
    }, 150);
  }

  // ---------- Profil, Sichtbarkeit, Fortschritt ----------
  const matches = when => !when || Object.entries(when).every(([k, v]) => (Array.isArray(v) ? v.includes(S.profile[k]) : S.profile[k] === v));
  const visible = it => !!it.id && matches(it.when);
  const activeItems = p => p.items.filter(visible);
  function prog(p) {
    let total = 0, done = 0, na = 0;
    for (const it of p.items) {
      if (!visible(it)) continue;
      total++;
      const c = S.checks[it.id];
      if (c === 'done') done++; else if (c === 'na') na++;
    }
    return { total, done, na, fin: done + na, complete: total > 0 && done + na === total };
  }
  function sumProg(list) {
    return list.reduce((a, p) => {
      const g = prog(p);
      a.total += g.total; a.fin += g.fin; a.na += g.na; if (g.complete) a.phases++;
      return a;
    }, { total: 0, fin: 0, na: 0, phases: 0 });
  }
  const pct = (a, b) => Math.round((100 * a) / Math.max(1, b));

  // ---------- Text, Platzhalter, Badges ----------
  const profLabel = k => { const f = PROF.get(k); const op = f && f.options.find(o => o[0] === S.profile[k]); return op ? op[1] : ''; };
  const fieldVal = k => (PROF.has(k) ? profLabel(k) : (S.data[k] || '').trim());
  const bold = s => s.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  function fill(s) {
    return bold(esc(s || '')).replace(/\{\{(\w+)\}\}/g, (_, k) => {
      const v = fieldVal(k);
      return `<span class="fv${v ? '' : ' empty'}" data-ph="${k}">${v ? esc(v) : '___'}</span>`;
    });
  }
  const plain = s => String(s || '').replace(/\*\*(.+?)\*\*/g, '$1').replace(/\{\{(\w+)\}\}/g, (_, k) => fieldVal(k) || '___');
  const shorten = (s, n) => {
    s = String(s || '');
    if (s.length <= n) return s;
    const cut = s.lastIndexOf(' ', n);
    return s.slice(0, cut > n * 0.5 ? cut : n) + ' …';
  };
  const badge = src => (src ? `<span class="badge ${esc(src)}" title="${esc(SRC[src] ? SRC[src].text : '')}">${esc(SRC[src] ? SRC[src].label : src)}</span>` : '');
  const revTag = it => (it.rev ? `<span class="rev ${it.rev}" title="${it.rev === 'v3' ? 'In V3 neu oder geändert' : 'In V2 geändert'}">${it.rev.toUpperCase()}</span>` : '');
  const markHtml = id => {
    const c = S.checks[id];
    if (c === 'done') return '<span class="chkmark" role="img" aria-label="erledigt">✓</span>';
    if (c === 'na') return '<span class="namark" role="img" aria-label="nicht zutreffend">N/A</span>';
    return '';
  };

  // ---------- Kopf ----------
  function renderStore() {
    const el = $('#store');
    el.className = 'chip ' + storeState;
    el.lastElementChild.textContent = storeState === 'saved' ? 'Gespeichert' : 'Nur diese Sitzung';
    el.title = storeState === 'saved'
      ? 'Häkchen, Flugdaten und Profil liegen im Speicher dieses Browsers.'
      : 'Der Browser erlaubt kein Speichern – nach dem Schließen ist alles weg. Sicherung unter „Daten & Reset“.';
  }
  function renderHeader() {
    const f = sumProg(FLOW);
    const c = CLS.filter(p => prog(p).complete).length;
    $('#count').innerHTML = `<b>${f.fin}</b>/${f.total} Schritte · <b>${c}</b>/${CLS.length} Checklisten`;
    $('#prof-chip').textContent = `${profLabel('approach')} · T/O ${profLabel('toConf')} · LDG ${profLabel('ldgConf')}`;
    $('#dim').setAttribute('aria-pressed', String(S.dim));
    document.documentElement.classList.toggle('dim', S.dim);
    renderStore();
  }

  // ---------- Navigation ----------
  function posOf(id) { const p = PH.get(id); const list = listOf(p); return { p, list, i: list.indexOf(p) }; }
  function renderNav() {
    const { p, list, i } = posOf(S.view);
    const opt = (q, lbl) => `<option value="${q.id}">${lbl} · ${esc(q.title)}${prog(q).complete ? ' ✓' : ''}</option>`;
    const sel = $('#jump');
    sel.innerHTML = `<optgroup label="Normal Flow">${FLOW.map((q, k) => opt(q, pad2(k + 1))).join('')}</optgroup>`
      + `<optgroup label="Sonderverfahren">${SPEC.map((q, k) => opt(q, 'S' + pad2(k + 1))).join('')}</optgroup>`;
    sel.value = S.view;
    $('#nav-position').textContent = p.kind === 'flow'
      ? `Phase ${i + 1} von ${list.length} · ${STAGE_OF.get(p.id).title}`
      : `Sonderverfahren ${i + 1} von ${list.length}`;
    $('#prev').disabled = i <= 0;
    $('#next').disabled = i >= list.length - 1;
  }
  function renderRail() {
    const f = sumProg(FLOW);
    $('#sum-count').textContent = `${FLOW.length} Phasen · ${D.stages.length} Abschnitte`;
    $('#sum-prog').textContent = `${f.fin}/${f.total} Schritte · ${pct(f.fin, f.total)} %`;
    $('#rail').innerHTML = D.stages.map(st => {
      const ps = st.phases.map(id => PH.get(id));
      const g = sumProg(ps);
      const here = st.phases.includes(S.view) ? ' here' : '';
      const pips = ps.map(p => {
        const q = prog(p);
        const n = FLOW.indexOf(p) + 1;
        const now = p.id === S.view;
        return `<button type="button" class="pip${now ? ' now' : ''}${q.complete ? ' done' : ''}" data-go="${p.id}" title="${esc(p.title)} · ${q.fin}/${q.total}"`
          + ` aria-label="Phase ${n}: ${esc(p.title)}, ${q.fin} von ${q.total} erledigt"${now ? ' aria-current="step"' : ''}>`
          + `<span class="pip-label">${pad2(n)}</span><span class="fill" style="width:${pct(q.fin, q.total)}%"></span></button>`;
      }).join('');
      return `<div class="act${here}"><button type="button" class="chapter-link" data-go="${st.phases[0]}">${esc(st.title)} <b>${g.fin}/${g.total}</b></button><div class="pips">${pips}</div></div>`;
    }).join('');
  }

  // ---------- Briefing (links) ----------
  const NUMERIC = new Set(['v1', 'vr', 'v2', 'vapp', 'thr', 'acc', 'eoAcc', 'ta', 'qnhDep', 'qnhArr', 'sqk', 'apOff', 'tl', 'flex']);
  const fieldInput = k => {
    const f = FIELD.get(k);
    return `<label class="dfield"><span>${esc(f.label)}${f.unit ? ` <em>${esc(f.unit)}</em>` : ''}</span>`
      + `<input type="text" data-field="${k}" value="${esc(S.data[k] || '')}" placeholder="${esc(f.hint || '')}" autocomplete="off" spellcheck="false" maxlength="16" inputmode="${NUMERIC.has(k) ? 'numeric' : 'text'}"></label>`;
  };
  const profSeg = k => {
    const f = PROF.get(k);
    return `<div class="pf"><span>${esc(f.label)}</span><div class="seg" role="group" aria-label="${esc(f.label)}">`
      + f.options.map(([v, l]) => `<button type="button" data-prof="${k}" data-val="${esc(v)}" aria-pressed="${S.profile[k] === v}">${esc(l)}</button>`).join('')
      + '</div></div>';
  };
  function datacard(p) {
    const keys = (p.fields || []).filter(k => { const f = FIELD.get(k); return !f || !f.when || matches(f.when); });
    if (!keys.length) return '';
    const fields = keys.filter(k => FIELD.has(k));
    const profs = keys.filter(k => PROF.has(k));
    const grp = fields.length && FIELD.get(fields[0]).group === 'arr' ? 'Ankunft' : 'Abflug';
    const filled = fields.filter(k => fieldVal(k)).length;
    return `<div class="datacard"><div class="dc-title"><span>Flugdaten · ${grp}</span><b id="dc-count">${fields.length ? `${filled}/${fields.length}` : ''}</b></div>`
      + (fields.length ? `<div class="dc-grid">${fields.map(fieldInput).join('')}</div>` : '')
      + (profs.length ? `<div class="dc-prof">${profs.map(profSeg).join('')}</div>` : '')
      + '</div>';
  }
  function legmetaHtml(p, g) {
    const cl = (p.checklists || []).map(c => PH.get(c).title);
    return [p.zone && `<span>${esc(p.zone)}</span>`, `<span>${g.total} Schritte</span>`,
      cl.length && `<span>C/L ${esc(cl.join(' · '))}</span>`, g.complete && '<span class="ok">✓ erledigt</span>'].filter(Boolean).join('');
  }
  function actionsHtml(p, g, next) {
    const a = [];
    if (g.complete && next) a.push(`<button type="button" class="btn primary" data-go="${next.id}">Weiter: ${esc(next.title)} →</button>`);
    else if (!g.complete) a.push('<button type="button" class="btn primary" data-act="open">Nächster offener Schritt</button>');
    if (p.kind === 'special') a.push(`<button type="button" class="btn" data-go="${S.lastFlow}">Zurück zum Flow</button>`);
    if (g.fin) a.push('<button type="button" class="btn ghost" data-act="reset-phase">Phase zurücksetzen</button>');
    return a.join('');
  }
  function renderProse() {
    const { p, list, i } = posOf(S.view);
    const g = prog(p);
    const isF = p.kind === 'flow';
    const stage = isF ? STAGE_OF.get(p.id).title : 'Sonderverfahren';
    const profKeys = [...new Set(p.items.flatMap(it => (it.id && it.when ? Object.keys(it.when) : [])))];
    $('#prose').innerHTML = `
      <div class="eyebrow${isF ? '' : ' special'}">${esc(stage)} · ${isF ? 'Phase' : 'Karte'} ${pad2(i + 1)} / ${list.length}</div>
      <div class="legmeta" id="legmeta">${legmetaHtml(p, g)}</div>
      <h2 class="route-title">${esc(p.title)}</h2>
      ${p.note ? `<p class="claim${isF ? '' : ' special'}">${fill(p.note)}</p>` : ''}
      ${datacard(p)}
      <div class="actions" id="prose-actions">${actionsHtml(p, g, list[i + 1])}</div>
      ${profKeys.length ? `<div class="kicker"><span>Profil</span>${profKeys.map(k => `<span>${esc(PROF.get(k).label)} <b>${esc(profLabel(k))}</b></span>`).join('')}</div>` : ''}`;
  }

  // ---------- Stage (rechts): Schritte, Checkliste, Profil ----------
  function stepHtml(it, learn) {
    const c = S.checks[it.id];
    const id = esc(it.id);
    const det = `<div class="st-det" id="det-${id}"${learn ? '' : ' hidden'}>`
      + (it.detail ? `<p>${fill(it.detail)}</p>` : '')
      + `<div class="st-meta">${badge(it.src)}${revTag(it)}`
      + (it.link ? `<button type="button" class="btn small" data-cl="${it.link}">Checkliste ${esc(PH.get(it.link).title)}</button>` : '')
      + `<button type="button" class="btn small ghost" data-na="${id}">${c === 'na' ? 'Wieder zutreffend' : 'Nicht zutreffend'}</button></div></div>`;
    return `<li class="step t-${it.type}${c === 'done' ? ' done' : c === 'na' ? ' na' : ''}" data-row="${id}">`
      + `<label class="st-line"><input type="checkbox" data-check="${id}"${c === 'done' ? ' checked' : ''}${c === 'na' ? ' disabled' : ''}>`
      + `<span class="st-item">${fill(it.item)}${c === 'na' ? '<span class="na-tag">N/A</span>' : ''}</span><span class="st-dots" aria-hidden="true"></span><span class="st-state">${fill(it.state)}</span></label>`
      + `<button type="button" class="st-info${it.detail ? ' has' : ''}" data-info="${id}" aria-expanded="${learn}" aria-controls="det-${id}" aria-label="Details: ${esc(plain(it.item))}" title="Details, Quelle, nicht zutreffend">i</button>`
      + (it.caution ? `<p class="st-caution">${fill(it.caution)}</p>` : '')
      + det + '</li>';
  }
  function stepsHtml(p, learn) {
    const out = [];
    const items = p.items;
    for (let k = 0; k < items.length; k++) {
      const it = items[k];
      if (it.sub !== undefined) {
        let any = false, cond = false;
        for (let j = k + 1; j < items.length && items[j].sub === undefined; j++) {
          if (visible(items[j])) { any = true; if (items[j].when) cond = true; }
        }
        if (any) out.push(`<li class="subhead${cond ? ' cond' : ''}">${fill(it.sub)}</li>`);
        continue;
      }
      if (visible(it)) out.push(stepHtml(it, learn));
    }
    return out.join('');
  }
  function nclHtml(c, pre) {
    const g = prog(c);
    const rows = c.items.map(it => {
      if (it.line) return `<li class="line">${esc(it.label || '')}</li>`;
      if (!visible(it)) return '';
      const st = S.checks[it.id];
      return `<li class="${st === 'done' ? 'done' : ''}" data-row="${esc(it.id)}"><label><input type="checkbox" data-check="${esc(it.id)}"${st === 'done' ? ' checked' : ''}>`
        + `<span class="ci">${fill(it.item)}</span><span class="dots" aria-hidden="true"></span><span class="cs">${fill(it.state)}</span></label></li>`;
    }).join('');
    return `<section class="ncl${g.complete ? ' done' : ''}" id="${pre}-${c.id}" data-ncl="${c.id}" aria-label="Checkliste ${esc(c.title)}">`
      + `<header><h3>${esc(c.title)}</h3><span class="count" data-clcount="${c.id}"><b>${g.fin}</b>/${g.total}</span>`
      + `<button type="button" class="btn small ghost" data-clreset="${c.id}" aria-label="Checkliste ${esc(c.title)} zurücksetzen" title="Checkliste zurücksetzen">↺</button></header>`
      + `<ol>${rows}</ol></section>`;
  }
  function doneBanner(p, g, next) {
    if (!g.complete) return '';
    const cls = (p.checklists || []).map(id => PH.get(id)).filter(c => !prog(c).complete);
    return `<div class="phase-done"><span>✓ Phase erledigt${cls.length ? ` – jetzt die Checkliste ${esc(cls.map(c => c.title).join(' · '))}` : ''}</span>`
      + (next ? `<button type="button" class="btn small primary" data-go="${next.id}">Weiter →</button>` : '') + '</div>';
  }
  function renderStage() {
    const { p, list, i } = posOf(S.view);
    const g = prog(p);
    const learn = S.mode === 'learn';
    const cls = (p.checklists || []).map(id => PH.get(id));
    $('#stage').innerHTML = `
      <div class="stagebar"><span class="figtitle">Schritte · <b id="stage-count">${g.fin}/${g.total}</b></span>
        <div class="seg" role="group" aria-label="Ansicht"><button type="button" data-mode="flight" aria-pressed="${!learn}">Flug</button><button type="button" data-mode="learn" aria-pressed="${learn}">Lernen</button></div></div>
      <ol class="steps${learn ? ' learn' : ''}" aria-label="Schritte: ${esc(p.title)}">${stepsHtml(p, learn)}</ol>
      <div id="phase-done">${doneBanner(p, g, list[i + 1])}</div>
      ${cls.length ? `<h3 class="sub-h">Checkliste <small>nach dem Flow lesen</small></h3><div class="ncl-list">${cls.map(c => nclHtml(c, 'cl')).join('')}</div>` : ''}
      ${p.plate ? plateBlock(p.plate) : ''}`;
  }

  // ---------- Tracks ----------
  function renderTracks() {
    const f = sumProg(FLOW);
    const cDone = CLS.filter(c => prog(c).complete).length;
    const cur = PH.get(S.view).kind === 'flow' ? PH.get(S.view) : PH.get(S.lastFlow);
    const n = FLOW.indexOf(cur) + 1;
    const nextCl = CLS.find(c => !prog(c).complete);
    const allF = D.fields.filter(fd => !fd.when || matches(fd.when));
    const filled = allF.filter(fd => (S.data[fd.id] || '').trim()).length;
    const miss = ['v1', 'vr', 'v2', 'flex', 'trim', 'qnhDep', 'clearedAlt'].filter(k => !(S.data[k] || '').trim()).map(k => FIELD.get(k).label);
    const allDone = f.fin === f.total;
    $('#tracks').innerHTML = `
      <div class="track${allDone ? ' good' : ' live'}"><div class="name">Normal Flow</div><div class="state">Schritte erledigt</div>
        <div class="val">${f.fin}<small> / ${f.total}</small></div><div class="bar${allDone ? ' ok' : ''}"><i style="width:${pct(f.fin, f.total)}%"></i></div>
        <div class="note">${f.phases} von ${FLOW.length} Phasen komplett${f.na ? ` · ${f.na} N/A` : ''}</div></div>
      <div class="track${cDone === CLS.length ? ' good' : ''}"><div class="name">Checklisten</div><div class="state">Airbus Normal Checklist</div>
        <div class="val">${cDone}<small> / ${CLS.length}</small></div><div class="bar ok"><i style="width:${pct(cDone, CLS.length)}%"></i></div>
        <div class="note">${nextCl ? `Als Nächstes: ${esc(nextCl.title)}` : 'Alle gelesen'}</div></div>
      <div class="track live"><div class="name">Phase</div><div class="state">${esc(STAGE_OF.get(cur.id).title)}</div>
        <div class="val">${pad2(n)}<small> / ${FLOW.length}</small></div><div class="bar"><i style="width:${pct(n, FLOW.length)}%"></i></div>
        <div class="note">${esc(cur.title)}</div></div>
      <div class="track${miss.length ? '' : ' good'}"><div class="name">Flugdaten</div><div class="state">eingetragen</div>
        <div class="val">${filled}<small> / ${allF.length}</small></div><div class="bar${miss.length ? '' : ' ok'}"><i style="width:${pct(filled, allF.length)}%"></i></div>
        <div class="note${miss.length ? ' warn' : ''}">${miss.length ? `Fehlt: ${esc(miss.join(' · '))}` : 'Abflugdaten vollständig'}</div></div>`;
  }

  // ---------- Reiter ----------
  const TABS = ['all', 'spec', 'cl', 'ref', 'new', 'data'];
  function showTab(t, focus) {
    S.tab = t;
    TABS.forEach(x => {
      const on = x === t;
      const tab = $('#tab-' + x);
      tab.setAttribute('aria-selected', String(on));
      tab.tabIndex = on ? 0 : -1;
      $('#panel-' + x).hidden = !on;
    });
    renderPanel(t);
    save();
    if (focus) $('#tab-' + t).focus();
  }
  function renderPanel(t) { ({ all: renderAll, spec: renderSpec, cl: renderCl, ref: renderRef, new: renderNew, data: renderData })[t](); }

  let qTimer = 0;
  function renderAll() {
    const srcSel = $('#f-src');
    if (!srcSel.options.length) {
      srcSel.innerHTML = '<option value="all">Alle Quellen</option>' + Object.entries(SRC).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join('');
    }
    const q = $('#q').value.trim().toLowerCase();
    const fs = $('#f-status').value, fk = $('#f-kind').value, fsrc = srcSel.value;
    const rows = [];
    let n = 0, shown = 0;
    for (const p of D.phases) {
      if (p.kind === 'reference' || (fk !== 'all' && p.kind !== fk)) continue;
      const hits = [];
      for (const it of p.items) {
        if (!visible(it)) continue;
        n++;
        const c = S.checks[it.id];
        if ((fs === 'open' && c) || (fs === 'done' && c !== 'done') || (fs === 'na' && c !== 'na')) continue;
        if ((fs === 'cau' && it.type !== 'cau') || (fs === 'wrn' && it.type !== 'wrn') || (fs === 'v3' && it.rev !== 'v3')) continue;
        if (fsrc !== 'all' && it.src !== fsrc) continue;
        if (q) {
          const hay = [p.title, it.item, plain(it.state), it.caution, it.detail, SRC[it.src] && SRC[it.src].label].join(' ').toLowerCase();
          if (!hay.includes(q)) continue;
        }
        hits.push(it);
      }
      if (!hits.length) continue;
      const home = p.kind === 'checklist' ? FLOW.find(f => (f.checklists || []).includes(p.id)) : p;
      const kindLbl = p.kind === 'flow' ? `Phase ${pad2(FLOW.indexOf(p) + 1)}` : p.kind === 'special' ? 'Sonderverfahren' : 'Checkliste';
      rows.push(`<tr class="grp"><td colspan="5">${kindLbl} · <b>${esc(p.title)}</b></td></tr>`);
      for (const it of hits) {
        shown++;
        rows.push(`<tr data-go="${home ? home.id : ''}" data-item="${esc(it.id)}"${p.kind === 'checklist' ? ` data-clgo="${p.id}"` : ''}>`
          + `<td data-mark="${esc(it.id)}">${markHtml(it.id)}</td><td>${fill(it.item)}</td><td class="st t-${it.type}">${fill(it.state)}</td>`
          + `<td>${badge(it.src)}</td><td class="dim">${esc(shorten(plain(it.caution || it.detail || ''), 140))}</td></tr>`);
      }
    }
    $('#alltbl tbody').innerHTML = rows.join('') || '<tr class="empty-row"><td colspan="5">Keine Schritte passen zu Suche und Filter.</td></tr>';
    $('#allinfo').textContent = shown === n ? `${n} Schritte in Flow, Sonderverfahren und Checklisten` : `${shown} von ${n} Schritten`;
    $('#clear-filters').hidden = !(q || fs !== 'all' || fk !== 'all' || fsrc !== 'all');
  }
  function renderSpec() {
    $('#panel-spec').innerHTML = `<h2>Sonderverfahren</h2>
      <p class="lede">Karten für Ausnahmen, Training und die Besonderheiten deiner Weltreise. „Öffnen“ zeigt die Karte oben wie eine Phase – mit Schritten, Flugdaten und Profil.</p>
      <div class="cards">${SPEC.map((p, k) => {
        const g = prog(p);
        const isNew = p.items.every(it => !it.id || it.rev === 'v3');
        return `<article class="hcard${isNew ? ' v3' : ''}"><div class="ht"><span class="${isNew ? 'tagc' : ''}">S${pad2(k + 1)}${isNew ? ' · neu in V3' : ''}</span><span>${esc(p.zone || '')}</span></div>`
          + `<h3>${esc(p.title)}</h3><p>${esc(shorten(plain(p.note), 190))}</p>`
          + `<div class="foot"><span class="count"><b>${g.fin}</b>/${g.total}</span><button type="button" class="btn small" data-go="${p.id}">Öffnen →</button></div></article>`;
      }).join('')}</div>`;
  }
  function renderCl() {
    $('#panel-cl').innerHTML = `<h2>Checklisten</h2>
      <p class="lede">Airbus Normal Checklist mit Strich: der Teil über dem Strich zuerst, der Rest zum genannten Zeitpunkt. Im Flow steht jede Checkliste auch direkt bei ihrer Phase – die Häkchen sind dieselben.</p>
      <div class="ncl-grid">${CLS.map(c => nclHtml(c, 'tcl')).join('')}</div>`;
  }
  function tableHtml(t) {
    return `<div class="reftbl"><table><thead><tr>${t.head.map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>`
      + `<tbody>${t.rows.map(r => `<tr>${r.map(c => `<td>${fill(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function renderRef() {
    const parts = REF.filter(p => !p.sources).map(p => `<h3 class="sect">${esc(p.title)}${p.note ? ` <small>${esc(plain(p.note))}</small>` : ''}</h3>`
      + p.items.map(it => (it.sub !== undefined ? `<div class="figtitle ref-sub">${fill(it.sub)}</div>` : it.table ? tableHtml(it.table) : '')).join(''));
    $('#panel-ref').innerHTML = `<h2>Referenz</h2>
      <p class="lede">Grenzwerte, Klappenlogik und Faustregeln – mit Quelle. Leistungswerte kommen immer aus dem Fenix-EFB für den konkreten Flug.</p>
      ${parts.join('')}
      <h3 class="sect">Profile <small>mit deinen Flugdaten, soweit eingetragen</small></h3>
      <div class="plates-grid">${PLATE_ORDER.map(k => `<figure><figcaption>${esc(PLATES[k].title)}</figcaption><div class="screen" data-plate="${k}">${PLATES[k].svg(true)}</div></figure>`).join('')}</div>
      <h3 class="sect">Quellen <small>an jedem Schritt in der Ansicht „Lernen“</small></h3>
      <div class="srclist">${Object.entries(SRC).map(([k, v]) => `<div>${badge(k)}<span>${esc(v.text)}</span></div>`).join('')}</div>`;
  }
  function renderNew() {
    const logItem = l => { const r = ITEM.get(l.id); return r ? plain(r.it.item) : l.id; };
    $('#panel-new').innerHTML = `<h2>Was V3 anders macht</h2>
      <p class="lede">V3 führt V1 (Fable) und V2 (Astra) zusammen: Astras berechtigte Korrekturen und ihre stabilen Schritt-IDs, wieder konkrete Werte, wo V2 nur noch „as briefed“ sagte – und alles für deinen Fenix A320 mit CFM56-5B auf der Weltreise.</p>
      <div class="scroll free"><table class="cmp"><thead><tr><th scope="col">Kennzahl</th><th scope="col">V1 · Fable</th><th scope="col">V2 · Astra</th><th scope="col">V3</th></tr></thead>
      <tbody>${D.compare.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
      <div class="chg">${D.changes.map(c => `<article><div class="area">${esc(c.area)}</div><h3>${esc(c.title)}</h3><p>${esc(c.text)}</p><div class="eff">${esc(c.effect)}</div></article>`).join('')}</div>
      <details class="chk"><summary><span>Alle Änderungen gegenüber V2</span><em>${D.log.length} Einträge mit Begründung</em></summary>
      <div class="scroll"><table><thead><tr><th scope="col">Bereich</th><th scope="col">Schritt</th><th scope="col">Änderung</th><th scope="col">Begründung</th></tr></thead>
      <tbody>${D.log.map(l => `<tr${isView(l.phase) ? ` data-go="${l.phase}"${ITEM.has(l.id) ? ` data-item="${esc(l.id)}"` : ''}` : ''}><td class="mono">${esc(l.phase)}</td><td>${esc(logItem(l))}</td><td>${esc(l.action)}</td><td>${esc(l.why)}</td></tr>`).join('')}</tbody></table></div></details>`;
  }
  function renderData() {
    const dep = D.fields.filter(f => f.group === 'dep');
    const arr = D.fields.filter(f => f.group === 'arr');
    $('#panel-data').innerHTML = `<h2>Flugdaten, Sicherung und Reset</h2>
      <p class="lede">${storeState === 'saved'
        ? 'Häkchen, Flugdaten und Profil liegen im Speicher dieses Browsers – getrennt je Datei-Adresse. Für einen anderen Browser oder das Tablet: Sicherung speichern und dort laden.'
        : 'Dieser Browser erlaubt gerade kein Speichern. Speichere eine Sicherung, bevor du die Seite schließt.'}</p>
      <div class="datagrid">
        <section class="dbox wide" id="flightdata"><h3>Flugdaten &amp; Profil</h3>
          <p class="note">Werte erscheinen in den Schritten grün, leere Felder als ___. Keine automatische Performance-Berechnung – die Werte kommen aus dem Fenix-EFB, der Freigabe und dem Flugplan.</p>
          <div class="grp-t">Abflug</div><div class="dc-grid">${dep.map(f => fieldInput(f.id)).join('')}</div>
          <div class="grp-t">Ankunft</div><div class="dc-grid">${arr.map(f => fieldInput(f.id)).join('')}</div>
          <div class="grp-t">Profil</div><div class="dc-prof">${D.profile.map(f => profSeg(f.id)).join('')}</div>
          <div class="actions"><button type="button" class="btn" data-act="newflight">Neuer Flug …</button></div>
          <div class="confirm" id="nf-confirm" hidden><p><b>Neuen Flug beginnen?</b> Löscht alle Häkchen, N/A-Markierungen und Flugdaten. Das Profil bleibt.</p>
            <div class="actions"><button type="button" class="btn" data-act="export">Erst Sicherung speichern</button><button type="button" class="btn danger" data-act="newflight-yes">Ja, neuer Flug</button><button type="button" class="btn" data-act="newflight-no">Abbrechen</button></div></div>
        </section>
        <section class="dbox"><h3>Sicherung</h3><p>Speichert Häkchen, Flugdaten, Profil und Ansicht als JSON – und lädt eine solche Datei wieder.</p>
          <div class="actions"><button type="button" class="btn" data-act="export">Sicherung speichern</button><label class="btn" for="restore">Sicherung laden</label><input class="visually-hidden" type="file" id="restore" accept="application/json,.json"></div>
          <div class="confirm" id="rs-confirm" hidden></div></section>
        <section class="dbox reset"><h3>Zurücksetzen</h3>
          <p>Einzelne Phasen oder Checklisten setzt du direkt dort zurück.</p>
          <div class="actions"><button type="button" class="btn danger" data-act="reset-checks">Alle Häkchen zurücksetzen …</button></div>
          <div class="confirm" id="rc-confirm" hidden><p><b>Alle Häkchen und N/A löschen?</b> Flugdaten und Profil bleiben.</p>
            <div class="actions"><button type="button" class="btn danger" data-act="reset-checks-yes">Ja, zurücksetzen</button><button type="button" class="btn" data-act="reset-checks-no">Abbrechen</button></div></div></section>
      </div>`;
  }

  // ---------- Profile (SVG, Plot-Screen) ----------
  const W = 640;
  let svgN = 0;
  const v = (k, pre = '') => { const x = fieldVal(k); return x ? `<tspan class="p-val">${esc(pre + x)}</tspan>` : `<tspan class="p-sub">${esc(pre)}___</tspan>`; };
  function svgOpen(h, title) {
    const u = ++svgN;
    const head = `<svg viewBox="0 0 ${W} ${h}" role="img" aria-label="${esc(title)}"><title>${esc(title)}</title><defs>`
      + `<filter id="g${u}" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`
      + `<marker id="a${u}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#aab5be"/></marker>`
      + `<marker id="b${u}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#33b4f5"/></marker></defs>`;
    return { u, head };
  }
  const grid = (h, g) => { let s = ''; for (let y = 40; y < g; y += 40) s += `<line class="p-grid" x1="0" y1="${y}" x2="${W}" y2="${y}"/>`; return s; };
  const txt = (x, y, cls, s, anchor = 'start') => `<text class="${cls}" x="${x}" y="${y}" text-anchor="${anchor}">${s}</text>`;
  const dot = (x, y, cls = '') => `<circle class="p-mark ${cls}" cx="${x}" cy="${y}" r="5"/>`;
  function lbl(mx, my, tx, ty, main, sub, anchor = 'middle') {
    const above = ty < my;
    const ly = above ? ty + (sub ? 19 : 5) : ty - 14;
    return `<line class="p-lead" x1="${mx}" y1="${my}" x2="${tx}" y2="${ly}"/>` + txt(tx, ty, 'p-lbl', main, anchor) + (sub ? txt(tx, ty + 14, 'p-sub', sub, anchor) : '');
  }
  function chip(x, y, t, anchor = 'middle') {
    const w = Math.round(t.length * 6.7 + 14);
    const x0 = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
    return `<rect class="p-cfg" x="${x0}" y="${y - 13}" width="${w}" height="19" rx="3"/>` + txt(x0 + w / 2, y, 'p-cfg-t', esc(t), 'middle');
  }
  const hline = (y, x1, x2, t, tx, anchor = 'end') => `<line class="p-hline" x1="${x1}" y1="${y}" x2="${x2}" y2="${y}"/>` + txt(tx, y - 5, 'p-hlbl', t, anchor);
  const pathD = pts => 'M' + pts.map(p => p.join(',')).join(' L');
  const route = (u, d) => `<path class="p-path" d="${d}" filter="url(#g${u})"/>`;

  function plTakeoff() {
    const g = 262;
    const { u, head } = svgOpen(300, 'Startprofil');
    const thr = fieldVal('thr'), acc = fieldVal('acc');
    const same = thr === acc;
    const f1 = S.profile.toConf !== '1';
    const P = [[24, g], [182, g], [296, 184], same ? [296, 184] : [372, 156], [448, 142], [520, 128], [616, 84]];
    let s = head + grid(300, g) + txt(16, 24, 'p-title', `STARTPROFIL · T/O CONF ${esc(profLabel('toConf'))}`)
      + `<line class="p-ground" x1="0" y1="${g}" x2="${W}" y2="${g}"/><line class="p-rwy" x1="24" y1="${g}" x2="196" y2="${g}"/>`
      + route(u, pathD(P))
      + dot(120, g, 'warn') + txt(116, g + 24, 'p-lbl', `V1 ${v('v1')}`, 'end') + dot(166, g) + txt(172, g + 24, 'p-lbl', `VR ${v('vr')}`, 'start')
      + txt(236, 206, 'p-sub', 'SRS · 15°', 'end')
      + dot(214, 239) + lbl(214, 239, 228, 254, 'POSITIVE CLIMB · GEAR UP', null, 'start')
      + dot(296, 184) + lbl(296, 184, 296, 148, same ? `THR RED / ACC ${v('thr')}` : `THR RED ${v('thr')}`, same ? 'CL · PACKS · SPEED ↑' : 'CL · PACKS ON');
    if (!same) s += dot(372, 156) + lbl(372, 156, 382, 190, `ACC ${v('acc')}`, 'SPEED ↑ · CLEAN UP', 'start');
    if (f1) s += dot(448, 142) + lbl(448, 142, 448, 108, 'F → FLAPS 1', null);
    s += dot(520, 128) + lbl(520, 128, 528, 162, 'S → FLAPS 0', 'SPLRS DISARM', 'start')
      + txt(616, 56, 'p-lbl', 'CLIMB', 'end') + txt(616, 70, 'p-sub', 'AFTER TAKEOFF / CLIMB C/L', 'end');
    return s + '</svg>';
  }
  function plApproach() {
    const g = 262;
    const ap = S.profile.approach;
    const full = S.profile.ldgConf === 'FULL';
    const { u, head } = svgOpen(300, 'Anflugprofil');
    const P = [[16, 106], [262, 106], [560, g]];
    let s = head + grid(300, g)
      + `<line class="p-ground" x1="0" y1="${g}" x2="${W}" y2="${g}"/><line class="p-rwy" x1="560" y1="${g}" x2="632" y2="${g}"/>`
      + txt(566, g + 24, 'p-rwy-lbl', 'THR') + hline(40, 262, 632, `GA ALT ${v('gaAlt')}`, 632) + route(u, pathD(P));
    if (ap === 'npa') {
      s += txt(16, 24, 'p-title', 'ANFLUG · NPA · TRK/FPA · EARLY STABILISED')
        + dot(150, 106) + lbl(150, 106, 150, 72, 'STABILISED BEFORE FDP', `VAPP ${v('vapp')}`) + chip(150, 132, `GEAR DN · FLAPS ${profLabel('ldgConf')}`)
        + dot(262, 106) + lbl(262, 106, 276, 72, `FPA ${v('fpa')}°`, 'PULL 0.2 NM BEFORE FDP', 'start')
        + chip(350, 206, 'ALT / DIST CHECK')
        + dot(461, 210) + lbl(461, 210, 470, 172, '1000 ft · STABILISED', 'OR GO AROUND', 'start')
        + dot(520, 241, 'alert') + lbl(520, 241, 548, 286, `MDA/DA ${v('mins')}`, null, 'end');
    } else {
      const fdp = ap === 'rnav' ? 'FINAL APP · FDP' : 'G/S* · FDP';
      s += txt(16, 24, 'p-title', `ANFLUG · ${ap === 'rnav' ? 'RNAV · FINAL APP' : 'ILS'} · DECELERATED`)
        + dot(60, 106) + lbl(60, 106, 60, 72, 'DECEL', 'APPR PHASE') + chip(165, 132, 'FLAPS 1 · S SPEED')
        + dot(262, 106) + lbl(262, 106, 262, 72, fdp, `SET GA ALT ${v('gaAlt')}`)
        + dot(361, 158) + lbl(361, 158, 368, 128, '2000 ft · FLAPS 2', 'GEAR DOWN · SPLRS ARM', 'start')
        + chip(392, 212, 'FLAPS 3') + (full ? chip(420, 238, 'FLAPS FULL') : '')
        + dot(461, 210) + lbl(461, 210, 470, 172, '1000 ft · STABILISED', `VAPP ${v('vapp')}`, 'start')
        + dot(540, 252, 'alert') + lbl(540, 252, 548, 286, `MIN ${v('mins')}`, null, 'end');
    }
    return s + '</svg>';
  }
  function plEo() {
    const g = 262;
    const { u, head } = svgOpen(300, 'Triebwerksausfall nach V1');
    const P = [[24, g], [182, g], [262, 226], [376, 178], [576, 178], [628, 150]];
    return head + grid(300, g) + txt(16, 24, 'p-title', 'TRIEBWERKSAUSFALL NACH V1')
      + `<line class="p-ground" x1="0" y1="${g}" x2="${W}" y2="${g}"/><line class="p-rwy" x1="24" y1="${g}" x2="196" y2="${g}"/>`
      + hline(110, 300, 632, 'MAX EO ACC ALT · TOGA 10 min', 632) + route(u, pathD(P))
      + dot(120, g, 'alert') + txt(116, g + 24, 'p-lbl', `V1 ${v('v1')} · ENG FAIL`, 'end')
      + dot(166, g) + txt(172, g + 24, 'p-lbl', `VR ${v('vr')} · 12.5°`, 'start')
      + dot(262, 226) + lbl(262, 226, 272, 250, '400 ft · ECAM ACTIONS', null, 'start')
      + dot(376, 178) + lbl(376, 178, 376, 138, `EO ACC ${v('eoAcc')}`, 'LEVEL OFF · ACCELERATE')
      + dot(450, 178) + chip(450, 206, 'F → FLAPS 1') + dot(520, 178) + chip(520, 230, 'S → FLAPS 0')
      + dot(576, 178) + lbl(576, 178, 566, 138, 'GREEN DOT', 'OP CLB · MCT', 'end')
      + '</svg>';
  }
  function plGoaround() {
    const g = 262;
    const { u, head } = svgOpen(300, 'Durchstarten');
    const P = [[16, 120], [240, 236], [300, 206], [366, 172], [430, 150], [500, 140], [560, 130], [624, 96]];
    return head + grid(300, g) + txt(16, 24, 'p-title', 'DURCHSTARTEN · TOGA')
      + `<line class="p-ground" x1="0" y1="${g}" x2="${W}" y2="${g}"/><line class="p-rwy" x1="400" y1="${g}" x2="560" y2="${g}"/>` + txt(404, g + 24, 'p-rwy-lbl', 'RWY')
      + hline(70, 300, 632, `GA ALT ${v('gaAlt')}`, 632) + route(u, pathD(P))
      + dot(240, 236, 'alert') + lbl(240, 236, 252, 256, 'MINIMUM → TOGA', null, 'start')
      + chip(350, 232, 'FLAPS 1 STEP UP')
      + dot(300, 206) + lbl(300, 206, 292, 176, 'POS CLIMB', 'GEAR UP', 'end')
      + dot(366, 172) + lbl(366, 172, 366, 140, 'THR RED · CL', null)
      + dot(430, 150) + lbl(430, 150, 438, 178, 'ACC · GREEN DOT', null, 'start')
      + dot(500, 140) + chip(500, 116, 'F → FLAPS 1') + dot(560, 130) + chip(566, 158, 'S → FLAPS 0')
      + '</svg>';
  }
  function plGsAbove() {
    const g = 262;
    const { u, head } = svgOpen(300, 'Glide Slope von oben');
    return head + grid(300, g) + txt(16, 24, 'p-title', 'G/S VON OBEN')
      + `<line class="p-ground" x1="0" y1="${g}" x2="${W}" y2="${g}"/><line class="p-rwy" x1="560" y1="${g}" x2="632" y2="${g}"/>` + txt(566, g + 24, 'p-rwy-lbl', 'THR')
      + `<path class="p-path2" d="M60,40 L560,${g}"/>` + txt(64, 36, 'p-hlbl', 'GLIDE SLOPE')
      + hline(48, 150, 460, 'FCU ALT ÜBER DEM FLUGZEUG', 460)
      + route(u, 'M16,70 L150,70 L380,182 L560,262')
      + dot(150, 70) + lbl(150, 70, 140, 100, 'APPR · LOC*', 'V/S −1500', 'end')
      + chip(210, 162, 'GEAR DN · FLAPS 2')
      + dot(380, 182) + lbl(380, 182, 392, 150, 'G/S*', `SET GA ALT ${v('gaAlt')}`, 'start')
      + dot(470, 222) + lbl(470, 222, 478, 196, '1000 ft · STABILISED', 'OR GO AROUND', 'start')
      + '</svg>';
  }
  function plCircling() {
    const { u, head } = svgOpen(340, 'Circling-Anflug');
    return head + txt(16, 24, 'p-title', 'CIRCLING · MDA → DOWNWIND → LANDUNG')
      + '<rect x="230" y="196" width="200" height="12" fill="#2a323c" stroke="#66737f"/>'
      + txt(236, 224, 'p-rwy-lbl', '09', 'start') + txt(424, 224, 'p-rwy-lbl', '27', 'end')
      + '<path class="p-path2" d="M632,202 L500,202"/>' + txt(632, 190, 'p-sub', 'APPROACH RWY 27', 'end')
      + route(u, 'M500,202 L456,158 Q440,130 410,130 L170,130 Q110,130 110,166 Q110,202 150,202 L230,202')
      + dot(500, 202, 'alert') + txt(510, 236, 'p-lbl', 'MDA · LEVEL OFF') + txt(510, 250, 'p-sub', 'RWY IN SIGHT')
      + txt(486, 176, 'p-sub', '45° · 30 s')
      + txt(390, 116, 'p-lbl', 'DOWNWIND · CONF 3 · F', 'middle') + txt(390, 100, 'p-sub', 'GEAR DOWN · SEC F-PLN ACTIVE', 'middle')
      + dot(230, 130) + txt(244, 112, 'p-lbl', 'ABEAM THR · CHRONO', 'end') + txt(244, 98, 'p-sub', '3 s per 100 ft', 'end')
      + dot(110, 166) + txt(124, 166, 'p-lbl', 'BASE · FINAL') + txt(124, 180, 'p-sub', 'AP/FD OFF · LDG CONF')
      + txt(16, 326, 'p-sub', 'MINIMA: MDH ≥ 600 ft · VIS ≥ 2400 m (CAT C) · TRK-FPA DURCHGEHEND')
      + '</svg>';
  }
  function plCircuit(kind) {
    const quick = kind === 'quick';
    const { u, head } = svgOpen(340, quick ? 'Quick Return mit Triebwerksausfall' : 'Visual Approach');
    let s = head + txt(16, 24, 'p-title', quick ? 'QUICK RETURN · ENGINE OUT · LINKSPLATZRUNDE' : 'VISUAL APPROACH · LINKSPLATZRUNDE · 1500 ft')
      + '<rect x="230" y="250" width="220" height="12" fill="#2a323c" stroke="#66737f"/>'
      + txt(236, 280, 'p-rwy-lbl', '09', 'start') + txt(444, 280, 'p-rwy-lbl', '27', 'end');
    if (quick) {
      s += route(u, 'M240,256 L560,256 Q620,256 620,200 L620,180 Q620,120 560,120 L170,120 Q110,120 110,180 L110,200 Q110,256 170,256 L230,256')
        + dot(520, 256) + txt(520, 284, 'p-lbl', 'ACC HT · LEVEL OFF', 'middle') + txt(520, 298, 'p-sub', 'S SPEED · FLAPS 1', 'middle')
        + txt(560, 108, 'p-lbl', 'DOWNWIND · FLAPS 1 · S', 'end')
        + dot(380, 120) + txt(380, 146, 'p-lbl', 'ACTIVATE APPR', 'middle') + txt(380, 160, 'p-sub', 'FCU SPEED PUSH', 'middle')
        + dot(230, 120) + txt(230, 102, 'p-lbl', 'ABEAM THR · CHRONO', 'middle') + txt(230, 88, 'p-sub', '45 s ± 1 s / kt', 'middle')
        + dot(110, 190) + txt(124, 196, 'p-lbl', 'BASE · FLAPS 2') + txt(124, 210, 'p-sub', 'GEAR DOWN')
        + chip(170, 236, 'FINAL CONF');
    } else {
      s += route(u, 'M620,120 L170,120 Q110,120 110,180 L110,200 Q110,256 170,256 L230,256')
        + txt(632, 108, 'p-lbl', 'DOWNWIND · 1500 ft', 'end') + chip(450, 100, 'FLAPS 1')
        + dot(340, 120) + txt(340, 146, 'p-lbl', 'ABEAM RWY', 'middle') + txt(340, 160, 'p-sub', 'APPR PHASE · TRK/FPA · FD OFF', 'middle')
        + dot(230, 120) + txt(230, 102, 'p-lbl', 'ABEAM THR · CHRONO', 'middle') + txt(230, 88, 'p-sub', '3 s / 100 ft ± 1 s / kt', 'middle')
        + chip(160, 146, 'FLAPS 2')
        + dot(110, 190) + txt(124, 196, 'p-lbl', 'BASE') + txt(124, 210, 'p-sub', 'GEAR DN · SPLRS ARM · FLAPS 3')
        + chip(170, 236, 'FLAPS FULL')
        + dot(200, 256) + txt(200, 300, 'p-lbl', '500 ft · STABILISED', 'middle')
        + txt(16, 326, 'p-sub', 'DOWNWIND 2,5–3 NM · QUERNEIGUNG 15° GEGENWIND / 25° RÜCKENWIND');
    }
    return s + '</svg>';
  }
  const ZONES_ON = { n4: [1], n5: [5, 2, 4], n6: [3, 6] };
  function plZones(all) {
    const on = all ? [] : (ZONES_ON[S.view] || []);
    const { u, head } = svgOpen(360, 'Cockpit-Zonen');
    const z = n => (on.includes(n) ? ' on' : '');
    const num = (n, x, y) => `<circle class="p-num${z(n)}" cx="${x}" cy="${y}" r="11"/>` + txt(x, y + 4, 'p-num-t', String(n), 'middle');
    const ar = (n, d) => `<path class="p-arrow${z(n)}" d="${d}" marker-end="url(#${on.includes(n) ? 'b' : 'a'}${u})"/>`;
    return head + txt(16, 24, 'p-title', 'COCKPIT-ZONEN · FLOW-REIHENFOLGE')
      + `<polygon class="p-zone${z(1)}" points="200,36 440,36 468,104 172,104"/>` + txt(320, 66, 'p-zone-t', 'OVERHEAD', 'middle') + ar(1, 'M220,86 L420,86') + num(1, 452, 52)
      + `<rect class="p-zone${z(5)}" x="80" y="116" width="480" height="30" rx="3"/>` + txt(320, 135, 'p-zone-t', 'GLARESHIELD · FCU · EFIS', 'middle') + num(5, 580, 131)
      + '<rect class="p-zone" x="80" y="156" width="170" height="86" rx="3"/>' + txt(165, 203, 'p-zone-t', 'CAPT PFD · ND', 'middle')
      + '<rect class="p-zone" x="390" y="156" width="170" height="86" rx="3"/>' + txt(475, 203, 'p-zone-t', 'F/O PFD · ND', 'middle')
      + `<rect class="p-zone${z(2)}" x="262" y="156" width="116" height="100" rx="3"/>` + txt(320, 210, 'p-zone-t', 'E/WD · SD', 'middle') + num(2, 320, 176)
      + `<rect class="p-zone${z(4)}" x="170" y="250" width="80" height="26" rx="3"/>` + txt(210, 267, 'p-zone-t', 'ISIS · CLK', 'middle') + num(4, 154, 263)
      + `<rect class="p-zone${z(3)}" x="262" y="266" width="116" height="84" rx="3"/>` + txt(320, 298, 'p-zone-t', 'PEDESTAL', 'middle') + txt(320, 314, 'p-sub', 'MCDU · ENG · RMP', 'middle') + ar(3, 'M320,322 L320,344') + num(3, 394, 280)
      + `<rect class="p-zone${z(6)}" x="16" y="156" width="52" height="150" rx="3"/>` + txt(42, 236, 'p-zone-t', 'CAPT', 'middle') + num(6, 42, 178)
      + `<rect class="p-zone${z(6)}" x="572" y="156" width="52" height="150" rx="3"/>` + txt(598, 236, 'p-zone-t', 'F/O', 'middle') + num(6, 598, 178)
      + '</svg>';
  }
  const LEG_PROFILE = [['', 'Flugweg'], ['dot', 'Aktionspunkt'], ['cfg', 'Konfiguration'], ['data', 'deine Flugdaten']];
  const PLATES = {
    zones: { title: 'Cockpit-Zonen', svg: plZones, legend: [[null, '1 Overhead'], [null, '2 ECAM'], [null, '3 Pedestal'], [null, '4 ISIS & Uhr'], [null, '5 Glareshield'], [null, '6 Seitenkonsolen']] },
    takeoff: { title: 'Startprofil', svg: plTakeoff, legend: [['', 'Flugweg'], ['dot', 'Aktionspunkt'], ['data', 'deine Flugdaten']] },
    approach: { title: 'Anflugprofil', svg: plApproach, legend: [...LEG_PROFILE, ['dash', 'Go-around-Höhe']] },
    eo: { title: 'Triebwerksausfall nach V1', svg: plEo, legend: [...LEG_PROFILE, ['dash', 'max. EO-Beschleunigungshöhe']] },
    goaround: { title: 'Durchstarten', svg: plGoaround, legend: [...LEG_PROFILE, ['dash', 'Go-around-Höhe']] },
    gsabove: { title: 'G/S von oben', svg: plGsAbove, legend: [['', 'Flugweg'], ['dash', 'Glide Slope / FCU-Höhe'], ['cfg', 'Konfiguration']] },
    circling: { title: 'Circling', svg: plCircling, legend: [['', 'Flugweg'], ['dash', 'Instrumentenanflug'], ['dot', 'Aktionspunkt']] },
    visual: { title: 'Visual Approach', svg: () => plCircuit('visual'), legend: [['', 'Flugweg'], ['dot', 'Aktionspunkt'], ['cfg', 'Konfiguration']] },
    quickreturn: { title: 'Quick Return', svg: () => plCircuit('quick'), legend: [['', 'Flugweg'], ['dot', 'Aktionspunkt'], ['cfg', 'Konfiguration']] },
  };
  const PLATE_ORDER = ['zones', 'takeoff', 'approach', 'eo', 'goaround', 'gsabove', 'circling', 'visual', 'quickreturn'];
  function plateBlock(key) {
    const pl = PLATES[key];
    const legend = pl.legend.map(([c, t]) => `<span>${c !== null ? `<i class="swatch ${c}"></i>` : ''}${esc(t)}</span>`).join('');
    return `<div class="plate"><div class="stagebar"><span class="figtitle">${esc(pl.title)}</span></div>`
      + `<div class="screen" data-plate="${key}">${pl.svg()}</div><div class="legend">${legend}</div></div>`;
  }
  const redrawPlates = () => $$('.screen[data-plate]').forEach(el => { el.innerHTML = PLATES[el.dataset.plate].svg(!!el.closest('#panel-ref')); });

  // ---------- Aktionen ----------
  function syncItem(id) {
    const c = S.checks[id];
    $$(`[data-row="${cssq(id)}"]`).forEach(row => {
      row.classList.toggle('done', c === 'done');
      row.classList.toggle('na', c === 'na');
      const inp = row.querySelector('input[data-check]');
      if (inp) { inp.checked = c === 'done'; inp.disabled = c === 'na'; }
      const item = row.querySelector('.st-item');
      if (item) {
        const tag = item.querySelector('.na-tag');
        if (c === 'na' && !tag) item.insertAdjacentHTML('beforeend', '<span class="na-tag">N/A</span>');
        if (c !== 'na' && tag) tag.remove();
      }
      const nab = row.querySelector('[data-na]');
      if (nab) nab.textContent = c === 'na' ? 'Wieder zutreffend' : 'Nicht zutreffend';
    });
    $$(`[data-mark="${cssq(id)}"]`).forEach(td => { td.innerHTML = markHtml(id); });
  }
  function refreshMeta() {
    renderHeader(); renderNav(); renderRail(); renderTracks();
    const { p, list, i } = posOf(S.view);
    const g = prog(p);
    const sc = $('#stage-count'); if (sc) sc.textContent = `${g.fin}/${g.total}`;
    const pd = $('#phase-done'); if (pd) pd.innerHTML = doneBanner(p, g, list[i + 1]);
    const pa = $('#prose-actions'); if (pa) pa.innerHTML = actionsHtml(p, g, list[i + 1]);
    const lm = $('#legmeta'); if (lm) lm.innerHTML = legmetaHtml(p, g);
    $$('[data-ncl]').forEach(el => {
      const q = prog(PH.get(el.dataset.ncl));
      el.classList.toggle('done', q.complete);
      const cnt = el.querySelector('[data-clcount]');
      if (cnt) cnt.innerHTML = `<b>${q.fin}</b>/${q.total}`;
    });
    if (S.tab === 'spec') renderSpec();
  }
  function setCheck(id, val) {
    if (val) S.checks[id] = val; else delete S.checks[id];
    save(); syncItem(id); refreshMeta();
  }
  function resetIds(ids) {
    ids.forEach(id => delete S.checks[id]);
    save(); ids.forEach(syncItem); refreshMeta();
  }
  function setField(k, value, srcEl) {
    const val = value.slice(0, 16);
    if (val.trim()) S.data[k] = val; else delete S.data[k];
    save();
    $$(`input[data-field="${cssq(k)}"]`).forEach(inp => { if (inp !== srcEl) inp.value = val; });
    $$(`[data-ph="${cssq(k)}"]`).forEach(sp => { const x = fieldVal(k); sp.textContent = x || '___'; sp.classList.toggle('empty', !x); });
    redrawPlates();
    renderTracks();
    const dc = $('#dc-count');
    if (dc) { const p = PH.get(S.view); const fs = (p.fields || []).filter(x => FIELD.has(x) && (!FIELD.get(x).when || matches(FIELD.get(x).when))); dc.textContent = `${fs.filter(x => fieldVal(x)).length}/${fs.length}`; }
  }
  function setProfile(k, val, btn) {
    if (S.profile[k] === val) return;
    S.profile[k] = val;
    save();
    const where = btn && btn.closest('#prose') ? '#prose' : btn && btn.closest('#panel-data') ? '#panel-data' : null;
    renderHeader(); renderNav(); renderRail(); renderProse(); renderStage(); renderTracks(); renderPanel(S.tab);
    if (where) { const b = $(`${where} [data-prof="${cssq(k)}"][data-val="${cssq(val)}"]`); if (b) b.focus({ preventScroll: true }); }
  }
  function go(id, opts = {}) {
    if (!isView(id)) return;
    const p = PH.get(id);
    S.view = id;
    if (p.kind === 'flow') S.lastFlow = id;
    save();
    try { history.replaceState(null, '', '#' + id); } catch { /* file:// in manchen Browsern */ }
    renderHeader(); renderNav(); renderRail(); renderProse(); renderStage(); renderTracks();
    if (S.tab === 'spec') renderSpec();
    const gridEl = $('#grid');
    if (opts.item) {
      setTimeout(() => {
        let row = opts.cl ? $(`#cl-${cssq(opts.cl)} [data-row="${cssq(opts.item)}"]`) : null;
        if (!row) row = $(`#stage [data-row="${cssq(opts.item)}"]`);
        if (!row) return;
        row.scrollIntoView({ block: 'center', behavior: smooth() });
        row.classList.remove('flash'); void row.offsetWidth; row.classList.add('flash');
        const inp = row.querySelector('input');
        if (inp && !inp.disabled) inp.focus({ preventScroll: true });
      }, 0);
      return;
    }
    const top = gridEl.getBoundingClientRect().top;
    if (top < 0 || top > innerHeight * 0.6) gridEl.scrollIntoView({ block: 'start', behavior: smooth() });
    if (opts.focus !== false) gridEl.focus({ preventScroll: true });
  }
  function nextOpen() {
    const p = PH.get(S.view);
    const order = p.kind === 'flow' ? FLOW.slice(FLOW.indexOf(p)).concat(FLOW.slice(0, FLOW.indexOf(p))) : [p];
    for (const q of order) {
      const it = activeItems(q).find(x => !S.checks[x.id]);
      if (it) return go(q.id, { item: it.id });
      for (const cid of q.checklists || []) {
        const ci = activeItems(PH.get(cid)).find(x => !S.checks[x.id]);
        if (ci) return go(q.id, { item: ci.id, cl: cid });
      }
    }
    toast(p.kind === 'flow' ? 'Alles erledigt – kein offener Schritt mehr.' : 'Diese Karte ist vollständig abgehakt.');
  }
  function openChecklist(cid) {
    const el = document.getElementById('cl-' + cid);
    if (el) {
      el.scrollIntoView({ block: 'start', behavior: smooth() });
      const inp = el.querySelector('input:not(:checked)') || el.querySelector('input');
      if (inp) inp.focus({ preventScroll: true });
      return;
    }
    showTab('cl');
    setTimeout(() => { const t = document.getElementById('tcl-' + cid); if (t) t.scrollIntoView({ block: 'start', behavior: smooth() }); }, 0);
  }
  function toggleInfo(btn) {
    const det = document.getElementById('det-' + btn.dataset.info);
    if (!det) return;
    const open = det.hidden;
    det.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
  }
  function exportBackup() {
    const blob = new Blob([JSON.stringify({ app: 'fenix-a320-flow', version: 3, exported: today(), ...S }, null, 1)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `Fenix-A320-Flow-V3-${today()}.json`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  }
  let pendingImport = null;
  function readBackup(file) {
    if (!file) return;
    const r = new FileReader();
    r.onload = () => {
      let s = null;
      try { s = sanitize(JSON.parse(r.result)); } catch { s = null; }
      const box = $('#rs-confirm');
      box.hidden = false;
      if (!s) { pendingImport = null; box.innerHTML = '<p><b>Keine V3-Sicherung.</b> Die Datei wurde nicht geladen, nichts wurde geändert.</p>'; return; }
      pendingImport = s;
      box.innerHTML = `<p><b>Sicherung laden?</b> ${Object.keys(s.checks).length} Häkchen/N/A und ${Object.keys(s.data).length} Flugdaten`
        + `${s.dropped ? `; ${s.dropped} unbekannte Einträge werden ignoriert` : ''}. Der aktuelle Stand wird ersetzt.</p>`
        + '<div class="actions"><button type="button" class="btn danger" data-act="import-yes">Ja, laden</button><button type="button" class="btn" data-act="import-no">Abbrechen</button></div>';
      const yes = box.querySelector('[data-act="import-yes"]');
      if (yes) yes.focus();
    };
    r.readAsText(file);
  }
  function renderEverything() {
    renderHeader(); renderNav(); renderRail(); renderProse(); renderStage(); renderTracks(); showTab(S.tab);
  }
  function act(a, btn) {
    const p = PH.get(S.view);
    switch (a) {
      case 'open': return nextOpen();
      case 'reset-phase': return resetIds(activeItems(p).map(it => it.id));
      case 'newflight': $('#nf-confirm').hidden = false; $('#nf-confirm [data-act="newflight-no"]').focus(); return undefined;
      case 'newflight-no': $('#nf-confirm').hidden = true; return undefined;
      case 'newflight-yes':
        S.checks = {}; S.data = {}; S.view = FLOW[0].id; S.lastFlow = FLOW[0].id;
        save(); renderEverything(); toast('Neuer Flug – Häkchen und Flugdaten gelöscht.'); return undefined;
      case 'reset-checks': $('#rc-confirm').hidden = false; $('#rc-confirm [data-act="reset-checks-no"]').focus(); return undefined;
      case 'reset-checks-no': $('#rc-confirm').hidden = true; return undefined;
      case 'reset-checks-yes': S.checks = {}; save(); renderEverything(); toast('Alle Häkchen zurückgesetzt.'); return undefined;
      case 'export': return exportBackup();
      case 'import-yes':
        if (pendingImport) { S = pendingImport; pendingImport = null; save(); renderEverything(); toast('Sicherung geladen.'); }
        return undefined;
      case 'import-no': pendingImport = null; $('#rs-confirm').hidden = true; return undefined;
      default: return btn;
    }
  }
  let toastTimer = 0;
  function toast(msg) {
    let el = $('#toast');
    if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; el.setAttribute('role', 'status'); document.body.appendChild(el); }
    el.textContent = msg; el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, 3200);
  }
  function find() {
    showTab('all');
    $('#book').scrollIntoView({ block: 'start', behavior: smooth() });
    $('#q').focus({ preventScroll: true });
  }

  // ---------- Ereignisse ----------
  document.addEventListener('change', ev => {
    const t = ev.target;
    if (t.matches('input[data-check]')) return setCheck(t.dataset.check, t.checked ? 'done' : null);
    if (t.id === 'jump') return go(t.value);
    if (t.id === 'restore') { readBackup(t.files && t.files[0]); t.value = ''; return undefined; }
    if (t.matches('#f-status, #f-kind, #f-src')) renderAll();
    return undefined;
  });
  document.addEventListener('input', ev => {
    const t = ev.target;
    if (t.matches('input[data-field]')) return setField(t.dataset.field, t.value, t);
    if (t.id === 'q') { clearTimeout(qTimer); qTimer = setTimeout(renderAll, 150); }
    return undefined;
  });
  document.addEventListener('click', ev => {
    const t = ev.target.closest('button, tr[data-go]');
    if (!t) return undefined;
    const d = t.dataset;
    if (t.id === 'prev' || t.id === 'next') { const { list, i } = posOf(S.view); const n = list[i + (t.id === 'next' ? 1 : -1)]; return n ? go(n.id) : undefined; }
    if (t.id === 'resume') return nextOpen();
    if (t.id === 'find') return find();
    if (t.id === 'dim') { S.dim = !S.dim; save(); return renderHeader(); }
    if (t.id === 'prof-chip') { showTab('data'); setTimeout(() => { const fd = $('#flightdata'); if (fd) fd.scrollIntoView({ block: 'start', behavior: smooth() }); }, 0); return undefined; }
    if (t.id === 'clear-filters') { $('#q').value = ''; $('#f-status').value = 'all'; $('#f-kind').value = 'all'; $('#f-src').value = 'all'; return renderAll(); }
    if (d.info) return toggleInfo(t);
    if (d.na) return setCheck(d.na, S.checks[d.na] === 'na' ? null : 'na');
    if (d.prof) return setProfile(d.prof, d.val, t);
    if (d.mode) { S.mode = d.mode; save(); return renderStage(); }
    if (d.tab) return showTab(d.tab);
    if (d.cl) return openChecklist(d.cl);
    if (d.clreset) return resetIds(activeItems(PH.get(d.clreset)).map(it => it.id));
    if (d.act) return act(d.act, t);
    if (d.go) return go(d.go, { item: d.item, cl: d.clgo });
    return undefined;
  });
  document.addEventListener('keydown', ev => {
    const el = ev.target;
    const tag = (el.tagName || '').toLowerCase();
    const typing = (tag === 'input' && el.type !== 'checkbox') || tag === 'textarea' || tag === 'select' || el.isContentEditable;
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k') { ev.preventDefault(); find(); return; }
    if (typing || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (el.closest && el.closest('[role="tablist"]') && (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight' || ev.key === 'Home' || ev.key === 'End')) {
      ev.preventDefault();
      const i = TABS.indexOf(S.tab);
      const n = ev.key === 'Home' ? 0 : ev.key === 'End' ? TABS.length - 1 : (i + (ev.key === 'ArrowRight' ? 1 : -1) + TABS.length) % TABS.length;
      showTab(TABS[n], true);
      return;
    }
    if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') {
      const { list, i } = posOf(S.view);
      const n = list[i + (ev.key === 'ArrowRight' ? 1 : -1)];
      if (n) { ev.preventDefault(); go(n.id); }
    } else if (ev.key === 'n' || ev.key === 'N') { ev.preventDefault(); nextOpen(); }
    else if (ev.key === '/') { ev.preventDefault(); find(); }
  });
  window.addEventListener('hashchange', () => { const h = decodeURIComponent(location.hash.slice(1)); if (isView(h) && h !== S.view) go(h, { focus: false }); });

  // ---------- Start ----------
  const h = decodeURIComponent(location.hash.slice(1));
  if (isView(h)) { S.view = h; if (PH.get(h).kind === 'flow') S.lastFlow = h; }
  // Direktlinks: ?tab=cl öffnet einen Reiter, ?mode=learn die Lernansicht (z. B. als Lesezeichen)
  const qs = new URLSearchParams(location.search);
  if (TABS.includes(qs.get('tab'))) S.tab = qs.get('tab');
  if (['flight', 'learn'].includes(qs.get('mode'))) S.mode = qs.get('mode');
  renderEverything();
  $('#credits').textContent = `Nur für die Flugsimulation – kein Dokument für den echten Flugbetrieb. ${D.meta.aircraft} · Stand ${D.meta.date.split('-').reverse().join('.')} · ${D.meta.basis}`;
})();
