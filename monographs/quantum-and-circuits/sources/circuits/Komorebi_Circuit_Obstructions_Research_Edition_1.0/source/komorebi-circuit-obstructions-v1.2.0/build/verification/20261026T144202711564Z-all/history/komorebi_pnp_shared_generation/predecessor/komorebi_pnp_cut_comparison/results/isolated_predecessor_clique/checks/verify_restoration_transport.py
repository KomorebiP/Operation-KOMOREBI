#!/usr/bin/env python3
"""Exact finite controls for restoration transport. Standard library only.
All gate controls/targets are distinct. No solver and no floating arithmetic.
Finite checks are not universal proof certificates; see RESEARCH_NOTE.md.
"""
from __future__ import annotations
import argparse, hashlib, json, random, sys
from pathlib import Path
from itertools import combinations

Gate = tuple

def validate(ops: list[Gate], width: int) -> None:
    for op in ops:
        assert op[0] in ('NOT','CNOT','TOF')
        assert len(op) == {'NOT':2,'CNOT':3,'TOF':4}[op[0]]
        assert len(set(op[1:])) == len(op)-1, ('repeated wire',op)
        assert all(0 <= i < width for i in op[1:])

def apply(ops: list[Gate], state: list[int]) -> list[int]:
    a=state.copy()
    for g in ops:
        if g[0]=='NOT': a[g[1]]^=1
        elif g[0]=='CNOT': a[g[2]]^=a[g[1]]
        else: a[g[3]]^=a[g[1]] & a[g[2]]
    return a

def tt_vars(n: int) -> list[int]:
    return [sum(((x>>i)&1)<<x for x in range(1<<n)) for i in range(n)]

def apply_tt(ops: list[Gate], state: list[int], n: int) -> list[int]:
    a=state.copy(); one=(1<<(1<<n))-1
    for g in ops:
        if g[0]=='NOT': a[g[1]]^=one
        elif g[0]=='CNOT': a[g[2]]^=a[g[1]]
        else: a[g[3]]^=a[g[1]] & a[g[2]]
    return a

def degree(table: int, n: int) -> int:
    a=[(table>>x)&1 for x in range(1<<n)]
    for i in range(n):
        for x in range(1<<n):
            if (x>>i)&1: a[x]^=a[x^(1<<i)]
    return max((x.bit_count() for x,v in enumerate(a) if v),default=-1)

def tofs(ops): return sum(g[0]=='TOF' for g in ops)

def is_passive(ops,y): return all(y not in g[1:-1] for g in ops)

def compile_boolean(n,gates):
    ops=[]
    for j,g in enumerate(gates):
        t=n+j; typ,*ab=g
        if typ=='NOT': ops += [('NOT',t),('CNOT',ab[0],t)]
        elif ab[0]==ab[1]: ops.append(('CNOT',ab[0],t))
        elif typ=='AND': ops.append(('TOF',ab[0],ab[1],t))
        elif typ=='OR': ops += [('CNOT',ab[0],t),('CNOT',ab[1],t),('TOF',ab[0],ab[1],t)]
        else: raise ValueError(g)
    forward=ops.copy(); y=n+len(gates)
    source=n+len(gates)-1 if gates else n-1
    ops += [('CNOT',source,y)] + forward[::-1]
    validate(ops,y+1)
    return ops,y+1,y

def eval_boolean(n,gates,x):
    v=[(x>>i)&1 for i in range(n)]
    for g in gates:
        if g[0]=='NOT': v.append(1^v[g[1]])
        elif g[0]=='AND': v.append(v[g[1]]&v[g[2]])
        else: v.append(v[g[1]]|v[g[2]])
    return v[-1]

def make_passive(ops,width,y):
    scratch=width
    renamed=[(g[0],*(scratch if i==y else i for i in g[1:])) for g in ops]
    ans=renamed+[('CNOT',scratch,y)]+renamed[::-1]
    validate(ans,width+1); assert is_passive(ans,y)
    assert len(ans)==2*len(ops)+1 and tofs(ans)==2*tofs(ops)
    return ans,width+1

def oracle_table(n,width,y,ops):
    v=tt_vars(n); initial=v+[0]*(width-n)
    assert y>=n
    zero=apply_tt(ops,initial,n); f=zero[y]
    assert all(zero[i]==initial[i] for i in range(width) if i!=y)
    initial[y]=(1<<(1<<n))-1
    one=apply_tt(ops,initial,n)
    assert one[y]==initial[y]^f
    assert all(one[i]==initial[i] for i in range(width) if i!=y)
    return f

def kth_oracle(k):
    y=2*k-2; width=y+1
    if k==2: return [('TOF',0,1,y)],width,y
    anc=list(range(k,2*k-2)); a=[('TOF',0,1,anc[0])]
    for i in range(2,k-1): a.append(('TOF',anc[i-2],i,anc[i-1]))
    ops=a+[('TOF',anc[-1],k-1,y)]+a[::-1]
    return ops,width,y

def check_passive(n,width,y,ops):
    assert is_passive(ops,y); validate(ops,width)
    f=oracle_table(n,width,y,ops); d=degree(f,n)
    w=sum(g[0]=='TOF' and g[-1]!=y for g in ops)
    before=0; state=tt_vars(n)+[0]*(width-n); checked=0
    one=(1<<(1<<n))-1
    contributions=0
    for g in ops:
        if g[-1]==y:
            h=one if g[0]=='NOT' else state[g[1]]
            if g[0]=='TOF': h &= state[g[2]]
            offset={'NOT':0,'CNOT':1,'TOF':2}[g[0]]
            bound=0 if g[0]=='NOT' else min(before,w-before)+offset
            assert degree(h,n)<=bound,(g,degree(h,n),bound)
            contributions^=h; checked+=1
        elif g[0]=='TOF': before+=1
        state=apply_tt([g],state,n)
    assert contributions==f
    if d>=2: assert tofs(ops)>=2*d-3
    return checked

def monomial_table(n,subset):
    v=tt_vars(n); a=(1<<(1<<n))-1
    for i in subset: a &= v[i]
    return a

def span_solution(vectors,target):
    basis={}
    for j,v in enumerate(vectors):
        witness=1<<j
        while v:
            k=v.bit_length()-1
            if k in basis: v^=basis[k][0];witness^=basis[k][1]
            else: basis[k]=(v,witness);break
    v=target; w=0
    while v:
        k=v.bit_length()-1
        if k not in basis: return None
        v^=basis[k][0];w^=basis[k][1]
    return w

def minimum_decoder_degree(D,n):
    one=(1<<(1<<n))-1
    active=[i for i,d in enumerate(D) if d]
    for k in range(n+1):
        terms=[(i,J,D[i]&monomial_table(n,J)) for i in active
               for r in range(k+1) for J in combinations(range(n),r)]
        sol=span_solution([q[2] for q in terms],one)
        if sol is None: continue
        lam=[0]*len(D)
        for j,(i,J,_) in enumerate(terms):
            if (sol>>j)&1:lam[i]^=monomial_table(n,J)
        val=0
        for a,d in zip(lam,D):val^=a&d
        assert val==one and all(degree(a,n)<=k for a in lam)
        return k,lam
    raise AssertionError('no covering decoder')

def check_cut(n,width,y,ops,cut,solve=True):
    f=oracle_table(n,width,y,ops)
    zero=tt_vars(n)+[0]*(width-n);one=zero.copy();one[y]=(1<<(1<<n))-1
    A=apply_tt(ops[:cut],zero,n);P1=apply_tt(ops[:cut],one,n)
    C=apply_tt(ops[cut:][::-1],zero,n);R1=apply_tt(ops[cut:][::-1],one,n)
    D=[a^b for a,b in zip(A,P1)];E=[a^b for a,b in zip(C,R1)]
    assert D==E
    assert all((a^c)==(f&d) for a,c,d in zip(A,C,D))
    union=0
    for d in D:union|=d
    assert union==(1<<(1<<n))-1
    a=tofs(ops[:cut]); b=tofs(ops[cut:])
    assert all(degree(z,n)<=a+1 for z in A)
    assert all(degree(z,n)<=b+1 for z in C)
    assert all(degree(z,n)<=min(a,b) for z in D)
    if solve:
        kappa,lam=minimum_decoder_degree(D,n)
        reconstructed=0
        for ll,u,v in zip(lam,A,C):reconstructed^=ll&(u^v)
        assert reconstructed==f
        assert degree(f,n)<=kappa+max(a,b)+1
        if abs(a-b)<=1: assert a+b+2*kappa>=2*degree(f,n)-3
        return kappa
    return None

def mask_encoder(n):
    y=n; terms=list(range(n+1,2*n+1));nextwire=2*n+1
    ops=[('TOF',y,i,terms[i]) for i in range(n)]
    OR=[];cur=terms[0]
    for i in range(1,n):
        t=nextwire;nextwire+=1
        OR += [('CNOT',cur,t),('CNOT',terms[i],t),('TOF',cur,terms[i],t)]
        cur=t
    ops += OR+[('CNOT',cur,y)]+OR[::-1]
    width=max(nextwire,2*n+1)
    validate(ops,width)
    assert tofs(ops)==3*n-2
    return ops,width,y,terms

def random_ops(rng,width,length,exclude=None):
    wires=[i for i in range(width) if i!=exclude]
    ops=[]
    for _ in range(length):
        count=rng.choice(range(1,min(3,len(wires))+1));args=rng.sample(wires,count)
        ops.append((['','NOT','CNOT','TOF'][count],*args))
    validate(ops,width)
    return ops

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    report={'status':'PASS','seed':7,'domain':'exact Boolean truth tables and GF(2) linear algebra',
            'not_claimed':['Lean verification','unrestricted optimal Toffoli count for monomials','P versus NP separation','exhaustive enumeration of all circuits']}
    rng=random.Random(7);comp_inputs=0;dup_source=0;bad_old_tofs=0;numcircuits=0
    control_cases=[]
    for n in range(2,5):
        for s in range(1,8):
            for rep in range(30):
                gates=[]
                for j in range(s):
                    op=rng.choice(['AND','OR','NOT'])
                    if op=='NOT':g=(op,rng.randrange(n+j))
                    else:g=(op,rng.randrange(n+j),rng.randrange(n+j))
                    if op!='NOT' and g[1]==g[2]:dup_source+=1;bad_old_tofs+=2
                    gates.append(g)
                ops,width,y=compile_boolean(n,gates)
                assert len(ops)<=6*s+1
                f=oracle_table(n,width,y,ops)
                for x in range(1<<n):
                    expected=eval_boolean(n,gates,x)
                    assert ((f>>x)&1)==expected
                    for b in (0,1):
                        inp=[(x>>i)&1 for i in range(n)]+[0]*(width-n);inp[y]=b
                        got=apply(ops,inp);end=inp.copy();end[y]^=expected
                        assert got==end;comp_inputs+=1
                numcircuits+=1
                if rep==0 and s<=3:control_cases.append((n,width,y,ops))
    report['predecessor_compiler_audit']={'source_circuits':numcircuits,'repeated_operand_source_gates':dup_source,
      'standard_Toffoli_violations_in_old_compute_uncompute':bad_old_tofs,'corrected_scalar_input_checks_both_target_values':comp_inputs,
      'repair':'AND(a,a) and OR(a,a) compiled as CNOT(a,target); all gate wires distinct'}
    report['passive_contribution_checks']=0
    masks=[];scalar=0
    for k in range(2,11):
        ops,width,y=kth_oracle(k);validate(ops,width)
        assert tofs(ops)==2*k-3
        report['passive_contribution_checks']+=check_passive(k,width,y,ops)
        for x in range(1<<k):
            for b in (0,1):
                inp=[(x>>i)&1 for i in range(k)]+[0]*(width-k);inp[y]=b
                expected=inp.copy();expected[y]^=int(x==(1<<k)-1)
                assert apply(ops,inp)==expected;scalar+=1
        masks.append({'k':k,'passive_optimal_Toffoli_count_proved':2*k-3})
    report['monomial_controls']={'family':masks,'scalar_inputs':scalar}
    # An arbitrary borrowed bit, not an initialized scratch bit.
    ops=[('TOF',0,1,3),('TOF',3,2,4),('TOF',0,1,3),('TOF',3,2,4)]
    validate(ops,5)
    for x in range(32):
        inp=[(x>>i)&1 for i in range(5)];expected=inp.copy();expected[4]^=inp[0]&inp[1]&inp[2]
        assert apply(ops,inp)==expected
    report['borrowed_cubic_control']={'gates':4,'all_full_register_inputs':32,'borrowed_wire':3}
    # More passive loops and arbitrary output-active identity excursions.
    rr=random.Random(271828);active_cases=[]
    for n in range(2,6):
        for rep in range(20):
            width=n+3;y=width-1
            P=random_ops(rr,width,5,exclude=y)
            controls=rr.sample([i for i in range(width) if i!=y],2)
            base=P+[('TOF',*controls,y)]+P[::-1]
            report['passive_contribution_checks']+=check_passive(n,width,y,base)
            excursion=random_ops(rr,width,4)
            j=rr.randrange(len(base)+1)
            active=base[:j]+excursion+excursion[::-1]+base[j:]
            oracle_table(n,width,y,active)
            active_cases.append((n,width,y,active))
    norm_inputs=0;cut_count=0;maxkap=0
    for n,width,y,ops in control_cases+active_cases:
        passive,w2=make_passive(ops,width,y);f=oracle_table(n,width,y,ops)
        assert oracle_table(n,w2,y,passive)==f
        report['passive_contribution_checks']+=check_passive(n,w2,y,passive)
        for x in range(1<<n):
            for b in (0,1):
                inp=[(x>>i)&1 for i in range(n)]+[0]*(w2-n);inp[y]=b
                end=inp.copy();end[y]^=(f>>x)&1
                assert apply(passive,inp)==end;norm_inputs+=1
        # Every gate cut for short controls; three specified cuts for decorated controls.
        cuts=range(len(ops)+1) if n<=3 else sorted(set((0,len(ops)//2,len(ops))))
        for cut in cuts:
            kap=check_cut(n,width,y,ops,cut)
            maxkap=max(maxkap,kap);cut_count+=1
    report['normal_form']={'circuits':len(control_cases)+len(active_cases),'scalar_input_checks':norm_inputs,
      'exact_cost':'2*S+1 gates and 2*T Toffolis'}
    report['midpoint_transport']={'cuts_with_exact_minimum_decoder_degree':cut_count,'max_kappa_in_generated_controls':maxkap,
      'checks':'all x for forward/backward difference identity, coverage, certificate and degree bounds'}
    maskreport=[]
    for n in range(1,9):
        P,width,y,terms=mask_encoder(n)
        initial=tt_vars(n)+[0]*(width-n);initial[y]=(1<<(1<<n))-1
        D=apply_tt(P,initial,n)
        zero=tt_vars(n)+[0]*(width-n);A=apply_tt(P,zero,n)
        D=[a^b for a,b in zip(A,D)]
        delta=1 # truth table of indicator x=0
        assert D[y]==delta
        assert all(D[j]==tt_vars(n)[i] for i,j in enumerate(terms))
        kap,lam=minimum_decoder_degree(D,n);assert kap==n-1
        whole=P+P[::-1];assert oracle_table(n,width,y,whole)==0
        assert check_cut(n,width,y,whole,len(P))==n-1
        scalar_cases=0
        for x in range(1<<n):
            for b in (0,1):
                inp=[(x>>i)&1 for i in range(n)]+[0]*(width-n);inp[y]=b
                mid=apply(P,inp);expected=inp.copy();expected[y]=b*int(x==0)
                for i,j in enumerate(terms):expected[j]=b*inp[i]
                assert mid==expected and apply(P[::-1],mid)==inp;scalar_cases+=1
        maskreport.append({'n':n,'prefix_gates':len(P),'prefix_Toffolis':tofs(P),'exact_kappa':kap,'scalar_inputs':scalar_cases})
    report['linear_cost_nonflat_transport']=maskreport
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results')
    main(parser.parse_args().out)
