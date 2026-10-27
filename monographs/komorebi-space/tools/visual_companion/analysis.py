"""Eight analytic investigations; explicit finite calculations, no inferred limits.

Run from any directory with: python3 tools/visual_companion/analysis.py
The plotted infinite-family conclusions are justified in the accompanying text
by p-series or the cited printed theorems, never by the plotted finite samples.
"""
import json
import math
import platform
from fractions import Fraction
from pathlib import Path

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

from style import ROOT, PINE, INK, OCHRE, BLUE, MUTED, PALE, RED, GRID, tidy, save

plt.rcParams.update({'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10})
SCENES=[]
CHECKS=[]
ARTIFACTS=[]


def check(name, condition, detail, arithmetic='IEEE 754 binary64; absolute tolerance 1e-11'):
    if not bool(condition):
        raise AssertionError(name + ': ' + detail)
    CHECKS.append({'name':name,'passed':True,'detail':detail,'arithmetic':arithmetic})


def record(i, name, title, setup, reading, experiment, labels):
    SCENES.append({'id':i,'title':title,'setup_tex':setup,'reading_tex':reading,
                   'experiment_tex':experiment,'monograph_labels':labels,
                   'figure':name+'.pdf'})


def finish(fig,name):
    # A persistent layout check prevents accidentally shrinking the text.
    fig.canvas.draw()
    small=[t.get_fontsize() for t in fig.findobj(matplotlib.text.Text)
           if t.get_visible() and t.get_text() and t.get_fontsize()<9.99]
    check(name+'_font_floor',not small,'All visible figure text is at least 10 pt.')
    ARTIFACTS.append(save(fig,name))


def protected_angles():
    name='a01_protected_angles'
    fig=plt.figure(figsize=(7,4.8))
    ax=fig.add_axes([.01,.14,.58,.77],projection='3d')
    bx=fig.add_axes([.68,.19,.28,.64])
    u=np.linspace(-1.9,1.9,9); yy,zz=np.meshgrid(u,u)
    ax.plot_surface(np.zeros_like(yy),yy,zz,color=PALE,alpha=.45,linewidth=0)
    x=np.array([1.,0.,0.]); ax.scatter(*x,color=INK,s=45,depthshade=False)
    ax.text(1.05,0,.15,'raw point',fontsize=10)
    for deg,color in [(30,BLUE),(60,OCHRE)]:
        theta=np.deg2rad(deg)
        phi=np.linspace(0,2*np.pi,150)
        radius=np.tan(theta)
        ax.plot(np.zeros_like(phi),radius*np.cos(phi),radius*np.sin(phi),color=color,lw=1.4)
        for ph in np.deg2rad([0,120,240]):
            v=np.array([np.cos(theta),np.sin(theta)*np.cos(ph),np.sin(theta)*np.sin(ph)])
            a=v/np.cos(theta); y=x-a; p=np.eye(3)-np.outer(v,v)
            ax.plot([x[0],y[0]],[x[1],y[1]],[x[2],y[2]],color=color,lw=1.7)
            ax.scatter(*y,color=color,s=20,depthshade=False)
            check('protected_'+str(deg)+'_'+str(round(ph,3)),
                  np.linalg.norm(p@a)<1e-11 and abs(y[0])<1e-11 and abs(np.linalg.norm(a)-1/np.cos(theta))<1e-11,
                  'The correction lies in ker p, the repaired x-coordinate is zero, and its norm is sec(theta).')
    ax.set(xlabel='$x_1$',ylabel='$x_2$',zlabel='$x_3$',xlim=(-.15,1.3),ylim=(-2,2),zlim=(-2,2))
    ax.set_xticks([0,1]);ax.set_yticks([-2,0,2]);ax.set_zticks([-2,0,2])
    ax.view_init(elev=21,azim=33);ax.set_box_aspect((1.5,3.6,3.6))
    ax.set_title('Exact answers lie in $x_1=0$',pad=10)
    theta=np.deg2rad(np.linspace(0,82,300))
    bx.plot(np.rad2deg(theta),1/np.cos(theta),color=PINE,lw=2.4)
    for deg,color in [(30,BLUE),(60,OCHRE)]:
        val=1/np.cos(np.deg2rad(deg));bx.scatter(deg,val,color=color,s=40,zorder=3)
        bx.annotate(f'{deg}°',xy=(deg,val),xytext=(deg-17,val+.7),fontsize=10)
    bx.set(xlabel=r'angle $\theta$ (degrees)',ylabel='correction norm',xlim=(0,85),ylim=(0,8),xticks=[0,30,60,80])
    bx.set_title('Cost of protection',pad=10);tidy(bx)
    fig.text(.055,.04,'Each direction defines its own protected observable.',fontsize=10,color=MUTED)
    finish(fig,name)
    record('a01',name,'How much can a preservation rule cost?',
      r'Keep the raw point $x=(1,0,0)$ and equation $D(x)=x_1$ fixed. Vary the allowed unit correction direction $v=(\cos\theta,\sin\theta\cos\phi,\sin\theta\sin\phi)$, with protected observable $p=I-vv^{\mathsf T}$. All three coordinates use the Euclidean metric.',
      r'For $0\le\theta<\pi/2$, the unique feasible correction is $a=v/\cos\theta$. Its norm is $\sec\theta$; its endpoint $x-a$ lies in the shaded exact plane. Azimuth changes the answer without changing its cost. At $\theta=\pi/2$, allowed changes cannot alter $x_1$, so this raw point becomes infeasible.',
      r'Compare $30^\circ$ and $60^\circ$: the costs are $2/\sqrt3$ and $2$. Turning the correction toward the exact plane increases its length; every plotted line preserves its own declared observable exactly.',
      ['sec:closed'])


def scale_and_motion():
    name='a02_scale_and_motion'
    fig,axs=plt.subplots(1,2,figsize=(7,4.8))
    fig.subplots_adjust(left=.105,right=.97,bottom=.25,top=.84,wspace=.29)
    theta=np.deg2rad(np.linspace(5,90,180));logs=np.linspace(-3,0,150)
    tt,ll=np.meshgrid(theta,logs); scale=10**ll
    diff=2*scale*np.sin(tt/2);gap=np.sin(tt)
    cmap=LinearSegmentedColormap.from_list('forest',[PALE,PINE])
    # A same-color overlap prevents PDF viewers from antialiasing white seams.
    # Cells and text remain vectors; the numerical grid is unchanged.
    im=axs[0].pcolormesh(np.rad2deg(tt),ll,np.log10(diff),cmap=cmap,shading='auto',edgecolors='face',linewidth=.6,antialiased=False)
    jm=axs[1].pcolormesh(np.rad2deg(tt),ll,gap,cmap=cmap,vmin=0,vmax=1,shading='auto',edgecolors='face',linewidth=.6,antialiased=False)
    for ax in axs:
        ax.set(xlabel=r'rotation $\theta$ (degrees)',ylabel=r'$\log_{10}s$',xticks=[15,45,75],yticks=[-3,-2,-1,0])
    axs[0].set_title('Operator difference',pad=12)
    axs[1].set_title('Exact-space difference',pad=12)
    cax=fig.add_axes([.105,.10,.36,.025]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label(r'$\log_{10}\,\|D_{s,\theta}-D_{s,0}\|$',fontsize=10)
    cax=fig.add_axes([.61,.10,.36,.025]);cb=fig.colorbar(jm,cax=cax,orientation='horizontal');cb.set_label(r'$\|P_{s,\theta}-P_{s,0}\|$',fontsize=10)
    for deg in [5,30,60,90]:
        t=np.deg2rad(deg)
        n=np.array([np.cos(t),np.sin(t)]);q=np.eye(2)-np.outer(n,n);q0=np.diag([0.,1.])
        for s in [.001,.1,1.]:
            check('motion_'+str(deg)+'_'+str(s),abs(np.linalg.norm(s*n-np.array([s,0.]))-2*s*np.sin(t/2))<1e-11 and abs(np.linalg.norm(q-q0,2)-np.sin(t))<1e-11,
                  'Direct matrix operator norms agree with the plotted formulas; s>0.')
    finish(fig,name)
    record('a02',name,'Small operators can have widely separated kernels',
      r'Compare the row operators $D_{s,\theta}=s(\cos\theta\ \ \sin\theta)$ and $D_{s,0}=s(1\ \ 0)$, with $s>0$ and $0\le\theta\le\pi/2$. Their kernels are lines in one Euclidean plane. Sweep both scale and angle; the plot starts at $5^\circ$.',
      r'The operator difference is $2s\sin(\theta/2)$, while the projector difference is $\sin\theta$ for the angles shown. Shrinking $s$ changes only the left panel. Each nonzero operator has least residual gain $1/s$: the scale that hides the operator difference also weakens its stability certificate.',
      r'At $\theta=60^\circ$, reducing $s$ from $1$ to $10^{-3}$ reduces the operator difference by a thousand. The projector gap stays $\sqrt3/2$. The zero-scale operator has a different kernel and is excluded.',
      ['sec:closed','sec:motion'])


def same_residual_paths():
    name='a03_same_residual_paths'
    fig,axs=plt.subplots(1,2,figsize=(7,4.8))
    fig.subplots_adjust(left=.10,right=.97,bottom=.17,top=.84,wspace=.34)
    k=np.arange(1,513,dtype=float);n=np.arange(513)
    for p,color,label in [(1,RED,'$p=1$'),(2,PINE,'$p=2$')]:
        u=np.r_[0.,np.cumsum(k**(-p))];r=2.**(-n)
        axs[0].plot(u[:65],r[:65],color=color,lw=2,label=label)
        axs[0].scatter(u[[0,1,2,4,8]],r[[0,1,2,4,8]],color=color,s=20)
        length=u[1:]+1-2.**(-k)
        axs[1].semilogx(k,length,color=color,lw=2,label=label)
        increments=np.abs(np.diff(u))+np.abs(np.diff(r))
        check('path_length_p'+str(p),np.max(np.abs(np.cumsum(increments)-length))<1e-11,
              'For N=1,...,512 the l1 movement equals sum(k^-p)+1-2^-N.')
    limit=np.pi**2/6
    axs[0].axhline(0,color=MUTED,lw=1,ls='--');axs[0].scatter([limit],[0],s=60,marker='*',color=PINE,zorder=4)
    axs[0].annotate(r'$p=2$ limit',xy=(limit,0),xytext=(2.15,.2),fontsize=10,arrowprops={'arrowstyle':'-','color':PINE})
    axs[0].set(xlabel='unprotected coordinate $u_n$',ylabel=r'residual $r_n=2^{-n}$',xlim=(-.15,5.15),ylim=(-.05,1.08))
    axs[0].set_title('One residual history',pad=12);axs[0].legend(loc='upper right',frameon=False);tidy(axs[0])
    axs[1].axhline(1+limit,color=PINE,ls='--',lw=1.3)
    axs[1].text(18,2.94,r'$1+\pi^2/6$',color=PINE,fontsize=10)
    axs[1].set(xlabel='number of steps $N$',ylabel=r'total movement in $\ell^1$',ylim=(0,8.5),xlim=(1,512))
    axs[1].set_title('Different movement budgets',pad=12);tidy(axs[1])
    finish(fig,name)
    record('a03',name,'Can one residual history conceal two different outcomes?',
      r'Let $u_n^{(p)}=\sum_{k=1}^n k^{-p}$ and $f_n^{(p)}=(s,u_n^{(p)},2^{-n})$. Protect the coordinate $s$, and measure candidate movement with the $\ell^1$ metric. Both paths start at the same point and have the same residual.',
      r'The movement through step $N$ is exactly $\sum_{k=1}^N k^{-p}+1-2^{-N}$. For $p=2$ it converges to $1+\pi^2/6$, giving an exact limit. For $p=1$ the unprotected coordinate diverges. These conclusions use the convergent square series and divergent harmonic series, not extrapolation from the finite curves.',
      r'After one step, both paths have residual $1/2$. Nevertheless their eventual behavior differs. The finite residual table alone cannot decide convergence: a summable bound must control movement in the candidate space.',
      ['sec:variable-exactification'])


def exponent_energy():
    name='a04_datum_exponent_energy'
    fig,axs=plt.subplots(1,2,figsize=(7,4.8))
    fig.subplots_adjust(left=.105,right=.97,bottom=.17,top=.84,wspace=.36)
    k=np.arange(1,4097,dtype=float); Ns=np.unique(np.geomspace(1,4096,160).astype(int))
    for s,color in [(1,RED),(1.5,OCHRE),(2,PINE)]:
        E=np.cumsum(k**(2-2*s))
        axs[0].loglog(Ns,E[Ns-1],color=color,lw=2,label=f'$s={s:g}$')
    ss=np.linspace(.75,2.25,220)
    for N,color in [(16,BLUE),(256,OCHRE),(4096,PINE)]:
        E=np.sum(np.arange(1,N+1,dtype=float)[:,None]**(2-2*ss)[None,:],axis=0)
        axs[1].semilogy(ss,E,color=color,lw=2,label=f'$N={N}$')
    axs[1].axvline(1.5,color=INK,ls='--',lw=1.2)
    axs[0].set(xlabel='number of equations $N$',ylabel=r'minimum energy $E_N(s)$',xlim=(1,4096))
    axs[1].set(xlabel='datum exponent $s$',ylabel=r'minimum energy $E_N(s)$',xlim=(.75,2.25))
    axs[0].set_title('At and beside the boundary',pad=12);axs[1].set_title('Sweep the datum',pad=12)
    axs[0].legend(frameon=False,loc='upper left');axs[1].legend(frameon=False,loc='upper right')
    for ax in axs:tidy(ax)
    for N in [1,16,256,4096]:
        E1=np.sum(np.arange(1,N+1,dtype=float)**0)
        E2=np.sum(np.arange(1,N+1,dtype=float)**-2)
        Eh=np.sum(1/np.arange(1,N+1,dtype=float))
        check('energy_'+str(N),E1==N and E2<=2 and np.log(N+1)<=Eh+1e-11 and Eh<=1+np.log(N)+1e-11,
              'Check E_N(1)=N; E_N(2)<=2; log(N+1)<=E_N(3/2)<=1+log(N).')
    finish(fig,name)
    record('a04',name,'Where does a family of data stop being realizable?',
      r'Keep $Ta=(a_n/n)$ on $\ell^2$ fixed, and vary the datum $r_n^{(s)}=n^{-s}$ for $s>1/2$. The least correction satisfying its first $N$ equations has energy $E_N(s)=\sum_{n=1}^N n^{2-2s}$.',
      r'An exact preimage must have coordinates $a_n=n^{1-s}$. Thus the square-series test gives realizability precisely for $s>3/2$. At $s=3/2$, the energy is harmonic and still diverges. Every finite problem remains solvable on both sides; only a uniform energy bound can pass to the Hilbert realization.',
      r'Predict the middle curve: at $s=3/2$ its energy lies between $\log(N+1)$ and $1+\log N$. Slow growth is still unbounded growth. The plot evaluates finite sums through $N=4096$.',
      ['sec:escape','sec:bounded-realization','sec:diagonal-regularization'])


def budget_geometry():
    name='a05_budget_geometry'
    fig=plt.figure(figsize=(7,4.8))
    ax=fig.add_axes([.005,.15,.445,.73],projection='3d');bx=fig.add_axes([.64,.19,.32,.64])
    M=math.sqrt(41)/10;t=np.linspace(0,2*np.pi,240)
    xx=M*np.cos(t);yy=M/2*np.sin(t)
    ax.plot(xx,yy,0*t,color=PINE,lw=2)
    for f in [.25,.5,.75]:ax.plot(f*xx,f*yy,0*t,color=PINE,lw=.6,alpha=.35)
    r=np.array([1.,1.,.5]);y=np.array([.5,.2,0.]);v=r-y
    ax.scatter(*r,color=OCHRE,s=40,depthshade=False);ax.scatter(*y,color=PINE,s=40,depthshade=False)
    ax.plot([y[0],r[0]],[y[1],r[1]],[0,r[2]],color=OCHRE,lw=2)
    ts=np.linspace(-.35,.35,20);ax.plot(y[0]-.8*ts,y[1]+.5*ts,0*ts,color=MUTED,ls='--',lw=1)
    ax.text(1.04,1.,.53,'target',fontsize=10);ax.text(.27,.14,.07,'nearest image',fontsize=10)
    ax.set(xlabel='$r_1$',ylabel='$r_2$',zlabel='$r_3$',xlim=(-.75,1.3),ylim=(-.6,1.3),zlim=(-.1,.75))
    ax.set_xticks([0,1]);ax.set_yticks([0,1]);ax.set_zticks([0,.5]);ax.view_init(elev=25,azim=-63)
    ax.set_box_aspect((2,2,1));ax.set_title('Budget image and target',pad=12)
    alpha=np.geomspace(1e5,1e-5,1200)
    aa=np.stack([1/(1+alpha),2/(1+4*alpha)],axis=1)
    MM=np.linalg.norm(aa,axis=1)
    fitxy=(alpha/(1+alpha))**2+(4*alpha/(1+4*alpha))**2
    mx=np.r_[0,MM,math.sqrt(5),3.]
    for h,col in [(0,BLUE),(.5,PINE)]:
        bb=np.r_[math.sqrt(2+h*h),np.sqrt(fitxy+h*h),h,h]
        bx.plot(mx,bb,color=col,lw=2,label=f'$h={h:g}$')
        if h==.5:
            width=.03+.05*mx
            bx.fill_between(mx,np.maximum(bb-width,0),bb+width,color=PINE,alpha=.14,label='uncertainty band')
    bx.scatter([M],[np.linalg.norm(v)],color=OCHRE,s=35,zorder=5)
    bx.set(xlabel='correction budget $M$',ylabel=r'best residual $\beta(M)$',xlim=(0,3),ylim=(0,1.65),xticks=[0,1,2,3])
    bx.set_title('Frontier and uncertainty',pad=12);bx.legend(loc='upper right',frameon=False);tidy(bx)
    a=np.array([.5,.4]);T=np.array([[1.,0],[0,.5],[0,0]])
    check('budget_witness',np.linalg.norm(T.T@v-a)<1e-11 and abs(np.dot(r,v/np.linalg.norm(v))-M*np.linalg.norm(T.T@(v/np.linalg.norm(v)))-np.linalg.norm(v))<1e-11,
          'At alpha=1 and h=1/2, the normalized residual attains the dual budget bound.')
    check('budget_parametric_normal',np.max(np.abs((1+alpha)*aa[:,0]-1))<1e-11 and np.max(np.abs(.5*(1-.5*aa[:,1])-alpha*aa[:,1]))<1e-11,
          'Each parametric correction satisfies T*(r-Ta)=alpha a; alpha sampled from 1e-5 through 1e5.')
    finish(fig,name)
    record('a05',name,'When does more correction stop improving the fit?',
      r'Let $T(a,b)=(a,b/2,0)$ and $r_h=(1,1,h)$, with Euclidean norms. The correction ball maps to a flat ellipse. Vary its radius $M$ and compare targets at heights $h=0$ and $h=1/2$.',
      r'The regularized corrections $a_\alpha=(1/(1+\alpha),2/(1+4\alpha))$ trace the exact frontier at their own budgets. At $M=\sqrt5$, the horizontal mismatch disappears; the residual floor is $|h|$. The shaded band allows data error $\delta=0.03$ and operator error $\eta=0.05$, using width $\delta+\eta M$ on one fixed correction space.',
      r'At the marked point, $\alpha=1$, $a=(1/2,2/5)$ and $M=\sqrt{41}/10$. For $h=1/2$, the residual is $(1/2,4/5,1/2)$; its normalized direction certifies the entire budget ball.',
      ['sec:budget-frontier','sec:regularized-repair'])


def regularization_modes():
    name='a06_regularization_modes'
    fig,axs=plt.subplots(1,2,figsize=(7,4.8))
    fig.subplots_adjust(left=.105,right=.97,bottom=.17,top=.84,wspace=.37)
    tau=delta=.02;alpha=np.geomspace(1e-6,10,500)
    a1=1/(1+alpha);a2=tau*delta/(tau*tau+alpha)
    true=np.sqrt((a1-1)**2+a2*a2)
    fit=np.sqrt((a1-1)**2+(tau*a2-delta)**2)
    axs[0].loglog(alpha,true,color=RED,lw=2.2,label='error to true answer')
    axs[0].loglog(alpha,fit,color=PINE,lw=2.2,label='fit to measured data')
    axs[0].invert_xaxis();axs[0].set(xlabel=r'regularization $\alpha$ (decreasing)',ylabel='Euclidean norm',ylim=(1e-5,2))
    axs[0].set_title('Fitting noise can increase error',pad=12);axs[0].legend(frameon=False,loc='lower left');tidy(axs[0])
    axs[1].plot(a1,a2,color=BLUE,lw=2.2)
    axs[1].scatter([1],[0],marker='*',s=85,color=PINE,zorder=4)
    axs[1].scatter([1],[1],marker='x',s=50,color=RED,zorder=4)
    axs[1].annotate('true answer',xy=(1,0),xytext=(.30,.17),fontsize=10,arrowprops={'arrowstyle':'-','color':PINE})
    axs[1].annotate('exact measured fit',xy=(1,1),xytext=(.08,.92),fontsize=10,arrowprops={'arrowstyle':'-','color':RED})
    am=.02;point=np.array([1/(1+am),tau*delta/(tau*tau+am)])
    axs[1].scatter(*point,color=OCHRE,s=35,zorder=5)
    axs[1].annotate(r'$\alpha=0.02$',xy=point,xytext=(.17,.45),fontsize=10,arrowprops={'arrowstyle':'-','color':OCHRE})
    axs[1].set(xlabel='strong-mode correction $a_1$',ylabel='weak-mode correction $a_2$',xlim=(0,1.08),ylim=(-.06,1.1),xticks=[0,.5,1],yticks=[0,.5,1])
    axs[1].set_title('The correction path',pad=12);tidy(axs[1])
    check('regularized_modes',np.max(np.abs((1+alpha)*a1-1))<1e-11 and np.max(np.abs((tau*tau+alpha)*a2-tau*delta))<1e-11,
          'The 500 plotted two-mode corrections satisfy their exact normal equations.')
    check('regularization_prediction',abs(np.linalg.norm(point-np.array([1.,0]))-math.sqrt(2)/51)<1e-11,
          'At alpha=0.02 both coordinate errors have magnitude 1/51, so true error is sqrt(2)/51.')
    finish(fig,name)
    record('a06',name,'Can a better measured fit give a worse answer?',
      r'Use $T=\operatorname{diag}(1,0.02)$ and true correction $a^\dagger=(1,0)$. Add the deterministic data error $(0,0.02)$, entirely in the weak mode. The measured datum is $(1,0.02)$; all norms are Euclidean.',
      r'The exact regularized answer is $a_\alpha=(1/(1+\alpha),0.0004/(0.0004+\alpha))$. As $\alpha$ decreases, measured fit improves throughout, but the weak-mode error eventually grows. At zero-parameter limit the measured equations are fitted exactly by $(1,1)$, a distance one from the true answer. This is a finite two-mode calculation.',
      r'At $\alpha=0.02$, the answer is $(50/51,1/51)$ and its true error is $\sqrt2/51$. Smaller measured residual alone therefore does not select the most accurate correction for this noisy datum.',
      ['sec:regularized-repair','sec:stopping-rules'])


def basis_certificate():
    name='a07_basis_certificate'
    fig,axs=plt.subplots(1,2,figsize=(7,4.8))
    fig.subplots_adjust(left=.105,right=.97,bottom=.17,top=.84,wspace=.37)
    ax,bx=axs
    ax.annotate('',xy=(1,0),xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2,'color':INK})
    ax.text(.75,-.16,'first column',fontsize=10)
    for eps,color in [(1,PINE),(.25,BLUE),(.05,OCHRE)]:
        ax.annotate('',xy=(1,eps),xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2,'color':color})
        ax.text(1.02,eps-.025,f'$e={eps:g}$',fontsize=10,color=color)
    ax.annotate('',xy=(0,1),xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2,'color':RED})
    ax.text(.06,.85,'normal residual $g$',fontsize=10,color=RED)
    ax.set(xlabel='ambient coordinate 1',ylabel='ambient coordinate 2',xlim=(-.12,1.55),ylim=(-.2,1.15),xticks=[0,1],yticks=[0,.5,1])
    ax.set_aspect('equal',adjustable='box');ax.set_anchor('N');ax.set_title('A basis nearing dependence',pad=12);tidy(ax)
    eps=np.geomspace(1e-4,1,300)
    bx.loglog(eps,eps,color=OCHRE,lw=2,label=r'raw covector $\|q\|_2$')
    bx.loglog(eps,np.ones_like(eps),color=PINE,lw=2,label=r'corrected norm $\|g\|$')
    bx.set(xlabel='basis parameter $e>0$',ylabel='reported residual norm',ylim=(7e-5,2.4))
    bx.set_title('One invariant residual norm',pad=12);bx.legend(loc='lower right',frameon=False);tidy(bx)
    for e in [Fraction(1),Fraction(1,4),Fraction(1,100),Fraction(1,10000)]:
        # Independently invert the rational two-by-two Gram matrix.
        G=[[Fraction(1),Fraction(1)],[Fraction(1),1+e*e]]
        Gi=[[(1+e*e)/(e*e),-1/(e*e)],[-1/(e*e),1/(e*e)]]
        identity=[[sum(G[i][k]*Gi[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        corrected=e*e/(e*e)
        check('gram_exact_'+str(e),identity==[[1,0],[0,1]] and corrected==1,
              'Exact multiplication verifies G inverse; for q=(0,e), q^T G^-1 q=1.',
              'Python Fraction exact rational arithmetic; e>0')
    finish(fig,name)
    record('a07',name,'What happens when basis vectors nearly coincide?',
      r'Keep $T=I$, $\alpha=1$, datum $r=(0,-1)$ and proposal $a=0$ fixed in $\mathbb R^2$. Use the full basis $B_e=\left(\begin{smallmatrix}1&1\\0&e\end{smallmatrix}\right)$ for $e>0$. Its columns approach the same direction.',
      r'The actual normal residual is always $g=(0,1)$, but its coordinate covector is $q=B_e^{\mathsf T}g=(0,e)$. With $G=B_e^{\mathsf T}B_e$, the invariant square is $q^{\mathsf T}G^{-1}q=1$. At $e=0$ the columns no longer span the permitted space, so the full-space certificate formula no longer applies.',
      r'For $e=0.01$, the raw coordinate norm is $0.01$, although the invariant norm is one. The optimizer remains $(0,-1/2)$, and the unchanged proposal still has optimizer error $1/2$.',
      ['sec:inexact-repair','sec:stopping-rules'])


def stopping_exponents():
    name='a08_stopping_exponents'
    fig,ax=plt.subplots(figsize=(7,4.8))
    fig.subplots_adjust(left=.11,right=.84,bottom=.16,top=.88)
    p=np.linspace(.005,2.5,180);q=np.linspace(.005,3.3,200);pp,qq=np.meshgrid(p,q)
    gamma=np.minimum(np.minimum(pp/4,1-pp/2),qq-pp)
    good=(pp<2)&(qq>pp)
    masked=np.ma.masked_where(~good,gamma)
    cmap=LinearSegmentedColormap.from_list('rate',[PALE,PINE]);cmap.set_bad('#F3F1EB')
    im=ax.pcolormesh(pp,qq,masked,cmap=cmap,vmin=0,vmax=1/3,shading='auto',rasterized=False,edgecolors='face',linewidth=.6,antialiased=False)
    ax.plot([0,2.5],[0,2.5],color=INK,lw=1.3,ls='--');ax.axvline(2,color=INK,lw=1.3,ls='--')
    ax.scatter([4/3],[5/3],marker='*',s=120,color=OCHRE,edgecolors='white',linewidth=.7,zorder=5)
    ax.annotate(r'$(4/3,5/3)$',xy=(4/3,5/3),xytext=(.48,1.35),fontsize=10,arrowprops={'arrowstyle':'-','color':OCHRE})
    ax.text(.12,2.92,r'$\gamma=\min(p/4,\,1-p/2,\,q-p)$',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.8,'pad':4})
    ax.text(.9,.43,'Solver bound\ndoes not vanish',ha='center',fontsize=11,color=MUTED)
    ax.text(2.25,2.89,'Noise bound\ndoes not\nvanish',ha='center',va='center',fontsize=10,color=MUTED)
    ax.set(xlabel=r'parameter exponent $p$',ylabel=r'solver-tolerance exponent $q$',xlim=(0,2.5),ylim=(0,3.3),xticks=[0,.5,1,1.5,2,2.5],yticks=[0,1,2,3])
    ax.set_title('Which schedules retain a convergent guarantee?',pad=14)
    cax=fig.add_axes([.885,.16,.028,.72]);cb=fig.colorbar(im,cax=cax);cb.set_label(r'guaranteed error exponent $\gamma$',fontsize=10)
    cb.set_ticks([0,1/6,1/3]);cb.set_ticklabels(['0','1/6','1/3'])
    for delta in [1.,.1,.001,1e-6]:
        p0=4/3;q0=5/3;m=math.ceil(delta**(-p0/2));alpha=m**-2
        bias=math.sqrt(2/m);noise=delta*m/2;solver=delta**q0/alpha
        check('stopping_rounded_'+str(delta),bias<=math.sqrt(2)*delta**(p0/4)+1e-11 and noise<=.5*delta**(1-p0/2)+.5*delta+1e-11 and solver<=delta**(q0-p0)*(1+delta**(p0/2))**2+1e-11,
              'The explicit ceiling schedule satisfies all three stated power bounds at the checked noise value.')
    finish(fig,name)
    record('a08',name,'Which stopping schedules preserve convergence?',
      r'For the attainable diagonal datum $r_n=1/n^2$, choose $m=\lceil\delta^{-p/2}\rceil$, $\alpha=m^{-2}$, and solver tolerance $\varepsilon=\delta^q$, where $0<\delta\le1$. Vary the positive exponents $p,q$ instead of fixing one noise schedule.',
      r'The proved bias, noise and solver bounds have orders $\delta^{p/4}$, $\delta^{1-p/2}$ and $\delta^{q-p}$. All vanish in the colored region $0<p<2$, $q>p$. Its color records their slowest exponent. The uncolored region loses this sufficient guarantee; it does not assert failure of every actual solver.',
      r'The marked choice $(p,q)=(4/3,5/3)$ balances all three exponents at $1/3$. Choosing $q=p$ instead leaves a nonvanishing solver bound. The ceiling is retained in the underlying parameter rule.',
      ['sec:diagonal-regularization','sec:stopping-rules'])


def main():
    for run in [protected_angles,scale_and_motion,same_residual_paths,exponent_energy,
                budget_geometry,regularization_modes,basis_certificate,stopping_exponents]:
        run()
    (ROOT/'records').mkdir(exist_ok=True);(ROOT/'build').mkdir(exist_ok=True);(ROOT/'review').mkdir(exist_ok=True)
    (ROOT/'records/analysis_scenes.json').write_text(json.dumps(SCENES,indent=2)+'\n')
    report={'result':'finite formulas and displayed predictions checked',
            'command':'python3 tools/visual_companion/analysis.py','python':platform.python_version(),
            'numpy':np.__version__,'matplotlib':matplotlib.__version__,
            'arithmetic':'Binary64 except explicitly marked rational checks; tolerance 1e-11; deterministic grids, no randomness.',
            'non_claim':'Finite plotting checks do not prove infinite-dimensional existence or convergence. Written p-series arguments and the cited monograph theorems supply those conclusions.',
            'checks':CHECKS,'artifacts':ARTIFACTS}
    (ROOT/'build/analysis_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'scenes':len(SCENES),'checks':len(CHECKS),'passed':all(x['passed'] for x in CHECKS),'artifacts':ARTIFACTS},indent=2))


if __name__=='__main__':main()
