#!/usr/bin/env python3
"""Replay Block 68 from pinned inputs; full predecessor replay is optional.

No cached PASS label substitutes for regenerated scientific output. Reports are
written outside the immutable package. NumPy is an optional exact-integer
accelerator; set BEAL_FORCE_STDLIB=1 to use the slower scalar count backends.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PREDECESSOR = 'Komorebi_Beal_Block67_Deep_Cyclotomic_Semilinearity_Conductor_Closure_v6.7.0.zip'
OUTPUTS = [
 'columns68.json','independent_columns68.json','sieve68.json','independent_sieve68.json',
 'count68.json','independent_count68.json','columns_extended68.json',
 'independent_columns_extended68.json','sieve_extended68.json','independent_sieve_extended68.json',
 'input_audit68.json','support68.json','backend_audit68.json',
]

def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(path: Path):
    return json.loads(path.read_text())

def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')

def integrity(root: Path) -> dict:
    manifest = load(root/'MANIFEST.json')
    expected = manifest['payload_sha256']
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual == set(expected)|{'MANIFEST.json'}, 'Package member set changed')
    for name, digest in expected.items():
        require(sha((root/name).read_bytes()) == digest, 'Payload hash changed: '+name)
    return {'payload_hashes': len(expected), 'member_count': len(actual), 'status': 'PASS'}

def inherited_inputs(root: Path) -> dict:
    record = load(root/'work68/source_records/INHERITED_INPUTS.json')
    raw = (root/'predecessor'/PREDECESSOR).read_bytes()
    require(sha(raw) == record['predecessor_sha256'], 'Predecessor archive changed')
    cache = {(): raw}
    leaf_bytes = []
    for item in record['files']:
        chain = tuple(item['archive_chain'])
        for i in range(1,len(chain)+1):
            prefix = chain[:i]
            if prefix not in cache:
                with zipfile.ZipFile(io.BytesIO(cache[chain[:i-1]])) as archive:
                    cache[prefix] = archive.read(chain[i-1])
        with zipfile.ZipFile(io.BytesIO(cache[chain])) as archive:
            data = archive.read(item['member'])
        require(sha(data) == item['sha256'], 'Inherited source leaf changed: '+item['member'])
        leaf_bytes.append(data)
    # Reconstruct the old Frobenius fixture from its THREE actual frozen outputs.
    f67,f66,f65 = [json.loads(x) for x in leaf_bytes[:3]]
    gens = copy.deepcopy(f65['generators'])
    rows = copy.deepcopy(f65['kummer_rows'])
    pairs = copy.deepcopy(f65['paired_trace_sets'])
    for previous in (f66,f67):
        for test in previous['tests']:
            k=str(test['q']);gens[k]=test['generator'];rows[k]=test['kummer_rows'];pairs[k]=test['paired_trace_sets']
    reconstructed = {
      'schema':'beal.block68.frozen-frobenius.v1',
      'test_order':[71,29,491,43,211,239,281,379,421,449,631,659,1051],
      'generators':gens,'kummer_rows':rows,'paired_trace_sets':pairs,
      'inherited_universe':f65['universe'],'inherited_columns':f65['columns'],
      'claimed_previous_final_count':f67['count'],
      'coefficient_encoding':'a+7*b denotes a+b*w, w^2=5 in F49',
      'source_leaves':record['files'][:3],
    }
    fixture = root/'work68/inputs/frobenius.json'
    require(load(fixture)==reconstructed,'Frozen fixture is not derived from its pinned sources')
    require(sha(fixture.read_bytes())==record['fixture_sha256'],'Frozen fixture hash changed')
    idx=next(i for i,item in enumerate(record['files']) if item['member'].endswith('/work62/verification/pointcounts.json'))
    old_counts=json.loads(leaf_bytes[idx])
    ref={'status':'PASS_FINITE_COUNTS','primes':[next(x for x in old_counts['primes'] if x['q']==29)]}
    require(load(root/'work68/inputs/backend_reference29.json')==ref,'Backend reference is not its pinned count record')
    return {'status':'PASS','source_leaves':len(leaf_bytes),'archive_levels_opened':len(cache),
            'predecessor_sha256':sha(raw),'fixture_reconstructed_from_source':True}

def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            target=(destination/item.filename).resolve()
            require(target.is_relative_to(destination.resolve()),'Unsafe archive path')
            require(not item.is_dir() or target!=destination.resolve(),'Unexpected archive root entry')
        z.extractall(destination)

def comparable(name: str, data):
    # Backend availability is environmental evidence, not a mathematical invariant.
    d=copy.deepcopy(data)
    if name=='backend_audit68.json':
        d.pop('numpy_available',None);d.pop('primary_backend_equalities',None)
    return d

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path)
    p.add_argument('--integrity-only',action='store_true')
    p.add_argument('--replay-predecessors',action='store_true')
    p.add_argument('--job-timeout',type=int,default=1200)
    a=p.parse_args()
    require(a.job_timeout>0,'Positive timeout required')
    if a.report:
        a.report=a.report.resolve()
        require(not a.report.is_relative_to(ROOT),'Write verification reports OUTSIDE the immutable package')
    start=time.monotonic()
    report={'schema':'beal.block68.execution.v1','started_at':dt.datetime.now(dt.timezone.utc).isoformat(),
      'status':'RUNNING','jobs':[],'negative_controls':[], 'python':sys.version,'platform':platform.platform(),
      'job_timeout_seconds':a.job_timeout,'replay_predecessors':a.replay_predecessors,
      'proof_boundary':'Finite arithmetic and provenance only. Universal and analytical proofs remain conditional written arguments; no Lean or external mathematical review.'}
    try:
        report['integrity']=integrity(ROOT)
        report['inherited_inputs']=inherited_inputs(ROOT)
        if a.integrity_only:
            report['status']='PASS_INTEGRITY'
        else:
            with tempfile.TemporaryDirectory(prefix='beal68_replay_') as temp:
                scratch=Path(temp)/'project'
                shutil.copytree(ROOT,scratch)
                v=scratch/'work68/verification';c=scratch/'work68/computations';inp=scratch/'work68/inputs'
                expected={name:load(v/name) for name in OUTPUTS}
                expected_extension=load(inp/'frobenius_extended.json')
                for name in OUTPUTS:(v/name).unlink()
                (inp/'frobenius_extended.json').unlink()
                env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
                env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1';env['MKL_NUM_THREADS']='1'
                def run(name: str, script: Path, args: list, reject: str|None=None):
                    argv=[sys.executable,'-B',str(script),*[str(x) for x in args]]
                    before=time.monotonic()
                    try:
                        result=subprocess.run(argv,cwd=scratch,env=env,text=True,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,timeout=a.job_timeout,check=False)
                    except subprocess.TimeoutExpired as exc:
                        report['jobs'].append({'name':name,'argv':argv,'status':'TIMEOUT_INCONCLUSIVE',
                            'elapsed_seconds':time.monotonic()-before})
                        raise RuntimeError('Timeout is inconclusive: '+name) from exc
                    event={'name':name,'argv':argv,'returncode':result.returncode,
                           'elapsed_seconds':time.monotonic()-before,'output':result.stdout}
                    report['jobs'].append(event)
                    if reject is None:
                        require(result.returncode==0,'Execution failed: '+name+'\n'+result.stdout[-2000:])
                    else:
                        require(result.returncode!=0 and reject in result.stdout,
                                'Negative control failed or rejected for wrong reason: '+name+'\n'+result.stdout[-2000:])
                        report['negative_controls'].append({'name':name,'rejected':True,'diagnostic':reject})
                    print(name,result.returncode,round(event['elapsed_seconds'],3),flush=True)
                    return result
                # Every output is regenerated, including both old and expanded conductor systems.
                run('counts',c/'count68.py',['--output',v/'count68.json'])
                run('separate_counts',c/'independent_count68.py',['--counts',v/'count68.json','--output',v/'independent_count68.json'])
                run('extend_fixture',c/'extend_inputs68.py',['--fixture',inp/'frobenius.json','--counts',v/'count68.json','--output',inp/'frobenius_extended.json'])
                require(load(inp/'frobenius_extended.json')==expected_extension,'Regenerated extended fixture mismatch')
                for suffix,fixture in [('',inp/'frobenius.json'),('_extended',inp/'frobenius_extended.json')]:
                    primary_col=v/f'columns{suffix}68.json'; independent_col=v/f'independent_columns{suffix}68.json'
                    primary_sieve=v/f'sieve{suffix}68.json';independent_sieve=v/f'independent_sieve{suffix}68.json'
                    run('columns'+suffix,c/'columns68.py',['--fixture',fixture,'--output',primary_col])
                    run('separate_columns'+suffix,c/'independent_columns68.py',['--fixture',fixture,'--certificate',primary_col,'--output',independent_col])
                    run('sieve'+suffix,c/'sieve68.py',['--fixture',fixture,'--columns',primary_col,'--output',primary_sieve])
                    run('separate_sieve'+suffix,c/'independent_sieve68.py',['--fixture',fixture,'--columns',independent_col,'--certificate',primary_sieve,'--output',independent_sieve])
                run('input_audit',c/'audit_inputs68.py',['--base',inp/'frobenius.json','--extended',inp/'frobenius_extended.json','--counts',v/'count68.json','--output',v/'input_audit68.json'])
                run('support',c/'support68.py',['--sieve',v/'sieve_extended68.json','--output',v/'support68.json'])
                run('backend_and_factors',c/'backend_audit68.py',['--reference',inp/'backend_reference29.json','--columns',v/'columns_extended68.json','--output',v/'backend_audit68.json'])
                report['regenerated_outputs']={}
                for name in OUTPUTS:
                    found=load(v/name)
                    require(comparable(name,found)==comparable(name,expected[name]),'Full output comparison failed: '+name)
                    report['regenerated_outputs'][name]=sha((v/name).read_bytes())
                report['scientific_json_comparisons']=len(OUTPUTS)
                report['support_result']=load(v/'support68.json')
                report['backend_audit']=load(v/'backend_audit68.json')
                # Diagnostic-specific corruption controls. These must fail; no timeout counts as rejection.
                neg=Path(temp)/'negative';neg.mkdir()
                corrupted=load(v/'columns_extended68.json')
                rec=next(x for x in corrupted['columns'] if x['q']==307)
                rec['rows']['701']=(rec['rows']['701']+1)%7
                save(neg/'column.json',corrupted)
                run('reject_changed_degree_two_column',c/'independent_columns68.py',
                    ['--fixture',inp/'frobenius_extended.json','--certificate',neg/'column.json','--output',neg/'unused_column.json'],
                    'Changed degree-dependent twisted column')
                corrupted=load(v/'columns_extended68.json');corrupted['universe'].remove(797)
                save(neg/'missing_conductor.json',corrupted)
                run('reject_omitted_new_conductor',c/'independent_columns68.py',
                    ['--fixture',inp/'frobenius_extended.json','--certificate',neg/'missing_conductor.json','--output',neg/'unused_missing.json'],
                    'Incomplete conductor universe')
                corrupted=load(inp/'frobenius_extended.json');corrupted['paired_trace_sets']['701'].append([0])
                save(neg/'false_pair.json',corrupted)
                run('reject_invented_polynomial_pair',c/'audit_inputs68.py',
                    ['--base',inp/'frobenius.json','--extended',neg/'false_pair.json','--counts',v/'count68.json','--output',neg/'unused_pair.json'],
                    'Invented or missing actual polynomial pair')
                corrupted=load(v/'sieve_extended68.json');corrupted['expanded28']['count']=0;corrupted['expanded28']['survivors']=[]
                save(neg/'false_zero.json',corrupted)
                run('reject_false_zero_survivors',c/'independent_sieve68.py',
                    ['--fixture',inp/'frobenius_extended.json','--columns',v/'independent_columns_extended68.json','--certificate',neg/'false_zero.json','--output',neg/'unused_zero.json'],
                    'Changed complete survivor list')
                corrupted=load(v/'count68.json');corrupted['primes'][0]['rows'][0]['N1']+=1
                save(neg/'false_count.json',corrupted)
                run('reject_altered_point_count',c/'independent_count68.py',
                    ['--counts',neg/'false_count.json','--output',neg/'unused_count.json'],
                    'Point-count row mismatch')
                old=(scratch/'README.md').read_bytes();(scratch/'README.md').write_bytes(old+b'\nCORRUPTED\n')
                try:
                    integrity(scratch)
                except AssertionError as exc:
                    require('Payload hash changed: README.md' in str(exc),'Wrong payload rejection')
                    report['negative_controls'].append({'name':'reject_changed_payload','rejected':True,'diagnostic':str(exc)})
                else:
                    raise AssertionError('Changed payload accepted')
                finally:
                    (scratch/'README.md').write_bytes(old)
                # Preserve and distinguish the observed historical replay from an optional new one.
                historical=load(ROOT/'work68/verification/Block67_Replay_exit.json')
                historical_result=load(ROOT/'work68/verification/Block67_Replay.json')
                require(historical['returncode']==0,'Historical predecessor replay did not finish')
                require(str(historical_result['status']).startswith('PASS'),'Historical predecessor reported failure')
                report['recorded_predecessor_replay']={
                    'status':historical_result['status'],'returncode':historical['returncode'],
                    'elapsed_seconds':historical['elapsed_seconds'],
                    'record_sha256':sha((ROOT/'work68/verification/Block67_Replay.json').read_bytes()),
                    'meaning':'Separate observed replay during Block68 development; not rerun in this invocation unless requested.'}
                if a.replay_predecessors:
                    pr=Path(temp)/'predecessor_restore';pr.mkdir()
                    safe_extract(ROOT/'predecessor'/PREDECESSOR,pr)
                    prior=pr/'Komorebi_Beal_Block67'
                    run('fresh_full_predecessor',prior/'verify.py',
                        ['--replay-predecessors','--report',Path(temp)/'predecessor_new_report.json'])
                    report['fresh_predecessor_replay']=load(Path(temp)/'predecessor_new_report.json')
                # Ensure no script altered the release package being certified.
                require(integrity(ROOT)==report['integrity'],'Release package changed during replay')
                report['status']='PASS_DECLARED_CHECKS'
    except Exception as exc:
        report['status']='FAILED'
        report['error']=type(exc).__name__+': '+str(exc)
        print(report['error'],file=sys.stderr,flush=True)
    report['elapsed_seconds']=time.monotonic()-start
    report['finished_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    if a.report:save(a.report,report)
    print(report['status'],flush=True)
    return 0 if report['status'].startswith('PASS') else 1

if __name__=='__main__':
    raise SystemExit(main())
