#!/usr/bin/env python3
"""Independent audit: sqrt(5) arithmetic, inverse-conic derivatives,
cyclic logarithm enumeration, and digit-by-digit Hensel lifting.
Imports no primary computation module. This is not an independent reviewer.
"""
from __future__ import annotations
import argparse, hashlib, json, math, struct
from fractions import Fraction
from pathlib import Path


def check(ok, message):
    if not ok: raise AssertionError(message)


class Root5:
    def __init__(self, modulus=0, root=None):
        self.p,self.root=modulus,root
        self.one=self.z(1); self.zero=self.z(0)
        self.d=self.z(0,1)
        self.phi=self.divide(self.plus(self.one,self.d),self.z(2))
    def z(self,a=0,b=0):
        if self.p:
            a,b=int(a)%self.p,int(b)%self.p
            return ((a+b*self.root)%self.p,0) if self.root is not None else (a,b)
        return Fraction(a),Fraction(b)
    def plus(self,x,y): return self.z(x[0]+y[0],x[1]+y[1])
    def minus(self,x,y): return self.z(x[0]-y[0],x[1]-y[1])
    def times(self,x,y): return self.z(x[0]*y[0]+5*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    def invert(self,x):
        v=x[0]*x[0]-5*x[1]*x[1]
        if self.p:
            v%=self.p; check(v!=0,'division by zero');w=pow(v,-1,self.p)
        else:
            check(v!=0,'division by zero');w=1/v
        return self.z(x[0]*w,-x[1]*w)
    def divide(self,x,y):return self.times(x,self.invert(y))
    def power(self,x,n):
        if n<0:return self.power(self.invert(x),-n)
        result=self.one
        for bit in bin(n)[2:]:
            result=self.times(result,result)
            if bit=='1':result=self.times(result,x)
        return result
    def mult(self,x,n):return self.times(x,self.z(n))
    def phi_output(self,x):
        a,b=x
        if self.p:return [(a-b)%self.p,(2*b)%self.p] if self.root is None else [a%self.p,0]
        return [str(a-b),str(2*b)]
    def power_test(self,x,m):
        order=(self.p if self.root is not None else self.p**2)-1
        return self.power(x,order//math.gcd(order,m))==self.one


def inverse_conic_computation(K):
    one,phi,d=K.one,K.phi,K.d
    delta=K.divide(K.mult(K.minus(K.z(5),d),3),K.z(2))
    a,b=K.minus(phi,one),K.mult(phi,-1)
    aplus=K.minus(phi,K.z(2));bplus=K.minus(K.mult(phi,3),K.z(6));bminus=K.mult(phi,3)
    # X(lambda)=a+2delta*(aplus-lambda)/(lambda^2-delta).
    def derivative(L):
        top=K.plus(K.minus(K.power(L,2),K.mult(K.times(aplus,L),2)),delta)
        bottom=K.power(K.minus(K.power(L,2),delta),2)
        return K.divide(K.times(K.mult(delta,2),top),bottom)
    cp_a=K.invert(derivative(aplus))
    cm_a=K.invert(K.mult(delta,-2))  # derivative X(1/v) at v=0
    cp_b=K.invert(K.times(K.minus(bplus,bminus),derivative(bplus)))
    cm_b=K.invert(K.times(K.minus(bminus,bplus),derivative(bminus)))
    values=[]
    for x,cp,cm in [(a,cp_a,cm_a),(b,cp_b,cm_b)]:
        # The smoothing perturbation is evaluated directly, not reduced via g.
        R=K.minus(K.plus(K.mult(K.power(x,3),-20),K.mult(x,36)),K.z(20))
        h=K.plus(K.minus(K.power(x,2),K.mult(x,2)),K.z(5))
        gp=K.plus(K.mult(x,2),one)
        H2=K.times(delta,K.times(h,K.power(gp,2)))
        kap=K.divide(K.mult(K.times(K.times(cp,cm),K.times(delta,R)),-1),K.mult(H2,4))
        values.append(kap)
        check(K.plus(K.plus(K.power(x,2),x),K.z(-1))==K.zero,'actual node polynomial')
        check(R==K.mult(x,-4),'smoothing derivative at actual node')
    ka,kb=values
    cross=K.divide(K.minus(aplus,bplus),K.minus(aplus,bminus))
    check(K.divide(kb,ka)==cross,'diagonal ratio/cross-ratio')
    return {key:K.phi_output(v) for key,v in [('kappa_a',ka),('kappa_b',kb),('cross_ratio',cross),
             ('cp_a',cp_a),('cm_a',cm_a),('cp_b',cp_b),('cm_b',cm_b)]}


def sieve(n):
    a=[True]*(n+1);a[0]=a[1]=False
    for p in range(2,math.isqrt(n)+1):
        if a[p]:
            for j in range(p*p,n+1,p):a[j]=False
    return [p for p in range(11,n+1) if a[p]]


def direct_log(q,descending=True):
    candidates=range(q-1,1,-1) if descending else range(2,q)
    for g in candidates:
        logs={};x=1
        for i in range(q-1):
            if x in logs:break
            logs[x]=i;x=x*g%q
        if len(logs)==q-1 and x==1:return g,logs
    raise AssertionError('no generator')


def count_by_logs(q):
    g,logs=direct_log(q)
    c7=c49=0;digest=hashlib.sha256()
    off49=logs[3]+9*logs[5];off7=logs[3]+2*logs[5]
    for C in range(1,q):
        target=off49-35*logs[C]
        for A in range(1,q):
            if (logs[A]+off7)%7==0:c7+=1
            if (logs[A]+target)%49==0:
                c49+=1;digest.update(struct.pack('<HH',A,C))
    return {'q':q,'all_unit_pairs':(q-1)**2,'full7_pairs':c7,'full49_pairs':c49,
        'full49_pairs_sha256':digest.hexdigest(),'A_per_C0_level49':(q-1)//49,'A_per_C0_level7':(q-1)//7}


def hensel_by_digits(q,A,N):
    target=q**49-A**3
    b0=next(b for b in range(1,q) if (pow(b,5,q)-target)%q==0)
    check(sum((pow(b,5,q)-target)%q==0 for b in range(q))==1,'unique initial fifth root')
    b=b0;mod=q
    for j in range(1,N):
        need_divisible=target-b**5
        check(need_divisible%mod==0,'digit-lift hypothesis')
        correction=(need_divisible//mod)*pow(5*pow(b,4,q),-1,q)%q
        b+=mod*correction;mod*=q
        check((b**5-target)%mod==0,'digit-lift equation')
    return b0,b


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();data=json.loads(a.primary.read_text())
    check(data['symbolic']==inverse_conic_computation(Root5()),'rational smoothing constants mismatch')
    expected_algebra={'f0_coefficients':[5,-12,0,10,0,0,1],
      'smoothing_derivative_coefficients':[-20,36,0,-20],'smoothing_derivative_mod_g':[0,-4],
      'exact_scaling_instances':60,'theta_exponents':[-3,7,-3,-5],
      'E7_exponents':[1,0,1,4],'E49_exponents':[1,-35,1,18],
      'marked_matrix':[[1,-2],[-2,-1]],'marked_matrix_square':[[5,0],[0,5]],
      'elliptic_leading_coefficient':'-1/64'}
    # Independently test the polynomial identity at enough rational arguments
    # to determine a degree-six polynomial, and its linear node remainder.
    for x in range(-4,5):
        check(x**6+10*x**3-12*x+5==(x*x+x-1)**2*(x*x-2*x+5),'special-fiber polynomial identity')
        check((-20*x**3+36*x-20)-(-4*x)==(-20*x+20)*(x*x+x-1),'exact smoothing remainder identity')
    check(data['algebra']==expected_algebra,'algebra certificate mismatch')
    rows=[]
    for q in sieve(2000):
        roots_d=[z for z in range(q) if z*z%q==5]
        phi_roots=sorted((1+z)*pow(2,-1,q)%q for z in roots_d)
        for root in (phi_roots if phi_roots else [None]):
            K=Root5(q,None if root is None else (2*root-1)%q)
            row={'q':q,'phi_root':root,**inverse_conic_computation(K),
                 'phi_power_status':{str(m):K.power_test(K.phi,m) for m in (7,49,343)}}
            rows.append(row)
    check(data['fields']==rows,'complete residue field records mismatch')
    expected_counts=[count_by_logs(q) for q in [197,883,1373,1667]]
    check(data['unit_pair_counts']==expected_counts,'all-unit-pair enumeration mismatch')
    witness_rows=[]
    for q in [197,883,1373,1667]:
        g,_=direct_log(q,descending=False)
        A0=pow(3*5**9,-1,q)
        for kind,exp in [('positive',0),('seventh_not_fortyninth',7),('fails_seventh',1)]:
            A=A0*pow(g,exp,q)%q
            b0,b=hensel_by_digits(q,A,52)
            P7={pow(z,7,q) for z in range(1,q)}
            P49={pow(z,49,q) for z in range(1,q)}
            flags={'7':75*A%q in P7,'49':3*pow(5,9,q)*A%q in P49}
            check(flags==({'7':True,'49':True} if exp==0 else {'7':True,'49':False} if exp==7 else {'7':False,'49':False}), 'independent witness power flags')
            witness_rows.append({'q':q,'kind':kind,'primitive_root':g,'A_integer':A,'B_residue':b0,
              'B_mod_q52':str(b),'C_integer':str(q**7),'C_unit':1,'C_valuation':7,
              'root_precision':52,'newton_stages':[1,2,4,8,16,32,52],
              'equation_residue':0,'natural_monodromy_content':2,'full_torsion_by_period_test':flags})
    check(data['witnesses']==witness_rows,'complete Hensel witness mismatch')
    check(data['interpretation']=={'local_period_criterion_only':True,'global_beta_constructed':False,
        'global_integer_solution_constructed':False,'new_survivor_prime_exclusion':False,
        'analytic_smoothing_comparison_is_written_not_computational':True},'interpretation altered')
    check(data['coverage']=={'residue_fields':445,'unit_pairs':5474280,'full49_pairs':111720,
      'local_witnesses':12,'positive_local_witnesses':4,'seventh_not_fortyninth_controls':4,
      'fails_seventh_controls':4},'coverage mismatch')
    result={'schema':'komorebi.beal.block60.independent.v1','status':'PASS_INDEPENDENT_FINITE_CHECKS',
      'implementation':'sqrt5 basis, inverse-conic derivatives, descending-generator logs, digit Hensel',
      'coverage':data['coverage'],'unit_pair_counts':expected_counts,
      'primary_bytes_sha256':hashlib.sha256(a.primary.read_bytes()).hexdigest(),
      'imports_primary_code':False,'independent_mathematical_review':False,
      'analytic_comparison_formally_verified':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status']);print(json.dumps(result['coverage'],sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
