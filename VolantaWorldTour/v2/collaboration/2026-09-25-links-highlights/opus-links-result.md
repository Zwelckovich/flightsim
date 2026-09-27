# Linkprüfung und Ergänzung – Ergebnis (Opus 5.5, Medium Effort)

Stand: 25.09.2026. Keine Unteragenten, keine Shell, keine Commits. Geschrieben wurden nur `v2/scenery-links.json` (neu), drei URL-Zeilen in `v2/content.json` und dieser Bericht.

## Ergebnis in Zahlen

| | Anzahl |
|---|---|
| Neue Datei `v2/scenery-links.json`: ICAO-Schlüssel | **230** |
| davon Link-Einträge insgesamt | **339** |
| … URL aus `v2/research-2026-09-24.json` (Freeware-/Payware-Slot der 289 Ergebnisse) | 297 |
| … URL aus älterer `work/`-Recherche (EGNS-Freeware 5919, MMUN-Freeware 17796) | 2 |
| … URL neu per WebSearch/WebFetch ermittelt | 40 |
| Korrigierte URLs in `v2/content.json` (Suchseite → Produktseite) | **3** (FSIA, HTKJ, DGAA) |
| Sonstige Änderungen an `content.json` (Status, Texte, Bewertungen, Highlights, Route) | 0 |
| Schlüssel, die nicht als Airport (`"i"`) in `tour-v2.json` vorkommen | 0 von 230 |
| Einträge, die eine bereits sichtbare `scenery.url`/`alt`/`dependency` am selben Airport duplizieren | 0 |
| Einträge mit Such- statt Produktlink | 0 |
| Nicht-https-URLs | 0 |

Alle `context`-Texte nennen den Status ausdrücklich („verworfen“, „nur zum Prüfen“, „keine Empfehlung“ oder „nur relevant, falls …“). Kein Kaufstatus und kein Qualitätsurteil wurde verändert.

## Umfang der Prüfung

- `content.json` vollständig gelesen: `airports` (hl, brief, tips), alle 170 `scenery`-Einträge (why, alt, dependencies, installNote), `handcrafted`, `ownedNotes`, `excursions`, `changes`, alle `defaultOk`-Texte, `trials` und `simChecks`.
- `research-2026-09-24.json`: Titel/Autor/Produkt/Entwickler/URL aller 289 `results` extrahiert und mit den Texten abgeglichen.
- `work/`: gezielt für Altbestände (EGNS, BIKF, TXKF, MMUN, LGSK, FIMP) in `payware-discovery.json`, `freeware-discovery.json` und `research-reviewed.json` gesucht.
- Aufgenommen wurde nur, was ein angezeigter Text **namentlich oder eindeutig beschreibend** erwähnt. Archiv-Produkte, die in keinem Text vorkommen, sind nicht aufgenommen, z. B. SLLP BoliviaVFR, SKBO fsotelo2, SEQM Ram249, LDDU edvingr, KSLC FeelThere, MMGL Magsoft, MBPV Final Approach, FZAA FSDG Kinshasa, FVFA „Victoria Falls V2“, OLBA Simsoft, GMMH Redwing, LYBE Fly2High und NZAA fras444.
- Grundlage: tatsächlich verwendete Airports aus `tour-v2.json`. EGLC (nur in `ownedNotes`) ist nicht in der Tour und deshalb nicht aufgenommen.

## Korrekturen in `content.json`

| Eintrag | Vorher | Nachher | Beleg |
|---|---|---|---|
| `scenery.FSIA.url` | `fsaddoncompare.com/search/FSIA` | `…/product/4701/Seychelles` | FSAC-Suche per WebFetch: FSDG „Seychelles“ 4,68 · 20 = Wert im Text |
| `scenery.HTKJ.url` | `…/search/HTKJ` | `…/product/4204/HTKJ-Kilimanjaro-Intl.-Airport` | FSAC-Suche: VueloSimple 4,33 · 18 = Wert im Text |
| `scenery.DGAA.url` | `…/search/DGAA` | `…/product/7817/DGAA-Kotoka-International-Airport` | FSAC-Suche: FSDG 4,57 · 18 (Marketplace-Listing, auf das sich das Rating bezieht). Die im Text genannte Shop-Version „Accra“ (4713) steht in `scenery-links.json`. |

## Neu per Web ermittelte URLs (40)

**Seite per WebFetch abgerufen** (FSAddonCompare-Suchseiten, Produkt und Bewertung mit dem Text abgeglichen):
- FIMP FSDG Mauritius 4704 (3,15 · 93)
- HAAB Barelli 10051
- FALE Gaffer 6202
- LRCL South Oak 9469
- HTZA South Oak 7523
- HKMO MSFScenerybuilders 1060
- FAOR NMG 10297 und iniBuilds 9660
- GVAC FSDG „Cape Verde Sal“ 13111
- GMMN FSDG Casablanca 12687
- LBSF Aflosim 5014
- OTHH MXI 3136
- OBBI Mfsg 5534
- UBBB Azrsim-Bundle 12091 und Ac Scenery 11843
- YPPH Orbx 12518 und Mfsg 8932
- MPTO DominicDesignTeam 14184
- MSLP PKSIM 14530
- TVSA FLYNDRIVE4D Caribbean Pack 2 9215
- SKCG V Pilot V2 6697
- DGAA FSDG Accra 4713
- ROAH MK Studios 9291 (4,91 · 35)
- ENTC M'M 4106 (3,55 · 64)
- LNMC: flightsim.to 11665 (T0kenDesign, 4,3 · 26) direkt abgerufen

**Nur als Treffer in WebSearch-Ergebnissen gesehen, Seite nicht abgerufen:**
- EGNS UK2000 FSAC 1407
- BIKF MK Studios FSAC 4361
- TXKF SLH FSAC 5413
- MMUN maccosim.com
- LGSK orbxdirect.com
- SEGS Ecuavirtual3d simMarket
- VHHH inibuilds.com
- VRMM fsdg-online.com
- SCGC Wolf's Fang inibuilds.com
- LYBE flightsim.to 50776
- HHAS Nevermind1982 105800
- VVTS Yoshino 44554
- VOPB arvind320 46016
- UTAA bymaxgames 81441
- AD-ALV Cami heliport 61560

**Ausdrücklich: Nicht alle URLs wurden live getestet.** Die 297 Archiv-URLs und die beiden `work/`-URLs habe ich unverändert übernommen und nicht erneut abgerufen.

Zwei Einträge sind im `context` als wahrscheinliche Zuordnung markiert: EGNS 5919 und MMUN 17796. Grundlage ist jeweils der einzige passende Treffer in der älteren Recherche; eine ausdrückliche Zuordnung im Text fehlt.

## Datenauffälligkeiten (nicht verändert, zur Entscheidung)

1. **OOMS** `installNote`: „Das hochauflösende Luftbild ist ein separates, empfohlenes Paket.“ Laut flightsim.to-Beschreibung (Suchtreffer) ist es ein optionaler Ordner („Aerial Imagery OPTIONAL“) im selben Download, kein eigenes Add-on.
2. **FAOR** `defaultOk`: NMG „3,25 aus 26“; FSAC zeigt am 25.09. 3,35 aus 27. Das Urteil ändert sich dadurch nicht; ich habe es nicht angepasst.
3. **LNMC** `defaultOk`: Autor „t0kenkiwi“; auf flightsim.to angezeigt als „T0kenDesign“. Das Label nutzt den angezeigten Namen, der `context` nennt beide.
4. **LCLK**: Die Archiv-URL `inibuilds-larnaca-lclk-msfs` trägt kein „2024“ im Slug, obwohl der Text von der MSFS-2024-Version spricht. Nicht geprüft.
5. **Archiv FVFA**: Im Freeware-Slot steht ein FSAC-Produkt („Victoria Falls V2 · Taburet“). Das ist eine Inkonsistenz im Archiv; der Eintrag wird nicht gerendert.
6. **simChecks**: Die URLs für ZMCK (Flyingplum 114241), ZZ-0002 (63230) und FMZJ (45110) stehen bereits als `simChecks.sources`. In `scenery-links.json` sind sie trotzdem enthalten, weil sie keine `scenery.url`/`alt`/`dependency` sind. Falls Astra die `simChecks`-Quellen auf derselben Karte zeigt, bitte dort deduplizieren.
7. **ELLX- und YPKG-Abhängigkeiten** verweisen auf dieselbe URL wie das Hauptpaket. Das ist gewollt (Datei im selben Download) und im Text erklärt.

## Offene, nicht eindeutig auflösbare Verweise

- MROC: „MSFS-2024-Erweiterung (Nyyoko, Aug. 2026)“. Gefunden wurden nur ein Claro-Billboard-Mod von Nyyoko (flightsim.to 95669) und eine X-Plane-Erweiterung, deshalb nicht verlinkt.
- SBCF: FlightSimAdventures-Freeware (5,0 aus 2) wurde nicht gefunden.
- BIKF: „die Freeware ist unfertig“ (nicht eindeutig).
- LGSK: „Freeware von 2020“ (nicht eindeutig).
- FIMP: „Freeware nur mittelmäßig“ (nicht eindeutig).
- RPMD: Bdoaviation-Payware.
- LCLK: JustSim (4,18 aus 51).
- LMML: JustSim (4,17 aus 89).
- LIKD: Pille83-Version für 2020.
- VTSP: „separates Update-Paket eines Dritten“.
- SCFA: „ältere Paywares“.
- FMZJ: Helipads FMZ1/FMZ2.
- OIIE: bamzi-Freeware (zum Download gesperrt).
- TIST: „Dave's 3D People Library“ (laut Text HTTP 404).
- TFFF: neun Objektbibliotheken (Liste nur in der Produktbeschreibung).
- PGUM, NSTU und OLBA: UK2000- bzw. ESD-Bibliothek. Diese gibt es nur im Marketplace, einen Web-Link dafür gibt es nicht.
- Bewusst nicht verlinkt:
  - Konfliktnennungen in `ENBO.installNote` (Real Taxiways, Andres3d, GSX-Jetways): Das sind Hinweise zum Deaktivieren, keine Angebote.
  - Besessene oder Basis-Sim-Inhalte (SimWings EDDM, Aerosoft Paderborn, EICK Cork).
  - `EGLC.ownedNotes` (FlightSim Studio E190/195, Just Flight BAe 146): EGLC ist nicht in der Tour.
- Airports mit „kein Add-on gefunden“ (z. B. CYWK, WABB, ZMKD, HCMH, HALA, FNME, DNSO, ZDM): Hier ist kein Produktlink möglich. Suchseiten als Quellen habe ich nicht aufgenommen.

## Statische Prüfung `scenery-links.json` (durch Lesen/Grep, kein Parser)

- 801 Zeilen: `{`, 230 Schlüsselzeilen `"ICAO": [`, 339 Eintragszeilen, 230 schließende `]`, `}`.
- Alle 339 Eintragszeilen entsprechen dem Muster `{"label": "…", "url": "https://…", "context": "…"}` mit optionalem Komma.
- Pro Array endet genau eine Zeile ohne Komma (230). Genau ein `]` ohne Komma steht vor dem abschließenden `}`. Keine Trailing Commas (Multiline-Grep auf `},\n]` ergab 0 Treffer).
- Keine ASCII-Anführungszeichen innerhalb der Strings; zitiert wird mit „…“.
- Alle 230 Schlüssel existieren als Airport in `tour-v2.json` (Grep-Zählung 230/230).
- Keine der neuen FSAC-Produkt-IDs und flightsim.to-IDs kommt als `scenery.url`, `alt` oder `dependency` in `content.json` vor. Die einzigen Treffer sind die drei `simChecks.sources` oben.
- `content.json`: Es wurden nur drei `url`-Stringwerte ersetzt; die Struktur ist unverändert.

Tests und Build führt Astra aus.
