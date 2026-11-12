"""Terminal-C shunting arbitrary RL: exact seven-sample margin refutation.

Author: Komorebi P. The classical RL characterization gives a Stieltjes
admittance; the positive finite-sum shape is checked in CapShuntMargin.lean.
"""
from fractions import Fraction as F
import json
from pure_type_margins import P,Q,SAMPLES,gamma
from parallel_refutation import var,const,add,sub,scale,square,dump,digest,check_refutation

WEIGHTS=(1,-6,15,-20,15,-6,1)
MARGIN=F(1,100000)
FAMILY='A direct-terminal capacitor in parallel with any finite positive ordinary RL network'

def equations():
    eqs={};shape=const(0);upper=F(0);intervals=[]
    for k,(w,s) in enumerate(zip(WEIGHTS,SAMPLES)):
        g=gamma(s)
        if g-MARGIN<=-1:raise ValueError('Cayley interval reaches the short face')
        lo=(1-g-MARGIN)/(1+g+MARGIN);hi=(1-g+MARGIN)/(1+g-MARGIN)
        intervals.append([str(lo),str(hi)])
        y=var('y'+str(k));t=var('slack'+str(k))
        shape=add(shape,scale(y,w));upper+=w*(hi if w>0 else lo)
        linear=sub(const(hi),y) if w>0 else sub(y,const(lo))
        eqs['box_'+str(k)]=sub(linear,square(t))
    if upper>=0:raise ValueError('Stencil upper bound does not exclude zero')
    eqs['shape']=sub(shape,square(var('shape_slack')))
    return eqs,-upper,intervals

def certificate():
    eqs,eta,intervals=equations()
    proof={'format':'komorebi-rational-refutation-v1','equations_sha256':digest(eqs),
      'squares':[{'weight':str(F(abs(w))/eta),'polynomial':dump(var('slack'+str(k)))} for k,w in enumerate(WEIGHTS)]+
        [{'weight':str(1/eta),'polynomial':dump(var('shape_slack'))}],
      'multipliers':[{'equation':'box_'+str(k),'polynomial':dump(const(F(abs(w))/eta))} for k,w in enumerate(WEIGHTS)]+
        [{'equation':'shape','polynomial':dump(const(1/eta))}]}
    return {'format':'komorebi-shunt-capacitor-RL-margin-v1','physical_family':FAMILY,
      'target':{'P':list(P),'Q':list(Q)},'margin':str(MARGIN),
      'sample_gammas':[str(gamma(s)) for s in SAMPLES],
      'admittance_intervals':intervals,'negative_stencil_upper_bound':str(-eta),
      'shape_lemma':'SmithCapShuntMargin.shape','proof':proof}

def verify(record):
    eqs,eta,intervals=equations()
    expected=certificate()
    if {k:v for k,v in record.items() if k!='proof'}!={k:v for k,v in expected.items() if k!='proof'}:
        raise ValueError('Physical class, target, shape, sample or interval binding mismatch')
    return {'status':'PASS','strict_sample_error_lower_bound':str(MARGIN),'physical_family':FAMILY,
      'proof_consumer':check_refutation(eqs,record['proof']),
      'scope':'The terminal-C/arbitrary-RL class, including its finite and open/short limits as stated; no all-mixed exclusion.'}

def covered(graph):
    capacitors=[(u,v) for kind,u,v in graph if kind=='C']
    return len(capacitors)==1 and set(capacitors[0])=={0,1}

if __name__=='__main__':
    record=certificate();verify(record);print(json.dumps(record,indent=2))
