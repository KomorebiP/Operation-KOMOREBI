"""Behavioral and boundary tests. Author: Komorebi P."""
import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import engine,solver,evaluate
from repairs import inspect_repair

def candidate(name='family',color=2,block=14,program=None,cost=1):
    c={'entrant':name,'program':program or {},'test_outputs':[[[color]]],'source_block':block,
       'complexity':cost,'behavior_hash':engine.contract.digest([[[color]]])}
    c['candidate_hash']=engine.contract.digest(c);return c

def record(*rows):return engine.seal({'candidates':list(rows),'task_semantic_hash':'fixture','base':[{'attempt_1':[[0]],'attempt_2':[[1]]}],'receipts':{}})

def codebook(mapping,feature='foreground_count'):
    return candidate('multiscale_codec',program={'operator':'scalar_feature_codebook','feature':feature,'mapping':mapping})

class Integrity(unittest.TestCase):
    def test_reject_attached_test_labels(self):
        with self.assertRaisesRegex(ValueError,'attached'):
            engine.sanitize({'train':[{'input':[[0]],'output':[[1]]}],'test':[{'input':[[0]],'output':[[2]]}]})
    def test_ids_and_metadata_are_removed(self):
        t={'id':'secret','train':[{'input':[[0]],'output':[[1]],'id':'x'}],'test':[{'input':[[2]],'id':'y'}]}
        self.assertEqual(engine.sanitize(t),{'train':[{'input':[[0]],'output':[[1]]}],'test':[{'input':[[2]]}]})
    def test_veto_is_executable_negative_evidence(self):
        c=codebook([['a',1],['b',1],['c',2]])
        r=inspect_repair(c)
        self.assertEqual(r['status'],'veto')
        self.assertEqual(r['witness']['collisions'],{'1':['a','b']})
        self.assertEqual(r['witness_hash'],engine.contract.digest(r['witness']))
        self.assertEqual(len(solver.rank_record(record(c),'recent_control')['behaviors']),1)
        self.assertEqual(solver.rank_record(record(c),'typed_recent')['behaviors'],[])
    def test_injective_codebook_survives(self):
        self.assertEqual(inspect_repair(codebook([['a',1],['b',2]]))['status'],'supported')
    def test_binary_predicate_and_unrelated_family_are_outside_scope(self):
        c=codebook([['a',1],['b',1]],'orthogonal_symmetry_span3')
        self.assertEqual(inspect_repair(c)['status'],'out_of_scope')
        c['entrant']='unrelated';self.assertEqual(inspect_repair(c)['status'],'out_of_scope')
    def test_absent_descendant_is_not_a_veto(self):
        c=candidate('family');r=solver.rank_record(record(c),'typed_recent')
        self.assertEqual(len(r['behaviors']),1)
    def test_trace_control_abstains_on_unseen_keys_without_declaring_program_false(self):
        c=candidate('feature_induction');c['evidence']={'unseen_test_keys':3}
        r=record(c)
        self.assertEqual(len(solver.rank_record(r,'typed_recent')['behaviors']),1)
        d=solver.rank_record(r,'typed_supported')
        self.assertEqual(d['behaviors'],[])
        self.assertEqual(d['repairs'][-1]['status'],'abstained_unknown')
        c['evidence']['unseen_test_keys']=0
        self.assertEqual(len(solver.rank_record(record(c),'typed_supported')['behaviors']),1)
    def test_active_descendant_supersedes_ancestor_without_vote_inflation(self):
        a,b=candidate('family',1),candidate('family_v2',2)
        r=solver.rank_record(record(a,b),'typed_recent')
        self.assertEqual([x['test_outputs'] for x in r['behaviors']],[[[[2]]]])
        self.assertEqual(r['superseded'],[a['candidate_hash']])
    def test_tampered_candidate_record_rejected(self):
        r=record(candidate());r['candidates'][0]['test_outputs']=[[[9]]]
        with self.assertRaisesRegex(ValueError,'hash'):solver.rank_record(r,'typed_recent')
    def test_source_hash_checked_before_import(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'unsafe.py').write_text("raise RuntimeError('must not run')")
            with self.assertRaisesRegex(engine.contract.TournamentError,'hash mismatch'):
                engine.contract.load_entrants(p,{'unsafe':'0'*64})
    def test_scorer_keeps_wrong_predictions_and_multitest_arity(self):
        truth={'a':[[[1]],[[2]]],'b':[[[3]]]}
        pred={'a':[{'attempt_1':[[1]],'attempt_2':[[0]]},{'attempt_1':[[0]],'attempt_2':[[2]]}],
              'b':[{'attempt_1':[[0]],'attempt_2':[[0]]}]}
        r=evaluate.score(pred,truth)
        self.assertEqual((r['pass1_exact_outputs'],r['pass2_exact_outputs'],r['whole_tasks'],r['total_outputs']),(1,2,1,3))
    def test_dispatch_preserves_live_attempt1_and_spends_second_slot_on_distinct_behavior(self):
        task={'train':[{'input':[[0]],'output':[[1]]}],'test':[{'input':[[0]]}]}
        r=record(candidate('same',0,cost=0),candidate('different',2,cost=2))
        r['task_semantic_hash']=engine.contract.digest(task);r=engine.seal(r)
        census=engine.seal({'scope':'all_banks','records':{'a':r},'challenges_hash':engine.contract.digest({'a':task}),
                           'bank_hash':engine.bank_hash(),'code_hash':engine.code_hash()})
        out=solver.dispatch({'a':task},census,'typed_recent')['submission']['a'][0]
        self.assertEqual(out,{'attempt_1':[[0]],'attempt_2':[[2]]})
    def test_census_bound_to_challenges(self):
        census=engine.seal({'scope':'all_banks','records':{},'challenges_hash':'wrong','bank_hash':engine.bank_hash(),'code_hash':engine.code_hash()})
        with self.assertRaisesRegex(ValueError,'challenge'):solver.dispatch({},census,'typed_recent')

if __name__=='__main__':unittest.main()
