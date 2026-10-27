#!/usr/bin/env python3
"""Exact rational branch-and-bound with a separately checked proof tree.

The solver is untrusted. The Python checker replays a structural certificate;
Lean proves soundness of that same tree contract. No powerset enumeration is
performed in production generation, checking or input echo. Worst-case search
and proof size remain exponential. All external inputs use exact rational cells.
"""
from __future__ import annotations
from typing import Any
from fractions import Fraction as F
from pathlib import Path
import argparse, json, re
from repair_certificates import (Mat, InvalidData, require, read_json, canonical,
    digest, emit_matrix, _integer, MAX_BYTES)
from rational_menu import (linear_alternative, mask_matrix, members, subset,
    cost, lean_set, ResourceLimit)

SCHEMA='komorebi.repair.branch-menu.v0.5.0'
MAX_CANDIDATES=24
MAX_NODES=8191
MAX_TABLE=4096
MAX_COST=10**9


def problem(D:Mat,E:Mat,R:Mat,weights:list[int],admitted:list[int]|None=None)->dict[str,Any]:
    p={'schema':SCHEMA,'kind':'branch_menu','D':D.to_wire(),'E':E.to_wire(),
       'R':R.to_wire(),'costs':weights,'admissible_masks':admitted}
    parse_problem(p);return p


def parse_problem(p:Any)->tuple[Mat,Mat,Mat,list[int],list[int]|None]:
    require(type(p)is dict and set(p)=={'schema','kind','D','E','R','costs','admissible_masks'},'Invalid branch problem keys')
    require(p['schema']==SCHEMA and p['kind']=='branch_menu','Wrong branch schema')
    D,E,R=(Mat.from_wire(p[k]) for k in ('D','E','R'))
    require(D.rows==E.rows==R.rows,'Target dimensions differ')
    if E.cols>MAX_CANDIDATES:raise ResourceLimit('Candidate resource limit exceeded')
    w=p['costs'];a=p['admissible_masks']
    require(type(w)is list and len(w)==E.cols,'Wrong weight count')
    for c in w:require(0<=_integer(c)<=MAX_COST,'Cost must be a bounded nonnegative integer')
    if a is not None:
        require(type(a)is list,'Admissibility must be null (all) or an exact list')
        if len(a)>MAX_TABLE:raise ResourceLimit('Admissibility table resource limit')
        for mask in a:require(0<=_integer(mask)<1<<E.cols,'Admissible mask out of range')
        require(a==sorted(set(a)),'Admissible masks must be sorted and unique')
    return D,E,R,w,a


def admitted(mask:int,table:list[int]|None)->bool:
    return table is None or mask in table


def interval_excluded(lo:int,hi:int,table:list[int]|None)->bool:
    return table is not None and not any(subset(lo,t) and subset(t,hi) for t in table)


def construct(p:dict[str,Any],trace:list[str]|None=None,*,max_nodes:int=MAX_NODES,
              max_linear_trials:int=MAX_NODES,stats:dict[str,Any]|None=None)->dict[str,Any]:
    D,E,R,weights,table=parse_problem(p);q=E.cols;full=(1<<q)-1
    for b in (max_nodes,max_linear_trials):require(type(b)is int and b>=0,'Budget must be a nonnegative integer')
    if max_nodes>MAX_NODES:raise ResourceLimit('Requested node budget exceeds guardrail')
    metrics={'visited_nodes':0,'linear_trials':0,'cache_hits':0,'incumbent_updates':0,
             'bound_leaves':0,'separator_leaves':0,'inadmissible_leaves':0,'splits':0,
             'candidate_count':q,'subset_universe_size':1<<q,'max_depth':0}
    cache:dict[int,tuple[str,Mat]]={};best:int|None=None;bestX:Mat|None=None
    def emit(text:str)->None:
        if trace is not None:trace.append(text)
    def solve(mask:int)->tuple[str,Mat]:
        if mask in cache:metrics['cache_hits']+=1;return cache[mask]
        if metrics['linear_trials']>=max_linear_trials:raise ResourceLimit('Linear trial budget exhausted')
        metrics['linear_trials']+=1
        ans=linear_alternative(D.join(E.columns(members(mask,q))),R);cache[mask]=ans
        emit(f'  LINEAR mask={mask} status={ans[0]} witness={ans[1].display()}')
        return ans
    def visit(lo:int,hi:int,depth:int)->dict[str,Any]:
        nonlocal best,bestX
        if metrics['visited_nodes']>=max_nodes:raise ResourceLimit('Search node budget exhausted')
        metrics['visited_nodes']+=1;metrics['max_depth']=max(metrics['max_depth'],depth)
        emit(f'NODE {metrics["visited_nodes"]} depth={depth} lo={lo} hi={hi} '
             f'cost_lo={cost(lo,weights)} incumbent={None if best is None else cost(best,weights)}')
        if interval_excluded(lo,hi,table):
            metrics['inadmissible_leaves']+=1;emit('  LEAF inadmissible (original table)')
            return {'type':'inadmissible'}
        if best is not None and cost(lo,weights)>=cost(best,weights):
            metrics['bound_leaves']+=1;emit('  LEAF bound (nonnegative additive costs)')
            return {'type':'bound'}
        status,X=solve(hi)
        if status=='infeasible':
            metrics['separator_leaves']+=1;emit('  LEAF separator (entire upper interval infeasible)')
            return {'type':'separator','Y':X.to_wire()}
        if admitted(lo,table):
            status,X=solve(lo)
            if status=='feasible':
                if best is None or cost(lo,weights)<cost(best,weights):
                    best,bestX=lo,X;metrics['incumbent_updates']+=1
                    emit(f'  INCUMBENT selected={members(best,q)} cost={cost(best,weights)}')
                metrics['bound_leaves']+=1;return {'type':'bound'}
        require(hi!=lo,'Unreachable complete interval without a valid leaf')
        # Cheapest unresolved column first. The heuristic is not trusted.
        j=min(members(hi&~lo,q),key=lambda j:(weights[j],j));metrics['splits']+=1
        include=visit(lo|(1<<j),hi,depth+1)
        exclude=visit(lo,hi&~(1<<j),depth+1)
        return {'type':'split','j':j,'exclude':exclude,'include':include}
    try:tree=visit(0,full,0)
    finally:
        if stats is not None:stats.update(metrics)
    c={'schema':SCHEMA,'kind':'no_admissible_repair' if best is None else 'optimal_menu',
       'problem_sha256':digest(p),'tree':tree}
    if best is not None:
        assert bestX is not None
        vals=[[F(0) for _ in range(R.cols)] for _ in range(q)]
        for i,j in enumerate(members(best,q)):vals[j]=list(bestX.data[D.cols+i])
        c.update(selection=best,cost=cost(best,weights),
                 U=bestX.select_rows(list(range(D.cols))).to_wire(),W=Mat.of(vals,R.cols).to_wire())
    checked=check_certificate(p,c)
    emit(f'RESULT {c["kind"]} cost={c.get("cost")} metrics={json.dumps(metrics,sort_keys=True)}')
    emit(f'INDEPENDENT_PYTHON_CHECK {json.dumps(checked,sort_keys=True)}')
    return c


def decode_certificate(p:dict[str,Any],c:Any)->tuple[Mat,Mat,list[Mat],int]:
    """Validate shapes, wire cells, tree schema and original-input binding only."""
    require(len(canonical(c)) <= MAX_BYTES, 'Certificate size resource limit')
    D,E,R,w,table=parse_problem(p);q=E.cols
    require(type(c)is dict,'Certificate must be an object')
    kind=c.get('kind');keys={'schema','kind','problem_sha256','tree'}
    if kind=='optimal_menu':keys|={'selection','cost','U','W'}
    else:require(kind=='no_admissible_repair','Unknown outcome')
    require(set(c)==keys and c['schema']==SCHEMA,'Invalid certificate schema/keys')
    require(c['problem_sha256']==digest(p),'Certificate bound to different original input')
    if kind=='optimal_menu':
        sel=_integer(c['selection'],nonnegative=True);require(sel<1<<q,'Selection out of range')
        require(_integer(c['cost'],nonnegative=True)==cost(sel,w),'Wrong cost')
        U,W=Mat.from_wire(c['U']),Mat.from_wire(c['W'])
        require((U.rows,U.cols)==(D.cols,R.cols),'Wrong U shape')
        require((W.rows,W.cols)==(q,R.cols),'Wrong W shape')
    else:U,W=Mat.zero(D.cols,R.cols),Mat.zero(q,R.cols)
    count=0;ys=[]
    def walk(node:Any,depth:int)->None:
        nonlocal count
        count+=1
        if count>MAX_NODES or depth>q:raise ResourceLimit('Certificate tree size/depth limit')
        require(type(node)is dict,'Tree node must be an object')
        t=node.get('type')
        if t in ('bound','inadmissible'):require(set(node)=={'type'},'Unexpected leaf keys')
        elif t=='separator':
            require(set(node)=={'type','Y'},'Invalid separator keys');Y=Mat.from_wire(node['Y'])
            require((Y.rows,Y.cols)==(1,D.rows),'Wrong separator shape');ys.append(Y)
        elif t=='split':
            require(set(node)=={'type','j','exclude','include'},'Split must contain both branches and only their data')
            require(0<=_integer(node['j'])<q,'Split index out of range')
            walk(node['exclude'],depth+1);walk(node['include'],depth+1)
        else:raise InvalidData('Unknown proof-tree node')
    walk(c['tree'],0)
    return U,W,ys,count


def check_certificate(p:dict[str,Any],c:Any)->dict[str,Any]:
    D,E,R,w,table=parse_problem(p);U,W,ys,count=decode_certificate(p,c);q=E.cols
    if c['kind']=='optimal_menu':
        sel=c['selection'];require(admitted(sel,table),'Selected menu is forbidden')
        require(D@U+mask_matrix(E,sel)@W==-R,'Original repair equations fail')
        threshold=cost(sel,w)
    else:threshold=None
    leaves={'bound':0,'separator':0,'inadmissible':0};splits=0
    def check(node:dict[str,Any],lo:int,hi:int)->None:
        nonlocal splits
        t=node['type'];require(subset(lo,hi),'Malformed interval')
        if t=='bound':
            require(threshold is not None,'Cost leaf cannot certify impossibility')
            require(threshold<=cost(lo,w),'False cost lower bound');leaves[t]+=1
        elif t=='inadmissible':
            require(interval_excluded(lo,hi,table),'An admitted subset survives this interval');leaves[t]+=1
        elif t=='separator':
            Y=Mat.from_wire(node['Y'])
            require(Y@D==Mat.zero(1,D.cols),'Separator changes original correction')
            require(Y@mask_matrix(E,hi)==Mat.zero(1,q),'Separator fails on upper interval')
            require(Y@R!=Mat.zero(1,R.cols),'Separator hides the original residual');leaves[t]+=1
        else:
            j=node['j'];require(bool(hi&(1<<j)) and not bool(lo&(1<<j)),'Split index is not unresolved')
            splits+=1;check(node['exclude'],lo,hi&~(1<<j));check(node['include'],lo|(1<<j),hi)
    check(c['tree'],0,(1<<q)-1)
    return {'status':'PYTHON_BRANCH_CERTIFICATE_VALID','kind':c['kind'],
            'nodes':count,'splits':splits,'leaves':leaves,'subset_universe_size':1<<q,
            'checker_enumerates_powerset':False}


def _safe_name(ns:str)->None:
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',ns)is not None,'Unsafe namespace')


def emit_input(p:dict[str,Any],ns:str)->str:
    _safe_name(ns);D,E,R,w,table=parse_problem(p);q=E.cols
    ws='(fun j => Fin.elim0 j)' if q==0 else '!['+', '.join(map(str,w))+']'
    a='none' if table is None else '(some ['+', '.join(lean_set(x,q) for x in table)+'])'
    lines=['import KomorebiRepair.BranchCertificate','-- Original input, emitted independently of witnesses.',
           '-- Canonical JSON SHA256: '+digest(p),'set_option autoImplicit false','set_option maxRecDepth 100000',
           'open KomorebiRepair.RationalCertificates','namespace '+ns,
           *emit_matrix('D',D),*emit_matrix('E',E),*emit_matrix('R',R),
           f'def weights : Fin {q} → ℕ := {ws}',
           f'def admitted : Option (List (Finset (Fin {q}))) := {a}',
           f'def original : BranchProblem {D.rows} {D.cols} {q} {R.cols} := ⟨D, E, R, weights, admitted⟩',
           'theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel',
           'end '+ns]
    return '\n'.join(lines)+'\n'


def emit_certificate(p:dict[str,Any],c:dict[str,Any],ns:str,module:str,*,check:bool=True)->str:
    _safe_name(ns);require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]*',module)is not None,'Unsafe module')
    D,E,R,w,a=parse_problem(p);U,W,ys,count=decode_certificate(p,c)
    if check:check_certificate(p,c)
    lines=['import '+module,'-- Certificate contains no replacement problem data.',
           'set_option autoImplicit false','set_option maxRecDepth 100000','set_option maxHeartbeats 5000000',
           'open KomorebiRepair.RationalCertificates','namespace '+ns];valid=[];node_id=0;y_id=0
    if c['kind']=='optimal_menu':
        lines+=emit_matrix('U',U)+emit_matrix('W',W);valid+=['WireMatrixValid wireU','WireMatrixValid wireW']
        lines.append(f'def chosen : Finset (Fin {E.cols}) := {lean_set(c["selection"],E.cols)}')
    def tree(node:dict[str,Any])->str:
        nonlocal node_id,y_id
        t=node['type']
        if t=='split':
            ex=tree(node['exclude']);inc=tree(node['include']);expr=f'.split {node["j"]} {ex} {inc}'
        elif t=='separator':
            name=f'Y{y_id}';y_id+=1
            lines.extend(emit_matrix(name,Mat.from_wire(node['Y'])));valid.append('WireMatrixValid wire'+name)
            expr='.separator '+name
        else:expr='.'+t
        name=f'node{node_id}';node_id+=1
        lines.append(f'def {name} : BranchTree {D.rows} {E.cols} := {expr}')
        return name
    root=tree(c['tree']);lines.append(f'def tree : BranchTree {D.rows} {E.cols} := {root}')
    lines.append('theorem certificate_encoding_valid : '+(' ∧ '.join(valid) or 'True')+' := by decide +kernel')
    if c['kind']=='optimal_menu':
        lines+=['theorem certificate_checked : checkTreeOptimal original chosen U W tree = true := by decide +kernel',
          'theorem certified : original.original.allowed chosen = true ∧ Equation original.original chosen U W ∧',
          f'    ∀ T : Finset (Fin {E.cols}), original.original.allowed T = true → Feasible original.original T → original.original.cost chosen ≤ original.original.cost T :=',
          '  checkTreeOptimal_sound original chosen U W tree certificate_checked',
          f'theorem declared_cost : original.original.cost chosen = {c["cost"]} := by decide +kernel',
          'theorem original_equations_checked : D * U + masked original.original chosen * W = -R := certified.2.1']
    else:
        lines+=['theorem certificate_checked : checkTreeNoRepair original tree = true := by decide +kernel',
          f'theorem certified : ∀ T : Finset (Fin {E.cols}), original.original.allowed T = true → ¬ Feasible original.original T :=',
          '  checkTreeNoRepair_sound original tree certificate_checked']
    lines+=['end '+ns];return '\n'.join(lines)+'\n'


def emit_echo(p:dict[str,Any],ns:str,module:str)->str:
    _safe_name(ns);parse_problem(p)
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]*',module)is not None,'Unsafe module')
    return f'import {module}\nopen KomorebiRepair.RationalCertificates\n#eval IO.println (branchInputJson {ns}.original)\n'


def check_echo(p:dict[str,Any],echo:Any)->bool:
    D,E,R,w,table=parse_problem(p)
    require(type(echo)is dict and set(echo)=={'D','E','R','costs','admissible_masks'},'Bad branch echo')
    for k in ('D','E','R'):require(echo[k]==p[k]['entries'],'Original '+k+' echo mismatch')
    require(echo['costs']==w and all(type(x)is int for x in echo['costs']),'Cost echo mismatch')
    expected=None if table is None else [members(t,E.cols) for t in table]
    actual=echo['admissible_masks']
    if expected is not None:
        require(type(actual)is list and all(type(row)is list for row in actual),'Bad admissibility echo shape')
        require(all(type(j)is int and 0<=j<E.cols for row in actual for j in row),'Bad admissibility echo index')
    require(actual==expected,'Admissibility echo mismatch')
    return True


def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--max-nodes',type=int,default=MAX_NODES)
    ap.add_argument('--max-linear-trials',type=int,default=MAX_NODES);args=ap.parse_args()
    if args.output.exists():ap.error('Output must be a new directory')
    args.output.mkdir(parents=True);trace=[];stats={}
    try:
        p=read_json(args.input);c=construct(p,trace,max_nodes=args.max_nodes,max_linear_trials=args.max_linear_trials,stats=stats)
        (args.output/'input.json').write_bytes(canonical(p));(args.output/'certificate.json').write_bytes(canonical(c))
        result=check_certificate(p,c);result['search_statistics']=stats
        print(result['status'])
        rc=0
    except Exception as e:
        result={'status':'UNRESOLVED','error':str(e),'search_statistics':stats};print('UNRESOLVED: '+str(e));rc=2
    (args.output/'trace.txt').write_text('\n'.join(trace)+'\n', encoding="utf-8");(args.output/'result.json').write_bytes(canonical(result));return rc

if __name__=='__main__':raise SystemExit(main())
