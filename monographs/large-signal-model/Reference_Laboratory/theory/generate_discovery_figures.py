"""Generate six separate Matplotlib figures from exact examples and one seeded path.

Uses Matplotlib default colors, no subplots, no generated images. Numeric values
used for plotting are exported with their mathematical or sampling provenance.
"""
from pathlib import Path
import json,sys
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import binom
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from continuous_reference import load_json
from quadratic_reference import verify_quadratic
from sequential_reference import V, positive_coefficients, dependent_example, anytime_radius


def main():
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    ledger={}
    def save(fig,stem,source,data):
        for ext in ['pdf','png','svg']:fig.savefig(out/f'{stem}.{ext}',dpi=170,bbox_inches='tight')
        plt.close(fig);ledger[stem]={'source':source,'data':data}
    obj=verify_quadratic(load_json(ROOT/'certificates/discovered_quadratic_certificate.json'))
    H=np.array(obj.metric,float);c=np.array(obj.center,float).ravel();eig,U=np.linalg.eigh(H)
    t=np.linspace(0,2*np.pi,501);pts=c[:,None]+(U@np.diag(1/np.sqrt(eig)))@np.vstack([np.cos(t),np.sin(t)])
    fig,ax=plt.subplots(figsize=(7.0,4.8),layout='constrained')
    ax.plot(*pts,label='Discovered boundary');ax.plot(*c,'o',label='Initial predictive state')
    z=obj.initial;path=[np.array(z[1:,0],float).ravel().tolist()]
    for i,obs in enumerate([sp.Rational(1,2),-sp.Rational(1,2),sp.Rational(2,3),sp.Rational(1,4),-sp.Rational(3,4)]):
        _,z=obj.condition_at('direct' if i%2==0 else 'rotated',obs,z);path.append(np.array(z[1:,0],float).ravel().tolist())
    arr=np.array(path);ax.plot(arr[:,0],arr[:,1],'-o',markersize=4,label='Declared observation sequence')
    ax.set(xlabel='$q_1$',ylabel='$q_2$',title='Recovered geometry in predictive coordinates',xlim=(0,1),ylim=(0,1));ax.set_aspect('equal')
    ax.legend(loc='upper left',bbox_to_anchor=(1.02,1),fontsize=9)
    save(fig,'28_discovered_geometry','Exact rational certificate, evaluated numerically for display.',{'center':c.tolist(),'metric':H.tolist(),'sequence':path})
    u=np.linspace(-1,1,501);tau=(1-9*u*u)**2/16;beta=(1+9*u*u)/4
    fig,ax=plt.subplots(figsize=(7.0,4.3),layout='constrained')
    ax.plot(u,beta,label=r'Mass orientation $\beta(u)$');ax.plot(u,tau,label=r'Quadratic factor $\tau(u)$')
    ax.axhline(0,linestyle=':',linewidth=1);ax.set(xlabel='Observation value $u$',ylabel='Certificate quantity',title='The certificate is an identity over the whole interval')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2,fontsize=9)
    save(fig,'29_polynomial_witness','Analytic polynomials from the independent certificate.',{'u':u.tolist(),'beta':beta.tolist(),'tau':tau.tolist()})
    x=np.linspace(0,1,1001);p=.5+2*np.abs(x-.5);curves={}
    fig,ax=plt.subplots(figsize=(7.0,4.3),layout='constrained')
    ax.plot(x,p,linewidth=2,label='Nonpolynomial density')
    pieces=[(sp.Integer(0),sp.Rational(1,2),sp.Rational(3,2)-2*V),(sp.Rational(1,2),sp.Integer(1),2*V-sp.Rational(1,2))]
    for n in [0,2,8]:
        co=positive_coefficients(None,n,split=pieces)
        values=sum(float(v)*binom.pmf(k,n,x) for k,v in enumerate(co));curves[str(n)]={'coefficients':[str(v) for v in co],'values':values.tolist()}
        ax.plot(x,values,label=f'Positive degree {n}')
    ax.set(xlabel='Observation $x$',ylabel='Density relative to $dx$',title='Positive polynomial approximation without a true-degree assumption')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2,fontsize=9)
    save(fig,'30_positive_approximation','Exact rational integral coefficients of a piecewise-linear density.',{'x':x.tolist(),'true_density':p.tolist(),'approximations':curves})
    fig,ax=plt.subplots(figsize=(7.0,4.3),layout='constrained')
    ax.plot(x,3*x*x,label='Valid density $3x^2$');ax.plot(x,3*x-.5,label='$L^2$ degree-one projection');ax.plot(x,x+.5,label='Positive degree-one average')
    ax.axhline(0,linestyle=':',linewidth=1);ax.set(xlabel='Observation $x$',ylabel='Density',title='Ordinary truncation can leave the probability domain')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=1,fontsize=9)
    save(fig,'31_projection_negative','Exact analytic functions. Negative values are the deliberate counterexample.',{'x':x.tolist(),'original':(3*x*x).tolist(),'orthogonal_projection':(3*x-.5).tolist(),'positive_approximation':(x+.5).tolist()})
    path=dependent_example();rows=np.array(path['rows']);sel=rows[:,0]>=64;rows=rows[sel];n=rows[:,0]
    fig,ax=plt.subplots(figsize=(7.2,4.5),layout='constrained')
    ax.plot(n,rows[:,4]/n,label='Ungated residual');ax.plot(n,rows[:,5]/n,label='History-gated residual');ax.plot(n,rows[:,6]/n,label='Correct gated predictor')
    ax.plot(n,rows[:,9]/n,linestyle='--',label='Registered boundary');ax.plot(n,-rows[:,9]/n,linestyle='--')
    ax.set(xlabel='Observed transitions',ylabel='Accumulated residual / transitions',title='Conditional evidence under a dependent binary signal')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=2,fontsize=9)
    save(fig,'32_dependent_evidence','One prospectively specified synthetic Markov path. Not a coverage-rate experiment.',{'seed':path['seed'],'n':path['n'],'summary':path['summary']})
    n=np.unique(np.geomspace(20,200000,250).astype(int));widths={}
    fig,ax=plt.subplots(figsize=(7.0,4.3),layout='constrained')
    for pi in [1,.5,.25,.1]:
        y=np.array([anytime_radius(int(t),.05,value_range=1/pi)/t for t in n]);widths[str(pi)]=y.tolist();ax.loglog(n,y,label=f'Minimum action probability {pi:g}')
    ax.axhline(.1,linestyle=':',linewidth=1)
    ax.set(xlabel='Observed contexts',ylabel='Sufficient average-mean half-width',title='Action coverage has an explicit statistical cost')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,fontsize=8.5)
    save(fig,'33_coverage_cost','Analytic sufficient confidence boundaries for separate coverage scenarios; not sample measurements.',{'n':n.tolist(),'delta':.05,'widths':widths})
    (ROOT/'verification/discovery_figure_data.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print('Generated six separate PDF, PNG and SVG figure sets with a source-data ledger.')
if __name__=='__main__':main()
