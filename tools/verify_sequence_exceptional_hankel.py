"""Standard-library replay of the coordinate-boundary classification."""
import argparse,itertools,json,time
from fractions import Fraction as F
from math import comb,factorial
from pathlib import Path
import verify_sequence_sharp_quadratic as parent
from sequence_differential_hankel import structured_differential_hankel
from test_sequence_differential_hankel import direct_determinant

ONE={(0,0):F(1)}
def atom(i=0,j=0,c=1):return {} if not c else {(i,j):F(c)}
def add(*items):
    out={}
    for item in items:
        for key,value in item.items():out[key]=out.get(key,F(0))+value
    return {key:value for key,value in out.items() if value}
def scale(p,c):return {key:value*c for key,value in p.items() if value*c}
def mul(a,b):
    out={}
    for (i,j),x in a.items():
        for (k,l),y in b.items():out[i+k,j+l]=out.get((i+k,j+l),F(0))+x*y
    return {key:value for key,value in out.items() if value}
def power(p,k):
    out=ONE
    for _ in range(k):out=mul(out,p)
    return out
def decode(rows):
    out={};seen=set()
    for i,j,value in rows:
        assert type(i) is type(j) is int and i>=0 and j>=0 and (i,j) not in seen
        seen.add((i,j));value=F(value)
        if value:out[i,j]=value
    return out
def evaluate(p,t):
    degree=max((j for i,j in p),default=0);out=[F(0)]*(degree+1)
    for (i,j),value in p.items():out[j]+=value*t**i
    return trim(out)
def trim(p):
    p=list(p)
    while len(p)>1 and not p[-1]:p.pop()
    return p
def umul(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return trim(out)
def upower(p,k):
    out=[F(1)]
    for _ in range(k):out=umul(out,p)
    return out
def uadd(a,b):return trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def det_poly(matrix):
    size=len(matrix);out={}
    for permutation in itertools.permutations(range(size)):
        sign=(-1)**sum(permutation[i]>permutation[j] for i in range(size) for j in range(i+1,size))
        term=ONE
        for i,j in enumerate(permutation):term=mul(term,matrix[i][j])
        out=add(out,scale(term,sign))
    return out

def moment_rho(k,which):
    if k%2:return F(0)
    m=k//2
    return F(m*comb(2*m,m),2) if which==1 else F(m*(m-1)*comb(2*m,m),12)
def raw1(n):
    if n==0:return [F(-4)]
    if n==1:return [F(0),F(-2)]
    out=[F(0)]*(n+1)
    for degree,c in [(n,n-2),(n-2,-n)]:
        for i,value in enumerate(parent.chebyshev(degree)):out[i]+=c*value
    return trim(out)
def raw2(n):
    if n==0:return [F(24)]
    if n in (1,3):return [F(0),F(12)]
    if n==2:return [F(8),F(0),F(4)]
    if n==4:return [F(24)]
    return [value*(n-3)*(n-4) for value in parent.pn(n)]
def reduce_x(poly,R):
    out=[scale(ONE,F(value)) for value in poly];degree=len(R)-1
    assert R[-1]==ONE
    while len(out)>degree:
        k=len(out)-1;lead=out.pop()
        for j in range(degree):out[k-degree+j]=add(out[k-degree+j],scale(mul(lead,R[j]),-1))
    return out+[{}]*(degree-len(out))
def boundary_models():
    B,C=atom(1),atom(0,1);quad=[C,B,ONE];cubic=[{},scale(B,-1),{},ONE]
    count=0
    for which,R,raw,indices,kind in [(1,quad,raw1,[1,2],'rho1_quad'),
                                  (2,quad,raw2,[1,2,3,4],'rho2_quad'),
                                  (2,cubic,raw2,[1,2,3,4],'rho2_odd')]:
        def mu(k):return add(*(scale(value,moment_rho(k+j,which)) for j,value in enumerate(R)))
        for N in indices:
            degree=len(R)-1
            columns=[reduce_x(raw(N+j),R) for j in range(degree)]
            determinant=det_poly([[columns[j][i] for j in range(degree)] for i in range(degree)])
            factor=F((-2)**N,16) if kind=='rho1_quad' else F(2**N*(N-1)*(N-2),4608) if kind=='rho2_quad' else F((-2)**N,4608)
            assert scale(determinant,factor)==det_poly([[mu(i+j) for j in range(N)] for i in range(N)]),(kind,N)
            count+=1
        columns=[reduce_x(raw(j),R) for j in range(len(R)-1)]
        constant=det_poly([[columns[j][i] for j in range(len(R)-1)] for i in range(len(R)-1)])
        factor=F(1,16) if kind=='rho1_quad' else F(2,4608) if kind=='rho2_quad' else F(1,4608)
        expected=F(1,2) if kind=='rho1_quad' else F(1,8) if kind=='rho2_quad' else F(1,4)
        assert scale(constant,factor)==scale(ONE,expected)
    return count
def rho1_audit():
    for n in range(3,17):
        t=F(2*n-3,2);p=[F(1)]
        for k in range(n):
            derivative=[j*p[j] for j in range(1,len(p))]
            first=parent.poly_mul([-4,0,1],derivative);second=[F(0)]+[2*(t-k)*x for x in p]
            p=[(first[j] if j<len(first) else 0)+(second[j] if j<len(second) else 0) for j in range(max(len(first),len(second)))]
        leading=F(factorial(2*n-3),factorial(n-3));assert p[-1]==leading
        p=[value/leading for value in p]
        assert trim(p)==trim([value/F(n-2) for value in raw1(n)])
        for j in range(n):assert not sum(value*moment_rho(i+j,1) for i,value in enumerate(p))
        assert sum(x*y*moment_rho(i+j,1) for i,x in enumerate(p) for j,y in enumerate(p))==F(-2*n,n-2)
    assert direct_determinant([[moment_rho(i+j,1) for j in range(3)] for i in range(3)])==-1
    # Complete Laurent ODE identity with z**n factored out.
    n=parent.mono(1);one=parent.ONE;z=parent.mono(z=1);inv=parent.mono(z=-1)
    plus,mult,sc,minus=parent.plus,parent.mul,parent.scale,parent.minus
    shift=lambda k:plus(n,sc(one,k))
    L=minus(shift(-2),mult(n,parent.mono(z=-2)));dx=minus(one,parent.mono(z=-2))
    x=plus(z,inv);fz=plus(parent.diff(L,1),mult(mult(n,L),inv))
    fzz=plus(parent.diff(parent.diff(L,1),1),sc(mult(mult(n,parent.diff(L,1)),inv),2),mult(mult(mult(n,shift(-1)),L),parent.mono(z=-2)))
    ode=minus(minus(mult(minus(parent.power(x,2),sc(one,4)),minus(mult(fzz,dx),mult(fz,parent.diff(dx,1)))),mult(mult(x,fz),parent.power(dx,2))),mult(mult(mult(n,shift(-2)),L),parent.power(dx,3)))
    assert not ode

def base(label):
    t,z=atom(1),atom(0,1);z2=atom(0,2)
    if label=='identity':return mul(add(ONE,scale(z,-2)),add(ONE,scale(z,-4),scale(mul(t,z),4),scale(z2,4)))
    if label=='constant':return add(ONE,scale(z,-8),scale(z2,24),scale(mul(t,z2),4),atom(0,3,-32),atom(0,4,16))
    if label=='zero_a':return add(ONE,scale(z,8),scale(z2,24),scale(mul(t,z2),4),atom(0,3,32),atom(0,4,16))
    assert label=='pure_odd'
    return mul(add(ONE,scale(z,4)),add(ONE,scale(z,8),scale(mul(t,z),-96),scale(mul(power(t,2),z),144),scale(z2,16)))
def obstruction(label):
    t=atom(1)
    if label=='identity':return scale(mul(power(t,5),add(t,scale(ONE,-2))),8)
    if label=='constant':return scale(mul(power(t,3),add(t,scale(ONE,16))),2)
    if label=='zero_a':return scale(mul(power(t,7),power(add(t,scale(ONE,16)),3)),80)
    return scale(mul(mul(power(t,10),power(add(scale(t,3),scale(ONE,-2)),7)),power(add(scale(t,3),scale(ONE,-1)),7)),79254226206720)
def expected_special(label,t):
    if label=='identity':return [1,-2] if not t else umul(upower([1,-2],3),upower([1,2],4))
    if label=='constant':return [1,-2] if not t else umul(upower([1,2],4),upower([1,-12,4],3))
    if label=='zero_a':return upower([1,2],3) if not t else umul(upower([1,-2],8),upower([1,12,4],7))
    if not t:return upower([1,4],3)
    return umul(upower([1,4],7),upower([1,-4],6)) if t==F(1,3) else upower([1,4],9)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();started=time.perf_counter();rho1_audit();boundary=boundary_models()
    data=json.loads(Path(args.certificate).read_text());families=data['families']
    assert [item['family'] for item in families]==['identity','constant','zero_a','pure_odd']
    degrees=[9,12,28,21];exponents=[3,3,7,7];continuations=[F(1,2),F(1,2),F(1,8),F(1,4)]
    expected_nodes=[list(range(10)),[j*j for j in range(7)],[j*j for j in range(15)],list(range(43))]
    expected_critical=[[F(0),F(2)],[F(0),F(-16)],[F(0),F(-16)],[F(0),F(1,3),F(2,3)]]
    nodes_checked=coefficients_checked=direct_checks=specials=0
    for family,degree,exponent,cont,nodes,critical in zip(families,degrees,exponents,continuations,expected_nodes,expected_critical):
        label=family['family'];N=decode(family['numerator']);Q=decode(family['base_denominator']);assert Q==base(label)
        assert family['exponent']==exponent and list(map(F,family['interpolation_nodes']))==nodes
        for (i,j),value in N.items():
            bound=2*j if label=='pure_odd' else j if label=='identity' else j//2
            assert j<=degree and i<=bound
        D=power(Q,exponent);assert max(j for i,j in D)==degree
        leading=lambda p:{(i,0):value for (i,j),value in p.items() if j==degree}
        assert leading(N)==scale(leading(D),1-cont)
        U,V=decode(family['bezout_u']),decode(family['bezout_v'])
        H={(i,0):F(c) for i,c in family['obstruction'] if F(c)}
        assert H==obstruction(label) and add(mul(U,N),mul(V,Q))==H,label
        for index,node in enumerate(nodes):
            if label=='identity':weights,operator,last=[1,node],[1,0],degree
            elif label=='constant':weights,operator,last=[1,0],[1,index],degree
            elif label=='zero_a':weights,operator,last=[0,F(1,2)],[1,F(index,3)],degree
            else:weights,operator,last=[1,node],[0,1],2*degree
            values=structured_differential_hankel(weights,operator,last)
            original=values
            if label=='pure_odd':assert not any(values[1::2]);values=values[::2]
            ds=evaluate(D,F(node));ns=evaluate(N,F(node))
            actual=[sum(ds[j]*values[k-j] for j in range(min(k,len(ds)-1)+1)) for k in range(degree+1)]
            assert trim(actual)==ns,(label,node);nodes_checked+=1;coefficients_checked+=degree+1
            a,b=map(F,weights);u,v=map(F,operator)
            def moment(k):
                m=k//2
                return u*(a+b*m)*comb(2*m,m) if not k%2 else v*(2*m+1)*(a+b*m)*comb(2*m,m)
            sizes=list(range(min(12,last)+1))
            if index==1 and last>12:sizes.append(last)
            for size in sizes:
                assert original[size]==direct_determinant([[moment(i+j) for j in range(size)] for i in range(size)])
                direct_checks+=1
        assert [F(item['parameter']) for item in family['specializations']]==critical
        for item in family['specializations']:
            t=F(item['parameter']);Nr,Dr=map(lambda key:list(map(F,item[key])),['numerator','denominator'])
            assert Dr==expected_special(label,t) and Dr[0]==1
            assert item['order_in_gf_variable']==len(Dr)-1 and len(Nr)==len(Dr) and Nr[-1]
            assert umul(Nr,evaluate(D,t))==umul(evaluate(N,t),Dr)
            ur,vr=map(lambda key:list(map(F,item[key])),['bezout_u','bezout_v'])
            assert uadd(umul(ur,Nr),umul(vr,Dr))==[1]
            specials+=1
    # Closed intersection formulas, checked in the actual monomial moments.
    for a,b,u,v,kind in [(0,1,1,0,'rho1'),(0,1,0,1,'rho2_odd'),(1,0,0,1,'constant_odd')]:
        values=structured_differential_hankel([a,b],[u,v],32)
        for n in range(1,33):
            if kind=='rho1':expected=F((-4*b*u)**n*(n-1)*(n-2),16)
            elif n%2:expected=F(0)
            elif kind=='rho2_odd':expected=F((-144*b*b*v*v)**(n//2)*(n-1)**2*(n-2)**2*(n-3)**2,576)
            else:expected=F((-4*a*a*v*v)**(n//2)*(n-1)**2,4)
            assert values[n]==expected,(kind,n)
    report={'outcome':'Coordinate-boundary polynomial certificates and defining-object checks passed',
        'review':'project self-review, not independent review','rho1_ode':True,'rho1_norm_and_orthogonality_indices':[3,16],
        'complete_small_boundary_identities':boundary,'parameter_polynomial_families':4,
        'complete_parameter_nodes':nodes_checked,'numerator_coefficient_checks':coefficients_checked,
        'cleared_parameter_bezout_identities':4,'critical_reduced_gf_and_bezout_identities':specials,
        'direct_monomial_determinants':direct_checks,'intersection_formula_checks':96,
        'boundary_orders':[0,1,3,6,7,9,10,12,14,18,22,26,28,42],
        'scope':'Complete boundary classification requires the written smaller-recurrence derivations, coefficient degree bounds and the verified polynomial identities. The fully nonzero locus is not classified.',
        'elapsed_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))

if __name__=='__main__':main()
