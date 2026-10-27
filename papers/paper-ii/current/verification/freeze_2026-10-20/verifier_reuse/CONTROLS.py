#!/usr/bin/env python3
"""Independent synthetic controls for the exact delivered freeze verifier."""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, os, shutil, subprocess, sys

HERE = Path(__file__).resolve().parent
DELIVERED = HERE.parent/'release/Paper_I_Frozen_Release_2026-10-20/scripts/verify_integrity.py'
HELPER = HERE.parent/'verify_integrity_frozen.py'
FIXTURES = HERE/'control_fixtures'
PRESERVATION = 'verification/freeze_2026-10-20/BASELINE_PRESERVATION.json'
BEFORE = 'verification/freeze_2026-10-20/before/'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2)+'\n')
def entry(path, original=None):
    p=path
    result={'path':str(path), 'bytes':p.stat().st_size, 'sha256':sha(p)}
    return result
def list_manifest(root):
    rows=[]
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.relative_to(root).as_posix()!='MANIFEST_SHA256.json':
            rows.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    return {'schema':'synthetic-freeze-control/1','count':len(rows),'self_excluded':'MANIFEST_SHA256.json','files':rows}
def make_fixture(name):
    root=FIXTURES/name
    if root.exists(): shutil.rmtree(root)
    (root/'scripts').mkdir(parents=True)
    shutil.copyfile(DELIVERED,root/'scripts/verify_integrity.py')
    (root/'source.txt').write_bytes(b'unchanged source\n')
    (root/'admin.txt').write_bytes(b'current administrative text\n')
    old=root/BEFORE/'admin.txt'
    old.parent.mkdir(parents=True,exist_ok=True)
    old.write_bytes(b'original administrative text\n')
    baseline={'count':2,'changed_administrative_paths':['admin.txt'],'files':[
        {'original_path':'source.txt','preserved_path':'source.txt','bytes':(root/'source.txt').stat().st_size,'sha256':sha(root/'source.txt')},
        {'original_path':'admin.txt','preserved_path':BEFORE+'admin.txt','bytes':old.stat().st_size,'sha256':sha(old)}
    ]}
    dump(root/PRESERVATION,baseline)
    dump(root/'MANIFEST_SHA256.json',list_manifest(root))
    return root
def run_case(name, expected_success, mutate=None, re_manifest=False, expected_message=None):
    root=make_fixture(name)
    if mutate: mutate(root)
    if re_manifest: dump(root/'MANIFEST_SHA256.json',list_manifest(root))
    run=subprocess.run([sys.executable,str(root/'scripts/verify_integrity.py')],cwd=root,text=True,capture_output=True,timeout=15,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    passed=(run.returncode==0)==expected_success and (expected_message is None or expected_message in run.stderr+run.stdout)
    return {'case':name,'expected':'accept' if expected_success else 'reject','passed':passed,'exit_code':run.returncode,'expected_message':expected_message,'stdout':run.stdout,'stderr':run.stderr}
def change_manifest(root,fn):
    p=root/'MANIFEST_SHA256.json'; m=json.loads(p.read_text()); fn(m); dump(p,m)
def change_preservation(root,fn):
    p=root/PRESERVATION; m=json.loads(p.read_text()); fn(m); dump(p,m)
def duplicate_manifest(root):
    def fn(m): m['files'].append(copy.deepcopy(m['files'][0])); m['count']=len(m['files'])
    change_manifest(root,fn)
def colon_file(root): (root/'data:stream').write_bytes(b'colon path\n')
def alias_destinations(root):
    def fn(m): m['files'][1]['preserved_path']=m['files'][0]['preserved_path']
    change_preservation(root,fn)
def invalid_mapping(root):
    shutil.copyfile(root/'source.txt',root/'alias.txt')
    change_preservation(root,lambda m:m['files'][0].update(preserved_path='alias.txt'))
def invalid_original(root):
    change_preservation(root,lambda m:m['files'][0].update(original_path='../source.txt'))
def baseline_same_size_corruption(root):
    p=root/BEFORE/'admin.txt'; b=p.read_bytes(); p.write_bytes(bytes([b[0]^1])+b[1:])
def symlink(root): (root/'source_link').symlink_to('source.txt')

initial_hash=sha(DELIVERED)
assert initial_hash==sha(HELPER),'Delivered/helper verifier mismatch'
cases=[
    run_case('positive_unchanged_and_changed_admin',True,expected_message='Baseline preservation PASS'),
    run_case('missing_file',False,lambda r:(r/'source.txt').unlink(),expected_message='File set mismatch'),
    run_case('extra_file',False,lambda r:(r/'extra.txt').write_text('extra'),expected_message='File set mismatch'),
    run_case('same_size_corruption',False,lambda r:(r/'source.txt').write_bytes(b'Unchanged source\n'),expected_message='File identity mismatch'),
    run_case('duplicate_manifest_path',False,duplicate_manifest,expected_message='Duplicate path'),
    run_case('windows_colon_path',False,colon_file,True,expected_message='Invalid manifest path'),
    run_case('aliased_baseline_destinations',False,alias_destinations,True,expected_message='destinations are not unique'),
    run_case('invalid_baseline_mapping',False,invalid_mapping,True,expected_message='Invalid baseline preservation mapping'),
    run_case('traversal_original_path',False,invalid_original,True,expected_message='Noncanonical manifest path'),
    run_case('baseline_same_size_corruption',False,baseline_same_size_corruption,True,expected_message='Preserved baseline mismatch'),
    run_case('symlink_rejected',False,symlink,False,expected_message='Symlink not permitted'),
]
assert sha(DELIVERED)==initial_hash,'Delivered verifier changed while controls ran'
result={
    'schema':'komorebi.paper-i.freeze-integrity-controls/1',
    'status':'PASS' if all(c['passed'] for c in cases) else 'FAIL',
    'checked_at_utc':datetime.now(timezone.utc).isoformat(),
    'verifier_sha256':initial_hash,
    'verifier_source':str(DELIVERED),
    'helper_matches_delivered':True,
    'final_root_modified':False,
    'execution_platform':sys.platform,
    'python_version':sys.version,
    'case_count':len(cases),'positive_cases':1,'negative_cases':len(cases)-1,
    'cases':cases,
    'scope':'Independent small filesystem fixtures exercise the exact delivered verifier. Mutated preservation tables are rehashed into otherwise valid outer manifests so baseline checks are reached. No actual frozen-release file was modified.',
    'limitations':['These controls run on Linux, including explicit Windows-colon syntax rejection; they are not execution on Windows.','The verifier authenticates identities relative to its manifest; it is not a digital signature or proof checker.']
}
dump(HERE/'CONTROLS.json',result)
summary='Paper I frozen-verifier controls\n\n'+result['status']+'\n\n'+str(len(cases))+' synthetic cases: one positive and ten rejection cases.\nDelivered verifier SHA-256: '+initial_hash+'\n\n'
summary+='\n'.join(c['case']+': '+('PASS' if c['passed'] else 'FAIL')+' (exit '+str(c['exit_code'])+')' for c in cases)
summary+='\n\nExecuted on Linux. Windows-colon syntax rejection was exercised; no Windows runtime execution is claimed. Preservation-table attacks were included in valid outer manifests, so their rejection tests the baseline-preservation checks. The final root was not modified.\n'
(HERE/'CONTROLS.txt').write_text(summary)
print(json.dumps({'status':result['status'],'case_count':len(cases),'failed':[c['case'] for c in cases if not c['passed']],'verifier_sha256':initial_hash},indent=2))
sys.exit(result['status']!='PASS')
