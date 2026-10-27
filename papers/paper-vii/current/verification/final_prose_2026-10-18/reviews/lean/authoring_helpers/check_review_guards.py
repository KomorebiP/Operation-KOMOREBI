from pathlib import Path
import hashlib,json,shutil,subprocess,sys

ROOT=Path('/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18')
H=ROOT/'editable/lean_guide'
S=ROOT/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot'
OUT=Path('/workspace/scratch/be33f0b6c391/tmp/p7_final_lean_prose')
C=OUT/'guard_controls/guide'
C.mkdir(parents=True,exist_ok=True)
for name in ('static_check.py','data_helpers.py','assemble.py','navigation.py','Paper_VII_Lean_Guide_Final.tex'):
    shutil.copy2(H/name,C/name)
for name in ('chapters','excerpts','prose_review_2026-10-18'):
    shutil.copytree(H/name,C/name,dirs_exist_ok=True)
for name in ('chapters','excerpts'):
    shutil.copytree(H/'historical_assembly'/name,C/'historical_assembly'/name,dirs_exist_ok=True)
(C/'generated').mkdir(exist_ok=True)
for name in ('dependency_pins.json','excerpts.json'):
    shutil.copy2(H/'generated'/name,C/'generated'/name)

def run(name,expected):
    p=subprocess.run([sys.executable,'-B',str(C/'static_check.py'),'--source',str(S)],capture_output=True,text=True)
    report={'name':name,'exit_code':p.returncode,'expected_exit_code':expected,'stdout':p.stdout,'stderr':p.stderr,'pass':p.returncode==expected}
    for f in ('static_reconciliation.json','preservation.json','mathematical_span_preservation.json','prose_review_preservation.json'):
        report[f]=json.loads((C/'generated'/f).read_text())['status']
    return report

records=[run('unchanged_reviewed_source',0)]
p=C/'chapters/geometry.tex';original=p.read_bytes()
needle='The section $s$ is twice continuously differentiable there.'
assert p.read_text().count(needle)==1
p.write_text(p.read_text().replace(needle,'The section $s$ is continuously differentiable there.',1))
records.append(run('reject_deleted_regularity_hypothesis_with_unchanged_math_spans',1))
assert records[-1]['prose_review_preservation.json']=='FAIL'
p.write_bytes(original)
p=C/'excerpts/packet_structure.lean.txt';original=p.read_bytes()
p.write_bytes(original+b'\n-- Deliberate isolated source-excerpt tamper control.\n')
records.append(run('reject_changed_raw_source_excerpt',1))
assert records[-1]['preservation.json']=='FAIL'
p.write_bytes(original)
out={'status':'PASS' if all(r['pass'] for r in records) else 'FAIL','scope':'Verifier-software controls for the new closed editorial preservation check. No Lean execution and no change to delivered mathematical or formal sources.','positive_checks':1,'rejected_controls':2,'records':records}
(OUT/'CLOSED_REVIEW_GUARD_CHECKS.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':out['status'],'positive_checks':1,'rejected_controls':2}))
