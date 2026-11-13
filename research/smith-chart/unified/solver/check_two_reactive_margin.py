"""Independent finite controls of the coefficient separator and exception bridge."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
import two_reactive_margin as margin
from exact_phasor import C,response
from pure_type_margins import gamma

def main():
    record=margin.certificate();margin.verify(record)
    polys=margin.polynomials();bounds=record['polynomial_box_bounds']
    corners=0
    for signs in product((-1,1),repeat=6):
        values={n:v+sign*margin.EPSILON for n,v,sign in zip(margin.VARIABLES,margin.TARGET,signs)}
        for name,poly in polys.items():
            value=margin.evaluate(poly,values)
            lo,hi=map(F,bounds[name]);assert lo<=value<=hi
        corners+=1
    # Figure A.11 / formula A.252: L1=C1=R1=R3=1, R2=2.
    # This bridge is NONREGULAR. A false "all two-reactive are regular"
    # shortcut would be rejected by this physically solved control.
    edges=[('L',1,2,F(1)),('R',2,0,F(2)),('R',1,3,F(1)),
           ('R',3,0,F(1)),('C',2,3,F(1))]
    coeff=dict(zip(margin.VARIABLES,map(F,(5,4,4,3,4,4))))
    vals={name:margin.evaluate(poly,coeff) for name,poly in polys.items()}
    assert vals['t']>0 and vals['lambda1']<0 and vals['lambda2']<0 and vals['mu1']>=0
    comparisons=0;separation=[]
    for s in margin.SAMPLES:
        Z=(5*s*s+4*s+4)/(3*s*s+4*s+4);g=(Z-1)/(Z+1)
        assert response(edges,C(s))['gamma']==C(g);comparisons+=1
        separation.append(abs(g-gamma(s)))
    for omega in (F(1,2),F(1),F(2)):
        s=C(0,omega);Z=(5*s*s+4*s+4)/(3*s*s+4*s+4)
        assert response(edges,s)['gamma']==(Z-1)/(Z+1);comparisons+=1
    assert max(separation)>margin.MARGIN
    controls=[]
    for name in ('margin','coefficient_error_factor','coefficient_box_radius'):
        bad=deepcopy(record);bad[name]='0'
        try:margin.verify(bad)
        except ValueError:controls.append(name)
        else:raise AssertionError('Corrupt coefficient certificate accepted')
    bad=deepcopy(record);bad['matrix_inverse'][0][0]='0'
    try:margin.verify(bad)
    except ValueError:controls.append('inverse_entry')
    else:raise AssertionError('Corrupt inverse accepted')
    print(json.dumps({'status':'PASS','coefficient_box_corners':corners,
      'polynomial_enclosure_comparisons':corners*len(polys),'physical_bridge_comparisons':comparisons,
      'nonregular_bridge_polynomials':{k:str(v) for k,v in vals.items()},
      'adversarial_controls':controls,'certificate':record,
      'coverage':'Finite implementation controls; all-topology and arbitrary-resistor scope is from the written network-polynomial and authenticated classical-source argument.'},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
