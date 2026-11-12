"""Author: Komorebi P. Reusable target-only sparse q3 topology proposal search.

No witness/fixture access occurs here. All returned candidates are NUMERICAL
PROPOSALS. A separate exact interval or algebraic checker must accept them.
"""
from functools import lru_cache
from fractions import Fraction
from itertools import combinations
import time
import numpy as np
from scipy.optimize import least_squares

def canonical(spec):
    variants=[]
    for ps in (False,True):
        for ins in (False,True):
            p=[int(ps),int(not ps),3 if ins else 2,2 if ins else 3]
            variants.append(tuple(sorted((t,*sorted((p[a],p[b]))) for t,a,b in spec)))
    return min(variants)

@lru_cache(None)
def catalog(resistors=4):
    if resistors not in (4,5):raise ValueError('This bounded catalog supports four or five resistors')
    pairs=list(combinations(range(4),2));specs=set()
    for reactive in combinations(pairs,3):
        for singleton in ('L','C'):
            other='C' if singleton=='L' else 'L'
            for one in range(3):
                re=[(singleton if i==one else other,*p) for i,p in enumerate(reactive)]
                for res in combinations(pairs,resistors):
                    specs.add(canonical(re+[('R',*p) for p in res]))
    return tuple(sorted(specs))

def components(spec,ids):
    p=list(range(4))
    def find(a):
        while p[a]!=a:a=p[a]
        return a
    for j in ids:
        _,a,b=spec[j];a=find(a);b=find(b)
        if a==b:return None
        p[a]=b
    return tuple(find(i) for i in range(4))

@lru_cache(None)
def model(spec):
    m=len(spec);nl=sum(t=='L' for t,a,b in spec);terms=[[],[]]
    for side,size in ((0,2),(1,3)):
        for ids in combinations(range(m),size):
            co=components(spec,ids)
            if co is None:continue
            if side==0 and (len(set(co))!=2 or co[0]==co[1]):continue
            if side==1 and len(set(co))!=1:continue
            k=nl+sum({'L':-1,'C':1,'R':0}[spec[j][0]] for j in ids)
            terms[side].append((k,ids))
    if any(not side or max(k for k,_ in side)!=3 for side in terms):return None
    ex=np.zeros((sum(map(len,terms)),m),dtype=int);a=np.zeros((8,len(ex)))
    row=0
    for side,terms_side in enumerate(terms):
        for k,ids in terms_side:
            ex[row,list(ids)]=1;a[4*side+k,row]=1;row+=1
    def both(z):
        mon=np.exp(ex@z);v=a@mon;d=(a*mon[None,:])@ex
        indices=[0,1,2,4,5,6,7];f=v[indices]/v[3]
        j=(d[indices]-f[:,None]*d[3][None,:])/v[3]
        return f,j
    return both

@lru_cache(None)
def ranked_catalog(resistors=4):
    out=[]
    for index,spec in enumerate(catalog(resistors)):
        fun=model(spec)
        if fun is None:continue
        z=np.array([-.5,.1,.4,-.2,.6,-.3,.2,.35][:len(spec)])
        if np.linalg.matrix_rank(fun(z)[1])==7:out.append((index,spec,fun))
    return tuple(out)

def fit_target(P,Q,*,resistors=4,starts=1,max_nfev=220,seed=2026111223,
               threshold=1e-10,max_candidates=1):
    """Fit fixed sparse catalog with only target coefficients as task data.

    For eight branches, first find an underdetermined proposal, then rationally
    fix one resistor and solve the remaining seven variables. The returned
    fixed_parameters is an additional equality for exact certification.
    """
    P=[Fraction(p) for p in P];Q=[Fraction(q) for q in Q]
    if len(P)!=4 or len(Q)!=4 or P[-1]<=0 or Q[-1]<=0:
        return {'status':'UNKNOWN','reason':'Requires positive-leading full(3,3) target'}
    target=np.array([float(x/P[-1]) for x in P[:3]+Q]);scale=np.maximum(1,abs(target))
    rng=np.random.default_rng(seed);cats=ranked_catalog(resistors)
    order=rng.permutation(len(cats));best=None;proposals=[];attempts=0;now=time.perf_counter()
    for round_no in range(starts):
        for position in order:
            cat_index,spec,fun=cats[position];m=len(spec)
            def f(z):return (fun(z)[0]-target)/scale
            def jac(z):return fun(z)[1]/scale[:,None]
            z0=np.zeros(m) if round_no==0 else rng.normal(0,1.5,m)
            attempts+=1
            fit=least_squares(f,z0,jac=jac,bounds=(-16,16),max_nfev=max_nfev,
                              ftol=1e-12,xtol=1e-12,gtol=1e-12)
            err=float(max(abs(f(fit.x))))
            if best is None or err<best['scaled_residual']:
                best={'catalog_index':cat_index,'scaled_residual':err,'round':round_no,'nfev':fit.nfev}
            if err>threshold:continue
            fixed=[];z=fit.x
            if m==8:
                options=[]
                for j,(typ,a,b) in enumerate(spec):
                    if typ!='R':continue
                    cols=[k for k in range(m) if k!=j]
                    cond=float(np.linalg.cond(jac(z)[:,cols]))
                    options.append((cond,j,cols))
                resolved=False
                for cond,j,cols in sorted(options):
                    v=Fraction(float(np.exp(z[j]))).limit_denominator(64)
                    if v<=0:continue
                    z_fixed=float(np.log(float(v)))
                    def unpack(y):
                        full=np.empty(m);full[cols]=y;full[j]=z_fixed;return full
                    refined=least_squares(lambda y:f(unpack(y)),z[cols],
                        jac=lambda y:jac(unpack(y))[:,cols],bounds=(-16,16),
                        max_nfev=max_nfev,ftol=1e-13,xtol=1e-13,gtol=1e-13)
                    err2=float(max(abs(f(unpack(refined.x)))))
                    if err2<threshold:
                        z=unpack(refined.x);err=err2;fixed=[{'index':j,'value':str(v)}];resolved=True;break
                if not resolved:continue
            proposal={'catalog_index':cat_index,'spec':spec,
                'target':{'P':list(map(str,P)),'Q':list(map(str,Q))},
                'parameters':[format(x,'.17g') for x in np.exp(z)],
                'fixed_parameters':fixed,'scaled_residual':err,'round':round_no,
                'nfev':fit.nfev,'jacobian_condition':float(np.linalg.cond(jac(z)))}
            proposals.append(proposal)
            if len(proposals)>=max_candidates:
                return {'status':'NUMERICAL_PROPOSAL','proposals':proposals,'best':best,
                    'attempts':attempts,'elapsed_seconds':time.perf_counter()-now,
                    'catalog_count':len(catalog(resistors)),'rank7_count':len(cats),
                    'seed':seed,'starts':starts,'max_nfev':max_nfev}
    return {'status':'UNKNOWN','proposals':proposals,'best':best,'attempts':attempts,
        'elapsed_seconds':time.perf_counter()-now,'catalog_count':len(catalog(resistors)),
        'rank7_count':len(cats),'seed':seed,'starts':starts,'max_nfev':max_nfev}
