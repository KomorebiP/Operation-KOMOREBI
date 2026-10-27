"""Exact modular dyadic tail evaluation. No large-index Bernoulli construction.

Conventions: B1=-1/2; r is first omitted depth; E_(2N) is target.
All polynomial approximations are coefficientwise modulo 2**precision.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, factorial


def v2(n):
    if not n:
        return float('inf')
    n=abs(int(n))
    return (n & -n).bit_length()-1


def mod_fraction(q, precision):
    q=Fraction(q)
    if q.denominator%2==0:
        raise ValueError('Nonintegral dyadic rational')
    mod=1<<precision
    return (q.numerator*pow(q.denominator,-1,mod))%mod

@lru_cache(None)
def bernoulli_small(n):
    if n==0: return Fraction(1)
    if n==1: return Fraction(-1,2)
    if n%2: return Fraction(0)
    return -sum((comb(n+1,k)*bernoulli_small(k) for k in range(n)),Fraction(0))/(n+1)

@lru_cache(None)
def twice_bernoulli_mod(n, precision):
    """Return 2 B_n modulo 2^precision for even n>=2.

    Bernoulli distribution identity:
    (1-2^(n-1))*2 B_n = sum_k binom(n,k) 2^k B_k.
    Terms k>=precision+1 vanish. Requires only B_0,...,B_precision.
    """
    if n<2 or n%2 or precision<1: raise ValueError('n positive even; precision positive')
    mod=1<<precision
    acc=0
    for k in range(min(n,precision)+1):
        bk=bernoulli_small(k)
        if bk:
            acc=(acc+comb(n,k)*mod_fraction((1<<k)*bk,precision))%mod
    return acc*pow((1-pow(2,n-1,mod))%mod,-1,mod)%mod


def lam(r,q):return 3*q+(r+q).bit_count()-r.bit_count()

def minimum(r):
    if r<1:raise ValueError('r >= 1')
    weights=[lam(r,q) for q in range((r.bit_count()-1)//3+1)]
    m=min(weights)
    return m,[q for q,w in enumerate(weights) if w==m]


def gamma_mod(r,q,mu,precision):
    """2^(-mu) 8^q beta_(r+q)/beta_r, stripped before division."""
    cost=lam(r,q)-mu
    if cost<0:raise ValueError('normalization not integral')
    if cost>=precision:return 0
    bits=precision-cost
    mod=1<<bits
    product_unit=1
    for t in range(1,2*q+1):
        z=2*r+t
        product_unit=product_unit*(z>>v2(z))%mod
    unit=(2*(r+q)-1)*pow(2*r-1,-1,mod)%mod
    unit=unit*twice_bernoulli_mod(2*(r+q),bits)%mod
    unit=unit*pow(twice_bernoulli_mod(2*r,bits),-1,mod)%mod
    unit=unit*pow(product_unit,-1,mod)%mod
    return unit<<cost


def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0:a.pop()
    return a or [0]

def add(a,b,mod):
    out=[0]*max(len(a),len(b))
    for i,x in enumerate(a):out[i]+=x
    for i,x in enumerate(b):out[i]+=x
    return trim([x%mod for x in out])

def mul(a,b,mod):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:out[i+j]+=x*y
    return trim([x%mod for x in out])

def affine(a,s,h,mod):
    """Polynomial a(s+h*y), using Horner."""
    out=[0]
    for c in reversed(a):
        out=mul(out,[s%mod,h%mod],mod)
        out[0]=(out[0]+c)%mod
    return trim(out)

def evaluate(a,x,mod):
    out=0
    for c in reversed(a):out=(out*x+c)%mod
    return out

@lru_cache(None)
def source_polynomial(precision):
    """A(x) in (Z/2^P)[x], correct coefficientwise.
    A(x)=ell/8 * sum ell^k/(k+1)!*(x+1)^k * (1+2x)^-1.
    ell=log(9); v2(ell)=3.
    """
    if precision<1:raise ValueError('positive precision required')
    mod=1<<precision
    log8=0
    for h in range(1,precision+2):
        exponent=3*h-3-v2(h)
        if exponent<precision:
            term=(1<<exponent)*pow(h>>v2(h),-1,mod)%mod
            log8=(log8+(term if h%2 else -term))%mod
    b=[0]
    for k in range(precision+1):
        fact=factorial(k+1);cost=3*k-v2(fact)
        if cost>=precision:continue
        coefficient=(1<<cost)*pow(log8,k+1,mod)*pow(fact>>v2(fact),-1,mod)%mod
        b=add(b,[coefficient*comb(k,i)%mod for i in range(k+1)],mod)
    inv=[pow(-2,k,mod) for k in range(precision)]
    return tuple(mul(b,inv,mod))


def tail_polynomial(r,precision):
    """G_r=2^-mu H_r modulo 2^P, with complete proven tail cutoff."""
    mu,J=minimum(r);mod=1<<precision
    qmax=max(0,(precision+r.bit_count()+mu-2)//3)
    # For q>=qmax+1, 3q+1-s2(r)-mu >= precision.
    assert 3*(qmax+1)+1-r.bit_count()-mu>=precision
    a=source_polynomial(precision);p=[1];g=[0]
    for q in range(qmax+1):
        if q:
            i=q-1
            p=mul(p,[-i,1],mod)
            p=mul(p,[-(2*i+1),2],mod)
        c=gamma_mod(r,q,mu,precision)
        if c:
            aq=affine(a,-q,1,mod)
            term=mul(p,aq,mod)
            g=add(g,[(c*x)%mod for x in term],mod)
    return {'r':r,'mu':mu,'minima':J,'precision':precision,
            'qmax':qmax,'coefficients':g}


def root_atlas(data,max_depth=100):
    """Certified leaves from coefficientwise approximations.
    Reports unresolved precision/depth; never promotes such leaves to roots.
    """
    leaves=[]
    def visit(p,bits,s,k,c):
        if k>max_depth:
            leaves.append({'kind':'unresolved_depth','s':s,'k':k,'content':c,'bits':bits});return
        nu=min((v2(z) for z in p if z),default=bits)
        if nu>=bits:
            leaves.append({'kind':'unresolved_precision','s':s,'k':k,'content_lower':c+bits});return
        nu=int(nu)
        if nu:
            p=trim([z>>nu for z in p]);bits-=nu;c+=nu
        red=trim([z%2 for z in p])
        if red==[1]:
            leaves.append({'kind':'constant','s':s,'k':k,'value':c,
                           'reduction':red});return
        if len(red)==2 and red[1]==1:
            mod=1<<bits;root=red[0]
            for b in range(1,bits):
                if evaluate(p,root,1<<(b+1)):
                    root+=1<<b
                assert evaluate(p,root,1<<(b+1))==0
            leaves.append({'kind':'simple_root','s':s,'k':k,'content':c,
                           'offset':c-k,'root_mod':s+(1<<k)*root,
                           'root_bits':bits+k,'reduction':red});return
        # Other reductions may be nonzero as polynomials but have no residue roots.
        mod=1<<bits
        for e in (0,1):
            visit(affine(p,e,2,mod),bits,s+(1<<k)*e,k+1,c)
    visit(data['coefficients'],data['precision'],0,0,0)
    return leaves


def wall_threshold(j):
    e=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
    return 3*j+1+(j-1).bit_count()-min(e)


def binary_divmod(a,b):
    """Division of F2 polynomials encoded as integers."""
    if b==0:raise ZeroDivisionError('zero polynomial')
    q=0;db=b.bit_length()-1
    while a and a.bit_length()-1>=db:
        shift=a.bit_length()-1-db
        q ^= 1<<shift
        a ^= b<<shift
    return q,a


def bits_coefficients(x):
    return [(x>>i)&1 for i in range(max(1,x.bit_length()))]


def weierstrass_mod(data):
    """Unique monic W and U=1 mod 2 with G=W*U mod 2^precision.

    This is constructive coefficientwise Weierstrass preparation via binary
    polynomial long division. Output includes a factorization certificate.
    """
    f=data['coefficients'];p=data['precision'];mod=1<<p
    reduction=trim([z%2 for z in f])
    if not any(reduction):raise ValueError('primitive input required')
    degree=len(reduction)-1
    if degree==0:
        return {'r':data['r'],'precision':p,'degree':0,'W':[1],'U':f[:]}
    w=reduction[:];u=[1]
    red_bits=sum(z<<i for i,z in enumerate(reduction))
    for k in range(1,p):
        smod=1<<(k+1)
        product=mul(w,u,smod)
        error=add(f,[-z for z in product],smod)
        assert all(z%(1<<k)==0 for z in error)
        err_bits=sum(((z>>k)&1)<<i for i,z in enumerate(error))
        quo,rem=binary_divmod(err_bits,red_bits)
        wc=[(z<<k) for z in bits_coefficients(rem)]
        uc=[(z<<k) for z in bits_coefficients(quo)]
        w=add(w,wc,mod);u=add(u,uc,mod)
        assert len(w)==degree+1 and w[-1]==1
        assert all(z==0 for z in add(f,[-z for z in mul(w,u,smod)],smod))
    assert mul(w,u,mod)==trim([z%mod for z in f])
    assert u[0]%2==1 and all(z%2==0 for z in u[1:])
    return {'r':data['r'],'precision':p,'degree':degree,'W':w,'U':u}
