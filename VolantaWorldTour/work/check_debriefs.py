"""Regression checks for preserving reported facts and rejecting mismatched flights."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from debrief_data import read_archive, route_legs, validate_archive, write_journal

PROJECT = Path(__file__).resolve().parent.parent
LEGS = route_legs(PROJECT)


def report(leg, status='final'):
    return {
        'legId': str(leg['id']), 'from': leg['from'], 'to': leg['to'],
        'status': status, 'updatedAt': '2026-09-22', 'flightDate': None,
        'actualScenery': {'departure': {'product': 'Explicitly reported departure', 'version': None},
                          'arrival': {'product': 'Explicitly reported arrival', 'version': '1.2'},
                          'landscape': None},
        'volanta': 'open',
    }


def archive(*entries):
    return {'schemaVersion': 1, 'tour': 'EDLV-2026-09-v1', 'entries': list(entries)}


class DebriefChecks(unittest.TestCase):
    def test_project_archive_matches_route(self):
        self.assertEqual(len(LEGS), 449)
        read_archive(PROJECT)

    def test_all_three_aircraft_and_missing_optional_facts(self):
        side = json.loads((PROJECT / 'work/excursions.json').read_text(encoding='utf8'))
        examples = [LEGS[0]] + [next(e for e in side['excursions'] if e['profile'] == profile)['legs'][0] for profile in ('H160', 'DHC6')]
        data = archive(*(report(leg) for leg in examples))
        original = copy.deepcopy(data)
        self.assertIs(validate_archive(data, LEGS), data)
        self.assertEqual(data, original, 'Validation must not fill unknown facts or recommendations.')

    def test_wrong_leg_duplicate_and_wrong_endpoints_rejected(self):
        entry = report(LEGS[0])
        for data in [archive(entry, entry), archive(dict(entry, legId='not-a-leg')),
                     archive(dict(entry, to='ZZZZ')), archive(dict(entry, legId=entry['legId'] + '0'))]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_archive(data, LEGS)

    def test_final_requires_both_actual_airports_but_draft_can_wait(self):
        for end in ('departure', 'arrival'):
            entry = report(LEGS[0])
            entry['actualScenery'][end]['product'] = None
            with self.assertRaises(ValueError):
                validate_archive(archive(entry), LEGS)
            entry['status'] = 'draft'
            validate_archive(archive(entry), LEGS)

    def test_dates_types_status_and_tour(self):
        base = report(LEGS[0])
        for patch in [{'flightDate': '2026-02-30'}, {'updatedAt': '2026-9-22'}, {'status': 'done'},
                      {'volanta': True}, {'aircraft': ['A320']}, {'issues': ''}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate_archive(archive(dict(base, **patch)), LEGS)
        with self.assertRaises(ValueError):
            validate_archive(dict(archive(base), tour='other-tour'), LEGS)

    def test_journal_reports_facts_and_open_fields(self):
        entry = report(LEGS[0])
        entry['highlights'] = '<script>alert(1)</script>\nRidge approach'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'work').mkdir()
            (root / 'outputs').mkdir()
            for name in ('tour-data.json', 'excursions.json'):
                (root / 'work' / name).write_bytes((PROJECT / 'work' / name).read_bytes())
            write_journal(root, archive(entry))
            text = (root / 'outputs/Debriefings.md').read_text(encoding='utf8')
            self.assertIn('Explicitly reported departure', text)
            self.assertIn('Noch nicht angegeben', text)
            self.assertIn('Noch nicht geprüft', text)
            self.assertNotIn('<script>', text)
            self.assertIn('&lt;script&gt;', text)
            write_journal(root, archive())
            self.assertIn('Noch kein Flug debrieft', (root / 'outputs/Debriefings.md').read_text(encoding='utf8'))


if __name__ == '__main__':
    unittest.main(verbosity=1)
