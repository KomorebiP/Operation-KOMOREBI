"""Bounded-width Smith proposer with exact raw-row provenance.

UNTRUSTED producer: acceptance requires a separately checked complete trace.
At each accepted row the Smith input has at most dimension+1 rows, rather than
all earlier raw rows. The retained change-of-generator coefficients reconstruct
membership witnesses in the raw observation tests expected by the verifier.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Any
from chainring import ModuleForm, module_form, identity
from discover import validate_spec, rowmul, separating_delta, source_digest

@dataclass
class BoundedSpanProposer:
    p: int
    r: int
    d: int
    basis: list[list[int]] = field(default_factory=list)
    provenance: list[list[int]] = field(default_factory=list)
    raw_count: int = 0
    form: ModuleForm | None = None
    max_smith_rows: int = 0
    smith_calls: int = 0

    def membership(self, row: list[int]) -> list[int] | None:
        """Return raw-row coefficients, or None (not itself a certificate)."""
        if len(row) != self.d:
            raise ValueError('row shape')
        m = self.p ** self.r
        if self.form is None:
            return [0]*self.raw_count if not any(row) else None
        c = self.form.coordinates(row)
        if c is None:
            return None
        return [sum(c[i]*self.provenance[i][j] for i in range(len(c))) % m
                for j in range(self.raw_count)]

    def separator(self, row: list[int]) -> list[int]:
        return separating_delta(self.form, row, self.p, self.r, self.d)

    def insert(self, row: list[int]) -> None:
        m = self.p ** self.r
        X = self.basis + [row]
        self.max_smith_rows = max(self.max_smith_rows, len(X))
        self.smith_calls += 1
        f = module_form(X, self.p, self.r)
        # Express the temporary small matrix in the new raw observation family.
        B = [v+[0] for v in self.provenance] + [[0]*self.raw_count+[1]]
        new_count = self.raw_count+1
        new_prov = [[sum(f.U[i][h]*B[h][j] for h in range(len(X))) % m
                     for j in range(new_count)] for i in range(f.count)]
        new_basis = [[self.p**f.valuations[i]*v % m for v in f.V_inverse[i]]
                     for i in range(f.count)]
        if len(new_basis) > self.d:
            raise ArithmeticError('invalid Smith width')
        self.basis, self.provenance, self.raw_count = new_basis, new_prov, new_count
        # new_basis * V is already diagonal, so its row transform is identity.
        self.form = ModuleForm(self.p,self.r,self.d,f.valuations,identity(f.count),
                               f.V,f.V_inverse)


def certified_discover(source: dict[str, Any], *, candidate_cap: int | None = None
                       ) -> tuple[dict[str, Any], dict[str, int]]:
    p,r,d,m = validate_spec(source)
    bound = len(source['observations']) + len(source['actions'])*r*d
    cap = bound if candidate_cap is None else candidate_cap
    if type(cap) is not int or cap < 0:
        raise ValueError('candidate_cap must be a nonnegative integer')
    todo = deque(([],j,list(v)) for j,v in enumerate(source['observations']))
    tests, events = [], []
    backend = BoundedSpanProposer(p,r,d)
    while todo:
        if len(events) >= cap:
            raise RuntimeError('candidate cap reached with pending work: unresolved')
        w,j,v = todo.popleft()
        test = {'word':w,'observation':j}
        c = backend.membership(v)
        if c is not None:
            events.append({'test':test,'decision':'skip','coefficients':c})
        else:
            delta = backend.separator(v)
            events.append({'test':test,'decision':'accept','delta':delta})
            tests.append(test)
            backend.insert(v)
            for a,A in enumerate(source['actions']):
                todo.append(([a]+w,j,rowmul(v,A,m)))
    trace = {'schema':'complete-observation-queue-trace-v1',
             'source_sha256':source_digest(source),'events':events,
             'result':tests,'status':'complete'}
    stats = {'accepted':len(tests),'decisions':len(events),
             'max_smith_rows':backend.max_smith_rows,
             'smith_calls':backend.smith_calls,'max_smith_rows_bound':d+1,
             'final_basis_rows':len(backend.basis)}
    return trace, stats
