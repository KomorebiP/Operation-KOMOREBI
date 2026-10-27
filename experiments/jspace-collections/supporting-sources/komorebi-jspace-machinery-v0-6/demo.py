"""Run and save an inspectable machinery demonstration. Komorebi P."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from machinery import Value, Store
from machinery.operations import base_registry
from scenarios import make_bank,grid_case,scalar_case

ROOT = Path(__file__).resolve().parent


def write(path,obj): path.write_text(json.dumps(obj,indent=2,allow_nan=False))


def demo(folder):
    folder = Path(folder); folder.mkdir(parents=True,exist_ok=False)
    bank = make_bank(); original = bank.run('grid')
    expected = grid_case()[2]; np.testing.assert_array_equal(original['outputs']['result']['data'],expected)
    bank.fork('grid','rotation_trial')
    preview = bank.preview('rotation_trial',{'turns':Value('index',2)})
    committed = bank.edit('rotation_trial',{'turns':Value('index',2)})
    difference = bank.compare('grid','rotation_trial')
    assert difference['outputs']['result']['changed_cells']==2
    scene = np.array(bank.snapshot('grid')['inputs']['scene']['data']); scene[3,6]=0;scene[6,9]=3
    before = bank.pack(); rejected = bank.edit('grid',{'scene':Value('grid',scene)})
    assert rejected['status']=='rejected' and bank.pack()==before
    bank.fork('grid','disabled_copy'); bank.edit('disabled_copy',{'enabled':Value('flag',False),'source_color':Value('color',9)})
    disabled = bank.run('disabled_copy'); assert disabled['outputs']['changed_cells']['data']==0
    edited = bank.run('rotation_trial')['outputs']; bank.undo('rotation_trial')
    assert bank.run('rotation_trial')['outputs']==original['outputs']
    bank.checkout('rotation_trial',committed['revision']); assert bank.run('rotation_trial')['outputs']==edited
    path = folder/'workspace_bank.json'; bank.save(path)
    reloaded = Store.load(path,base_registry()); assert reloaded.pack()==bank.pack()
    for label,obj in [('original_run',original),('preview',preview),('edit',committed),('difference',difference),('rejected_write',rejected),('disabled_run',disabled),('scalar_run',bank.run('scalar'))]:
        write(folder/(label+'.json'),obj)
    report = {'author':'Komorebi P.','release':'v0.6 machinery','status':'passed','training_performed':False,
              'registered_operations':len(bank.registry.operations),'reusable_functions':len(bank.registry.definitions()),
              'workspaces':list(bank.branches),'persisted_revisions':len(bank.revisions),
              'initial_grid_changed_cells':4,'rotation_edit_changed_cells':2,
              'failed_bounds_edit_preserved_bank':True,'disabled_branch_skipped_empty_selection':True,
              'undo_and_checkout_reproduced_outputs':True,'disk_reload_replayed_all_revisions':True,
              'edit_cache_hits':preview['run']['cache_hits'],'edit_native_executions':preview['run']['native_executions'],
              'trace_events':len(original['trace']),'scalar_outputs':bank.run('scalar')['outputs']}
    write(folder/'SUMMARY.json',report); return report


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'runs'/('demo_'+str(time.time_ns())))
    args = p.parse_args();print(json.dumps({'folder':str(args.output),**demo(args.output)},indent=2))
