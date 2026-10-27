from pathlib import Path
import sys, os, json, subprocess, hashlib

root = Path(__file__).resolve().parents[1]
audit = root / 'privatechecks/audit_replay'
(audit / 'lean').mkdir(parents=True, exist_ok=True)
(audit / 'logs').mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / 'checks'))
from lean_env import lean_env
lean, env = lean_env('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
env['LEAN_PATH'] = str(audit / 'build') + os.pathsep + env['LEAN_PATH'].split(os.pathsep, 1)[1]
controls = {
    'AuditResiduePositive': ('pass', '''import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ((-1 : ℤ) : ZMod 3) ≠ ((-1 : ℤ).natAbs : ZMod 3) := by decide
example : ∀ a b : ZMod 4, (a ^ 2 + b ^ 2).val % 2 = 1 → a ^ 2 + b ^ 2 = 1 := by
  decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 0)).card = 2 := by decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 0 := by decide
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 2)).card = 2 := by decide
'''),
    'AuditFalseUnsignedCongruence': ('unsolved goals', '''import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ((-1 : ℤ) : ZMod 3) = ((-1 : ℤ).natAbs : ZMod 3) := by
  have hn : ((-1 : ℤ) : ZMod 3) ≠ ((-1 : ℤ).natAbs : ZMod 3) := by decide
  simp only [hn]
'''),
    'AuditFalseNormResidueSurjectivity': ('unsolved goals', '''import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : ∃ a b : ZMod 4, a ^ 2 + b ^ 2 = 3 := by
  have hn : ¬ ∃ a b : ZMod 4, a ^ 2 + b ^ 2 = 3 := by decide
  simp only [hn]
'''),
    'AuditFalseTargetUniformity': ('unsolved goals', '''import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic
example : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 1 := by
  have hn : (Finset.univ.filter (fun x : ZMod 4 => 2 * x = 1)).card = 0 := by decide
  rw [hn]
  norm_num
'''),
    'AuditPlaceholder': ('declaration uses `sorry`', '''example : True := by
  sorry
''')
}
selected = sys.argv[1:] or list(controls)
records_path = audit / 'controls.json'
records = json.loads(records_path.read_text()) if records_path.exists() else []
records = [r for r in records if r['name'] not in selected]
for name in selected:
    expected, source = controls[name]
    path = audit / 'lean' / f'{name}.lean'
    path.write_text(source)
    p = subprocess.run([lean, '-DwarningAsError=true', str(path)], cwd=audit / 'lean',
                       env=env, capture_output=True, text=True)
    output = p.stdout + p.stderr
    (audit / 'logs' / f'{name}.log').write_text(output)
    valid = (p.returncode == 0) if expected == 'pass' else (
        p.returncode != 0 and expected in output and ('⊢ False' in output or name == 'AuditPlaceholder'))
    row = {'name': name, 'expected': expected, 'exit_code': p.returncode,
           'expected_result_observed': valid,
           'source_sha256': hashlib.sha256(source.encode()).hexdigest()}
    records.append(row)
    print(json.dumps(row), flush=True)
records_path.write_text(json.dumps(records, indent=2) + '\n')
raise SystemExit(0 if all(r['expected_result_observed'] for r in records) else 1)
