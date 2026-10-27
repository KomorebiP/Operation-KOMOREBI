from fractions import Fraction
from math import comb, factorial
import json
from pathlib import Path

def v2(x):
    x=Fraction(x)
    if not x: return None
    def vi(n):
        n=abs(n)
        return (n&-n).bit_length()-1
    return vi(x.numerator)-vi(x.denominator)

expected={
 0:['1','-2','72'],
 1:['1','-6/5','184/45'],
 2:['1','-16/15','64/45','-14848/1365','71426048/69615','-25509691392/85085','149113198870528/765765'],
 3:['1','-36/35','256/231','-65792/35035','161644544/4849845'],
}
B=[1,1,4,2]
results=[]
for j,es in expected.items():
    K=len(es)-1
    C=[Fraction(1)]
    for n in range(1,K+1):
        C.append(-sum(Fraction(comb(4*n,4*q))*Fraction(factorial(j)*factorial(4*q),factorial(4*q+j))*C[n-q] for q in range(1,n+1)))
    row=C; coeff=[]
    for k in range(K+1):
        a=row[0]
        assert a==Fraction(es[k]),(j,k,a,es[k])
        va=v2(a)
        if k==1: assert va==B[j]
        if k>=2: assert va>=B[j]+1+k.bit_length()-1
        coeff.append({'k':k,'coefficient':str(a),'v2':va})
        row=[row[i+1]-row[i] for i in range(len(row)-1)]
    results.append({'j':j,'normalized_difference_shift':B[j],'unnormalized_difference_shift':B[j]+v2(factorial(j)),'coefficients':coeff})
report={'status':'PASS','claim_scope':'Exact finite low-Mahler checks. Sharp global periods additionally use the separately proved threshold-free Mahler divisibility theorem.','lanes':results}
path=Path(__file__).with_name('low_mahler_verified.json')
path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
