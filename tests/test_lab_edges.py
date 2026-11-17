from pathlib import Path
import tempfile
import unittest
from labs.support import Denied
from labs.ssrf import vulnerable as ssrf_v, secure as ssrf_s
from labs.path_traversal import secure as paths
from labs.path_traversal.data import fixtures
from labs.missing_login_rate_limiting.secure import LoginService
from labs.weak_password_storage import secure as passwords
from labs.fail_open_error_handling.secure import authorize
from labs.missing_security_audit_logs.secure import change_role

class EdgeTests(unittest.TestCase):
    def test_ssrf_safety_boundary_rejects_non_fixture_targets(self):
        public, internal = 'http://127.0.0.1:12345', 'http://127.0.0.1:12346'
        for module in (ssrf_v, ssrf_s):
            for url in ('http://example.invalid/', 'http://169.254.169.254/', public+'@example.invalid/', public+'#fragment'):
                with self.subTest(module=module.__name__, url=url), self.assertRaises(Denied):
                    module.fetch_preview(url, public, internal)
    def test_resolved_symlink_cannot_escape_public_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            public = fixtures(Path(directory))
            (public/'shortcut').symlink_to(public.parent/'private/payroll.txt')
            with self.assertRaises(Denied): paths.read_file(public, 'shortcut')
    def test_login_limiter_expires_and_preserves_correct_login(self):
        now = [0.0]
        service = LoginService(clock=lambda: now[0])
        for _ in range(3): self.assertEqual(service.login('alice', 'wrong')[0], 401)
        self.assertEqual(service.login('ALICE', 'dummy-correct-horse')[0], 429)
        now[0] = 31.0
        self.assertEqual(service.login('alice', 'dummy-correct-horse'), (200, True))
    def test_password_record_cannot_select_excessive_work_factor(self):
        for malformed in ('md5$bad', 'scrypt$999999999$8$1$00$00', 'scrypt$16384$8$1$zz$zz'):
            self.assertFalse(passwords.verify('dummy-password', malformed))
    def test_non_boolean_policy_results_do_not_grant_access(self):
        for value in (None, 'allow', 1, [], {}):
            self.assertFalse(authorize('alice', 'admin', lambda a, r: value))
    def test_failed_critical_audit_write_prevents_state_change(self):
        with tempfile.TemporaryDirectory() as directory:
            users = {'admin': {'role':'admin'}, 'alice': {'role':'user'}}
            with self.assertRaises(OSError):
                change_role('admin', 'alice', 'admin', users, Path(directory)/'missing'/'audit.jsonl')
            self.assertEqual(users['alice']['role'], 'user')
