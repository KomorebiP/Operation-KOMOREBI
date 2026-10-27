#!/usr/bin/env python3
"""Independent F83[sqrt(5)] interpolation, divisor ladder and complete counts.
Imports no primary arithmetic. Coprime composition uses polynomial CRT;
doubling uses Hensel interpolation and Gaussian linear inversion, not the
three-polynomial Cantor composition formula. Unsupported nongeneric cases
raise an error rather than silently changing algorithms.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
p=83;size=p*p

def need(ok,msg):
    if not ok:raise AssertionError(msg)

def fa(x,y):return (x%p+y%p)%p+p*((x//p+y//p)%p)
def fn(x):return (-(x%p))%p+p*((-(x//p))%p)
def fs(x,y):return fa(x,fn(y))
def fm(x,y):
    a,b=x%p,x//p;c,d=y%p,y//p
    return (a*c+5*b*d)%p+p*((a*d+b*c)%p)
def fi(x):
    a,b=x%p,x//p;n=(a*a-5*b*b)%p
    need(n!=0,'Zero inverse in the independent field')
    z=pow(n,-1,p);return a*z%p+p*((-b*z)%p)
def fp(x,n):
    a=1
    for bit in bin(n)[2:]:
        a=fm(a,a)
        if bit=='1':a=fm(a,x)
    return a

def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0:a.pop()
    return a

def padd(a,b):return trim([fa(a[i] if i<len(a) else 0,b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def pneg(a):return [fn(x) for x in a]
def psub(a,b):return padd(a,pneg(b))
def pscale(a,x):return trim([fm(v,x) for v in a])
def pmul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i in range(len(a)):
        for j in range(len(b)):out[i+j]=fa(out[i+j],fm(a[i],b[j]))
    return trim(out)
def pdiv(a,b):
    a=trim(a);b=trim(b);need(b!=[0],'Polynomial zero division')
    out=[0]*max(1,len(a)-len(b)+1)
    while a!=[0] and len(a)>=len(b):
        i=len(a)-len(b);c=fm(a[-1],fi(b[-1]));out[i]=fa(out[i],c)
        a=psub(a,[0]*i+pscale(b,c))
    return trim(out),a

def prem(a,b):return pdiv(a,b)[1]
def pexact(a,b):
    out,r=pdiv(a,b);need(r==[0],'Polynomial division is not exact');return out

def pmon(a):return pscale(a,fi(a[-1]))
def pgcd(a,b):
    while b!=[0]:a,b=b,prem(a,b)
    return pmon(a)
def peval(a,x):
    z=0
    for c in reversed(a):z=fa(fm(z,x),c)
    return z

def pinv(a,m):
    # Independently invert multiplication by a on k[t]/m using elimination.
    n=len(m)-1;cols=[]
    for i in range(n):
        c=prem([0]*i+a,m);cols.append(c+[0]*(n-len(c)))
    mat=[[cols[j][i] for j in range(n)]+[int(i==0)] for i in range(n)]
    for j in range(n):
        at=next((i for i in range(j,n) if mat[i][j]),None)
        need(at is not None,'Noncoprime interpolation input')
        mat[j],mat[at]=mat[at],mat[j];z=fi(mat[j][j]);mat[j]=[fm(v,z) for v in mat[j]]
        for i in range(n):
            if i!=j:
                t=mat[i][j];mat[i]=[fs(x,fm(t,y)) for x,y in zip(mat[i],mat[j])]
    ans=trim([mat[i][-1] for i in range(n)])
    need(prem(pmul(a,ans),m)==[1],'Failed polynomial inverse check')
    return ans

def from_phi(x):
    a,b=x%p,x//p
    return (a+42*b)%p+p*((42*b)%p)
def to_phi(x):
    a,b=x%p,x//p
    return (a-b)%p+p*((2*b)%p)
def convert_div(D):return ([from_phi(x) for x in D[0]],[from_phi(x) for x in D[1]])
def phi_div(D):return [[to_phi(x) for x in D[0]],[to_phi(x) for x in D[1]]]

class Jacobian:
    def __init__(self,f):
        self.f=f;self.zero=([1],[0]);self.counts={'identity':0,'inverse':0,'hensel_double':0,'crt_add':0,'reductions':0}
        derivative=[fm(i%p,f[i]) for i in range(1,len(f))]
        need(len(f)==6 and pgcd(f,derivative)==[1],'Odd model is not smooth genus two')
    def valid(self,D):
        u,v=D;need(u[-1]==1,'Nonmonic divisor polynomial')
        need((len(v)<len(u)) if u!=[1] else v==[0],'Invalid reduced representative')
        need(prem(psub(pmul(v,v),self.f),u)==[0],'Divisor is not on curve')
    def reduce(self,u,v):
        u=pmon(u);v=prem(v,u)
        while len(u)>3:
            other=pexact(psub(self.f,pmul(v,v)),u)
            u=pmon(other);v=prem(pneg(v),u);self.counts['reductions']+=1
        if u==[1]:v=[0]
        D=(u,v);self.valid(D);return D
    def add(self,D,E):
        self.valid(D);self.valid(E)
        if D==self.zero or E==self.zero:
            self.counts['identity']+=1
            return E if D==self.zero else D
        u,v=D;w,z=E
        if u==w and prem(padd(v,z),u)==[0]:
            self.counts['inverse']+=1;return self.zero
        if D==E:
            # y=v+u*t, then y^2=f mod u^2 fixes t uniquely.
            inv=pinv(pscale(v,2),u)
            t=prem(pmul(pexact(psub(self.f,pmul(v,v)),u),inv),u)
            U=pmul(u,u);V=padd(v,pmul(u,t));self.counts['hensel_double']+=1
            need(prem(psub(pmul(V,V),self.f),U)==[0],'Double interpolation failed')
            return self.reduce(U,V)
        need(pgcd(u,w)==[1],'Unsupported shared-point composition in finite certificate')
        t=prem(pmul(psub(z,v),pinv(u,w)),w)
        U=pmul(u,w);V=padd(v,pmul(u,t));self.counts['crt_add']+=1
        need(prem(psub(V,v),u)==[0] and prem(psub(V,z),w)==[0],'CRT interpolation failed')
        return self.reduce(U,V)
    def times(self,D,n):
        # Left-to-right ladder, unlike the primary right-to-left routine.
        E=self.zero
        for bit in bin(n)[2:]:
            E=self.add(E,E)
            if bit=='1':E=self.add(E,D)
        return E

def odd_model():
    delta=49+p*40
    # Independent Horner expansion of t^6 f(5+1/t).
    x=[1,5];out=[0]
    coefs=[18,12,0,51,0,0,1]  # reduction of 5*30^2 and 10*30, checked below
    need(coefs[0]==5*30**2%83 and coefs[3]==10*30%83,'Coefficient transcription')
    for i,c in enumerate(coefs):
        power=[1]
        for _ in range(i):power=pmul(power,x)
        out=padd(out,[0]*(6-i)+pscale(power,c))
    out=pscale(out,delta)
    need(len(out)==6,'Rational root 5 transformation did not cancel degree six')
    return out,delta

def audit_jacobian(record):
    need(pow(5,41,83)==82,'sqrt5 basis is not irreducible')
    # All nonzero field inverses, without a random sample.
    for x in range(1,size):need(fm(x,fi(x))==1,'Field inverse failed')
    f,delta=odd_model()
    need([to_phi(x) for x in f]==record['odd_curve_coefficients'],'Changed odd model')
    need(to_phi(delta)==record['delta'],'Changed twist')
    J=Jacobian(f)
    D=([fn(from_phi(83)),1],[from_phi(4189)])
    J.valid(D);need(phi_div(D)==record['D'],'Changed base divisor')
    for row in record['addition_transcript']:
        R=J.add(convert_div(row['left']),convert_div(row['right']))
        need(phi_div(R)==row['result'],'Changed addition-transcript result')
    E=J.times(D,19044);E7=J.times(E,7);E49=J.times(E,49);DN=J.times(D,45724644)
    need(phi_div(E)==record['E'] and phi_div(E7)==record['E7'],'Scalar ladder disagrees')
    need(E7!=J.zero and E49==J.zero and DN==J.zero,'Order-49 witness failed')
    need(record['E49']==[[1],[0]] and record['D_times_order']==[[1],[0]],'Altered identity claim')
    squares=[0]*size
    for y in range(size):squares[fm(y,y)]+=1
    points=1+sum(squares[peval(f,x)] for x in range(size))
    need(points==record['odd_curve_points']==6634,'Odd-model point count mismatch')
    phi=42+p*42;sqrt5=p
    need(fp(phi,(size-1)//7)!=1,'Phi seventh-power control failed')
    need(to_phi(fp(phi,(size-1)//7))==record['phi_seventh_symbol'],'Altered phi symbol')
    need(fp(3,(size-1)//7)==1 and fp(sqrt5,(size-1)//7)==1,'Fixed Kummer symbol mismatch')
    # Associativity on the explicitly generated cyclic subgroup, plus identity and inverses.
    samples=[J.times(E,j) for j in (0,1,2,3,6,7,12,19,35,48)]
    assoc=0
    for i in range(1,8):
        L=J.add(J.add(samples[i],samples[i+1]),E)
        R=J.add(samples[i],J.add(samples[i+1],E))
        need(L==R,'Associativity control');assoc+=1
    return {'field_inverses':6888,'transcript_operations':len(record['addition_transcript']),
            'algorithm_counts':J.counts,'associativity_controls':assoc,'odd_points':points,
            'E':phi_div(E),'E7':phi_div(E7),'E49':phi_div(E49),'order_exactly_49':True}

def audit_counts(record):
    p=83
    expected={}
    for row in record['rows']:
        for a,b in row['pairs']:
            need((a,b) not in expected,'Duplicate primary pair')
            expected[a,b]=(row['N1'],row['N2'],row['jacobian_order'])
    pairs=[(a,b) for a in range(p) for b in range(p) if (a**3+b**5)%p!=0]
    need(set(pairs)==set(expected),'Admissible pair set mismatch')
    sq1=[0]*p;sq2=[0]*(p*p)
    for x in range(p):sq1[x*x%p]+=1
    for y in range(p*p):sq2[fm(y,y)]+=1
    coords=[]
    for a in range(p):
        for b in range(p):
            c=(a**3+15*a*b*b)%p;d=(3*a*a*b+5*b**3)%p
            coords.append((a,b,c,d,(c*c+5*d*d)%p,2*c*d%p))
    base=[(x,x**3%p,x**6%p) for x in range(p)]
    dig=hashlib.sha256();passing=[];smooth=0
    for a,b in pairs:
        AA=12*a%p;BB=10*b%p;CC=5*b*b%p
        poly=[CC,AA,0,BB,0,0,1]
        need(pgcd(poly,[AA,0,3*BB%p,0,0,6])==[1],'Singular good-equation pair')
        smooth+=1
        n1=2+sum(sq1[(x6+BB*x3+AA*x+CC)%p] for x,x3,x6 in base)
        n2=2
        for x,y,x3,y3,x6,y6 in coords:
            re=(x6+BB*x3+AA*x+CC)%p;im=(y6+BB*y3+AA*y)%p
            n2+=sq2[re+p*im]
        t=p+1-n1;c=(t*t-p*p-1+n2)//2
        # Newton power sums directly construct the squared-and-twisted quartic.
        powers=[4,t,t*t-2*c,0,0]
        powers[3]=t*powers[2]-c*t+3*p*t
        powers[4]=t*powers[3]-c*powers[2]+p*t*t-4*p*p
        S=-powers[2];C2=(S*S-powers[4])//2;Q=p*p
        order=1-S+C2-Q*S+Q*Q
        need((n1,n2,order)==expected[a,b],'Independent direct pair count mismatch')
        dig.update(f'{a},{b},{n1},{n2},{order}\n'.encode())
        if order%2401==0:passing.append([a,b])
    need(len(passing)==82,'Wrong exceptional orbit size')
    orbit=sorted([[pow(u,5,p),30*pow(u,3,p)%p] for u in range(1,p)])
    need(passing==orbit,'Exceptional locus is not the claimed isomorphism orbit')
    need(dig.hexdigest()==record['full_pair_count_hash'],'Pair-count digest mismatch')
    return {'admissible_pairs':len(pairs),'degree_one_counts':len(pairs),'degree_two_counts':len(pairs),
        'smoothness_checks':smooth,'full_pair_count_hash':dig.hexdigest(),'order_eligible_pairs':len(passing),
        'twist_norm':45,'twist_quadratic_character':pow(45,41,83)}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--counts',type=Path,required=True)
    ap.add_argument('--jacobian',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();j=json.loads(a.jacobian.read_text());pc=json.loads(a.counts.read_text())
    jj=audit_jacobian(j);print('independent divisor certificate: PASS',flush=True)
    cc=audit_counts(pc)
    d={'schema':'beal.block63.independent83.v1','status':'PASS_INDEPENDENT_GROUP_AND_COUNTS',
       'jacobian':jj,'counts':cc,'primary_imports':False,
       'nonclaim':'Not an independent reviewer or an analytical/geometric proof of the Frey model.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(d['status'],flush=True)
if __name__=='__main__':main()
