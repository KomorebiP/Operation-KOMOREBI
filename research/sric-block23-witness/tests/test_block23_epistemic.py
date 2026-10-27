from block23 import EpisodeSpec,audit_hidden,build_episode,compile_ontology

def run(f,seed):
 ep=build_episode(EpisodeSpec(f,seed,'final'));c=compile_ontology(ep.visible,seed+17011);return c,audit_hidden(ep,c)

def test_gauge_is_not_unique_coordinates():
 c,r=run('gauge_equivalent',65000)
 assert c.pre_certificate=='CANDIDATE_GAUGE_AMBIGUOUS'
 assert r['certificate']=='ONTOLOGY_IDENTIFIED_UP_TO_GAUGE'
 assert r['minimum_gauge_invariant_r2']>.98

def test_semantic_ambiguity_refuses_naming():
 c,r=run('semantic_ambiguity',65100)
 assert c.pre_certificate=='CANDIDATE_GAUGE_AMBIGUOUS'
 assert r['certificate']=='ONTOLOGY_UNDERIDENTIFIED'
 assert r['alternative_semantic_disagreement']>.55

def test_partial_ontology_reports_coverage():
 c,r=run('partial_ontology',65200)
 assert c.selected_rank==3
 assert r['certificate']=='PARTIAL_ONTOLOGY'
 assert r['semantic_coverage']==.75

def test_destructive_loss_produces_collision_certificate():
 c,r=run('destructive_loss',65300)
 assert c.pre_certificate=='NO_GO'
 assert r['certificate']=='SEMANTIC_INFORMATION_LOSS'
 assert r['collision_count']>=64
 assert r['minimum_protected_consequence_gap']>.75
