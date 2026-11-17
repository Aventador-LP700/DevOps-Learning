import unittest
from scripts.zap import evaluate_zap

class DASTGateTests(unittest.TestCase):
    def test_medium_and_high_are_blocking(self):
        alerts, blocking = evaluate_zap({'site': [{'alerts': [{'riskcode':str(n)} for n in range(4)]}]})
        self.assertEqual(len(alerts), 4)
        self.assertEqual([x['riskcode'] for x in blocking], ['2','3'])
    def test_empty_valid_scan_is_accepted(self):
        self.assertEqual(evaluate_zap({'site': [{'alerts': []}]}), ([], []))
    def test_missing_malformed_and_unknown_risk_fail_closed(self):
        for report in (None, {}, {'site': []}, {'site': [{}]}, {'site': [{'alerts':[{'riskcode':'unknown'}]}]}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                evaluate_zap(report)
