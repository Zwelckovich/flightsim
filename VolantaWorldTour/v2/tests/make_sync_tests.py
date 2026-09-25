"""Erzeugt selbstprüfende Testseiten für Fortschritt, Cloud-Abgleich, Reset und Wiederherstellung.

Aufruf:  python v2/tests/make_sync_tests.py
Danach die Seiten aus v2/tests/out/ im Browser öffnen (z. B. über `python -m http.server`).
Jede Seite spielt ein Szenario mit simulierter Cloud-Datenbank durch und zeigt oben PASS oder FAIL.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PAGE = (HERE.parent.parent / "Volanta-Worldtour-V2.html").read_text(encoding="utf-8")

# Die Tests dürfen den echten Fortschritt nie berühren: eigener Speicherschlüssel im
# eingebetteten App-Code und im Testtreiber. Bricht ab, falls die Stelle im App-Code fehlt.
REAL_KEY = "weltreise-edlv-v2"
TEST_KEY = "weltreise-edlv-v2-test"
KEY_LINE = f"const LS_KEY = '{REAL_KEY}';"
if PAGE.count(KEY_LINE) != 1 or PAGE.count(f"'{REAL_KEY}'") != 1:
    raise SystemExit("Speicherschlüssel im App-Code nicht eindeutig gefunden – Tests nicht erzeugt.")
PAGE = PAGE.replace(KEY_LINE, f"const LS_KEY = '{TEST_KEY}';")
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

MOCK = """<script>
// Simulierte Artifact-Datenbank (nur für Tests)
window.__realKeyBefore = localStorage.getItem('__REAL_KEY__');
localStorage.setItem('__TEST_KEY__', JSON.stringify(__LOCAL__));
const store = __CLOUD__;
window.__writes = []; window.__store = store;
const subs = {};
const snapOf = c => ({ docs: Object.entries(store[c] || {}).map(([id, d]) => ({ id, exists: true, data: () => d })) });
const notify = k => (subs[k] || []).forEach(f => f());
window.__notify = notify;
const db = {
  collection: c => ({
    onSnapshot(next) { (subs[c] ||= []).push(() => next(snapOf(c))); setTimeout(() => next(snapOf(c)), 20); return () => {}; },
    doc: id => ({
      set: async d => { (store[c] ||= {})[id] = d; __writes.push(c + '/' + id); notify(c); },
      delete: async () => { delete (store[c] || {})[id]; __writes.push(c + '/' + id + ':del'); notify(c); },
    }),
    get: async () => snapOf(c),
  }),
  doc: path => { const [c, id] = path.split('/'); return {
    onSnapshot(next) { const f = () => next({ exists: !!(store[c] || {})[id], data: () => (store[c] || {})[id] }); (subs[path] ||= []).push(f); setTimeout(f, 10); return () => {}; },
    set: async d => { (store[c] ||= {})[id] = d; __writes.push(c + '/' + id); notify(path); },
  }; },
};
window.claude = { use: async name => (name === 'db' ? db : null) };
</script>"""

DRIVER = """<script>
(async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const ls = () => JSON.parse(localStorage.getItem('__TEST_KEY__'));
  const flown = () => { const s = ls(); return Object.entries(s.marks).filter(([k, v]) => v.on && v.t > s.epochs.progress).map(([k]) => k).sort(); };
  const uploadedLegs = () => __writes.filter(p => p.startsWith('flown/')).map(p => __store.flown[p.slice(6)].legId).sort();
  const confirmed = () => Number((document.getElementById('count').innerText.match(/(\\d+) bestätigt/) || [])[1]);
  const reset = async (progress, volanta) => {
    document.getElementById('tab-data').click(); await wait(50);
    document.getElementById('rs-progress').checked = progress;
    document.getElementById('rs-volanta').checked = volanta;
    document.getElementById('rs-go').click(); document.getElementById('rs-yes').click(); await wait(200);
  };
  const restore = async obj => {
    const dt = new DataTransfer();
    dt.items.add(new File([JSON.stringify(obj)], 'sicherung.json', { type: 'application/json' }));
    const inp = document.getElementById('restore'); inp.files = dt.files;
    inp.dispatchEvent(new Event('change', { bubbles: true })); await wait(200);
  };
  const checks = [];
  const expect = (what, got, want) => checks.push({ what, ok: JSON.stringify(got) === JSON.stringify(want), got, want });
  await wait(300);
  __STEPS__
  expect('echter Fortschritt im Browser unverändert', localStorage.getItem('__REAL_KEY__') === window.__realKeyBefore, true);
  localStorage.removeItem('__TEST_KEY__');
  const ok = checks.every(c => c.ok);
  document.title = (ok ? 'PASS' : 'FAIL') + ' · __NAME__';
  const bar = document.createElement('pre');
  bar.id = 'testresult';
  bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99;margin:0;padding:8px 12px;font:12px Consolas,monospace;white-space:pre-wrap;color:#fff;background:' + (ok ? '#1f6b3a' : '#8a2b1f');
  bar.textContent = (ok ? 'PASS' : 'FAIL') + ' · __NAME__\\n' + checks.map(c => (c.ok ? '✓ ' : '✗ ') + c.what + ' → ' + JSON.stringify(c.got) + (c.ok ? '' : '  (erwartet ' + JSON.stringify(c.want) + ')')).join('\\n');
  document.body.appendChild(bar);
})();
</script>"""

M = lambda on, at, t: {"on": on, "at": at, "t": t}
EMPTY_CLOUD = {"flown": {}, "volanta": {}, "debriefs": {}, "meta": {}}
SCENARIOS = {
    "1-merge-lokal-und-cloud": dict(
        local={"v": 3, "marks": {"L001": M(True, "2026-09-20", 1000), "L002": M(True, "2026-09-21", 2000), "L003": M(True, "2026-09-22", 3000)},
               "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "flown": {"L001": {"legId": "L001", **M(True, "2026-09-20", 1000)}, "L003": {"legId": "L003", **M(False, "2026-09-22", 5000)}}},
        steps="""await wait(200);
  expect('lokal ergänztes L002 bleibt, in der Cloud entferntes L003 ist weg', flown(), ['L001', 'L002']);
  expect('nur L002 wird hochgeladen', uploadedLegs(), ['L002']);"""),
    "2-zweites-geraet-nach-reset": dict(
        local={"v": 3, "marks": {"L001": M(True, "2026-09-20", 1000), "L002": M(True, "2026-09-21", 2000), "L010": M(True, "2026-09-25", 6000)},
               "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "meta": {"reset": {"progress": 4000, "volanta": 4000}}},
        steps="""await wait(200);
  expect('nur das nach dem Reset geflogene L010 zählt', flown(), ['L010']);
  expect('nichts Veraltetes wird hochgeladen', uploadedLegs(), ['L010']);"""),
    "3-sicherung-nach-reset-wiederherstellen": dict(
        local={"v": 3, "marks": {"L001": M(True, "2026-09-20", 1000)}, "vstates": {"DE": {"s": "credited", "t": 1500}},
               "epochs": {"progress": 0, "volanta": 0}},
        cloud=EMPTY_CLOUD,
        steps="""await wait(200);
  const s0 = ls();
  const backup = { app: 'weltreise-edlv', version: 3, marks: s0.marks, vstates: s0.vstates, epochs: s0.epochs };
  await reset(true, true);
  expect('nach dem Reset ist nichts geflogen', flown(), []);
  await restore(backup);
  expect('nach dem Laden der Sicherung ist L001 wieder geflogen', flown(), ['L001']);
  expect('Volanta-Status aus der Sicherung ist wieder da', confirmed(), 1);"""),
    "4a-altes-cloud-format-ohne-zeitstempel": dict(
        local={"v": 3, "marks": {}, "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "flown": {"L005": {"legId": "L005", "at": "2026-09-24", "from": "EGLL", "to": "EGJJ"}}},
        steps="""await wait(200);
  expect('alter Cloud-Eintrag ohne on/t zählt als geflogen', flown(), ['L005']);"""),
    "4b-altes-cloud-format-nach-reset": dict(
        local={"v": 3, "marks": {}, "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "flown": {"L005": {"legId": "L005", "at": "2026-09-24", "from": "EGLL", "to": "EGJJ"}},
               "meta": {"reset": {"progress": 5000, "volanta": 0}}},
        steps="""await wait(200);
  expect('alter Cloud-Eintrag vor einem späteren Reset zählt nicht', flown(), []);"""),
    "5-volanta-reset-mit-debriefing": dict(
        local={"v": 3, "marks": {}, "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "debriefs": {"L001": {"legId": "L001", "from": "EDLV", "to": "EHAM", "status": "draft",
                                                   "updatedAt": "2026-09-20", "volanta": "credited"}}},
        steps="""await wait(200);
  expect('Debriefing bestätigt Deutschland und Niederlande', confirmed(), 2);
  await reset(false, true);
  expect('nach dem Volanta-Reset zählt das alte Debriefing nicht mehr', confirmed(), 0);
  __store.debriefs.L002 = { legId: 'L002', from: 'EHAM', to: 'EBBR', status: 'draft', updatedAt: '2026-09-24',
                            volanta: 'credited', volantaAt: new Date(Date.now() + 1000).toISOString() };
  __notify('debriefs'); await wait(100);
  expect('ein nach dem Reset erfasstes Debriefing zählt wieder', confirmed(), 2);
  expect('das Tagebuch bleibt erhalten', Object.keys(__store.debriefs).sort(), ['L001', 'L002']);"""),
    "6-verspaetete-aenderung-nach-geschlossenem-geraet": dict(
        local={"v": 3, "marks": {}, "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "flown": {
            "newer_event": {"legId": "L001", **M(False, "2026-09-24", 2000)},
            "delayed_event": {"legId": "L001", **M(True, "2026-09-24", 1000)}},
            "volanta": {"newer_event": {"code": "DE", "s": "credited", "t": 2000},
                        "delayed_event": {"code": "DE", "s": "not_credited", "t": 1000}}},
        steps="""expect('neues Gerät berücksichtigt den neueren erhaltenen Eintrag', flown(), []);
  expect('neuere Volanta-Bestätigung bleibt erhalten', confirmed(), 1);"""),
    "7-unabhaengige-reset-eintraege": dict(
        local={"v": 3, "marks": {}, "vstates": {}, "epochs": {"progress": 0, "volanta": 0}},
        cloud={**EMPTY_CLOUD, "flown": {"L001": {"legId": "L001", **M(True, "2026-09-24", 1000)}},
               "volanta": {"DE": {"code": "DE", "s": "credited", "t": 1000}},
               "resets": {"p5000_v0": {"progress": 5000, "volanta": 0}, "p0_v6000": {"progress": 0, "volanta": 6000}}},
        steps="""expect('Fortschrittsreset bleibt erhalten', flown(), []);
  expect('Volanta-Reset bleibt unabhängig erhalten', confirmed(), 0);
  expect('beide Reset-Zeitpunkte übernommen', ls().epochs, {progress: 5000, volanta: 6000});"""),
}

for name, sc in SCENARIOS.items():
    mock = (MOCK.replace("__LOCAL__", json.dumps(sc["local"])).replace("__CLOUD__", json.dumps(sc["cloud"]))
            .replace("__TEST_KEY__", TEST_KEY).replace("__REAL_KEY__", REAL_KEY))
    driver = (DRIVER.replace("__STEPS__", sc["steps"]).replace("__NAME__", name)
              .replace("__TEST_KEY__", TEST_KEY).replace("__REAL_KEY__", REAL_KEY))
    page = PAGE.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + mock, 1).replace("</html>", driver + "\n</html>")
    (OUT / f"{name}.html").write_text(page, encoding="utf-8")
    print("erzeugt:", f"out/{name}.html")
