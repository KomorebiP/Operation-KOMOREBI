"""Exact quartic boundary and uniform mixed-linear recurrence replay."""
import argparse,itertools,json,time
from fractions import Fraction as F
from math import comb,isqrt
from pathlib import Path
from sequence_differential_hankel import structured_differential_hankel
from test_sequence_differential_hankel import direct_determinant,chebyshev

ONE={(0,0,0,0):F(1)}
def add(*items):
    out={}
    for item in items:
        for key,value in item.items():out[key]=out.get(key,F(0))+value
    return {key:value for key,value in out.items() if value}
def scale(p,x):return {key:value*x for key,value in p.items() if value*x}
def mul(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():
            key=tuple(u+v for u,v in zip(i,j));out[key]=out.get(key,F(0))+x*y
    return {key:value for key,value in out.items() if value}
def det_poly(matrix):
    size=len(matrix);out={}
    for permutation in itertools.permutations(range(size)):
        sign=(-1)**sum(permutation[i]>permutation[j] for i in range(size) for j in range(i+1,size))
        term=ONE
        for i,j in enumerate(permutation):term=mul(term,matrix[i][j])
        out=add(out,scale(term,sign))
    return out
def nu(k):
    if k%2:return F(0)
    m=k//2;return F(m*(m-1)*comb(2*m,m),12)
def raw_P(N):
    if N==2:return [8,0,4]
    if N==3:return [0,12]
    if N==4:return [24]
    out=[F(0)]*(N+1)
    for degree,coefficient in [(N,(N-3)*(N-4)),(N-2,-2*N*(N-4)),(N-4,N*(N-1))]:
        for i,value in enumerate(chebyshev(degree)):out[i]+=coefficient*value
    return out
def boundary():
    variables=[]
    for i in range(4):
        key=[0]*4;key[i]=1;variables.append({tuple(key):F(1)})
    def reduce(poly):
        out=[scale(ONE,F(x)) for x in poly]
        while len(out)>4:
            k=len(out)-1;leading=out.pop()
            for j in range(4):out[k-4+j]=add(out[k-4+j],scale(mul(leading,variables[j]),-1))
        return out+[{}]*(4-len(out))
    def moment(k):return add(scale(ONE,nu(k+4)),*(scale(variables[j],nu(k+j)) for j in range(4)))
    for N in range(2,5):
        columns=[reduce(raw_P(N+j)) for j in range(4)]
        matrix=[[columns[j][i] for j in range(4)] for i in range(4)]
        actual=det_poly([[moment(i+j) for j in range(N)] for i in range(N)])
        assert scale(det_poly(matrix),2**N)==scale(actual,4608*N*(N-1)),N
    # Polynomial boundary limits, after the vanishing column is removed.
    def coefficient_matrix(columns):
        return [[F(col[i]) if i<len(col) else F(0) for col in columns] for i in range(4)]
    J=[0,8,0,-2]
    assert direct_determinant(coefficient_matrix([[0,12],[8,0,4],J,[24]]))==2304
    assert direct_determinant(coefficient_matrix([[24],[0,12],[8,0,4],J]))==-2304

def product(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def power(a,k):
    out=[F(1)]
    for _ in range(k):out=product(out,a)
    return out
def resultant_quartic(R,C):
    # Fixed degree four for R, even when its leading coefficients vanish.
    k=len(C)-1;rows=[]
    for i in range(k):rows.append([0]*i+list(reversed(R))+[0]*(k-1-i))
    for i in range(4):rows.append([0]*i+list(reversed(C))+[0]*(3-i))
    return direct_determinant(rows)
def base_polynomial(R):
    traces=[F(0)]+[2**k*resultant_quartic(R,chebyshev(k)) for k in range(1,17)]
    coefficients=[F(1)]
    for j in range(1,17):coefficients.append(-sum(coefficients[j-k]*traces[k] for k in range(1,j+1))/j)
    assert coefficients[1]==-2*R[0]
    assert coefficients[-1]==(2*R[4])**16
    for j in range(9):assert coefficients[16-j]==(2*R[4])**(16-2*j)*coefficients[j]
    return coefficients

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--sample-certificate',required=True)
    args=parser.parse_args();started=time.perf_counter();boundary()
    expected=[1,-16,384,1600,-21568,129792,649216,-2378752,9340416,-9515008,10387456,8306688,-5521408,1638400,1572864,-262144,65536]
    assert base_polynomial([8,4,-6,2,1])==expected
    sample=json.loads(Path(args.sample_certificate).read_text())
    assert sample['weights']==[1,1] and sample['operator']==[1,2]
    cases=[(1,1,1,2),(2,-1,1,1),(0,1,1,2),(1,1,0,1),(1,1,1,0),
           (2,0,1,3),(0,0,1,2),(1,1,0,0),(1,-1,2,-1),(1,2,-1,2)]
    residues=direct=relations=0;last=132
    for a,b,u,v in cases:
        R=[u*(16*a-8*b),v*(-4*a+6*b),u*(-8*a+2*b),v*a,u*a]
        def moment(k):
            m=k//2
            return u*(a+b*m)*comb(2*m,m) if not k%2 else v*(2*m+1)*(a+b*m)*comb(2*m,m)
        for k in range(33):assert sum(R[j]*nu(k+j) for j in range(5))==moment(k);relations+=1
        coeff=power(list(reversed(base_polynomial(R))),7)
        values=structured_differential_hankel([a,b],[u,v],last)
        if (a,b,u,v)==(1,1,1,2):
            D=list(reversed(coeff))
            N=[sum(D[j]*values[k-j] for j in range(k+1)) for k in range(113)]
            assert D==list(map(F,sample['reduced_denominator']))
            assert N==list(map(F,sample['reduced_numerator']))
            assert N[-1] and D[-1] and N[-1]==D[-1]/2
            witness=sample['coprimality'];prime=witness['prime']
            assert prime==1000003 and all(prime%j for j in range(2,isqrt(prime)+1))
            assert all(value.denominator==1 for value in N+D)
            assert int(N[-1])%prime and int(D[-1])%prime
            left=product(list(map(F,witness['u'])),N);right=product(list(map(F,witness['v'])),D)
            left+=[F(0)]*max(0,len(right)-len(left))
            for j,value in enumerate(right):left[j]+=value
            assert all(value.denominator==1 for value in left)
            assert [int(value)%prime for value in left]==[1]+[0]*(len(left)-1)
        for N in range(17):
            assert values[N]==direct_determinant([[F(moment(i+j)) for j in range(N)] for i in range(N)])
            direct+=1
        for N in range(1,last-112+1):
            assert sum(x*values[N+j] for j,x in enumerate(coeff))==0,(a,b,u,v,N)
            residues+=1
        assert 2*sum(x*values[j] for j,x in enumerate(coeff))==coeff[0]
    report={'outcome':'Universal quartic boundary identities and mixed-family regressions passed',
        'review':'project self-review, not independent review','boundary_ring':'Q[r0,r1,r2,r3] with leading quartic coefficient normalized to one',
        'complete_boundary_indices':[2,3,4],'boundary_limit_at_one':'a','exponential_value_at_zero':'1/2',
        'newton_resultant_sample_matches':True,'sample_base_descending':expected,
        'sample_numerator_reconstructed':True,'sample_coprimality_witness_verified':True,
        'sample_minimal_eventual_order':112,
        'parameter_order':['a','b','u','v'],'parameter_cases':[list(row) for row in cases],
        'functional_moment_checks':relations,'direct_monomial_determinants':direct,
        'schur_last_index':last,'recurrence_indices':[1,last-112],'recurrence_residues':residues,
        'scope':'Written formal determinant, sixteen-base degree argument, resultant trace identity and polynomial specialization prove uniform coverage. Numeric cases alone do not.',
        'elapsed_seconds':time.perf_counter()-started}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))

if __name__=='__main__':main()
