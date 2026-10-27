#!/usr/bin/env python3
"""Fresh bounded regression of the paired address-two bound and homogeneous sharpness."""
from __future__ import annotations
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
import argparse,json,time
from check_dyadic_differences import valuation,differences,rational_coefficients,rational_to_mod

VERSION="1.0.0"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bound',type=int,default=96);p.add_argument('--precision',type=int,default=1024)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    start=time.monotonic();modulus=1<<args.precision
    assert args.precision>4*args.bound
    step_types=[1,2,3,4,5,7,8,9]
    sequences=[q for k in range(1,6) for q in combinations_with_replacement(step_types,k) if sum(q)<=args.bound]
    data={'version':VERSION,'bounds':{'maximum_index':args.bound,'precision_bits':args.precision,'homogeneous_steps':list(range(1,17)),'homogeneous_domain':'All k>=1,n>=0,n+k*u<=96.','mixed_order':5,'mixed_step_types':step_types,'mixed_domain':'All nondecreasing multisets, all admissible bases.'},'address_results':[],'non_claims':['Bounded regression does not prove any universal statement.','Earlier bounded manifests are retained without changing their input files.']}
    failures=[]
    for j in [0,1,2]:
        inv=[pow(comb(4*m+j,j),-1,modulus) for m in range(args.bound+1)];values=[1]
        for n in range(1,args.bound+1):values.append(-sum(comb(4*n,4*r)*values[r]*inv[n-r] for r in range(n))%modulus)
        exact=rational_coefficients(j,8)
        assert all(values[n]==rational_to_mod(c,modulus) for n,c in enumerate(exact))
        result={'j':j,'homogeneous_exact_checks':0,'homogeneous_exact_failures':[],'j2_floor_checks':0,'j2_floor_failures':[],'j2_floor_equalities':0,'j2_order_minima':[],'homogeneous_ranges':[]}
        def check_floor(row,steps):
            k=len(steps);h=sum(valuation(u,args.precision) for u in steps)
            target=3*k-k.bit_count()+k//2+h
            order=next((v for v in result['j2_order_minima'] if v['order']==k),None)
            if order is None:
                order={'order':k,'minimum_surplus':args.precision,'minimum_witness':None,'equality_count':0};result['j2_order_minima'].append(order)
            for n,c in enumerate(row):
                actual=valuation(c,args.precision);witness={'base':n,'steps':list(steps),'actual_valuation':actual,'lower_bound':target}
                result['j2_floor_checks']+=1
                if actual<target:result['j2_floor_failures'].append(witness);failures.append({'j':j}|witness)
                if actual==target:result['j2_floor_equalities']+=1;order['equality_count']+=1
                if actual-target<order['minimum_surplus']:order.update(minimum_surplus=actual-target,minimum_witness=witness)
        for u in range(1,17):
            row=values[:];kmax=args.bound//u
            result['homogeneous_ranges'].append({'step':u,'maximum_order':kmax,'base_condition':'n+k*u<=96'})
            for k in range(1,kmax+1):
                row=differences(row,u,modulus)
                if j in [0,1]:
                    expected=2*k-k.bit_count()+k*valuation(u,args.precision)
                    for n,c in enumerate(row):
                        result['homogeneous_exact_checks']+=1
                        if valuation(c,args.precision)!=expected:
                            witness={'base':n,'order':k,'step':u,'actual':valuation(c,args.precision),'expected':expected}
                            result['homogeneous_exact_failures'].append(witness);failures.append({'j':j}|witness)
                elif j==2:check_floor(row,[u]*k)
        if j==2:
            for steps in sequences:
                row=values[:]
                for u in steps:row=differences(row,u,modulus)
                check_floor(row,steps)
            result['j2_order_minima'].sort(key=lambda x:x['order'])
            result['j2_exact_low_order_witnesses']={'order1':{'rational_value':str(exact[1]-exact[0]),'valuation':4},'order2':{'rational_value':str(exact[2]-2*exact[1]+exact[0]),'valuation':6},'order4':{'rational_value':str(sum((-1)**(4-r)*comb(4,r)*exact[r] for r in range(5))),'valuation':13}}
        data['address_results'].append(result)
        print(json.dumps({'j':j,'homogeneous_exact_checks':result['homogeneous_exact_checks'],'homogeneous_exact_failures':len(result['homogeneous_exact_failures']),'j2_floor_checks':result['j2_floor_checks'],'j2_floor_failures':len(result['j2_floor_failures']),'j2_floor_equalities':result['j2_floor_equalities']}),flush=True)
    data.update(passed=not failures,failures=failures,runtime_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'passed':not failures,'runtime_seconds':data['runtime_seconds']}))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
