#!/usr/bin/env python3
"""Exercise the audit against isolated fixtures using the actual pinned Lean.

This is verification-tool testing. It is NOT a replay of Paper X's 122 modules.
Each fixture builds fresh objects in its own directory. No old project object
is on LEAN_PATH. Failed cases require specific diagnostics, not just nonzero exit.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from audit_engine import (AuditError, audit_source, execute, parse_audit,
    require_rejection, require_success, runtime_env, save_json, sha256, utc)
ROOT=Path(__file__).resolve().parents[1]
FLAGS=['-j1','-M2048','-DwarningAsError=true']

def run(runtime:Path, work:Path, first:int=1, last:int=18)->dict:
    if not (1 <= first <= last <= 18):
        raise AuditError("Case range must satisfy 1 <= first <= last <= 18")
    if work.exists():
        raise AuditError('Choose a NEW control output directory')
    work.mkdir(parents=True)
    report={'schema':'paper_x.audit_controls.v1','status':'RUNNING','started_utc':utc(),
            'scope':'isolated verifier fixtures, not Paper X production',
            'paper_x_production_modules_checked':0,'first_case':first,'last_case':last,
            'runner_sha256':sha256(Path(__file__)),
            'engine_sha256':sha256(ROOT/'scripts/audit_engine.py'),
            'cases':[],'commands':[]}
    def save():save_json(work/'CONTROLS.json',report)
    common=work/'common';common.mkdir()
    shutil.copy2(ROOT/'lean/AuditCore.lean',common/'AuditCore.lean')
    lean,env=runtime_env(runtime,[common])
    def cmd(label,argv,cwd,localenv):
        record=execute(list(map(str,argv)),cwd,localenv,60,work/'logs'/(label+'.log'))
        record['relative_log']=Path(record['log']).relative_to(work).as_posix()
        record['relative_cwd']=Path(record['cwd']).relative_to(work).as_posix()
        report['commands'].append(record);save()
        return record,Path(record['log']).read_text(encoding='utf-8',errors='replace')
    try:
        r,text=cmd('compiler_version',[lean,'--version'],common,env);require_success(r)
        report['compiler_version']=text.strip();report['compiler_sha256']=sha256(lean)
        r,text=cmd('audit_tool_compile',[lean,*FLAGS,'-o',common/'AuditCore.olean','AuditCore.lean'],common,env)
        require_success(r)
        report['audit_source_sha256']=sha256(common/'AuditCore.lean')
        positive='namespace Fixture\ndef number : Nat := 7\ntheorem ok : number = 7 := rfl\nend Fixture\n'
        cases=[
         dict(name='valid_theorem_and_definition',source=positive,
              targets=[dict(name='Fixture.ok',kind='theorem',owner='Fixture'),dict(name='Fixture.number',kind='definition',owner='Fixture')]),
         dict(name='private_generated_declarations',source='namespace Fixture\nprivate theorem hidden : True := True.intro\ntheorem shown : True := hidden\nstructure Carrier where\n  value : Nat\nend Fixture\n',private_check=True),
         dict(name='axiom_in_type_detected',source='namespace Escaped\naxiom typeOnly : Prop\nend Escaped\nnamespace Fixture\ntheorem typedIdentity (p : Escaped.typeOnly) : Escaped.typeOnly := p\nend Fixture\n',reject='P10_FORBIDDEN_AXIOMS'),
         dict(name='direct_custom_axiom',source='namespace Fixture\naxiom injected : False\ntheorem invalid : False := injected\nend Fixture\n',reject='P10_FORBIDDEN_AXIOMS'),
         dict(name='transitive_custom_axiom',source='namespace Fixture\naxiom injected : False\nprivate theorem bridge : False := injected\ntheorem invalid : False := bridge\nend Fixture\n',reject='P10_FORBIDDEN_AXIOMS'),
         dict(name='axiom_outside_namespace',source='namespace Other\naxiom injected : False\nend Other\nnamespace Fixture\ntheorem invalid : False := Other.injected\nend Fixture\n',reject='P10_FORBIDDEN_AXIOMS'),
         dict(name='unused_axiom_not_in_target_list',source=positive+'namespace Elsewhere\naxiom unused : False\nend Elsewhere\n',targets=[dict(name='Fixture.ok',kind='theorem',owner='Fixture')],reject='P10_FORBIDDEN_AXIOMS'),
         dict(name='wrong_declaration_kind',source=positive,targets=[dict(name='Fixture.number',kind='theorem',owner='Fixture')],reject='P10_TARGET_KIND'),
         dict(name='missing_target',source=positive,targets=[dict(name='Fixture.absent',kind='theorem',owner='Fixture')],reject='P10_TARGET_MISSING'),
         dict(name='wrong_owner',source=positive,owners=['Fixture','AuditCore'],targets=[dict(name='Fixture.ok',kind='theorem',owner='AuditCore')],reject='P10_TARGET_OWNER:'),
         dict(name='duplicate_target',source=positive,targets=[dict(name='Fixture.ok',kind='theorem',owner='Fixture')]*2,reject='P10_DUPLICATE_TARGET'),
         dict(name='false_equality',source='theorem falseEq : (0 : Nat) = 1 := by rfl\n',compile_reject='error'),
         dict(name='sorry_rejected',source='theorem hole : False := by sorry\n',compile_reject='sorry'),
         dict(name='admit_rejected',source='theorem hole : False := by admit\n',compile_reject='sorry'),
         dict(name='distinct_existentials_not_same_witness',source='theorem bad (p q : Nat → Prop) (hp : ∃ n, p n) (hq : ∃ n, q n) : ∃ n, p n ∧ q n := by\n  rcases hp with ⟨a, ha⟩\n  rcases hq with ⟨b, hb⟩\n  exact ⟨a, ha, hb⟩\n',compile_reject='Application type mismatch'),
         dict(name='zero_multiplicity_not_nonzero',source='theorem bad (multiplicity : Nat) : multiplicity ≠ 0 := by\n  intro h\n  exact Nat.noConfusion h\n',compile_reject='error'),
         dict(name='linked_witness_positive',source='namespace Fixture\ntheorem linked (p q : Nat → Prop) (a b : Nat) (hp : p a) (hq : q b) (h : a = b) : ∃ n, p n ∧ q n := by\n  subst b\n  exact ⟨a, hp, hq⟩\nend Fixture\n'),
         dict(name='witness_countermodel_positive',source='namespace Fixture\ntheorem separated : (∃ n : Nat, n = 0) ∧ (∃ n : Nat, n = 1) ∧ ¬ (∃ n : Nat, n = 0 ∧ n = 1) := by\n  refine ⟨⟨0,rfl⟩, ⟨1,rfl⟩, ?_⟩\n  rintro ⟨n,h0,h1⟩\n  exact Nat.zero_ne_one (h0.symm.trans h1)\nend Fixture\n'),
        ]
        report['all_case_names']=[c['name'] for c in cases]
        cases=cases[first-1:last]
        report['selected_case_names']=[c['name'] for c in cases];save()
        for case in cases:
            name=case['name'];print('CONTROL',name,flush=True)
            directory=work/'cases'/name;directory.mkdir(parents=True)
            f=directory/'Fixture.lean';f.write_text(case['source'],encoding='utf-8')
            lean,localenv=runtime_env(runtime,[directory,common])
            r,text=cmd(name+'_compile',[lean,*FLAGS,'-o',directory/'Fixture.olean','Fixture.lean'],directory,localenv)
            result={'name':name,'source_sha256':sha256(f),'compile_returncode':r['returncode']}
            if 'compile_reject' in case:
                require_rejection(r,text,case['compile_reject'])
                result.update(status='PASS',observed='intended compiler rejection')
            else:
                require_success(r)
                owners=case.get('owners',['Fixture']);targets=case.get('targets',[])
                a=directory/'AuditRun.lean';a.write_text(audit_source(owners,targets),encoding='utf-8')
                r,text=cmd(name+'_audit',[lean,*FLAGS,a.name],directory,localenv)
                result['audit_returncode']=r['returncode']
                if 'reject' in case:
                    require_rejection(r,text,case['reject'])
                    result.update(status='PASS',observed='compiled fixture rejected by policy')
                else:
                    parsed=parse_audit(r,text,owners,targets)
                    if case.get('private_check') and not any('_private' in d['name'] for d in parsed['records']):
                        raise AuditError('Private declaration disappeared from module census')
                    save_json(directory/'AUDIT.json',parsed)
                    result.update(status='PASS',observed='positive audited',declarations=parsed['declarations'])
            report['cases'].append(result);save()
        report.update(status='PASS',finished_utc=utc(),case_count=len(report['cases']))
    except BaseException as error:
        report.update(status='FAILED',finished_utc=utc(),error=f'{type(error).__name__}: {error}')
    save();return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--first',type=int,default=1,help='First case, 1-indexed inclusive')
    ap.add_argument('--last',type=int,default=18,help='Last case, 1-indexed inclusive')
    args=ap.parse_args()
    try:
        r=run(args.runtime.resolve(),args.work.resolve(),args.first,args.last)
        print(r['status'],len(r['cases']),r.get('error',''))
        sys.exit(0 if r['status']=='PASS' else 1)
    except Exception as e:
        print('FAILED:',e,file=sys.stderr);sys.exit(1)
