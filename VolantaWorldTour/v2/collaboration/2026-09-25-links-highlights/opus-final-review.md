**Verdict: no blocker.** Every point you asked me to check is addressed. I only read the code. The test PASS results come from Astra.

| Check | Result |
|---|---|
| `promote` only for TFFJ | ✅ `highlight-audit.json:22` is the only `"promote"` in the file. `build_v2.py:524-527` only raises the level to 2 when `promote is True` and the airport has real arrivals. `tag` and `hl` use `setdefault`, so wording from `content.json` still wins. KLAS, KSFO, VHHH and the other airports keep their editorial level. |
| `highlightSources` removed | ✅ It no longer appears in `build_v2.py` or `app.js`. |
| Clicks in the expanded references | ✅ `app.js:1355` now excludes `a, summary, .scenery-references`. |
| simCheck URL dedup | ✅ At `app.js:482-483`, links already shown as simCheck sources are filtered out of the references. It works for both plain strings and `{url}` objects. |
| Duplicate URL rejection | ✅ `build_v2.py:277-279` now fails the build on a duplicate URL within an airport. |
| Missing `airports` list | ✅ `build_v2.py:505-506` now exits with a clear message instead of a `KeyError`. |
| Route migration warning | ✅ Stated in the audit intro at `app.js:1049`: IDs stay the same in this update, and a later route change needs stable IDs or a progress migration. |
| EGLC | ✅ `highlight-audit.json:320` now says clearly that neither preferred aircraft can make a regular landing, rules out a Twin Otter, and drops "Hohe Priorität". |
| VHHH | ✅ The sources are now a VHHH 25R approach thread and the Hong Kong CAD page (`:153-154`). The FR24 Kai Tak mention is gone. |
| Saba | ✅ The West Indies Helicopters operator link was added (`:308`). |
| No route changes | ✅ `route.json` isn't in the git status snapshot. `tour-v2.json` is modified, but it's generated build output. I didn't diff it. |

**Remaining minor points (P3, none blocking):**
- **EGLC wording:** "H160-Landung … nicht als reguläre Option belegt" is still softer than the actual rule, which bans helicopters at London City except rescue, police and SAR. The practical outcome (no landing) is correct, though.
- **Still-open P3-5 validation gaps:**
  - Unknown fields in `scenery-links` and audit entries aren't checked.
  - The link corrections only match exact URLs, so a variant (e.g. with a trailing slash) would slip through without a warning.
  - Duplicates are only caught within one airport.
  - An audit entry without `icao` would still raise a `KeyError`.

I didn't re-check the 339 refs, the four new product links or the corrected OOMS aerial-folder instruction. I'm relying on Astra's validation for those.