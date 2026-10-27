from pathlib import Path
import os, re, subprocess, hashlib, json, time

here=Path(__file__).resolve().parent
project=here.parents[1]
runtime=project.parent/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'
modules=['CyclicNormalization113','CyclicDefect113','ActualScalarLift113','EquivariantRepresentation113']
endpoints=[
 'PaperXI.CyclicNormalization113.canonical_action_of_actual_profile',
 'PaperXI.CyclicNormalization113.canonical_generator_of_actual_form',
 'PaperXI.CyclicNormalization113.canonical_equivariant_bridge_of_actual_profile',
 'PaperXI.CyclicDefect113.correctingCharacter_coboundary',
 'PaperXI.CyclicDefect113.exists_equivariant_cochain',
 'PaperXI.CyclicDefect113.exists_equivariant_scalarBridge',
 'PaperXI.ActualScalarLift113.actualLift_power_eq_one',
 'PaperXI.EquivariantRepresentation113.scalarTransport_covariant',
 'PaperXI.EquivariantRepresentation113.exists_equivariant_actual_action',
]
source=here/'INDEPENDENT_ENDPOINT_AXIOMS.lean'
source.write_text(''.join('import PaperXI.'+m+'\n' for m in modules)+
                  ''.join('#check '+n+'\n#print axioms '+n+'\n' for n in endpoints))
env=os.environ.copy()
env['LD_PRELOAD']=str(runtime/'compat/app_path.so')
env['PATH']=str(runtime/'toolchain/bin')+':'+env['PATH']
env['LEAN_PATH']=':'.join(map(str,[here/'objects',*sorted((runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]))
t0=time.monotonic()
proc=subprocess.run([str(runtime/'toolchain/bin/lean'),'-j1','-DwarningAsError=true',str(source)],env=env,cwd=project,capture_output=True,text=True,timeout=90)
log=proc.stdout+proc.stderr
(here/'INDEPENDENT_ENDPOINT_AXIOMS.log').write_text(log)
assert proc.returncode==0,log
found=re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",log,re.S)
assert {n for n,_ in found}==set(endpoints)
axioms={a.strip() for _,body in found for a in body.split(',') if a.strip()}
assert axioms <= {'Classical.choice','Quot.sound','propext'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'status':'PASS','exit_code':proc.returncode,'seconds':time.monotonic()-t0,
        'endpoints':endpoints,'axioms':sorted(axioms),'audit_source_sha256':sha(source),
        'objects':{m:sha(here/'objects/PaperXI'/f'{m}.olean') for m in modules},
        'source_hashes':{m:sha(project/'formalization/PaperXI'/f'{m}.lean') for m in modules}}
(here/'AXIOMS_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'endpoint_count':len(endpoints),'axioms':sorted(axioms)}))
