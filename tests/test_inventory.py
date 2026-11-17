import json
from pathlib import Path
import unittest
from lab.inventory import scenario_inventory
from lab.scenarios import SCENARIOS

ROOT=Path(__file__).resolve().parents[1]

class InventoryTests(unittest.TestCase):
    def test_all_25_implementations_and_proofs_exist(self):
        entries=scenario_inventory()
        self.assertEqual([e['number'] for e in entries],list(range(1,26)))
        self.assertEqual(len({e['id'] for e in entries}),25)
        for entry in entries:
            for group in ('vulnerable_files','fixed_files','proof_files','test_files'):
                for name in entry[group]:
                    with self.subTest(scenario=entry['number'],file=name):
                        self.assertTrue((ROOT/name).is_file())
                        self.assertGreater((ROOT/name).stat().st_size,0)
    def test_registry_and_inventory_agree(self):
        local=[e for e in scenario_inventory() if e['runtime']=='local-python']
        self.assertEqual({e['id'] for e in local},set(SCENARIOS))
        for entry in local:
            self.assertEqual(SCENARIOS[entry['id']][2],entry['cwe'])
    def test_primary_mappings_match_the_recorded_official_sources(self):
        source=json.loads((ROOT/'docs/evidence/audit-mapping-sources.json').read_text())['categories']
        for entry in scenario_inventory():
            with self.subTest(scenario=entry['number']):
                if entry['mapping_basis']=='contextual':
                    self.assertEqual(entry['number'],5)
                    self.assertIn('not in',entry['mapping_note'])
                else:
                    self.assertIn(entry['cwe'],source[entry['owasp_primary']]['cwes'])
    def test_new_walkthrough_mapping_matches_catalog(self):
        for entry in scenario_inventory()[5:]:
            path=ROOT/f"scenarios/{entry['number']:02d}-{entry['id']}/README.md"
            mapping='/'.join([entry['owasp_primary'],*entry['owasp_related']])
            self.assertIn(f"**OWASP Top 10:2025:** {mapping}",path.read_text())
            self.assertIn(entry['cwe'],path.read_text())
