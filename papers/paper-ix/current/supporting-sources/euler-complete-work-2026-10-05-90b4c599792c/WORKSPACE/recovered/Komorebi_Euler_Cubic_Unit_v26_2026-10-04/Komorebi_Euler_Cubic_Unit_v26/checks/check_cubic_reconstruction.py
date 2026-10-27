#!/usr/bin/env python3
"""Fresh 256-bit reconstruction against v25's frozen 224-bit cubic records.
Different source, factorial, local translation, and inflection algorithms.
Bernoulli modular evaluator and polynomial multiplication remain shared.
"""
from pathlib import Path
import argparse,json,time,math
import check_critical_value as base
import check_critical_replay as alt
from check_cubic_critical import jet, lift_inflection, vv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--records',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    t=time.monotonic();n=0;out=[]
    def check(c,msg):
        nonlocal n
        if not c:raise AssertionError(msg)
        n+=1
    for B in [3,7,11,15]:
        old=json.loads((a.records/f'v25_actual_{B}.json').read_text())['records'][0]
        r=B*(1<<640)-161;P=256;mod=1<<P
        G=alt.reconstruct_alt(r,-154,P)
        H=base.shift(G,90,mod)
        L=[c*pow(2,7*k,mod)%mod for k,c in enumerate(H)]
        c=min(vv(z,P) for z in L);check(c==old['content'],'local content')
        F=[z>>c for z in L];p=P-c;shared=old['precision'];sm=1<<shared
        prev=list(map(int,old['coefficients']))
        for i in range(max(len(F),len(prev))):
            check((F[i] if i<len(F) else 0)%sm==(prev[i] if i<len(prev) else 0)%sm,'complete local coefficient')
        rho=lift_inflection(F,p)
        check(rho%sm==int(old['inflection_residue']),'independent critical point')
        A=base.ev(jet(F,1),rho,1<<p);C=base.ev(F,rho,1<<p)
        check(A%sm==int(old['A_residue']),'slope residue')
        check(C%sm==int(old['C_residue']),'value residue')
        check(vv(A,p)==old['v_A'] and vv(C,p)==old['v_C'],'stable exact nonzero valuations')
        # Independently evaluate terminating original packet values at small integer offsets.
        gam=base.gamma(r,-154,P,7)
        for x in range(8):
            prod=1;total=0
            for q in range(x+1):
                if q:prod=prod*(x-q+1)*(2*x-2*q+1)%mod
                src=base.fmod(__import__('fractions').Fraction(9**(x-q+1)-1,8*(x-q+1)*(2*(x-q)+1)),P)
                total=(total+gam[q]*prod*src)%mod
            check(base.ev(G,x,mod)==total,'original finite packet evaluation')
        out.append({'B':B,'P':P,'normalized_precision':p,'content':c,'v_C':vv(C,p),'v_A':vv(A,p),
                    'inflection_residue':str(rho),'C_residue':str(C),'A_residue':str(A)})
    obj={'status':'PASS','checks':n,'seconds':time.monotonic()-t,
         'shared_components':['modular Bernoulli evaluator','polynomial multiplication'],
         'nonclaim':'No infinite multiplier progression or new family classified','records':out}
    a.output.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
if __name__=='__main__':main()
