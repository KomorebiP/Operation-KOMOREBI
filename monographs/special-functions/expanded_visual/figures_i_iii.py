"""Thirty-six new mathematical figures for lessons I--III.

Dependencies: NumPy, Matplotlib, mpmath, SymPy and SciPy.
Infinite arithmetic sums use a declared cutoff and elementary absolute tails.
Source asymptotics are illustrated, not certified by plots.
"""
from pathlib import Path
from functools import lru_cache
import hashlib
import json
import math
import numpy as np
import mpmath as mp
import sympy as sp
import matplotlib.pyplot as plt
from scipy.special import gammainc, roots_genlaguerre, gamma
from guide_style import apply_style, save_figure, COLORS, INK, MUTED, PALE, mobius_sieve

ROOT = Path(__file__).resolve().parent
N = 200_000
mp.mp.dps = 100
apply_style()
AUDIT = {"role": "Finite figures and exact example checks, not universal proof certification",
         "arithmetic_cutoff": N, "energy_tail_bound": 1/(3*N**3),
         "signed_amplitude_tail_bound": 1/N, "figures": {}, "checks": {}}
n = np.arange(1, N+1, dtype=float)
mu = mobius_sieve(N)[1:]
w = mu.astype(float)**2/n**4
inv2 = n**-2
x = (1-inv2)**2
gap = 2*inv2-inv2**2
logx = np.full(N, -np.inf)
logx[1:] = 2*np.log1p(-inv2[1:])
A = 3/(2**2.5*np.pi**1.5)
B = 3/(2**1.5*np.pi)

def canvas(panels=1, figsize=(8.1,4.2)):
    fig, axes = plt.subplots(1,panels,figsize=figsize,layout="constrained")
    return fig, np.atleast_1d(axes)

def emit(stem, fig, **facts):
    save_figure(fig, stem)
    path = ROOT/'figures'/f'{stem}.pdf'
    AUDIT['figures'][stem] = {**facts, 'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def grid(ax):
    ax.grid(True, axis='y'); ax.set_axisbelow(True)

@lru_cache(None)
def bp(order):
    a=sp.symbols('a'); return sp.lambdify(a,sp.bernoulli(order,a),'numpy')

def energy(k, q=1):
    filt=np.ones(N) if k==0 else np.exp(k*logx)
    mask=np.ones(N,dtype=bool) if q==1 else (np.gcd(n.astype(int),q)==1)
    return float(np.dot(w*mask,filt))

@lru_cache(None)
def tilt(k):
    raw=w*np.exp(k*logx); total=float(raw.sum())
    return raw/total, k*gap, 2*k*inv2, total

@lru_cache(None)
def exact_energy(k):
    return mp.fsum((-1)**j*mp.binomial(2*k,j)*mp.zeta(4+2*j)/mp.zeta(8+4*j)
                   for j in range(2*k+1))

def inner(c,d,mom,shift=0):
    return mp.fsum(c[i]*d[j]*mom[i+j+shift] for i in range(len(c)) for j in range(len(d)))

@lru_cache(None)
def exact_jacobi(m):
    mom=[exact_energy(r) for r in range(2*m+1)]
    previous=[mp.mpf(0)]; p=[mp.mpf(1)]; previous_norm=mp.mpf(1)
    diagonals=[]; off=[]
    for degree in range(m):
        h=inner(p,p,mom); a=inner(p,p,mom,1)/h
        diagonals.append(a)
        recurrence=h/previous_norm if degree else mp.mpf(0)
        if degree: off.append(mp.sqrt(recurrence))
        nxt=[mp.mpf(0)]*(len(p)+1)
        for j,c in enumerate(p): nxt[j+1]+=c; nxt[j]-=a*c
        for j,c in enumerate(previous): nxt[j]-=recurrence*c
        previous,p,previous_norm=p,nxt,h
    J=mp.diag(diagonals)
    for j,b in enumerate(off): J[j,j+1]=J[j+1,j]=b
    nodes,V=mp.eigsy(J)
    weights=[V[0,j]**2 for j in range(m)]
    return J,list(nodes),weights

@lru_cache(None)
def tilted_jacobi(k,m):
    prob,u,U,total=tilt(k); seed=np.sqrt(prob); Q=[]; ds=[]; bs=[]
    for j in range(m):
        Q.append(seed.copy()); a=float(np.dot(seed,u*seed)); ds.append(a)
        residual=u*seed-a*seed
        for old in Q: residual-=np.dot(old,residual)*old
        b=float(np.linalg.norm(residual))
        if j<m-1: bs.append(b); seed=residual/b
    J=np.diag(ds)+np.diag(bs,1)+np.diag(bs,-1)
    nodes,V=np.linalg.eigh(J)
    return J,nodes,V[0]**2

def moment_error_bound(k,m):
    prob,u,U,total=tilt(k)
    finite=float(np.dot(prob,U**m))
    tail=(2*k)**m/((3+2*m)*N**(3+2*m))
    return (tail+finite/(3*N**3))/total

def figure_I04():
    """Render the exponential section lesson independently for label revisions."""
    fig,axes=canvas(2); uu=np.linspace(0,8,201)
    sections=[]; derivatives=[]
    for r in range(3):
        sections.append(sum(uu**j/math.factorial(3*j+r) for j in range(22)))
        derivatives.append(sum(j*uu**(j-1)/math.factorial(3*j+r) for j in range(1,22)))
        axes[0].plot(uu,sections[-1],label=f'address {r}')
    lhs=3*uu*derivatives[0]; rhs=uu*sections[2]
    axes[1].plot(uu,lhs,label='3u E₀′');axes[1].plot(uu,rhs,'--',label='u E₂')
    axes[0].set(xlabel='u',ylabel='Exponential packet',title='Three 22-term section samples');axes[1].set(xlabel='u',ylabel='First lifted row',title='First row: two finite sides')
    for ax in axes: ax.legend();grid(ax)
    AUDIT['checks']['I_exponential_lift_max_residual']=float(np.max(np.abs(lhs-rhs)))
    tails=[float(mp.mpf(8)**22/mp.factorial(66+r)/(1-mp.mpf(8)/((67+r)*(68+r)*(69+r)))) for r in range(3)]
    emit('I04_exponential_system',fig,terms=22,u_range=[0,8],packet_tail_bounds=tails,unmatched_row_term_bound=float(mp.mpf(8)**22/mp.factorial(65)),residual=AUDIT['checks']['I_exponential_lift_max_residual'])

def figures_I():
    fig,(ax,)=canvas(); M=3
    for r in range(M):
        ids=np.arange(r,18,M); ax.scatter(ids,np.full(len(ids),r),s=170,c=COLORS[r],zorder=3)
        for j in ids: ax.text(j,r,str(j),ha='center',va='center',color='white',fontsize=10)
    ax.set(xlabel='Taylor exponent n',ylabel='Residue address r',yticks=[0,1,2],
           xticks=np.arange(0,18,3),ylim=(-.7,2.7),title='Every exponent has exactly one address modulo 3')
    emit('I01_coefficient_addresses',fig,example='exponential coefficients a_n=1/n!, M=3',shown_exponents=[0,17])

    fig,axes=canvas(2); C=np.array([[0,0,.5],[1,0,0],[0,1,0.]])
    im=axes[0].imshow(C,cmap='Blues',vmin=0,vmax=1)
    for r in range(3):
        for c in range(3): axes[0].text(c,r,f'{C[r,c]:g}',ha='center',va='center',color='white' if C[r,c]>.7 else INK)
    axes[0].set(xticks=range(3),yticks=range(3),xlabel='Input address',ylabel='Output address',title='Carry matrix at u = 1/2')
    axes[1].axis('off')
    for y,txt in zip([.8,.52,.24],['address 0  →  address 1','address 1  →  address 2','address 2  →  u × address 0']):
        axes[1].text(.03,y,txt,fontsize=14,bbox=dict(boxstyle='round,pad=.5',facecolor=PALE,edgecolor='none'))
    emit('I02_carry_matrix',fig,matrix=C.tolist())

    fig,(ax,)=canvas(); vals=np.array([[3*m+r for m in range(5)] for r in range(3)])
    ax.imshow(vals,cmap='YlGnBu',aspect='auto')
    for r in range(3):
        for m in range(5): ax.text(m,r,str(vals[r,m]),ha='center',va='center',color='white' if vals[r,m]>6 else INK)
    ax.set(xticks=range(5),yticks=range(3),xlabel='Packet monomial degree m',ylabel='Address r',title='The packet Euler eigenvalue is the original exponent')
    emit('I03_euler_addresses',fig,eigenvalues=vals.tolist())

    figure_I04()

    fig,(ax,)=canvas(); zz=np.linspace(0,8,257)
    vals=[1. if z==0 else float(-mp.mpf(float(z))*mp.zeta(1-mp.mpf(float(z)),mp.mpf('.5'))) for z in zz]
    ax.plot(zz,vals,label='complex-order family on the real axis')
    ints=np.arange(9); samples=[float(sp.bernoulli(int(j),sp.Rational(1,2))) for j in ints]
    ax.scatter(ints,samples,c=COLORS[1],s=65,zorder=4,label='integer Bernoulli samples')
    ax.axhline(0,color=MUTED,lw=.8);ax.set(xlabel='Order z',ylabel='B(z; 1/2)',title='Entire interpolation with removable value B(0; a) = 1');ax.legend();grid(ax)
    emit('I05_bernoulli_interpolation',fig,a=.5,order_range=[0,8],evaluation_precision_digits=100)

    fig,(ax,)=canvas(); aa=np.linspace(.05,1,240)
    parent=8*bp(4)((aa+1)/2); c1=64*bp(4)((aa+1)/4);c3=64*bp(4)((aa+3)/4)
    ax.plot(aa,c1,label='child (M,r)=(4,1)');ax.plot(aa,c3,label='child (4,3)')
    ax.plot(aa,parent,color=INK,label='parent (2,1)');ax.plot(aa,c1+c3,'--',color=COLORS[4],label='sum of both children')
    ax.set(xlabel='Translation a > 0',ylabel='Order-four packet',title='Refinement preserves the parent exactly');ax.legend(ncol=2,fontsize=10);grid(ax)
    emit('I06_parent_child_refinement',fig,order=4,parent=[2,1],children=[[4,1],[4,3]],max_residual=float(np.max(np.abs(parent-c1-c3))))

    fig,axes=canvas(2); L=4;a=sp.Rational(1,3)
    children=np.array([float(L**3*sp.bernoulli(4,(a+j)/L)) for j in range(L)])
    details=np.fft.fft(children)/np.sqrt(L)
    axes[0].bar(range(L),children,color=COLORS[:L]);axes[0].set(xlabel='Child address ℓ',ylabel='bℓ',title='Integer-order child values')
    axes[1].axhline(0,color=MUTED,lw=.8);axes[1].axvline(0,color=MUTED,lw=.8)
    offsets=[(18,-22),(16,0),(-25,20),(-24,-12)]
    for j,v in enumerate(details):
        axes[1].scatter(v.real,v.imag,s=75,color=COLORS[j]);axes[1].annotate(f'W{j}',(v.real,v.imag),xytext=offsets[j],textcoords='offset points',arrowprops=dict(arrowstyle='-',color=COLORS[j],lw=1),fontsize=12)
    extent=max(float(np.max(abs(details.real))),float(np.max(abs(details.imag))),.1)*1.4
    axes[1].set(xlabel='Real part',ylabel='Imaginary part',title='Unitary cyclotomic channels',xlim=(-extent,extent),ylim=(-extent,extent));axes[1].set_aspect('equal')
    residual=abs(float(np.dot(children,children))-float(np.vdot(details,details).real))
    emit('I07_unitary_details',fig,L=L,a='1/3',order=4,parseval_residual=residual)

    fig,axes=canvas(2);aa=np.linspace(0,1,240);bb0=8*bp(4)(aa/2);bb1=8*bp(4)((aa+1)/2)
    axes[0].plot(aa,bb0,label='first child');axes[0].plot(aa,bb1,label='second child')
    low=(bb0+bb1)/np.sqrt(2);high=(bb0-bb1)/np.sqrt(2)
    axes[1].plot(aa,low,label='Bernoulli low-pass');axes[1].plot(aa,high,label='Euler high-pass')
    for ax in axes: ax.set(xlabel='Translation a',ylabel='Order-four value');ax.legend(fontsize=10);grid(ax)
    axes[0].set_title('One pair of Bernoulli children');axes[1].set_title('The same pair in channel coordinates')
    emit('I08_bernoulli_euler_bank',fig,order=4,integer_polynomial_extension_at_a_zero=True)

    fig,axes=canvas(2);aa=np.linspace(-1,2,401);W=aa*(aa-1)*(5*aa**4-10*aa**3+5*aa-2)/5
    axes[0].plot(aa,W);axes[0].axhline(0,color=MUTED,lw=.8);axes[0].axvspan(0,1,color=PALE,zorder=-1)
    axes[0].set(xlabel='a',ylabel='W₄(a)',title='Positive on (0,1), with other sign regions')
    roots=np.array([0,1,.5-np.sqrt((15+2*np.sqrt(65))/20),.5+np.sqrt((15+2*np.sqrt(65))/20),.5+1j*np.sqrt((2*np.sqrt(65)-15)/20),.5-1j*np.sqrt((2*np.sqrt(65)-15)/20)],complex)
    axes[1].scatter(roots.real,roots.imag,c=[COLORS[0]]*4+[COLORS[1]]*2,s=75)
    axes[1].axhline(0,color=MUTED,lw=.8);axes[1].set(xlabel='Real part of root',ylabel='Imaginary part',title='Two roots are nonreal');axes[1].set_ylim(-.5,.5);grid(axes[1])
    emit('I09_wronskian_negative_control',fig,real_roots=4,nonreal_roots=2,roots=[[v.real,v.imag] for v in roots])

    fig,axes=canvas(2);vals=[-729/10,1093/30,1093/30]
    axes[0].bar(range(3),vals,color=COLORS[:3]);axes[0].set(xticks=range(3),xlabel='Third-root child address',ylabel='n = 8 child',title='Two equal children yield a rational detail');grid(axes[0])
    orders=np.arange(2,14);ratios=np.where(orders%2==0,1,3)
    axes[1].bar(orders,ratios,color=[COLORS[j%2] for j in orders]);axes[1].set(xlabel='Positive integer order n',ylabel='Norm divided by rational square',title='Even: 1     Odd: 3',yticks=[1,3],ylim=(0,3.5));grid(axes[1])
    emit('I10_cyclotomic_norm_parity',fig,n8_detail='-328/3',n8_norm='107584/9',orders=[2,13])

    fig,(ax,)=canvas();yy=np.linspace(.18,4,400)
    for k in [40,160,640]:
        peak=np.sqrt(k+1);xx=peak*yy;f=xx**-2*np.exp(k*np.log1p(-xx**-2));fpeak=peak**-2*(1-peak**-2)**k
        ax.plot(yy,f/fpeak,label=f'k = {k}')
    ax.axvline(1,color=MUTED,ls='--');ax.set(xlabel='x / √(k+1)',ylabel='Kernel / its maximum',title='The arithmetic filter has an exact scale center');ax.legend();grid(ax)
    emit('I11_kernel_localization',fig,k_values=[40,160,640],normalized_x_range=[.18,4],continuous_kernel_domain='x >= 1')

    fig,axes=canvas(2);ks=np.unique(np.geomspace(10,10_000,45).astype(int));cs=[];Es=[];Ss=[]
    for k in ks:
        f=np.exp(k*logx/2);cs.append(float(np.dot(mu/n**2,f)));Es.append(energy(int(k)));Ss.append(float(np.dot(mu.astype(float)**2/n**2,f)))
    cs=np.array(cs);Es=np.array(Es);Ss=np.array(Ss);err=1/N;g=cs**2/Es
    axes[0].loglog(ks,np.abs(cs),label='|signed finite amplitude|');axes[0].loglog(ks,np.sqrt(Es),label='√positive energy');axes[0].loglog(ks,Ss,label='all signs made positive')
    axes[0].set(xlabel='Packet order k',ylabel='Amplitude scale',title=f'Common cutoff N = {N:,}');axes[0].legend(fontsize=9);grid(axes[0])
    lo=np.maximum(np.abs(cs)-err,0)**2/(Es+1/(3*N**3));hi=(np.abs(cs)+err)**2/Es
    axes[1].semilogx(ks,g);axes[1].fill_between(ks,lo,hi,color=COLORS[0],alpha=.2,label='absolute truncation-tail band')
    axes[1].set(xlabel='k',ylabel='Principal coherence Γk',title='Finite data leave an asymptotic question');axes[1].legend(fontsize=9);grid(axes[1])
    k=1200;f=np.exp(k*logx/2);ck=float(np.dot(mu/n**2,f));ek=energy(k)
    emit('I12_signed_coherence_boundary',fig,N=N,signed_tail=err,energy_tail=1/(3*N**3),example_k=k,finite_c=ck,finite_E=ek,finite_Gamma=ck**2/ek)

def figures_II():
    fig,axes=canvas(2);zz=np.linspace(-.2,.3,181);slope=-np.log(2)/np.sqrt(2)
    def detail(z):
        if abs(z)<1e-14:return 0.
        z=mp.mpf(float(z));return float(-z*2**(z-1)*(mp.zeta(1-z,mp.mpf('.5'))-mp.zeta(1-z,1))/mp.sqrt(2))
    yy=np.array([detail(v) for v in zz]);axes[0].plot(zz,yy,label='detail W₁(z;1)');axes[0].plot(zz,slope*zz,'--',label='exact tangent')
    axes[1].plot(zz,yy-slope*zz);axes[1].axhline(0,color=MUTED,lw=.8)
    axes[0].set(xlabel='Complex-order coordinate on real axis z',ylabel='Detail value',title='A Stieltjes packet fixes the slope');axes[0].legend(fontsize=10)
    axes[1].set(xlabel='z',ylabel='Detail minus tangent',title='Higher Taylor data remain');grid(axes[1])
    emit('II01_stieltjes_tangent',fig,a=1,slope=slope,z_range=[-.2,.3],precision_digits=100)

    fig,(ax,)=canvas();g1=float(-mp.digamma(mp.mpf(1)/4));g3=float(-mp.digamma(mp.mpf(3)/4))
    vals=[g1,-g3,g1-g3];ax.bar(range(3),vals,color=COLORS[:3]);ax.set(xticks=range(3),xticklabels=['γ₀(1/4)','−γ₀(3/4)','character sum'],ylabel='Contribution',title='The modulo-four character returns π')
    ax.axhline(np.pi,color=COLORS[4],ls='--',label='4 L(1,χ₄) = π');ax.legend();grid(ax)
    emit('II02_character_stieltjes',fig,modulus=4,character_values=[1,0,-1,0],sum=vals[-1],pi_residual=abs(vals[-1]-np.pi))

    fig,axes=canvas(2);children=np.array([-.9,13/30,13/30]);mean=children.mean();dev=children-mean
    axes[0].bar(range(3),children,color=COLORS[:3]);axes[0].axhline(mean,color=INK,ls='--',label='parent mean = −1/90');axes[0].set(xlabel='Child address',ylabel='Order-four value',title='One unequal child creates all the detail');axes[0].legend(fontsize=10)
    axes[1].bar(range(3),dev**2,color=COLORS[:3]);axes[1].set(xlabel='Child address',ylabel='Squared deviation from mean',title='The three contributions sum to 32/27');grid(axes[1])
    emit('II03_detail_variance',fig,children=['-9/10','13/30','13/30'],mean='-1/90',variance='32/27')

    fig,axes=canvas(2);theta=np.linspace(0,2*np.pi,361);z=np.exp(1j*theta)
    for ax,order,child in zip(axes,[3,4],[np.array([0,1/3,-1/3]),children]):
        path=child[0]+child[1]*z+child[2]*z**2;ax.plot(path.real,path.imag)
        for angle in [2*np.pi/3,4*np.pi/3]:
            v=sum(child[j]*np.exp(1j*angle*j) for j in range(3));ax.scatter(v.real,v.imag,color=COLORS[1],s=70)
        ax.axhline(0,color=MUTED,lw=.7);ax.axvline(0,color=MUTED,lw=.7);ax.set(xlabel='Real P(eⁱθ)',ylabel='Imaginary P(eⁱθ)',title=f'Order n = {order}');ax.set_aspect('equal',adjustable='datalim')
    emit('II04_primitive_resultants',fig,L=3,integer_polynomial_a_zero=True,resultant_n3='1/3',resultant_n4='16/9',unitary_normalization='resultant = 3 W1 W2')

    fig,axes=canvas(2);sel=(mu[:60]!=0);ns=n[:60][sel];xs=x[:60][sel];ws=w[:60][sel]
    axes[0].scatter(xs,ws,s=65,color=COLORS[0]);axes[0].set(xlabel='Packet node xₙ',ylabel='Weight wₙ',title='The n = 1 atom has unit mass');axes[0].annotate('n = 1',(0,1),xytext=(.15,.8),arrowprops=dict(arrowstyle='->',color=MUTED))
    axes[1].scatter(xs[1:],ws[1:],s=45);axes[1].set_yscale('log');axes[1].set(xlabel='Positive packet node xₙ',ylabel='Weight wₙ (log scale)',title='Positive atoms accumulate at 1');grid(axes[1])
    emit('II05_positive_measure',fig,shown_n_max=60,full_measure_infinite=True,E0_exact='105/pi^4')

    fig,(ax,)=canvas();ks=np.arange(1,31);orders=np.arange(7);data=np.array([[np.dot(w*np.exp(int(k)*logx),gap**int(m)) for k in ks] for m in orders])
    im=ax.imshow(np.log10(data),aspect='auto',origin='lower',extent=[.5,30.5,-.5,6.5],cmap='YlGnBu');fig.colorbar(im,ax=ax,label='log₁₀ of positive difference layer')
    ax.set(xlabel='Starting order k',ylabel='Difference order m',title='Direct positive sums avoid cancellation in finite differences')
    emit('II06_complete_monotonicity',fig,N=N,k_range=[1,30],m_range=[0,6],minimum_finite_value=float(data.min()),tail_by_m=[2**int(m)/((3+2*int(m))*N**(3+2*int(m))) for m in orders])

    fig,axes=canvas(2);H=mp.matrix([[exact_energy(i+j) for j in range(3)] for i in range(3)]);hh=np.array(H.tolist(),float);corr=hh/np.sqrt(np.outer(np.diag(hh),np.diag(hh)))
    im=axes[0].imshow(corr,vmin=0,vmax=1,cmap='YlGnBu');axes[0].set(xticks=range(3),yticks=range(3),xlabel='Column degree j',ylabel='Row degree i',title='Normalized 3 × 3 Hankel Gram matrix')
    for i in range(3):
        for j in range(3): axes[0].text(j,i,f'{corr[i,j]:.3f}',ha='center',va='center',color='white' if corr[i,j]>.65 else INK,fontsize=11)
    eig,V=mp.eigsy(H);ee=np.array(list(eig),float);axes[1].bar(range(3),ee,color=COLORS[:3]);axes[1].set_yscale('log');axes[1].set(xticks=range(3),xlabel='Eigenvalue index',ylabel='Positive eigenvalue',title='High-precision low-order witness');grid(axes[1])
    emit('II07_hankel_gram',fig,precision_digits=100,eigenvalues=ee.tolist(),H1_determinant=mp.nstr(exact_energy(0)*exact_energy(2)-exact_energy(1)**2,30))

    fig,(ax,)=canvas();re=np.linspace(-2,2,101);im=np.linspace(-1.5,1.5,81);Z=re[None,:]+1j*im[:,None];out=np.empty_like(Z)
    NN=2000;xx=x[:NN];ww=w[:NN]
    for r in range(len(im)): out[r]=np.sum(ww[None,:]/(1-Z[r,:,None]*xx[None,:]),axis=1)
    masked=np.ma.array(out.imag,mask=(np.abs(Z.imag)<.03)&(Z.real>=1));limit=float(np.percentile(abs(masked.compressed()),95))
    mesh=ax.pcolormesh(re,im,masked,cmap='RdBu_r',vmin=-limit,vmax=limit,shading='auto');fig.colorbar(mesh,ax=ax,label='Imaginary part of the resolvent')
    ax.plot([1,2],[0,0],color=INK,lw=3);ax.set(xlabel='Re z',ylabel='Im z',title='Positive above the real axis, negative below');ax.set_aspect('equal')
    zz=Z[~masked.mask];t=np.clip(np.divide(zz.real,np.abs(zz)**2,out=np.zeros(len(zz)),where=np.abs(zz)>0),0,1);mind=float(np.min(np.abs(1-zz*t)))
    emit('II08_zero_free_resolvent',fig,N=NN,real_range=[-2,2],imaginary_range=[-1.5,1.5],excluded_cut=True,maximum_absolute_tail_bound=1/(3*NN**3*mind))

    fig,axes=canvas(2);ks=np.arange(7);NN=2000;direct=np.array([np.dot(w[:NN],np.ones(NN) if k==0 else np.exp(k*logx[:NN])) for k in ks]);exact=np.array([float(exact_energy(int(k))) for k in ks]);errors=exact-direct
    axes[0].plot(ks,exact,'o-',label='exact zeta-ratio stencil');axes[0].plot(ks,direct,'x--',label=f'direct sum n ≤ {NN}');axes[0].set_yscale('log');axes[0].set(xlabel='k',ylabel='Positive energy',title='Two coordinates of the same sequence');axes[0].legend(fontsize=10)
    axes[1].plot(ks,errors,'o-');axes[1].axhline(1/(3*NN**3),color=COLORS[1],ls='--',label='1 / (3N³)');axes[1].set(xlabel='k',ylabel='Exact minus finite sum',title='The displayed discrepancy is a positive tail');axes[1].legend(fontsize=10);grid(axes[1])
    emit('II09_zeta_ratio_stencil',fig,N=NN,precision_digits=100,k_range=[0,6],errors=errors.tolist(),absolute_tail_bound=1/(3*NN**3))

    fig,(ax,)=canvas();ks=np.unique(np.geomspace(10,100_000,55).astype(int));Es=np.array([energy(int(k)) for k in ks]);scaled=Es*ks**1.5
    beta=np.array([float(3/np.pi**2*mp.beta(mp.mpf('1.5'),2*int(k)+1))*int(k)**1.5 for k in ks])
    ax.semilogx(ks,scaled,label='finite squarefree energy');ax.semilogx(ks,beta,'--',label='density beta-integral term');ax.axhline(A,color=INK,ls=':',label='asymptotic constant A')
    ax.set(xlabel='k',ylabel='k³ᐟ² Eₖ',title='A counting theorem fixes the limiting scale');ax.legend(fontsize=11);grid(ax)
    emit('II10_energy_asymptotic',fig,N=N,k_range=[10,100000],A=A,absolute_energy_tail=1/(3*N**3),max_scaled_tail=float(max(ks**1.5)/(3*N**3)),asymptotic_role='source-dependent theorem illustration')

    fig,axes=canvas(2);uu=np.linspace(0,9,301);ks=[100,1000,10000];stats={}
    for k in ks:
        prob,u,U,total=tilt(k);idx=np.argsort(U);sortedU=U[idx];cdf=np.cumsum(prob[idx]);loc=np.searchsorted(sortedU,uu,side='right')-1;values=np.where(loc>=0,cdf[np.maximum(loc,0)],0)
        axes[0].plot(uu,values,label=f'k={k}');stats[str(k)]={'mean':float(np.dot(prob,U)),'second_moment':float(np.dot(prob,U**2)),'cdf_tail_bound':1/(3*N**3*total)}
    axes[0].plot(uu,gammainc(1.5,uu),'--',color=INK,label='Gamma(3/2,1)');axes[0].set(xlabel='U = 2k / n²',ylabel='Cumulative probability',title='The positive packet law has a limiting profile');axes[0].legend(fontsize=10)
    axes[1].bar([0,1],[stats['10000']['mean'],stats['10000']['second_moment']],color=COLORS[:2]);axes[1].scatter([0,1],[1.5,3.75],c=INK,marker='_',s=250,label='Gamma moments');axes[1].set(xticks=[0,1],xticklabels=['mean','second moment'],ylabel='Moment value',title='A two-moment check at k = 10,000');axes[1].legend(fontsize=10);grid(axes[1])
    emit('II11_gamma_packet_law',fig,N=N,k_values=ks,U_grid=[0,9,301],statistics=stats)

    fig,axes=canvas(2);residue=n.astype(int)%5;logs=np.zeros(N,dtype=int)
    for r,l in {1:0,2:1,4:2,3:3}.items():logs[residue==r]=l
    chars=np.array([np.where(residue==0,0,np.exp(2j*np.pi*j*logs/4)) for j in range(4)])
    ks=np.unique(np.geomspace(20,100000,38).astype(int));maxcorr=[];example=None
    for k in ks:
        raw=w*np.exp(int(k)*logx);G=(chars*raw)@chars.conj().T;C=G/G[0,0].real
        maxcorr.append(float(np.max(np.abs(C-np.eye(4)))))
    raw=w*np.exp(10000*logx);G=(chars*raw)@chars.conj().T;C=np.abs(G/G[0,0].real)
    axes[0].imshow(C,vmin=0,vmax=1,cmap='YlGnBu');axes[0].set(xticks=range(4),yticks=range(4),xlabel='Character index',ylabel='Character index',title='Normalized Gram magnitudes, k=10,000')
    for i in range(4):
        for j in range(4):axes[0].text(j,i,f'{C[i,j]:.3f}',ha='center',va='center',fontsize=9,color='white' if C[i,j]>.6 else INK)
    axes[1].loglog(ks,maxcorr,label='largest off-diagonal entry');axes[1].loglog(ks,maxcorr[0]*(ks/ks[0])**(-.25),'--',label='k⁻¹ᐟ⁴ shape reference')
    axes[1].set(xlabel='k',ylabel='Absolute correlation',title='Four distinct characters of one modulus');axes[1].legend(fontsize=9);grid(axes[1])
    emit('II12_character_decoherence',fig,N=N,modulus=5,character_count=4,k_range=[20,100000],matrix_k10000=C.tolist(),maximum_entry_error_bound=2/(3*N**3*energy(10000,5)),reference_line='anchored rate shape, not a uniform proven envelope')

def figures_III():
    fig,axes=canvas(2);orders=np.arange(8);Es=np.array([energy(int(k)) for k in orders]);axes[0].bar(orders,Es,color=[COLORS[1]]+[COLORS[0]]*7)
    axes[0].set(xlabel='Depth k',ylabel='Moment Eₖ',title='The zero atom contributes at k=0 only');axes[0].annotate('includes mass 1',(0,Es[0]),xytext=(2,.75),arrowprops=dict(arrowstyle='->',color=MUTED))
    nn=n[1:5000];axes[1].loglog(nn,gap[1:5000]);axes[1].set(xlabel='Integer-basis label n',ylabel='1 − xₙ',title='Nodes approach 1; the infinite norm is 1');grid(axes[1])
    emit('III01_zero_atom_contraction',fig,zero_atom_mass=1,E0_exact='105/pi^4',T_norm=1,gap_formula='2/n^2 - 1/n^4',node_plot_scope='all integer nodes; squarefree restriction selects a subsequence')

    fig,(ax,)=canvas();sets=[(0,1),(0,2),(1,3)];vals=[]
    for rr in sets:
        vals.append([float(mp.det(mp.matrix([[exact_energy(r+s) for s in ss] for r in rr]))) for ss in sets])
    vv=np.array(vals);im=ax.imshow(np.log10(vv),cmap='YlGnBu');fig.colorbar(im,ax=ax,label='log₁₀ minor');ax.set(xticks=range(3),yticks=range(3),xticklabels=[str(v) for v in sets],yticklabels=[str(v) for v in sets],xlabel='Column exponents',ylabel='Row exponents',title='Generalized minors need not be principal minors')
    for i in range(3):
        for j in range(3):ax.text(j,i,f'{vv[i,j]:.2e}',ha='center',va='center',fontsize=10,color='white' if np.log10(vv[i,j])>np.log10(vv).mean() else INK)
    emit('III02_generalized_minors',fig,precision_digits=100,exponent_sets=[list(v) for v in sets],values=vv.tolist(),minimum=float(vv.min()))

    fig,axes=canvas(2);J,nodes,weights=exact_jacobi(6);JJ=np.array(J.tolist(),float)
    axes[0].imshow(JJ,cmap='YlGnBu');axes[0].set(xticks=range(6),yticks=range(6),xlabel='Jacobi basis index',ylabel='Jacobi basis index',title='The first six Jacobi coordinates')
    axes[1].plot(range(6),np.diag(JJ),'o-',label='diagonal aⱼ');axes[1].plot(range(1,6),np.diag(JJ,1),'s-',label='off-diagonal bⱼ');axes[1].set(xlabel='Index',ylabel='Recurrence coefficient',title='A nearest-neighbor realization');axes[1].legend();grid(axes[1])
    emit('III03_global_jacobi',fig,m=6,precision_digits=100,matrix=JJ.tolist())

    fig,(ax,)=canvas();xi=float(exact_energy(1)/exact_energy(0));atoms=np.array([0,9/16,64/81,576/625,1225/1296])
    ax.scatter(atoms,np.zeros(len(atoms)),s=70,c=COLORS[0],label='selected arithmetic atoms');ax.scatter([xi],[.3],s=110,c=COLORS[1],marker='D',label='one-node Gaussian model')
    ax.axvspan(0,9/16,color=PALE,zorder=-1);ax.annotate(f'ξ₁ = {xi:.6f}',(xi,.3),xytext=(.17,.45),arrowprops=dict(arrowstyle='->',color=MUTED));ax.annotate('first positive atom 9/16',(9/16,0),xytext=(.54,-.25),arrowprops=dict(arrowstyle='->',color=MUTED))
    ax.set(xlabel='Node location',yticks=[],ylim=(-.4,.65),xlim=(-.04,1.02),title='Gaussian nodes lie in the interval, not necessarily at atoms');ax.legend(loc='upper right',fontsize=10)
    emit('III04_gaussian_support_gap',fig,xi=xi,first_positive_atom=9/16,exact_upper_bound=5/48,claim='0 < xi < 5/48 < 9/16')

    fig,(ax,)=canvas();J,nodes,weights=exact_jacobi(4);errs=[]
    for r in range(13):
        reduced=exact_energy(0)*mp.fsum(weights[j]*nodes[j]**r for j in range(4));errs.append(float(abs(exact_energy(r)-reduced)))
    ax.bar(range(13),np.maximum(errs,1e-60),color=[COLORS[0] if r<8 else COLORS[1] for r in range(13)]);ax.set_yscale('log');ax.axvline(7.5,color=MUTED,ls='--')
    ax.set(xlabel='Moment degree r',ylabel='Absolute residual (display floor 10⁻⁶⁰)',title='Four Gaussian nodes match moments 0 through 7');grid(ax)
    emit('III05_exact_moment_contract',fig,m=4,precision_digits=100,errors=errs,display_floor=1e-60,matching_degrees=[0,7],finite_arithmetic_role='100-digit witness of the exact source identity')

    fig,axes=canvas(2);J,nn,ww=exact_jacobi(4);nodes=np.array(nn,float);weights=np.array(ww,float);poles=1/nodes;residues=-float(exact_energy(0))*weights/nodes
    axes[0].scatter(poles,weights,s=75);axes[0].set_xscale('log');axes[0].set_yscale('log');axes[0].axvline(1,color=MUTED,ls='--');axes[0].set(xlabel='Pole z = 1 / ξⱼ',ylabel='Positive spectral weight λⱼ',title='Every pole is on the physical cut')
    axes[1].bar(range(1,5),residues,color=COLORS[1]);axes[1].set_yscale('symlog',linthresh=1);axes[1].axhline(0,color=MUTED,lw=.8);axes[1].set(xlabel='Node index j',ylabel='Residue in the z coordinate',title='The resolvent residues are negative');grid(axes[1])
    emit('III06_poles_and_residue_signs',fig,m=4,nodes=nodes.tolist(),spectral_weights=weights.tolist(),poles=poles.tolist(),residues=residues.tolist())

    fig,(ax,)=canvas();ks=np.unique(np.geomspace(20,10000,35).astype(int));stats={}
    for m in [1,2,3]:
        target=float(mp.rf(mp.mpf('1.5'),m));eu=[];ee=[]
        for k in ks:
            prob,u,U,total=tilt(int(k));eu.append(abs(float(np.dot(prob,U**m))/target-1));ee.append(abs(float(np.dot(prob,u**m))/target-1))
        ax.loglog(ks,eu,color=COLORS[m-1],label=f'U moment m={m}');ax.loglog(ks,ee,'--',color=COLORS[m-1],label=f'u moment m={m}')
        stats[str(m)]={'target':target,'U_moment_k1000':float(np.dot(tilt(1000)[0],tilt(1000)[2]**m)),'u_moment_k1000':float(np.dot(tilt(1000)[0],tilt(1000)[1]**m)),'absolute_U_moment_tail_bound_k1000':moment_error_bound(1000,m)}
    ax.set(xlabel='k',ylabel='Relative moment error from Gamma',title='Two finite-depth coordinates share every fixed moment limit');ax.legend(ncol=2,fontsize=9);grid(ax)
    emit('III07_all_moment_bridge',fig,N=N,k_range=[20,10000],statistics=stats,exact_relation='u = U - U^2/(4k)',bridge_bound='E[U^m-u^m] <= m E[U^(m+1)]/(4k)')

    fig,axes=canvas(2);uu=np.linspace(0,8,240);coeffs={}
    for ax,m in zip(axes,[2,3]):
        for k in [100,10000]:
            prob,u,U,total=tilt(k);mom=np.array([np.dot(prob,u**r) for r in range(2*m+1)])
            H=np.array([[mom[i+j] for j in range(m)] for i in range(m)]);c=np.r_[np.linalg.solve(H,-mom[m:2*m]),1.]
            ax.plot(uu,np.polynomial.polynomial.polyval(uu,c),label=f'packet k={k}');coeffs[f'm{m}_k{k}']=c.tolist()
        z=sp.symbols('z');poly=(-1)**m*sp.factorial(m)*sp.assoc_laguerre(m,sp.Rational(1,2),z);f=sp.lambdify(z,poly,'numpy');ax.plot(uu,f(uu),'--',color=INK,label='monic Laguerre limit')
        ax.axhline(0,color=MUTED,lw=.8);ax.set(xlabel='Endpoint coordinate u',ylabel=f'Monic degree-{m} polynomial',title=f'Fixed degree m = {m}');ax.legend(fontsize=9);grid(ax)
    emit('III08_laguerre_polynomials',fig,N=N,degrees=[2,3],k_values=[100,10000],finite_coefficients=coeffs,display_range_u=[0,8])

    fig,axes=canvas(2);ids=np.arange(5);targeta=2*ids+1.5;targetb=np.sqrt((ids+1)*(ids+1.5));stats={}
    for k in [100,10000]:
        J,nn,ww=tilted_jacobi(k,6);aa=np.diag(J)[:5];bb=np.diag(J,1);axes[0].plot(ids,aa,'o-',label=f'k={k}');axes[1].plot(ids,bb,'o-',label=f'k={k}');stats[str(k)]={'a':aa.tolist(),'b_next':bb.tolist()}
    axes[0].plot(ids,targeta,'--',color=INK,label='2m + α');axes[1].plot(ids,targetb,'--',color=INK,label='√((m+1)(m+α))')
    axes[0].set(xlabel='m',ylabel='Diagonal aₘ',title='Gamma–Laguerre diagonal');axes[1].set(xlabel='m',ylabel='Off-diagonal bₘ₊₁',title='Gamma–Laguerre coupling')
    for ax in axes:ax.legend(fontsize=9);grid(ax)
    emit('III09_jacobi_fixed_point',fig,N=N,alpha=1.5,k_values=[100,10000],statistics=stats)

    fig,(ax,)=canvas();ks=np.unique(np.geomspace(30,10000,35).astype(int));stats={}
    for d in [1,2,3]:
        G=float(mp.fprod(mp.factorial(j)*mp.rf(mp.mpf('1.5'),j) for j in range(d+1)));ratios=[]
        for k in ks:
            prob,u,U,total=tilt(int(k));mom=[float(np.dot(prob,u**r)) for r in range(2*d+1)];H=mp.matrix([[mp.mpf(mom[i+j]) for j in range(d+1)] for i in range(d+1)])
            ratios.append((total*int(k)**1.5/A)**(d+1)*float(mp.det(H))/G)
        ax.semilogx(ks,ratios,label=f'd={d}');stats[str(d)]={'last_ratio':ratios[-1],'G':G}
    ax.axhline(1,color=INK,ls='--');ax.set(xlabel='k',ylabel='Determinant / predicted leading term',title='An affine moment transform avoids catastrophic cancellation');ax.legend();grid(ax)
    emit('III10_shifted_hankel_asymptotic',fig,N=N,k_range=[30,10000],degrees=[1,2,3],statistics=stats,numerical_method='determinant of scaled u moments, not nearly equal shifted E values',tail_scope='each u moment is bounded by the recorded U moment tail; no certified determinant error interval claimed')

    fig,axes=canvas(2);uu=np.linspace(0,8,240);k=10000;prob,u,U,total=tilt(k);kernel=np.zeros(len(uu));limit=np.zeros(len(uu))
    for m in range(3):
        mom=np.array([np.dot(prob,u**r) for r in range(2*m+1)])
        c=np.array([1.]) if m==0 else np.r_[np.linalg.solve(np.array([[mom[i+j] for j in range(m)] for i in range(m)]),-mom[m:2*m]),1.]
        norm=sum(c[i]*c[j]*mom[i+j] for i in range(len(c)) for j in range(len(c)));kernel+=np.polynomial.polynomial.polyval(uu,c)**2/norm
        z=sp.symbols('z');poly=(-1)**m*sp.factorial(m)*sp.assoc_laguerre(m,sp.Rational(1,2),z);ff=sp.lambdify(z,poly,'numpy');limit+=np.asarray(ff(uu))**2/float(mp.factorial(m)*mp.rf(mp.mpf('1.5'),m))
    axes[0].plot(uu,kernel,label='packet K₂(u,u)');axes[0].plot(uu,limit,'--',color=INK,label='Gamma–Laguerre limit');axes[0].set(xlabel='u',ylabel='Diagonal kernel',title='A fixed three-polynomial kernel');axes[0].legend(fontsize=9);grid(axes[0])
    J,nodes,weights=tilted_jacobi(k,3);tn,tw=roots_genlaguerre(3,.5);tw=tw/gamma(1.5)
    axes[1].scatter(nodes,weights,s=90,label='packet rule');axes[1].scatter(tn,tw,s=110,facecolors='none',edgecolors=INK,label='Gauss–Laguerre limit');axes[1].set(xlabel='Quadrature node',ylabel='Normalized weight',title='The associated three-node Gaussian rule');axes[1].legend(fontsize=9);grid(axes[1])
    emit('III11_kernel_quadrature_limit',fig,N=N,k=k,kernel_degree=2,quadrature_m=3,packet_nodes=nodes.tolist(),packet_weights=weights.tolist(),limit_nodes=tn.tolist(),limit_weights=tw.tolist())

    fig,(ax,)=canvas();eps=np.geomspace(1e-5,.1,50);vals=[]
    for e in eps:vals.append(float(np.dot(w,e*x/(gap*(gap+e*x)))))
    scaled=np.array(vals)/np.sqrt(eps);upper=scaled+1/(N*np.sqrt(eps))
    ax.semilogx(eps,scaled,label=f'finite measure n ≤ {N:,}');ax.fill_between(eps,scaled,upper,color=COLORS[0],alpha=.2,label='positive truncation-tail band');ax.axhline(B,color=INK,ls='--',label='source-conditioned cusp constant')
    ax.invert_xaxis();ax.set(xlabel='ε = 1 − z (decreases to the right)',ylabel='[E(1) − E(1−ε)] / √ε',title='The principal edge follows from the energy asymptotic');ax.legend(fontsize=9);grid(ax)
    emit('III12_principal_edge_cusp',fig,N=N,epsilon_range=[1e-5,.1],cusp_constant=B,absolute_difference_tail_bound=1/N,scope='conditional on source energy asymptotic and consolidation Abelian derivation; not an RH estimate')

def main():
    figures_I();figures_II();figures_III()
    assert len(AUDIT['figures'])==36
    assert AUDIT['checks']['I_exponential_lift_max_residual']<1e-12
    assert AUDIT['figures']['I07_unitary_details']['parseval_residual']<1e-12
    assert AUDIT['figures']['III02_generalized_minors']['minimum']>0
    assert max(AUDIT['figures']['III05_exact_moment_contract']['errors'][:8])<1e-60
    assert all(v<0 for v in AUDIT['figures']['III06_poles_and_residue_signs']['residues'])
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence'/'figures_i_iii_audit.json').write_text(json.dumps(AUDIT,indent=2)+'\n')
    print(json.dumps({'figures':len(AUDIT['figures']),'arithmetic_cutoff':N,'audit':'evidence/figures_i_iii_audit.json'}))

if __name__=='__main__': main()
