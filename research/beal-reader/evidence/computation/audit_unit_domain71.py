#!/usr/bin/env python3
"""Confirm a legacy metadata correction without changing historical source bytes."""
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);ns=p.parse_args()
    inputs=Path('evidence/computation/metadata71_inputs')
    primary=json.loads((inputs/'fixed_seven71.json').read_text())
    separate=json.loads((inputs/'independent_fixed_seven71.json').read_text())
    assert pow(5,3,7)==6
    units=[(a,b) for a in range(49) for b in range(49) if (a%7,b%7)!=(0,0)]
    actual=len(units)
    assert actual==49**2-7**2==2352
    assert primary['unit_domain']==2304 and actual!=primary['unit_domain']
    assert actual==separate['unit_elements_checked']==primary['unit_class_count']*primary['unit_class_fiber_size']
    result={'status':'METADATA_CORRECTION_CONFIRMED','legacy_primary_unit_domain':2304,'actual_enumerated_unit_domain':2352,
            'separate_original_unit_elements_checked':separate['unit_elements_checked'],'exact_count_formula':'49^2-7^2=49*48=2352',
            'unit_quotient_size':primary['unit_class_count'],'unit_class_fiber_size':primary['unit_class_fiber_size'],
            'correction_scope':'One hardcoded metadata number. The original loop, quotient and accepted period/gauge classification are unchanged.',
            'historical_bytes_changed':False,'new_publication_count_to_use':2352,'actual_arithmetic_target_computed':False}
    ns.output.mkdir(parents=True,exist_ok=True);(ns.output/'correction.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
