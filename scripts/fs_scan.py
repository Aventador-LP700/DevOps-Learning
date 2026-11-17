"""Trivy vulnerability/misconfiguration/secret gate on an explicitly selected fixed-code snapshot."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from scripts.sast import ROOT, secure_paths

def main():
    os.chdir(ROOT)
    target = ROOT / '.work/release-scan'
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    files = secure_paths() + [Path('requirements-dev.txt'), Path('Dockerfile'),
                             Path('infra/kubernetes/base.yaml'), Path('infra/kubernetes/hardened-rbac.yaml')]
    for path in files:
        destination = target/path
        if path.is_dir():
            shutil.copytree(path, destination, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    shutil.copyfile('requirements-dev.txt', target/'requirements.txt')
    Path('reports').mkdir(exist_ok=True)
    for output in ('trivy-fs.json', 'trivy-fs.sarif'):
        (Path('reports')/output).unlink(missing_ok=True)
    cache = ROOT/'.work/cache/trivy'
    cache.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TRIVY_CACHE_DIR=os.environ.get('TRIVY_CACHE_DIR', str(cache)))
    result = subprocess.run(['trivy', 'fs', '--scanners', 'vuln,misconfig,secret', '--severity', 'HIGH,CRITICAL',
                             '--exit-code', '1', '--format', 'json', '--output', 'reports/trivy-fs.json', str(target)], env=env)
    if Path('reports/trivy-fs.json').is_file():
        converted = subprocess.run(['trivy', 'convert', '--format', 'sarif', '--output', 'reports/trivy-fs.sarif', 'reports/trivy-fs.json'], env=env)
        if converted.returncode: return converted.returncode
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
