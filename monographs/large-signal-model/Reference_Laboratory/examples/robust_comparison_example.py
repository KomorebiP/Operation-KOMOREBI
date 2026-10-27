"""Compare the corrected model with its known generating reference.

This is separate verification, not information supplied to geometry discovery.
It establishes a second common-domain certificate before invoking a law bound.
"""
from pathlib import Path
import json,sys
import sympy as sp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import *
from noisy_generator import noisy_fixture

def main():
    original,noisy,z,delta=noisy_fixture()
    found=json.loads((ROOT/'certificates/robust_curved_certificate.json').read_text())
    corrected={k:poly_matrices(v) for k,v in found['actions'].items()}
    T0=sp.Matrix([[1,0,0],[-sp.Rational(2,3),sp.Rational(10,3),-2],[-sp.Rational(4,3),0,sp.Rational(8,3)]])
    certificate=make_certificate(corrected,z,T0,sp.Rational(1,16),sp.Rational(1,128),sp.Rational(1,128))
    (ROOT/'certificates/robust_comparison_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    data={}
    for name in original:
        D=(T0*(noisy[name]-original[name])*T0.inv()).applyfunc(sp.expand)
        bs=[]
        for k in range(3):
            dk=D.applyfunc(lambda x:x.coeff(U,k))
            bs.append(max(sum(abs(x) for x in dk[0,:]),sum(abs(x) for x in dk[1:,:])))
        error=sum(b/(k+1) for k,b in enumerate(bs))
        data[name]={'coefficient_bounds':[str(x) for x in bs],'integrated_bound':str(error)}
    noise=max(sp.Rational(v['integrated_bound']) for v in data.values());eta=sp.Rational(1,8)
    budget=(1-eta)*noise+2*eta
    out={'comparison_domain':'predecessor ellipsoid, independently checked for corrected operators',
         'initial_error':'0','noise':data,'repair_weight':str(eta),'total_instrument_error_bound':str(budget),
         'law_bound':'min(1,T*'+str(budget/2)+')','replay':replay_certificate(certificate),
         'statistical_coverage':False}
    (ROOT/'verification/robust_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
