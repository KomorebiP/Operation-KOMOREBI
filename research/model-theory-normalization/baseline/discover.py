"""Certificate-producing observation discovery over Z/p^r Z.

Input: a complete finite-dimensional linear system, with all initial states
admissible. No enumeration of those states, answer basis, or hidden coordinates.
Output: an exact sufficient observation encoding, a minimal free coordinate
count for this all-initial-state linear encoding model, and checkable witnesses.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
import json
from typing import Any, Sequence
from chainring import is_prime, module_form, vector_matrix

SCHEMA = 'komorebi-observable-module-v0.2'

def canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def source_digest(spec: dict) -> str:
    return sha256(canonical(spec)).hexdigest()

def rowmul(v: Sequence[int], a: Sequence[Sequence[int]], m: int) -> list[int]:
    return [sum(v[i] * a[i][j] for i in range(len(v))) % m for j in range(len(a))]

def matvec(a: Sequence[Sequence[int]], x: Sequence[int], m: int) -> list[int]:
    return [sum(v * y for v, y in zip(row, x)) % m for row in a]

def validate_spec(spec: dict) -> tuple[int, int, int, int]:
    required={'schema','p','r','dimension','actions','observations','initial_interface','word_order'}
    if set(spec) != required or spec['schema'] != 'finite-linear-profile-v1':
        raise ValueError('wrong source schema/fields')
    p,r,d=spec['p'],spec['r'],spec['dimension']
    if type(p) is not int or not is_prime(p) or type(r) is not int or not 1 <= r <= 256:
        raise ValueError('prime p and precision 1..256 required')
    if type(d) is not int or not 1 <= d <= 32 or not spec['actions'] or not spec['observations']:
        raise ValueError('nonempty actions/observations and dimension 1..32 required')
    if spec['initial_interface'] != 'all_states' or spec['word_order'] != 'left_to_right':
        raise ValueError('this implementation certifies all initial states, left-to-right words')
    if len(spec['actions'])>16 or len(spec['observations'])>32:
        raise ValueError('declared operational cap exceeded, not a nonexistence result')
    m=p**r
    for a in spec['actions']:
        if len(a)!=d or any(len(row)!=d for row in a):raise ValueError('action shape')
    if any(len(row)!=d for row in spec['observations']):raise ValueError('observation shape')
    entries=[v for a in spec['actions'] for row in a for v in row]
    entries += [v for row in spec['observations'] for v in row]
    if any(type(v) is not int or not 0<=v<m for v in entries):raise ValueError('noncanonical ring value')
    return p,r,d,m

def observation_row(spec: dict, word: Sequence[int], j: int) -> list[int]:
    _,_,_,m=validate_spec(spec)
    row=list(spec['observations'][j])
    # run([a,b],x)=A_b A_a x, so the covector is o A_b A_a.
    for a in reversed(word):row=rowmul(row,spec['actions'][a],m)
    return row

def separating_delta(form, row: list[int], p: int, r: int, d: int) -> list[int]:
    """Witness that a new test is not implied by old tests, using chain-ring duality."""
    m=p**r
    if form is None:
        j=next(j for j,c in enumerate(row) if c)
        return [int(i==j) for i in range(d)]
    transformed=vector_matrix(row,form.V,m)
    for j,c in enumerate(transformed):
        weight=p**form.valuations[j] if j<form.count else m
        if c%weight:
            z=[0]*d
            z[j]=p**(r-form.valuations[j]) if j<form.count else 1
            return matvec(form.V,z,m)
    raise ArithmeticError('membership and separation inconsistent')

def discover(spec: dict, *, max_accepts: int | None = None) -> dict:
    p,r,d,m=validate_spec(spec)
    bound=r*d
    if max_accepts is None:max_accepts=bound
    if type(max_accepts) is not int or max_accepts<0:raise ValueError('nonnegative cap required')
    pending=deque((j,[],list(o)) for j,o in enumerate(spec['observations']))
    raw=[];tests=[];events=[];form=None;examined=0
    while pending:
        j,word,row=pending.popleft();examined+=1
        if not any(row) or (form is not None and form.coordinates(row) is not None):continue
        if len(raw)>=max_accepts:
            raise RuntimeError('observation module generation cap reached: unresolved')
        delta=separating_delta(form,row,p,r,d)
        old_length=0 if form is None else form.length
        # These checks audit the search; the independent checker recomputes them.
        if any(sum(a*b for a,b in zip(old,delta))%m for old in raw):raise ArithmeticError('old-test witness')
        if not sum(a*b for a,b in zip(row,delta))%m:raise ArithmeticError('new-test witness')
        raw.append(row);tests.append({'observation':j,'word':word})
        form=module_form(raw,p,r)
        if not old_length<form.length<=bound:raise ArithmeticError('strict finite module growth')
        events.append({'test':tests[-1], 'delta':delta})
        for a,matrix in enumerate(spec['actions']):
            pending.append((j,[a]+word,rowmul(row,matrix,m)))
    if form is None:
        basis=[];combos=[];V=[[int(i==j) for j in range(d)] for i in range(d)];W=V
        vals=[]
        def coords(row):
            if any(row):raise ArithmeticError('nonzero row in zero module')
            return []
    else:
        vals=list(form.valuations);t=form.count
        combos=[list(row) for row in form.U[:t]]
        basis=[[sum(c*raw[k][j] for k,c in enumerate(comb))%m for j in range(d)] for comb in combos]
        V=form.V;W=form.V_inverse
        def coords(row):
            c=form.coordinates(row)
            if c is None:raise ArithmeticError('closure did not hold')
            return list(c)
    transitions=[[coords(rowmul(row,a,m)) for row in basis] for a in spec['actions']]
    outputs=[coords(o) for o in spec['observations']]
    cert={'schema':SCHEMA,'source_sha256':source_digest(spec),'dimension':len(basis),
          'basis':basis,'raw_tests':tests,'basis_combinations':combos,
          'transitions':transitions,'observation_decoder':outputs,
          'smith_valuations':vals,'V':V,'V_inverse':W,
          'strict_growth_witnesses':events}
    return {'certificate':cert,'summary':{'source_dimension':d,'coordinate_count':len(basis),
       'quotient_p_digits':sum(r-s for s in vals),'source_p_digits':r*d,
       'accepted_tests':len(tests),'candidates_examined':examined,
       'max_test_word_length':max((len(t['word']) for t in tests),default=0),
       'state_enumeration_used':False,'scope':'all initial states; free linear encodings; not DFA minimization'}}

def encode(cert: dict, x: Sequence[int], modulus: int) -> list[int]:
    return matvec(cert['basis'],x,modulus)

def compressed_output(cert: dict, state: Sequence[int], word: Sequence[int], j: int, modulus: int) -> int:
    y=list(state)
    for a in word:y=matvec(cert['transitions'][a],y,modulus)
    return sum(c*v for c,v in zip(cert['observation_decoder'][j],y))%modulus
