"""Generate exact binary witnesses and source-level Lean certificate consumers."""
from pathlib import Path
from dataclasses import asdict
import json
from proof_path_theory import analyze_affine_realizations

ROOT = Path(__file__).resolve().parents[1]
CASES = [
 dict(name='one_bit', dimension=3, compatibility=[[1,1,1]], protected=[[1,0,0]], candidate=[0,0,0], observation=[[0,1,0]]),
 dict(name='incompatible', dimension=3, compatibility=[[1,1,0]], protected=[[1,0,0],[0,1,0]], candidate=[0,1,0], observation=[[0,0,1]]),
 dict(name='redundant', dimension=3, compatibility=[[1,1,0]], protected=[[0,0,0]], candidate=[0,0,0], observation=[[0,0,1],[0,0,1]]),
 dict(name='unique', dimension=3, compatibility=[[1,0,0],[0,1,0],[0,0,1]], protected=[[0,0,0]], candidate=[1,1,1], observation=[[1,1,1]]),
]
def vec(xs): return '![' + ', '.join(map(str, xs)) + ']'
def mat(rows): return '![' + ', '.join(vec(r) for r in rows) + ']'
def main():
    lines=['import ProofPath.Binary', '', 'namespace ProofPath.Generated', 'open Matrix', '']
    records=[]
    for case in CASES:
        args={k:v for k,v in case.items() if k != 'name'}
        report=analyze_affine_realizations(**args)
        name=case['name']; n=case['dimension']; a=case['compatibility'];p=case['protected']; x=case['candidate']
        rows=a+p; b=[0]*len(a)+[sum(i*j for i,j in zip(row,x))%2 for row in p]
        lines += [f'def {name}_M : Matrix (Fin {len(rows)}) (Fin {n}) (ZMod 2) := {mat(rows)}',
                  f'def {name}_b : Fin {len(rows)} → ZMod 2 := {vec(b)}']
        if report.feasible:
            lines += [f'theorem {name}_positive : ∃ y, {name}_M.mulVec y = {name}_b := by',
                      f'  exact ⟨{vec(report.solution)}, by decide⟩',
                      f'theorem {name}_count : (Finset.univ.filter (fun y : Fin {n} → ZMod 2 =>',
                      f'    {name}_M.mulVec y = {name}_b)).card = {report.realization_count} := by decide']
            q=case['observation']
            lines += [f'def {name}_Q : Matrix (Fin {len(q)}) (Fin {n}) (ZMod 2) := {mat(q)}',
                      f'theorem {name}_observations : ((Finset.univ.filter (fun y : Fin {n} → ZMod 2 =>',
                      f'    {name}_M.mulVec y = {name}_b)).image {name}_Q.mulVec).card = {2**report.observation_gain_bits} := by decide']
        else:
            lines += [f'def {name}_w : Fin {len(rows)} → ZMod 2 := {vec(report.obstruction_witness)}',
                      f'theorem {name}_negative : ¬ ∃ y, {name}_M.mulVec y = {name}_b := by',
                      f'  exact row_witness_sound {name}_M {name}_b {name}_w (by decide) (by decide)']
        lines += ['']
        records.append(dict(input=case,report=asdict(report),stacked_matrix=rows,rhs=b))
    lines += ['end ProofPath.Generated','']
    (ROOT/'formal/ProofPath/Generated.lean').write_text('\n'.join(lines))
    (ROOT/'data/bridge_examples.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Generated four examples with exact Lean certificate obligations.')
if __name__=='__main__':main()
