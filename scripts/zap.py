"""Run passive baseline DAST only against a newly allocated loopback secure application."""
import json
from pathlib import Path
import subprocess
import sys
import uuid
from labs.web import serve_lab

ZAP_IMAGE = 'ghcr.io/zaproxy/zaproxy:stable@sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af'

def evaluate_zap(report):
    sites = report.get('site') if isinstance(report, dict) else None
    if not isinstance(sites, list) or not sites:
        raise ValueError('Missing ZAP site results')
    alerts = []
    for site in sites:
        if not isinstance(site, dict) or not isinstance(site.get('alerts'), list):
            raise ValueError('Malformed ZAP alert results')
        for alert in site['alerts']:
            if not isinstance(alert, dict) or str(alert.get('riskcode')) not in ('0','1','2','3'):
                raise ValueError('Invalid ZAP risk code')
            alerts.append(alert)
    return alerts, [alert for alert in alerts if int(alert['riskcode']) >= 2]


def main():
    destination = Path(__file__).resolve().parents[1]/'reports'
    destination.mkdir(exist_ok=True)
    for output in ('zap.json', 'zap.html', 'zap.md'):
        (destination/output).unlink(missing_ok=True)
    name = 'pipelineproof-zap-' + uuid.uuid4().hex[:12]
    try:
        with serve_lab() as (_, origin):
            subprocess.run(['docker', 'create', '--name', name, '--network', 'host', '--workdir', '/zap/wrk', ZAP_IMAGE,
                            'zap-baseline.py', '-t', origin, '-J', 'zap.json', '-r', 'zap.html', '-w', 'zap.md'], check=True)
            process = subprocess.run(['docker', 'start', '--attach', name])
            for file in ('zap.json', 'zap.html', 'zap.md'):
                subprocess.run(['docker', 'cp', f'{name}:/zap/wrk/{file}', str(destination/file)], check=True)
        if process.returncode not in (0, 1, 2):
            return process.returncode
        report = json.loads((destination/'zap.json').read_text())
        alerts, blocking = evaluate_zap(report)
        print(f'ZAP quality policy: {len(blocking)} medium/high alerts block; {len(alerts)-len(blocking)} low/info alerts retained for review.')
        return 1 if blocking or process.returncode == 1 else 0
    finally:
        subprocess.run(['docker', 'rm', '--force', name], check=False)

if __name__ == '__main__':
    sys.exit(main())
