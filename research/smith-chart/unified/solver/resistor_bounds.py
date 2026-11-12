"""Endpoint resistor lower bounds, separate from reactive degree. Author: Komorebi P.

The universal endpoint theorem is a written physical-graph proof. This module
checks its exact hypotheses and combines it with an unchanged circuit consumer.
"""
from first_order import normalize,rational_text
from composition_certificate import verify_circuit


def endpoint_bound(target):
    P,Q=normalize(target)
    low=P[0]/Q[0] if Q[0] else None
    high=P[-1]/Q[-1] if len(P)==len(Q) else 0 if len(P)<len(Q) else None
    positive=[v for v in (low,high) if v is not None and v>0]
    bound=2 if len(positive)==2 and low!=high else 1 if positive else 0
    return {'format':'komorebi-endpoint-resistor-bound-v1',
        'target':{'P':rational_text(P),'Q':rational_text(Q)},
        'limits':{'zero':str(low) if low is not None else 'pole',
                  'infinity':str(high) if high is not None else 'pole'},
        'resistors_at_least':bound,
        'model':'Finite positive ordinary uncoupled transformer-free RLC; arbitrary reactive count',
        'proof_basis':'Written endpoint deletion/contraction theorem; selected finite contraction identities have Lean companions'}


def verify_bound(record,expected_target):
    expected=endpoint_bound(expected_target)
    if record!=expected:raise ValueError('Endpoint bound is not exactly bound to the expected target')
    return expected['resistors_at_least']


def verify_resistor_minimum(certificate,target,budget):
    upper=verify_circuit(certificate,expected_target=target,expected_budget=budget)
    lower=endpoint_bound(target);bound=verify_bound(lower,target)
    if upper['resistors']<bound:raise ValueError('Witness contradicts the endpoint theorem')
    return {'status':'PASS','lower_bound':bound,'upper_bound':upper['resistors'],
        'resistor_minimum_certified':upper['resistors']==bound,'endpoint_certificate':lower,
        'scope':'Exact witness replay plus application of the written universal endpoint theorem; no unstated reactive-minimum or complete formal coverage'}
