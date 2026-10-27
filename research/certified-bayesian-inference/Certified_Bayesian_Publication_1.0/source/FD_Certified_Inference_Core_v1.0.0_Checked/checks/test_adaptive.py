#!/usr/bin/env python3
"""Finite exact diagnostics using independent scalar sums for model and residual."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
from exact_certificate import Model,encode,matrix,rational
from test_posterior_output import reference as output_reference
import adaptive_packet_solver as solver
import posterior_output as output
checks=0

def check(v,msg):
    global checks
    checks+=1
    if not v:raise AssertionError(msg)

def mm(A,B):return [[sum((A[i][h]*B[h][j] for h in range(len(B))),Q(0)) for j in range(len(B[0]))] for i in range(len(A))]
def en(A):return sum((x*x for row in A for x in row),Q(0))
def eq(A,B):return all(A[i][j]==B[i][j] for i in range(len(A)) for j in range(len(A[0])))
def reference(m,B):
    n,k=len(B),len(B[0]);u,w=len(m.L[0]),len(m.N[0])
    P=[[sum((m.L[i][a]*m.L[j][a] for a in range(u)),Q(0)) for j in range(n)] for i in range(n)]
    S=[[sum((m.H[i][x]*P[x][y]*m.H[j][y] for x in range(n) for y in range(n)),Q(0))+sum((m.N[i][a]*m.N[j][a] for a in range(w)),Q(0))+m.sigma*(i==j) for j in range(k)] for i in range(k)]
    F=[[sum((P[i][l]*m.H[j][l] for l in range(n)),Q(0))-sum((B[i][l]*S[l][j] for l in range(k)),Q(0)) for j in range(k)] for i in range(n)]
    return S,F

def main():
    cases=[]
    for cid,(n,k,u,w) in enumerate([(1,1,1,1),(2,1,2,1),(1,2,1,2),(2,2,1,1),(3,2,2,1),(2,3,1,2)]):
        H=[[Q((-1)**(i+j)*(i+j+1),3) for j in range(n)] for i in range(k)]
        L=[[Q(i+j+1,4) for j in range(u)] for i in range(n)];N=[[Q(i-j,7) for j in range(w)] for i in range(k)]
        ps=[[[Q(int(i==j==a)) for j in range(n)] for i in range(n)] for a in range(n)]
        ds=[[[Q(int(i==j==a)) for j in range(k)] for i in range(k)] for a in range(k)]
        m=Model.parse(encode(dict(H=H,L=L,N=N,sigma=Q(1,1000) if cid==5 else Q(2,3),mean=[Q(i-1,5) for i in range(n)],observation=[Q(j+1,7) for j in range(k)],output_packets=ps,input_packets=ds)))
        gain=tuple(tuple(Q(i-j-1,9) for j in range(k)) for i in range(n));seed=n-1;scan=list(reversed(range(n)))+[0]
        pars=solver.parameters(m,gain,Q(1,10),seed,scan);choices=[]
        for it in range(8):
            S,F=reference(m,gain);check(eq(S,m.S),'innovation');check(eq(F,m.residual(gain)),'residual')
            packets=[mm(p,F) for p in m.outputs];es=list(map(en,packets))
            nxt,a,got=solver.packet_update(m,gain,seed,scan);choices.append(a)
            check(es==got,'energies');check(es[a]==max(es),'maximum');check(sum(es)==en(F),'complete accounting')
            inc=packets[a];_,F2=reference(m,nxt)
            for i in range(n):
                for j in range(k):
                    check(nxt[i][j]==gain[i][j]+pars['step']*inc[i][j],'selected update')
                    check(F2[i][j]==F[i][j]-pars['step']*sum((inc[i][h]*S[h][j] for h in range(k)),Q(0)),'residual recurrence')
            for b in range(n):
                before=packets[b];after=mm(m.outputs[b],F2)
                if b!=a:
                    check(eq(before,after),'unselected residual');check(eq(mm(m.outputs[b],gain),mm(m.outputs[b],nxt)),'unselected gain')
                else:check(en(after)<=pars['full_rate']*en(before),'selected contraction')
                if en(before)==0:check(en(after)==0,'zero packet preserved')
            check(en(F2)<=en(F)-(1-pars['full_rate'])*es[a],'local descent');check(en(F2)<=pars['adaptive_rate']*en(F),'global contraction')
            for D in m.inputs:
                left=mm(F2,D);right0=mm(F,D);right1=mm(mm(inc,S),D)
                check(all(left[i][j]==right0[i][j]-pars['step']*right1[i][j] for i in range(n) for j in range(k)),'input cross effects')
            gain=nxt
        cases.append(dict(n=n,k=k,prior_columns=u,noise_columns=w,noise_floor=str(m.sigma),updates=8,selections=choices))
    executions=[]
    for name in ['coordinate','rotated']:
        raw=json.loads(Path(f'examples/adaptive_{name}.json').read_text());m=Model.parse(raw['model']);B=matrix(raw['initial_gain'],'gain');eps=rational(raw['epsilon']);delta=rational(raw['output_radius'])
        r=solver.solve(m,B,eps,delta,raw['seed'],raw['scan'],[4,12]);check(r['status']=='PASS_ADAPTIVE_PROVISIONAL','complete execution')
        stored=json.loads(Path(f'results/adaptive_{name}.json').read_text());stored.pop('input_sha256');check(r==stored,'reproducible execution')
        G=matrix(r['final_candidate']['gain'],'final');mean,cov=output_reference(m,G);am,ac=output.graph(m,G,precision=r['parameter_output']['precision'])
        for i in range(len(G)):
            check(am[i].encloses(mean[i]) and am[i].radius<=delta,'mean enclosure')
            for j in range(len(G)):check(ac[i][j].encloses(cov[i][j]) and ac[i][j].radius<=delta,'covariance enclosure')
        expected=[0,1,0,1,0] if name=='coordinate' else [0,0,0]
        check([u['selected_packet'] for u in r['updates']]==expected,'selection sequence')
        if name=='rotated':check(all(Q(u['packet_energies'][1])==0 for u in r['updates']),'zero packet omitted')
        executions.append(dict(example=name,updates=r['iterations'],selected=expected,certificate_precision=r['chosen_precision'],output_precision=r['parameter_output']['precision'],gain=r['final_candidate']['gain'],score=r['rounded_score']))
    m=Model.parse({'H':[[1],[1]],'L':[[1]],'N':[[0],[0]],'sigma':1,'mean':[0],'observation':[0,0],'output_packets':[[[1]]],'input_packets':[[[1,0],[0,0]],[[0,0],[0,1]]]})
    B=matrix([['-1/3','2/3']],'gain');after,_,_=solver.packet_update(m,B,0,[0]);_,f=reference(m,B);_,fn=reference(m,after)
    check(en(mm(f,m.inputs[1]))==0 and en(mm(fn,m.inputs[1]))==Q(1,25),'input energy grows');check(en(f)==1 and en(fn)==Q(2,5),'total energy decreases')
    rejected=0
    bad=[lambda:solver.parameters(m,B,Q(1,10),0,[]),lambda:solver.parameters(m,B,Q(1,10),True,[0]),lambda:solver.parameters(m,B,Q(0),0,[0]),lambda:solver.parameters(m,B,Q(1,10),0,[1]),lambda:solver.solve(m,B,Q(1,10),Q(0),0,[0],[12]),lambda:solver.solve(m,B,Q(1,10),Q(1,1000),0,[0],[12.0])]
    for op in bad:
        try:op()
        except ValueError:rejected+=1
        else:raise AssertionError('invalid input accepted')
    limited=solver.solve(m,B,Q(1,1000),Q(1,1000),0,[0],[12],max_steps=0);check(limited['status']=='RESOURCE_LIMIT','step cap')
    limited_output=solver.solve(m,B,Q(1,10),Q(1,2**1000),0,[0],[12]);check(limited_output['status']=='RESOURCE_LIMIT','output cap')
    for r in [limited,limited_output]:
        try:solver.export_lean(m,B,Q(1,10),Q(1,1000),r,'MustFail')
        except ValueError:rejected+=1
        else:raise AssertionError('capped result exported')
    report=dict(status='PASS',assertions=checks,expected_rejections=rejected,cases=cases,executions=executions,
        input_packet_counterexample={'before':['1','0'],'after':['3/5','-1/5'],'input_energy_before':'0','input_energy_after':'1/25','total_energy_after':'2/5'},
        arithmetic='Exact Fraction; independent scalar model/residual sums and direct Joseph factors',non_claims=['Finite diagnostics are not a universal proof.','No timings or speedup comparison.'])
    p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','assertions','expected_rejections']}))
if __name__=='__main__':main()
