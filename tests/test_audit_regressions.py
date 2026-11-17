"""Independent audit checks: execute controls instead of trusting report flags."""
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
import threading
from labs.support import Denied, json_service
from labs.business_logic_bypass import secure as coupons
from labs.untrusted_build_dependency import secure as builds
from labs.dependency_confusion import secure as resolver
from labs.weak_password_storage import secure as passwords
from labs.mass_assignment import secure as profiles
from labs.unsigned_artifact_acceptance import secure as artifacts
from lab.controls import verify_artifact

ROOT = Path(__file__).resolve().parents[1]

class OriginalScenarioAuditTests(unittest.TestCase):
    def test_01_execute_both_metadata_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            payload = 'release; printf AUDIT > marker; #'
            env = {'PATH': os.defpath, 'CHANGE_TITLE': payload}
            def execute(mode):
                return subprocess.run([sys.executable, str(ROOT/f'pipelines/{mode}/metadata.py')],
                                      cwd=work, env=env, capture_output=True, text=True, timeout=5)
            bad = execute('vulnerable')
            self.assertEqual(bad.returncode, 0, bad.stderr)
            self.assertEqual((work/'marker').read_text(), 'AUDIT')
            (work/'marker').unlink()
            good = execute('hardened')
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(good.stdout.strip(), payload)
            self.assertFalse((work/'marker').exists())
    def test_02_execute_both_log_scripts(self):
        token = 'AUDIT_SYNTHETIC_ONLY'
        env = {'PATH': os.defpath, 'LAB_TOKEN': token}
        for mode in ('vulnerable', 'hardened'):
            with self.subTest(mode=mode):
                result = subprocess.run([sys.executable, str(ROOT/f'pipelines/{mode}/secrets.py')],
                                        env=env, capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(token in result.stdout+result.stderr, mode=='vulnerable')
    def test_03_unchecked_read_accepts_but_trusted_digest_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory)/'release.json'
            artifact.write_text('{"app":"trusted"}')
            expected = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertEqual(verify_artifact(artifact, expected), expected)
            artifact.write_text('{"app":"tampered"}')
            self.assertEqual(json.loads(artifact.read_text())['app'], 'tampered')
            with self.assertRaises(ValueError): verify_artifact(artifact, expected)
    def test_04_execute_the_actual_hardened_gate_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            clean = Path(directory)/'clean.json'
            clean.write_text(json.dumps({'SchemaVersion':2, 'Results':[{'Target':'demo', 'Vulnerabilities':None}]}))
            missing = Path(directory)/'missing.json'
            bad = ROOT/'fixtures/trivy-vulnerable.json'
            for path, expected in ((clean,0),(bad,1),(missing,2)):
                with self.subTest(path=path.name):
                    result = subprocess.run([sys.executable,'-m','pipelines.hardened.gate',str(path)],
                                            cwd=ROOT, capture_output=True, text=True, timeout=5)
                    self.assertEqual(result.returncode, expected, result.stderr)

class FixedImplementationAuditTests(unittest.TestCase):
    def test_08_mixed_profile_update_is_atomic(self):
        profile = {'role':'user', 'display_name':'Alice'}
        with self.assertRaises(Denied):
            profiles.update_profile(profile, {'display_name':'Changed','role':'admin'})
        self.assertEqual(profile, {'role':'user','display_name':'Alice'})
    def test_12_private_dependency_identity_and_digest_are_enforced(self):
        trusted = {'name':'demo','namespace':'private','version':'1.0.0','content':'trusted-data'}
        expected = hashlib.sha256(trusted['content'].encode()).hexdigest()
        for field, changed in (('content','modified'),('namespace','public'),('version','99.0.0'),('name','other')):
            package = dict(trusted, **{field: changed})
            with self.subTest(field=field), json_service({'/private/demo':package}) as (origin,_):
                with self.assertRaises(Denied): resolver.resolve(origin,'demo','1.0.0',expected)
    def test_13_reject_malformed_trusted_dependency_metadata(self):
        # A correct digest alone must not turn invalid metadata into valid input.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'dependency.json'
            path.write_text(json.dumps({'name':None,'version':{},'kind':'prebuilt-metadata'}))
            with self.assertRaises(Denied):
                builds.build(path, hashlib.sha256(path.read_bytes()).hexdigest())
    def test_14_record_matches_the_claimed_kdf(self):
        record = passwords.store('audit-dummy-password')
        scheme,n,r,p,salt,digest = record.split('$')
        self.assertEqual((scheme,n,r,p), ('scrypt','16384','8','5'))
        self.assertEqual(len(bytes.fromhex(salt)), 16)
        expected = hashlib.scrypt(b'audit-dummy-password', salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), maxmem=64*1024*1024)
        self.assertEqual(expected.hex(), digest)
        self.assertTrue(passwords.verify('audit-dummy-password',record))
        self.assertFalse(passwords.verify('wrong',record))
    def test_19_reject_missing_principal_before_a_nullable_ledger(self):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.execute('CREATE TABLE redemptions (user TEXT, coupon TEXT, PRIMARY KEY(user,coupon))')
        with self.assertRaises(Denied): coupons.checkout(db,None,'ONCE10')
        self.assertEqual(db.execute('SELECT count(*) FROM redemptions').fetchone()[0], 0)
    def test_19_concurrent_redemptions_are_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory)/'checkout.db')
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE redemptions (user TEXT, coupon TEXT, PRIMARY KEY(user,coupon))')
            db.close()
            barrier = threading.Barrier(2)
            def redeem(_):
                db = sqlite3.connect(path, timeout=5)
                try:
                    barrier.wait(timeout=5)
                    try: return coupons.checkout(db,'alice','ONCE10')
                    except Denied: return 'denied'
                finally: db.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(redeem, range(2)))
            self.assertCountEqual(results, [1500,'denied'])
    def test_23_wrong_key_and_modified_body_are_rejected(self):
        key = secrets.token_bytes(32)
        signed = artifacts.authenticate(b'{"app":"trusted"}',key)
        self.assertEqual(artifacts.accept(signed,key),{'app':'trusted'})
        with self.assertRaises(Denied): artifacts.accept(signed,secrets.token_bytes(32))
        modified = dict(signed,payload=base64.b64encode(b'{"app":"modified"}').decode())
        with self.assertRaises(Denied): artifacts.accept(modified,key)
