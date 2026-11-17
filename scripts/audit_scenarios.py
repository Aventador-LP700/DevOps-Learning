"""Execute every local proof; include scenario 05 only with fresh real API evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from lab.inventory import scenario_inventory
from lab.scenarios import run_scenario

ROOT=Path(__file__).resolve().parents[1]


def verify_kubernetes(report, now):
    required=('vulnerable_secret_read','hardened_secret_read_forbidden','hardened_deployment_patch_allowed','passed')
    if (not isinstance(report, dict) or report.get('scenario')!='excessive-deployment-permissions'
            or any(report.get(key) is not True for key in required)):
        raise ValueError('Kubernetes proof is missing successful API assertions')
    generated=datetime.fromisoformat(report['generated_at'])
    if generated.tzinfo is None or not -60 <= (now-generated).total_seconds() <= 900:
        raise ValueError('Kubernetes evidence must be timezone-aware and at most 15 minutes old')
    return report


def audit(*, kubernetes_report=None):
    now=datetime.now(timezone.utc)
    results=[]
    for entry in scenario_inventory():
        row=dict(entry)
        files=set(entry['vulnerable_files']+entry['fixed_files']+entry['proof_files']+entry['test_files'])
        row['file_sha256']=[{'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in sorted(files) if (ROOT/name).is_file()]
        missing=[name for name in files if not (ROOT/name).is_file() or (ROOT/name).stat().st_size==0]
        if missing:
            row.update(status='FAIL',evidence={'missing_or_empty_files':missing})
        elif entry['runtime']=='kubernetes-api':
            if kubernetes_report is None:
                row.update(status='NOT_RUN',evidence={'reason':'Requires a fresh real Kubernetes API test; run make k8s-up k8s-test'})
            else:
                try:
                    actual=verify_kubernetes(json.loads(kubernetes_report.read_text()),now)
                    row.update(status='PASS',evidence={'report':actual,'source':str(kubernetes_report)})
                except (ValueError,OSError,TypeError,KeyError) as exc:
                    row.update(status='FAIL',evidence={'error':str(exc)})
        else:
            try:
                actual=run_scenario(entry['id'])
                row.update(status='PASS' if actual['passed'] else 'FAIL',evidence=actual)
            except Exception as exc:
                row.update(status='FAIL',evidence={'error':f'{type(exc).__name__}: {exc}'})
        results.append(row)
    return {'schema_version':1,'generated_at':now.isoformat(),
            'tested_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
            'passed':sum(r['status']=='PASS' for r in results),
            'failed':sum(r['status']=='FAIL' for r in results),
            'not_run':sum(r['status']=='NOT_RUN' for r in results),'results':results}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',action='store_true',help='Explicitly run fixed teaching proofs on this host without a sandbox')
    parser.add_argument('--kubernetes-report',type=Path)
    parser.add_argument('--output',type=Path,default=Path('reports/scenario-audit'))
    args=parser.parse_args()
    if not args.native and not Path('/lab/.pipelineproof-container').is_file():
        parser.error('Explicit --native opt-in is required outside the isolated lab')
    report=audit(kubernetes_report=args.kubernetes_report)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    for row in report['results']:
        print(f"{row['number']:02d} {row['status']} {row['id']}")
    print(f"PASS={report['passed']} FAIL={report['failed']} NOT_RUN={report['not_run']}")
    return 1 if report['failed'] else 2 if report['not_run'] else 0

if __name__=='__main__':
    sys.exit(main())
