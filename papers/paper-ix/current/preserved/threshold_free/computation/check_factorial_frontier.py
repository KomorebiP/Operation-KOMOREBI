#!/usr/bin/env python3
"""Small exact regression and sharpness frontier for the strengthened theorem."""
from __future__ import annotations
import argparse
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
import json
import time

from check_dyadic_differences import differences, valuation, rational_coefficients, rational_to_mod

VERSION="1.0.0"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound",type=int,default=96)
    parser.add_argument("--precision",type=int,default=1024)
    parser.add_argument("--mixed-order",type=int,default=5)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic();modulus=1<<args.precision
    assert args.precision>4*args.bound
    step_types=[1,2,3,4,5,7,8,9]
    mixed_sequences=[steps for k in range(1,args.mixed_order+1) for steps in combinations_with_replacement(step_types,k) if sum(steps)<=args.bound]
    data={"version":VERSION,"bound":args.bound,"precision_bits":args.precision,"mixed_order":args.mixed_order,"mixed_step_types":step_types,"mixed_sequences_tested":len(mixed_sequences),"base_domain":"Every n>=0 with n+sum(steps)<=bound.","family_results":[],"non_claims":["A bounded pass does not prove a universal statement.","Sharpness observations apply only to declared domains."]}
    regression_failures=[]
    for j in range(4):
        inv=[pow(comb(4*m+j,j),-1,modulus) for m in range(args.bound+1)]
        values=[1]
        for n in range(1,args.bound+1):values.append(-sum(comb(4*n,4*r)*values[r]*inv[n-r] for r in range(n))%modulus)
        exact=rational_coefficients(j,8)
        assert all(values[n]==rational_to_mod(v,modulus) for n,v in enumerate(exact))
        result={"j":j,"unit_step_exact_checks":0,"unit_step_exact_failures":[],"mixed_lower_bound_checks":0,"mixed_lower_bound_failures":[],"mixed_equality_count":0,"mixed_strict_count":0,"mixed_equality_witness":None,"first_mixed_equality_failure":None,"by_order":[],"j2_double_slope_checks":0,"j2_double_slope_failures":[],"j2_extra_bit_violations":[],"j2_minimum_double_slope_surplus":None,"j2_minimum_double_slope_witness":None,"odd_only_equality_checks":0,"odd_only_equality_failures":[],"parity_equality_rule_counterexamples":[],"row_minimum_witnesses":[]}
        unit_row=values[:]
        for k in range(1,args.bound+1):
            unit_row=differences(unit_row,1,modulus)
            target=2*k-k.bit_count()
            if j in (0,1):
                for n,c in enumerate(unit_row):
                    result["unit_step_exact_checks"]+=1
                    if valuation(c,args.precision)!=target:result["unit_step_exact_failures"].append({"n":n,"k":k,"actual":valuation(c,args.precision),"expected":target})
            actual_min=min(valuation(c,args.precision) for c in unit_row)
            witness=next(n for n,c in enumerate(unit_row) if valuation(c,args.precision)==actual_min)
            result["row_minimum_witnesses"].append({"order":k,"minimum_valuation":actual_min,"base":witness,"baseline_factorial":target+[0,0,3,1][j]})
            if j==2:
                for n,c in enumerate(unit_row):
                    result["j2_double_slope_checks"]+=1
                    strong=3*k-k.bit_count()
                    actual=valuation(c,args.precision);difference=actual-strong
                    record={"n":n,"steps":[1]*k,"actual":actual,"strong_lower_bound":strong}
                    if difference<0:
                        result["j2_double_slope_failures"].append(record);regression_failures.append({"j":j}|record)
                    if difference<1:result["j2_extra_bit_violations"].append(record|{"candidate_lower_bound":strong+1})
                    if result["j2_minimum_double_slope_surplus"] is None or difference<result["j2_minimum_double_slope_surplus"]:result.update(j2_minimum_double_slope_surplus=difference,j2_minimum_double_slope_witness=record)
        for steps in mixed_sequences:
            row=values[:]
            for u in steps:row=differences(row,u,modulus)
            k=len(steps);step_value=sum(valuation(u,args.precision) for u in steps)
            core=2*k-k.bit_count()+step_value
            lower=core+[0,0,3,1][j]
            order_entry=next((v for v in result["by_order"] if v["order"]==k),None)
            if order_entry is None:
                order_entry={"order":k,"tested":0,"minimum_surplus":args.precision,"equality_count":0,"strict_count":0,"minimum_witness":None}
                result["by_order"].append(order_entry)
            for n,c in enumerate(row):
                actual=valuation(c,args.precision);witness={"n":n,"steps":list(steps),"actual":actual,"lower_bound":lower}
                result["mixed_lower_bound_checks"]+=1;order_entry["tested"]+=1
                surplus=actual-lower
                if surplus<0:
                    result["mixed_lower_bound_failures"].append(witness);regression_failures.append({"j":j}|witness)
                if surplus<order_entry["minimum_surplus"]:order_entry.update(minimum_surplus=surplus,minimum_witness=witness)
                if surplus==0:
                    result["mixed_equality_count"]+=1;order_entry["equality_count"]+=1
                    if result["mixed_equality_witness"] is None:result["mixed_equality_witness"]=witness
                else:
                    result["mixed_strict_count"]+=1;order_entry["strict_count"]+=1
                    if result["first_mixed_equality_failure"] is None:result["first_mixed_equality_failure"]=witness
                if j in (0,1) and all(u%2 for u in steps):
                    result["odd_only_equality_checks"]+=1
                    if actual!=core:result["odd_only_equality_failures"].append(witness)
                if j in (0,1):
                    predicted_exact=(k%2==1 or sum(u%2 for u in steps)%2==0)
                    if (actual==core)!=predicted_exact and len(result["parity_equality_rule_counterexamples"])<10:result["parity_equality_rule_counterexamples"].append(witness|{"predicted_exact":predicted_exact})
                if j==2:
                    result["j2_double_slope_checks"]+=1
                    strong=3*k-k.bit_count()+step_value
                    difference=actual-strong
                    if difference<0:
                        violation=witness|{"strong_lower_bound":strong}
                        result["j2_double_slope_failures"].append(violation);regression_failures.append({"j":j}|violation)
                    if difference<1:result["j2_extra_bit_violations"].append(witness|{"candidate_lower_bound":strong+1})
                    if result["j2_minimum_double_slope_surplus"] is None or difference<result["j2_minimum_double_slope_surplus"]:result.update(j2_minimum_double_slope_surplus=difference,j2_minimum_double_slope_witness=witness|{"strong_lower_bound":strong})
        if j in (0,1):
            exact_mixed=exact[3]-exact[2]-exact[1]+exact[0]
            result["exact_rational_mixed_counterexample"]={"n":0,"steps":[1,2],"rational_value":str(exact_mixed),"actual_valuation":valuation(abs(exact_mixed.numerator),args.precision)-valuation(exact_mixed.denominator,args.precision),"proposed_exact_valuation":4}
        result["unit_step_exact_passed"]=not result["unit_step_exact_failures"] if j in (0,1) else None
        data["family_results"].append(result)
        print(json.dumps({"j":j,"mixed_checks":result["mixed_lower_bound_checks"],"unit_exact_failures":len(result["unit_step_exact_failures"]),"mixed_regression_failures":len(result["mixed_lower_bound_failures"]),"first_equality_failure":result["first_mixed_equality_failure"],"j2_double_slope_minimum_surplus":result["j2_minimum_double_slope_surplus"]}),flush=True)
    data.update(regression_failures=regression_failures,regression_passed=not regression_failures,runtime_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"regression_passed":not regression_failures,"runtime_seconds":data["runtime_seconds"]}))
    if regression_failures:raise SystemExit(1)


if __name__=="__main__":main()
