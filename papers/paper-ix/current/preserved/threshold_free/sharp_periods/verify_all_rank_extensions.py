from fractions import Fraction
from math import comb, factorial
from pathlib import Path
import json

def v2(x):
    x=Fraction(x)
    if not x: return None
    def vi(n):
        n=abs(n)
        return (n&-n).bit_length()-1
    return vi(x.numerator)-vi(x.denominator)

def sequence(N,j,K):
    C=[Fraction(1)]
    for n in range(1,K+1):
        C.append(-sum(Fraction(comb(N*n,N*q),comb(N*q+j,j))*C[n-q] for q in range(1,n+1)))
    return C

def needed_orders(b):
    R=2
    while R-(R.bit_length()-1)<b+1:
        R*=2
    return [k for k in range(2,R) if k<b+1+k.bit_length()-1]

lanes=[]
for N in (2,8):
    for j in range(N):
        b=v2(Fraction(-1,comb(N+j,j))-1)
        needed=needed_orders(b)
        K=max([1]+needed)
        C=sequence(N,j,K)
        row=C; checks=[]
        for k in range(K+1):
            a=row[0]
            if k==1:
                assert v2(a)==b
                checks.append({'k':k,'coefficient':str(a),'v2':v2(a),'required_exact':b})
            elif k in needed:
                required=b+1+k.bit_length()-1
                assert v2(a)>=required,(N,j,k,a,required)
                checks.append({'k':k,'coefficient':str(a),'v2':v2(a),'required_lower_bound':required})
            row=[row[i+1]-row[i] for i in range(len(row)-1)]
        lanes.append({'N':N,'j':j,'normalized_exact_shift':b,'unnormalized_exact_shift':b+v2(factorial(j)),'low_Mahler_checks':checks})

failures=[]
for N,j,H in ((16,9,2),(32,18,2),(32,19,2)):
    C=sequence(N,j,H)
    d1=C[1]-C[0];dH=C[H]-C[0]
    b=v2(d1);actual=v2(dH);predicted=b+v2(H)
    assert actual!=predicted
    failures.append({'N':N,'j':j,'n':0,'H':H,'first_difference':str(d1),'first_difference_v2':b,'H_difference':str(dH),'actual_H_difference_v2':actual,'naive_exact_law_prediction':predicted})

central=[]
for a in range(1,10):
    N=1<<a;value=comb(2*N,N)
    assert value%8==6
    central.append({'a':a,'N':N,'central_binomial_mod8':value%8})
report={'status':'PASS','scope':'Exact finite coefficient checks complete the separately proved threshold-free Mahler theorem for all N=2 and N=8 lanes. Upper-lane counterchecks are exact rational calculations, not Euler counterexamples. All-rank lower-half proof is symbolic in SHARP_PERIOD_LEMMA.md.','complete_exact_laws':lanes,'upper_lane_non_isometry_examples':failures,'central_binomial_checks':central}
Path(__file__).with_name('all_rank_extensions_verified.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','complete_exact_law_N2_shifts':[x['normalized_exact_shift'] for x in lanes if x['N']==2],'complete_exact_law_N8_shifts':[x['normalized_exact_shift'] for x in lanes if x['N']==8],'upper_lane_failures':[{k:v for k,v in x.items() if not k.endswith('difference')} for x in failures]},indent=2))
