"""Collection execution, proposal, residual and persistence checks. Komorebi P."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from machinery import Value,Fault,Store,Runner
from machinery.values import equivalent,digest
from machinery.objects import components,translate,erase
from machinery.operations import base_registry
from machinery.actions import Actions,residual
from collection_scenarios import registry,collection_case,make_bank,proposal
from scenarios import node


class CollectionTests(unittest.TestCase):
    def test_collections_are_typed_bounded_and_roundtrip(self):
        for kind in ['list[index]','list[grid]','list[object]']:
            value=Value(kind,[]);self.assertEqual(Value.unpack(value.pack()).pack(),value.pack())
        with self.assertRaises(Fault):Value('list[index]',[Value('scalar',1)])
        with self.assertRaises(Fault):Value('list[index]',[Value('index',1)]*65)
        with self.assertRaises(Fault):Value('list[list[index]]',[])

    def test_component_connectivity_color_and_order(self):
        scene=Value('grid',[[2,0,4],[0,2,4]])
        four=components(scene,Value('color',0),Value('index',4))
        eight=components(scene,Value('color',0),Value('index',8))
        self.assertEqual([len(x.data.pixels) for x in four.data],[1,2,1])
        self.assertEqual([len(x.data.pixels) for x in eight.data],[2,2])
        self.assertEqual(four.pack(),components(scene,Value('color',0),Value('index',4)).pack())
        all_pixels=[p for obj in four.data for p in obj.data.pixels]
        self.assertEqual(sorted(all_pixels),[(0,0,2),(0,2,4),(1,1,2),(1,2,4)])

    def test_object_translation_preserves_source_lineage_and_checks_bounds(self):
        scene=Value('grid',[[2,0,0],[0,0,0]])
        item=components(scene,Value('color',0),Value('index',4)).data[0]
        moved=translate(item,Value('point',[1,2]))
        self.assertEqual(moved.data.pixels,((1,2,2),));self.assertEqual(moved.data.origin_id,item.data.origin_id)
        self.assertEqual(moved.data.source,scene.identity());self.assertNotEqual(moved.identity(),item.identity())
        with self.assertRaises(Fault):translate(item,Value('point',[-1,0]))
        malformed=item.pack();malformed['data']['pixels'].append([0,0,2])
        with self.assertRaises(Fault):Value.unpack(malformed)

    def test_stale_erase_rejects_changed_selected_pixels(self):
        item=components(Value('grid',[[2,0]]),Value('color',0),Value('index',4)).data[0]
        with self.assertRaises(Fault):erase(Value('grid',[[3,0]]),item,Value('color',0))

    def test_object_collection_limit_is_enforced(self):
        scene=np.zeros((17,17),int);scene[::2,::2]=2
        with self.assertRaises(Fault) as caught:components(Value('grid',scene),Value('color',0),Value('index',4))
        self.assertEqual(caught.exception.code,'budget')

    def test_map_filter_fold_move_objects_without_flattening_context(self):
        program,inputs,expected=collection_case();inputs['offset']=Value('point',[0,2])
        run=Runner(registry()).run(program,inputs)
        self.assertEqual(run['status'],'ok');np.testing.assert_array_equal(run['outputs']['result']['data'],expected)
        self.assertEqual(run['outputs']['areas']['data'],[Value('index',3).pack(),Value('index',1).pack(),Value('index',2).pack()])
        self.assertEqual(run['outputs']['selected_count']['data'],2)
        self.assertEqual(run['outputs']['changed_cells']['data'],10)
        self.assertTrue(any(row['event']=='filter' and row['decisions']==[True,False,True] for row in run['trace']))
        self.assertIn('root/shifted/item_1',run['values'])

    def test_empty_map_filter_fold_do_not_evaluate_unused_bindings(self):
        program,inputs,_=collection_case();inputs['minimum']=Value('index',100);inputs['offset']=Value('point',[999,999])
        run=Runner(registry()).run(program,inputs)
        self.assertEqual(run['status'],'ok');self.assertEqual(run['outputs']['changed_cells']['data'],0)
        self.assertFalse(any(row.get('operation') in ['object.translate','object.erase','object.paint'] for row in run['trace']))

    def test_collection_signature_and_nested_map_are_rejected(self):
        program,inputs,_=collection_case();program['nodes'][1]['map']['items']='minimum'
        self.assertEqual(Runner(registry()).run(program,inputs)['error']['code'],'type')
        r=registry();r.native('list_return',{'item':'object'},'list[object]',lambda item:Value('list[object]',[item]),'test-only')
        # A map calling a primitive with the wrong item role cannot execute.
        bad={'nodes':[{'id':'bad','map':{'op':'index.add','items':'items','bindings':{'b':'minimum'}}}],'outputs':{'result':'bad'}}
        self.assertEqual(Runner(r).run(bad,{'items':Value('list[index]',[]),'minimum':Value('index',1)})['error']['code'],'type')
        nested={'nodes':[{'id':'nested','map':{'op':'list_return','items':'items','bindings':{}}}],'outputs':{'result':'nested'}}
        self.assertEqual(Runner(r).run(nested,{'items':Value('list[object]',[])})['error']['code'],'type')

    def test_collision_after_partial_fold_leaves_whole_bank_unchanged(self):
        bank=make_bank();scene=np.array(bank.snapshot('objects')['inputs']['scene']['data'])
        scene[1,5]=0;scene[4,8]=8
        self.assertEqual(bank.edit('objects',{'scene':Value('grid',scene)})['status'],'committed')
        before=bank.pack();result=bank.edit('objects',{'offset':Value('point',[0,4])})
        self.assertEqual(result['status'],'rejected');self.assertEqual(result['run']['error']['code'],'collision')
        self.assertTrue(any(r.get('operation')=='object.paint' for r in result['run']['trace']))
        self.assertEqual(bank.pack(),before)

    def test_collection_steps_share_execution_budget(self):
        program,inputs,_=collection_case()
        result=Runner(registry(),max_steps=8).run(program,inputs)
        self.assertEqual(result['error']['code'],'budget')

    def test_action_observation_proposal_residual_and_commit(self):
        bank=make_bank();api=Actions(bank);before=bank.pack()
        observe=api.apply({'action':'observe','workspace':'objects'})
        self.assertEqual(observe['status'],'observed');self.assertEqual(observe['revision'],bank.branches['objects'])
        proposed=api.apply(proposal(bank));self.assertEqual(proposed['status'],'ready');self.assertEqual(bank.pack(),before)
        self.assertEqual(proposed['residual_before']['outputs']['result']['mismatched_cells'],10)
        self.assertEqual(proposed['residual_after']['outputs']['result']['mismatched_cells'],0)
        done=api.apply({'action':'commit','receipt':proposed['receipt']})
        self.assertEqual(done['status'],'committed');self.assertTrue(done['residual']['all_matched'])
        self.assertEqual(bank.revisions[done['revision']]['parent'],before['branches']['objects'])

    def test_stale_and_tampered_receipts_are_rejected(self):
        bank=make_bank();api=Actions(bank);r=api.apply(proposal(bank))['receipt']
        changed=copy.deepcopy(r);changed['payload']['candidate']['inputs']['offset']['data']=[0,3]
        self.assertEqual(api.apply({'action':'commit','receipt':changed})['error']['code'],'integrity')
        bank.edit('objects',{'minimum':Value('index',3)})
        self.assertEqual(api.apply({'action':'commit','receipt':r})['error']['code'],'conflict')

    def test_old_receipt_does_not_survive_library_extension(self):
        bank=make_bank();api=Actions(bank);r=api.apply(proposal(bank))['receipt']
        bank.define_function('identity',{'state':'scalar'},{'nodes':[],'outputs':{'result':'state'}})
        self.assertEqual(api.apply({'action':'commit','receipt':r})['error']['code'],'identity')

    def test_target_and_output_locks_prevent_commit(self):
        bank=make_bank();api=Actions(bank);old=bank.pack()
        p=api.apply(proposal(bank,(0,1)));self.assertEqual(p['status'],'rejected');self.assertEqual(p['reason'],'target_mismatch')
        self.assertEqual(api.apply({'action':'commit','receipt':p['receipt']})['error']['code'],'constraint')
        request=proposal(bank);request['locked_outputs']=['result']
        locked=api.apply(request);self.assertEqual(locked['reason'],'locked_output_changed');self.assertEqual(bank.pack(),old)

    def test_graph_edit_proposal_rebinds_by_role(self):
        bank=make_bank();api=Actions(bank)
        request={'action':'propose','workspace':'scalar','expected_revision':bank.branches['scalar'],
                 'graph_edits':[{'kind':'rebind','node':'product','argument':'b','ref':'a'}],
                 'targets':{'product':Value('scalar',9).pack()},'require_target_match':True}
        r=api.apply(request);self.assertEqual(r['status'],'ready')
        self.assertEqual(api.apply({'action':'commit','receipt':r['receipt']})['status'],'committed')
        request['expected_revision']=bank.branches['scalar'];request['graph_edits'][0]['ref']='missing'
        bad=api.apply(request);self.assertEqual(bad['status'],'rejected');self.assertEqual(bad['error']['code'],'binding')

    def test_receipt_roundtrip_and_nested_values_replay_after_reload(self):
        bank=make_bank();r=Actions(bank).apply(proposal(bank))['receipt']
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'bank.json';bank.save(path);loaded=Store.load(path,base_registry())
            done=Actions(loaded).apply({'action':'commit','receipt':json.loads(json.dumps(r))})
            self.assertEqual(done['status'],'committed');loaded.save(path)
            self.assertEqual(Store.load(path,base_registry()).pack(),loaded.pack())

    def test_residual_reports_shape_errors_instead_of_false_cell_accuracy(self):
        r=residual({'answer':Value('grid',[[1,2]]).pack()},{'answer':Value('grid',[[1],[2]]).pack()})
        self.assertFalse(r['all_matched']);self.assertEqual(r['outputs']['answer']['reason'],'shape_mismatch')
        r=residual({'a':Value('scalar',4).pack()},{'a':Value('scalar',7).pack()})
        self.assertEqual(r['outputs']['a']['signed_error'],-3)


if __name__=='__main__':unittest.main()
