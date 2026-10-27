#!/usr/bin/env python3
"""Reproduce the monograph's dyadic matrix example and its declared figures.

Run from any directory. Exact algebra uses SymPy. The tail enclosure uses
only the supplied engine, and an independent closed-form interval is used
as a control. Figure curves are explanatory point evaluations, not intervals.
"""
from pathlib import Path
from dataclasses import asdict
from decimal import Decimal
import json,sys,math
import numpy as np
import sympy as sp
import mpmath as mp
from mpmath import iv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from interval_kcos import interval_positive_logsf
from directed_accuracy import outward_interval_string, interval_endpoint_strings, directed_relative_accuracy
OUT=ROOT/'book'/'figures_edition';OUT.mkdir(exist_ok=True)
REC=ROOT/'verification'/'current_revision';REC.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':12,'axes.labelsize':12,
                     'legend.fontsize':10,'pdf.fonttype':42,'savefig.bbox':'tight'})
A=sp.Matrix([[1,1,1,1,1,1],[1,-1,1,-1,1,-1],[1,1,-1,-1,-1,-1],[1,-1,-1,1,-1,1]])/2
K=A*A.T
U=sp.Matrix([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]])/2
assert U.T*U==sp.eye(4)
assert K==U*sp.diag(1,1,2,2)*U.T
blocks=[A[:,j:j+2] for j in (0,2,4)]
assert sum((B*B.T for B in blocks),sp.zeros(4))==K
assert blocks[1]==blocks[2]
v=sp.Matrix([1,2,-1,0]); assert sum((B*(B.T*v) for B in blocks),sp.zeros(4,1))==K*v
q=sp.Symbol('q',nonnegative=True)
f=(sp.exp(-q/4)-sp.exp(-q/2))/2
sf=2*sp.exp(-q/4)-sp.exp(-q/2)
assert sp.simplify(sp.diff(sf,q)+f)==0 and sf.subs(q,0)==1
th=(14-sp.sqrt(26))/40
assert sp.simplify(2/(1-2*th)+4/(1-4*th)-40)==0
with mp.workdps(100):
 theta=(14-mp.sqrt(26))/40
 exact=2*mp.exp(-10)-mp.exp(-20)
 theta_s=mp.nstr(theta,90)
 theta_val=float(theta)
 exact_s=mp.nstr(exact,70)
 x=np.linspace(0,170,800)
 density=.5*(np.exp(-x/4)-np.exp(-x/2))
 cgf=-np.log(1-2*theta_val)-np.log(1-4*theta_val)
 tilted=.5*(np.exp(-(0.25-theta_val)*x)-np.exp(-(0.5-theta_val)*x))*np.exp(-cgf)
 fig,ax=plt.subplots(figsize=(7,3.7),layout='constrained')
 ax.plot(x,density,label='Original density',lw=1.8)
 ax.plot(x,tilted,label='Tilted density',lw=1.8,linestyle='--')
 ax.axvline(40,linestyle=':',lw=1,label='Threshold q = 40')
 ax.set(xlim=(0,170),ylim=(0,None),xlabel='Quadratic-form value x',ylabel='Density')
 ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False)
 fig.savefig(OUT/'worked_tilt.pdf');plt.close(fig)
 s=mp.mpc('0.1','0.4'); vals=list(map(mp.mpf,['1.96','1.98','2.02','2.04']))
 mu=mp.mpf(2);delta=[v-mu for v in vals];alpha=2*s/(1-2*s*mu);rho=abs(alpha)*max(map(abs,delta))
 exact_cgf=-mp.fsum(mp.log(1-2*s*v) for v in vals)/2
 packet=[]
 for order in [0,2,4,6,8,10]:
  approx=-2*mp.log(1-2*s*mu)+mp.fsum(alpha**m*mp.fsum(d**m for d in delta)/m for m in range(1,order+1))/2
  error=abs(exact_cgf-approx);bound=2*rho**(order+1)/((order+1)*(1-rho))
  assert error<=bound
  packet.append({'order':order,'observed_error':mp.nstr(error,50),'analytic_bound':mp.nstr(bound,50)})
 fig,ax=plt.subplots(figsize=(7,3.7),layout='constrained')
 ax.semilogy([r['order'] for r in packet],[float(r['observed_error']) for r in packet],'o-',label='Point-evaluated error')
 ax.semilogy([r['order'] for r in packet],[float(r['analytic_bound']) for r in packet],'s--',label='Analytic remainder bound')
 ax.set(xlabel='Retained moment order',ylabel='Absolute CGF error',xticks=[0,2,4,6,8,10])
 ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False)
 fig.savefig(OUT/'worked_packet_error.pdf');plt.close(fig)
 # Refine rather than relax the requested tolerance after a failed fixed-resolution decision.
 refinements=[]
 for modes in [8192,16384]:
  result=interval_positive_logsf('40',['1','1','2','2'],theta_decimal=theta_s,
          upper_decimal='512',eta_decimal='0.245',K=modes,interval_dps=60)
  accuracy=directed_relative_accuracy(result.log10_interval,'0.02',dps=100)
  refinements.append({'modes':modes,'result':asdict(result),'accuracy':asdict(accuracy)})
 assert not refinements[0]['accuracy']['accepted'] and refinements[1]['accuracy']['accepted']
 iv.dps=100
 control=iv.log(2*iv.exp(-iv.mpf(10))-iv.exp(-iv.mpf(20)))/iv.log(10)
 control_s=outward_interval_string(control)
 lo,hi=map(Decimal,interval_endpoint_strings(result.log10_interval))
 clo,chi=map(Decimal,interval_endpoint_strings(control_s))
 contained=lo<=clo and chi<=hi
 assert result.passed_positive_sum and contained and accuracy.accepted
 # A tighter request must be rejected for this same fixed enclosure.
 rejected=not directed_relative_accuracy(result.log10_interval,'0.001',dps=100).accepted
 assert rejected
 data={'factor':str(A),'gram':str(K),'spectrum':['1','1','2','2'],
       'streamed_action':str(K*v),'exact_tail_formula':'2 exp(-q/4) - exp(-q/2), q>=0',
       'tail_at_q40':exact_s,'theta_at_q40':theta_s,'rho_packet':mp.nstr(rho,40),
       'packet_error_samples':packet,'refinements':refinements,'interval':asdict(result),'accuracy':asdict(accuracy),
       'independent_log10_interval':control_s,'independent_interval_contained':contained,
       'fixed_enclosure_rejects_0_001':rejected,'exact_algebra_assertions_passed':True,
       'figure_semantics':'Point-evaluated density and CGF curves illustrate declared finite inputs; not a production benchmark.'}
 (REC/'worked_example.json').write_text(json.dumps(data,indent=2)+'\n')
 def texnum(s,digits=5):
  value=mp.mpf(s);ex=int(mp.floor(mp.log10(abs(value))));m=value/mp.power(10,ex)
  return mp.nstr(m,digits)+r'\times10^{'+str(ex)+'}'
 rows='\n'.join(f"{r['order']} & ${texnum(r['observed_error'])}$ & ${texnum(r['analytic_bound'])}$\\\\" for r in packet)
 (ROOT/'book'/'worked_packet_table.tex').write_text(r'\begin{tabular}{rrr}\toprule Order & Point-evaluated error & Analytic bound\\\midrule'+'\n'+rows+'\n'+r'\bottomrule\end{tabular}'+'\n')
 # This outward display has deliberately coarse decimals, so the book itself contains an outer interval.
 from decimal import localcontext,ROUND_FLOOR,ROUND_CEILING
 with localcontext() as c:
  c.prec=100;c.rounding=ROUND_FLOOR;dlo=lo.quantize(Decimal('0.00000001'))
  c.rounding=ROUND_CEILING;dhi=hi.quantize(Decimal('0.00000001'))
 display=f'[{dlo},{dhi}]';display_acc=directed_relative_accuracy(display,'0.02',dps=100)
 assert display_acc.accepted
 text=r'''With $b=512$, $N=16384$, auxiliary tilt $\eta=0.245$, and 60 interval decimal digits, the supplied backend returns a logarithmic interval. Rounding its lower endpoint downward and its upper endpoint upward gives the readable enclosure
\[
\log_{10}P(Q\ge40)\in\bigl['''+str(dlo)+','+str(dhi)+r'''\bigr].
\]
At $N=8192$, the directed ratio upper bound is approximately $0.0246131$, which fails the requested tolerance $0.02$. Doubling the retained mode count, rather than relaxing the tolerance, gives the interval above. The full serialized interval has a directed multiplicative ratio upper bound below $'''+mp.nstr(mp.mpf(accuracy.ratio_upper)*mp.mpf('1.0001'),5)+r'''$. The displayed, coarser interval also meets the requested tolerance $0.02$. An independently evaluated interval for the exact expression $2e^{-10}-e^{-20}$ lies entirely inside the COS enclosure.

This same fixed enclosure does not meet tolerance $0.001$. The acceptance routine rejects that tighter request. This is an intended distinction between an accurate point estimate and an established enclosure width. The rank-four example has slower Fourier decay than the rank-eighty control developed later, so its mode count should not be interpreted as a general cost prediction.
'''
 (ROOT/'book'/'worked_enclosure_result.tex').write_text(text)
 print('Exact algebra: passed. Packet comparisons:',len(packet))
 print('Tail at q40:',exact_s)
 print('Directed interval:',display,'ratio bound',accuracy.ratio_upper,'contained',contained)
