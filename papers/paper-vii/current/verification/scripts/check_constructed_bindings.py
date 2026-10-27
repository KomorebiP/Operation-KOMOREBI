#!/usr/bin/env python3
"""Fresh static binding checks for six inherited constructed-object axiom audits."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    base=a.source.resolve()/'complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot'
    folder=base/'verification/final_finite_release_run';report=json.loads((folder/'CONSTRUCTED_OBJECTS_AUDIT.json').read_text())
    spec=importlib.util.spec_from_file_location('construction_original_verifier',base/'scripts/verify.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    inv=base/'verification/constructed_objects_inventory.json';source=base/report['source']
    log=folder/'constructed_objects.log';summary=folder/'SUMMARY.json';runner=base/'scripts/check_low_memory.py'
    expected=set(json.loads(inv.read_text()));parsed=v.parse_axiom_audits(log.read_text())
    prior=json.loads(summary.read_text())
    checks={'source_hash':sha(source)==report['source_sha256'],
        'inventory_hash':sha(inv)==report['inventory_sha256'],'runner_hash':sha(runner)==report['runner_sha256'],
        'log_hash':sha(log)==report['log_sha256'],'cumulative_summary_binding':sha(summary)==report['cumulative_summary_sha256'],
        'inventory_six':len(expected)==report['construction_count']==6,
        'source_print_inventory':set(re.findall(r'^#print axioms ([\w.]+)',v.without_comments(source.read_text()),re.M))==expected,
        'parsed_log_inventory':set(parsed)==expected,
        'stored_audits_equal_log':parsed==report['axiom_audits'],
        'allowed_axioms':not ({ax for xs in parsed.values() for ax in xs}-v.ALLOWED_AXIOMS),
        'inherited_success':report['pass'] and report['exit_code']==0 and prior['complete'] and prior['pass'],
        'cumulative_sources_current':all(sha(base/row['source'])==row['sha256'] for row in prior['modules'])}
    assert all(checks.values()),checks
    r={'scope':'Fresh static binding audit of inherited six constructed-object checks; no Lean invocation',
       'checks':checks,'check_count':len(checks),'construction_count':6,'theorem_count_addition':0,
       'inherited_utc':prior['started_utc'],'axiom_audits':parsed,
       'hashes':{str(p.relative_to(a.source.resolve())):sha(p) for p in (source,inv,runner,log,summary,folder/'CONSTRUCTED_OBJECTS_AUDIT.json')},
       'nonclaims':['No fresh Lean kernel compilation or constructed-object audit execution.',
           'Omitted compiled interfaces and imported Mathlib proofs are not independently rechecked.'],'status':'passed'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('PASS: 12 static binding checks for six inherited constructed objects; no new theorem count')

if __name__=='__main__':main()
