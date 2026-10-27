"""Independent imperative port of the v0.9 explicit arithmetic cost semantics.

The unit charges describe a stipulated eager scalar model, NOT CPython/Lean
instructions, elapsed time, allocations or bit operations. This Python port is
not verified extraction. The Lean evaluator and its proofs are authoritative.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Any, Sequence

@dataclass
class Meter:
    counts: Counter = field(default_factory=Counter)

    def charge(self, op: str, value: Any) -> Any:
        self.counts[op] += 1
        return value

    @property
    def units(self) -> int:
        return sum(self.counts.values())

    def add(self, a: int, b: int) -> int: return self.charge('integer_add', a+b)
    def sub(self, a: int, b: int) -> int: return self.charge('integer_sub', a-b)
    def mul(self, a: int, b: int) -> int: return self.charge('integer_mul', a*b)
    def div(self, a: int, b: int) -> int: return self.charge('integer_div', a//b)
    def rem(self, a: int, b: int) -> int: return self.charge('integer_rem', a%b)
    def abs(self, a: int) -> int: return self.charge('integer_abs', abs(a))
    def neg(self, a: int) -> int: return self.charge('integer_neg', -a)
    def zero(self, a: int) -> bool: return self.charge('zero_compare', a == 0)
    def nonneg(self, a: int) -> bool: return self.charge('sign_compare', a >= 0)
    def rmul(self, a: int, b: int, m: int) -> int: return self.charge('residue_mul', (a*b)%m)
    def radd(self, a: int, b: int, m: int) -> int: return self.charge('residue_add', (a+b)%m)


def euclid_coeff(a: int, b: int, meter: Meter) -> tuple[int, int]:
    """Stack implementation of the same recursion; terminal comparison is charged."""
    quotients = []
    while not meter.zero(b):
        rem = meter.rem(a,b)
        quotient = meter.div(a,b)
        quotients.append(quotient)
        a,b = b,rem
    s,t = 1,0
    for q in reversed(quotients):
        s,t = t,meter.sub(s,meter.mul(q,t))
    return s,t


def euclid_gcd(a: int, b: int, meter: Meter) -> int:
    while not meter.zero(b):
        a,b = b,meter.rem(a,b)
    return a


def signed_coeff(q: int, a: int, meter: Meter) -> tuple[int, int]:
    s,t = euclid_coeff(meter.abs(q),meter.abs(a),meter)
    sign = 1 if meter.nonneg(a) else -1
    return s,meter.mul(sign,t)


def _basis(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    n=len(rows)
    if any(len(r)!=n for r in rows): raise ValueError('square basis required')
    if any(type(v) is not int for r in rows for v in r): raise ValueError('integer basis required')
    if any(rows[i][i]<=0 or any(rows[i][j] for j in range(i)) for i in range(n)):
        raise ValueError('positive-pivot upper triangular basis required')
    return [list(r) for r in rows]


def coordinates(rows: Sequence[Sequence[int]], vector: Sequence[int], meter: Meter) -> list[int]|None:
    B=_basis(rows);n=len(B)
    if len(vector)!=n or any(type(v) is not int for v in vector): raise ValueError('invalid integer vector')
    v=list(vector);c=[]
    for i,row in enumerate(B):
        if not meter.zero(meter.rem(v[i],row[i])):return None
        ci=meter.div(v[i],row[i]);c.append(ci)
        for j in range(i+1,n):v[j]=meter.sub(v[j],meter.mul(ci,row[j]))
    return c


def residue(rows: Sequence[Sequence[int]], vector: Sequence[int], meter: Meter) -> list[int]:
    B=_basis(rows);n=len(B)
    if len(vector)!=n:raise ValueError('invalid vector dimension')
    v=list(vector)
    for i,row in enumerate(B):
        ci=meter.div(v[i],row[i]);v[i]=meter.rem(v[i],row[i])
        for j in range(i+1,n):v[j]=meter.sub(v[j],meter.mul(ci,row[j]))
    return v


def normalize(rows: Sequence[Sequence[int]], meter: Meter) -> list[list[int]]:
    B=_basis(rows);n=len(B)
    for i in range(n-1,-1,-1):
        # The lower basis has already been normalized.
        lower=[r[i+1:] for r in B[i+1:]]
        B[i][i+1:]=residue(lower,B[i][i+1:],meter)
    return B


def insert(rows: Sequence[Sequence[int]], vector: Sequence[int], meter: Meter) -> list[list[int]]:
    B=_basis(rows);n=len(B)
    if len(vector)!=n or any(type(v) is not int for v in vector):raise ValueError('invalid vector')
    v=list(vector)
    for i in range(n):
        row=B[i][:];q,a=row[i],v[i]
        # Deliberately distinct calls: neither the cost nor the work hides a gcd.
        g=euclid_gcd(meter.abs(q),meter.abs(a),meter)
        s,t=signed_coeff(q,a,meter)
        A=meter.div(a,g);Q=meter.div(q,g);minusA=meter.neg(A)
        out=[0]*n;out[i]=g
        for j in range(i+1,n):
            oldv=v[j]
            out[j]=meter.add(meter.mul(s,row[j]),meter.mul(t,oldv))
            v[j]=meter.add(meter.mul(minusA,row[j]),meter.mul(Q,oldv))
        B[i]=out
    return B


def update(rows: Sequence[Sequence[int]], vector: Sequence[int], meter: Meter) -> list[list[int]]:
    return normalize(insert(rows,vector,meter),meter)


def test_row(source: dict[str, Any], word: Sequence[int], observation: int, meter: Meter) -> list[int]:
    m=source['p']**source['r'];d=source['dimension']
    v=list(source['observations'][observation])
    for a in reversed(word):
        A=source['actions'][a];out=[]
        for j in range(d):
            acc=0
            for i in range(d-1,-1,-1):
                acc=meter.radd(meter.rmul(v[i],A[i][j],m),acc,m)
            out.append(acc)
        v=out
    return v


def units_bound(bits: int, dimension: int, fuel: int) -> int:
    B=bits+(2*bits+2)*dimension+1;d=dimension;F=fuel
    return d**3+F*(2*d*d*F+d**3+4*d*d+11*d+14*B*d+1)


def discover_costed(source: dict[str, Any], *, fuel: int|None=None) -> tuple[list[dict[str,Any]]|None,dict[str,Any]]:
    # Reuse the frozen source contract for normal positive-rank cases.
    from discover import validate_spec
    p,r,d,m=validate_spec(source)
    k=len(source['actions']);o=len(source['observations'])
    fuel=o+k*r*d+1 if fuel is None else fuel
    if type(fuel) is not int or fuel<0:raise ValueError('fuel must be a natural number')
    original_fuel=fuel
    meter=Meter();B=normalize([[m if i==j else 0 for j in range(d)] for i in range(d)],meter)
    initial_units=meter.units
    queue=deque(([],j) for j in range(o));accepted=[];decisions=0
    phases=Counter();stage_records=[]
    result=None
    while True:
        if fuel==0:break
        fuel-=1
        if not queue:result=accepted;break
        word,j=queue.popleft();decisions+=1
        before=meter.units;v=test_row(source,word,j,meter);phases['source']+=meter.units-before
        v=[meter.charge('residue_lift',x) for x in v]
        before=meter.units;c=coordinates(B,v,meter);member=meter.charge('option_test',c is not None)
        phases['membership']+=meter.units-before
        if not member:
            accepted.append({'word':word,'observation':j})
            before=meter.units;B=update(B,v,meter);u=meter.units-before;phases['updates']+=u
            stage_records.append({'word_length':len(word),'update_units':u})
            for a in range(k):queue.append(([a]+word,j))
    bits=(m-1).bit_length();bound=units_bound(bits,d,original_fuel)
    assert meter.units<=bound
    return result,{'units':meter.units,'unit_counts':dict(sorted(meter.counts.items())),
        'phase_units':dict(phases),'initial_units':initial_units,'decisions':decisions,
        'accepted':len(accepted),'success':result is not None,'fuel':original_fuel,
        'final_basis':B,'bound':bound,'bits':bits,'updates':stage_records}
