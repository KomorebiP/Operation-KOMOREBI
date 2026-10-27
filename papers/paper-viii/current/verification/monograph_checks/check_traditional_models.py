#!/usr/bin/env python3
"""Independent rational validation of three authored illustrative model tables."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from fractions import Fraction as Q
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def apply(A,x):return [dot(r,x) for r in A]
def multiply(A,B):return [[dot(r,c) for c in zip(*B)] for r in A]
def inverse(A):
 n=len(A);M=[r[:]+[Q(i==j) for j in range(n)] for i,r in enumerate(A)]
 for j in range(n):
  k=next(i for i in range(j,n) if M[i][j]);M[j],M[k]=M[k],M[j];v=M[j][j];M[j]=[x/v for x in M[j]]
  for i in range(n):
   if i!=j:
    v=M[i][j];M[i]=[x-v*y for x,y in zip(M[i],M[j])]
 return [r[n:] for r in M]
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=json.loads(a.data.read_text());checks=[]
 def check(name,x):
  assert x,name;checks.append({'name':name,'pass':True})
 def eq(name,x,y):check(name,x==y)
 b=d['bdlr'];diag=list(map(Q,[2,3,4,5]));u=list(map(Q,[1,0,1,0]));v=list(map(Q,[1,1,0,0]));x=list(map(Q,[1,2,3,4]));A=[[Q(i==j)*diag[i]+u[i]*v[j] for j in range(4)] for i in range(4)];y=apply(A,x)
 for name,value in [('D_diagonal',diag),('u',u),('v',v),('x',x),('y',y)]:eq('BDLR '+name,value,list(map(Q,b[name])))
 eq('BDLR matrix',A,[[Q(z) for z in r] for r in b['A']]);eq('BDLR output',[Q(5),Q(6),Q(15),Q(20)],y)
 dx=[z*w for z,w in zip(diag,x)];correction=[z*dot(v,x) for z in u];eq('Diagonal component',dx,list(map(Q,b['Dx'])));eq('Rank-one component',correction,list(map(Q,b['correction'])))
 inv=inverse(A);I=[[Q(i==j) for j in range(4)] for i in range(4)];eq('Gaussian inverse left identity',multiply(inv,A),I);eq('Gaussian inverse right identity',multiply(A,inv),I);eq('Gaussian solve',apply(inv,y),x)
 diyu=[w/z for w,z in zip(u,diag)];diyy=[w/z for w,z in zip(y,diag)];den=1+dot(v,diyu);coef=dot(v,diyy)/den
 eq('Woodbury denominator',den,Q(b['woodbury_denominator']));eq('Woodbury coefficient',coef,Q(b['woodbury_coefficient']));eq('Woodbury recovered vector',[w-z*coef for w,z in zip(diyy,diyu)],apply(inv,y));eq('Stored scalar slots',b['stored_scalar_slots'],4+2*4);eq('Dense scalar slots',b['dense_scalar_slots'],4*4)
 c=d['compiler'];rows=[{'leaves':['r'],'cost':1,'error':6},{'leaves':['a','b'],'cost':3,'error':4},{'leaves':['a1','a2','b'],'cost':5,'error':1}];eq('Complete tree enumeration',rows,c['prunings'])
 for r in rows:
  eq('Tree cost '+','.join(r['leaves']),sum(c['nodes'][n]['cost'] for n in r['leaves']),r['cost']);eq('Tree error '+','.join(r['leaves']),sum(c['nodes'][n]['error'] for n in r['leaves']),r['error'])
 for row in c['lagrangian']:
  lam=Q(row['lambda']);scores=[Q(r['cost'])+lam*r['error'] for r in rows];eq('Lagrange scores '+str(lam),scores,list(map(Q,row['scores'])));eq('Lagrange minimum '+str(lam),min(scores),Q(row['minimum']));eq('Lagrange argmin '+str(lam),[i for i,v in enumerate(scores) if v==min(scores)],row['optimal_indices'])
 for row in c['budget_frontier']:eq('Tree budget '+str(row['budget']),min((r['cost'] for r in rows if r['error']<=row['budget']),default=None),row['minimum_cost'])
 lower=Q(rows[1]['cost']-rows[0]['cost'],rows[0]['error']-rows[1]['error']);upper=Q(rows[2]['cost']-rows[1]['cost'],rows[1]['error']-rows[2]['error']);cross=Q(rows[2]['cost']-rows[0]['cost'],rows[0]['error']-rows[2]['error'])
 eq('Unsupported lower endpoint',lower,Q(c['middle_optimum_lambda_lower']));eq('Unsupported upper endpoint',upper,Q(c['middle_optimum_lambda_upper']));eq('Supported crossing',cross,Q(c['supported_transition']));check('Middle never minimizes any nonnegative lambda',lower>upper)
 pr=d['precision'];opts=pr['options'];assign=[]
 for labels in itertools.product('FA',repeat=3):assign.append({'assignment':''.join(labels),'cost':sum(opts[i][k]['cost'] for i,k in enumerate(labels)),'error':sum(opts[i][k]['error'] for i,k in enumerate(labels))})
 eq('All eight precision assignments',assign,pr['assignments']);eq('Prefix zero state',pr['dynamic_program_tables'][0],{'0':0})
 for n in range(1,4):
  values={}
  for labels in itertools.product('FA',repeat=n):
   err=sum(opts[i][k]['error'] for i,k in enumerate(labels));cost=sum(opts[i][k]['cost'] for i,k in enumerate(labels));values[str(err)]=min(cost,values.get(str(err),cost))
  eq('Exact prefix table '+str(n),values,pr['dynamic_program_tables'][n])
 for budget in range(9):eq('Precision budget '+str(budget),min((r['cost'] for r in assign if r['error']<=budget),default=None),min((cost for err,cost in pr['dynamic_program_tables'][-1].items() if int(err)<=budget),default=None))
 feasible=[r for r in assign if r['error']<=3];opt=min(r['cost'] for r in feasible);winners=[r for r in feasible if r['cost']==opt];eq('Budget3 unique exact optimum',winners,[{'assignment':'AFF','cost':6,'error':3}]);eq('Recorded precision optimum',winners[0],pr['optimum'])
 false={'dropping_rank_one_action_detected':dx!=y,'incorrect_Woodbury_denominator_detected':[w-z*Q(9,2) for w,z in zip(diyy,diyu)]!=x,'unsupported_middle_requires_empty_lambda_interval':lower>upper,'all_fast_precision_exceeds_budget':next(r['error'] for r in assign if r['assignment']=='FFF')>3,'ignoring_sensitive_edge_infeasible':next(r['error'] for r in assign if r['assignment']=='FAA')>3}
 eq('Five concrete false controls',false,d['false_controls']);check('All controls false in these models',all(false.values()))
 result={'status':'PASS','arithmetic_domain':'fractions.Fraction exact Q; independent Gaussian elimination and exhaustive finite enumerations','data_sha256':sha(a.data),'positive_assertions':len(checks),'checks':checks,'false_controls_rejected':len(false),'false_controls':false,'bounds':{'matrix_dimension':4,'tree_nodes':5,'complete_prunings':3,'Lagrange_samples':7,'tree_budgets':[0,6],'precision_assignments':8,'precision_prefix_lengths':[0,3],'precision_budgets':[0,8]},'exact_values':{'bdlr_y':list(map(str,y)),'woodbury_denominator':str(den),'woodbury_coefficient':str(coef),'unsupported_lambda_lower':str(lower),'unsupported_lambda_upper':str(upper),'supported_crossing':str(cross),'precision_B3':winners},'non_claims':['Declared costs/errors are illustrative, not actual precision-kernel or device behavior.','These finite models do not extend formal coverage.','A universal compiler correctness result remains in the separately stated proof contract.']}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
