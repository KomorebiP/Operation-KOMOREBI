#!/usr/bin/env python3
"""Exact support consequences and retained countervectors of the finite refinement."""
import argparse,json,collections,hashlib
from pathlib import Path

def main():
 a=argparse.ArgumentParser();a.add_argument('--refinement',type=Path,required=True);a.add_argument('--columns',type=Path,required=True);a.add_argument('--counts-dir',type=Path,required=True);a.add_argument('--output',type=Path,required=True);o=a.parse_args()
 d=json.loads(o.refinement.read_text());cols=json.loads(o.columns.read_text());s=d['survivors'];sets=[{p for p,t in zip(z['columns'],z['inertia']) if t} for z in s]
 forced=sorted(set.intersection(*sets)) if s else [];hist=dict(sorted(collections.Counter(str(len(x)) for x in sets).items()));mins=[z for z,x in zip(s,sets) if len(x)==min(map(len,sets))] if s else []
 byq={x['q']:x for x in cols['columns']};oldq=[307,463,617,883,967,1483,1723];oldi=[5,4,2,3,4,2,5];oldrow=[byq[q]['rows']['1471'] for q in oldq];b=sum(x*y for x,y in zip(oldrow,oldi))%7
 counts=[]
 for stage in d['stages']:
  c=json.loads((o.counts_dir/f"count_{stage['q']}.json").read_text())['primes'][0]
  counts.append({k:c[k] for k in ['q','nu','admissible_pairs','degree_one_counts','degree_two_counts','residual_pairs']})
 out={'schema':'beal.block69.support.v1','status':'PASS_EXACT_SUPPORT_SUMMARY','survivor_count':len(s),'minimum_support':min(map(len,sets),default=None),'forced_ramification':forced,'support_histogram':hist,'ratio_histogram':d['ratio_histogram'],
 'special_prime_subsets':dict(sorted(collections.Counter(','.join(map(str,sorted(t&{307,797,1483}))) for t in sets).items())),
 'minimal_survivors':mins,'old_seven_prime_witness':{'test_prime':1471,'support':oldq,'inertia':oldi,'twisted_row':oldrow,'beta_value':b,'natural_rows':[[2,2,5],[5,2,5]],'products_w_codes':[24,31]},
 'new_counts':counts,'totals':{k:sum(c[k] for c in counts) for k in ['admissible_pairs','degree_one_counts','degree_two_counts','residual_pairs']},
 'scope':'Actual depth one and complete rational beta ramification <=2000, under all inherited hypotheses. Not a global support bound without that scope.'}
 assert b==4
 o.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS_SUPPORT',len(s),hist,forced)
if __name__=='__main__':main()
