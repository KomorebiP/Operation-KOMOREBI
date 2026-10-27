"""Verify collection/action contracts and runnable delivery. Komorebi P."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from machinery import Store,Value,Fault
from machinery.operations import base_registry
from machinery.values import equivalent
from collection_scenarios import make_bank
from demo import demo
from test_machinery import MachineryTests
from test_collections import CollectionTests

ROOT=Path(__file__).resolve().parent


def main():
    output=io.StringIO();suite=unittest.TestSuite()
    for cls in [MachineryTests,CollectionTests]:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    if not result.wasSuccessful():print(output.getvalue());raise SystemExit(1)
    previous=ROOT/'previous/Komorebi_JSpace_Machinery_v0_6.zip'
    prefix='Komorebi_JSpace_Machinery_v0_6/'
    with zipfile.ZipFile(previous) as z:
        for name in ['machinery/legacy_kernels.py','models/learned_square_0.npz','models/catalog_square_0.json']:
            assert (ROOT/name).read_bytes()==z.read(prefix+name)
        old_grid=json.loads(z.read(prefix+'examples/recorded_run/original_run.json'))['outputs']
        old_scalar=json.loads(z.read(prefix+'examples/recorded_run/scalar_run.json'))['outputs']
        old_bank=z.read(prefix+'examples/recorded_run/workspace_bank.json')
    fresh=make_bank();legacy_outputs=0
    for name,expected in [('grid',old_grid),('scalar',old_scalar)]:
        actual=fresh.run(name)['outputs'];assert set(actual)==set(expected)
        for key in actual:
            assert equivalent(Value.unpack(actual[key]),Value.unpack(expected[key]));legacy_outputs+=1
    commands=0
    with tempfile.TemporaryDirectory() as temp:
        temp=Path(temp);summary=demo(temp/'demo');bank=temp/'bank.json'
        def call(script,*args,ok=True):
            nonlocal commands
            run=subprocess.run([sys.executable,str(ROOT/script),'--bank',str(bank),*args],capture_output=True,text=True)
            assert (run.returncode==0)==ok,(script,args,run.stdout,run.stderr)
            commands+=1;return json.loads(run.stdout)
        call('cli.py','init');initial=call('cli.py','run','objects')['outputs']
        call('control.py','--request',str(ROOT/'examples/observe_objects.json'),'--response',str(temp/'observation.json'))
        assert json.loads((temp/'observation.json').read_text())['status']=='observed'
        before=bank.read_bytes()
        proposed=call('control.py','--request',str(ROOT/'examples/move_proposal.json'),'--response',str(temp/'proposal.json'))
        assert proposed['status']=='ready' and bank.read_bytes()==before
        bad=call('control.py','--request',str(ROOT/'examples/collision_proposal.json'),ok=False)
        assert bad['error']['code']=='collision' and bank.read_bytes()==before
        bad=call('control.py','--request',str(ROOT/'examples/wrong_target_proposal.json'),'--response',str(temp/'wrong.json'),ok=False)
        assert bad['reason']=='target_mismatch' and bank.read_bytes()==before
        call('control.py','--commit',str(temp/'wrong.json'),ok=False)
        committed=call('control.py','--commit',str(temp/'proposal.json'),'--response',str(temp/'commit.json'))
        assert committed['status']=='committed' and committed['bank_updated']
        current=bank.read_bytes();bad=call('control.py','--commit',str(temp/'proposal.json'),ok=False)
        assert bad['error']['code']=='conflict' and bank.read_bytes()==current
        tampered=json.loads((temp/'proposal.json').read_text());tampered['receipt']['payload']['candidate']['inputs']['offset']['data']=[0,3]
        (temp/'tampered.json').write_text(json.dumps(tampered))
        bad=call('control.py','--commit',str(temp/'tampered.json'),ok=False)
        assert bad['error']['code']=='integrity' and bank.read_bytes()==current
        value=call('cli.py','inspect','objects','root/shifted')['value'];assert value['kind']=='list[object]' and len(value['data'])==2
        def action(obj):
            path=temp/'request.json';path.write_text(json.dumps(obj))
            return call('control.py','--request',str(path))
        action({'action':'fork','workspace':'objects','name':'trial','expected_revision':committed['revision']})
        assert not action({'action':'compare','a':'objects','b':'trial'})['changes']['outputs']
        action({'action':'undo','workspace':'trial','expected_revision':committed['revision']})
        assert call('cli.py','run','trial')['outputs']==initial
        call('control.py','--request',str(ROOT/'examples/scalar_graph_proposal.json'),'--response',str(temp/'scalar.json'))
        call('control.py','--commit',str(temp/'scalar.json'))
        assert abs(call('cli.py','run','scalar')['outputs']['product']['data']-9)<1e-9
        call('cli.py','preview','grid','--patch',str(ROOT/'examples/turns_2.json'))
        call('cli.py','create','copied','--program',str(ROOT/'examples/grid_program.json'),'--inputs',str(ROOT/'examples/grid_inputs.json'))
        assert call('cli.py','run','copied')['outputs']==old_grid
        call('cli.py','trace','objects','--output',str(temp/'trace.json'))
        assert any(row['event']=='fold' for row in json.loads((temp/'trace.json').read_text())['trace'])
        call('cli.py','graph','objects');call('cli.py','history','objects');call('cli.py','list')
        (temp/'old.json').write_bytes(old_bank)
        try:Store.load(temp/'old.json',base_registry())
        except Fault as error:assert error.code=='schema'
        else:raise AssertionError('A v0.6 bank was silently treated as a v0.7 bank.')
    saved=Store.load(ROOT/'examples/recorded_run/workspace_bank.json',base_registry())
    receipt={'author':'Komorebi P.','status':'passed','behavioral_tests':result.testsRun,'test_failures':0,
             'live_cli_commands':commands,'legacy_v06_outputs_preserved':legacy_outputs,'frozen_v05_kernel_files_identical':3,
             'recorded_revisions_replayed':len(saved.revisions),'recorded_workspaces':len(saved.branches),
             'demonstration':summary,'training_performed':False,'powershell_executed':False,
             'previous_release_sha256':hashlib.sha256(previous.read_bytes()).hexdigest()}
    (ROOT/'results/verification.json').write_text(json.dumps(receipt,indent=2))
    (ROOT/'results/tests.txt').write_text(output.getvalue());print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
