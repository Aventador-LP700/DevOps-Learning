"""Discover the per-scenario vulnerable/fixed/positive regression contracts."""
import importlib
import unittest
from pathlib import Path

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for path in sorted((Path(__file__).resolve().parents[1] / "labs").glob("*/test_lab.py")):
        suite.addTests(loader.loadTestsFromModule(importlib.import_module(f"labs.{path.parent.name}.test_lab")))
    return suite
