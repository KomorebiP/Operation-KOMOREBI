#!/usr/bin/env python3
"""Isolated tests of actual release helper functions; never runs production gates."""
from __future__ import annotations
import ast
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
common = importlib.import_module('release_common_v041')
negative = importlib.import_module('run_negative_v041')
records = []

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(name, actual, expected):
    records.append({'name': name, 'actual': actual, 'expected': expected, 'passed': actual == expected})

with tempfile.TemporaryDirectory(prefix='gate_review_tmp_', dir=ROOT/'results/v0.41.0') as directory:
    root = Path(directory)
    (root/'tests/negative').mkdir(parents=True)
    (root/'negative').mkdir()
    (root/'AVOC').mkdir()
    (root/'.lake/build/lib/lean/AVOC').mkdir(parents=True)
    source = root/'tests/negative/FalseGateFixture.lean'
    source.write_text('import AVOC.Fixture\nexample : False := by\n  trivial\n')
    log = root/'negative/FalseGateFixture.log'
    record_path = log.with_suffix('.json')
    imports = {'AVOC.Fixture': 'fixture-digest'}
    negative.ROOT = root
    negative.NEG = root/'negative'
    negative.import_hashes = lambda _: imports.copy()
    def negative_case(name, text, expected, **changes):
        log.write_text(text)
        record = dict(source_sha256=sha(source), returncode=1, timed_out=False,
                      source_unchanged=True, imports_unchanged=True,
                      warning_as_error=True, log_sha256=sha(log), import_outputs=imports.copy())
        record.update(changes)
        record_path.write_text(json.dumps(record))
        check(name, negative.valid(source), expected)
    substantive = 'error: unsolved goals\n⊢ False\n'
    negative_case('negative_substantive_control', substantive, True)
    negative_case('negative_empty_log', '', False)
    negative_case('negative_timeout', substantive, False, timed_out=True)
    negative_case('negative_signal_crash', substantive, False, returncode=-11)
    negative_case('negative_wrong_exit', substantive, False, returncode=2)
    negative_case('negative_stale_source', substantive, False, source_sha256='stale')
    negative_case('negative_stale_import', substantive, False, import_outputs={'AVOC.Fixture':'old'})
    negative_case('negative_changed_import', substantive, False, imports_unchanged=False)
    negative_case('negative_missing_import', substantive, False, import_outputs={'AVOC.Fixture':None})
    negative_case('negative_setup', substantive+'error: failed to synthesize Decidable False\n', False)
    negative_case('negative_mixed_unknown', substantive+'error: unknown identifier foo\n', False)
    negative_case('negative_mixed_expected_token', substantive+"error: expected token ')'\n", False)
    negative_case('negative_mixed_unexpected_eof', substantive+'error: unexpected end of input\n', False)
    negative_case('negative_mixed_exception', substantive+'uncaught exception: invalid object file\n', False)
    negative_case('negative_mixed_panic', substantive+'PANIC at Lean.Main: internal compiler error\n', False)
    positive_source = root/'AVOC/Fixture.lean'
    positive_source.write_text('theorem fixture : True := by trivial\n')
    positive_log = root/'positive.log'
    positive_log.write_text('')
    output = root/'.lake/build/lib/lean/AVOC/Fixture.olean'
    output.write_bytes(b'fixture object')
    common.ROOT = root
    common.import_hashes = lambda _: imports.copy()
    base = dict(returncode=0,timed_out=False,warning_as_error=True,
                source_sha256=sha(positive_source),source_unchanged=True,imports_unchanged=True,
                import_outputs=imports.copy(),log='positive.log',log_sha256=sha(positive_log),output_sha256=sha(output))
    check('build_valid_control', not common.build_record_errors('AVOC/Fixture.lean',base),True)
    check('build_empty_record',bool(common.build_record_errors('AVOC/Fixture.lean',{})),True)
    for key,value in [('returncode',1),('timed_out',True),('warning_as_error',False),('source_sha256','stale'),('source_unchanged',False),('imports_unchanged',False),('import_outputs',{}),('log','missing.log'),('log_sha256','stale'),('output_sha256','stale')]:
        record=deepcopy(base);record[key]=value
        check('build_reject_'+key,bool(common.build_record_errors('AVOC/Fixture.lean',record)),True)
    output.unlink()
    check('build_missing_object',bool(common.build_record_errors('AVOC/Fixture.lean',base)),True)
    tree=ast.parse((ROOT/'tools/release_check_v041.py').read_text())
    functions={node.name:node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}
    ns=dict(ROOT=root,errors=[],evidence={},sha=sha,json=json)
    exec(compile(ast.Module(body=[functions['load'],functions['check_hashes']],type_ignores=[]),'<actual release helpers>','exec'),ns)
    evidence_path=root/'fixture.json'
    for name,value in [('empty_object',{}),('empty_array',[]),('null',None),('false',False),('number',0),('wrong_array',[1])]:
        ns['errors'].clear();evidence_path.write_text(json.dumps(value))
        result=ns['load']('fixture.json')
        check('load_reject_'+name,result is None and bool(ns['errors']),True)
    ns['errors'].clear();evidence_path.write_text('{"passed":true}')
    check('load_dictionary_control',ns['load']('fixture.json'),{'passed':True})
    for name,mapping in [('empty',{}),('null',None),('missing',{'missing':'abc'}),('stale',{'fixture.json':'abc'})]:
        ns['errors'].clear();ns['check_hashes']('fixture',mapping)
        check('hash_reject_'+name,bool(ns['errors']),True)

tree=ast.parse((ROOT/'tools/release_check_v041.py').read_text())
functions={node.name:node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}
ns={'re':re}
exec(compile(ast.Module(body=[functions['recorder_oracle_errors']],type_ignores=[]),'<actual oracle schema helper>','exec'),ns)
# This is a synthetic validator control, not evidence of a Lean execution.
oracle=json.loads((ROOT/'results/v0.41.0/executable_development_python.json').read_text())
oracle['calibration_export']['checks']=16
oracle['actual_lean']=dict(status='passed',exhaustive_words=4369,word_lengths=[0,3],
    longer_scenarios=12,total_words=4381,invalid_structure_checks=22,
    valid_boundary_checks=4,per_call_timeout_seconds=180,comparison='exact parsed JSON equality',
    batches=[dict(start=start,count=min(256,4381-start),request_sha256='a'*64,
                  response_sha256='b'*64,runtime_seconds=0.1) for start in range(0,4381,256)])
oracle_errors=ns['recorder_oracle_errors']
check('oracle_synthetic_schema_control',oracle_errors(oracle),[])
check('oracle_empty',bool(oracle_errors({})),True)
for name,section,key,value in [
    ('not_run','actual_lean','status','not_run'),
    ('finite_count','finite_oracle','word_count',69904),
    ('missing_status','finite_oracle','status_counts',{}),
    ('status_count','finite_oracle','status_counts',{'recorded':957,'rejected':68947}),
    ('interface_count','interface','invalid_raw_json',0),
    ('export_incomplete','calibration_export','checks',14),
    ('false_authentication','calibration_export','authentication_established',True),
    ('missing_batch','actual_lean','batches',oracle['actual_lean']['batches'][:-1])]:
    candidate=deepcopy(oracle);candidate[section][key]=value
    check('oracle_reject_'+name,bool(oracle_errors(candidate)),True)
for name,key,value in [('overlap','start',0),('empty_count','count',0),('float_count','count',256.0),('digest','response_sha256','bad'),('duration','runtime_seconds',-1)]:
    candidate=deepcopy(oracle);candidate['actual_lean']['batches'][1][key]=value
    check('oracle_reject_batch_'+name,bool(oracle_errors(candidate)),True)
candidate=deepcopy(oracle);candidate['source_sha256'].pop('AVOC/RecorderCodec.lean')
check('oracle_reject_omitted_codec',bool(oracle_errors(candidate)),True)
module_assignment=next(node for node in ast.walk(functions['main']) if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='new_modules' for t in node.targets))
ns=dict(order=['AVOC/Old.lean','AVOC/NewNoTheorems.lean','tools/Runner.lean'],inherited_modules={'AVOC/Old.lean':'abc'})
exec(compile(ast.Module(body=[module_assignment],type_ignores=[]),'<actual module review membership>','exec'),ns)
check('review_includes_new_module_without_named_theorems',sorted(ns['new_modules']),['AVOC/NewNoTheorems.lean'])
check('baseline_record_pin',sha(ROOT/'results/v0.41.0/release_baseline.json'),common.BASELINE_RECORD_SHA256)

result=dict(kind='isolated_actual_gate_helper_probes',status='passed' if all(r['passed'] for r in records) else 'failed',
            cases=len(records),passed=sum(r['passed'] for r in records),records=records,
            tool_sha256={name:sha(ROOT/name) for name in sorted(common.RELEASE_TOOLS)},
            limits=['Synthetic local fixtures exercise helpers, not a universal gate proof.',
                    'The production release gate, Lean build, and package were not run by this probe.'])
out=ROOT/'results/v0.41.0/gate_review_probes.json'
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':result['status'],'cases':result['cases'],'passed':result['passed'],'failed':[r['name'] for r in records if not r['passed']]}))
raise SystemExit(0 if result['status']=='passed' else 1)
