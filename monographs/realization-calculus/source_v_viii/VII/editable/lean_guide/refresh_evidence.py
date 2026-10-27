#!/usr/bin/env python3
"""Pin the frozen current computational report into the guide's evidence record."""
from pathlib import Path
import argparse,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--verification',type=Path,default=R/'verification/monograph_checks/COMPUTATIONAL_REVIEW.json');a=p.parse_args();report=a.verification.resolve();x=json.loads(report.read_text())
if x['status']!='PASS_FOR_STATED_SCOPE':raise RuntimeError('Current computation report does not pass its stated scope')
expected={'original_pytest':('collected_cases',22),'original_direct_functions':('functions',22),'verifier_software':('methods',16),'original_experiments':('numeric_fields',1045),'strengthened_raw':('checks',18049),'strengthened_corrected':('checks',17699),'independent_fraction':('assertions_total',269),'inherited_formal_static':('targets',323),'constructed_bindings':('objects',6),'guide_original_sympy':('total_assertions_including_controls',180),'guide_extended_exact':('positive_assertions',373),'guide_plates':('plate_sources',38)}
for gate,(key,count) in expected.items():
    if x['gates'][gate]['status']!='PASS' or x['gates'][gate][key]!=count:raise RuntimeError('Revise current prose for changed count or status: '+gate)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,value in x['report_dependency_pins'].items():
    if sha(R/name)!=value:raise RuntimeError('Current report dependency changed: '+name)
S=R/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot'
out={'edition_date':'2026-10-09','current_report_relative_to_package':report.relative_to(R).as_posix(),'current_report_sha256':sha(report),'current_computation_report':x,'inherited_release_summary_sha256':sha(S/'verification/final_finite_release_run/SUMMARY.json'),'inherited_constructed_audit_sha256':sha(S/'verification/final_finite_release_run/CONSTRUCTED_OBJECTS_AUDIT.json'),'lean_kernel_checked_in_current_edition':False,'scope':'Frozen report identity and documentation count consistency. No new experiment execution.'}
models_path=R/'verification/monograph_checks/TRADITIONAL_EXACT_MODELS_REVIEW.json'
models=json.loads(models_path.read_text())
if models['status']!='PASS_FOR_STATED_SCOPE' or models['positive_assertions']!=30 or models['false_assertions_rejected']!=6:raise RuntimeError('Revise current model prose for changed scope')
for name,value in models['input_pins'].items():
    if sha(R/name)!=value:raise RuntimeError('Traditional model report pin changed: '+name)
out.update(traditional_model_report_relative_to_package=models_path.relative_to(R).as_posix(),traditional_model_report_sha256=sha(models_path),traditional_model_report=models)
(H/'generated/evidence_provenance.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'PASS','current_computation_report_sha256':sha(report)}))
