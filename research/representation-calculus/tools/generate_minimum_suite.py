"""Generate untrusted, kernel-checked optimality endpoints for the frozen v0.3 suite."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]

def main():
    records=json.loads((ROOT/'source_records/SYMBOLIC_EXPORTS_v03.json').read_text())
    lines=['module','public import MatrixPrimeMinimality']
    lines += ['public import '+r['module'] for r in records]
    lines += ['', '@[expose] public section',
              'set_option backward.isDefEq.respectTransparency false',
              'open Fin.CommRing',
              'open Komorebi.Representation Komorebi.Representation.Matrix','']
    report=[]
    for rec in records:
        src=json.loads((ROOT/rec['source']).read_text())
        p,r,d=src['p'],src['r'],src['dimension']
        k,o=len(src['actions']),len(src['observations']);t=rec['target_coordinates']
        ns=rec['namespace']
        lines += [f'namespace {ns}',
                  'theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide',
                  f'theorem minimum_linear_budget (budget : Nat) :',
                  f'    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin {k}) (Fin {o}) R)',
                  f'      (e : (Fin {d} → R) →ₗ[R] (Fin n → R)),',
                  f'      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔',
                  f'      {t} ≤ budget :=',
                  f'  fin_certificate_minimum_iff (m:={p**r}) (p:={p}) (r:={r}) (by decide) (by decide) (by decide)',
                  '    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget',
                  f'end {ns}','']
        report.append({'tag':rec['tag'],'namespace':ns,'p':p,'r':r,'d':d,'t':t,
                       'source':rec['source'],'certificate':rec['certificate'],
                       'theorem':ns+'.minimum_linear_budget'})
    # Keep each algebraic instantiation batch small enough for bounded Lean checks.
    chunks=[]
    for start in range(0,len(records),16):
        group=records[start:start+16]
        name=f'MinimumBatch{start//16:02d}'
        text=['module','public import MatrixPrimeMinimality']
        text+=['public import '+x['module'] for x in group]
        text+=['','@[expose] public section',
               'set_option backward.isDefEq.respectTransparency false',
               'open Fin.CommRing',
               'open Komorebi.Representation Komorebi.Representation.Matrix','']
        alltext='\n'.join(lines)
        for item in group:
            ns=item['namespace'];begin=alltext.index('namespace '+ns+'\n')
            end=alltext.index('end '+ns+'\n',begin)+len('end '+ns+'\n')
            text.append(alltext[begin:end])
        (ROOT/'formalization'/(name+'.lean')).write_text('\n'.join(text)+'\n')
        chunks.append(name)
    (ROOT/'formalization/CertifiedMinima.lean').write_text('module\n'+'\n'.join('public import '+n for n in chunks)+'\n')
    (ROOT/'evidence/MINIMUM_INSTANCES.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'generated_minimum_endpoints':len(report),'zero_coordinate_cases':sum(r['t']==0 for r in report)}))
if __name__=='__main__': main()
