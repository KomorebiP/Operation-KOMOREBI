"""Exercise the delivered runtime and CLI, with source/checkpoint provenance. Komorebi P."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from machinery import Store
from machinery.operations import base_registry
from demo import demo
from test_machinery import MachineryTests

ROOT = Path(__file__).resolve().parent


def main():
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MachineryTests))
    if not tests.wasSuccessful(): print(stream.getvalue());raise SystemExit(1)
    source = ROOT/'previous/Komorebi_JSpace_Learned_Primitives_v0_5.zip'
    prefix = 'Komorebi_JSpace_Learned_Primitives_v0_5/'
    with zipfile.ZipFile(source) as z:
        for target,member in [('machinery/legacy_kernels.py','primitive_model.py'),
                              ('models/learned_square_0.npz','results/models/trained_square_0.npz'),
                              ('models/catalog_square_0.json','results/catalog_square_0.json')]:
            assert (ROOT/target).read_bytes()==z.read(prefix+member)
    commands = 0
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary); demo_result = demo(temp/'demo')
        bank = temp/'cli.json'
        def call(*args,ok=True):
            nonlocal commands
            r = subprocess.run([sys.executable,str(ROOT/'cli.py'),'--bank',str(bank),*args],capture_output=True,text=True)
            assert (r.returncode==0)==ok, (args,r.stdout,r.stderr)
            commands += 1; return json.loads(r.stdout)
        call('init'); original = call('run','grid')['outputs']; call('fork','grid','trial')
        before = bank.read_bytes(); p = call('preview','trial','--patch',str(ROOT/'examples/turns_2.json'))
        assert p['status']=='ready' and bank.read_bytes()==before
        edit = call('edit','trial','--patch',str(ROOT/'examples/turns_2.json'))
        assert edit['changed_outputs']['result']['changed_cells']==2
        patch = call('inspect','trial','root/copy/turned')['value']; assert patch['data']==[[2,2],[0,2]]
        graph = call('graph','trial'); assert set(graph['potential_dependencies']['chosen'])=={'enabled','copy','scene'}
        call('trace','trial','--output',str(temp/'trace.json'))
        assert json.loads((temp/'trace.json').read_text())['status']=='ok'
        before = bank.read_bytes(); call('edit','trial','--patch',str(ROOT/'examples/invalid_type.json'),ok=False)
        assert bank.read_bytes()==before
        call('undo','trial'); assert call('run','trial')['outputs']==original
        call('checkout','trial',edit['revision']);call('define','--file',str(ROOT/'examples/double_function.json'))
        assert 'double' in call('registry')
        call('create','second_grid','--program',str(ROOT/'examples/grid_program.json'),'--inputs',str(ROOT/'examples/grid_inputs.json'))
        assert call('run','second_grid')['outputs']==original
        new_program = json.loads((ROOT/'examples/scalar_program.json').read_text()); new_program['nodes'][0]['args']={'a':'a','b':'a'}
        program_file = temp/'program.json';program_file.write_text(json.dumps(new_program))
        call('program','scalar','--file',str(program_file)); assert abs(call('run','scalar')['outputs']['product']['data']-9)<1e-9
        assert call('compare','grid','trial')['outputs']['result']['changed_cells']==2
        call('history','trial'); call('list'); call('init',ok=False)
        empty_bank = temp/'empty.json'
        subprocess.run([sys.executable,str(ROOT/'cli.py'),'--bank',str(empty_bank),'empty'],check=True,capture_output=True)
        assert not Store.load(empty_bank,base_registry()).branches
        commands += 1
    prepared = Store.load(ROOT/'examples/recorded_run/workspace_bank.json',base_registry())
    report = {'author':'Komorebi P.','status':'passed','behavioral_tests':tests.testsRun,'test_failures':0,
              'live_cli_commands':commands,'frozen_v05_kernel_files_identical':3,
              'recorded_workspaces_replayed':len(prepared.branches),'recorded_revisions_replayed':len(prepared.revisions),
              'demonstration':demo_result,'training_performed':False,'powershell_executed':False,
              'prior_release_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    (ROOT/'results/verification.json').write_text(json.dumps(report,indent=2))
    (ROOT/'results/tests.txt').write_text(stream.getvalue())
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
