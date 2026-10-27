#!/usr/bin/env python3
"""Execute the eleven unchanged standard-library baseline regression run() gates.

Only the reviewed regression source members are copied from the preserved ZIP,
byte for byte, into the fresh output directory. Their importable run functions
are invoked; no Lean verifier, historical test launcher, installation, or
archived output is executed or changed. Counts have heterogeneous units.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import zipfile

NAMES=['regressions','second_regressions','third_regressions','fourth_regressions','fifth_regressions','sixth_regressions','seventh_regressions','eighth_regressions','ninth_regressions','tenth_regressions','eleventh_regressions']
SEEDS={'regressions':90609,'fourth_regressions':904704,'fifth_regressions':9052026,'sixth_regressions':906,'seventh_regressions':907,'eighth_regressions':908,'ninth_regressions':9072026,'tenth_regressions':91010}
HISTORICAL={'regressions':'verification/regressions.json','second_regressions':'verification/second_exact_regressions.json','third_regressions':'verification/third_exact_regressions.json','fourth_regressions':'verification/fourth_exact_regressions.json','fifth_regressions':'verification/fifth_regressions.json','sixth_regressions':'verification/sixth_regressions/20260907T175337626387Z/regressions.json','seventh_regressions':'verification/seventh_regressions/20260907T175338565246Z/regressions.json','eighth_regressions':'verification/eighth_regressions/20260907T175339896772Z/regressions.json','ninth_regressions':'verification/ninth_regressions/results.json','eleventh_regressions':'verification/eleventh_regressions.json'}

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--archive',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
prefix='PRSC_IX_v0.11.0_Nishibuchi_Completion/'
entries=[]
with zipfile.ZipFile(args.archive) as z:
    srcdir=args.output_dir/'unchanged_sources';srcdir.mkdir()
    for index,name in enumerate(NAMES):
        member=prefix+'scripts/'+name+'.py';data=z.read(member)
        local=srcdir/(name+'.py');local.write_bytes(data)
        spec=importlib.util.spec_from_file_location('baseline_exact_'+str(index),local)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        started=time.monotonic()
        result=module.run()
        elapsed=time.monotonic()-started
        if result.get('status') not in ('PASS','EXACT_RATIONAL_REGRESSIONS_PASS','EXACT_FINITE_CHECKS_PASS','EXACT_ARITHMETIC_REGRESSIONS_PASS'):
            # Preserve alternate positive spelling without silently accepting failure.
            status=result.get('status','')
            if not isinstance(status,str) or ('PASS' not in status) or any(word in status for word in ('FAIL','INCOMPLETE')):
                raise AssertionError((name,'non-passing regression result',status))
        if local.read_bytes()!=data:raise AssertionError('Executed source changed')
        historical_path=HISTORICAL.get(name);comparisons={}
        if historical_path:
            historic=json.loads(z.read(prefix+historical_path))
            for key in ('counts','mathematical_sha256','mathematical_digest','digest'):
                if key in result and key in historic:
                    comparisons[key]=result[key]==historic[key]
                    if not comparisons[key]:raise AssertionError((name,key,'historical comparison mismatch'))
        output=args.output_dir/(name+'.json');output.write_text(json.dumps(result,indent=2)+'\n')
        entries.append({'gate':name,'executed_function':name+'.run','source_member':member,'source_sha256':hashlib.sha256(data).hexdigest(),'source_copy_sha256':hashlib.sha256(local.read_bytes()).hexdigest(),'status':result['status'],'recorded_seed':SEEDS.get(name),'runtime_seconds':elapsed,'count_units':'Original script fields; include cases, rows, families, algebraic assertions, metadata, and invalid-input controls. Do not sum as a theorem or experiment count.','counts':result.get('counts'),'historical_comparisons':comparisons,'historical_report_member':prefix+historical_path if historical_path else None,'result_file':str(output)})
        print(name+': '+str(result['status'])+'; unchanged source and available mathematical fingerprints compared',flush=True)
report={'status':'PASS','archive_sha256':hashlib.sha256(args.archive.read_bytes()).hexdigest(),'gate_count':len(entries),'execution':'Reviewed unchanged byte-identical regression modules loaded by importlib and their run functions directly invoked. Original CLI main wrappers, Lean/Lake verifiers and historical unittest scripts are not invoked.','entries':entries,'software':'Python standard library; deterministic seeded random samples where declared','non_claims':['No fresh Lean compilation','No pytest/unittest session','Counts are not homogeneous and not a universal proof','Not the unrecovered original July experimental package'],'residual_risks':['The original regression implementations are replayed, not independently rewritten; the separate independent finite gate provides orthogonal construction checks.','Some scripts exercise seed-determined samples rather than exhaustive full families.']}
(args.output_dir/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: eleven unchanged baseline exact regression gates')
