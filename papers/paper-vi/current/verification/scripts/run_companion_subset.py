#!/usr/bin/env python3
"""Directly invoke 37 unchanged tests; independently reproduce 17 boundary cases.
This runner does not implement or substitute for pytest and does not claim a pytest run.
"""
import argparse, importlib.util, inspect, json, sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--companion',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 if sys.flags.optimize:raise RuntimeError('Original assertions require nonoptimized Python.')
 sys.path.insert(0,str(args.companion)); records=[]
 for path in sorted((args.companion/'tests').glob('test_*.py')):
  if path.name=='test_review_boundaries.py':continue
  spec=importlib.util.spec_from_file_location(path.stem,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  for name,fun in sorted(vars(mod).items()):
   if name.startswith('test_') and inspect.isfunction(fun):
    if len(inspect.signature(fun).parameters):raise RuntimeError('Unexpected fixture or parameter')
    fun();records.append({'file':path.name,'function':name,'status':'PASS'})
 if len(records)!=37:raise RuntimeError('Expected 37 unchanged direct tests')
 import numpy as np
 from projector_transfer_semigroups.bayes import bayes_update,packet_bayes_update,coarsen_probability,effective_coarse_likelihood,bayesian_coarsening_defect,canonical_bayesian_partition
 boundaries=[]
 def passed(name):boundaries.append({'case':name,'status':'PASS'})
 def check(name,condition):
  if not bool(condition):raise RuntimeError(name)
  passed(name)
 def rejects(name,exc,fun):
  try:fun()
  except exc:passed(name)
  else:raise RuntimeError('Expected exception not raised: '+name)
 for i,p in enumerate([[-1,2],[np.nan,1],[np.inf,1],[[1,2]]]):rejects('invalid_prior_'+str(i),ValueError,lambda p=p:bayes_update(np.array(p),np.ones(2)))
 for i,l in enumerate([[np.nan,1],[np.inf,1]]):rejects('nonfinite_likelihood_'+str(i),ValueError,lambda l=l:bayes_update(np.array([.4,.6]),np.array(l)))
 for i,g in enumerate([[[0],[0,1]],[[0]],[[.2],[1]],[[],[0,1]]]):rejects('invalid_partition_'+str(i),ValueError,lambda g=g:packet_bayes_update(np.array([.4,.6]),np.ones(2),g))
 r=packet_bayes_update(np.array([.25,.25,.5]),np.array([0,0,2]),[[0,1],[2]])
 check('zero_evidence_packet',np.array_equal(r['conditional_shapes'][0],[0,0]) and np.array_equal(r['packet_masses'],[0,1]) and np.array_equal(r['posterior'],r['reconstructed']))
 p,l,g=np.array([0.,0.,1.]),np.array([3.,8.,2.]),[[0,1],[2]];r=effective_coarse_likelihood(p,l,g);d=bayesian_coarsening_defect(p,l,g,np.array([1.,3.]))
 check('zero_prior_effective_factorization',np.array_equal(r,[0,2]) and np.allclose(coarsen_probability(bayes_update(p,l),g),bayes_update(coarsen_probability(p,g),r)) and np.allclose(d['defect'],d['factored_defect'],atol=1e-15))
 p,l,k=np.array([.5,.5]),np.array([1.,0.]),np.array([0.,1.])
 if not l@p>0 or not k@p>0:raise RuntimeError('positive individual evidence prerequisite')
 rejects('sequential_zero_evidence',ValueError,lambda:bayes_update(bayes_update(p,l),k))
 p,l=np.array([.5,.5]),np.array([1.,3.]);g=[[0,1]]
 check('one_packet_closure',canonical_bayesian_partition([l])==((0,),(1,)) and np.array_equal(coarsen_probability(bayes_update(p,l),g),[1]) and np.array_equal(bayes_update(coarsen_probability(p,g),np.array([7.])),[1]))
 l=np.array([0.,.75,1.5]);check('tolerance_not_equivalence',abs(l[0]-l[1])<=1 and abs(l[1]-l[2])<=1 and abs(l[0]-l[2])>1 and canonical_bayesian_partition([l],atol=1)==((0,1),(2,)) and canonical_bayesian_partition([l[[1,0,2]]],atol=1)==((0,1,2),))
 a=np.diag([0.,1.])
 if not np.array_equal(np.linalg.inv(-a[1:,1:]),[[-1.]]):raise RuntimeError('hidden inverse prerequisite')
 rejects('hidden_inverse_not_full_resolvent',np.linalg.LinAlgError,lambda:np.linalg.inv(-a))
 a=np.zeros((2,2));p=np.array([.5,.5]);check('defective_exit_density',np.all(a.sum(axis=0)<=0) and -np.ones(2)@a@p==0 and np.ones(2)@p==1)
 if len(boundaries)!=17:raise RuntimeError('Expected 17 independent boundary cases')
 report={'status':'PASS','unchanged_original_tests_directly_invoked':37,'original_test_records':records,'independent_boundary_reproductions':17,'boundary_records':boundaries,'pytest_invoked':False,'count_boundary':'37 unchanged functions and 17 independently coded cases are separate categories. This is not the original full pytest gate.','non_claims':['Numerical API regressions only, not universal proofs or fresh Lean compilation.']}
 args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['original_test_records','boundary_records']},indent=2))
if __name__=='__main__':main()
