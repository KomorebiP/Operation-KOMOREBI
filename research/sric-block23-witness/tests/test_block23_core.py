import inspect
from block23 import FAMILIES,EpisodeSpec,audit_hidden,build_episode,compile_ontology,expected_certificate
from block23.core import THRESHOLDS

def test_visible_compiler_interface_hides_family_and_semantics():
 ep=build_episode(EpisodeSpec('identified',23000,'preaudit'))
 assert not hasattr(ep.visible,'family')
 assert not hasattr(ep.visible,'hidden')
 src=inspect.getsource(compile_ontology)
 assert '.family' not in src
 assert 'z0' not in src

def test_pre_certificate_classes():
 expected={'identified':'CANDIDATE_IDENTIFIED','answer_shortcut':'CANDIDATE_IDENTIFIED','gauge_equivalent':'CANDIDATE_GAUGE_AMBIGUOUS','semantic_ambiguity':'CANDIDATE_GAUGE_AMBIGUOUS','partial_ontology':'CANDIDATE_PARTIAL','destructive_loss':'NO_GO'}
 for i,f in enumerate(FAMILIES):
  ep=build_episode(EpisodeSpec(f,24000+i,'preaudit'));c=compile_ontology(ep.visible,41000+i);assert c.pre_certificate==expected[f]

def test_final_certificates():
 for i,f in enumerate(FAMILIES):
  ep=build_episode(EpisodeSpec(f,64000+i,'final'));c=compile_ontology(ep.visible,81000+i);r=audit_hidden(ep,c);assert r['certificate']==expected_certificate(f)

def test_answer_only_shortcut_is_rejected():
 ep=build_episode(EpisodeSpec('answer_shortcut',64100,'final'));c=compile_ontology(ep.visible,81100)
 row=next(x for x in c.candidate_table if x['method']=='answer_only')
 assert row['worst_answer_accuracy']>=THRESHOLDS['answer_accuracy']
 assert row['worst_future_r2']<THRESHOLDS['future_r2']
 assert row['worst_intervention_r2']<THRESHOLDS['intervention_r2']
 assert not row['passed'] and c.selected_method=='predictive' and c.selected_rank==4

def test_counterfactual_patch_is_specific():
 ep=build_episode(EpisodeSpec('identified',64200,'final'));c=compile_ontology(ep.visible,81200);r=audit_hidden(ep,c)
 for m in r['counterfactual_patch'].values():
  assert m['selected_future_r2']>.95
  assert m['selected_intervention_r2']>.95
  assert m['answer_only_future_r2']<.30
  assert m['pca_future_r2']<.30
