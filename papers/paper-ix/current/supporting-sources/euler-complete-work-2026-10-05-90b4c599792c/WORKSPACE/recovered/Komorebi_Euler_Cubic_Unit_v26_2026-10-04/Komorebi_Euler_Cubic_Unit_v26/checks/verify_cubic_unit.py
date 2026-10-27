#!/usr/bin/env python3
"""Compare all fresh raw/alternative v26 coefficients and jet residues.
No new universal claim is inferred from these four actual indices.
"""
from pathlib import Path
import json,argparse,hashlib,math,time

def jetev(a,k,x,m):
    return sum(math.comb(n,k)*a[n]*pow(x,n-k,m) for n in range(k,len(a)))%m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ns=ap.parse_args()
    if ns.output.exists():raise FileExistsError(ns.output)
    start=time.monotonic();count=0;rows=[];inputs={}
    def check(c):
        nonlocal count
        if not c:raise AssertionError('comparison failed')
        count+=1
    for B in [3,7,11,15]:
        pair=[]
        for route in ['actual','alternate']:
            f=ns.evidence/f'v26_{route}_{B}.json';inputs[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
            r=json.loads(f.read_text());check(r['status']=='PASS');pair.append(r['records'][0])
        a,b=pair;p=min(a['precision'],b['precision']);mod=1<<p
        aa=list(map(int,a['coefficients']));bb=list(map(int,b['coefficients']))
        for n in range(max(len(aa),len(bb))):check((aa[n] if n<len(aa) else 0)%mod==(bb[n] if n<len(bb) else 0)%mod)
        for k in ['inflection_residue','A_residue','C_residue','v_residue','D_residue']:
            check(int(a[k])%mod==int(b[k])%mod)
        rho=int(a['inflection_residue'])
        check(jetev(aa,2,rho,mod)==0)
        for k,key in [(0,'C_residue'),(1,'A_residue'),(3,'v_residue')]:check(jetev(aa,k,rho,mod)==int(a[key]))
        check(2*a['v_D']<10+7*a['v_A'])
        # Direct finite arithmetic soundness for the two norm-equality inputs.
        if B in [3,11]:
            for y in range(32):
                if jetev(aa,2,y,32)==0:
                    D=(4*jetev(aa,1,y,32)**3+27*jetev(aa,3,y,32)*jetev(aa,0,y,32)**2)%32
                    check(D!=0)
            check(a['unit_data_mod8']['A_odd']!=(5*a['unit_data_mod8']['cubic_jet'])%8)
        rows.append({'B':B,'common_precision':p,'v_D':a['v_D'],'new_test':True})
    report={'status':'PASS','comparisons':count,'inputs_sha256':inputs,'records':rows,
            'seconds':time.monotonic()-start,
            'shared_components':['modular Bernoulli evaluator','polynomial multiplication'],
            'nonclaims':['No full multiplier-family result','No original-index coefficient Lean proof']}
    ns.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
