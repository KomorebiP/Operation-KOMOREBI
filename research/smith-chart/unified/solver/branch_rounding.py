"""Exact consequences of the written positive-real branch-rounding bound.
Author: Komorebi P. Physical comparison is not an imaginary-axis tolerance bound.
"""
from fractions import Fraction as F
import json
from pure_type_margins import SAMPLES
from two_reactive_margin import certificate as two_certificate

def certificate():
    old=two_certificate();base=F(old['margin']);fit=eta=F(1,10**7)
    per_edge=2*max(max(s,1/s) for s in SAMPLES)*eta
    assert per_edge==4*eta
    assert fit+per_edge<base and fit+2*per_edge<base
    return {'status':'PASS','fit_error_threshold':str(fit),'physical_value_interval':[str(eta),str(1/eta)],
      'one_reactive_rounding_error':str(per_edge),'two_reactive_rounding_error':str(2*per_edge),
      'accepted_two_reactive_margin':str(base),
      'strict_slacks':{'q3':str(base-fit-per_edge),'q4':str(base-fit-2*per_edge)},
      'q3_consequence':'Every reactive physical value lies in [1e-7,1e7] for any three-reactive fit with error <=1e-7.',
      'q4_consequence':'At least three of four reactive physical values lie in [1e-7,1e7] for any four-reactive fit with error <=1e-7.',
      'units':'Reference resistance one and the fixed normalized positive-real Laplace samples; these are dimensionless normalized L/C values.',
      'scope':'Arbitrary resistor count and placement; actual deletion/contraction and the accepted two-reactive closure margin. The general fixed-source finite-change/flow bound is proved in writing.',
      'non_claims':['No resistor-value bounds','No whole three/four-reactive separator','No imaginary-axis or hardware tolerance guarantee','No novel general sensitivity principle']}

def verify(record):
    if record!=certificate():raise ValueError('Rounding consequence binding differs')
    return {'status':'PASS'}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
