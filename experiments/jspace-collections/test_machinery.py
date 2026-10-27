"""Behavioral checks for workspace machinery. Author: Komorebi P."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from machinery import Value, Fault, Program, Runner, Store
from machinery.operations import base_registry
from scenarios import registry, grid_case, scalar_case, make_bank, node


class MachineryTests(unittest.TestCase):
    def setUp(self): self.registry = registry()

    def test_types_keep_colors_counts_flags_and_scalars_distinct(self):
        for kind,data in [('scalar',True),('index',2.0),('flag',1),('color',10),('mask',[[0,1]]),('grid',[[1.,2.]]),('scalar',float('nan'))]:
            with self.subTest(kind=kind,data=data), self.assertRaises(Fault): Value(kind,data)
        program = {'nodes':[node('bad','number.add',a='count',b='a')],'outputs':{'result':'bad'}}
        self.assertEqual(Runner(self.registry).run(program,{'count':Value('index',2),'a':Value('scalar',1)})['error']['code'],'type')

    def test_explicit_operand_binding_preserves_subtraction_order(self):
        program = {'nodes':[node('forward','learned.channel_17',a='x',b='y'),node('reverse','learned.channel_17',a='y',b='x')],
                   'outputs':{'a':'forward','b':'reverse'}}
        out = Runner(self.registry).run(program,{'x':Value('scalar',7),'y':Value('scalar',2)})['outputs']
        self.assertAlmostEqual(out['a']['data'],5); self.assertAlmostEqual(out['b']['data'],-5)

    def test_crop_transform_place_retains_original_scene(self):
        program,inputs,expected = grid_case(); before = inputs['scene'].data.copy()
        run = Runner(self.registry).run(program,inputs)
        self.assertEqual(run['status'],'ok')
        np.testing.assert_array_equal(run['outputs']['result']['data'],expected)
        np.testing.assert_array_equal(run['outputs']['original']['data'],before)
        np.testing.assert_array_equal(inputs['scene'].data,before)
        self.assertIn('root/copy/destination',run['values'])
        self.assertEqual(run['outputs']['changed_cells']['data'],4)

    def test_reusable_function_rebinds_colors_and_scene(self):
        program,inputs,expected = grid_case()
        scene = inputs['scene'].data.copy(); scene[scene==2] = 4; scene[scene==3] = 6
        expected[expected==2] = 4
        inputs.update(scene=Value('grid',scene),source_color=Value('color',4),target_color=Value('color',6))
        out = Runner(self.registry).run(program,inputs)
        np.testing.assert_array_equal(out['outputs']['result']['data'],expected)

    def test_lazy_choice_skips_unsafe_branch(self):
        program,inputs,_ = grid_case(); inputs['source_color'] = Value('color',9); inputs['enabled'] = Value('flag',False)
        run = Runner(self.registry).run(program,inputs)
        self.assertEqual(run['status'],'ok'); self.assertEqual(run['outputs']['changed_cells']['data'],0)
        self.assertFalse(any(row.get('operation')=='copy_pattern' for row in run['trace']))
        inputs['enabled'] = Value('flag',True)
        self.assertEqual(Runner(self.registry).run(program,inputs)['error']['code'],'empty_selection')

    def test_scalar_maximum_and_bounded_learned_iteration(self):
        program,inputs = scalar_case(); run = Runner(self.registry).run(program,inputs)
        self.assertEqual(run['outputs']['maximum']['data'],2)
        self.assertAlmostEqual(run['outputs']['accumulated']['data'],2)
        self.assertEqual(len([r for r in run['trace'] if r.get('operation')=='advance']),4)
        inputs['count'] = Value('index',65)
        self.assertEqual(Runner(self.registry).run(program,inputs)['error']['code'],'budget')

    def test_zero_iterations_do_not_evaluate_unused_binding(self):
        program = {'nodes':[node('unsafe','number.divide',a='start',b='zero'),
                            {'id':'repeat','repeat':{'op':'advance','state':'start','count':'count','bindings':{'delta':'unsafe'}}}],
                   'outputs':{'result':'repeat'}}
        run = Runner(self.registry).run(program,{'start':Value('scalar',7),'zero':Value('scalar',0),'count':Value('index',0)})
        self.assertEqual(run['outputs']['result']['data'],7)

    def test_global_execution_budget_bounds_function_calls(self):
        program,inputs = scalar_case(); result = Runner(self.registry,max_steps=3).run(program,inputs)
        self.assertEqual(result['error']['code'],'budget')

    def test_cycles_and_missing_bindings_are_rejected(self):
        cyclic = {'nodes':[node('x','number.add',a='y',b='seed'),node('y','number.add',a='x',b='seed')],'outputs':{'result':'x'}}
        self.assertEqual(Runner(self.registry).run(cyclic,{'seed':Value('scalar',0)})['error']['code'],'cycle')
        cyclic['nodes'][0]['args']['a'] = 'missing'
        self.assertEqual(Runner(self.registry).run(cyclic,{'seed':Value('scalar',0)})['error']['code'],'binding')

    def test_masked_copy_checks_alignment_and_only_writes_mask(self):
        program = {'nodes':[node('out','grid.masked_copy',destination='a',source='b',mask='m')],'outputs':{'result':'out'}}
        inputs = {'a':Value('grid',[[1,1],[1,1]]),'b':Value('grid',[[2,3],[4,5]]),'m':Value('mask',[[True,False],[False,True]])}
        run = Runner(self.registry).run(program,inputs)
        self.assertEqual(run['outputs']['result']['data'],[[2,1],[1,5]])
        inputs['m'] = Value('mask',[[True]])
        self.assertEqual(Runner(self.registry).run(program,inputs)['error']['code'],'shape')

    def test_failed_edit_is_atomic(self):
        bank = make_bank(); before = bank.pack()
        scene = np.array(bank.snapshot('grid')['inputs']['scene']['data']); scene[3,6] = 0; scene[6,9] = 3
        edit = bank.edit('grid',{'scene':Value('grid',scene)})
        self.assertEqual(edit['status'],'rejected'); self.assertEqual(edit['run']['error']['code'],'bounds')
        self.assertEqual(bank.pack(),before)

    def test_preview_fork_undo_and_checkout_preserve_siblings(self):
        bank = make_bank(); bank.fork('grid','trial'); before = bank.pack()
        preview = bank.preview('trial',{'turns':Value('index',2)})
        self.assertEqual(preview['status'],'ready'); self.assertEqual(bank.pack(),before)
        edit = bank.edit('trial',{'turns':Value('index',2)})
        self.assertEqual(edit['changes']['outputs']['result']['changed_cells'],2)
        edited = bank.run('trial')['outputs']; bank.undo('trial')
        self.assertEqual(bank.run('trial')['outputs'],bank.run('grid')['outputs'])
        bank.checkout('trial',edit['revision']); self.assertEqual(bank.run('trial')['outputs'],edited)
        self.assertEqual(bank.branches['grid'],before['branches']['grid'])

    def test_editing_program_changes_named_dependencies(self):
        bank = make_bank(); program = bank.snapshot('scalar')['program']
        program['nodes'][0]['args'] = {'a':'a','b':'a'}
        edit = bank.edit('scalar',program=program)
        self.assertAlmostEqual(edit['run']['outputs']['product']['data'],9)
        self.assertNotIn('maximum',edit['changes']['outputs'])

    def test_cache_reuses_only_unchanged_arguments(self):
        bank = make_bank(); bank.run('grid')
        preview = bank.preview('grid',{'turns':Value('index',2)})
        calls = {row['operation']:row for row in preview['run']['trace'] if row['event']=='call'}
        self.assertTrue(calls['grid.crop']['cached']); self.assertFalse(calls['grid.rotate']['cached'])
        self.assertFalse(calls['grid.paste']['cached'])

    def test_stale_revision_and_changed_registry_are_rejected(self):
        bank = make_bank()
        with self.assertRaises(Fault): bank.edit('grid',expected_revision='r999999')
        bank.registry.get('number.add').identity = 'changed'
        with self.assertRaises(Fault): bank.run('grid')

    def test_save_reload_replays_history_and_retains_branches(self):
        bank = make_bank(); bank.fork('grid','trial'); bank.edit('trial',{'turns':Value('index',2)})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bank.json'; bank.save(path); other = Store.load(path,base_registry())
            self.assertEqual(bank.pack(),other.pack())
            self.assertEqual(bank.run('trial')['outputs'],other.run('trial')['outputs'])
            other.undo('trial'); other.save(path)
            with self.assertRaises(Fault): bank.save(path)

    def test_tampered_snapshot_and_changed_operation_cannot_load(self):
        bank = make_bank()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bank.json'; bank.save(path); raw = path.read_bytes()
            obj = json.loads(raw); obj['revisions']['r000000']['snapshot']['inputs']['turns']['data'] = 3
            path.write_text(json.dumps(obj))
            with self.assertRaises(Fault): Store.load(path,base_registry())
            path.write_bytes(raw); changed = base_registry(); changed.get('grid.rotate').identity = 'changed'
            with self.assertRaises(Fault): Store.load(path,changed)

    def test_existing_destination_and_active_writer_lock_are_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bank.json'; original = make_bank(); original.save(path)
            with self.assertRaises(Fault): make_bank().save(path)
            lock = path.with_name(path.name+'.lock'); lock.write_text('test lock')
            with self.assertRaises(Fault): original.save(path)
            self.assertTrue(lock.exists())

    def test_registry_definition_and_pack_do_not_alias(self):
        bank = make_bank(); before = bank.registry_identity; packed = bank.pack()
        packed['functions'][0]['body']['nodes'].clear()
        self.assertEqual(bank.pack()['registry_identity'],before)

    def test_unknown_and_recursive_function_references_are_rejected(self):
        with self.assertRaises(Fault):
            self.registry.define('self_call',{'state':'scalar'},{'nodes':[node('x','self_call',state='state')],'outputs':{'result':'x'}})
        self.assertNotIn('self_call',self.registry.operations)

    def test_library_extension_preserves_history_and_cannot_redefine(self):
        bank = make_bank(); before = bank.run('scalar')['outputs']; revisions = copy.deepcopy(bank.revisions)
        body = {'nodes':[node('twice','number.add',a='state',b='state')],'outputs':{'result':'twice'}}
        bank.define_function('double',{'state':'scalar'},body)
        self.assertEqual(bank.revisions,revisions); self.assertEqual(bank.run('scalar')['outputs'],before)
        with self.assertRaises(Fault): bank.define_function('double',{'state':'scalar'},body)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'extended.json'; bank.save(path)
            loaded = Store.load(path,base_registry()); self.assertIn('double',loaded.registry.operations)


if __name__=='__main__': unittest.main()
