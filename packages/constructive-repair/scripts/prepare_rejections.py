from pathlib import Path
import sys,copy,json
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'python'))
from repair_certificates import *
p=read_json(root/'examples/corpus/Case000_input.json');c=read_json(root/'examples/corpus/Case000_certificate.json')
lines=['import KomorebiRepair.Generated.Inputs00','set_option autoImplicit false',
       'set_option maxRecDepth 100000','open KomorebiRepair.RationalCertificates']
records=[]
for key,label in [('P','BrokenSplit'),('G','BrokenFactor'),('J','FalseDimension'),('U','FalseOutput')]:
    bad=copy.deepcopy(c);a=Mat.from_wire(bad['matrices'][key]);rows=[list(r) for r in a.data];rows[0][0]+=1
    bad['matrices'][key]=Mat.of(rows,a.cols).to_wire();ms=decode_certificate(p,bad)
    ns='Reject'+label;lines += ['namespace '+ns,'abbrev D := Case000.D','abbrev R := Case000.R']
    for name,a in ms.items():lines+=emit_matrix(name,a)
    expr='checkOptimalConstruction D R P K L F G J Q' if key!='U' else 'decide (D * U + E * W = -R)'
    lines += [f'def result : Bool := {expr}','theorem rejected : result = false := by decide +kernel','end '+ns]
    records.append({'name':label,'namespace':ns,'expression':'result','expected':'false'})
    (root/'examples'/('corrupted_'+label+'.json')).write_bytes(canonical(bad))
lines += ['namespace RejectZeroDenominator',
          'def result : Bool := checkWireMatrix (Matrix.of ![![(0,0)]] : WireMatrix 1 1)',
          'theorem rejected : result = false := by decide +kernel','end RejectZeroDenominator',
          'namespace RejectHiddenObstruction',
          'def result : Bool := checkOptimalConstruction (0 : Mat 1 0) (1 : Mat 1 1) (0 : Mat 0 1) (0 : Mat 1 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 1 0)',
          'theorem rejected : result = false := by decide +kernel','end RejectHiddenObstruction']
for label in ['ZeroDenominator','HiddenObstruction']:records.append({'name':label,'namespace':'Reject'+label,'expression':'result','expected':'false'})
(root/'lean/KomorebiRepair/RejectedCertificates.lean').write_text('\n'.join(lines)+'\n', encoding="utf-8")
for rec in records:
    ns=rec['namespace'];text=f'import KomorebiRepair.RejectedCertificates\ntheorem counterfeit : {ns}.result = true := by\n  exact {ns}.rejected\n'
    (root/'lean/certificate_negative_controls'/(rec['name']+'.lean')).write_text(text, encoding="utf-8")
(root/'evidence/rejection_index.json').write_text(json.dumps(records,indent=2), encoding="utf-8")
