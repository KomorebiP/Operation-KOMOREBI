"""Witness-producing FIFO row discovery. The producer uses the unverified Smith
backend. Its complete queue trace is checked without importing that backend.
This is not a verified Python program; the generic Lean trace calculus validates
witnesses emitted in selected literal instances.
"""
from __future__ import annotations
from collections import deque
from typing import Any
from chainring import module_form
from discover import validate_spec, rowmul, separating_delta, source_digest


def traced_discover(source: dict[str, Any], *, candidate_cap: int | None = None) -> dict[str, Any]:
    p,r,d,m=validate_spec(source)
    bound=len(source['observations'])+len(source['actions'])*r*d
    if candidate_cap is None: candidate_cap=bound
    if type(candidate_cap) is not int or candidate_cap < 0:
        raise ValueError('candidate_cap must be nonnegative')
    todo=deque(([],j,list(v)) for j,v in enumerate(source['observations']))
    tests=[]; rows=[]; events=[]; form=None
    while todo:
        if len(events)>=candidate_cap:
            raise RuntimeError('candidate cap reached while pending queue is nonempty: unresolved')
        word,j,v=todo.popleft()
        coords=(() if not any(v) else None) if form is None else form.coordinates(v)
        test={'word':word,'observation':j}
        if coords is not None:
            coeff=[sum(coords[i]*form.U[i][h] for i in range(len(coords)))%m
                   for h in range(len(rows))] if form is not None else []
            events.append({'test':test,'decision':'skip','coefficients':coeff})
        else:
            delta=separating_delta(form,v,p,r,d)
            events.append({'test':test,'decision':'accept','delta':delta})
            tests.append(test); rows.append(v)
            form=module_form(rows,p,r)
            for a,A in enumerate(source['actions']):
                todo.append(([a]+word,j,rowmul(v,A,m)))
    return {'schema':'complete-observation-queue-trace-v1','source_sha256':source_digest(source),
            'events':events,'result':tests,'status':'complete'}
