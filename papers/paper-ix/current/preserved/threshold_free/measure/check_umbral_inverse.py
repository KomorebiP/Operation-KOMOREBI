"""Bounded exact checks of the threshold-free inverse theorem.

These checks are not the universal proof. All arithmetic is in Z/(2^P).
"""
from math import comb
from pathlib import Path
import json

P=128
MOD=1<<P
ROOT=Path(__file__).resolve().parent

def v2(a):
    a%=MOD
    return P if a==0 else (a&-a).bit_length()-1

def reciprocal_packets(N, source, count):
    out=[1]
    for n in range(1,count+1):
        out.append(-sum(comb(N*n,N*i)*source[i]*out[n-i]
                        for i in range(1,n+1))%MOD)
    return out

def difference(c,n,k,H):
    return sum((-1)**(k-i)*comb(k,i)*c[n+i*H]
               for i in range(k+1))%MOD

def check_packets(N,source,label,count=192):
    c=reciprocal_packets(N,source,count)
    tests=0
    for H in (1,2,3,4,5,7,8,12,16):
        h=v2(H)
        for k in range(1,9):
            for n in range(25):
                if n+k*H<=count:
                    actual=v2(difference(c,n,k,H))
                    assert actual>=k*(h+1),(label,n,k,H,actual,k*(h+1))
                    tests+=1
    mahler=[v2(difference(c,0,k,1)) for k in range(1,33)]
    return {'label':label,'N':N,'tests':tests,'mahler_valuations_k_1_to_32':mahler}

def main():
    count=192
    records=[]
    for j in range(4):
        source=[pow(comb(4*n+j,j),-1,MOD) for n in range(count+1)]
        records.append(check_packets(4,source,f'actual_N4_j{j}',count))
    # Deliberately non-Euler P2 sources: finite Newton expansions.
    # This probes the generalized inverse statement rather than just the four cases.
    for N in (2,4,8):
        for seed in range(3):
            weights=[1]+[(2**r)*(2*seed+3)**r for r in range(1,10)]
            source=[sum(weights[r]*comb(n,r) for r in range(min(n,9)+1))%MOD
                    for n in range(count+1)]
            records.append(check_packets(N,source,f'generic_N{N}_seed{seed}',count))
    result={'status':'PASS','precision':P,'max_packet_index':count,
            'scope':'bounded exact arithmetic checks; universal proof in adjacent Markdown',
            'total_difference_checks':sum(r['tests'] for r in records),'records':records}
    (ROOT/'UMBRAL_INVERSE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

if __name__=='__main__':
    main()
