"""Six separate figures. Diagnostics and exact certificates are labeled distinctly."""
from pathlib import Path
import sys,json
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import U,mat,poly_matrices


def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    c=json.loads((ROOT/'certificates/robust_curved_certificate.json').read_text())
    data=json.loads((ROOT/'examples/noisy_operator_inputs.json').read_text())
    T=mat(c['transform_to_lorentz']);Ti=T.inv()
    old={k:poly_matrices(v) for k,v in data['actions'].items()}
    fixed={k:poly_matrices(v) for k,v in c['actions'].items()}
    theta=np.linspace(0,2*np.pi,721)
    points=np.vstack([np.ones(theta.size),np.cos(theta),np.sin(theta)])
    ledger={}
    def save(fig,name,entry):
        fig.savefig(out/(name+'.pdf'),bbox_inches='tight')
        fig.savefig(out/(name+'.png'),dpi=165,bbox_inches='tight')
        fig.savefig(out/(name+'.svg'),bbox_inches='tight')
        plt.close(fig);ledger[name]=entry
    fig,ax=plt.subplots(figsize=(7.7,4.1))
    values={}
    for label,B in [('Raw perturbed fit',old['direct']),('After the declared repair',fixed['direct'])]:
        F=np.array((T*B*Ti).subs(U,-1),dtype=float);w=F@points
        rad=np.sqrt(w[1]**2+w[2]**2)/w[0];values[label]=rad.tolist()
        ax.plot(theta/np.pi,rad,label=label)
    ax.axhline(1,linestyle='--',label='Admissible boundary')
    ax.set(xlabel='Boundary input angle / pi',ylabel='Normalized output radius',title='The raw fit leaves the probability domain')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.19),ncol=1,fontsize=9)
    fig.tight_layout();save(fig,'34_raw_and_repaired',{'kind':'sampled diagnostic, not the proof','u':-1,'angles':theta.tolist(),'series':values})
    us=np.linspace(-1,1,301);vals={}
    for label,B in [('Raw fit (sampled minimum)',old['direct']),('Repaired (sampled minimum)',fixed['direct'])]:
        fn=sp.lambdify(U,T*B*Ti,'numpy');y=[]
        for u in us:
            w=np.array(fn(u),dtype=float)@points;y.append(float(np.min(w[0]-np.sqrt(w[1]**2+w[2]**2))))
        vals[label]=y
    fig,ax=plt.subplots(figsize=(7.7,4.2))
    for label,y in vals.items():ax.plot(us,y,label=label)
    ax.axhline(1/16,linestyle='--',label='Exact certified lower bound: 1/16')
    ax.axhline(1/64,linestyle=':',label='Combined uncertainty budget: 1/64')
    ax.set(xlabel='Continuous observation u',ylabel='Mass minus spatial norm',title='A positive margin can cover uncertainty')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.19),ncol=1,fontsize=9)
    fig.tight_layout();save(fig,'35_uniform_margin',{'kind':'sampled curves with exact certificate thresholds','observations':us.tolist(),'series':vals,'certified_margin':'1/16','uncertainty_budget':'1/64'})
    def rect(path):
        a,b,c,d=-1.,1.,-1.,1.
        for ch in path:
            um=(a+b)/2;tm=(c+d)/2
            if ch in '01':b=um
            else:a=um
            if ch in '02':d=tm
            else:c=tm
        return a,b,c,d
    leaves=c['proofs']['direct']['1']['cone_gap']
    fig,ax=plt.subplots(figsize=(7.0,5.0))
    for leaf in leaves:
        a,b,lo,hi=rect(leaf['path']);ax.add_patch(Rectangle((a,lo),b-a,hi-lo,fill=False,linewidth=.7))
    ax.set(xlim=(-1,1),ylim=(-1,1),xlabel='Observation u',ylabel='Rational semicircle parameter t',title='One exact polynomial certificate covers the whole square')
    ax.set_aspect('equal');fig.tight_layout()
    save(fig,'36_exact_subdivision',{'kind':'exact proof partition, direct action positive chart cone polynomial','leaves':leaves})
    fig=plt.figure(figsize=(7.7,5.4));ax=fig.add_subplot(111,projection='3d')
    mass=np.linspace(.08,1,13);ang=np.linspace(0,2*np.pi,81)
    ms,th=np.meshgrid(mass,ang,indexing='ij');pts=np.vstack([ms.ravel(),(ms*np.cos(th)).ravel(),(ms*np.sin(th)).ravel()])
    pred=np.array(Ti,dtype=float)@pts;xx=pred[1].reshape(ms.shape);yy=pred[2].reshape(ms.shape)
    ax.plot_wireframe(xx,yy,ms,rstride=2,cstride=6,linewidth=.65)
    ax.set_xlabel('q1',labelpad=4);ax.set_ylabel('q2',labelpad=4);ax.set_zlabel('');ax.text2D(.88,.57,'Mass',transform=ax.transAxes,rotation=90)
    ax.set_title('The proposed curved probability cone',pad=18);ax.view_init(elev=24,azim=-55)
    ax.set_box_aspect((1,1,1));fig.subplots_adjust(left=.08,right=.88,bottom=.12,top=.9)
    save(fig,'37_discovered_cone',{'kind':'geometry rendered from the exact accepted transform','transform':c['transform_to_lorentz']})
    et=np.linspace(0,.4,241);d0=.02;nu=np.maximum(0,et-(1-et)*d0)
    fig,ax=plt.subplots(figsize=(7.7,4.2))
    ax.plot(et,nu,label='Combined perturbation budget available')
    ax.plot(et,(1-et)*d0+2*et,label='Conservative instrument-error budget')
    ax.set(xlabel='Reset mixture weight eta',ylabel='Declared bound',title='More robustness has a prediction cost')
    ax.legend(loc='upper left',fontsize=9);fig.tight_layout()
    save(fig,'38_repair_tradeoff',{'kind':'theoretical illustration, not fitted data','assumed_raw_budget':d0,'reset_density_minimum':1,'eta':et.tolist(),'available_budget':nu.tolist(),'error_budget':((1-et)*d0+2*et).tolist()})
    comp=json.loads((ROOT/'verification/robust_comparison.json').read_text());slope=float(sp.Rational(comp['total_instrument_error_bound'])/2)
    t=np.arange(0,13);bound=np.minimum(1,t*slope)
    fig,ax=plt.subplots(figsize=(7.7,4.0));ax.plot(t,bound,marker='o',label='Proved upper bound, not measured TV')
    ax.axhline(1,linestyle='--',label='Trivial bound')
    ax.set(xlabel='Prediction horizon',ylabel='Total-variation upper bound',title='The worked error certificate becomes vacuous at eight steps',ylim=(0,1.06),xticks=np.arange(0,13,2))
    ax.legend(loc='lower right',fontsize=9);fig.tight_layout()
    save(fig,'39_finite_horizon_limit',{'kind':'exact bound evaluated for plotting','instrument_budget':comp['total_instrument_error_bound'],'horizons':t.tolist(),'values':bound.tolist()})
    (ROOT/'verification/robust_figure_data.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print('Generated six separate PDF, PNG and SVG figure sets.')

if __name__=='__main__':main()
