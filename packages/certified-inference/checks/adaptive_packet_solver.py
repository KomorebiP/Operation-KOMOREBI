#!/usr/bin/env python3
"""Greedy exact-rational output-packet updates, rounded verification and output arrays.
The full packet scan is a dense reference implementation. No speedup claim.
A Python PASS is provisional until its exported Lean instance compiles.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from fractions import Fraction as Q
from exact_certificate import Model, matrix, rational, energy, vec_energy, shape, encode, mul, add, scale, mlean, vlean, qlean
import rounded_certificate as rb
import precision_certificate as pb
import posterior_output as po
from rounded_gain_solver import ResourceLimit

def parameters(m,initial,eps,seed,scan):
    if eps<=0 or m.sigma<=0:raise ValueError('Positive tolerance and noise floor required.')
    if shape(initial)!=(len(m.H[0]),len(m.H)):raise ValueError('Gain shape mismatch.')
    count=len(m.outputs)
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0<=seed<count:raise ValueError('Invalid seed.')
    if not isinstance(scan,list) or len(scan)>128 or any(isinstance(a,bool) or not isinstance(a,int) or not 0<=a<count for a in scan):raise ValueError('Invalid scan labels.')
    if set(scan)!=set(range(count)):raise ValueError('Scan must cover every output packet.')
    pb.graph(m,initial) # finite dimensions and valid packet geometry
    cap=m.sigma+sum((m.S[i][i] for i in range(len(m.S))),Q(0));tau=1/cap
    q=(1-m.sigma/cap)**2;rate=1-(1-q)/count
    weight=(m.sigma+vec_energy(m.innovation))/m.sigma**2
    score=energy(m.residual(initial))*weight
    f=score/((eps/2)**2*(1-rate));fuel=max(0,-((-f.numerator)//f.denominator))
    return dict(step=tau,full_rate=q,adaptive_rate=rate,weight=weight,initial_score=score,fuel=fuel)

def packet_update(m,gain,seed,scan):
    f=m.residual(gain);packets=[mul(p,f) for p in m.outputs]
    energies=list(map(energy,packets));a=seed
    for b in scan:
        if energies[a]<energies[b]:a=b
    tau=1/(m.sigma+sum((m.S[i][i] for i in range(len(m.S))),Q(0)))
    return add(gain,scale(tau,packets[a])),a,energies

def solve(m,initial,eps,delta,seed,scan,probes,max_steps=10000,max_precision=512,max_bits=32768):
    if delta<=0:raise ValueError('Positive output radius tolerance required.')
    if not isinstance(probes,list) or len(probes)>16 or any(isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512 for p in probes):raise ValueError('Invalid precision probes.')
    for x,lo,hi in [(max_steps,0,100000),(max_precision,1,512),(max_bits,64,1000000)]:
        if isinstance(x,bool) or not isinstance(x,int) or not lo<=x<=hi:raise ValueError('Invalid resource cap.')
    pars=parameters(m,initial,eps,seed,scan);gain=initial;updates=[];trace=[]
    try:
        for n in range(min(max_steps,pars['fuel'])+1):
            if any(max(abs(x.numerator).bit_length(),x.denominator.bit_length())>max_bits for row in gain for x in row):raise ResourceLimit('Gain rational size cap reached.')
            pstar,_,_=pb.sufficient_precision(m,gain,eps*eps/4);attempts=[]
            for p in probes+[pstar]:
                if p>max_precision:raise ResourceLimit(f'Certificate requires {p} bits; cap is {max_precision}.')
                candidate,_=rb.produce(m,gain,p);passed=candidate.tolerance(m,eps)
                attempts.append(dict(precision=p,score=str(candidate.score(m)),passed=passed))
                if passed:
                    trace.append(dict(iteration=n,certificates=attempts))
                    output=po.represent(m,gain,delta,max_precision)
                    return dict(status='PASS_ADAPTIVE_PROVISIONAL',iterations=n,parameters=encode(pars),seed=seed,scan=scan,
                        chosen_precision=p,precision_probes=probes,final_candidate=candidate.to_dict(),rounded_score=str(candidate.score(m)),
                        iteration_trace=trace,updates=updates,parameter_output=output,requested_tolerance=str(eps),
                        model_sha256=m.digest(),proof_status='Compile exported Lean source to certify this instance.',
                        arithmetic='Exact rational packet updates; outward-rounded dyadic certificate and parameter arithmetic.',
                        non_claims=['No rounded packet-update convergence theorem.','No hierarchy-changing refinement or speedup claim.',
                            'No hardware floating-point, bounded-word, parser-fidelity or executable sampler theorem.'])
            trace.append(dict(iteration=n,certificates=attempts))
            if n==pars['fuel']:raise ArithmeticError('Proved horizon failed.')
            if n==max_steps:raise ResourceLimit('Update cap reached.')
            gain,a,es=packet_update(m,gain,seed,scan)
            updates.append(dict(iteration=n+1,selected_packet=a,packet_energies=encode(es),gain=encode(gain)))
    except ResourceLimit as e:
        return dict(status='RESOURCE_LIMIT',reason=str(e),parameters=encode(pars),updates=updates,iteration_trace=trace,posterior_tolerance_certified=False)
    raise ArithmeticError('Unreachable solver state.')

def export_lean(m,initial,eps,delta,result,namespace):
    if result.get('status')!='PASS_ADAPTIVE_PROVISIONAL':raise ValueError('Failed/capped runs cannot export a proof.')
    if not namespace.isascii() or not namespace.isidentifier():raise ValueError('ASCII identifier required.')
    g=matrix(result['final_candidate']['gain'],'gain');n,k=shape(g);u,w=len(m.L[0]),len(m.N[0]);a,b=len(m.outputs),len(m.inputs)
    seed=result['seed'];scan='['+', '.join(map(str,result['scan']))+']';probes='['+', '.join(map(str,result['precision_probes']))+']'
    fuel=result['parameters']['fuel'];it=result['iterations'];p=result['chosen_precision'];e=qlean(eps);d=qlean(delta)
    lines=['import Komorebi.AdaptivePacketOutput','import Komorebi.AdaptivePacketOrigin','import Komorebi.AdaptivePacketInvariants',
      'import Komorebi.RationalSolverDecidable','import Mathlib.LinearAlgebra.Matrix.Notation','',
      'set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 8000000',
      f'namespace Komorebi.AdaptivePosterior.{namespace}',
      'open Komorebi.ExactPosterior Komorebi.RoundedPosterior Komorebi.PosteriorOutput Komorebi.QuadraticTransport','',
      f'def model : RationalModel (Fin {n}) (Fin {k}) (Fin {u}) (Fin {w}) where',
      f'  observationMatrix := {mlean(m.H)}',f'  priorFactor := {mlean(m.L)}',f'  noiseFactor := {mlean(m.N)}',
      f'  noiseFloor := {qlean(m.sigma)}',f'  mean := {vlean(m.mean)}',f'  observation := {vlean(m.observation)}',
      f'def outputs : Fin {a} → Matrix (Fin {n}) (Fin {n}) ℚ := !['+', '.join(mlean(x) for x in m.outputs)+']',
      f'def inputs : Fin {b} → Matrix (Fin {k}) (Fin {k}) ℚ := !['+', '.join(mlean(x) for x in m.inputs)+']',
      f'def initial : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(initial)}',
      f'def finalGain : Matrix (Fin {n}) (Fin {k}) ℚ := {mlean(g)}',
      f'def certificate := roundedCandidate {p} model outputs inputs finalGain',
      f'theorem fuel_computed : adaptiveFuel model initial {e} {a} = {fuel} := by decide +kernel',
      f'theorem iterate_computed : greedyGain model outputs {seed} {scan} initial {it} = finalGain := by decide +kernel',
      f'theorem score_computed : candidateScore model certificate = {qlean(Q(result["rounded_score"]))} := by decide +kernel',
      f'theorem adaptive_return : solveAdaptive model outputs inputs {seed} {scan} {e} {probes} initial = some ({p},certificate) := by decide +kernel',
      f'theorem posterior_tolerance : wasserstein2 model.posterior (model.approximation certificate.gain) ≤ ENNReal.ofReal (({e} : ℚ) : ℝ) :=',
      f'  adaptive_solver_return_bounds_posterior model outputs inputs {seed} {scan} {e} {probes} initial {p} certificate adaptive_return']
    for i,up in enumerate(result['updates']):
        lines.append(f'theorem selected_{i} : selectPacket model outputs {seed} {scan} (greedyGain model outputs {seed} {scan} initial {i}) = {up["selected_packet"]} := by decide +kernel')
    o=result['parameter_output'];op=o['precision'];mc=vlean(tuple(map(Q,o['mean']['center'])));mr=vlean(tuple(map(Q,o['mean']['radius'])))
    cc=mlean(matrix(o['covariance']['center'],'cov'));cr=mlean(matrix(o['covariance']['radius'],'cov radius'))
    lines += [f'def outputArrays := represent model finalGain {d}',f'theorem output_precision_computed : outputPrecision model finalGain {d} = {op} := by decide +kernel']
    for name,lhs,rhs in [('mean_centers','fun i => (outputArrays.mean i).center',mc),('mean_radii','fun i => (outputArrays.mean i).radius',mr),('covariance_centers','fun i j => (outputArrays.covariance i j).center',cc),('covariance_radii','fun i j => (outputArrays.covariance i j).radius',cr)]:
        proof=('by funext i j; fin_cases i; fin_cases j; decide +kernel' if n==1 else 'by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel') if name.startswith('covariance') else 'by decide +kernel'
        lines.append(f'theorem {name}_computed : ({lhs}) = {rhs} := {proof}')
    lines += [f'def outputResult : Result (Fin {n}) (Fin {k}) (Fin {a}) (Fin {b}) := ⟨{p},certificate,outputPrecision model finalGain {d},outputArrays⟩',
      f'theorem output_return : runAdaptive model outputs inputs {seed} {scan} {e} {d} {probes} initial = some outputResult := by',
      f'  simp only [runAdaptive, ite_eq_left (show (0 : ℚ) < {d} by norm_num), adaptive_return]', '  rfl',
      f'theorem output_valid : ResultValid model outputs inputs {e} {d} outputResult :=',
      f'  runAdaptive_sound model outputs inputs {seed} {scan} {e} {d} {probes} initial outputResult output_return',
      f'end Komorebi.AdaptivePosterior.{namespace}','']
    return '\n'.join(lines)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedAdaptive')
    ap.add_argument('--try-precisions',type=int,nargs='*',default=[4,12]);ap.add_argument('--max-steps',type=int,default=10000)
    ap.add_argument('--max-precision',type=int,default=512);ap.add_argument('--max-bits',type=int,default=32768)
    x=ap.parse_args();raw=x.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded.')
    data=json.loads(raw);m=Model.parse(data['model']);initial=matrix(data['initial_gain'],'initial_gain');eps=rational(data['epsilon']);delta=rational(data['output_radius'])
    r=solve(m,initial,eps,delta,data['seed'],data['scan'],x.try_precisions,x.max_steps,x.max_precision,x.max_bits)
    r['input_sha256']=hashlib.sha256(raw).hexdigest();x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(r,indent=2)+'\n')
    if x.emit_lean:
        source=export_lean(m,initial,eps,delta,r,x.namespace);x.emit_lean.parent.mkdir(parents=True,exist_ok=True);x.emit_lean.write_text(source)
    print(r['status'],'updates',r.get('iterations'),'certificate bits',r.get('chosen_precision'),'selected',[u['selected_packet'] for u in r['updates']])
    return 0 if r['status']=='PASS_ADAPTIVE_PROVISIONAL' else 2
if __name__=='__main__':raise SystemExit(main())
