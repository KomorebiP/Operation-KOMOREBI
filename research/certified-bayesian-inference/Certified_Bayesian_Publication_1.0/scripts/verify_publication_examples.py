#!/usr/bin/env python3
"""Fresh, bounded exact-rational checks for the publication; no Lean compilation."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source/FD_Certified_Inference_Core_v1.0.0_Checked'
sys.path.insert(0,str(SOURCE/'checks'))
import cached_posterior as cp
import rounded_certificate as rb
import precision_certificate as pb
import posterior_output as po
from exact_certificate import Model, matrix, rational, encode

def mm(A,B):
    return [[sum((a*b for a,b in zip(row,col)),Q(0)) for col in zip(*B)] for row in A]
def tr(A):return list(map(list,zip(*A)))
def add(A,B):return [[a+b for a,b in zip(ar,br)] for ar,br in zip(A,B)]
def neg(A):return [[-a for a in row] for row in A]
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def en(A):return sum((a*a for row in A for a in row),Q(0))
def eq(A,B):return [list(r) for r in A]==[list(r) for r in B]
def inv(A):
    n=len(A);W=[list(a)+e for a,e in zip(A,eye(n))]
    for j in range(n):
        k=next(i for i in range(j,n) if W[i][j]);W[j],W[k]=W[k],W[j]
        s=W[j][j];W[j]=[a/s for a in W[j]]
        for i in range(n):
            if i!=j:
                s=W[i][j];W[i]=[a-s*b for a,b in zip(W[i],W[j])]
    return [r[n:] for r in W]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def source_inventory():return {str(p.relative_to(SOURCE)):digest(p) for p in SOURCE.rglob('*') if p.is_file()}
count=0

def check(v,label):
    global count
    count+=1
    if not v:raise AssertionError(label)

def joseph_factor(m,B):
    n,k=len(B),len(B[0]);u,w=len(m.L[0]),len(m.N[0])
    v=[m.observation[j]-sum((m.H[j][i]*m.mean[i] for i in range(n)),Q(0)) for j in range(k)]
    mean=[m.mean[i]+sum((B[i][j]*v[j] for j in range(k)),Q(0)) for i in range(n)]
    A=[[m.L[i][a]-sum((B[i][j]*m.H[j][l]*m.L[l][a] for j in range(k) for l in range(n)),Q(0)) for a in range(u)] for i in range(n)]
    D=[[sum((B[i][j]*m.N[j][a] for j in range(k)),Q(0)) for a in range(w)] for i in range(n)]
    cov=[[sum((A[i][a]*A[j][a] for a in range(u)),Q(0))+sum((D[i][a]*D[j][a] for a in range(w)),Q(0))+m.sigma*sum((B[i][a]*B[j][a] for a in range(k)),Q(0)) for j in range(n)] for i in range(n)]
    return mean,cov

def case(name):
    raw=json.loads((SOURCE/f'examples/adaptive_{name}.json').read_text());m=Model.parse(raw['model']);B=matrix(raw['initial_gain'],'gain');eps=rational(raw['epsilon']);delta=rational(raw['output_radius'])
    P=mm(m.L,tr(m.L));R=add(mm(m.N,tr(m.N)),[[m.sigma*a for a in r] for r in eye(len(m.H))]);S=add(mm(mm(m.H,P),tr(m.H)),R);C=mm(P,tr(m.H));K=mm(C,inv(S));v=[[a] for a in m.innovation]
    posterior_mean=[m.mean[i]+r[0] for i,r in enumerate(mm(K,v))]
    posterior_cov=add(P,neg(mm(mm(C,inv(S)),tr(C))))
    work=cp.Work();ctx=cp.prepare(m,work);cache=cp.initialize(m,ctx,B,work);states=[]
    for it in range(100):
        F=add(C,neg(mm(cache.gain,S)));G=[mm(p,F) for p in m.outputs];energies=[en(g) for g in G]
        check(eq(ctx.S,S),'independent S');check(en(F)==sum(energies)==cache.total,'energy decomposition')
        for a in range(len(G)):
            check(eq(G[a],cache.residuals[a]),'cached packet residual');check(energies[a]==cache.energies[a],'cached packet energy')
        mean,cov=joseph_factor(m,cache.gain);D=add([list(r) for r in cache.gain],neg(K));extra=mm(mm(D,S),tr(D))
        check(eq(cov,add(posterior_cov,extra)),'Joseph excess covariance identity')
        check(mean==[m.mean[i]+r[0] for i,r in enumerate(mm(cache.gain,v))],'direct mean formula')
        coupled=en(mm(D,v))+sum((extra[i][i] for i in range(len(extra))),Q(0))
        score=cache.total*ctx.weight
        check(coupled<=score,'independent coupling squared bound')
        selected=work.choose(cache.energies,raw['seed'],raw['scan'])
        check(cache.energies[selected]==max(energies),'greedy maximum')
        states.append(dict(iteration=it,gain=cache.gain,residual=F,energies=energies,total=cache.total,score=score,selected=selected,mean=mean,covariance=cov,coupling_squared=coupled,geometric_bound=(ctx.rate**it)*states[0]['score'] if states else score))
        if score<=eps*eps/4:break
        nxt=cp.advance(ctx,cache,selected,work)
        check(nxt.total<=ctx.rate*cache.total,'rate inequality')
        for b in range(len(G)):
            if b!=selected:check(nxt.residuals[b] is cache.residuals[b] and nxt.energies[b]==cache.energies[b],'unselected reuse')
        cache=nxt
    result=cp.solve(m,B,eps,delta,raw['seed'],raw['scan'],[4,12]);archived=json.loads((SOURCE/f'results/cached_{name}.json').read_text());fresh_deterministic=dict(result);fresh_deterministic.pop('timing_seconds')
    archived.pop('timing_seconds');archived.pop('input_sha256');check(fresh_deterministic==archived,'archived deterministic result reproduced')
    check(eq(cache.gain,matrix(result['final_candidate']['gain'],'gain')),'manual cached trajectory equals producer')
    replay=cp.solve(m,B,eps,delta,raw['seed'],raw['scan'],[4,12],mode='recompute')
    check(result['final_candidate']==replay['final_candidate'],'cached/recomputed final certificate');check(result['selected_packets']==replay['selected_packets'],'cached/recomputed sequence')
    intervals=result['parameter_output'];final_mean,final_cov=joseph_factor(m,cache.gain)
    for i,x in enumerate(final_mean):check(abs(x-Q(intervals['mean']['center'][i]))<=Q(intervals['mean']['radius'][i])<=delta,'reported mean interval')
    for i,row in enumerate(final_cov):
        for j,x in enumerate(row):check(abs(x-Q(intervals['covariance']['center'][i][j]))<=Q(intervals['covariance']['radius'][i][j])<=delta,'reported covariance interval')
    precision_scores=[]
    for p in range(1,17):
        candidate,_=rb.produce(m,cache.gain,p);check(candidate.valid(m),'rounded candidate validity');check(candidate.score(m)>=states[-1]['score'],'rounded score dominates exact')
        precision_scores.append(dict(precision=p,score=candidate.score(m),passed=candidate.tolerance(m,eps)))
    pstar,coefficient,parts=pb.sufficient_precision(m,cache.gain,eps*eps/4)
    check(coefficient/Q(1<<pstar)<=eps*eps/4,'fallback inflation budget')
    return dict(model=m.input_dict(),P=P,R=R,S=S,C=C,K=K,posterior_mean=posterior_mean,posterior_covariance=posterior_cov,tau=ctx.step,T=ctx.T,weight=ctx.weight,rate=ctx.rate,epsilon=eps,delta=delta,states=states,result=result,precision_scores=precision_scores,sufficient_precision=pstar,score_coefficient=coefficient)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();before=source_inventory()
    cases={name:case(name) for name in ['coordinate','rotated']}
    scalar=Model.parse({'H':[[1]],'L':[[1]],'N':[[0]],'sigma':1,'mean':[0],'observation':[1],'output_packets':[[[1]]],'input_packets':[[[1]]]})
    ctx=cp.prepare(scalar,cp.Work());initial=cp.initialize(scalar,ctx,matrix([[0]],'gain'),cp.Work());ideal=cp.advance(ctx,initial,0,cp.Work());bg=rb.down(0,ideal.gain[0][0]);gr=rb.down(0,ideal.residuals[0][0][0]);true_res=1-2*bg
    rounded_counterexample=dict(tau=ctx.step,ideal_gain=ideal.gain[0][0],ideal_residual=ideal.residuals[0][0][0],rounded_gain=bg,rounded_residual=gr,true_residual=true_res,cached_score=gr*gr*ctx.weight,true_score=true_res*true_res*ctx.weight)
    check(rounded_counterexample['cached_score']==0 and rounded_counterexample['true_score']==2,'naive rounded cache discrepancy')
    cert,_=rb.produce(scalar,((bg,),),12);check(not cert.tolerance(scalar,Q(1,10)),'independent verifier rejects false cached score')
    vector=[Q(1,2),Q(3,2)];true_cov=[[x*y for y in vector] for x in vector];center=[[rb.down(1,x) for x in row] for row in true_cov];w=[-3,1];negative=sum(w[i]*center[i][j]*w[j] for i in range(2) for j in range(2));check(negative==-1,'covariance-center counterexample')
    dyadic=rb.rexact(4,Q(1,3));check(dyadic.center==Q(5,16) and dyadic.radius==Q(1,16),'hand dyadic ball')
    scans=[]
    for es,seed,scan in [([Q(1),Q(1)],0,[1,0]),([Q(1),Q(1)],1,[0,1]),([Q(16),Q(1)],1,[1,0,0])]:
        chosen=cp.Work().choose(es,seed,scan);check(es[chosen]==max(es),'scan test maximum');scans.append(dict(energies=es,seed=seed,scan=scan,chosen=chosen))
    fresh_tests={}
    for script,key in [('test_cached.py','cache_diagnostics'),('test_posterior_output.py','output_diagnostics')]:
        target=args.output.parent/f'{key}.json';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');p=subprocess.run([sys.executable,str(SOURCE/'checks'/script),str(target.resolve())],cwd=SOURCE,env=env,capture_output=True,text=True,check=True)
        fresh_tests[key]=json.loads(target.read_text());check(fresh_tests[key]['status']=='PASS','existing diagnostic pass')
    after=source_inventory();check(before==after,'all baseline files unchanged')
    report=dict(status='PASS',arithmetic='Exact fractions.Fraction; plots numerically render exact rational inputs',assertions=count,source_files_unchanged=len(before),source_snapshot_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),cases=cases,rounded_counterexample=rounded_counterexample,covariance_center_counterexample=dict(exact_covariance=true_cov,rounded_centers=center,witness=w,quadratic_form=negative),dyadic=dict(value=Q(1,3),precision=4,center=dyadic.center,radius=dyadic.radius),scan_cases=scans,existing_diagnostics=fresh_tests,non_claims=['No fresh Lean execution.','Finite diagnostics do not establish universal theorems.','Gaussian contour rendering is numerical illustration, not interval-certified geometry.','No new performance measurements or practical scalability claim.'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(encode(report),indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','assertions','source_files_unchanged']}))
if __name__=='__main__':main()
