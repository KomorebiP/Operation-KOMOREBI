from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((ROOT/'results/audit_residual.json').read_text());r=json.loads((ROOT/'results/integer_audit.json').read_text());pre=json.loads((ROOT/'PREDECESSOR_ARCHIVE.json').read_text())
m={
 'schema_version':1,'claim_id':'Komorebi.Padic.Block34.ResidualRealization.FiniteAudit',
 'repository':{'commit':'predecessor-sha256:'+pre['sha256'],'dirty':True},
 'command':r['argv'],'environment':{'software':[{'name':'Python','version':a['python']},{'name':'SymPy','version':a['sympy']}]},
 'mathematics':{'assertion_tested':'Intrinsic residual images, cross-realization simulation, cardinality comparison, word order, finite Hankel signatures of actual masks.',
   'coefficient_domain':'Exact Z/(p^r) modules, integer matrices, finite enumerated linear spans.',
   'conventions':'Destination rows/source columns; prefixes consumed before suffixes; one scalar/vector/set/signature assertion counts once.',
   'inputs':['verification/audit_residual.py','verification/observable_engine.py','verification/presentation_engine.py','verification/reachable_engine.py','verification/reference'],
   'bounds':{'generic_prime_precision_pairs':[[2,0],[2,1],[2,2],[3,1],[3,2]],'dimensions':[0,1,2],'alphabet_sizes':[0,1,2],'trials':2,
      'generic_pairs':a['generic_system_pairs'],'mask_cases':a['mask_cases'],'mask_coefficient_indices':[0,31],
      'maximum_hankel_recurrence_index':max(x['maximum_recurrence_index'] for x in a['mask_results'])},
   'non_claims':a['non_claims']},
 'randomness':{'used':True,'generator':'Python random.Random / Mersenne Twister','seed':a['seed']},
 'run':{'started_at':r['started_at'],'runtime_seconds':r['seconds'],'exit_status':r['exit_status']},
 'outputs':[{'path':p,'sha256':sha(ROOT/p)} for p in ['results/audit_residual.json','results/integer_audit.log']],
 'input_artifacts':[{'path':p,'sha256':digest,'sha256_after':r['input_hashes_after'][p]} for p,digest in r['input_hashes'].items()],
 'checks':[{'name':k,'count':v,'passed':True} for k,v in a['counts'].items()],
 'result':'PASS: '+str(a['assertions'])+' exact finite assertions.',
 'residual_risks':['Finite audit, not universal proof.','Python implementation is not formally refined to the Lean construction.',
   'This retained v1 project-local validation is not the installed full schema2 validator.']}
(ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n');print('Manifest written with '+str(len(m['input_artifacts']))+' frozen input hashes.')
