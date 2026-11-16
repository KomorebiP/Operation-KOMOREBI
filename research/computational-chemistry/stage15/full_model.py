"""Canonical real H10 operator: exact sparse columns and matrix-free float actions.

Spin orbitals: all alpha modes, then all beta modes. CI arrays use increasing
integer bitmask order within each spin sector, alpha rows and beta columns.
"""
from fractions import Fraction as F
from itertools import combinations,product
import math
import numpy as np


def masks(n,k):return sorted(sum(1<<i for i in c) for c in combinations(range(n),k))
def ladder(mask,mode,create):
    if bool(mask&(1<<mode))==create:return None
    return mask^(1<<mode),(-1 if (mask&((1<<mode)-1)).bit_count()%2 else 1)
def apply_term(mask,sequence):
    sign=1
    for mode,create in sequence:
        step=ladder(mask,mode,create)
        if step is None:return None
        mask,value=step;sign*=value
    return mask,sign
def pair(p,q):return max(p,q)*(max(p,q)+1)//2+min(p,q)
def sqrt_upper(value,digits=30):
    value=F(value)
    if value<0:raise ValueError('Negative squared norm')
    a,b=math.isqrt(value.numerator),math.isqrt(value.denominator)
    if a*a==value.numerator and b*b==value.denominator:return F(a,b)
    scale=10**digits;k=math.isqrt(value.numerator*scale*scale//value.denominator)
    return F(k if k*k*value.denominator==value.numerator*scale*scale else k+1,scale)
def norm2_exact(vector):
    # Binary64 squares have power-of-two denominators; accumulate as integers.
    values=[F(float(x)) for x in np.asarray(vector).ravel()]
    if not values:return F(0)
    power=max(x.denominator.bit_length()-1 for x in values)
    return F(sum((x.numerator<<(power-(x.denominator.bit_length()-1)))**2 for x in values),1<<(2*power))


class ElectronicModel:
    def __init__(self,hraw,graw,sector):
        self.n=len(hraw);self.sector=tuple(sector)
        self.alpha=masks(self.n,self.sector[0]);self.beta=masks(self.n,self.sector[1])
        self.alpha_lookup={m:i for i,m in enumerate(self.alpha)};self.beta_lookup={m:i for i,m in enumerate(self.beta)}
        self.dimension=len(self.alpha)*len(self.beta)
        self.h=[[ (F(float(hraw[p,q]))+F(float(hraw[q,p])))/2 for q in range(self.n)] for p in range(self.n)]
        self.g={(p,q,r,s):(F(float(graw[pair(p,q),pair(r,s)]))+F(float(graw[pair(r,s),pair(p,q)])))/2 for p,q,r,s in product(range(self.n),repeat=4)}
        coefficients=[x for row in self.h for x in row]+[x/2 for x in self.g.values()]
        self.denominator=max(x.denominator for x in coefficients)
        assert all(self.denominator%x.denominator==0 for x in coefficients)
        self.h_int=[[int(x*self.denominator) for x in row] for row in self.h]
        self.g_half_int={key:int(x*self.denominator/2) for key,x in self.g.items()}
        electrons=sum(self.sector)
        hnorm=max(sum(abs(x) for x in row) for row in self.h)
        vnorm=max(sum(abs(self.g[p,q,r,s]) for q,s in product(range(self.n),repeat=2)) for p,r in product(range(self.n),repeat=2))
        self.norm_upper=electrons*hnorm+math.comb(electrons,2)*vnorm
        self._float_prepared=False

    def index(self,mask):
        low=mask&((1<<self.n)-1);high=mask>>self.n
        return self.alpha_lookup[low]*len(self.beta)+self.beta_lookup[high]

    def column(self,mask):
        result={}
        def add(sequence,coefficient):
            if not coefficient:return
            step=apply_term(mask,sequence)
            if step is not None:
                out,sign=step;result[out]=result.get(out,0)+sign*coefficient
        for p,q in product(range(self.n),repeat=2):
            for spin in [0,self.n]:add([(q+spin,False),(p+spin,True)],self.h_int[p][q])
        for (p,q,r,s),coefficient in self.g_half_int.items():
            for sigma,tau in product([0,self.n],repeat=2):
                add([(q+sigma,False),(s+tau,False),(r+tau,True),(p+sigma,True)],coefficient)
        return {self.index(mask):value for mask,value in result.items() if value}

    def retained_masks(self,core=3,end=6):
        fixed=sum(1<<i for i in range(core));active=range(core,end)
        return [fixed+sum(1<<i for i in a)+((fixed+sum(1<<i for i in b))<<self.n)
                for a in combinations(active,self.sector[0]-core) for b in combinations(active,self.sector[1]-core)]

    def sparse_columns(self,retained):return [self.column(mask) for mask in retained]

    def float_matrix(self):
        if self.dimension>2000:raise ValueError('Dense matrix deliberately prohibited at this size')
        all_masks=[a+(b<<self.n) for a in self.alpha for b in self.beta]
        out=np.zeros((self.dimension,self.dimension))
        for j,mask in enumerate(all_masks):
            for i,x in self.column(mask).items():out[i,j]=float(F(x,self.denominator))
        return out

    def prepare_float(self):
        if self._float_prepared:return
        n=self.n;m=n*n
        # E_pq E_rs - delta_qr E_ps gives the normal-ordered two-body term.
        heff=[[self.h[p][s]-sum(self.g[p,q,q,s] for q in range(n))/2 for s in range(n)] for p in range(n)]
        gmat=[[self.g[p,q,r,s] for r,s in product(range(n),repeat=2)] for p,q in product(range(n),repeat=2)]
        self.hf=np.array([[float(x) for x in row] for row in heff]).ravel()
        self.gf=np.array([[float(x) for x in row] for row in gmat])
        assert max(np.max(np.abs(self.hf)),np.max(np.abs(self.gf)))<=2**20
        self.coefficient_denominator_exponent=max(F(float(x)).denominator.bit_length()-1 for x in np.r_[self.hf,self.gf.ravel()])
        def fnorm(values):return sqrt_upper(sum(x*x for x in values))
        hnorm=fnorm([F(float(x)) for x in self.hf]);gnorm=fnorm([F(float(x)) for x in self.gf.ravel()])
        herror=fnorm([F(float(x))-y for x,y in zip(self.hf,[v for row in heff for v in row])])
        gerror=fnorm([F(float(x))-y for x,y in zip(self.gf.ravel(),[v for row in gmat for v in row])])
        unit=F(1,2**53)
        gamma=lambda k:k*unit/(1-k*unit)
        L=F(2*n);t_error=L*gamma(2);t_bound=L*(1+gamma(2))
        w_error=gerror*L+gnorm*t_error+gamma(2*m)*gnorm*t_bound
        w_bound=(1+gamma(2*m))*gnorm*t_bound
        s_error=L*w_error+gamma(2*m+2)*L*w_bound
        s_bound=(1+gamma(2*m+2))*L*w_bound
        a_error=herror*L+hnorm*t_error+gamma(2*m)*hnorm*t_bound
        a_bound=(1+gamma(2*m))*hnorm*t_bound
        self.action_error_per_norm=a_error+s_error/2+gamma(2)*(a_bound+s_bound/2)
        self.fp_constants=dict(operator_norm_upper=str(self.norm_upper),h_float_frobenius_upper=str(hnorm),g_float_frobenius_upper=str(gnorm),
            h_coefficient_error_frobenius_upper=str(herror),g_coefficient_error_frobenius_upper=str(gerror),
            action_error_per_input_norm_upper=str(self.action_error_per_norm),
            unit_roundoff=str(unit),assumptions='IEEE binary64 round-to-nearest dot-product/elementwise model, with no overflow or underflow; input/coefficients and denominator-exponent guards are checked',
            coefficient_denominator_exponent=self.coefficient_denominator_exponent)
        def links(states,lookup,p,q):
            source=[];target=[];signs=[]
            for i,state in enumerate(states):
                result=apply_term(state,[(q,False),(p,True)])
                if result is not None:
                    mask,sign=result;source.append(i);target.append(lookup[mask]);signs.append(sign)
            return np.array(source,dtype=int),np.array(target,dtype=int),np.array(signs,dtype=float)
        self.links=[(links(self.alpha,self.alpha_lookup,p,q),links(self.beta,self.beta_lookup,p,q)) for p,q in product(range(n),repeat=2)]
        self._float_prepared=True

    def apply_float(self,vector):
        self.prepare_float();vector=np.asarray(vector,dtype=np.float64)
        if vector.shape!=(self.dimension,) or not np.isfinite(vector).all():raise ValueError('Invalid action vector')
        if np.max(np.abs(vector),initial=0)>2**20:raise ValueError('Action exceeds the proved floating range')
        exp=max((F(float(x)).denominator.bit_length()-1 for x in vector),default=0)
        if exp+self.coefficient_denominator_exponent+1>=1000:raise ValueError('Cannot exclude underflow in this action')
        shape=(len(self.alpha),len(self.beta));ci=vector.reshape(shape)
        t=np.zeros((self.n*self.n,*shape))
        for k,(a,b) in enumerate(self.links):
            source,target,sign=a
            t[k,target,:]=sign[:,None]*ci[source,:]
            source,target,sign=b
            t[k][:,target]+=ci[:,source]*sign[None,:]
        flat=t.reshape(self.n*self.n,-1)
        w=(self.gf@flat).reshape(t.shape)
        one=(self.hf@flat).reshape(shape);two=np.zeros(shape)
        for k,(a,b) in enumerate(self.links):
            source,target,sign=a
            two[target,:]+=sign[:,None]*w[k,source,:]
            source,target,sign=b
            two[:,target]+=w[k][:,source]*sign[None,:]
        result=(one+two/2).ravel()
        if not np.isfinite(result).all():raise ValueError('Nonfinite action')
        return result


def source_from_ground(data,integer_order=True):
    n=int(data['n_orbitals']);sector=tuple(map(int,data['ground_sector']));sort=masks if integer_order else lambda n,k:[sum(1<<i for i in c) for c in combinations(range(n),k)]
    alpha,beta=sort(n,sector[0]),sort(n,sector[1]);ion=sort(n,sector[0]-1);lookup={m:i for i,m in enumerate(ion)}
    ground=data['ground_state'].reshape(len(alpha),len(beta));source=np.zeros((len(ion),len(beta)))
    weights=data['ao_to_mo'][:,int(data['source_index'])]
    for i,mask in enumerate(alpha):
        for p in range(n):
            step=ladder(mask,p,False)
            if step is not None:source[lookup[step[0]],:]+=step[1]*weights[p]*ground[i,:]
    return source.ravel()


def spin_flipped_source(data):
    # Fock spin-block exchange contributes (-1)^(N_alpha*N_beta), +1 here.
    alpha,beta=map(int,data['ion_sector']);n=int(data['n_orbitals'])
    source=data['source'].reshape(math.comb(n,alpha),math.comb(n,beta))
    return ((-1)**(alpha*beta)*source.T).ravel().copy()
