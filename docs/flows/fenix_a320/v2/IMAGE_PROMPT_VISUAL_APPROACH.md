# Visual Approach · Bildgestaltung

OpenAI Image wurde für Gestaltungsstudien eingesetzt. Drei Rasterentwürfe wurden visuell mit der V1-Grafik verglichen. Kontrast, eine falsche Höhenbemaßung und eine unterbrochene Bodenprojektion verhinderten ihre Verwendung als endgültige Trainingsgrafik. `visual-approach-image-study.png` dokumentiert den letzten Entwurf, nicht den finalen Diagrammstand.

Die finale `visual-approach-v2.svg` ist eine eigenständige technische Reinzeichnung nach dem Gestaltungsentwurf. Sie verwendet kontrollierte Texte und Koordinaten. Die SVG ist in der V2-HTML eingebettet. Die Originalgrafik ist unverändert zum Vergleich erreichbar. Quellenwerte sind aus Blackbox711, Visual Approach A320 übernommen; keine zusätzliche universelle Fenix-Verfahrensfreigabe.

## Letzter OpenAI-Image-Prompt

Create a NEW, precise A320 VISUAL APPROACH flight-simulator training diagram on completely opaque flat WHITE paper, landscape 1536x1024. Clean navy text, blue flight path, teal heading fields and pale amber instruction fields. No aircraft silhouettes, no photorealism, no gradients, no shadows. Simple circles mark points on the continuous path. Small arrowheads show downwind RIGHT TO LEFT, then a descending left base turn, then final to the lower-right runway. No invented numbers.

Exact layout:
- Downwind: a perfectly HORIZONTAL blue solid line at y=320, from x=1450 to x=400.
- Base: curve left from (400,320), through (225,370) and (205,500), to (335,650).
- Final: smooth sloping blue line from (335,650) through (650,760) to runway threshold (1110,860).
- A simple flat gray foreshortened runway starts at (1110,860) and extends horizontally right, with white threshold stripes but NO RUNWAY NUMBER.
- Dashed gray GROUND PROJECTION: a perfectly horizontal line at y=440 from x=1450 to x=400, curving round farther left and lower than the blue base, then continuing toward the runway threshold. Distinct ground plane.
- CRITICAL: The ONLY vertical altitude bracket is at x=1310. It is a SHORT, DOUBLE-HEADED bracket from the solid downwind at (1310,320) to the dashed ground-projection line at (1310,440). Label it '1500 ft' to its right. Do NOT draw any vertical arrow from downwind to final; that would be a technical error.
- Abeam threshold is point (750,320). A short vertical dashed projection to (750,440). From the GROUND point (750,440), draw a thin slanted dimension arrow to the runway threshold (1110,860), label '≈ 2.5 NM'. This is ground spacing, not altitude.
- Above the downwind, at y=175, draw a horizontal timing dimension from x=400 (beginning of base) to x=750 (abeam threshold). Label '3 s / 100 ft' and '± 1 s / kt wind component'.

Title at top: 'A320 · VISUAL APPROACH'
Subtitle: 'Configuration, timing & flight path'

Callouts with thin unambiguous leaders, all readable, no overlaps; preserve exact sequence:
1. At far right point (1420,320), high on right: heading 'Abeam RWY', body 'APPR phase — ACTIVATE' / 'Speed — MANAGED' / 'F/Ds — OFF' / 'TRK/FPA — SELECT'.
2. At (1030,320): heading 'At green dot speed or below', body 'FLAPS 1'.
3. At (750,320): heading 'Abeam threshold', body 'START STOPWATCH'.
4. At (470,320), before the curve: heading 'Before turning base', body 'FLAPS 2'.
5. At (345,332), at the curve start, box placed far upper left: heading 'Turning base', body 'L/G DOWN' / 'SPOILERS ARM'.
6. At (210,495), box at left: heading 'When L/G down', body 'FLAPS 3'.
7. At (335,650), box at left: heading 'When below VFE', body 'FLAPS FULL'.
8. At (650,760), box above it: heading 'By 500 ft at the latest', body 'STABILISED' / 'Flaps FULL · target speed'.

Make typographic and spacing refinements if necessary without altering any geometrical meaning or leader destinations. All vertical altitude measurement is confined to the short gap between the parallel downwind and ground line at the right of the drawing. No other vertical measurement anywhere.
Footer bottom left, dark navy and fully readable:
'Source: Blackbox711 · Visual Approach A320'
'Visual redesign · Not to scale · For simulation use only'
Legend bottom right: blue solid 'Flight path'; gray dashed 'Ground projection'.
All labels fit inside page. Quality: restrained, precise vector-like training manual plate, pure white background, high legibility. No airplanes.
