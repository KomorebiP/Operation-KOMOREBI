#!/usr/bin/env python3
"""Certified cached exact-packet solver. Python execution is provisional until Lean checks the export."""
from __future__ import annotations
from dataclasses import dataclass,field
from fractions import Fraction as Q
from pathlib import Path
import argparse,hashlib,json,time
from exact_certificate import Model,matrix,rational,encode,eye,packet_valid,mlean,vlean,qlean,shape
import rounded_certificate as rb
import precision_certificate as pb
import posterior_output as po
import adaptive_packet_solver as old
from rounded_gain_solver import ResourceLimit

@dataclass
class Work:
    multiplications:int=0
    additions:int=0
    comparisons:int=0
    packet_refreshes:int=0
    full_residuals:int=0
    def mm(self,A,B):
        n,k,m=len(A),len(B),len(B[0]);C=[[Q(0) for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for h in range(k):
                if A[i][h]==0:continue
                for j in range(m):
                    C[i][j]+=A[i][h]*B[h][j];self.multiplications+=1;self.additions+=1
        return tuple(tuple(row) for row in C)
    def add_scaled(self,A,t,B):
        self.multiplications+=len(A)*len(A[0]);self.additions+=len(A)*len(A[0])
        return tuple(tuple(x+t*y for x,y in zip(a,b)) for a,b in zip(A,B))
    def energy(self,A):
        self.multiplications+=len(A)*len(A[0]);self.additions+=len(A)*len(A[0])
        return sum((x*x for row in A for x in row),Q(0))
    def choose(self,es,seed,scan):
        a=seed
        for b in scan:
            self.comparisons+=1
            if es[a]<es[b]:a=b
        return a

@dataclass
class Context:
    S:tuple
    C:tuple
    T:tuple
    step:Q
    weight:Q
    rate:Q

@dataclass
class Cache:
    gain:tuple
    residuals:list
    energies:list
    total:Q

def prepare(m,work):
    # Compute each model matrix once. Work counters below concern iterative matrix work only.
    S=m.S;P=m.P;H=m.H
    C=tuple(tuple(sum((P[i][h]*H[j][h] for h in range(len(P))),Q(0)) for j in range(len(H))) for i in range(len(P)))
    tau=1/(m.sigma+sum((S[i][i] for i in range(len(S))),Q(0)))
    T=tuple(tuple(Q(i==j)-tau*S[i][j] for j in range(len(S))) for i in range(len(S)))
    weight=(m.sigma+sum((x*x for x in m.innovation),Q(0)))/m.sigma**2
    return Context(S,C,T,tau,weight,1-(1-(1-m.sigma*tau)**2)/len(m.outputs))

def residual(ctx,B,work):
    work.full_residuals+=1
    return work.add_scaled(ctx.C,Q(-1),work.mm(B,ctx.S))

def initialize(m,ctx,B,work):
    F=residual(ctx,B,work);G=[work.mm(p,F) for p in m.outputs];es=[work.energy(g) for g in G]
    work.packet_refreshes+=len(G);work.additions+=len(G)
    return Cache(B,G,es,sum(es,Q(0)))

def advance(ctx,c,a,work):
    G=c.residuals[a];Gn=work.mm(G,ctx.T);en=work.energy(Gn);B=work.add_scaled(c.gain,ctx.step,G)
    total=c.total-c.energies[a]+en;work.additions+=2;work.packet_refreshes+=1
    gs=c.residuals.copy();es=c.energies.copy();gs[a]=Gn;es[a]=en
    return Cache(B,gs,es,total)

def validate(m,B,eps,delta,seed,scan,probes,max_steps,max_bits):
    if eps<=0 or delta<=0 or m.sigma<=0:raise ValueError('Positive tolerances and noise floor required.')
    n,k=len(m.H[0]),len(m.H)
    if max(n,k,len(m.L[0]),len(m.N[0]))>8:raise ValueError('Release dimension cap is 8.')
    if shape(B)!=(n,k):raise ValueError('Gain shape mismatch.')
    if not packet_valid(m.outputs,n) or not packet_valid(m.inputs,k):raise ValueError('Invalid packet geometry.')
    A=len(m.outputs)
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0<=seed<A:raise ValueError('Invalid seed.')
    if not isinstance(scan,list) or len(scan)>128 or any(isinstance(a,bool) or not isinstance(a,int) or not 0<=a<A for a in scan) or set(scan)!=set(range(A)):raise ValueError('Scan must cover all output labels.')
    if not isinstance(probes,list) or len(probes)>16 or any(isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512 for p in probes):raise ValueError('Invalid precision probes.')
    if isinstance(max_steps,bool) or not isinstance(max_steps,int) or not 0<=max_steps<=100000:raise ValueError('Invalid step cap.')
    if isinstance(max_bits,bool) or not isinstance(max_bits,int) or not 64<=max_bits<=1000000:raise ValueError('Invalid bit cap.')

def solve(m,B,eps,delta,seed,scan,probes,max_steps=10000,max_bits=32768,mode='cached',record_trace=True):
    start=time.perf_counter();validate(m,B,eps,delta,seed,scan,probes,max_steps,max_bits);work=Work();ctx=prepare(m,work)
    if mode=='full':
        F=residual(ctx,B,work);cache=Cache(B,[F],[],work.energy(F))
    else:cache=initialize(m,ctx,B,work)
    initial_score=cache.total*ctx.weight;f=initial_score/((eps/2)**2*(1-ctx.rate));fuel=max(0,-((-f.numerator)//f.denominator))
    if mode not in ['cached','recompute','full']:raise ValueError('Unknown solve mode.')
    setup_end=time.perf_counter();trace=[];labels=[]
    try:
        for it in range(min(fuel,max_steps)+1):
            if any(max(abs(x.numerator).bit_length(),x.denominator.bit_length())>max_bits for row in cache.gain for x in row):raise ResourceLimit('Rational bit cap reached.')
            score=cache.total*ctx.weight
            if score<=eps*eps/4:break
            if it==max_steps:raise ResourceLimit('Update cap reached.')
            if it==fuel:raise ArithmeticError('Proved horizon exhausted.')
            a=work.choose(cache.energies,seed,scan) if mode!='full' else -1;labels.append(a)
            if record_trace:trace.append(dict(iteration=it,selected_packet=a,energies=encode(cache.energies),total=str(cache.total)))
            if mode=='cached':cache=advance(ctx,cache,a,work)
            elif mode=='recompute':
                gain=work.add_scaled(cache.gain,ctx.step,cache.residuals[a]);cache=initialize(m,ctx,gain,work)
            else:
                F=cache.residuals[0];gain=work.add_scaled(cache.gain,ctx.step,F);Fn=work.mm(F,ctx.T);cache=Cache(gain,[Fn],[],work.energy(Fn))
        solve_end=time.perf_counter();pstar,_,_=pb.sufficient_precision(m,cache.gain,eps*eps/4);attempts=[]
        for p in probes+[pstar]:
            if p>512:raise ResourceLimit('Verification precision cap reached.')
            candidate,_=rb.produce(m,cache.gain,p);passed=candidate.tolerance(m,eps)
            attempts.append(dict(precision=p,score=str(candidate.score(m)),passed=passed))
            if passed:break
        else:raise ArithmeticError('Sufficient final verifier failed.')
        cert_end=time.perf_counter();params=po.represent(m,cache.gain,delta);end=time.perf_counter()
        result=dict(status='PASS_CACHED_PROVISIONAL' if mode=='cached' else 'BENCHMARK_BASELINE_PROVISIONAL',mode=mode,iterations=it,seed=seed,scan=scan,
            precision_probes=probes,chosen_precision=p,final_candidate=candidate.to_dict(),rounded_score=str(candidate.score(m)),exact_score=str(score),
            parameter_output=params,requested_tolerance=str(eps),fuel=fuel,selected_packets=labels,iteration_trace=trace,certificate_attempts=attempts,
            work=vars(work),timing_seconds=dict(setup=setup_end-start,iteration=solve_end-setup_end,certificate=cert_end-solve_end,output=end-cert_end,total=end-start),
            proof_status='Compile emitted Lean source. Timings/counters are diagnostic and exclude Lean checking.',model_sha256=m.digest())
        return result
    except ResourceLimit as e:return dict(status='RESOURCE_LIMIT',reason=str(e),iterations=len(labels),selected_packets=labels,proof_export_permitted=False)

def export_lean(m,B,eps,delta,r,namespace):
    if r.get('status')!='PASS_CACHED_PROVISIONAL':raise ValueError('Only completed cached runs can export proofs.')
    # Reuse only exact-data formatting from the retained exporter, never its algorithm theorem.
    fake=dict(r,status='PASS_ADAPTIVE_PROVISIONAL',parameters={'fuel':r['fuel']},updates=[{'selected_packet':a} for a in r['selected_packets']])
    text=old.export_lean(m,B,eps,delta,fake,namespace)
    text=text[:text.index('theorem fuel_computed')]
    text=text.replace('namespace Komorebi.AdaptivePosterior.','namespace Komorebi.CachedPosterior.')
    text='import Komorebi.CachedPacketOutput\n'+text
    n,k=shape(B);A,D=len(m.outputs),len(m.inputs);seed=r['seed'];scan='['+', '.join(map(str,r['scan']))+']';probes='['+', '.join(map(str,r['precision_probes']))+']'
    e,d=qlean(eps),qlean(delta);p=r['chosen_precision'];it=r['iterations']
    text+=f'''def initialCache := initialState model outputs initial
def finalCache := trajectory (prepare model) {seed} {scan} initialCache {it}
theorem fuel_computed : Komorebi.AdaptivePosterior.adaptiveFuel model initial {e} {A} = {r['fuel']} := by decide +kernel
theorem gain_computed : finalCache.gain = finalGain := by decide +kernel
theorem exact_score_computed : score (prepare model) finalCache = {qlean(Q(r['exact_score']))} := by decide +kernel
theorem rounded_score_computed : candidateScore model certificate = {qlean(Q(r['rounded_score']))} := by decide +kernel
theorem cached_return : solveCached model outputs inputs {seed} {scan} {e} {probes} initial = some ({p},certificate) := by decide +kernel
'''
    for i,a in enumerate(r['selected_packets']):text+=f'theorem selected_{i} : chosen {seed} {scan} (trajectory (prepare model) {seed} {scan} initialCache {i}) = {a} := by decide +kernel\n'
    o=r['parameter_output'];op=o['precision'];text+=f'def outputArrays := represent model finalGain {d}\ntheorem output_precision_computed : outputPrecision model finalGain {d} = {op} := by decide +kernel\n'
    for name,lhs,rhs in [('mean_centers','fun i => (outputArrays.mean i).center',vlean(tuple(map(Q,o['mean']['center'])))),('mean_radii','fun i => (outputArrays.mean i).radius',vlean(tuple(map(Q,o['mean']['radius'])))),('covariance_centers','fun i j => (outputArrays.covariance i j).center',mlean(matrix(o['covariance']['center'],'cov'))),('covariance_radii','fun i j => (outputArrays.covariance i j).radius',mlean(matrix(o['covariance']['radius'],'rad')))]:
        proof=('by funext i j; fin_cases i; fin_cases j; decide +kernel' if n==1 else 'by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel') if name.startswith('covariance') else 'by decide +kernel'
        text+=f'theorem {name}_computed : ({lhs}) = {rhs} := {proof}\n'
    text+=f'''def outputResult : Result (Fin {n}) (Fin {k}) (Fin {A}) (Fin {D}) := ⟨{p},certificate,outputPrecision model finalGain {d},outputArrays⟩
theorem output_return : runCached model outputs inputs {seed} {scan} {e} {d} {probes} initial = some outputResult := by
  simp only [runCached,ite_eq_left (show (0 : ℚ) < {d} by norm_num),cached_return]
  rfl
theorem output_valid : ResultValid model outputs inputs {e} {d} outputResult :=
  runCached_sound model outputs inputs {seed} {scan} {e} {d} {probes} initial outputResult output_return
end Komorebi.CachedPosterior.{namespace}
'''
    return text

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedCached');ap.add_argument('--max-steps',type=int,default=10000);ap.add_argument('--try-precisions',type=int,nargs='*',default=[4,12]);x=ap.parse_args()
    raw=x.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded.')
    data=json.loads(raw);m=Model.parse(data['model']);B=matrix(data['initial_gain'],'gain');eps=rational(data['epsilon']);delta=rational(data['output_radius'])
    r=solve(m,B,eps,delta,data['seed'],data['scan'],x.try_precisions,x.max_steps);r['input_sha256']=hashlib.sha256(raw).hexdigest()
    x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(r,indent=2)+'\n')
    if x.emit_lean:
        source=export_lean(m,B,eps,delta,r,x.namespace);x.emit_lean.parent.mkdir(parents=True,exist_ok=True);x.emit_lean.write_text(source)
    print(r['status'],'updates',r['iterations'])
    return 0 if r['status']=='PASS_CACHED_PROVISIONAL' else 2
if __name__=='__main__':raise SystemExit(main())
