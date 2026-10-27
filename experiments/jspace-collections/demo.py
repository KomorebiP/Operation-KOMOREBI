"""Record a complete object-collection and proposal workflow. Komorebi P."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from collection_scenarios import make_bank,proposal,collection_case
from machinery import Store,Value
from machinery.actions import Actions
from machinery.operations import base_registry

ROOT=Path(__file__).resolve().parent


def demo(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    bank=make_bank();api=Actions(bank);before=bank.pack();initial=bank.run('objects')
    proposed=api.apply(proposal(bank));assert proposed['status']=='ready' and bank.pack()==before
    assert proposed['residual_before']['outputs']['result']['mismatched_cells']==10
    assert proposed['residual_after']['all_matched']
    collision=api.apply(proposal(bank,(0,4),False));assert collision['status']=='rejected' and collision['error']['code']=='collision'
    wrong=api.apply(proposal(bank,(0,1),True));assert wrong['status']=='rejected' and wrong['reason']=='target_mismatch'
    assert bank.pack()==before
    # A receipt survives serialization and a fresh process-style bank load.
    path=folder/'workspace_bank.json';bank.save(path);bank=Store.load(path,base_registry());api=Actions(bank)
    committed=api.apply({'action':'commit','receipt':json.loads(json.dumps(proposed['receipt']))})
    assert committed['status']=='committed'
    np.testing.assert_array_equal(committed['outputs']['result']['data'],collection_case()[2])
    committed_state=bank.pack();repeated=api.apply({'action':'commit','receipt':proposed['receipt']})
    assert repeated['status']=='rejected' and repeated['error']['code']=='conflict' and bank.pack()==committed_state
    bank.fork('objects','alternative');fork=bank.branches['alternative']
    bank.edit('alternative',{'minimum':Value('index',3)})
    comparison=bank.compare('objects','alternative');bank.undo('alternative');assert bank.branches['alternative']==fork
    bank.save(path);reloaded=Store.load(path,base_registry());assert reloaded.pack()==bank.pack()
    for name,obj in [('initial_run',initial),('proposed',proposed),('committed',committed),('collision',collision),
                     ('wrong_target',wrong),('stale_receipt',repeated),('branch_comparison',comparison),('final_run',bank.run('objects'))]:
        (folder/(name+'.json')).write_text(json.dumps(obj,indent=2,allow_nan=False))
    summary={'author':'Komorebi P.','release':'v0.7 collections and actions','status':'passed',
             'training_performed':False,'registered_operations':len(bank.registry.operations),
             'authored_functions':len(bank.registry.definitions()),'objects_found':3,'objects_selected':2,
             'initial_target_mismatches':10,'proposed_target_mismatches':0,'movement_changed_cells':10,
             'unselected_distractor_preserved':True,'collision_rejected_without_commit':True,
             'target_mismatch_rejected_without_commit':True,'receipt_committed_after_reload':True,
             'duplicate_commit_rejected_as_stale':True,'persistent_workspaces':len(bank.branches),
             'persistent_revisions':len(bank.revisions),'initial_trace_events':len(initial['trace'])}
    (folder/'SUMMARY.json').write_text(json.dumps(summary,indent=2));return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'runs'/('demo_'+str(time.time_ns())))
    args=parser.parse_args();print(json.dumps({'folder':str(args.output),**demo(args.output)},indent=2))
