**No blockers found.** I only read the code: I didn't run the build or any tests.

**What checks out**
- **Route and identities:** In chapter 07, `route` now goes `…KPHX, KSAN, KLAS…` and `legIds` goes `…L105, L389, L390, L107…` (`v2/route.json:284-311`). The pair counts line up. `L389` (KPHX→KSAN) and `L390` (KSAN→KLAS) both have `ch: "07"` (`v2/leg-identities.json:1943-1952`). `L106` is kept with `retired: true` (`:527-532`).
- **Identity enforcement:** `build_v2.py:358-360` requires an exact match on `{"f","t","ch"}`. Because of the extra `retired` key, `L106` can never match, so reusing it is rejected. Duplicate IDs are rejected through `used_main_ids`.
- **Numbering:** `n` is recomputed with `a320_n` in display order (`build_v2.py:362-365`). Legs after L105 move up by one and the A320 total goes up by one. The app only uses `n` for display (`legLabel`, `pad3(l.n)` at `app.js:34,431`), never for storage.
- **Progress, cloud and import:** Local marks, cloud docs and backup imports are all keyed by leg ID and filtered through `legIdx` (`app.js:77,80,190-191,1312,1326`). Old `L106` data is ignored cleanly and nothing crashes. Other IDs are unchanged, so their progress stays attached.
- **Debriefs:** They're validated by `legId` plus from/to (`build_v2.py:431-435`). The archive is empty, so there's nothing to migrate.
- **Built output:** `Volanta-Worldtour-V2.html` and `v2/dist/artifact.html` both contain `L389` and `L390` and no `L106`, so they look rebuilt. I checked this by searching the files, not by running the build.

**Minor points, none blocking**
1. **Old `L106` progress is dropped silently.** If a local, cloud or backup mark exists for `L106`, it disappears without a message, and the cloud doc stays behind unused. Only worth handling if KPHX→KLAS was actually flown.
2. **Part of a V1 import can be skipped.** The `KPHX>KLAS` entry from a V1 backup no longer matches any leg, so `app.js:1332` skips it without a message. Same effect as point 1.
3. **The build doesn't check for orphaned identities.** It never confirms that every non-retired entry in `leg-identities.json` is used by the route. A leg removed later without `retired: true` would still build.

Adding only KSAN matches your approval. I didn't check how the other missing highlights are held as proposals (`highlight-audit.json`).