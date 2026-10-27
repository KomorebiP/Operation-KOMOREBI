"""Seven separate mathematical figures. Uses Matplotlib default colors.

Analytic curves and explicit matrix calculations are illustrations, not measured
model performance. No subplots or external image assets are used.
"""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'

def main():
    OUT.mkdir(exist_ok=True)
    ledger={}
    def save(fig,name,source):
        for ext in ['pdf','png','svg']:
            fig.savefig(OUT/f'{name}.{ext}',dpi=175,bbox_inches='tight')
        plt.close(fig);ledger[name]=source
    def axes(title,xlabel,ylabel):
        fig,ax=plt.subplots(figsize=(7.2,4.25),layout='constrained')
        ax.set(title=title,xlabel=xlabel,ylabel=ylabel)
        ax.grid(True,alpha=.22)
        return fig,ax
    # 21: genuine three-dimensional cone, with no invented simulation results.
    fig=plt.figure(figsize=(8.0,6.1))
    ax=fig.add_subplot(111,projection='3d')
    ax.set_position([.065,.21,.79,.71])
    theta=np.linspace(0,2*np.pi,65);mass=np.linspace(0,1,11)
    X=np.outer(mass,np.cos(theta));Y=np.outer(mass,np.sin(theta));M=np.outer(mass,np.ones_like(theta))
    ax.plot_wireframe(X,Y,M,rstride=2,cstride=4,linewidth=.65)
    ax.plot(np.cos(theta),np.sin(theta),np.ones_like(theta),linewidth=1.8,label='Trace-one boundary')
    ax.scatter([0,12/13,-312/413],[0,0,-240/413],[1,1,1],s=36,label='Verified conditional states')
    ax.set(xlabel='x',ylabel='y',zlabel='')
    ax.set_xticks(np.linspace(-1,1,5));ax.set_yticks(np.linspace(-1,1,5))
    ax.set_zticks(np.linspace(0,1,6))
    fig.suptitle('A curved domain with one matrix inequality',y=.98)
    fig.text(.88,.57,'Mass m',rotation=90,va='center')
    ax.set_box_aspect((1,1,.9));ax.view_init(elev=24,azim=-55)
    handles,labels=ax.get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.47,.02),frameon=False)
    save(fig,'21_matrix_probability_cone',{'formula':'m >= sqrt(x^2+y^2); J(z) positive semidefinite','type':'analytic geometry'})
    # 22: densities relative to du/2, not probabilities of points.
    u=np.linspace(-1,1,501)
    fig,ax=axes('Continuous observation densities','Observation u','Density relative to du/2')
    for x in [-1,0,1]:
        ax.plot(u,(1+9*u*u+6*u*x)/4,label=f'Initial x = {x}',linewidth=1.7)
    ax.legend(loc='upper center',ncol=3,frameon=False)
    save(fig,'22_continuous_densities',{'formula':'p(u|x)=(1+9u^2+6ux)/4','initial_x':[-1,0,1],'type':'analytic curves'})
    # 23: exact rational conditional curves within the disk.
    fig,ax=axes('Conditioning stays inside the certified disk','Conditional x','Conditional y')
    ax.plot(np.cos(theta),np.sin(theta),'--',label='Domain boundary',linewidth=1)
    x0,y0=1/3,1/4
    for label,x,y in [('Direct action',x0,y0),('Rotated action',(3*x0-4*y0)/5,(4*x0+3*y0)/5)]:
        a=(1+9*u*u)/4;b=3*u/2;c=(1-9*u*u)/4;p=a+b*x
        ax.plot((b+a*x)/p,c*y/p,label=label,linewidth=1.8)
    ax.scatter([x0],[y0],s=30,label='Common initial state')
    ax.set_aspect('equal');ax.set_xlim(-1.1,1.1);ax.set_ylim(-1.1,1.1)
    ax.legend(loc='center left',bbox_to_anchor=(1.01,.5),frameon=False)
    save(fig,'23_conditional_state_curves',{'formula':'x+=(b+ax)/(a+bx), y+=cy/(a+bx)','initial':['1/3','1/4'],'type':'analytic curves sampled for rendering'})
    # 24: numerical condition numbers illustrate representation conditioning only.
    D=np.arange(0,13)
    cond=[]
    for d in D:
        W=np.array([[0 if (i+j)%2 else 1/(i+j+1) for j in range(d+1)] for i in range(d+1)])
        cond.append(float(np.linalg.cond(W)))
    fig,ax=axes('The observation basis has a conditioning cost','Maximum polynomial degree','2-norm Gram condition number')
    ax.semilogy(D,cond,'o-',label='Monomial basis')
    ax.semilogy(D,np.ones(len(D)),'--',label='Orthonormal Legendre basis')
    ax.legend(frameon=False)
    save(fig,'24_moment_conditioning',{'degrees':D.tolist(),'monomial_condition_numbers':cond,'orthonormal_gram':'identity','type':'float64 matrix illustration; not a sampling experiment'})
    # 25: exact counterexample family.
    eps=3/4;P3=(5*u**3-3*u)/2
    fig,ax=axes('Identical low moments, different valid densities','Observation u','Density relative to du/2')
    ax.plot(u,1+eps*P3,label='1 + (3/4) L3(u)',linewidth=1.8)
    ax.plot(u,1-eps*P3,label='1 - (3/4) L3(u)',linewidth=1.8)
    ax.legend(frameon=False)
    save(fig,'25_unseen_density_component',{'epsilon':'3/4','TV_exact':'39/160','same_moments':[0,1,2],'type':'analytic counterexample'})
    # 26: exact normalization defect of midpoint replacement.
    n=np.arange(1,17)
    fig,ax=axes('The covariance term restores the missing mass','Number of equal observation bins','Total assigned probability mass')
    ax.plot(n,1-3/(4*n*n),'o-',label='Midpoint congruence only')
    ax.plot(n,np.ones(len(n)),'--',label='Exact integrated instrument')
    ax.set_ylim(.18,1.07);ax.legend(frameon=False,loc='lower right')
    save(fig,'26_binning_mass_defect',{'formula':'naive mass=1-3/(4n^2)','bins':n.tolist(),'type':'exact formula plotted in floating point'})
    # 27: actual example's exact algebraic TV values and proved upper bound.
    data=json.loads((ROOT/'verification/curved_continuous_checks.json').read_text())['density_smoothing']
    n=[r['n'] for r in data];tv=[r['total_variation'] for r in data];upper=[r['certified_upper_bound'] for r in data]
    fig,ax=axes('Cell-average approximation has an explicit error budget','Number of equal observation bins','One-step total variation')
    ax.loglog(n,tv,'o-',label='Exact example value')
    ax.loglog(n,upper,'s--',label='Sufficient bound min(1, 2/n)')
    ax.legend(frameon=False)
    save(fig,'27_density_resolution_bound',{'exact_data':data,'type':'exact values from symbolic report; plotted numerically'})
    (ROOT/'verification/continuous_figure_sources.json').write_text(json.dumps(ledger,indent=2)+'\n')
    print('Generated seven separate figure sets (PDF, PNG and SVG).')
if __name__=='__main__':main()
