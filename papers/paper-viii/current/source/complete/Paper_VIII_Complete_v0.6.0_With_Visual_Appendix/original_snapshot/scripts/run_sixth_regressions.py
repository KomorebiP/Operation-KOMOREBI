#!/usr/bin/env python3
"""Independent numerical mirrors of small-core recompression. Author: Komorebi P.

This is not compiled/extracted Lean code. Rank decisions use a numerical tolerance.
The formal construction uses exact column spaces and an algebraic SVD certificate.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import numpy as np

TOL = 2e-9

def matrix(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.complex128)
    if a.ndim != 2 or not np.all(np.isfinite(a)):
        raise ValueError('Expected a finite two-dimensional complex matrix')
    return a

def opnorm(a: np.ndarray) -> float:
    a=matrix(a)
    return float(np.linalg.norm(a,2)) if min(a.shape)>0 else 0.0

def fnorm(a: np.ndarray) -> float:
    return float(np.linalg.norm(matrix(a),'fro'))

def column_factors(a: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    a=matrix(a)
    u,s,_=np.linalg.svd(a,full_matrices=False)
    cut=1e-11*max(1.0,float(s[0]) if s.size else 0.0)
    q=u[:,s>cut]
    return q,q.conj().T@a

def validate_svd(g: np.ndarray,w: np.ndarray,z: np.ndarray,sigma: np.ndarray) -> None:
    g,w,z=matrix(g),matrix(w),matrix(z)
    sig=np.asarray(sigma)
    if sig.ndim!=1 or np.iscomplexobj(sig) or not np.all(np.isfinite(sig)):
        raise ValueError('Expected finite real singular data')
    d=len(sig)
    if w.shape!=(g.shape[0],d) or z.shape!=(g.shape[1],d):
        raise ValueError('Incompatible thin-SVD shapes')
    if np.any(sig<0) or np.any(sig[:-1]<sig[1:]):
        raise ValueError('Singular data must be nonnegative and nonincreasing')
    if fnorm(w.conj().T@w-np.eye(d))>TOL or fnorm(z.conj().T@z-np.eye(d))>TOL:
        raise ValueError('Columns are not orthonormal')
    if fnorm((w*sig)@z.conj().T-g)>TOL*max(1.0,fnorm(g)):
        raise ValueError('The factorization does not reconstruct the core')

def recompress(l: np.ndarray,r: np.ndarray,k: int) -> dict:
    l,r=matrix(l),matrix(r)
    if not isinstance(k,int) or isinstance(k,bool) or k<0:
        raise ValueError('Truncation rank must be a nonnegative integer')
    if l.shape[1]!=r.shape[1]:
        raise ValueError('Input factor widths differ')
    ql,rl=column_factors(l);qr,rr=column_factors(r)
    g=rl@rr.conj().T
    w,s,vh=np.linalg.svd(g,full_matrices=False);z=vh.conj().T
    validate_svd(g,w,z,s)
    h=min(k,len(s))
    lk=(ql@w[:,:h])*np.sqrt(s[:h])
    rk=(qr@z[:,:h])*np.sqrt(s[:h])
    return dict(ql=ql,qr=qr,g=g,s=s,lk=lk,rk=rk,b=lk@rk.conj().T)

def random_isometry(rng: np.random.Generator,n: int,r: int) -> np.ndarray:
    if r==0:return np.zeros((n,0),dtype=np.complex128)
    q,_=np.linalg.qr(rng.normal(size=(n,r))+1j*rng.normal(size=(n,r)))
    return q[:,:r]

def prescribed_factor(rng: np.random.Generator,n: int,t: int,r: int) -> np.ndarray:
    u=random_isometry(rng,n,r);v=random_isometry(rng,t,r)
    return (u*np.linspace(0.5,2.0,r))@v.conj().T

def run(seed: int=60606) -> dict:
    rng=np.random.default_rng(seed)
    cases=[]
    for trial in range(144):
        m,n,t=map(int,rng.integers(0,11,size=3))
        rl=int(rng.integers(0,min(m,t)+1));rr=int(rng.integers(0,min(n,t)+1))
        cases.append(('random_rank_deficient',prescribed_factor(rng,m,t,rl),
                      prescribed_factor(rng,n,t,rr)))
    for d in range(1,9):
        for repeat in range(4):
            u=random_isometry(rng,d+2,d);v=random_isometry(rng,d+3,d)
            sig=np.array([3.0 if i<d//2 else 1.0 for i in range(d)])
            cases.append(('repeated_singular_values',u*sig,v))
    for m,n,t in [(0,0,0),(0,4,3),(4,0,3),(4,5,0),(4,5,3),(1,1,1)]:
        cases.append(('zero_or_empty',np.zeros((m,t),complex),np.zeros((n,t),complex)))
    maxdef={key:0.0 for key in ['compact_reconstruction','spectral_tail',
        'frobenius_tail','ambient_reference','lift_norm','compress_contraction']}
    ledger=[]; competitor_checks=0
    for idx,(kind,l,r) in enumerate(cases):
        a=l@r.conj().T
        us,sa,vha=np.linalg.svd(a,full_matrices=False)
        ql,_=column_factors(l);qr,_=column_factors(r)
        d=min(ql.shape[1],qr.shape[1])
        for k in sorted({0,1,max(0,d-1),d,d+2}):
            c=recompress(l,r,k);b=c['b'];s=c['s'];scale=max(1.0,fnorm(a))
            eqerr=fnorm(ql@c['g']@qr.conj().T-a)/scale
            e2=opnorm(a-b);ef=fnorm(a-b)
            t2=float(s[k]) if k<len(s) else 0.0
            tf=float(np.linalg.norm(s[k:]))
            ambient=(us[:,:k]*sa[:k])@vha[:k,:]
            ref2=abs(e2-opnorm(a-ambient))/scale
            reff=abs(ef-fnorm(a-ambient))/scale
            errs={'compact_reconstruction':eqerr,'spectral_tail':abs(e2-t2)/scale,
                  'frobenius_tail':abs(ef-tf)/scale,'ambient_reference':max(ref2,reff)}
            assert c['lk'].shape[1]==min(k,d)==c['rk'].shape[1]
            if b.size:
                rank=int(np.sum(np.linalg.svd(b,compute_uv=False)>1e-9*scale))
                assert rank<=k,(idx,k,rank)
            for key,value in errs.items():
                maxdef[key]=max(maxdef[key],value)
                assert value<TOL,(idx,k,key,value)
            for _ in range(5):
                rank=min(k,min(a.shape))
                x=rng.normal(size=(a.shape[0],rank))+1j*rng.normal(size=(a.shape[0],rank))
                y=rng.normal(size=(a.shape[1],rank))+1j*rng.normal(size=(a.shape[1],rank))
                cand=x@y.conj().T
                assert e2<=opnorm(a-cand)+TOL*scale
                assert ef<=fnorm(a-cand)+TOL*scale
                competitor_checks+=1
            # Compression of a completely unrestricted ambient matrix and norm invariance.
            ambient=rng.normal(size=a.shape)+1j*rng.normal(size=a.shape)
            comp=ql.conj().T@ambient@qr
            delta=max(opnorm(comp)-opnorm(ambient),fnorm(comp)-fnorm(ambient),0.0)
            delta/=max(1.0,fnorm(ambient))
            assert delta<TOL
            maxdef['compress_contraction']=max(maxdef['compress_contraction'],delta)
            g=rng.normal(size=c['g'].shape)+1j*rng.normal(size=c['g'].shape)
            lift=ql@g@qr.conj().T
            delta=max(abs(opnorm(g)-opnorm(lift)),abs(fnorm(g)-fnorm(lift)))/max(1.,fnorm(g))
            maxdef['lift_norm']=max(maxdef['lift_norm'],delta)
            assert delta<TOL
            ledger.append(dict(case=idx,kind=kind,shape=list(a.shape),input_width=l.shape[1],
                core_shape=list(c['g'].shape),k=k,output_columns=min(k,d),pass_check=True))
    rejected=[]
    def rejects(name,call):
        try:call()
        except ValueError:rejected.append(name)
        else:raise AssertionError('Expected rejection: '+name)
    g=np.diag([3.,1.]);I=np.eye(2);swap=I[:,::-1]
    rejects('unsorted_valid_factorization',lambda:validate_svd(g,swap,swap,np.array([1.,3.])))
    rejects('nonisometric_left',lambda:validate_svd(g,2*I,I,np.array([3.,1.])))
    rejects('wrong_reconstruction',lambda:validate_svd(g,I,I,np.array([4.,1.])))
    rejects('negative_value',lambda:validate_svd(g,I,I,np.array([3.,-1.])))
    rejects('nonfinite_value',lambda:validate_svd(g,I,I,np.array([3.,np.nan])))
    rejects('mismatched_shape',lambda:validate_svd(g,I[:,:1],I,np.array([3.,1.])))
    rejects('negative_k',lambda:recompress(I,I,-1))
    rejects('noninteger_k',lambda:recompress(I,I,1.5))
    rejects('mismatched_factors',lambda:recompress(I,np.ones((2,3)),1))
    # Removing assumptions really can invalidate the mathematical conclusion.
    wrong=np.diag([0.,1.])
    assert opnorm(g-wrong)>1.0 and fnorm(g-wrong)>1.0
    assert opnorm(2*I@g)>opnorm(g)
    return {'author':'Komorebi P.','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'seed':seed,'python':platform.python_version(),'numpy':np.__version__,
        'pass':True,'factor_pairs':len(cases),'recompression_cases':len(ledger),
        'arbitrary_rank_bounded_competitors':competitor_checks,
        'invalid_input_controls_rejected':rejected,'mathematical_negative_controls':2,
        'relative_tolerance':TOL,'maximum_residuals':maxdef,'cases':ledger,
        'boundary':'Independent NumPy complex128 mirror; numerical rank tolerance. Not compiled Lean, not universal proof, no GPU or timing claim.'}

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(); report=run(); report['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
if __name__=='__main__':main()
