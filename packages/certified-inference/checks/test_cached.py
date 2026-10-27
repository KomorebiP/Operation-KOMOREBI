#!/usr/bin/env python3
"""Independent exact cache-invariant and output diagnostics, with explicit rejection controls."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
from dataclasses import replace
from exact_certificate import Model,matrix,rational,encode,energy
from test_adaptive import reference,mm,en,eq
from test_posterior_output import reference as output_reference
from benchmark_cached import cases
import cached_posterior as cp
import rounded_certificate as rb
import posterior_output as po
checks=0

def check(x,label):
    global checks
    checks+=1
    if not x:raise AssertionError(label)

def main():
    records=[]
    for name,d in cases():
        m=Model.parse(d['model']);B=matrix(d['initial_gain'],'gain');n,k=len(B),len(B[0]);seed=len(m.outputs)-1;scan=list(reversed(range(len(m.outputs))))+[0]
        # Include arbitrary signed nonzero initial gains, independently of published examples.
        B=tuple(tuple(Q(i-j-1,7) for j in range(k)) for i in range(n))
        work=cp.Work();ctx=cp.prepare(m,work);c=cp.initialize(m,ctx,B,work)
        for it in range(7):
            S,F=reference(m,c.gain);check(eq(ctx.S,S),'precomputed innovation')
            expected=[mm(p,F) for p in m.outputs];es=[en(g) for g in expected]
            for a in range(len(m.outputs)):
                check(eq(c.residuals[a],expected[a]),'cache residual exact');check(c.energies[a]==es[a],'cache energy exact')
            check(c.total==en(F)==sum(c.energies),'cache total exact')
            a=work.choose(c.energies,seed,scan);check(es[a]==max(es),'maximum correct')
            nxt=cp.advance(ctx,c,a,work)
            for b in range(len(m.outputs)):
                if b!=a:check(nxt.residuals[b] is c.residuals[b] and nxt.energies[b]==c.energies[b],'unchanged entries actually reused')
            check(nxt.total<=ctx.rate*c.total,'cached contraction')
            c=nxt
        check(work.full_residuals==1,'only initial full residual')
        check(work.packet_refreshes==len(m.outputs)+7,'one refreshed energy per step')
        eps=rational(d['epsilon']);delta=rational(d['output_radius']);B=matrix(d['initial_gain'],'initial')
        cached=cp.solve(m,B,eps,delta,d['seed'],d['scan'],[12]);plain=cp.solve(m,B,eps,delta,d['seed'],d['scan'],[12],mode='recompute')
        check(cached['final_candidate']==plain['final_candidate'],'same final candidate');check(cached['selected_packets']==plain['selected_packets'],'same trajectory')
        G=matrix(cached['final_candidate']['gain'],'gain');mean,cov=output_reference(m,G);am,ac=po.graph(m,G,precision=cached['parameter_output']['precision'])
        for i in range(n):
            check(am[i].encloses(mean[i]) and am[i].radius<=delta,'mean output')
            for j in range(n):check(ac[i][j].encloses(cov[i][j]) and ac[i][j].radius<=delta,'covariance output')
        records.append(dict(case=name,n=n,k=k,invariant_steps=7,iterations=cached['iterations'],full_residuals=cached['work']['full_residuals']))
    d=cases()[0][1];m=Model.parse(d['model']);B=matrix(d['initial_gain'],'gain');eps=Q(1,20);delta=Q(1,1000);rejected=0
    bad=[lambda:cp.solve(m,B,eps,delta,0,[],[12]),lambda:cp.solve(m,B,Q(0),delta,0,[0,1],[12]),lambda:cp.solve(m,B,eps,Q(0),0,[0,1],[12]),lambda:cp.solve(m,B,eps,delta,True,[0,1],[12]),lambda:cp.solve(m,B,eps,delta,0,[0,1],[12.0]),lambda:cp.solve(m,B,eps,delta,0,[0,1],[12],max_steps=-1),lambda:rational(0.1)]
    for op in bad:
        try:op()
        except ValueError:rejected+=1
        else:raise AssertionError('invalid input accepted')
    for r in [cp.solve(m,B,eps,delta,0,[0,1],[12],max_steps=0),cp.solve(m,B,eps,Q(1,2**1000),0,[0,1],[12])]:
        check(r['status']=='RESOURCE_LIMIT','cap respected')
        try:cp.export_lean(m,B,eps,delta,r,'MustFail')
        except ValueError:rejected+=1
        else:raise AssertionError('capped proof exported')
    # Counterexample to naive independent rounding of cache and gain.
    scalar=Model.parse({'H':[[1]],'L':[[1]],'N':[[0]],'sigma':1,'mean':[0],'observation':[1],'output_packets':[[[1]]],'input_packets':[[[1]]]})
    ctx=cp.prepare(scalar,cp.Work());c=cp.initialize(scalar,ctx,matrix([[0]],'gain'),cp.Work());ideal=cp.advance(ctx,c,0,cp.Work())
    rounded_gain=tuple(tuple(rb.down(0,x) for x in row) for row in ideal.gain);rounded_res=tuple(tuple(rb.down(0,x) for x in row) for row in ideal.residuals[0])
    check(en(rounded_res)*ctx.weight==0,'naive cache claims zero');check(energy(scalar.residual(rounded_gain))*ctx.weight==2,'true score remains two')
    cand,_=rb.produce(scalar,rounded_gain,12);check(not cand.tolerance(scalar,Q(1,10)),'independent verifier protects soundness')
    report=dict(status='PASS',assertions=checks,expected_rejections=rejected,cases=records,rounded_cache_boundary={'cached_score':'0','true_score':'2','final_verifier':'rejects'},non_claims=['Finite diagnostics are not universal proofs.','No rounded selective solver is claimed.'])
    p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','assertions','expected_rejections']}))
if __name__=='__main__':main()
