"""Proof-checked, task-independent compression of a finite synthesis search.

Finite observations propose arithmetic equations. A separate local proof checker
validates equational derivations. Ordered quotienting keeps the earliest original
AST, so deterministic counterexample-guided search has exactly the same proposals
and counterexamples. No evaluation of arbitrary Python or external actions.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import product
import hashlib
import json
from typing import Callable, Iterable

from synthesized_pruning import grammar, evaluate as old_evaluate, expr_size, expr_text

Expr = tuple
ARITH = ('+', 'min', 'max')
CMP = ('>', '>=', '==', '<', '<=')
SEMANTICS = 'exact-integer-arithmetic-total-pure-v1'
_BOOL = {'true': True, 'false': False}


def _num(s: str) -> bool:
    return isinstance(s, str) and (s.isdecimal() or (s.startswith('-') and s[1:].isdecimal()))


def sort_of(e: Expr) -> str:
    if not isinstance(e, tuple) or not e or not isinstance(e[0], str):
        raise ValueError('Not a typed arithmetic term.')
    if len(e) == 1:
        if e[0] in _BOOL:
            return 'bool'
        if e[0] in ('x', 'y', 'a', 'b', 'm', 'c') or _num(e[0]):
            return 'int'
        raise ValueError('Unknown atom.')
    if len(e) != 3 or e[0] not in ARITH + CMP:
        raise ValueError('Unknown syntax.')
    if sort_of(e[1]) != 'int' or sort_of(e[2]) != 'int':
        raise ValueError('An integer argument is required.')
    return 'int' if e[0] in ARITH else 'bool'


def value(e: Expr, ctx: dict[str, int], count: Counter | None = None):
    if count is not None:
        count['semantic_node_visits'] += 1
    if len(e) == 1:
        atom = e[0]
        if atom in _BOOL: return _BOOL[atom]
        if _num(atom): return int(atom)
        v = ctx[atom]
        if type(v) is not int: raise ValueError('Context values must be exact integers.')
        return v
    x = value(e[1], ctx, count); y = value(e[2], ctx, count)
    return {'+':lambda:x+y, 'min':lambda:min(x,y), 'max':lambda:max(x,y),
            '>':lambda:x>y, '>=':lambda:x>=y, '==':lambda:x==y,
            '<':lambda:x<y, '<=':lambda:x<=y}[e[0]]()


def key(e: Expr):
    # A finite comparison on finite syntax; it is not a semantic complexity score.
    if len(e) == 1: return (0, e[0])
    order = {'+':0, 'min':1, 'max':2, '>':3, '>=':4, '==':5, '<':6, '<=':7}
    return (1, order[e[0]], key(e[1]), key(e[2]))


def measure(e: Expr):
    return (expr_size(e), key(e))


def root_step(e: Expr, law: str) -> Expr:
    """Small trusted arithmetic axiom interface. Every side condition is checked."""
    sort_of(e)
    if len(e) != 3: raise ValueError('An axiom requires a binary root.')
    op, a, b = e
    if law == 'commute' and op in ARITH + ('==',):
        return (op, b, a)
    if law == 'zero' and op == '+' and (a == ('0',) or b == ('0',)):
        return b if a == ('0',) else a
    if law == 'idempotence' and op in ('min', 'max') and a == b:
        return a
    if law == 'dual' and op in ('<', '<='):
        return ('>' if op == '<' else '>=', b, a)
    if law == 'reflexive' and op in CMP and a == b:
        return ('true' if op in ('>=', '<=', '==') else 'false',)
    if law == 'constant' and len(a) == len(b) == 1 and _num(a[0]) and _num(b[0]):
        v = value(e, {})
        return ('true' if v is True else 'false',) if type(v) is bool else (str(v),)
    raise ValueError('Unsupported arithmetic axiom or unsatisfied premise.')


def _at(e: Expr, path: tuple[int,...]) -> Expr:
    for i in path:
        if len(e) != 3 or i not in (1,2): raise ValueError('Invalid proof position.')
        e=e[i]
    return e


def _replace(e: Expr, path: tuple[int,...], replacement: Expr) -> Expr:
    if not path: return replacement
    i=path[0]
    if i not in (1,2) or len(e)!=3: raise ValueError('Invalid proof position.')
    parts=list(e); parts[i]=_replace(parts[i], path[1:], replacement)
    return tuple(parts)


def trusted_normalize(e: Expr) -> tuple[Expr,list[dict]]:
    """Build, do not assume, a replayable arithmetic proof for a canonicalization."""
    sort_of(e); current=e; steps=[]
    def walk(path):
        nonlocal current
        node=_at(current,path)
        if len(node)==1:return
        walk(path+(1,));walk(path+(2,))
        while True:
            node=_at(current,path); chosen=None
            for law in ('constant','zero','idempotence','reflexive','dual','commute'):
                try:new=root_step(node,law)
                except ValueError:continue
                if measure(new)<measure(node):chosen=(law,new);break
            if chosen is None:return
            law,new=chosen
            current=_replace(current,path,new)
            steps.append({'path':list(path),'law':law})
            if len(new)==1:return
    walk(())
    return current,steps


def replay(start:Expr, steps:list[dict], expected:Expr, count:Counter|None=None) -> None:
    cur=start; sort_of(start);sort_of(expected)
    for entry in steps:
        if not isinstance(entry,dict) or set(entry)!={'path','law'}:
            raise ValueError('Malformed proof step.')
        path=tuple(entry['path']);node=_at(cur,path)
        if count is not None:count['checked_axiom_steps']+=1
        result=root_step(node,entry['law'])
        cur=_replace(cur,path,result)
    if cur!=expected:raise ValueError('Proof has the wrong endpoint.')
    if sort_of(cur)!=sort_of(start):raise ValueError('Proof changed sort.')


def equation_certificate(left:Expr,right:Expr) -> dict:
    if sort_of(left)!=sort_of(right):raise ValueError('Sort mismatch.')
    ln,lp=trusted_normalize(left);rn,rp=trusted_normalize(right)
    if ln!=rn:raise ValueError('This bounded prover did not prove the equation.')
    return {'semantics':SEMANTICS,'left':left,'right':right,'common':ln,'left_steps':lp,'right_steps':rp}


def validate_equation(cert:dict,count:Counter|None=None)->None:
    required={'semantics','left','right','common','left_steps','right_steps'}
    if not isinstance(cert,dict) or set(cert)!=required or cert['semantics']!=SEMANTICS:
        raise ValueError('Certificate is not bound to the supported semantics.')
    left,right,common=map(to_tuple,(cert['left'],cert['right'],cert['common']))
    if sort_of(left)!=sort_of(right):raise ValueError('Sort mismatch.')
    replay(left,cert['left_steps'],common,count);replay(right,cert['right_steps'],common,count)


def to_tuple(e):
    if not isinstance(e,(tuple,list)):raise ValueError('A term must be an array.')
    return tuple(to_tuple(x) if isinstance(x,(tuple,list)) else x for x in e)


def free_vars(e:Expr)->set[str]:
    if len(e)==1:return {e[0]} if e[0] in ('x','y') else set()
    return free_vars(e[1])|free_vars(e[2])


def match(pattern:Expr,term:Expr,bindings:dict)->bool:
    if len(pattern)==1 and pattern[0] in ('x','y'):
        if sort_of(term)!='int':return False
        v=pattern[0]
        if v in bindings:return bindings[v]==term
        bindings[v]=term;return True
    if len(pattern)!=len(term) or pattern[0]!=term[0]:return False
    return len(pattern)==1 or (match(pattern[1],term[1],bindings) and match(pattern[2],term[2],bindings))


def substitute(e:Expr,bindings:dict)->Expr:
    if len(e)==1:return bindings.get(e[0],e)
    return (e[0],substitute(e[1],bindings),substitute(e[2],bindings))


def discover_library(probe_values:tuple[int,...]=(1,2,3))->tuple[dict,dict]:
    """Infer equations without any downstream task label; verify every admission.

    All one-operation schemas over x,y,0,1 are probed. Equal probe signatures
    merely propose equations. A fixed local prover may accept or fail to prove.
    """
    atoms=(('x',),('y',),('0',),('1',))
    ints=atoms+(('2',),)+tuple((op,a,b) for op in ARITH for a in atoms for b in atoms)
    bools=(('false',),('true',))+tuple((op,a,b) for op in CMP for a in atoms for b in atoms)
    count=Counter();probes=tuple({'x':x,'y':y} for x,y in product(probe_values,repeat=2))
    equations=[];rejected=[]
    for terms in (ints,bools):
        classes=defaultdict(list)
        for term in terms:
            sig=tuple(value(term,p,count) for p in probes)
            classes[sig].append(term);count['probe_evaluations']+=len(probes)
        for terms_with_same_values in classes.values():
            for i,left in enumerate(terms_with_same_values):
                for right in terms_with_same_values[i+1:]:
                    count['proposed_equations']+=1
                    try:
                        cert=equation_certificate(left,right)
                        validate_equation(cert,count)
                        count['proof_generation_steps']+=len(cert['left_steps'])+len(cert['right_steps'])
                    except ValueError:
                        rejected.append((left,right));continue
                    equations.append(cert)
    raw={'semantics':SEMANTICS,'probe_values':list(probe_values),'equations':equations}
    serialized=json.dumps(raw,sort_keys=True,separators=(',',':'))
    report={'counters':dict(count),'accepted_equations':len(equations),'unproved_proposals':len(rejected),
            'schema_terms':len(ints)+len(bools),'probe_contexts':len(probes),
            'library_bytes':len(serialized.encode()),'library_sha256':hashlib.sha256(serialized.encode()).hexdigest(),
            'rejected_examples':rejected[:12],
            'scope':'Sample signatures propose, local integer equations authorize. No downstream target labels used.'}
    return raw,report


class LearnedNormalizer:
    def __init__(self,library:dict,counters:Counter|None=None):
        if library.get('semantics')!=SEMANTICS:raise ValueError('Library semantics mismatch.')
        self.count=Counter() if counters is None else counters
        self.rules=defaultdict(list)
        seen=set()
        for cert in library.get('equations',[]):
            validate_equation(cert,self.count)
            a,b=to_tuple(cert['left']),to_tuple(cert['right'])
            for left,right in ((a,b),(b,a)):
                if len(left)!=3 or not free_vars(right)<=free_vars(left):continue
                if (left,right) in seen:continue
                seen.add((left,right));self.rules[left[0]].append((left,right))
        self.count['installed_directed_rules']=len(seen)

    def normalize(self,e:Expr)->Expr:
        self.count['normalizer_node_visits']+=1
        if len(e)==1:return e
        cur=(e[0],self.normalize(e[1]),self.normalize(e[2]))
        # Every successful step decreases (size, structural order) and no step
        # introduces new atoms. For finite input syntax this strictly terminates.
        while len(cur)==3:
            changed=False
            for left,right in self.rules.get(cur[0],[]):
                self.count['schema_match_attempts']+=1
                env={}
                if not match(left,cur,env):continue
                candidate=substitute(right,env)
                if measure(candidate)<measure(cur):
                    cur=candidate;self.count['applied_rewrites']+=1;changed=True;break
            if not changed:break
        return cur


def ordered_quotient(programs:tuple[Expr,...],library:dict)->tuple[tuple[int,...],dict]:
    count=Counter();normalizer=LearnedNormalizer(library,count)
    first={};mapping=[];kept=[];norms=[]
    for i,p in enumerate(programs):
        n=normalizer.normalize(p);norms.append(n)
        if n not in first:first[n]=i;kept.append(i)
        mapping.append(first[n]);count['quotient_key_queries']+=1
    report={'grammar_count':len(programs),'retained_candidates':len(kept),'removed_candidates':len(programs)-len(kept),
            'representative_indices':mapping,'counters':dict(count),
            'grammar_sha256':hashlib.sha256(json.dumps(programs,separators=(',',':')).encode()).hexdigest(),
            'semantics':SEMANTICS,
            'normal_forms':norms}
    return tuple(kept),report


def cegis(programs:tuple[Expr,...],contexts:tuple[dict,...],labels:tuple[bool,...],indices:Iterable[int]|None=None)->dict:
    if not contexts or len(contexts)!=len(labels):raise ValueError('Finite target is empty or malformed.')
    count=Counter();examples=[];trace=[];winner=None
    for i in (range(len(programs)) if indices is None else indices):
        expr=programs[i];count['visited_candidates']+=1
        consistent=True
        for j in examples:
            count['example_evaluations']+=1
            if value(expr,contexts[j],count)!=labels[j]:consistent=False;break
        if not consistent:continue
        count['teacher_calls']+=1;bad=None
        for j,ctx in enumerate(contexts):
            count['teacher_evaluations']+=1
            if value(expr,ctx,count)!=labels[j]:bad=j;break
        if bad is None:
            winner=i;trace.append({'index':i,'outcome':'pass'});break
        if bad in examples:raise AssertionError('Retained counterexample was lost.')
        examples.append(bad);trace.append({'index':i,'outcome':'counterexample','context_index':bad})
    return {'winner_index':winner,'winner':None if winner is None else programs[winner],
            'trace':trace,'examples':examples,'counters':dict(count),
            'status':'finite_consistent' if winner is not None else 'grammar_exhausted'}


def eager_quotient(programs:tuple[Expr,...])->tuple[tuple[int,...],dict]:
    """Stronger supplied-equational-normalizer comparator, charged separately."""
    first={};indices=[];steps=0
    for i,e in enumerate(programs):
        n,proof=trusted_normalize(e);steps+=len(proof)
        if n not in first:first[n]=i;indices.append(i)
    return tuple(indices),{'retained_candidates':len(indices),'proof_generation_steps':steps,
                           'note':'Full supplied normalizer, not learned from trace signatures.'}


def verify_quotient(programs:tuple[Expr,...],library:dict,record:dict)->tuple[int,...]:
    """Bind a cached grammar quotient to the actual syntax and integer semantics."""
    if record.get('semantics')!=SEMANTICS:raise ValueError('Stale semantic contract.')
    digest=hashlib.sha256(json.dumps(programs,separators=(',',':')).encode()).hexdigest()
    if record.get('grammar_sha256')!=digest:raise ValueError('Stale grammar order or contents.')
    kept,fresh=ordered_quotient(programs,library)
    if fresh['representative_indices']!=record.get('representative_indices'):
        raise ValueError('Unsupported or non-earliest candidate representative.')
    return kept
