"""Independent finite algebraic divisor construction and alternate gamma-series regressions.
No infinite canonical product, class-field value or directed enclosure is evaluated.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, collections, datetime, importlib.util, itertools, json, sys, time
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'dependencies'))
sys.path.insert(0,str(root/'v014_copy/prior'))
import mpmath as mp
from gamma_evaluator import Evaluator
spec=importlib.util.spec_from_file_location('archived_exact',root/'v014_copy/checks/exact_checks.py')
archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,required=True);args=ap.parse_args()
tic=time.monotonic();checks=[];negative=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def H(x):return int(x>0)
def w(c):return 4 if c%5==0 else -1
def position(a,b,c):
    # Coefficients in Q[beta]/(beta^3-7), in basis (1,beta,beta^2).
    return (Q(2*a-b,15),Q(a,15),Q(3*c-2*b,105))
def base_coordinates(coefficients):
    q0,q1,q2=coefficients
    aa=15*q2;bb=2*aa-15*q1;cc=(15*q0+2*bb)/3
    return aa,bb,cc
def numerator_lift(a,b,c):
    p=position(a,b,c);lifts=[]
    for k in range(7):
        x=base_coordinates((p[0]+Q(8*k,15),p[1],p[2]+Q(k,105)))
        if all(v.denominator==1 for v in x):lifts.append((k,tuple(int(v) for v in x)))
    if len(lifts)!=1:raise AssertionError(('unique numerator argument',a,b,c,lifts))
    return lifts[0]
def divisor(a,b,c):
    k,(aa,bb,cc)=numerator_lift(a,b,c)
    return w(cc)*(H(aa)-H(bb))-w(c)*(H(a)-H(b))
counts=collections.Counter();cube_points=0;transition_points=0
for a,b,c in itertools.product(range(-8,9),repeat=3):
    m=divisor(a,b,c);assert m==archive.order(a,b,c),(a,b,c,m)
    k,lift=numerator_lift(a,b,c);assert 0<=k<7 and w(lift[2])==w(c)
    counts[m]+=1;cube_points+=1
    assert divisor(a,b-15,c-10)-m==-w(c)*int(1<=b<=15)
    kd,_=numerator_lift(a,b-8,c-5);assert kd==(k-1)%7
    transition_points+=1
check('independent polynomial-basis numerator lifts and divisor on [-8,8]^3',cube_points==4913)
check('all five signed multiplicities observed',set(counts)=={-4,-1,0,1,4})
check('period-one divisor jump and seventh-shift digit carry',transition_points==4913)
table=[];family_points=0;chamber_points=0
for n in range(1,11):
    zs=[(-i,j,5*(n+k)) for i,j,k in itertools.product(range(1,n+1),repeat=3)]
    ps=[(-i,j,5*(n+k)-r) for i,j,k in itertools.product(range(1,n+1),repeat=3) for r in range(1,5)]
    zq={position(*p) for p in zs};pq={position(*p) for p in ps}
    assert len(zq)==n**3 and len(pq)==4*n**3 and not(zq&pq)
    for p,target in [(p,4) for p in zs]+[(p,-1) for p in ps]:
        a,b,c=p;assert a<0 and b>0 and c>0 and 3*c>2*b
        assert divisor(*p)==target and -n<=a<0 and 0<b<=n and 5*n<c<=10*n
        family_points+=1;chamber_points+=1
    table.append({'n':n,'zeros':len(zq),'poles':len(pq),'zero_multiplicity':4*len(zq),'pole_multiplicity':len(pq)})
check('growth-family Q[beta] injections and disjointness n=1..10',family_points==15125)
check('growth-family chamber orders and coordinate bounds',chamber_points==15125)
check('base removable points 0,1,1/3 outside divisor',divisor(0,0,0)==0 and divisor(0,-15,-10)==0 and Q(-10,3).denominator!=1)
negative.append('wrong positive period sign separated by exact beta-basis coordinates')
assert position(2,4,5)!=(Q(0),Q(-2,15),Q(-1,15))
assert divisor(-1,1,11)==-1;negative.append('erasing fifth smoothing turns a pole into an order-four zero')
assert divisor(-2,0,10)==0;negative.append('nonstrict chamber boundary H(0)=1 changes a zero-order boundary')
jet_samples=0
for a1,a2,a3 in [(Q(1,7),Q(-2,5),Q(4,9)),(Q(-3,11),Q(5,13),Q(-7,17)),(Q(0),Q(0),Q(1))]:
    P=lambda z:a1*z+a2*z*z+a3*z*z*z
    assert 3*P(Q(1,3))-P(1)==-Q(2,3)*a2-Q(8,9)*a3
    for z in [Q(-2,3),Q(0),Q(1,5),Q(3,2)]:assert P(z)+P(-z)==2*a2*z*z
    # (P(z+1)-P(z))'' at zero, calculated from finite differences.
    T=lambda z:P(z+1)-P(z)
    assert T(1)-2*T(0)+T(-1)==6*a3
    jet_samples+=1
check('reflection, transition and special-cube exponents on exact rational polynomials',jet_samples==3)
errors=[];numerical=[];positions=[]
with mp.workdps(80):
    e=Evaluator(50);beta,t,s=e.beta,e.t,e.s;tau=-t;d=(tau+2*s+4)/7
    tol=mp.mpf('1e-42')
    def near(name,lhs,rhs):
        error=abs(lhs/rhs-1)
        if error>=tol:raise AssertionError((name,mp.nstr(error,25)))
        numerical.append(name);errors.append(error)
    near('complex beta branch cube',beta**3,7)
    check('positive continuation periods have positive imaginary parts',mp.im(t)>0 and mp.im(s)>0 and mp.im(beta)<0)
    near('actual beta*s carry',beta*s,-tau)
    near('actual beta*delta carry',beta*d,-8*s-1)
    near('actual beta*third carry',beta/3,-5*s-mp.mpf(2)/3)
    K0=(abs(tau)+abs(s)+2)/abs(beta)
    for a,b,c in [(-i,j,5*(3+k)-r) for i,j,k in itertools.product(range(1,4),repeat=3) for r in range(5)]:
        lam=(a*tau+b*s+mp.mpf(c)/5)/beta
        coeff=position(a,b,c);ind=mp.fsum(mp.mpf(q.numerator)/q.denominator*beta**j for j,q in enumerate(coeff))
        assert abs(lam-ind)<mp.mpf('1e-70') and abs(lam)<=3*K0
        positions.append({'a':a,'b':b,'c':c,'order':divisor(a,b,c),'real':mp.nstr(mp.re(lam),60),'imag':mp.nstr(mp.im(lam),60)})
    check('135 complex n=3 family positions match exact beta basis and radius bound',len(positions)==135)
    cache={};continuation_shifts=[]
    Q_t=lambda z:e.theta(z,t)
    Q_s=lambda z:e.theta(z,s)
    def Gamma(z):
        # The inherited F wrapper admits only +/-12 shifts. Unit transition
        # arguments need about15; use a new explicit finite +/-40 continuation.
        candidates=[k for k in range(-40,41) if -mp.im(t)<mp.im(z+k*s)<mp.im(s)]
        if not candidates:raise ValueError('Independent +/-40 continuation cap exceeded')
        k=min(candidates,key=abs);out=mp.exp(e.logF(z+k*s))
        if k>0:
            for j in range(k):out*=Q_t(z+j*s)
        else:
            for j in range(k,0):out/=Q_t(z+j*s)
        continuation_shifts.append(k)
        return out
    def R(z):
        key=mp.mpc(z)._mpc_
        if key not in cache:cache[key]=mp.fprod(Gamma(z+k*d) for k in range(7))/Gamma(beta*z)
        return cache[key]
    for i,z in enumerate([mp.mpc('.173','.013'),mp.mpc('.307','-.009')]):
        rz=R(z);b=beta*z
        near(f'alternate gamma series unit transition {i}',R(z+1)/rz,1/mp.fprod(Q_t(b-r*s) for r in range(1,16)))
        near(f'alternate gamma series s transition {i}',R(z+s)/rz,Q_s(b-tau)/mp.fprod(Q_t(z+k*d) for k in range(7)))
        near(f'alternate gamma series tau transition {i}',R(z+tau)/rz,mp.fprod(Q_s(z+k*d) for k in range(7))*mp.fprod(Q_t(b+j*s) for j in range(4))/(Q_s(b)*Q_s(b+tau)))
        near(f'alternate gamma series delta transition {i}',R(z+d)/rz,Q_s(z)/(Q_t(z)*Q_t(z+s)*mp.fprod(Q_t(b-r*s) for r in range(1,9))))
        near(f'alternate gamma series reflection {i}',R(z)*R(-z),Q_t(z)*Q_s(beta*z)/(Q_s(z)*Q_t(beta*z))*mp.fprod(1/Q_t(z+k*d-s) for k in range(1,7)))
    anchor=mp.fprod(1/Q_t((t+d)/2+j*d) for j in range(3))
    near('alternate gamma series zero anchor',R(0),anchor)
    assert abs(R(mp.mpc('.173','.013'))/R(0)-1)>mp.mpf('1e-5')
    negative.append('actual correction is not a constant anchored at zero')
    max_cutoff=max(e.cutoffs);max_tail=mp.nstr(max(e.tails),25)
    complex_record={'working_digits':80,'series_design_digits':50,'tolerance':'1e-42','continuation_cap':[-40,40],'actual_continuation_shifts':[min(continuation_shifts),max(continuation_shifts)],'identities':numerical,'max_relative_error':mp.nstr(max(errors),25),'max_gamma_cutoff':max_cutoff,'max_logarithmic_series_tail':max_tail,'K0':mp.nstr(K0,60),'complex_family_positions':positions}
out={'result':'PASS','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-tic,'exact_checks':checks,'negative_controls':negative,'divisor_cube_triples':cube_points,'multiplicity_histogram':dict(counts),'growth_family_points':family_points,'growth_family_table':table,'exact_polynomial_samples':jet_samples,'numerical':complex_record,'scope':'Finite exact algebraic divisor construction, family data and normalization exponent checks; alternate inherited gamma-series floating regressions at new points. No unbounded divisor enumeration, infinite canonical-product approximation, class-field equality, or directed rounding certificate.'}
args.result.write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(checks),'named finite checks;',len(negative),'negative controls;',len(numerical),'floating identities;',family_points,'growth-family points')
