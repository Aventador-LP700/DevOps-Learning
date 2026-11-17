"""End-to-end checks for the Docker-free entry point and its foreground server."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which('bash')

@unittest.skipUnless(os.name == 'posix' and BASH, 'Native setup requires Bash and POSIX')
class NativeSetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='pipelineproof-native-test-')
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        # Fail loudly if setup attempts to use a container/package installer.
        bin_dir = self.work / 'bin'
        bin_dir.mkdir()
        self.called = self.work / 'unexpected-tool'
        for tool in ('docker', 'make', 'pip', 'pip3', 'sudo'):
            wrapper = bin_dir / tool
            wrapper.write_text('#!/bin/sh\nprintf attempted > "$NATIVE_TEST_TOOL_MARKER"\nexit 99\n')
            wrapper.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ.get('PATH', ''),
                        NATIVE_TEST_TOOL_MARKER=str(self.called))
        self.reports = self.work / 'reports'

    def test_lab_only_from_directory_with_spaces(self):
        checkout = self.work / 'checkout with spaces'
        checkout.symlink_to(ROOT, target_is_directory=True)
        result = subprocess.run([BASH, str(checkout / 'setup.sh'), '--lab-only', '--output', str(self.reports)],
                                cwd=self.work, env=self.env, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.reports / 'assessment.json').read_text())
        self.assertTrue(report['passed'])
        self.assertEqual(report['execution_mode'], 'native')
        self.assertEqual(len(report['results']), 24)
        self.assertIn('Execution mode: native', (self.reports / 'assessment.md').read_text())
        self.assertFalse(self.called.exists())

    def test_default_runs_lab_then_serves_api(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        proc = subprocess.Popen([BASH, str(ROOT / 'setup.sh'), '--port', str(port), '--output', str(self.reports)],
                                cwd=self.work, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 15
            while True:
                if proc.poll() is not None:
                    self.fail(f'Setup exited unexpectedly: {proc.communicate()}')
                try:
                    with urlopen(f'http://127.0.0.1:{port}/health', timeout=1) as response:
                        self.assertEqual(json.load(response), {'status': 'ok'})
                    break
                except (URLError, TimeoutError):
                    if time.monotonic() >= deadline:
                        self.fail('Native API did not become healthy')
                    time.sleep(0.05)
            self.assertTrue(json.loads((self.reports / 'assessment.json').read_text())['passed'])
            self.assertFalse(self.called.exists())
        finally:
            if proc.poll() is None:
                proc.terminate()
            stdout, stderr = proc.communicate(timeout=5)
        self.assertIn(f'http://127.0.0.1:{port}', stdout)

    def test_invalid_options_do_not_run_exercises(self):
        for args in (['--port', 'bad'], ['--port', '0'], ['--port'], ['--output'], ['--lab-only', '--serve-only'], ['--unknown']):
            with self.subTest(args=args):
                result = subprocess.run([BASH, str(ROOT / 'setup.sh'), '--output', str(self.reports), *args],
                                        env=self.env, text=True, capture_output=True, timeout=5)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.reports / 'assessment.json').exists())
