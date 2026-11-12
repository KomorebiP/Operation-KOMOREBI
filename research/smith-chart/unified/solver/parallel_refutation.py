"""Exact independent refutation of the shunt-RLC margin box. Author: Komorebi P.

The physical model is ONLY a resistor network shunting one L and one C directly
across the two terminals. All resistor-only internal nodes are eliminated first.
The unchanged rational refutation consumer checks the final polynomial identity.
"""
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'kernel'))
from pure_type_margins import P,Q,SAMPLES,gamma
from exact_polynomials import (var,const,add,sub,scale,square,dump,digest,check_refutation)
import json

WEIGHTS=tuple(map(F,('-1/2','9/4','-3','5/4')))


def model(margin):
    if not F(0)<margin<min(1+gamma(s) for s in SAMPLES[:4]):
        raise ValueError('Gamma error interval must stay strictly above -1')
    # Annihilation of 1, s and 1/s binds this certificate to the physical shunt
    # admittance g+C*s+h/s; arbitrary interval constraints cannot be substituted.
    for power in (-1,0,1):
        if sum(w*s**power for w,s in zip(WEIGHTS,SAMPLES))!=0:
            raise ValueError('Stencil does not annihilate the physical admittance basis')
    equations={};shape=const(0);lower=F(0);intervals=[]
    for k,(w,s) in enumerate(zip(WEIGHTS,SAMPLES)):
        center=gamma(s);lo=(1-(center+margin))/(1+center+margin)
        hi=(1-(center-margin))/(1+center-margin)
        if lo>hi:raise ValueError('Invalid Cayley interval order')
        intervals.append([str(lo),str(hi)])
        y=var('y'+str(k));slack=var('slack'+str(k))
        shape=add(shape,scale(y,w));lower+=w*(lo if w>0 else hi)
        linear=sub(y,const(lo)) if w>0 else sub(const(hi),y)
        equations['box_'+str(k)]=sub(linear,square(slack))
    equations['shape']=shape
    if lower<=0:raise ValueError('This interval stencil does not exclude zero')
    return equations,lower,intervals


def certificate(margin=F(1,1000)):
    equations,lower,intervals=model(margin)
    proof={'format':'komorebi-rational-refutation-v1','equations_sha256':digest(equations),
        'squares':[{'weight':str(abs(w)/lower),'polynomial':dump(var('slack'+str(k)))} for k,w in enumerate(WEIGHTS)],
        'multipliers':[{'equation':'box_'+str(k),'polynomial':dump(const(abs(w)/lower))} for k,w in enumerate(WEIGHTS)]+
            [{'equation':'shape','polynomial':dump(const(-1/lower))}]}
    record={'format':'komorebi-parallel-RLC-margin-v1','target':{'P':list(P),'Q':list(Q)},
        'margin':str(margin),'sample_gammas':[str(gamma(s)) for s in SAMPLES[:4]],
        'admittance_intervals':intervals,'positive_stencil_lower_bound':str(lower),'proof':proof}
    verify(record,margin)
    return record


def verify(record,expected_margin=F(1,1000)):
    if record.get('format')!='komorebi-parallel-RLC-margin-v1' or record.get('target')!={'P':list(P),'Q':list(Q)}:
        raise ValueError('Target/model binding mismatch')
    margin=F(record['margin'])
    if margin!=expected_margin:raise ValueError('Margin binding mismatch')
    if record.get('sample_gammas')!=[str(gamma(s)) for s in SAMPLES[:4]]:
        raise ValueError('Sample binding mismatch')
    equations,lower,intervals=model(margin)
    if record.get('admittance_intervals')!=intervals or record.get('positive_stencil_lower_bound')!=str(lower):
        raise ValueError('Interval/stencil binding mismatch')
    result=check_refutation(equations,record['proof'])
    return {'status':'PASS','strict_error_lower_bound':str(margin),
        'family':'Direct-terminal parallel L/C, with arbitrary resistor-only network',
        'canonical_mixed_representatives_excluded':1,'all_remaining_mixed_representatives_excluded':False,
        'proof_consumer':result}


if __name__=='__main__':print(json.dumps(certificate(),indent=2))
