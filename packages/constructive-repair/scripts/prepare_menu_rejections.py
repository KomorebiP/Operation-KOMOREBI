from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
# Each check is first proved false in a positive source module. A separate
# invalid source attempts to use that fact as true; diagnostic must be specific.
probes=[
 ('MissingCheaperCover','checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W (MenuCase000.blocks.take 1)'),
 ('ZeroSeparator','checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W [({0}, (0 : Mat 1 3)), ({1}, MenuCase000.Y1)]'),
 ('OverstatedBlock','checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U MenuCase000.W [({0, 1}, MenuCase000.Y0)]'),
 ('WrongCoefficients','checkCoveredOptimal MenuCase000.original MenuCase000.chosen MenuCase000.U (-MenuCase000.W) MenuCase000.blocks'),
 ('ExpensiveSingleton','checkCoveredOptimal MenuCase002.original {0} (0 : Mat 1 1) (!![-1; 0; 0] : Mat 3 1) MenuCase002.blocks'),
 ('ForbiddenSelection','checkCoveredOptimal MenuCase001.original {0, 1} MenuCase000.U MenuCase000.W MenuCase000.blocks'),
 ('BogusNoRepair','checkCoveredNoRepair MenuCase000.original MenuCase000.blocks'),
 ('UnselectedColumnUsed','checkCoveredOptimal MenuCase000.original {0} MenuCase000.U MenuCase000.W MenuCase000.blocks'),
]
lines=['import KomorebiRepair.MenuGenerated.Certificates00','set_option autoImplicit false','set_option maxRecDepth 100000',
       'open KomorebiRepair.RationalCertificates','namespace KomorebiRepair.MenuRejections']
ctl=ROOT/'lean/menu_negative_controls';ctl.mkdir(exist_ok=True);idx=[]
for name,expr in probes:
    lines += [f'def {name} : Bool := {expr}',f'theorem {name}_rejected : {name} = false := by decide +kernel']
    (ctl/(name+'.lean')).write_text('import KomorebiRepair.MenuRejected\nopen KomorebiRepair.MenuRejections\n'+
        f'example : {name} = true := {name}_rejected\n', encoding="utf-8")
    idx.append({'name':name,'positive_theorem':'KomorebiRepair.MenuRejections.'+name+'_rejected',
                'file':'lean/menu_negative_controls/'+name+'.lean','expected_diagnostic':'false-to-true Type mismatch'})
lines+=['end KomorebiRepair.MenuRejections']
(ROOT/'lean/KomorebiRepair/MenuRejected.lean').write_text('\n'.join(lines)+'\n', encoding="utf-8")
(ROOT/'evidence/menu_rejection_index.json').write_text(json.dumps(idx,indent=2)+'\n', encoding="utf-8")
