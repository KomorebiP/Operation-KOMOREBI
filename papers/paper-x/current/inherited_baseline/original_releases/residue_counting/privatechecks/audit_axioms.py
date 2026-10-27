from pathlib import Path
import sys, json, os, subprocess, hashlib
root=Path(__file__).resolve().parents[1]
audit=root/'privatechecks/audit_replay'
records=json.loads((audit/'compilation.json').read_text())
modules=sys.argv[1:] or list(dict.fromkeys(r['module'] for r in records if r['exit_code']==0))
src=audit/'lean/AuditAxioms.lean'
text=''.join(f'import PaperX.{m}\n' for m in modules)
text+='import Lean.Util.CollectAxioms\nopen Lean Elab Command in\nrun_cmd do\n'
text+='  let targetModules : Array Name := #['+', '.join(f'`PaperX.{m}' for m in modules)+']\n'
text+='''  let env ← getEnv
  let mut count : Nat := 0
  for (name, _) in env.constants.toList do
    if let some idx := env.getModuleIdxFor? name then
      if targetModules.contains env.header.moduleNames[idx.toNat]! then
        let axioms ← Lean.collectAxioms name
        for ax in axioms do
          unless #[`Classical.choice, `Quot.sound, `propext].contains ax do
            throwError "Unapproved axiom {ax} in {name}"
        logInfo m!"AUDIT_DECL {name}: {axioms}"
        count := count + 1
  logInfo m!"AUDIT_DECLARATION_COUNT {count}"
'''
src.write_text(text)
sys.path.insert(0,str(root/'checks'))
from lean_env import lean_env
lean,env=lean_env('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
env['LEAN_PATH']=str(audit/'build')+os.pathsep+str(root/'privatechecks/audit_baseline/build')+os.pathsep+env['LEAN_PATH'].split(os.pathsep,1)[1]
with (audit/'logs/AuditAxioms.log').open('w') as f:
 p=subprocess.run([lean,'-DwarningAsError=true',str(src)],cwd=audit/'lean',env=env,stdout=f,stderr=subprocess.STDOUT)
result={'exit_code':p.returncode,'modules':modules,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
(audit/'axioms.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
sys.exit(p.returncode)
