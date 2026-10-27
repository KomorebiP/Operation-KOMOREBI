#!/usr/bin/env python3
"""Exact rational finite-menu certificates and an untrusted Lean exporter.

No rational coefficient enumeration. Exact elimination supplies primal or dual
witnesses. A finite coverage check, and ultimately Lean, validates each answer.
This is a bounded research implementation, not a scalable general optimizer.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from typing import Any
import argparse, json, re
from repair_certificates import (Mat, InvalidData, require, rational_pair, read_json,
    canonical, digest, emit_matrix, _integer, MAX_BYTES)

SCHEMA = 'komorebi.repair.rational-menu.v0.4.0'
MAX_CANDIDATES = 8
MAX_COST = 10**9

class ResourceLimit(InvalidData):
    """Budget exhaustion means UNRESOLVED, never a no-repair theorem."""

def members(mask: int, q: int) -> list[int]:
    return [j for j in range(q) if mask & (1 << j)]

def subset(a: int, b: int) -> bool:
    return a & ~b == 0

def problem(D: Mat, E: Mat, R: Mat, costs: list[int],
            admissible_masks: list[int] | None = None) -> dict[str, Any]:
    p = {'schema': SCHEMA, 'kind': 'rational_menu', 'D': D.to_wire(),
         'E': E.to_wire(), 'R': R.to_wire(), 'costs': costs,
         'admissible_masks': list(range(1 << E.cols)) if admissible_masks is None else admissible_masks}
    parse_problem(p)
    return p

def parse_problem(p: Any) -> tuple[Mat, Mat, Mat, list[int], list[int]]:
    require(type(p) is dict and set(p) ==
            {'schema','kind','D','E','R','costs','admissible_masks'}, 'Invalid menu problem keys')
    require(p['schema'] == SCHEMA and p['kind'] == 'rational_menu', 'Wrong menu schema')
    D,E,R = (Mat.from_wire(p[k]) for k in ('D','E','R'))
    require(D.rows == E.rows == R.rows, 'Original target dimensions differ')
    if E.cols > MAX_CANDIDATES: raise ResourceLimit('Candidate limit exceeded')
    costs = p['costs']; allowed = p['admissible_masks']
    require(type(costs) is list and len(costs) == E.cols, 'Wrong candidate cost count')
    for x in costs: require(0 <= _integer(x) <= MAX_COST, 'Cost out of bounds')
    require(type(allowed) is list, 'Admissible masks must be a list')
    for x in allowed: require(0 <= _integer(x) < (1 << E.cols), 'Admissible mask out of bounds')
    require(allowed == sorted(set(allowed)), 'Admissible masks must be unique and sorted')
    return D,E,R,costs,allowed

def cost(mask: int, weights: list[int]) -> int:
    return sum(weights[j] for j in members(mask,len(weights)))

def mask_matrix(E: Mat, mask: int) -> Mat:
    return Mat(E.rows,E.cols,tuple(tuple(x if mask & (1<<j) else F(0)
             for j,x in enumerate(row)) for row in E.data))

def linear_alternative(B: Mat, R: Mat) -> tuple[str, Mat]:
    """Return X with BX=-R, or Y with YB=0 and YR != 0.

    Row reduction is restricted to coefficient columns. The left transformation
    is retained, so an inconsistent row gives an explicit rational separator.
    Every returned identity is rechecked outside the elimination loop.
    """
    require(B.rows == R.rows, 'Alternative target mismatch')
    m,n,s=B.rows,B.cols,R.cols
    a=[list(row) for row in B.data]
    rhs=[[-x for x in row] for row in R.data]
    left=[list(row) for row in Mat.eye(m).data]
    piv=[]; k=0
    for j in range(n):
        if k==m: break
        i=next((i for i in range(k,m) if a[i][j]),None)
        if i is None: continue
        for z in (a,rhs,left): z[k],z[i]=z[i],z[k]
        v=a[k][j]
        for z in (a,rhs,left): z[k]=[x/v for x in z[k]]
        for i in range(m):
            if i==k: continue
            v=a[i][j]
            if v:
                for z in (a,rhs,left): z[i]=[x-v*y for x,y in zip(z[i],z[k])]
        piv.append(j); k+=1
    for i in range(k,m):
        j=next((j for j in range(s) if rhs[i][j]),None)
        if j is not None:
            # rhs=-left*R, normalize YR at the chosen residual to +1.
            Y=Mat.of([[x/(-rhs[i][j]) for x in left[i]]],m)
            require(Y@B == Mat.zero(1,n) and Y@R != Mat.zero(1,s), 'Bad dual witness')
            return 'infeasible',Y
    vals=[[F(0) for _ in range(s)] for _ in range(n)]
    for i,j in enumerate(piv): vals[j]=rhs[i]
    X=Mat.of(vals,s)
    require(B@X == -R, 'Bad primal witness')
    return 'feasible',X

def construct(p: dict[str, Any], trace: list[str] | None = None,
              *, max_trials: int | None = None) -> dict[str, Any]:
    D,E,R,weights,allowed=parse_problem(p);q=E.cols
    if max_trials is not None:
        require(type(max_trials) is int and max_trials>=0,'Invalid trial budget')
        if (1<<q)>max_trials: raise ResourceLimit('Exhaustive menu budget exceeded')
    outcomes={}; admitted=set(allowed)
    for mask in range(1<<q):
        st,X=linear_alternative(D.join(E.columns(members(mask,q))),R)
        outcomes[mask]=(st,X)
        if trace is not None:
            trace.append(f'mask={mask}; selected={members(mask,q)}; admitted={mask in admitted}; '
                         f'cost={cost(mask,weights)}; linear_status={st}; witness={X.display()}')
    feasible=[x for x in allowed if outcomes[x][0]=='feasible']
    c={'schema':SCHEMA,'kind':'','problem_sha256':digest(p),'blocks':[]}
    if feasible:
        chosen=min(feasible,key=lambda x:(cost(x,weights),x))
        X=outcomes[chosen][1];sel=members(chosen,q)
        U=X.select_rows(list(range(D.cols)))
        vals=[[F(0) for _ in range(R.cols)] for _ in range(q)]
        for i,j in enumerate(sel): vals[j]=list(X.data[D.cols+i])
        W=Mat.of(vals,R.cols)
        c.update(kind='optimal_menu',selection=chosen,cost=cost(chosen,weights),U=U.to_wire(),W=W.to_wire())
        required={x for x in allowed if cost(x,weights)<cost(chosen,weights)}
    else:
        c['kind']='no_admissible_repair';required=set(allowed)
    # Maximal infeasible supersets are reusable separation blocks. They may
    # themselves be disallowed. Their impossibility is a linear statement.
    infeasible=[x for x in outcomes if outcomes[x][0]=='infeasible']
    maximal=[x for x in infeasible if not any(x!=y and subset(x,y) for y in infeasible)]
    uncovered=set(required)
    while uncovered:
        block=max(maximal,key=lambda b:(sum(subset(x,b) for x in uncovered),b.bit_count(),-b))
        hit={x for x in uncovered if subset(x,block)}
        require(bool(hit),'No valid separator cover for required alternatives')
        c['blocks'].append({'mask':block,'Y':outcomes[block][1].to_wire()})
        uncovered-=hit
    if trace is not None:
        trace.extend([f'outcome={c["kind"]}; cheaper/admitted rejection obligations={len(required)}; '
                      f'separation blocks={len(c["blocks"])}',
                      *[f'block={b["mask"]}; covers={sorted(x for x in required if subset(x,b["mask"]))}; '
                        f'Y={Mat.from_wire(b["Y"]).display()}' for b in c['blocks']]])
    check_certificate(p,c)
    return c

def decode_certificate(p: dict[str, Any], c: Any) -> tuple[Mat,Mat,list[tuple[int,Mat]]]:
    require(len(canonical(c)) <= MAX_BYTES, 'Certificate size resource limit')
    D,E,R,weights,allowed=parse_problem(p)
    require(type(c) is dict,'Certificate must be an object')
    kind=c.get('kind')
    keys={'schema','kind','problem_sha256','blocks'}
    if kind=='optimal_menu': keys|={'selection','cost','U','W'}
    else: require(kind=='no_admissible_repair','Unknown certificate kind')
    require(set(c)==keys,'Invalid menu certificate keys')
    require(c['schema']==SCHEMA,'Wrong certificate schema')
    require(c['problem_sha256']==digest(p),'Certificate is bound to a different original problem')
    require(type(c['blocks']) is list and len(c['blocks']) <= (1<<E.cols),'Invalid block count')
    seen=set();blocks=[]
    for b in c['blocks']:
        require(type(b) is dict and set(b)=={'mask','Y'},'Invalid block keys')
        mask=_integer(b['mask'],nonnegative=True)
        require(mask<(1<<E.cols) and mask not in seen,'Duplicate or out-of-range block')
        seen.add(mask);Y=Mat.from_wire(b['Y']);require((Y.rows,Y.cols)==(1,D.rows),'Wrong separator shape')
        blocks.append((mask,Y))
    if kind=='optimal_menu':
        sel=_integer(c['selection'],nonnegative=True)
        require(sel<(1<<E.cols),'Selected mask out of bounds')
        require(_integer(c['cost'],nonnegative=True)==cost(sel,weights),'Wrong claimed cost')
        U,W=Mat.from_wire(c['U']),Mat.from_wire(c['W'])
        require((U.rows,U.cols)==(D.cols,R.cols),'Wrong original coefficient shape')
        require((W.rows,W.cols)==(E.cols,R.cols),'Wrong menu coefficient shape')
    else: U,W=Mat.zero(D.cols,R.cols),Mat.zero(E.cols,R.cols)
    return U,W,blocks

def check_certificate(p: dict[str, Any], c: Any) -> dict[str, Any]:
    D,E,R,weights,allowed=parse_problem(p);U,W,blocks=decode_certificate(p,c)
    for mask,Y in blocks:
        require(Y@D==Mat.zero(1,D.cols),'Separator changes original corrections')
        require(Y@mask_matrix(E,mask)==Mat.zero(1,E.cols),'Separator does not annihilate its block')
        require(Y@R!=Mat.zero(1,R.cols),'Separator fails to detect an original residual')
    if c['kind']=='optimal_menu':
        sel=c['selection'];require(sel in allowed,'Selected menu is not admissible')
        require(D@U+mask_matrix(E,sel)@W==-R,'Original repair equations failed')
        required=[x for x in allowed if cost(x,weights)<cost(sel,weights)]
    else: required=allowed
    for x in required:
        require(any(subset(x,b) for b,Y in blocks),f'Missing rejection coverage for mask {x}')
    return {'status':'PYTHON_MENU_CERTIFICATE_VALID','kind':c['kind'],
            'required_rejections':len(required),'separation_blocks':len(blocks),
            'admissible_menus':len(allowed)}

def lean_set(mask: int,q: int) -> str:
    return '{'+', '.join(map(str,members(mask,q)))+'}'

def _safe_namespace(ns: str) -> None:
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',ns) is not None,'Unsafe namespace')

def emit_input(p: dict[str, Any], ns: str) -> str:
    _safe_namespace(ns);D,E,R,weights,allowed=parse_problem(p);q=E.cols
    w='(fun j => Fin.elim0 j)' if q==0 else '!['+', '.join(map(str,weights))+']'
    lines=['import KomorebiRepair.RationalMenuCover','-- Independently emitted original problem.',
           '-- Canonical input SHA256: '+digest(p),'set_option autoImplicit false',
           'set_option maxRecDepth 100000','open KomorebiRepair.RationalCertificates','namespace '+ns,
           *emit_matrix('D',D),*emit_matrix('E',E),*emit_matrix('R',R),
           f'def weights : Fin {q} → ℕ := {w}',
           f'def admitted : List (Finset (Fin {q})) := ['+', '.join(lean_set(x,q) for x in allowed)+']',
           f'def original : Problem {D.rows} {D.cols} {q} {R.cols} :=',
           '  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩',
           'theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel',
           'end '+ns]
    return '\n'.join(lines)+'\n'

def emit_certificate(p: dict[str, Any],c: dict[str, Any],ns: str,module: str,*,check: bool=True) -> str:
    _safe_namespace(ns);require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]*',module) is not None,'Unsafe module')
    D,E,R,weights,allowed=parse_problem(p);U,W,blocks=decode_certificate(p,c)
    if check:check_certificate(p,c)
    lines=['import '+module,'-- Untrusted witnesses; the original matrices and constraints are imported.',
           'set_option autoImplicit false','set_option maxRecDepth 100000',
           'set_option maxHeartbeats 5000000','open KomorebiRepair.RationalCertificates','namespace '+ns]
    valid=[]
    if c['kind']=='optimal_menu':
        lines+=emit_matrix('U',U)+emit_matrix('W',W)
        valid+=['WireMatrixValid wireU','WireMatrixValid wireW']
        lines+=[f'def chosen : Finset (Fin {E.cols}) := {lean_set(c["selection"],E.cols)}']
    for i,(mask,Y) in enumerate(blocks):
        lines+=emit_matrix('Y'+str(i),Y);valid.append('WireMatrixValid wireY'+str(i))
    lines+=[f'def blocks : List (SeparationBlock {D.rows} {E.cols}) := ['+
            ', '.join(f'({lean_set(mask,E.cols)}, Y{i})' for i,(mask,Y) in enumerate(blocks))+']',
            'theorem certificate_encoding_valid : '+(' ∧ '.join(valid) or 'True')+' := by decide +kernel']
    if c['kind']=='optimal_menu':
        lines+=['theorem certificate_checked : checkCoveredOptimal original chosen U W blocks = true := by decide +kernel',
                'theorem certified : original.allowed chosen = true ∧ Equation original chosen U W ∧',
                f'    ∀ T : Finset (Fin {E.cols}), original.allowed T = true → Feasible original T → original.cost chosen ≤ original.cost T :=',
                '  checkCoveredOptimal_sound original chosen U W blocks certificate_checked',
                f'theorem declared_cost : original.cost chosen = {c["cost"]} := by decide +kernel',
                'theorem original_equations_checked : D * U + masked original chosen * W = -R := certified.2.1']
    else:
        lines+=['theorem certificate_checked : checkCoveredNoRepair original blocks = true := by decide +kernel',
                f'theorem certified : ∀ T : Finset (Fin {E.cols}), original.allowed T = true → ¬ Feasible original T :=',
                '  checkCoveredNoRepair_sound original blocks certificate_checked']
    lines+=['end '+ns];return '\n'.join(lines)+'\n'

def emit_echo(p: dict[str, Any],ns: str,module: str) -> str:
    _safe_namespace(ns);parse_problem(p)
    return '\n'.join(['import '+module,'open KomorebiRepair.RationalCertificates',
        f'#eval IO.println (menuProblemJson {ns}.original)',''])

def check_echo(p: dict[str, Any], echo: Any) -> bool:
    D,E,R,weights,allowed=parse_problem(p)
    require(type(echo) is dict and set(echo)=={'D','E','R','menus'},'Bad Lean input echo')
    for k in ['D','E','R']: require(echo[k]==p[k]['entries'],'Original '+k+' echo mismatch')
    seen=set()
    require(type(echo['menus']) is list and len(echo['menus'])==(1<<E.cols),'Incomplete menu echo')
    for row in echo['menus']:
        require(type(row) is dict and set(row)=={'selected','allowed','cost'},'Bad menu echo row')
        sel=row['selected'];require(type(sel) is list,'Bad selection echo')
        for j in sel: require(type(j) is int and 0<=j<E.cols,'Bad echo index')
        require(sel==sorted(set(sel)),'Bad echo ordering')
        mask=sum(1<<j for j in sel);require(mask not in seen,'Duplicate echo menu');seen.add(mask)
        require(type(row['allowed']) is bool and row['allowed']==(mask in allowed),'Admissibility echo mismatch')
        require(type(row['cost']) is int and row['cost']==cost(mask,weights),'Cost echo mismatch')
    return True

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    a=sub.add_parser('solve');a.add_argument('input',type=Path);a.add_argument('output',type=Path);a.add_argument('--trace',type=Path);a.add_argument('--max-trials',type=int)
    a=sub.add_parser('check');a.add_argument('input',type=Path);a.add_argument('certificate',type=Path)
    a=sub.add_parser('export');a.add_argument('input',type=Path);a.add_argument('certificate',type=Path);a.add_argument('output_dir',type=Path);a.add_argument('--namespace',default='ExportedMenu')
    args=ap.parse_args()
    try:
        p=read_json(args.input)
        if args.command=='solve':
            trace=[];c=construct(p,trace,max_trials=args.max_trials);args.output.write_bytes(canonical(c))
            if args.trace:args.trace.write_text('\n'.join(trace)+'\n', encoding="utf-8")
            print(json.dumps(check_certificate(p,c)))
        else:
            c=read_json(args.certificate);result=check_certificate(p,c)
            if args.command=='check':print(json.dumps(result))
            else:
                args.output_dir.mkdir(parents=True,exist_ok=False)
                (args.output_dir/'Input.lean').write_text(emit_input(p,args.namespace), encoding="utf-8")
                (args.output_dir/'Certificate.lean').write_text(emit_certificate(p,c,args.namespace,'Input'), encoding="utf-8")
                (args.output_dir/'Echo.lean').write_text(emit_echo(p,args.namespace,'Input'), encoding="utf-8")
                print('Exported sources. No Lean acceptance is claimed until compilation and replay.')
        return 0
    except (InvalidData,ValueError,OSError,KeyError) as e:
        print(json.dumps({'status':'UNRESOLVED','error':str(e)}));return 2

if __name__=='__main__':raise SystemExit(main())
