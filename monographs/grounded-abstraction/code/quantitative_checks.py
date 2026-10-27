"""Small exact illustrations for the first-edition quantitative theorems.

Arithmetic is rational. No training, sampled evidence, or external interaction.
Run from any directory with Python 3.10+; only the standard library is needed.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parents[1]


def rational_vector(values):
    return tuple(F(x) for x in values)


def probability(values):
    p = rational_vector(values)
    if not p or any(x < 0 for x in p) or sum(p) != 1:
        raise ValueError('Expected a nonempty normalized probability vector')
    return p


def tv(p, q):
    p, q = probability(p), probability(q)
    if len(p) != len(q):
        raise ValueError('Probability dimensions differ')
    return sum(abs(a-b) for a,b in zip(p,q))/2


def quantize(p, denominator):
    p = probability(p)
    if not isinstance(denominator, int) or isinstance(denominator, bool) or denominator < 1:
        raise ValueError('Denominator must be a positive integer')
    raw = tuple(x*denominator for x in p)
    counts = [x.numerator//x.denominator for x in raw]
    left = denominator-sum(counts)
    order = sorted(range(len(p)), key=lambda i: (-(raw[i]-counts[i]), i))
    for i in order[:left]:
        counts[i] += 1
    return tuple(F(n,denominator) for n in counts)


def bayes(p, likelihood):
    p = probability(p)
    ell = rational_vector(likelihood)
    if len(ell) != len(p) or any(x < 0 or x > 1 for x in ell):
        raise ValueError('Invalid likelihood vector')
    weight = tuple(x*y for x,y in zip(p,ell))
    z = sum(weight)
    if not z:
        raise ValueError('Impossible report: no posterior is assigned')
    return tuple(x/z for x in weight)


def error_bound(k, denominator, beta, epsilon, horizon, initial=None):
    if (not isinstance(k,int) or k<1 or not isinstance(denominator,int) or denominator<1
        or not isinstance(horizon,int) or horizon<0):
        raise ValueError('Invalid dimensions, denominator, or horizon')
    beta,epsilon = F(beta),F(epsilon)
    if not 0<beta<=1 or epsilon<0:
        raise ValueError('Positive likelihood floor and nonnegative error required')
    eta = F(k,2*denominator)
    e0 = eta if initial is None else F(initial)
    if e0<0:
        raise ValueError('Initial error must be nonnegative')
    gamma = 1/beta
    return min(F(1), gamma**horizon*e0+(gamma*epsilon+eta)*sum(gamma**j for j in range(horizon)))


def compositions(total, k):
    if k == 1:
        yield (total,)
    else:
        for a in range(total+1):
            for tail in compositions(total-a,k-1):
                yield (a,)+tail


def simplex(total,k):
    return [tuple(F(a,total) for a in c) for c in compositions(total,k)]


def histories(horizon):
    for n in range(horizon+1):
        yield from product((0,1), repeat=n)


def matvec(M, x):
    return tuple(sum(a*b for a,b in zip(row,x)) for row in M)


def block_bound(g,b,c,d,V,H,e0,t):
    g,b,c,d,V,H,e0 = map(F,(g,b,c,d,V,H,e0))
    if min(g,b,c,d,V,H,e0)<0 or t<0:
        raise ValueError('Block bounds must be nonnegative')
    u=(V,H); err=e0
    for _ in range(t):
        err=g*err+b*u[1]
        u=matvec(((g,b),(c,d)),u)
    return err,u


def total_bound(g,b,c,d,V,H,e0):
    g,b,c,d,V,H,e0=map(F,(g,b,c,d,V,H,e0))
    D=(1-g)*(1-d)-b*c
    if min(g,b,c,d,V,H,e0)<0 or g>=1 or d>=1 or D<=0:
        raise ValueError('The strict common comparison condition is not met')
    return e0/(1-g)+b*(c*V+(1-g)*H)/((1-g)*D)


def sensor_trace(N, word):
    p=probability((F(3,8),F(1,8),F(1,8),F(3,8)))
    q=quantize(p,N)
    rows=[{'step':0,'exact':p,'rounded':q,'error':tv(p,q)}]
    for i,o in enumerate(word,1):
        ell=tuple(F(1,4) if theta==0 else F(3,4) for s,theta in product((0,1),repeat=2))
        if not o: ell=tuple(1-x for x in ell)
        p=bayes(p,ell);q=quantize(bayes(q,ell),N)
        rows.append({'step':i,'exact':p,'rounded':q,'error':tv(p,q)})
    return rows


def integrated(N=65536, word=(1,1,1), steps=3):
    trace=sensor_trace(N,word)
    p,q=trace[-1]['exact'],trace[-1]['rounded']
    actions=(F(0),F(1,2)**steps)
    exact_risks=[]; estimated=[]
    response=[]
    for s,theta,n in product((0,1), repeat=3):
        M=((F(1,2),F((-1)**n,64)),(F(1,8),F(1,2)))
        state=(F(s),F(1))
        for _ in range(steps):state=matvec(M,state)
        response.append((s,theta,n,state[0]))
    for a in actions:
        exact_risks.append(sum(p[2*s+theta]*F(1,2)*min(F(1),abs(y-a)) for s,theta,n,y in response))
        estimated.append(sum(q[2*s+theta]*min(F(1),abs(F(s,2**steps)-a)) for s,theta in product((0,1),repeat=2)))
    e=error_bound(4,N,F(1,4),0,len(word),trace[0]['error'])
    d,_=block_bound(F(1,2),F(1,64),F(1,8),F(1,2),1,1,0,steps)
    xi=min(F(1),e+d)
    best=min(range(2),key=lambda i: estimated[i])
    return {'N':N,'word':word,'prediction_steps':steps,'p':p,'rounded':q,
            'actual_mass_error':tv(p,q),'mass_error_bound':e,'dynamics_bound':d,'risk_radius':xi,
            'actions':actions,'exact_risks':tuple(exact_risks),'estimated_risks':tuple(estimated),
            'selected_index':best,'gap':estimated[1-best]-estimated[best],
            'upper_selected_risk':estimated[best]+xi,'threshold':F(3,50),
            'probability_field_bits':4*N.bit_length()}


class Checks:
    def __init__(self):self.groups=[];self.current=None
    def group(self,name,domain):
        self.current={'name':name,'domain':domain,'assertions':0};self.groups.append(self.current)
    def check(self,condition,message='exact assertion failed'):
        if not condition:raise AssertionError(message)
        self.current['assertions']+=1
    def rejects(self,fn):
        try:fn()
        except ValueError:self.check(True)
        else:raise AssertionError('An invalid mathematical input was accepted')


def encode(obj):
    if isinstance(obj,F):return str(obj)
    if isinstance(obj,dict):return {k:encode(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [encode(v) for v in obj]
    return obj


def main():
    started=time.perf_counter();T=Checks()
    T.group('simplex_rounding','All k=1..4 rational simplex points with denominator 1..5; output denominators 1..9.')
    for k in range(1,5):
        for den in range(1,6):
            for p in simplex(den,k):
                for N in range(1,10):
                    q=quantize(p,N)
                    T.check(sum(q)==1 and min(q)>=0)
                    T.check(tv(p,q)<=F(k,2*N))
                    T.check(all((x*N).denominator==1 for x in q))
                    T.check(quantize(q,N)==q)
    T.group('bayesian_perturbation','All two-cell quarter-grid priors and likelihood vectors with coordinates 1/4,1/2,3/4,1.')
    likelihoods=list(product((F(1,4),F(1,2),F(3,4),F(1)),repeat=2))
    for p,q in product(simplex(4,2),repeat=2):
        for ell,other in product(likelihoods,repeat=2):
            beta=min(ell+other); eps=max(abs(a-b) for a,b in zip(ell,other))
            T.check(tv(bayes(p,ell),bayes(q,other))<=(tv(p,q)+eps)/beta)
    T.group('exact_profile_rounding','Four sensor cells; every binary report history through length 5; denominators 8,16,64,256,65536.')
    for N in (8,16,64,256,65536):
        for word in histories(5):
            rows=sensor_trace(N,word)
            for row in rows:
                bound=error_bound(4,N,F(1,4),0,row['step'],rows[0]['error'])
                T.check(row['error']<=bound)
                T.check(tv((sum(row['exact'][:2]),sum(row['exact'][2:])),(sum(row['rounded'][:2]),sum(row['rounded'][2:])))<=row['error'])
    T.group('within_cell_likelihood_error','Four raw worlds in two target cells; differing likelihoods within cells, adaptive matched experiment choice, every report history through length 4; N=8,64,4096.')
    rawell=(F(1,4),F(3,8),F(5,8),F(3,4)); rep=(F(5,16),F(11,16))
    raw0=probability((F(1,10),F(2,10),F(3,10),F(4,10)))
    cell0=(sum(raw0[:2]),sum(raw0[2:]))
    for N in (8,64,4096):
        for word in histories(4):
            p=raw0;q=quantize(cell0,N);e0=tv(cell0,q)
            for i,o in enumerate(word,1):
                # A selector based only on the retained record reverses report meaning.
                reverse=(q[1]>F(1,2));use=o^reverse
                ell=rawell if use else tuple(1-x for x in rawell)
                reported=rep if use else tuple(1-x for x in rep)
                p=bayes(p,ell);q=quantize(bayes(q,reported),N)
                pushed=(sum(p[:2]),sum(p[2:]))
                T.check(tv(pushed,q)<=error_bound(2,N,F(1,4),F(1,16),i,e0))
    T.group('rare_evidence_control','Two worlds with d=1/(4N), N=2,4,16,64; impossible observations deliberately rejected.')
    for N in (2,4,16,64):
        d=F(1,4*N);p=(1-d,d);q=quantize(p,N)
        T.check(q==(1,0) and tv(p,q)==d)
        p1=bayes(p,(d*d,1));q1=bayes(q,(d*d,1))
        T.check(p1[1]==1/(1+d-d*d) and q1[1]==0)
        T.check(tv(p1,q1)>F(3,4))
        # Variant with both report outcomes strictly positive in every world.
        T.check(bayes(p,(d*d,1-d*d))[1]>F(3,4))
    T.rejects(lambda:bayes((1,0),(0,1)))
    T.group('block_comparison','Four rational norm-bound families, all sign-switching words through length 5, initial coordinates -1,0,1, and exact or 1/8-displaced initialization.')
    families=[(F(1,2),F(1,64),F(1,8),F(1,2)),(F(1,2),F(1,64),F(0),F(2)),
              (F(1,2),F(3,4),F(3,4),F(1,2)),(F(0),F(1,8),F(1,4),F(0))]
    for g,b,c,d in families:
        for v,h in product((-1,0,1),repeat=2):
            for shift in (F(0),F(1,8)):
                for word in histories(5):
                    state=(F(v),F(h));nom=F(v)+shift
                    for bit in word:
                        sign=(-1)**bit
                        state=matvec(((g,sign*b),(sign*c,sign*d)),state);nom=g*nom
                    bound,u=block_bound(g,b,c,d,1,1,shift,len(word))
                    T.check(abs(state[0]-nom)<=bound)
                    T.check(abs(state[0])<=u[0] and abs(state[1])<=u[1])
    T.group('infinite_series_and_feedback','Positive stable comparison families and finite partial sums through 30; exact unstable-output and two-way-feedback formulas through 10.')
    for g,b,c,d in (families[0],families[3],(F(1,2),F(1,10),F(1,10),F(1,2)),(F(0),F(0),F(1),F(1,2))):
        bound=total_bound(g,b,c,d,1,1,F(1,8));partial=F(0)
        for t in range(31):
            value,_=block_bound(g,b,c,d,1,1,F(1,8),t);partial+=value
            T.check(partial<=bound)
    for t in range(11):
        val,_=block_bound(F(1,2),F(1,64),0,2,0,1,0,t)
        T.check(val==F(1,64)*(F(2)**t-F(1,2)**t)/F(3,2))
        val,_=block_bound(F(1,2),0,1,2,1,1,0,t);T.check(val==0)
        y=(F(1),F(1))
        for _ in range(t):y=matvec(((F(1,2),F(3,4)),(F(3,4),F(1,2))),y)
        T.check(y==(F(5,4)**t,F(5,4)**t))
    T.rejects(lambda:total_bound(F(1,2),F(3,4),F(3,4),F(1,2),1,1,0))
    T.group('joint_risk_certificate','Eight-world sensor, all histories through three reports, future horizons 0..5, N=64,256,65536; exact risks for both numerical decisions.')
    for N in (64,256,65536):
        for word in histories(3):
            for steps in range(6):
                x=integrated(N,word,steps);j=x['selected_index'];xi=x['risk_radius']
                for r,est in zip(x['exact_risks'],x['estimated_risks']):T.check(abs(r-est)<=xi)
                T.check(x['exact_risks'][j]-min(x['exact_risks'])<=2*xi)
                T.check(x['gap']<=2*xi or x['exact_risks'][j]<x['exact_risks'][1-j])
                T.check(x['upper_selected_risk']>x['threshold'] or x['exact_risks'][j]<=x['threshold'])
    T.group('precision_choice','Horizons 0..4, likelihood floors 1/2 and 1/4, model errors 0 and 1/128, and tolerance 1/10 when its strict prerequisite holds.')
    for H,beta,eps in product(range(5),(F(1,2),F(1,4)),(F(0),F(1,128))):
        gam=1/beta;A=sum(gam**j for j in range(H+1));B=gam*sum(gam**j for j in range(H));tau=F(1,10)
        if tau>eps*B:
            f=4*A/(2*(tau-eps*B));N=max(1,-(-f.numerator//f.denominator))
            T.check(error_bound(4,N,beta,eps,H)<=tau)
            T.check(all(error_bound(4,N,beta,eps,j)<=tau for j in range(H+1)))
    T.group('input_boundaries','Invalid probability vectors, record dimensions, denominators, likelihoods and quantitative premises.')
    for fn in (lambda:quantize((),1),lambda:quantize((1,-1),4),lambda:quantize((F(1,2),),4),
               lambda:quantize((1,),0),lambda:quantize((1,),True),lambda:bayes((1,0),(1,)),
               lambda:bayes((1,0),(2,0)),lambda:error_bound(4,10,0,0,1),
               lambda:error_bound(4,10,F(1,4),-1,1),lambda:block_bound(-1,0,0,0,1,1,0,1)):
        T.rejects(fn)
    T.group('consolidated_example_values','The exact values printed in the first-edition sensor-to-predictor example.')
    x=integrated()
    for check in (sum(x['p'][2:])==F(41,56),x['probability_field_bits']==68,
                  x['mass_error_bound']==F(21,32768),x['dynamics_bound']==F(481,32768),
                  x['risk_radius']==F(251,16384),x['selected_index']==1,
                  x['gap']>2*x['risk_radius'],x['upper_selected_risk']<F(3,50),
                  x['exact_risks'][1]<x['exact_risks'][0]):T.check(check)
    curve=[]
    for N in (8,16,32,64,128,256,512,1024,4096,16384,65536):
        actual=max(row['error'] for word in product((0,1),repeat=3) for row in sensor_trace(N,word))
        curve.append({'N':N,'maximum_actual_TV_through_3':actual,
                      'generic_bound':error_bound(4,N,F(1,4),0,3)})
    leakage=[]
    for n in range(1,9):
        unstable,_=block_bound(F(1,2),F(1,64),0,2,0,1,0,n)
        stable,_=block_bound(F(1,2),F(1,64),0,F(1,2),0,1,0,n)
        leakage.append({'steps':n,'unstable':unstable,'stable':stable})
    data={'integrated':x,'precision_curve':curve,'leakage_curve':leakage,
          'scope':'Exact rational analytical fixtures. No learner training, empirical sample, or hardware-time claim.'}
    (ROOT/'data').mkdir(exist_ok=True);(ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'data'/'quantitative_illustrations.json').write_text(json.dumps(encode(data),indent=2)+'\n')
    report={'status':'PASS','group_count':len(T.groups),'assertions':sum(g['assertions'] for g in T.groups),
            'groups':T.groups,'runtime_seconds':time.perf_counter()-started,
            'arithmetic':'fractions.Fraction, integers, finite enumeration',
            'non_claim':'These are bounded project-authored checks, not proofs by enumeration, independent validation, or trained-agent results.'}
    (ROOT/'validation'/'quantitative_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS: {report['group_count']} groups; {report['assertions']} exact checks.")
    print(json.dumps(encode(x),indent=2))

if __name__=='__main__':main()
