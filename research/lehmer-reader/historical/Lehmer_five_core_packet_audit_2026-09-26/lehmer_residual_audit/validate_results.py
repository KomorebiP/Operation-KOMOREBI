"""Cross-validate independently generated outputs, with elementary primality checks."""
from pathlib import Path
from math import isqrt
import json
ROOT=Path(__file__).resolve().parent

def prime(n):
    return n>=2 and all(n%d for d in range(2,isqrt(n)+1))
def v2(n):
    assert n
    n=abs(n)
    return (n&-n).bit_length()-1

def main():
    small=json.loads((ROOT/'results_initial.json').read_text())
    dyadic=json.loads((ROOT/'dyadic_results.json').read_text())
    exact={r['p']:r['tau'] for r in small['selected']}
    exact.update({r['p']:r['tau'] for r in dyadic['rows']})
    lines=(ROOT/'eta_ntt_results.txt').read_text().splitlines()
    mod=int(lines[0].split()[1]); checks=0
    for line in lines[1:]:
        if line.startswith('seconds'): continue
        p,res=map(int,line.split())
        assert prime(p)
        assert exact[p]%mod==res,(p,exact[p]%mod,res)
        checks+=1
    for row in dyadic['rows']:
        assert prime(row['p'])
        assert row['p']==2**14*row['u']-1
        assert v2(row['tau'])==row['v2']
    p1,p2=245759,770047
    u1,u2=(p1+1)//2**14,(p2+1)//2**14
    F1,F2=exact[p1]//2**14,exact[p2]//2**14
    assert exact[p1]%2**14==exact[p2]%2**14==0
    assert v2(u2-u1)==5 and v2(F2-F1)==0
    out={'status':'PASS','independent_modular_comparisons':checks,
         'dyadic_prime_rows':len(dyadic['rows']),
         'counterexample':{'p1':p1,'p2':p2,'u1':u1,'u2':u2,
             'F1_mod_32':F1%32,'F2_mod_32':F2%32,
             'v2_input_difference':5,'v2_output_difference':0},
         'claim_refuted':'A single Z_2-integral restricted power series matching tau(2^14*u-1)/2^14 on all prime arguments',
         'not_refuted':['Lehmer nonvanishing','Finer local models','Analytic models allowing denominators or additional arithmetic variables']}
    (ROOT/'cross_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
