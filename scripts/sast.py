"""Gate fixed code; report expected findings from intentionally vulnerable code separately."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def secure_paths():
    return [Path('app'), Path('lab'), Path('scripts'), Path('pipelines/hardened'), Path('labs/support.py'),
            Path('labs/web.py'), Path('labs/catalog.py'), *sorted(Path('labs').glob('*/secure.py')),
            *sorted(Path('labs').glob('*/data.py'))]

def main():
    os.chdir(ROOT)
    Path('reports').mkdir(exist_ok=True)
    Path('.work').mkdir(exist_ok=True)
    env = dict(os.environ, SEMGREP_LOG_FILE=str(ROOT/'.work/semgrep.log'),
               SEMGREP_SETTINGS_FILE=str(ROOT/'.work/semgrep-settings.yml'))
    common = ['semgrep', 'scan', '--config', 'policies/semgrep.yml', '--metrics', 'off', '--disable-version-check']
    protected = subprocess.run(common + ['--error', '--json-output', 'reports/semgrep-secure.json',
                                         '--sarif-output', 'reports/semgrep-secure.sarif', *map(str, secure_paths())], env=env)
    intentional = sorted(Path('labs').glob('*/vulnerable.py')) + list(Path('pipelines/vulnerable').glob('*.py'))
    observed = subprocess.run(common + ['--json', '--output', 'reports/semgrep-intentional.json', *map(str, intentional)], env=env)
    if observed.returncode != 0:
        return observed.returncode
    report = json.loads(Path('reports/semgrep-intentional.json').read_text())
    rules = {result['check_id'].rsplit('.', 1)[-1] for result in report.get('results', [])}
    if not {'unsafe-python-deserialization', 'weak-password-md5', 'pipeline-shell-true', 'concatenated-sql-query'} <= rules:
        print('Expected teaching findings were not detected; investigate scanner/rule drift.', file=sys.stderr)
        return 1
    print('Intentional findings are recorded separately; fixed-code findings still fail the gate.')
    return protected.returncode

if __name__ == '__main__':
    sys.exit(main())
