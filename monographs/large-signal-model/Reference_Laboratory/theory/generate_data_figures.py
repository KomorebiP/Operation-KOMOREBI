"""Six separate figures from declared formulas and replayed records.

No fitted data or claimed measurements are fabricated. Uses Matplotlib defaults,
no explicit color choices. The 3D figure is a genuine moment-cone parametrization.
"""
from pathlib import Path
import json,sys
from fractions import Fraction as F
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from data_certificate_reference import NODES,WEIGHTS,probability_row

def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True);ledger={}
    report=json.loads((ROOT/'verification/dependent_data_result.json').read_text())
    cert=json.loads((ROOT/'certificates/dependent_data_certificate.json').read_text())
    def save(fig,name,source):
        for ext in ['pdf','png','svg']:fig.savefig(out/f'{name}.{ext}',bbox_inches='tight',dpi=160)
        ledger[name]=source;plt.close(fig)
    t=np.arange(0,41)
    fig,ax=plt.subplots(figsize=(7.5,4.4),layout='constrained')
    ax.plot(t,np.minimum(1,t*float(F(81687,640000))),label='0.7.0: reset weight 1/8')
    ax.plot(t,np.minimum(1,t*float(F(87471,2560000))),label='0.8.0: reset weight 1/32')
    ax.set(xlabel='Future record length',ylabel='Total-variation upper bound',title='A smaller checked repair, with its cost retained',ylim=(0,1.04))
    ax.legend(loc='upper left');ax.grid(alpha=.2)
    save(fig,'41_smaller_repair',{'type':'analytic bounds','old_slope':'81687/640000','new_slope':'87471/2560000','not_measured_errors':True})
    rows=report['checkpoints'];n=np.array([r['transitions'] for r in rows])
    fig,ax=plt.subplots(figsize=(7.5,4.6),layout='constrained')
    for p in ['a','b']:
        lo=np.array([float(F(r[p]['lower'])) for r in rows]);hi=np.array([float(F(r[p]['upper'])) for r in rows]);mid=(lo+hi)/2
        ax.errorbar(n,mid,yerr=np.vstack([mid-lo,hi-mid]),capsize=3,marker='o',label=f'Outer interval for {p}')
    ax.axhline(.4,linestyle='--',linewidth=.8,label='Generating a = 2/5')
    ax.axhline(.2,linestyle=':',linewidth=.8,label='Generating b = 1/5')
    ax.set(xscale='log',xlabel='Observed dependent transitions',ylabel='Parameter interval',title='Time-uniform confidence, conditional on the model')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2);ax.grid(alpha=.2)
    save(fig,'42_confidence_intervals',{'type':'one seeded exact-distribution trajectory','source':'verification/dependent_data_result.json','empirical_coverage_experiment':False})
    fig,ax=plt.subplots(figsize=(6.8,6),layout='constrained')
    ax.plot([1,0,-1,0,1],[0,1,0,-1,0],linestyle='--',label='Sufficient validity region |a| + |b| <= 1')
    for r in rows:
        if r['transitions'] not in [4096,32768,262144]:continue
        al,ah=float(F(r['a']['lower'])),float(F(r['a']['upper']));bl,bh=float(F(r['b']['lower'])),float(F(r['b']['upper']))
        ax.plot([al,ah,ah,al,al],[bl,bl,bh,bh,bl],label=f"{r['transitions']:,} transitions")
    ax.plot([.4],[.2],marker='x',markersize=9,label='Generating parameter, verification only')
    ax.set(xlabel='Parameter a',ylabel='Parameter b',title='The whole uncertainty set must fit the certificate',aspect='equal',xlim=(-1.1,1.1),ylim=(-1.1,1.1))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),fontsize=8);ax.grid(alpha=.2)
    save(fig,'43_confidence_geometry',{'type':'outer rectangles and sufficient geometry','not_minimal_validity_region':True,'source':'verification/dependent_data_result.json'})
    fig=plt.figure(figsize=(7.4,5.8),layout='constrained');ax=fig.add_subplot(111,projection='3d')
    s=np.linspace(-1,1,27);m=np.linspace(.04,1.1,16);S,M=np.meshgrid(s,m)
    ax.plot_wireframe(M*S,M*S*S,M,rstride=3,cstride=2,linewidth=.65)
    ax.plot_wireframe(M*S,M,M,rstride=3,cstride=2,linewidth=.45,alpha=.5)
    ax.plot(s,s*s,np.ones_like(s),linewidth=1.8)
    ax.plot(s,np.ones_like(s),np.ones_like(s),linewidth=1.1)
    ax.view_init(elev=22,azim=-54)
    ax.set(xlabel='First moment',ylabel='Second moment',zlabel='',title='A curved moment cone, not a free matrix-error ball')
    ax.text2D(.02,.87,'Vertical axis: mass',transform=ax.transAxes)
    ax.text2D(.02,.02,'Boundary: x² = m y      Upper face: y = m',transform=ax.transAxes,fontsize=10)
    save(fig,'44_moment_cone',{'type':'analytic geometric parametrization','domain':'[[m,x],[x,y]] PSD; m-y >= 0','full_validity_from_proposition_not_wireframe':True})
    law=cert['law'];D=float(F(law['one_step_TV_upper']));rho=float(F(cert['confidence']['density_floor']));t=np.arange(0,121)
    fig,ax=plt.subplots(figsize=(7.5,4.8),layout='constrained')
    ax.plot(t,np.minimum(1,t*D),label='Full-record TV upper bound')
    ax.plot(t,np.minimum(1,D*(1-(1-rho)**t)/rho),label='One-time marginal TV upper bound')
    a,b=F(law['center']['a']),F(law['center']['b']);P=np.array([[float(p) for p in probability_row(s,F(2,5),F(1,5))] for s in NODES]);Q=np.array([[float(p) for p in probability_row(s,a,b)] for s in NODES])
    p=np.array([0.,0.,1.,0.,0.]);q=p.copy();es=[0.]
    for _ in t[1:]:p=p@P;q=q@Q;es.append(np.abs(p-q).sum()/2)
    ax.plot(t,es,linestyle=':',label='Finite Float64 marginal comparison')
    ax.set(xlabel='Future time / record length',ylabel='Total variation',title='Single-time prediction and complete records are different',ylim=(-.01,1.04))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16));ax.grid(alpha=.2)
    save(fig,'45_prediction_horizons',{'type':'analytic bounds and separately labeled finite numerical comparison','delta':str(F(law['one_step_TV_upper'])),'rho':str(F(cert['confidence']['density_floor'])),'times':t.tolist(),'numerical_marginal_errors':es})
    fig,ax=plt.subplots(figsize=(7.5,4.6),layout='constrained');s=F(1,2);corners=[]
    for aa in ['lower','upper']:
        for bb in ['lower','upper']:corners.append([float(p) for p in probability_row(s,F(cert['confidence']['a'][aa]),F(cert['confidence']['b'][bb]))])
    vals=np.array(corners);mid=np.array([float(p) for p in probability_row(s,a,b)]);lo=vals.min(axis=0);hi=vals.max(axis=0)
    ax.errorbar([float(x) for x in NODES],mid,yerr=[mid-lo,hi-mid],capsize=6,marker='o',linestyle='none',label='Certified range and fitted center')
    ax.plot([float(x) for x in NODES],[rho*float(w) for w in WEIGHTS],linestyle=':',marker='.',label='Common minorization mass')
    ax.set(xlabel='Next observed value',ylabel='Probability mass at the node',title='Certified predictions after last observation 1/2',ylim=(0,.5))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16));ax.grid(alpha=.2)
    save(fig,'46_conditional_probabilities',{'type':'exact extrema of an affine parameter rectangle evaluated numerically for drawing','reference_measure':'five-node; not continuous densities','preceding_signal':'1/2','lower':lo.tolist(),'upper':hi.tolist(),'fitted':mid.tolist()})
    (ROOT/'verification/data_figure_sources.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print('Generated six separate figure sets (PDF, PNG and SVG).')
if __name__=='__main__':main()
