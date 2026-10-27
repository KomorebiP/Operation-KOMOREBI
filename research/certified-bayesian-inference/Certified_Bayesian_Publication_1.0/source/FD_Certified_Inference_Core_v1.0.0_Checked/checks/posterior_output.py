#!/usr/bin/env python3
"""Rounded posterior parameter intervals. Exact Fraction emulation, not hardware floats.
The intervals enclose the Joseph Gaussian of the certified gain. Their centers
are not asserted to be a covariance matrix of a separate certified law.
"""
from __future__ import annotations
import argparse, json, hashlib
from fractions import Fraction as Q
from pathlib import Path
from exact_certificate import Model, matrix, rational, eye, scale, qlean, mlean, vlean
import rounded_certificate as rb
import precision_certificate as pb
import rounded_gain_solver as rs


def graph(m, gain, budget=False, precision=0):
    n,k=len(m.H[0]),len(m.H)
    if len(gain)!=n or any(len(row)!=k for row in gain):
        raise ValueError('Gain dimensions do not match.')
    if max(n,k,len(m.L[0]),len(m.N[0]))>8:
        raise ValueError('Dimension cap is 8.')
    if budget:
        inp,mm,ma,ms,tr,mv=pb.inp,pb.mul,pb.add,pb.add,pb.trans,pb.mv
        source,add,sub=pb.source,pb.plus,pb.plus
    else:
        p=precision
        if isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=512:
            raise ValueError('Precision must be an integer in 0..512.')
        inp=lambda x:rb.inp(p,x)
        mm=lambda x,y:rb.mm(p,x,y)
        ma=lambda x,y:rb.ma(p,x,y)
        ms=lambda x,y:rb.ms(p,x,y)
        tr=rb.tr;mv=lambda x,y:rb.mv(p,x,y)
        source=lambda x:rb.rexact(p,x)
        add=lambda x,y:rb.radd(p,x,y)
        sub=lambda x,y:rb.rsub(p,x,y)
    h,l,z,b=inp(m.H),inp(m.L),inp(m.N),inp(gain)
    prior=mm(l,tr(l));noise=ma(mm(z,tr(z)),inp(scale(m.sigma,eye(k))))
    op=ms(inp(eye(n)),mm(b,h))
    residual_vector=tuple(sub(x,y) for x,y in zip(map(source,m.observation),mv(h,tuple(map(source,m.mean)))))
    mean=tuple(add(x,y) for x,y in zip(map(source,m.mean),mv(b,residual_vector)))
    cov=ma(mm(mm(op,prior),tr(op)),mm(mm(b,noise),tr(b)))
    return mean,cov


def represent(m,gain,delta,max_precision=512):
    if delta<=0: raise ValueError('Output radius tolerance must be positive.')
    bm,bc=graph(m,gain,budget=True)
    coefficient=sum((b.coeff for b in bm),Q(0))+sum((b.coeff for row in bc for b in row),Q(0))
    p=pb.precision_for(coefficient,delta)
    if p>max_precision: raise rs.ResourceLimit(f'Output requires {p} bits; cap is {max_precision}.')
    mean,cov=graph(m,gain,precision=p)
    flat=mean+tuple(b for row in cov for b in row)
    if any(b.radius<0 or b.radius>delta for b in flat):
        raise ArithmeticError('Output radius invariant failed.')
    return dict(precision=p,coefficient=str(coefficient),requested_radius=str(delta),
        maximum_radius=str(max((b.radius for b in flat),default=Q(0))),
        mean={'center':[str(b.center) for b in mean],'radius':[str(b.radius) for b in mean]},
        covariance=rb.serialize_ball_matrix(cov),
        interpretation='Intervals enclose parameters of the Joseph Gaussian at final_candidate.gain. Covariance centers are not a separately certified covariance.')


def solve(m,initial,eps,delta,probes,max_steps=10000,max_precision=512):
    if delta<=0:raise ValueError('Output radius tolerance must be positive.')
    result=rs.solve(m,initial,eps,probes,max_steps,max_precision)
    if result['status']!='PASS_ROUNDED_SOLVER_PROVISIONAL':return result
    try:
        result['parameter_output']=represent(m,matrix(result['final_candidate']['gain'],'gain'),delta,max_precision)
    except rs.ResourceLimit as e:
        return {'status':'RESOURCE_LIMIT','reason':str(e),'completed_output_certified':False}
    result['status']='PASS_OUTPUT_PROVISIONAL'
    result['proof_status']='Compile exported Lean instance. Python results alone are not formal certificates.'
    return result


def export_lean(m,initial,eps,delta,result,namespace):
    if result.get('status')!='PASS_OUTPUT_PROVISIONAL':raise ValueError('Only complete successful output may export proof.')
    prior=dict(result,status='PASS_ROUNDED_SOLVER_PROVISIONAL')
    text=rs.export_lean(m,initial,eps,prior,namespace)
    text='import Komorebi.PosteriorOutputSolver\n'+text
    end=f'end Komorebi.RoundoffSolver.{namespace}'
    text=text[:text.rindex(end)]
    o=result['parameter_output'];p=o['precision'];n,k=len(m.H[0]),len(m.H);a,b=len(m.outputs),len(m.inputs)
    d=qlean(delta);e=qlean(eps);vp=result['chosen_precision'];ps='['+', '.join(map(str,result['precision_probes']))+']'
    mc=vlean(tuple(map(Q,o['mean']['center'])));mr=vlean(tuple(map(Q,o['mean']['radius'])))
    cc=mlean(matrix(o['covariance']['center'],'covariance centers'));cr=mlean(matrix(o['covariance']['radius'],'covariance radii'))
    text+='\nopen Komorebi.PosteriorOutput\n'
    text+=f'\ndef outputArrays := represent model finalGain {d}\n'
    text+=f'theorem output_precision_computed : outputPrecision model finalGain {d} = {p} := by decide +kernel\n'
    for name,lhs,rhs in [('mean_centers','fun i => (outputArrays.mean i).center',mc),('mean_radii','fun i => (outputArrays.mean i).radius',mr),('covariance_centers','fun i j => (outputArrays.covariance i j).center',cc),('covariance_radii','fun i j => (outputArrays.covariance i j).radius',cr)]:
        proof=('by funext i j; fin_cases i; fin_cases j; decide +kernel' if n==1 else 'by funext i j; fin_cases i <;> fin_cases j <;> decide +kernel') if name.startswith('covariance') else 'by decide +kernel'
        text+=f'theorem {name}_computed : ({lhs}) = {rhs} := {proof}\n'
    text+=f'''\ndef outputResult : Result (Fin {n}) (Fin {k}) (Fin {a}) (Fin {b}) :=
  ⟨{vp},certificate,outputPrecision model finalGain {d},outputArrays⟩

theorem output_return : run model outputs inputs {e} {d} {ps} initial = some outputResult := by
  simp only [run, ite_eq_left (show (0 : ℚ) < {d} by norm_num), rounded_return]
  rfl

theorem output_valid : ResultValid model outputs inputs {e} {d} outputResult :=
  run_sound model outputs inputs {e} {d} {ps} initial outputResult output_return

{end}
'''
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--output-radius',default='1/1000');ap.add_argument('--try-precisions',type=int,nargs='*',default=[4,12])
    ap.add_argument('--max-steps',type=int,default=10000);ap.add_argument('--max-precision',type=int,default=512)
    ap.add_argument('--emit-lean',type=Path);ap.add_argument('--namespace',default='GeneratedOutput')
    args=ap.parse_args();raw=args.input.read_bytes()
    if len(raw)>1000000:raise ValueError('Input byte cap exceeded.')
    data=json.loads(raw);m=Model.parse(data['model']);initial=matrix(data['initial_gain'],'initial_gain')
    eps=rational(data['epsilon']);delta=rational(args.output_radius)
    result=solve(m,initial,eps,delta,args.try_precisions,args.max_steps,args.max_precision)
    result['input_sha256']=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    if args.emit_lean:
        source=export_lean(m,initial,eps,delta,result,args.namespace)
        args.emit_lean.parent.mkdir(parents=True,exist_ok=True);args.emit_lean.write_text(source)
    print(result['status'],result.get('parameter_output',{}).get('precision'))
    return 0 if result['status']=='PASS_OUTPUT_PROVISIONAL' else 2

if __name__=='__main__':raise SystemExit(main())
