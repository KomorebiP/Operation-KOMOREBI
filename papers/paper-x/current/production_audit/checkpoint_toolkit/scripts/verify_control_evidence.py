#!/usr/bin/env python3
"""Recheck the preserved fixture receipts, their source pins and raw logs.

This authenticates a recorded run against the delivered files. It does not
invoke Lean again and does not authenticate the truth of arbitrary supplied pins.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from audit_engine import (AuditError, LEAN_SHA256, audit_source, parse_audit,
    parse_json, require_rejection, require_success, safe_relative, sha256)
ROOT=Path(__file__).resolve().parents[1]
POSITIVE={
 'valid_theorem_and_definition':[
   {'name':'Fixture.ok','kind':'theorem','owner':'Fixture'},
   {'name':'Fixture.number','kind':'definition','owner':'Fixture'}],
 'private_generated_declarations':[], 'linked_witness_positive':[],
 'witness_countermodel_positive':[]}
POLICY={
 'axiom_in_type_detected':'P10_FORBIDDEN_AXIOMS',
 'direct_custom_axiom':'P10_FORBIDDEN_AXIOMS',
 'transitive_custom_axiom':'P10_FORBIDDEN_AXIOMS',
 'axiom_outside_namespace':'P10_FORBIDDEN_AXIOMS',
 'unused_axiom_not_in_target_list':'P10_FORBIDDEN_AXIOMS',
 'wrong_declaration_kind':'P10_TARGET_KIND',
 'missing_target':'P10_TARGET_MISSING',
 'wrong_owner':'P10_TARGET_OWNER:',
 'duplicate_target':'P10_DUPLICATE_TARGET'}
COMPILER={
 'false_equality':'error', 'sorry_rejected':'sorry','admit_rejected':'sorry',
 'distinct_existentials_not_same_witness':'Application type mismatch',
 'zero_multiplicity_not_nonzero':'error'}
EXPECTED=set(POSITIVE)|set(POLICY)|set(COMPILER)

def check(root:Path=ROOT)->dict:
    seen=set(); commands=0; receipts=[]; cases_out=[]
    files=sorted((root/'evidence/controls').glob('*/CONTROLS.json'))
    if not files:raise AuditError('No completed control receipts')
    for receipt in files:
        directory=receipt.parent
        r=parse_json(receipt.read_text())
        if r['status']!='PASS' or r['paper_x_production_modules_checked']!=0:
            raise AuditError('Receipt is not a fixture-only pass')
        for field,path in [('runner_sha256',root/'scripts/run_compiler_controls.py'),
                           ('engine_sha256',root/'scripts/audit_engine.py'),
                           ('audit_source_sha256',root/'lean/AuditCore.lean')]:
            if r[field]!=sha256(path):raise AuditError('Tool/source revision mismatch: '+field)
        if r['compiler_sha256']!=LEAN_SHA256:raise AuditError('Compiler mismatch')
        if set(r['all_case_names'])!=EXPECTED or len(r['all_case_names'])!=len(EXPECTED):
            raise AuditError('Unexpected case inventory')
        selected=r['all_case_names'][r['first_case']-1:r['last_case']]
        if selected!=r['selected_case_names'] or selected!=[c['name'] for c in r['cases']]:
            raise AuditError('Case range/inventory mismatch')
        if r['case_count']!=len(r['cases']):raise AuditError('Case count mismatch')
        logs={}
        for command in r['commands']:
            p=directory/safe_relative(command['relative_log'])
            if p.is_symlink() or sha256(p)!=command['log_sha256']:
                raise AuditError('Changed command log')
            key=p.stem
            if key in logs:raise AuditError('Duplicate command log')
            logs[key]=(command,p.read_text(encoding='utf-8',errors='strict'))
            if key!='compiler_version' and '-DwarningAsError=true' not in command['argv']:
                raise AuditError('Required compiler warning policy missing')
            commands+=1
        require_success(logs['compiler_version'][0]);require_success(logs['audit_tool_compile'][0])
        if sha256(directory/'common/AuditCore.lean')!=r['audit_source_sha256']:
            raise AuditError('Compiled auditor source mismatch')
        for c in r['cases']:
            name=c['name']
            if name in seen or name not in EXPECTED or c['status']!='PASS':
                raise AuditError('Overlapping/unknown/nonpassing case')
            seen.add(name)
            if sha256(directory/'cases'/name/'Fixture.lean')!=c['source_sha256']:
                raise AuditError('Changed fixture source')
            cr,ct=logs[name+'_compile']
            if cr['returncode']!=c['compile_returncode']:raise AuditError('Compiler return-code mismatch')
            if name in COMPILER:
                require_rejection(cr,ct,COMPILER[name]);stage='compiler rejection'
            else:
                require_success(cr)
                ar,at=logs[name+'_audit']
                if ar['returncode']!=c['audit_returncode']:raise AuditError('Audit return-code mismatch')
                if name in POLICY:
                    require_rejection(ar,at,POLICY[name]);stage='policy rejection after compilation'
                    if any('"complete"' in line for line in at.splitlines() if line.startswith('P10AUDIT ')):
                        raise AuditError('Rejected audit emitted a completion event')
                else:
                    source=directory/'cases'/name/'AuditRun.lean'
                    if source.read_text()!=audit_source(['Fixture'],POSITIVE[name]):
                        raise AuditError('Positive audit request mismatch')
                    parsed=parse_audit(ar,at,['Fixture'],POSITIVE[name])
                    if parsed['declarations']!=c['declarations']:raise AuditError('Census count mismatch')
                    if name=='private_generated_declarations' and not any('_private' in d['name'] for d in parsed['records']):
                        raise AuditError('No private declaration observed')
                    stage='positive audit'
            cases_out.append({'name':name,'status':'PASS','stage':stage,
                 'source_sha256':c['source_sha256'],
                 'receipt':receipt.relative_to(root).as_posix()})
        receipts.append({'path':receipt.relative_to(root).as_posix(),'sha256':sha256(receipt)})
    if seen!=EXPECTED:raise AuditError('Incomplete control suite')
    return {'status':'PASS','scope':'recorded verifier fixtures, not Paper X production',
       'paper_x_production_modules_checked':0,'cases':len(seen),
       'positive_cases':len(POSITIVE),'compiler_rejections':len(COMPILER),
       'policy_rejections_after_compilation':len(POLICY),'compiler_commands':commands,
       'receipt_parts':receipts,'results':cases_out}

if __name__=='__main__':
    try:print(json.dumps(check(),indent=2))
    except Exception as e:print('FAILED: '+str(e),file=sys.stderr);sys.exit(1)
