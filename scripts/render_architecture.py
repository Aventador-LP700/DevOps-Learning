"""Generate editable vector architecture diagrams; optionally export PDF and PNG.

SVG creation needs only Python. --export additionally needs Inkscape on PATH.
No external icon/font/image services are used, and no lab services are started.
"""
import argparse
from html import escape
import math
import os
from pathlib import Path
import shutil
import subprocess
from lab.inventory import scenario_inventory

ROOT = Path(__file__).resolve().parents[1]
COL = dict(bg='#0a1322', panel='#102036', inset='#0d1a2d', line='#29435e',
           white='#eef5ff', muted='#a2b6cf', cyan='#55d7f0', teal='#5ee4be',
           red='#ff7888', gold='#f2c476', purple='#bdabff')
# Human-readable labels are kept short; canonical IDs/paths come from the inventory.
CASES = {
 1: ('Pipeline metadata injection', 'Arguments; no shell'),
 2: ('Secrets exposed in build logs', 'Omit credential values'),
 3: ('Artifact bytes modified in storage', 'Trusted SHA256 digest'),
 4: ('Advisory scan bypasses release gate', 'Enforced severity policy'),
 5: ('Excessive CI deployment permissions', 'Scoped Kubernetes RBAC'),
 6: ('IDOR / broken object authorization', 'Verify object ownership'),
 7: ('Administrative function abuse', 'Server-side role check'),
 8: ('Mass assignment of protected fields', 'Writable-field allowlist'),
 9: ('SSRF to internal mock metadata', 'Exact public destination'),
10: ('Credentialed CORS misconfiguration', 'Exact trusted origins'),
11: ('Debug / exception information leak', 'Generic error + request ID'),
12: ('Dependency confusion', 'Private source + pinned digest'),
13: ('Untrusted dependency build hook', 'No hooks; validate metadata'),
14: ('Weak password storage', 'Salted scrypt; standalone KDF'),
15: ('SQL injection', 'Bound query parameters'),
16: ('Stored cross-site scripting', 'HTML encoding + browser CSP'),
17: ('OS command injection / local RCE', 'Argument array + validation'),
18: ('Path traversal to private fixtures', 'Resolved public-root check'),
19: ('Coupon replay / business logic bypass', 'Principal + atomic ledger'),
20: ('Missing login rate limiting', 'Bounded account attempts'),
21: ('Session fixation', 'Rotate and invalidate session'),
22: ('Unsafe Python deserialization', 'Schema-validated JSON'),
23: ('Unauthenticated artifact accepted', 'Protected-key HMAC check'),
24: ('Missing security audit events', 'Structured allow / deny log'),
25: ('Authorization fails open on error', 'Explicit allow; deny on error'),
}
GROUPS = [
 ('CI / BUILD PIPELINE','Pipeline inputs and dependency sources',[1,2,4,12,13],'server',
  'pipelines/ + labs/dependency_confusion/ + labs/untrusted_build_dependency/',
  'Synthetic build steps and a loopback JSON package index.'),
 ('API / BUSINESS POLICY','Objects, roles and application invariants',[6,7,8,19,25],'api',
  'labs/idor_bola/ · mass_assignment/ · business_logic_bypass/ · ...',
  'Module-local state; optional labs/web.py on 127.0.0.1:8081 (fixed by default).'),
 ('DATA / CODE EXECUTION','Data crossing interpreter boundaries',[15,16,17,18,22],'database',
  'labs/sql_injection/ · stored_xss/ · path_traversal/ · ...',
  'In-memory SQLite + temporary files; high-risk proofs are CLI-only.'),
 ('IDENTITY / BROWSER TRUST','Credentials, origins and session state',[10,14,20,21],'browser',
  'labs/cors_misconfiguration/ · weak_password_storage/ · ...',
  'HTTP adapter uses synthetic login; the password-storage lab is separate.'),
 ('ARTIFACTS / OBSERVABILITY','Integrity, diagnostics and audit records',[3,11,23,24],'artifact',
  'lab/controls.py + labs/unsigned_artifact_acceptance/ + ...',
  'HMAC is a shared-key MAC; local JSONL is not a deployed SIEM.'),
]

class SVG:
    def __init__(self,w,h,title,description):
        self.w,self.h=w,h
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title description">',
                    f'<title id="title">{escape(title)}</title>',f'<desc id="description">{escape(description)}</desc>',
                    '<defs>'+''.join(f'<marker id="arrow-{k}" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0 0 L8 4 L0 8 Z" fill="{COL[k]}"/></marker>' for k in ('red','teal','cyan','gold'))+'</defs>',
                    f'<rect width="{w}" height="{h}" rx="24" fill="{COL["bg"]}"/>']
        for x in range(35,w,70):
            self.parts.append(f'<path d="M{x} 0 V{h}" stroke="#16243a" stroke-width="0.6" opacity="0.35"/>')
        for y in range(35,h,70):
            self.parts.append(f'<path d="M0 {y} H{w}" stroke="#16243a" stroke-width="0.6" opacity="0.35"/>')
    def raw(self,markup): self.parts.append(markup)
    def rect(self,x,y,w,h,fill='panel',stroke='line',radius=16,dash=None):
        dash=f' stroke-dasharray="{dash}"' if dash else ''
        self.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{COL.get(fill,fill)}" stroke="{COL.get(stroke,stroke)}" stroke-width="2"{dash}/>')
    def text(self,x,y,value,size=22,color='white',weight=400,anchor='start',mono=False):
        family='DejaVu Sans Mono, monospace' if mono else 'DejaVu Sans, Arial, sans-serif'
        self.raw(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{COL.get(color,color)}" text-anchor="{anchor}">{escape(str(value))}</text>')
    def path(self,d,color='cyan',width=3,arrow=False,dash=None):
        marker=f' marker-end="url(#arrow-{color})"' if arrow else ''
        pattern=f' stroke-dasharray="{dash}"' if dash else ''
        self.raw(f'<path d="{d}" fill="none" stroke="{COL[color]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{marker}{pattern}/>')
    def dot(self,x,y,color='cyan',r=5):
        self.raw(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{COL[color]}"/>')
    def icon(self,kind,x,y,scale=1):
        self.raw(f'<g transform="translate({x} {y}) scale({scale})" aria-hidden="true">')
        # A small isometric platform plus an upright component; all paths stay vector.
        self.raw('<path d="M-64 25 L5 -2 L90 25 L20 55 Z" fill="#12374e" stroke="#55d7f0" stroke-width="1.7"/>')
        self.raw('<path d="M-64 25 L20 55 L20 63 L-64 33 Z" fill="#10293e"/><path d="M20 55 L90 25 L90 33 L20 63 Z" fill="#0c2032"/>')
        if kind=='database':
            self.raw('<path d="M-21 -55 C-21 -75 53 -75 53 -55 V12 C53 32 -21 32 -21 12 Z" fill="#19486a" stroke="#55d7f0" stroke-width="2"/>')
            for cy in (-55,-27,1):
                self.raw(f'<ellipse cx="16" cy="{cy}" rx="37" ry="12" fill="#1c5d80" stroke="#73e5ef" stroke-width="2"/>')
            self.raw('<path d="M-21 -54 V12 M53 -54 V12" stroke="#55d7f0" stroke-width="2"/>')
        elif kind in ('browser','api','terminal'):
            self.raw('<path d="M-27 -77 L54 -49 V28 L-27 0 Z" fill="#194569" stroke="#68e7f5" stroke-width="2"/><path d="M54 -49 L67 -57 V20 L54 28 Z" fill="#102b46"/>')
            self.raw('<path d="M-27 -77 L-14 -85 L67 -57 L54 -49 Z" fill="#286f8d"/><path d="M-21 -58 L45 -35" stroke="#9deaff" stroke-width="2"/>')
            if kind=='api':
                self.raw('<path d="M-5 -31 L-16 -23 L-5 -8 M25 -20 L38 -6 L25 0 M18 -35 L6 2" stroke="#83eede" fill="none" stroke-width="4"/>')
            else:
                self.raw('<path d="M-14 -39 L0 -26 L-14 -22 M8 -16 L32 -8" stroke="#83eede" fill="none" stroke-width="4"/>')
        elif kind=='kube':
            points=' '.join(f'{16+35*math.cos(-math.pi/2+i*2*math.pi/7):.1f},{-28+35*math.sin(-math.pi/2+i*2*math.pi/7):.1f}' for i in range(7))
            self.raw(f'<polygon points="{points}" fill="#174a70" stroke="#61def1" stroke-width="2.5"/>')
            self.raw('<circle cx="16" cy="-28" r="15" fill="none" stroke="#d8f9ff" stroke-width="3"/>')
            for i in range(7):
                angle=-math.pi/2+i*2*math.pi/7
                self.raw(f'<path d="M{16+15*math.cos(angle):.1f} {-28+15*math.sin(angle):.1f} L{16+29*math.cos(angle):.1f} {-28+29*math.sin(angle):.1f}" stroke="#d8f9ff" stroke-width="3"/>')
        elif kind=='artifact':
            self.raw('<path d="M-23 -44 L19 -62 L60 -43 L18 -25 Z" fill="#2b6d7f" stroke="#74ead7" stroke-width="2"/><path d="M-23 -44 L18 -25 V21 L-23 2 Z" fill="#19485d" stroke="#74ead7" stroke-width="2"/><path d="M18 -25 L60 -43 V2 L18 21 Z" fill="#133248" stroke="#74ead7" stroke-width="2"/>')
            self.raw('<path d="M-5 -20 L-5 0 M28 -21 L49 -30" stroke="#9bf4dd" stroke-width="4"/>')
        else:
            self.raw('<path d="M-23 -74 L31 -55 V30 L-23 11 Z" fill="#1b4b6a" stroke="#74e8ef" stroke-width="2"/><path d="M31 -55 L49 -65 V20 L31 30 Z" fill="#123047"/><path d="M-23 -74 L-5 -84 L49 -65 L31 -55 Z" fill="#32718c"/>')
            for yy in (-47,-22,3):
                self.raw(f'<path d="M-15 {yy} L23 {yy+13}" stroke="#8ce4ec" stroke-width="3"/>')
                self.raw(f'<circle cx="-12" cy="{yy-7}" r="2.6" fill="#5ee4be"/>')
        self.raw('</g>')
    def save(self,path):
        path.write_text('\n'.join(self.parts+['</svg>'])+'\n')

def header(s,large=True):
    s.icon('artifact',95,99,.72)
    s.text(210,98,'PipelineProof',60 if large else 58,weight=750)
    s.text(210,145,'Attack paths, runtime boundaries and lab structure',28,'muted')
    s.text(210,182,'ATTACK  /  OBSERVE  /  HARDEN  /  RETEST',18,'teal',weight=600)

def mini_case(s,x,y,w,n,entry):
    title,fix=CASES[n]
    s.raw(f'<g id="scenario-{n:02d}" data-scenario-id="{n:02d}">')
    s.raw(f'<title>{n:02d}: {escape(entry["id"])} — {escape(entry["cwe"])}</title>')
    s.rect(x,y,43,28,fill='#3a2434',stroke='#674050',radius=7)
    s.text(x+21.5,y+20,f'{n:02d}',18,'red',650,'middle')
    s.text(x+59,y+20,title,21.5,weight=550)
    s.text(x+w,y+19,entry['cwe'],15,'purple',anchor='end')
    path=entry['vulnerable_files'][0]
    if n>=6: path=path.removesuffix('vulnerable.py')
    s.text(x+59,y+43,path,15.5,'muted',mono=True)
    s.text(x+w,y+43,'Fix: '+fix,16,'teal',anchor='end')
    s.raw('</g>')

def full_map(out,inventory):
    s=SVG(3000,2800,'PipelineProof — full 25-scenario attack and architecture map',
          'All 25 documented attack scenarios, exact code locations, fixed controls, local fixture boundaries, separate real Kubernetes lab, security gates and evidence storage.')
    header(s)
    s.rect(2490,54,420,105,fill='inset',stroke='cyan')
    s.text(2700,99,'25 SCENARIOS',32,'cyan',700,'middle')
    s.text(2700,134,'24 local  +  1 real kind API',21,'muted',anchor='middle')
    # The top row represents commands and trusted orchestration, not remote attackers.
    for x,w in ((110,880),(1070,880),(2030,880)): s.rect(x,235,w,225)
    s.text(140,279,'LEARNER WORKSTATION',20,'cyan',650)
    s.icon('terminal',890,355,.75)
    s.text(140,320,'Native or restricted Docker mode',29,weight=600)
    s.text(140,360,'bash ./setup.sh --lab-only',22,'teal',mono=True)
    s.text(140,395,'make lab  →  Docker image pipelineproof:local',19,'muted')
    s.text(140,429,'Optional demo API: app/ on 127.0.0.1:8080',18,'muted')
    s.text(1100,279,'TRUSTED EXERCISE ROUTER',20,'cyan',650)
    s.icon('server',1850,355,.75)
    s.text(1100,320,'Replay controlled proof inputs',29,weight=600)
    s.text(1100,360,'lab/scenarios.py  +  labs/catalog.json',21,'teal',mono=True)
    s.text(1100,395,'Vulnerable effect  →  fixed retest  →  legitimate result',18.5,'muted')
    s.text(1100,429,'Temporary working directories; synthetic data only',18,'muted')
    s.text(2060,279,'GITHUB REPOSITORY / CI',20,'cyan',650)
    s.icon('api',2800,355,.75)
    s.text(2060,320,'Read-only validation workflows',29,weight=600)
    s.text(2060,360,'.github/workflows/',22,'teal',mono=True)
    s.text(2060,395,'Native · Docker · browser · SAST',20,'muted')
    s.text(2060,429,'Manual kind and live-security-tool jobs are separate',18,'muted')
    s.path('M990 348 H1060','cyan',3,True)
    s.path('M2030 348 H1960','cyan',3,True)
    s.rect(50,535,2900,1280,fill='inset',stroke='line',radius=22,dash='12 8')
    s.text(110,579,'24 LOCAL EXERCISES',25,'cyan',700)
    s.text(110,613,'The groups below locate code and fixtures; they are not 24 deployed network services.',19,'muted')
    s.text(2895,579,'Docker: non-root · read-only root · no Docker socket',19,'muted',anchor='end')
    s.text(2895,613,'Loopback mocks work inside the network-disabled container.',18,'muted',anchor='end')
    # Route only through margins and gutters, keeping labels clear.
    s.path('M1510 460 V645 H80 V1200 H2470','red',4)
    s.path('M80 645 H2470','red',4)
    for yy in (690,1240):
        for xx in (550,1510,2470):
            start=645 if yy==690 else 1200
            s.path(f'M{xx} {start} V{yy-9}','red',3,True)
    s.path('M550 1770 H2470','teal',4)
    for xx,gutter in ((110,1020),(1070,1980),(2030,2935)):
        s.path(f'M{xx+860} 1160 V1175 H{gutter} V1770 H{xx+440}','teal',2.5)
    for xx in (550,1510,2470): s.path(f'M{xx} 1710 V1770','teal',3)
    s.path('M1510 1770 V1875','teal',4,True)
    s.path('M2910 405 H2975 V2070 H2920','cyan',2.5,True,dash='10 8')
    for i,(tag,title,ids,icon,source,note) in enumerate(GROUPS):
        x=110+(i%3)*960; y=690+(i//3)*550
        s.rect(x,y,880,470)
        s.text(x+26,y+34,tag,18,'cyan',700)
        s.text(x+26,y+73,title,29,weight=600)
        s.text(x+26,y+104,source,15.2,'muted')
        s.icon(icon,x+770,y+81,.65)
        s.path(f'M{x+26} {y+120} H{x+854}','line')
        for j,n in enumerate(ids): mini_case(s,x+26,y+139+j*61,826,n,inventory[n])
        if i==3:
            s.text(x+26,y+405,'HTTP vulnerable mode requires both explicit flags:',16,'muted')
            s.text(x+26,y+428,'--vulnerable --enable-vulnerable-labs',16,'teal',mono=True)
        s.text(x+26,y+449,note,15.5,'muted')
        s.dot(x+440,y,'red')
        s.dot(x+860,y+470,'teal') if i<3 else s.dot(x+440,y+470,'teal')
    # Dedicated network fixture area. Both mocks are temporary and on loopback.
    x,y=2030,1240
    s.rect(x,y,880,470)
    s.text(x+26,y+34,'LOOPBACK MOCK SERVICES',18,'cyan',700)
    s.text(x+26,y+73,'Temporary HTTP fixtures',29,weight=600)
    s.text(x+26,y+104,'labs/ssrf/ + labs/support.py:json_service',16,'muted')
    s.path(f'M{x+26} {y+120} H{x+854}','line')
    mini_case(s,x+26,y+139,826,9,inventory[9])
    s.icon('server',x+205,y+290,.72)
    s.icon('server',x+620,y+290,.72)
    s.text(x+220,y+352,'PUBLIC PREVIEW MOCK',17,'cyan',650,'middle')
    s.text(x+220,y+379,'/public/info',18,'muted',anchor='middle',mono=True)
    s.text(x+635,y+352,'INTERNAL METADATA MOCK',17,'red',650,'middle')
    s.text(x+635,y+379,'/internal/metadata',18,'muted',anchor='middle',mono=True)
    s.rect(x+335,y+205,190,34,fill='inset',stroke='line',radius=8)
    s.text(x+430,y+228,'fetch_preview(url)',15,'white',anchor='middle',mono=True)
    s.path(f'M{x+335} {y+222} V{y+275} H{x+285}','teal',2.5,True)
    s.path(f'M{x+525} {y+222} V{y+275} H{x+560}','red',2.5,True)
    s.text(x+430,y+325,'internal read only in V',14,'red',anchor='middle')
    s.text(x+26,y+419,'Both: 127.0.0.1, allocated ports; no external destinations or redirects.',16,'muted')
    s.text(x+26,y+449,'12 uses a separate loopback JSON package index; no public package installs.',15.5,'muted')
    s.dot(x+440,y,'red');s.dot(x+440,y+470,'teal')
    # Separate real Kubernetes path. It is never included in the 24-local count.
    x,y=110,1885
    s.rect(x,y,880,360,stroke='gold',dash='12 6')
    s.raw('<g id="scenario-05" data-scenario-id="05"><title>05: excessive-permissions — real Kubernetes API</title>')
    s.rect(x+24,y+25,48,34,fill='#3b3024',stroke='gold',radius=8)
    s.text(x+48,y+49,'05',22,'gold',700,'middle')
    s.text(x+90,y+51,'Separate kind / Kubernetes lab',29,weight=600)
    s.text(x+850,y+49,inventory[5]['cwe'],16,'purple',anchor='end')
    s.text(x+26,y+89,'kind-pipelineproof  /  namespace: pipelineproof',19,'muted',mono=True)
    s.icon('kube',x+760,y+187,.85)
    s.text(x+26,y+135,'Vulnerable: wildcard Role permits fake Secret read',21,'red')
    s.text(x+26,y+176,'Fixed: Secret read forbidden; Deployment patch allowed',21,'teal')
    s.text(x+26,y+217,'infra/kubernetes/{vulnerable,hardened}-rbac.yaml',18,'muted',mono=True)
    s.text(x+26,y+255,'make k8s-up k8s-test',22,'gold',mono=True)
    s.text(x+26,y+294,'Real API requests via CI-identity impersonation; requires kind + Docker.',16.8,'muted')
    s.text(x+26,y+331,'Not started by native setup or make lab. No cloud accounts involved.',17,'muted')
    s.raw('</g>')
    # Evidence from the local modules and actual API requests.
    s.path('M990 2070 H1060','teal',3,True)
    x,y=1070,1885
    s.rect(x,y,880,360,stroke='teal')
    s.text(x+26,y+51,'Evidence and complete audit',30,weight=600)
    s.icon('artifact',x+760,y+162,.8)
    s.text(x+26,y+96,'reports/assessment.json + assessment.md',21,'teal',mono=True)
    s.text(x+26,y+139,'reports/rbac.json  ←  real kind/API proof',20,'muted',mono=True)
    s.text(x+26,y+182,'reports/scenario-audit/audit.json',21,'teal',mono=True)
    s.text(x+26,y+226,'24 local proofs + fresh scenario 05 evidence = full audit',19,'muted')
    s.text(x+26,y+272,'Each proof: exploit observed · fixed attack blocked',20,'white')
    s.text(x+26,y+305,'Positive checks preserve the intended legitimate behavior.',19,'muted')
    s.text(x+26,y+335,'docs/evidence/ stores reviewed snapshots; results are not assumed.',17,'muted')
    x,y=2030,1885
    s.rect(x,y,880,360,stroke='cyan')
    s.text(x+26,y+51,'Security quality gates',30,weight=600)
    s.text(x+26,y+96,'Semgrep SAST  /  Gitleaks history',22,'white')
    s.text(x+26,y+139,'Trivy filesystem, dependencies and actual image',21,'white')
    s.text(x+26,y+182,'ZAP baseline → new loopback secure app',21,'white')
    s.text(x+26,y+225,'Syft SBOM → Cosign original / tamper verification',21,'white')
    s.text(x+26,y+271,'Fixed-code findings block; teaching findings are separate.',19,'teal')
    s.text(x+26,y+309,'Release policy blocks HIGH / CRITICAL image findings.',19,'gold')
    s.text(x+26,y+338,'Outputs: JSON · SARIF where supported · SBOM · HTML',17,'muted')
    s.path('M2470 2245 V2284 H1510 V2254','cyan',2.5,True)
    s.text(1990,2274,'security-report artifacts',16,'cyan',anchor='middle')
    # Actual repository placement, rather than invented deployment components.
    s.rect(110,2330,2800,315,fill='panel')
    s.text(140,2375,'WHERE THE CODE LIVES',24,'cyan',700)
    s.text(2875,2375,'DevOps-Learning / PipelineProof',21,'muted',anchor='end')
    folders=[('lab/','Runner, controls and 25-scenario inventory'),
             ('labs/<scenario>/','vulnerable.py · secure.py · attack.py · test_lab.py'),
             ('pipelines/','Original vulnerable / hardened build steps'),
             ('infra/','kind configuration, deployment and RBAC manifests'),
             ('scenarios/','25 walkthroughs with technical knowledge checks'),
             ('tests/','Unit · HTTP · edge cases · browser regressions'),
             ('.github/workflows/','Validation · real Kubernetes · live security tools'),
             ('docs/ + reports/','Guides and saved evidence / generated assessments')]
    for i,(folder,desc) in enumerate(folders):
        xx=140+(i%4)*694; yy=2433+(i//4)*112
        s.path(f'M{xx} {yy-15} v-13 h22 l8 7 h24 v34 h-54 z','cyan',1.7)
        s.text(xx+68,yy,folder,23,'white',600,mono=True)
        s.text(xx,yy+37,desc,16,'muted')
    legend=[(130,'red','Controlled proof input'),(790,'teal','Fixed control / observed result'),(1650,'cyan','Execution / CI report flow'),(2360,'gold','Separate real API boundary')]
    for xx,color,label in legend:
        s.path(f'M{xx} 2700 h46',color,3,True)
        s.text(xx+60,2707,label,19,'muted')
    s.text(1500,2757,'Synthetic data only. Native mode has no sandbox. Diagram groups locate implementations and fixtures, not extra deployed infrastructure.',18,'muted',anchor='middle')
    s.save(out/'pipelineproof-attack-map.svg')


def overview(out):
    s=SVG(2400,1350,'PipelineProof — architecture overview',
          'A compact overview of native or Docker execution, 24 local attack exercises, the separate real kind lab, evidence and security quality gates.')
    header(s,False)
    s.rect(60,220,1660,850,fill='inset',stroke='line',radius=22,dash='12 8')
    s.text(100,269,'LOCAL LEARNING BOUNDARY  /  24 EXERCISES',25,'cyan',700)
    for x in (100,650,1200):s.rect(x,320,450,205)
    s.text(125,365,'Start locally',29,weight=650)
    s.icon('terminal',450,441,.64)
    s.text(125,407,'Native Python + Bash',22,'white')
    s.text(125,443,'or restricted Docker',22,'white')
    s.text(125,489,'setup.sh  /  make lab',20,'teal',mono=True)
    s.text(675,365,'Exercise router',29,weight=650)
    s.icon('server',1000,440,.64)
    s.text(675,407,'lab/scenarios.py',22,'white',mono=True)
    s.text(675,443,'labs/catalog.json',22,'white',mono=True)
    s.text(675,489,'Temporary synthetic fixtures',19,'muted')
    s.text(1225,365,'Attack → fixed retest',28,weight=650)
    s.text(1225,411,'Vulnerable implementation',21,'red')
    s.text(1225,450,'Separate fixed counterpart',21,'teal')
    s.text(1225,489,'Legitimate behavior checked',19,'muted')
    s.path('M550 425 H638','cyan',3,True)
    s.path('M1100 425 H1188','cyan',3,True)
    s.path('M875 525 V575','red',3,True)
    s.text(875,608,'CONTROLLED ATTACK DOMAINS',21,'red',650,'middle')
    tiles=[('CI and build pipeline','01 · 02 · 04 · 12 · 13','server'),
           ('API and business policy','06 · 07 · 08 · 19 · 25','api'),
           ('Data and code execution','15 · 16 · 17 · 18 · 22','database'),
           ('Identity and browser','10 · 14 · 20 · 21','browser'),
           ('Artifacts and telemetry','03 · 11 · 23 · 24','artifact'),
           ('Loopback mock services','09 · temporary HTTP fixtures','server')]
    for i,(title,ids,kind) in enumerate(tiles):
        x=100+(i%3)*550;y=650+(i//3)*185
        s.rect(x,y,450,150)
        s.icon(kind,x+370,y+103,.4)
        s.text(x+23,y+46,title,25,weight=600)
        s.text(x+23,y+92,ids,21,'muted')
        s.path(f'M{x+23} {y+119} h55','red',3)
        s.path(f'M{x+90} {y+119} h55','teal',3)
    s.text(100,1034,'Docker: non-root, read-only, no external network. Native: no sandbox. HTTP endpoints bind to loopback.',20,'muted')
    x,y=1780,220
    s.rect(x,y,560,430,stroke='gold',dash='12 6')
    s.text(x+25,y+50,'05  /  Separate real kind lab',29,'gold',650)
    s.icon('kube',x+421,y+162,.9)
    s.text(x+25,y+100,'Kubernetes API + scoped RBAC',23,'white')
    s.text(x+25,y+143,'kind-pipelineproof',22,'muted',mono=True)
    s.text(x+25,y+218,'V: CI identity reads dummy Secret',22,'red')
    s.text(x+25,y+260,'S: read denied; intended patch allowed',21,'teal')
    s.text(x+25,y+314,'make k8s-up k8s-test',22,'gold',mono=True)
    s.text(x+25,y+366,'Requires Docker + kind; not run by setup.sh.',20,'muted')
    s.path('M2060 650 V715','teal',3,True)
    x,y=1780,730
    s.rect(x,y,560,340,stroke='teal')
    s.text(x+25,y+51,'Auditable evidence',30,weight=650)
    s.text(x+25,y+105,'reports/assessment.*',21,'teal',mono=True)
    s.text(x+25,y+151,'reports/rbac.json',21,'teal',mono=True)
    s.text(x+25,y+197,'reports/scenario-audit/audit.json',20,'teal',mono=True)
    s.text(x+25,y+253,'24 local + fresh 05 = complete audit',21,'white')
    s.text(x+25,y+300,'Observed results, never assumed passes.',20,'muted')
    s.path('M1650 425 H1745 V900 H1768','teal',3,True)
    s.rect(60,1120,2280,150)
    s.text(90,1166,'GITHUB CI / SECURITY GATES',23,'cyan',700)
    s.text(90,1210,'Read-only validation workflows',22,'muted')
    s.text(680,1166,'Unit · browser · Semgrep · Trivy · Gitleaks',26,'white')
    s.text(680,1210,'ZAP baseline · Syft SBOM · Cosign integrity checks',23,'muted')
    s.text(1830,1166,'Release decision is separate',23,'gold',600)
    s.text(1830,1210,'HIGH / CRITICAL findings block',21,'muted')
    s.path('M900 1120 V1080','cyan',3,True)
    s.text(1200,1315,'lab/  ·  labs/  ·  pipelines/  ·  infra/  ·  scenarios/  ·  tests/  ·  docs/  ·  reports/',20,'muted',anchor='middle')
    s.save(out/'pipelineproof-overview.svg')


def export(out):
    executable=shutil.which('inkscape')
    if not executable: raise SystemExit('Inkscape is required only for --export (PDF/PNG). SVG files were already generated.')
    cache=ROOT/'.work/diagram-render'
    env=dict(os.environ,XDG_CACHE_HOME=str(cache/'cache'),XDG_CONFIG_HOME=str(cache/'config'),INKSCAPE_PROFILE_DIR=str(cache/'inkscape'))
    for folder in ('cache','config','inkscape'):(cache/folder).mkdir(parents=True,exist_ok=True)
    for stem,width in (('pipelineproof-overview',3600),('pipelineproof-attack-map',6000)):
        source=out/(stem+'.svg')
        subprocess.run([executable,str(source),'--export-type=pdf','--export-text-to-path',f'--export-filename={out/(stem+".pdf")}'],env=env,check=True)
        subprocess.run([executable,str(source),'--export-type=png',f'--export-width={width}',f'--export-filename={out/(stem+".png")}'],env=env,check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/diagrams')
    args=parser.parse_args()
    entries=scenario_inventory()
    assert {entry['number'] for entry in entries}==set(CASES)==set(range(1,26))
    args.output.mkdir(parents=True,exist_ok=True)
    full_map(args.output,{entry['number']:entry for entry in entries})
    overview(args.output)
    if args.export:export(args.output)
    print(f'Wrote diagram assets to {args.output}')

if __name__=='__main__':main()
