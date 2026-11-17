"""Shared assertions; each lab supplies observations from its own real implementations."""
from pathlib import Path
import tempfile
import unittest

class LabContract(unittest.TestCase):
    demonstrate = None
    @classmethod
    def setUpClass(cls):
        if cls.demonstrate is None:
            raise unittest.SkipTest("Abstract scenario contract")
        with tempfile.TemporaryDirectory(prefix="pipelineproof-contract-") as directory:
            cls.result = cls.demonstrate(Path(directory))
    def test_vulnerability_is_reproduced(self):
        self.assertTrue(self.result["vulnerable_exploited"], self.result["evidence"])
    def test_same_attack_is_blocked(self):
        self.assertTrue(self.result["secure_blocked"], self.result["evidence"])
    def test_legitimate_operation_still_works(self):
        self.assertTrue(self.result["legitimate_allowed"], self.result["evidence"])
