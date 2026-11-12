"""Terminal-L shunting arbitrary RC: a checked rational margin refutation.

Author: Komorebi P. The physical-to-shape rule is proved in the written chapter
using the classical RC characterization; its finite sum inequality is in Lean.
The unchanged polynomial consumer checks the resulting five-square identity.
"""
from fractions import Fraction as F
import json
from parallel_refutation import model,WEIGHTS,P,Q,SAMPLES,gamma
from exact_polynomials import var,const,add,square,dump,digest,check_refutation

FAMILY='A direct-terminal inductor in parallel with any finite positive ordinary RC network'

def equations(margin):
    eqs,beta,intervals=model(margin)
    # Physical shape is now <=0 instead of =0. Its extra real slack square
    # keeps the zero face and every strictly negative shape value.
    eqs['shape']=add(eqs['shape'],square(var('shape_slack')))
    return eqs,beta,intervals

def certificate():
    margin=F(1,1000);eqs,beta,intervals=equations(margin)
    proof={'format':'komorebi-rational-refutation-v1','equations_sha256':digest(eqs),
      'squares':[{'weight':str(abs(w)/beta),'polynomial':dump(var('slack'+str(k)))} for k,w in enumerate(WEIGHTS)]+
        [{'weight':str(1/beta),'polynomial':dump(var('shape_slack'))}],
      'multipliers':[{'equation':'box_'+str(k),'polynomial':dump(const(abs(w)/beta))} for k,w in enumerate(WEIGHTS)]+
        [{'equation':'shape','polynomial':dump(const(-1/beta))}]}
    record={'format':'komorebi-shunt-inductor-RC-margin-v1','target':{'P':list(P),'Q':list(Q)},
      'margin':str(margin),'sample_gammas':[str(gamma(s)) for s in SAMPLES[:4]],
      'admittance_intervals':intervals,'positive_stencil_lower_bound':str(beta),
      'physical_family':FAMILY,'shape_lemma':'SmithShuntMargin.shape','proof':proof}
    verify(record)
    return record

def verify(record):
    if record.get('format')!='komorebi-shunt-inductor-RC-margin-v1' or record.get('physical_family')!=FAMILY:
        raise ValueError('Physical family binding mismatch')
    if record.get('shape_lemma')!='SmithShuntMargin.shape':raise ValueError('Shape rule binding mismatch')
    if record.get('target')!={'P':list(P),'Q':list(Q)} or record.get('margin')!='1/1000':
        raise ValueError('Target/margin binding mismatch')
    eqs,beta,intervals=equations(F(1,1000))
    if record.get('admittance_intervals')!=intervals or record.get('positive_stencil_lower_bound')!=str(beta):
        raise ValueError('Cayley interval binding mismatch')
    if record.get('sample_gammas')!=[str(gamma(s)) for s in SAMPLES[:4]]:
        raise ValueError('Sample binding mismatch')
    return {'status':'PASS','strict_sample_error_lower_bound':'1/1000','physical_family':FAMILY,
      'proof_consumer':check_refutation(eqs,record['proof']),
      'scope':'All finite RC subnetworks and component values in the stated shunt-L class; no global mixed-RLC exclusion.'}

def covered(graph):
    inductors=[(u,v) for kind,u,v in graph if kind=='L']
    return len(inductors)==1 and set(inductors[0])=={0,1}

if __name__=='__main__':print(json.dumps(certificate(),indent=2))
