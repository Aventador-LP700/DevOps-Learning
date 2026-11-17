"""All 25 implementations, their proof paths and mapping provenance. No test outcomes."""
from labs.catalog import CATALOG


def scenario_inventory():
    definitions = [
        (1,'pipeline-injection','CWE-78','A05',[],
         ['pipelines/vulnerable/metadata.py'],['pipelines/hardened/metadata.py'],'injection'),
        (2,'secret-exposure','CWE-532','A09',['A02'],
         ['pipelines/vulnerable/secrets.py'],['pipelines/hardened/secrets.py'],'secrets'),
        (3,'artifact-tampering','CWE-353','A08',[],
         ['lab/scenarios.py'],['lab/controls.py'],'artifact'),
        (4,'security-gate-bypass','CWE-693','A06',['A02'],
         ['pipelines/vulnerable/gate.py'],['pipelines/hardened/gate.py','lab/controls.py'],'gate'),
        (5,'excessive-permissions','CWE-250','A01',[],
         ['infra/kubernetes/vulnerable-rbac.yaml'],['infra/kubernetes/hardened-rbac.yaml'],'scripts/k8s.sh'),
    ]
    entries = []
    for number,name,cwe,primary,related,vulnerable,fixed,proof in definitions:
        entries.append({'number':number,'id':name,'cwe':cwe,'owasp_primary':primary,
                        'owasp_related':related,'mapping_basis':'contextual' if number==5 else 'official-cwe-list',
                        'mapping_note': 'Excessive execution privileges violate least privilege in A01; CWE-250 itself is not in OWASP’s enumerated list.' if number==5 else 'Official CWE assignment; related categories are contextual only.',
                        'vulnerable_files':vulnerable,'fixed_files':fixed,
                        'proof_files':['scripts/k8s.sh'] if number==5 else ['lab/scenarios.py'],
                        'proof_entrypoint':proof,'test_files':['.github/workflows/kubernetes.yml'] if number==5 else ['tests/test_audit_regressions.py'],
                        'runtime':'kubernetes-api' if number==5 else 'local-python'})
    for entry in CATALOG:
        base='labs/'+entry['module']+'/'
        categories=entry['owasp_2025'].split('/')
        entries.append({'number':entry['number'],'id':entry['id'],'cwe':entry['cwe'],
                        'owasp_primary':categories[0],'owasp_related':categories[1:],
                        'mapping_basis':'official-cwe-list',
                        'mapping_note':'Official CWE assignment; related categories are contextual only.',
                        'vulnerable_files':[base+'vulnerable.py'],'fixed_files':[base+'secure.py'],
                        'proof_files':[base+'attack.py'],'proof_entrypoint':'demonstrate',
                        'test_files':[base+'test_lab.py'],'runtime':'local-python'})
    return entries
