from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
expressions={
 'FalseRootBound':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W .bound',
 'AllDeclaredInadmissible':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W .inadmissible',
 'ZeroDetector':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.separator (0 : Mat 1 3))',
 'RepeatedSplit':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.split 0 BranchCase000.tree BranchCase000.tree)',
 'DuplicatedBoundChild':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (.split 0 .bound .bound)',
 'SwappedBranches':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U BranchCase000.W (swapRoot BranchCase000.tree)',
 'WrongCoefficients':'checkTreeOptimal BranchCase000.original BranchCase000.chosen BranchCase000.U (-BranchCase000.W) BranchCase000.tree',
 'UnselectedDirection':'checkTreeOptimal BranchCase000.original {0} BranchCase000.U BranchCase000.W BranchCase000.tree',
 'ForbiddenSelection':'checkTreeOptimal BranchCase001.original {0,1} BranchCase000.U BranchCase000.W BranchCase000.tree',
 'FalseNoRepair':'checkTreeNoRepair BranchCase000.original BranchCase000.tree',
}
lines=['import KomorebiRepair.BranchGenerated.Certificates00','set_option autoImplicit false','set_option maxRecDepth 100000',
 'open KomorebiRepair.RationalCertificates','namespace KomorebiRepair.BranchRejections',
 'def swapRoot {m q : ℕ} : BranchTree m q → BranchTree m q',
 '  | .split j x y => .split j y x','  | t => t']
idx=[];out=R/'lean/branch_negative_controls';out.mkdir(exist_ok=True)
for name,expr in expressions.items():
 lines += [f'def {name} : Bool := {expr}',f'theorem {name}_rejected : {name} = false := by decide +kernel']
 (out/(name+'.lean')).write_text('import KomorebiRepair.BranchRejected\nopen KomorebiRepair.BranchRejections\n'+
    f'example : {name} = true := {name}_rejected\n', encoding="utf-8")
 idx.append({'name':name,'expected':'Type mismatch; = false versus = true','positive_theorem':'KomorebiRepair.BranchRejections.'+name+'_rejected'})
lines+=['end KomorebiRepair.BranchRejections']
(R/'lean/KomorebiRepair/BranchRejected.lean').write_text('\n'.join(lines)+'\n', encoding="utf-8")
(R/'evidence/branch_rejection_index.json').write_text(json.dumps(idx,indent=2)+'\n', encoding="utf-8")
