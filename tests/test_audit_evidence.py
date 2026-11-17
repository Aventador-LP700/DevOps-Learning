"""Validate evidence format/freshness only; these fixtures do not run scenario 05."""
from datetime import datetime, timedelta, timezone
import unittest
from scripts.audit_scenarios import verify_kubernetes

class EvidenceValidationTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime.now(timezone.utc)
        self.report={'scenario':'excessive-deployment-permissions','generated_at':self.now.isoformat(),
                     'vulnerable_secret_read':True,'hardened_secret_read_forbidden':True,
                     'hardened_deployment_patch_allowed':True,'passed':True}
    def test_each_real_api_assertion_is_required(self):
        self.assertIs(verify_kubernetes(self.report,self.now),self.report)
        for key in ('vulnerable_secret_read','hardened_secret_read_forbidden','hardened_deployment_patch_allowed','passed'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_kubernetes(dict(self.report,**{key:False}),self.now)
    def test_stale_future_and_naive_timestamps_are_rejected(self):
        for stamp in ((self.now-timedelta(hours=1)).isoformat(), (self.now+timedelta(minutes=5)).isoformat(), self.now.replace(tzinfo=None).isoformat()):
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                verify_kubernetes(dict(self.report,generated_at=stamp),self.now)
