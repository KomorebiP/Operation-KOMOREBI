"""Author: Komorebi P. Certificate-first RLC synthesis dispatcher.

Inherited exact charts precede interval-aware passive module composition and
the optional generic solver. UNKNOWN is not UNSAT.
"""
import argparse,json,time,sys
from pathlib import Path
from recursive_modules import synthesize
from interval_certificate import reduce_target


def dispatch(P,Q,max_degree=12,max_states=250,legacy_src=None,timeout_ms=1000,max_budget=None,
             interval_search=True,topology_starts=2,topology_evaluations=600,
             topology_seed=2026111223,max_topology_calls=16):
 t=time.perf_counter()
 try:
  for name,value,minimum in (('max_degree',max_degree,0),('max_states',max_states,1)):
   if isinstance(value,bool) or not isinstance(value,int) or value<minimum:
    raise ValueError(f'{name} must be an integer at least {minimum}')
  if max_budget is not None and (isinstance(max_budget,bool) or not isinstance(max_budget,int) or max_budget<0):
   raise ValueError('max_budget must be a nonnegative integer or None')
  reduced_P,reduced_Q=reduce_target(P,Q)
  degree=max(len(reduced_P),len(reduced_Q))-1
  if max_budget is not None and degree>max_budget:
   return {'status':'UNKNOWN','reason':'Budget is below the exact rational-degree lower bound',
           'reduced_target_degree':degree,'max_budget':max_budget,
           'degree_lower_bound_excludes_requested_budget':True,
           'elapsed_seconds':time.perf_counter()-t}
  r=synthesize(P,Q,max_degree=max_degree,max_states=max_states)
 except (ValueError,ZeroDivisionError,TypeError) as e:
  return {'status':'INVALID_INPUT','reason':str(e)}
 if r['status']=='CERTIFIED_MINIMUM':
  r['elapsed_seconds']=time.perf_counter()-t
  return r
 if interval_search and max_degree>=degree and degree>=3:
  from compositional_solver import synthesize_compositional
  searched=synthesize_compositional(P,Q,max_degree=max_degree,max_states=max_states,
                                   max_budget=max_budget,topology_starts=topology_starts,
                                   topology_evaluations=topology_evaluations,
                                   topology_seed=topology_seed,
                                   max_topology_calls=max_topology_calls)
  if searched['status']=='CERTIFIED_MINIMUM':
   searched['elapsed_seconds']=time.perf_counter()-t
   searched['front_end']={'status':r['status'],'source':'inherited exact rational chart dispatcher'}
   return searched
  if searched['status']=='INVALID_INPUT':return searched
  r['compositional_search']=searched
 if legacy_src is None:
  r['elapsed_seconds']=time.perf_counter()-t
  r['fallback']='not configured; no global infeasibility conclusion'
  return r
 try:
  old=Path(legacy_src)
  if not (old/'synthesize_checked.py').exists():
   raise ValueError('legacy_src must point to the prior proof-carrying src directory')
  sys.path.insert(1,str(old))
  from synthesize_checked import minimum
  z=minimum(P,Q,timeout_ms,max_budget,True)
  z['front_end']={'status':r['status'],'reason':r.get('reason'),
                  'source':'restricted certified Cauer/endpoints/bridge templates'}
  z['elapsed_seconds_total']=time.perf_counter()-t
  return z
 except Exception as e:
  r['elapsed_seconds']=time.perf_counter()-t
  r['fallback_error']={'type':type(e).__name__,'message':str(e)}
  return r

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('target',type=Path)
 parser.add_argument('--legacy-src',type=Path);parser.add_argument('--timeout-ms',type=int,default=1000)
 parser.add_argument('--max-budget',type=int);parser.add_argument('--max-degree',type=int,default=12)
 parser.add_argument('--max-states',type=int,default=250)
 parser.add_argument('--skip-interval-search',action='store_true')
 parser.add_argument('--topology-starts',type=int,default=2)
 parser.add_argument('--topology-evaluations',type=int,default=600)
 parser.add_argument('--topology-seed',type=int,default=2026111223)
 parser.add_argument('--max-topology-calls',type=int,default=16)
 parser.add_argument('--output',type=Path)
 args=parser.parse_args();d=json.loads(args.target.read_text())
 result=dispatch(d['P'],d['Q'],max_degree=args.max_degree,max_states=args.max_states,legacy_src=args.legacy_src,
                 timeout_ms=args.timeout_ms,max_budget=args.max_budget,
                 interval_search=not args.skip_interval_search,
                 topology_starts=args.topology_starts,topology_evaluations=args.topology_evaluations,
                 topology_seed=args.topology_seed,max_topology_calls=args.max_topology_calls)
 payload=json.dumps(result,indent=2)
 if args.output:args.output.write_text(payload)
 else:print(payload)
