from __future__ import annotations
import sys,json,time,hashlib,platform,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'Komorebi_Euler_Cubic_Unit_v26'
sys.path.insert(0,str(SRC/'checks'))
import check_critical_value as b
from prepare_probe import prepare,disc,v2res

def eval_critical(f,P):
    # f is supplied modulo 2^P. Dividing its derivative by 2 costs one bit.
    Qbits=P-1;M=1<<Qbits
    assert f[2]%2==1 and all(x%4==0 for x in f[3:])
    assert all((i*f[i])%2==0 for i in range(1,len(f)))
    Q=[(i*f[i]//2)%M for i in range(1,len(f))]
    assert Q[1]%2 and all(x%2==0 for x in Q[2:])
    c=0
    for k in range(Qbits):
        m=1<<(k+1)
        if b.ev(Q,c,m): c+=1<<k
        assert b.ev(Q,c,m)==0
    return c,b.ev(f,c,1<<P),Q

def run_case(T,P):
    start=time.monotonic();B=17659+(1<<18)*T;r=B*(1<<640)-161
    assert r>0
    G,mu,j=b.residual(r,P)
    assert (mu,j)==(-154,161)
    floc=b.local(G,10202,15,P)
    content=min(b.v2(x,P) for x in floc);assert content==178
    f=[x>>content for x in floc]; pp=P-content
    c,cv,Q=eval_critical(f,pp)
    W,U=prepare(f,pp);D=disc(W)%(1<<pp)
    rec={'T':T,'B':B,'global_precision':P,'local_precision':pp,'content':content,'terminal':j,'mu':mu,
         'local_coefficients':[str(x) for x in f], 'critical_center_residue':str(c),
         'critical_value_residue':str(cv),'critical_value_valuation_or_bound':v2res(cv,pp),
         'prepared_polynomial':[str(x) for x in W],'prepared_discriminant_residue':str(D),
         'prepared_discriminant_valuation_or_bound':v2res(D,pp),
         'nonzero_discriminant':D!=0,'seconds':time.monotonic()-start}
    return rec

if __name__=='__main__':
    Ts=list(map(int,sys.argv[1].split(','))); P=int(sys.argv[2]);output=Path(sys.argv[3])
    b.B=b.bernoullis(max(256,P))
    records=[]
    for T in Ts:
        rec=run_case(T,P);records.append(rec)
        output.write_text(json.dumps({'arithmetic':'integer/rational modular; inherited v26 Bernoulli evaluator','precision':P,
            'source_sha256':hashlib.sha256((SRC/'checks/check_critical_value.py').read_bytes()).hexdigest(),
            'python':platform.python_version(),'records':records},indent=2)+'\n')
        print({k:rec[k] for k in ['T','local_precision','critical_value_valuation_or_bound','prepared_discriminant_valuation_or_bound','seconds']},flush=True)
