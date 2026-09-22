"""Validate reported flight facts before embedding them; generate the readable journal."""
import json
import re
from datetime import date
from pathlib import Path

TOUR = 'EDLV-2026-09-v1'
TEXT_FIELDS = ('aircraft', 'approach', 'conditions', 'highlights', 'issues', 'verdict', 'nextTime')


def require(condition, message):
    if not condition:
        raise ValueError('Debriefing: ' + message)


def optional_text(value, label):
    require(value is None or isinstance(value, str) and bool(value.strip()), label + ' muss Text oder null sein.')


def valid_date(value, label, optional=False):
    if optional and value is None:
        return
    require(isinstance(value, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)), label + ': YYYY-MM-DD erwartet.')
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ValueError('Debriefing: ungültiges Datum für ' + label) from error


def route_legs(project):
    work = Path(project) / 'work'
    main = json.loads((work / 'tour-data.json').read_text(encoding='utf8'))
    side = json.loads((work / 'excursions.json').read_text(encoding='utf8'))
    result = []
    for leg in main['legs']:
        result.append(leg)
        for excursion in side['excursions']:
            if excursion['afterLeg'] == leg['id']:
                result.extend(excursion['legs'])
    return result


def validate_archive(archive, legs):
    require(isinstance(archive, dict), 'Archiv muss ein Objekt sein.')
    require(type(archive.get('schemaVersion')) is int and archive['schemaVersion'] == 1, 'Unbekannte Schema-Version.')
    require(archive.get('tour') == TOUR, 'Falsche Tour.')
    require(isinstance(archive.get('entries'), list), 'entries muss eine Liste sein.')
    route = {str(leg['id']): leg for leg in legs}
    seen = set()
    for entry in archive['entries']:
        require(isinstance(entry, dict), 'Eintrag muss ein Objekt sein.')
        key = entry.get('legId')
        require(isinstance(key, str) and key in route, 'Unbekannte Leg-ID: ' + str(key))
        require(key not in seen, 'Doppelte Leg-ID: ' + key)
        seen.add(key)
        leg = route[key]
        require(entry.get('from') == leg['from'] and entry.get('to') == leg['to'], 'Strecke stimmt nicht mit Leg ' + key + ' überein.')
        require(entry.get('status') in ('draft', 'final'), 'Status muss draft oder final sein.')
        valid_date(entry.get('updatedAt'), 'updatedAt')
        valid_date(entry.get('flightDate'), 'flightDate', optional=True)
        for field in TEXT_FIELDS:
            optional_text(entry.get(field), field)
        require(entry.get('volanta') in ('open', 'credited', 'not_credited'), 'Volanta-Status fehlt oder ist ungültig.')
        scenery = entry.get('actualScenery')
        require(isinstance(scenery, dict), 'actualScenery fehlt.')
        for end in ('departure', 'arrival'):
            actual = scenery.get(end)
            require(isinstance(actual, dict), end + ' fehlt.')
            optional_text(actual.get('product'), end + '.product')
            optional_text(actual.get('version'), end + '.version')
            if entry['status'] == 'final':
                require(bool(actual.get('product')), 'Finalbericht benötigt tatsächlich verwendete Szenerie für ' + end + '.')
        optional_text(scenery.get('landscape'), 'landscape')
    return archive


def read_archive(project):
    project = Path(project)
    archive = json.loads((project / 'debriefings.json').read_text(encoding='utf8'))
    return validate_archive(archive, route_legs(project))


def markdown_text(value):
    if not value:
        return 'Noch nicht angegeben'
    # User reports are plain text, including any angle brackets or Markdown syntax.
    value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'([\\`*_{}\[\]()#+.!|~-])', r'\\\1', value).replace('\n', '  \n')


def write_journal(project, archive):
    project = Path(project)
    entries = {entry['legId']: entry for entry in archive['entries']}
    lines = ['# Worldtour · Debriefings', '',
             'Aus den berichteten Flügen in `debriefings.json` erzeugt. Empfehlungen und Flug-Häkchen sind keine Nutzungsnachweise.', '',
             f"{sum(entry['status'] == 'final' for entry in entries.values())} final dokumentiert · {sum(entry['status'] == 'draft' for entry in entries.values())} mit offenen Angaben.", '']
    if not entries:
        lines += ['Noch kein Flug debrieft. Nach dem ersten Flug halten wir die tatsächlich verwendeten Szenerien und deine Eindrücke fest.', '']
    labels = [('flightDate', 'Flugdatum'), ('aircraft', 'Tatsächlich geflogenes Flugzeug'),
              ('approach', 'Anflug / Bahn / Landeplatz'), ('conditions', 'Wetter und Tageszeit'),
              ('highlights', 'Highlight'), ('issues', 'Performance und Probleme'),
              ('verdict', 'Szenerie-Fazit'), ('nextTime', 'Für das nächste Mal')]
    for sequence, leg in enumerate(route_legs(project), 1):
        entry = entries.get(str(leg['id']))
        if not entry:
            continue
        lines += [f"## Flug {sequence:03d} · Leg-ID {leg['id']} · {leg['from']} → {leg['to']}", '',
                  f"**{'Final dokumentiert' if entry['status'] == 'final' else 'Angaben offen'}** · Bearbeitet: {entry['updatedAt']}", '']
        for side, code in [('departure', leg['from']), ('arrival', leg['to'])]:
            actual = entry['actualScenery'][side]
            lines += [f"**Tatsächlich verwendet · {code}:** {markdown_text(actual.get('product'))}  ",
                      f"Version: {markdown_text(actual.get('version'))}", '']
        lines += ['**Landschafts-/Stadt-Add-ons:** ' + markdown_text(entry['actualScenery'].get('landscape')), '']
        for key, label in labels:
            lines += ['**' + label + ':** ' + markdown_text(entry.get(key)), '']
        status = {'open': 'Noch nicht geprüft', 'credited': 'Laut Bericht gutgeschrieben', 'not_credited': 'Laut Bericht nicht gutgeschrieben'}
        lines += ['**Volanta-Wertung:** ' + status[entry['volanta']], '']
    (project / 'outputs' / 'Debriefings.md').write_text('\n'.join(lines), encoding='utf8')
