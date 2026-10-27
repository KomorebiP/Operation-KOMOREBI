"""Small exact companion checks for output-relative grounding and Bayesian memory.

The manuscript supplies the proofs. These finite checks use rational arithmetic
and F2; they neither train an agent nor establish universal results by sampling.
Matrix storage here is row-major, unlike the retained first-draft helper.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parents[1]


def cast(x, prime=None):
    return int(x) % prime if prime else F(x)


def dot(x, y, prime=None):
    value = sum((a*b for a,b in zip(x,y)), F(0) if prime is None else 0)
    return value % prime if prime else value


def mv(A, v, prime=None):
    return tuple(dot(row,v,prime) for row in A)


def rowmul(row, A, prime=None):
    return tuple(dot(row,col,prime) for col in zip(*A))


def rank_basis(rows, n, prime=None):
    """RREF row basis, including the empty/zero-dimensional subspace."""
    data = [[cast(x,prime) for x in row] for row in rows]
    if any(len(row)!=n for row in data):
        raise ValueError('Row dimension mismatch')
    r=0
    for col in range(n):
        pivot = next((j for j in range(r,len(data)) if data[j][col]),None)
        if pivot is None: continue
        data[r],data[pivot]=data[pivot],data[r]
        inv = pow(data[r][col], -1, prime) if prime else 1/data[r][col]
        data[r] = [cast(x*inv,prime) for x in data[r]]
        for j in range(len(data)):
            if j != r and data[j][col]:
                fac=data[j][col]
                data[j]=[cast(x-fac*y,prime) for x,y in zip(data[j],data[r])]
        r += 1
        if r==len(data): break
    return tuple(tuple(row) for row in data[:r])


def kernel(rows,n,prime=None):
    basis=rank_basis(rows,n,prime)
    pivots=[next(j for j,x in enumerate(row) if x) for row in basis]
    result=[]
    for free in range(n):
        if free in pivots: continue
        v=[cast(0,prime) for _ in range(n)];v[free]=cast(1,prime)
        for row,pivot in zip(basis,pivots): v[pivot]=cast(-row[free],prime)
        result.append(tuple(v))
    return tuple(result)


def in_span(v,basis,prime=None):
    return len(rank_basis(list(basis)+[v],len(v),prime)) == len(rank_basis(basis,len(v),prime))


def observable_rows(maps,Q,prime=None):
    """Span Q A_w over all words; finite rank closure is the certificate."""
    n=len(maps[0]); basis=rank_basis(Q,n,prime); rounds=0
    while True:
        nxt=rank_basis(list(basis)+[rowmul(r,A,prime) for r in basis for A in maps],n,prime)
        if nxt==basis: return basis,rounds
        basis=nxt;rounds+=1
        if rounds>n: raise AssertionError('Row-space closure did not terminate')


def pair_rows(candidate, reference, Q, prime=None):
    n=len(reference[0]); zero=(0,)*n
    blocks=[]
    for A,B in zip(candidate,reference):
        blocks.append(tuple(tuple(row)+zero for row in A)+tuple(zero+tuple(row) for row in B))
    C=[tuple(q)+tuple(-x for x in q) for q in Q]
    return observable_rows(blocks,C,prime)


def output_initial_basis(models,Q,prime=None):
    n=len(models[0][0]); rows=[]
    for model in models:
        rb,_=pair_rows(model,models[0],Q,prime)
        rows += [tuple(cast(row[j]+row[n+j],prime) for j in range(n)) for row in rb]
    return kernel(rows,n,prime)


def discrepancy_span(models,prime=None):
    reference=models[0];n=len(reference[0]);cols=[]
    for model in models:
        for T,A in zip(model,reference):
            for j in range(n): cols.append(tuple(cast(T[i][j]-A[i][j],prime) for i in range(n)))
    basis=rank_basis(cols,n,prime);rounds=0
    while True:
        nxt=rank_basis(list(basis)+[mv(A,v,prime) for A in reference for v in basis],n,prime)
        if nxt==basis:return basis,rounds
        basis=nxt;rounds+=1
        if rounds>n:raise AssertionError('Discrepancy closure did not terminate')


def reachable(maps,L,prime=None):
    n=len(maps[0]);basis=rank_basis(L,n,prime)
    while True:
        nxt=rank_basis(list(basis)+[mv(A,v,prime) for A in maps for v in basis],n,prime)
        if nxt==basis:return basis
        basis=nxt


def predictor_dimension(maps,Q,L,prime=None):
    W=reachable(maps,L,prime);O,_=observable_rows(maps,Q,prime)
    # The rank of the observation map restricted to W equals dim W-dim N.
    image=[tuple(dot(row,v,prime) for row in O) for v in W]
    return len(rank_basis(image,len(O),prime)),W


def words(k,h):
    for depth in range(h+1):yield from product(range(k),repeat=depth)


def apply(maps,v,word,prime=None):
    for a in word:v=mv(maps[a],v,prime)
    return v


def matrices(n,prime=2):
    for values in product(range(prime),repeat=n*n):
        yield tuple(tuple(values[n*i:n*(i+1)]) for i in range(n))


class Checks:
    def __init__(self): self.groups=[];self.current=None
    def group(self,name,domain):
        self.current={'name':name,'domain':domain,'assertions':0};self.groups.append(self.current)
    def check(self,condition,message):
        if not condition:raise AssertionError(self.current['name']+': '+message)
        self.current['assertions']+=1


def compositions(total,parts):
    if parts==1:
        yield (total,);return
    for x in range(total+1):
        for rest in compositions(total-x,parts-1):yield (x,)+rest


def aggregate(mu,partition):
    return tuple(sum((mu[j] for j in cell),F(0)) for cell in partition)


def posterior(mu,likelihood):
    z=dot(mu,likelihood)
    if z==0:return z,None
    return z,tuple(a*b/z for a,b in zip(mu,likelihood))


def joint_moment(mu,target,likelihoods,word,y):
    value=F(0)
    for i,mass in enumerate(mu):
        if target[i]!=y:continue
        for b in word:mass*=likelihoods[b][i]
        value+=mass
    return value


def run():
    c=Checks();start=time.perf_counter()
    mats=list(matrices(2)); vectors=list(product((0,1),repeat=2)); qr=[(v,) for v in vectors]
    c.group('pair_closure_one_action',
            'Every ordered pair of 2x2 matrices over F2, every scalar linear observation including zero, every initial vector; direct words of lengths 0..4.')
    for A,B in product(mats,repeat=2):
        models=((A,),(B,))
        for Q in qr:
            rows,rounds=pair_rows(models[1],models[0],Q,2)
            c.check(rounds<=4,'rank termination')
            for v in vectors:
                paired=all(dot(row,v+v,2)==0 for row in rows)
                direct=all(mv(Q,apply((A,),v,w,2),2)==mv(Q,apply((B,),v,w,2),2)
                           for w in words(1,4))
                c.check(paired==direct,'paired kernel versus direct fixed words')

    c.group('pair_closure_two_actions',
            'Two fixed models with two actions chosen from four explicit 2x2 F2 matrices; all 256 families, all four scalar observations and four initial vectors; words through length four.')
    bank=[((0,0),(0,0)),((1,0),(0,1)),((0,1),(0,0)),((0,0),(1,0))]
    ww=list(words(2,4))
    for A0,A1,B0,B1 in product(bank,repeat=4):
        models=((A0,A1),(B0,B1))
        for Q in qr:
            rows,_=pair_rows(models[1],models[0],Q,2)
            for v in vectors:
                c.check(all(dot(row,v+v,2)==0 for row in rows)==
                        all(mv(Q,apply(models[0],v,w,2),2)==mv(Q,apply(models[1],v,w,2),2) for w in ww),
                        'multi-action finite word closure')

    c.group('unrestricted_calibration_no_enlargement',
            'V=F2^2; U=span(e1); every possible calibrated first column, all four linear completions, every nonzero scalar Q and every vector; horizons one through four.')
    U=set(((0,0),(1,0)))
    for col in vectors:
        models=tuple((A,) for A in mats if tuple(A[i][0] for i in range(2))==col)
        core=U.copy()
        for h in range(1,5):
            for Q in qr[1:]:
                for v in vectors:
                    ref=[mv(Q,apply(models[0],v,w,2),2) for w in words(1,h)]
                    same=all([mv(Q,apply(M,v,w,2),2) for w in words(1,h)]==ref for M in models)
                    c.check(same==(v in core),'nonzero output finite horizon')
            core={v for v in U if mv(models[0][0],v,2) in core}

    c.group('whole_space_quotient',
            'Every pair of 2x2 F2 matrices; all scalar outputs; uncertainty closure versus all initial-condition fixed-model agreement and quotient kernel invariance.')
    for A,B in product(mats,repeat=2):
        models=((A,),(B,));E,rounds=discrepancy_span(models,2)
        c.check(rounds<=2,'uncertainty closure bound')
        for Q in qr:
            criterion=all(mv(Q,v,2)==(0,) for v in E)
            I=output_initial_basis(models,Q,2)
            c.check(criterion==(len(I)==2),'all-state theorem')
            if criterion:
                O,_=observable_rows((A,),Q,2);N=kernel(O,2,2)
                for v in N:
                    c.check(in_span(mv(A,v,2),N,2) and in_span(mv(B,v,2),N,2),'common quotient invariance')
                for e in E:c.check(in_span(e,N,2),'uncertainty lies in unobservable kernel')

    c.group('fixed_model_and_hidden_return_controls',
            'Exact rational two-dimensional fixed nilpotent models, forbidden switching, and invisible one-step uncertainty returning at step two; steps zero through eight.')
    A=((0,1),(0,0));B=((0,0),(1,0));Q=((1,1),);v=(1,1)
    I=output_initial_basis(((A,),(B,)),Q)
    c.check(len(I)==1 and in_span(v,I),'fixed-model initial agreement line')
    c.check(not in_span(mv(A,v),I),'identifiable initial set is not invariant')
    fixed=[]
    for k in range(9):
        outA=mv(Q,apply((A,),v,(0,)*k))[0];outB=mv(Q,apply((B,),v,(0,)*k))[0]
        c.check(outA==outB,'fixed sequence agreement')
        fixed.append({'step':k,'A':int(outA),'B':int(outB)})
    c.check(mv(Q,mv(B,mv(A,v)))[0]==1,'forbidden switch disagreement')
    D=B;T=tuple(tuple(a+b for a,b in zip(x,y)) for x,y in zip(A,D));q=((1,0),)
    c.check(all(rowmul(q[0],D)[i]==0 for i in range(2)),'one-step invisible difference')
    c.check(mv(q,apply((A,),(1,0),(0,0)))[0]==0,'old second output')
    c.check(mv(q,apply((T,),(1,0),(0,0)))[0]==1,'new second output')
    c.check(len(discrepancy_span(((A,),(T,)))[0])==2,'hidden return spans ambient space')

    c.group('minimal_linear_initialization',
            'Every 2x2 F2 single-action map and scalar observation; five initial subspaces and four scalar record maps; kernel criterion versus direct output signatures through length four. Two rational worked realizations.')
    subspaces=[(),((1,0),),((0,1),),((1,1),),((1,0),(0,1))]
    for A,Q,L,R in product(mats,qr,subspaces,qr):
        points=[v for v in vectors if in_span(v,L,2)]
        O,_=observable_rows((A,),Q,2)
        criterion=all(mv(R,v,2)!=(0,) or all(dot(row,v,2)==0 for row in O) for v in points)
        direct=all(mv(R,x,2)!=mv(R,y,2) or
                   all(mv(Q,apply((A,),x,w,2),2)==mv(Q,apply((A,),y,w,2),2) for w in words(1,4))
                   for x,y in product(points,repeat=2))
        c.check(criterion==direct,'record initialization criterion')
        dim,W=predictor_dimension((A,),Q,L,2)
        c.check(0<=dim<=len(W)<=2,'realization dimension bounds')
    A=((0,1),(0,0));Q=((1,1),)
    dim,W=predictor_dimension((A,),Q,((1,1),))
    c.check(dim==2 and len(W)==2,'one-dimensional initial family needs two dynamic coordinates')
    A3=((1,1,0),(0,1,0),(0,0,0));B3=((1,1,0),(0,1,0),(2,-1,3));Q3=((1,0,0),)
    L3=((1,0,0),(0,1,0),(0,0,1))
    E,_=discrepancy_span(((A3,),(B3,)));dim,W=predictor_dimension((A3,),Q3,L3)
    c.check(len(E)==1 and dim==2,'three-dimensional family two-dimensional common quotient')
    for v3 in product((-1,0,1),repeat=3):
        for w in words(2,4):
            out=mv(Q3,apply((A3,B3),v3,w))[0]
            c.check(out==v3[0]+len(w)*v3[1],'common quotient even with switching')

    c.group('likelihood_profile_correction',
            'Eight sensor worlds with nuisance bit, two theta-dependent likelihood profiles, target s. All 35 quarter-grid joint priors placed in either nuisance slice; every binary report word through length three.')
    omega=list(product((0,1),repeat=3));target=[w[0] for w in omega]
    ell1=tuple(F(1,4) if t==0 else F(3,4) for s,t,k in omega);ells=(tuple(1-x for x in ell1),ell1)
    cells=[tuple(i for i,w in enumerate(omega) if w[1]==t and w[0]==s) for t in (0,1) for s in (0,1)]
    priors=[]
    for weights in compositions(4,4):
        for nuisance in (0,1):
            mu=[F(0)]*8
            for j,cell in enumerate(cells):mu[cell[nuisance]]=F(weights[j],4)
            mu=tuple(mu);p0=aggregate(mu,cells);priors.append((mu,p0))
            for word in words(2,3):
                raw=mu;agg=p0
                for bit in word:
                    zr,raw=posterior(raw,ells[bit]);la=tuple(ells[bit][cell[0]] for cell in cells)
                    za,agg=posterior(agg,la)
                    c.check(zr==za and aggregate(raw,cells)==agg,'raw/aggregated Bayes equality')
                pred=tuple(sum((agg[j] for j in range(4) if j%2==y),F(0)) for y in (0,1))
                truth=tuple(sum((raw[i] for i in range(8) if target[i]==y),F(0)) for y in (0,1))
                c.check(pred==truth,'target readout')
    # Degree <=m-1=1 is enough to separate all profile-target records.
    signatures=[tuple(joint_moment(mu,target,ells,w,y) for w in words(2,1) for y in (0,1)) for mu,p in priors]
    for i,j in combinations(range(len(priors)),2):
        c.check((signatures[i]==signatures[j])==(priors[i][1]==priors[j][1]),'short word separation criterion')
    # Zero likelihood outcome: return impossible, never a manufactured posterior.
    c.check(posterior((F(1),F(0)),(F(0),F(1)))==(F(0),None),'zero mass handling')

    c.group('probability_memory_migration',
            'All 15 partitions of four worlds as old and new joint-cell partitions; point masses as separating witnesses, and all 35 quarter-grid priors for every admissible aggregation.')
    from exact_checks import partitions
    parts=[]
    for code in partitions(4):parts.append(tuple(tuple(i for i,v in enumerate(code) if v==c0) for c0 in range(max(code)+1)))
    for old,new in product(parts,repeat=2):
        newlabels={x:j for j,cell in enumerate(new) for x in cell}
        refines=all(len({newlabels[x] for x in cell})==1 for cell in old)
        table={};functional=True
        for i in range(4):
            mu=tuple(F(int(j==i)) for j in range(4));a=aggregate(mu,old);b=aggregate(mu,new)
            if a in table and table[a]!=b:functional=False
            table[a]=b
        c.check(refines==functional,'point mass necessity')
        if refines:
            for weights in compositions(4,4):
                mu=tuple(F(x,4) for x in weights);op=aggregate(mu,old)
                transformed=tuple(sum((op[j] for j,cell in enumerate(old) if newlabels[cell[0]]==k),F(0)) for k in range(len(new)))
                c.check(transformed==aggregate(mu,new),'exact mass migration')

    c.group('noisy_association_and_scope_controls',
            'Opposite correlation priors with equal marginals, one noisy reference with probabilities 1/4 and 3/4, sequences of zero through eight matching reports, and a newly added likelihood splitting an old cell.')
    pplus=(F(1,2),F(0),F(0),F(1,2));pminus=(F(0),F(1,2),F(1,2),F(0));la=(F(1,4),F(1,4),F(3,4),F(3,4))
    c.check(sum(pplus[1::2])==sum(pminus[1::2])==F(1,2),'same target marginal')
    c.check(sum(pplus[:2])==sum(pminus[:2])==F(1,2),'same theta marginal')
    rows=[];x=pplus;y=pminus
    for k in range(9):
        px=sum(x[1::2]);py=sum(y[1::2]);c.check(px==F(3**k,1+3**k) and py==F(1,1+3**k),'posterior closed forms')
        c.check(0<px<1 and 0<py<1,'finite noisy support remains nondegenerate')
        rows.append({'reports':k,'plus':str(px),'minus':str(py)})
        zx,x=posterior(x,la);zy,y=posterior(y,la);c.check(zx==zy,'same predictive law with different correction')
    c.check(F(1,4)!=F(3,4),'new experiment separates an old memory cell')

    result={'status':'PASS','version':'0.5.0','arithmetic':'F2 and exact fractions.Fraction; no randomized acceptance',
            'group_count':len(c.groups),'assertions':sum(g['assertions'] for g in c.groups),'groups':c.groups,
            'runtime_seconds':time.perf_counter()-start}
    illustrations={'fixed_model_outputs':fixed,'noisy_association':rows,
                   'dimensions':{'fixed_model_initial':1,'fixed_model_minimal_predictor':2,
                                 'structured_physical':3,'structured_common_predictor':2,
                                 'raw_sensor_worlds':8,'profile_target_masses':4},
                   'non_claim':'Analytical examples, not neural data, learned trajectories, or universal proof by enumeration.'}
    (ROOT/'validation'/'observable_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'data'/'observable_illustrations.json').write_text(json.dumps(illustrations,indent=2)+'\n')
    print(f"PASS: {result['group_count']} groups, {result['assertions']} exact assertions; {result['runtime_seconds']:.3f}s")
    return result


if __name__=='__main__':run()
