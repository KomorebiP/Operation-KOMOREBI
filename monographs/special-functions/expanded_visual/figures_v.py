"""Twelve new exact-function visual lessons for Paper V.

Portable dependencies: numpy, scipy, mpmath, matplotlib and guide_style.py.
No original-source directory, download, network, random sample or AI image is used.
"""
from pathlib import Path
import json
import math
import numpy as np
import mpmath as mp
from scipy import special as sp
from scipy.integrate import quad
import matplotlib.pyplot as plt
from guide_style import save_figure, COLORS, mobius_sieve

ROOT = Path(__file__).resolve().parent
AUDIT = []
mp.mp.dps = 60

def window(a,y):
    y=np.asarray(y); return np.exp((a*y-np.exp(y)-sp.gammaln(a))/2)

def ambiguity(a,h,e):
    return np.exp(sp.loggamma(a+1j*np.asarray(e))-sp.gammaln(a)
                  -(a+1j*np.asarray(e))*np.log(np.cosh(np.asarray(h)/2)))

def fourier(a,w):
    return np.exp((a/2-1j*np.asarray(w))*np.log(2)
                  +sp.loggamma(a/2-1j*np.asarray(w))
                  -.5*np.log(2*np.pi)-.5*sp.gammaln(a))

def rho(a,w):
    return np.exp((a-1)*np.log(2)-np.log(np.pi)-sp.gammaln(a)
                  +2*sp.loggamma(a/2+1j*np.asarray(w)).real)

def poly(a,n,x):
    x=np.asarray(x); old=np.ones_like(x,dtype=float)
    if n==0:return old
    cur=2*x/np.sqrt(a)
    for j in range(1,n):
        old,cur=cur,(2*x*cur-np.sqrt(j*(j+a-1))*old)/np.sqrt((j+1)*(j+a))
    return cur

def laguerre(a,n,y):
    return (np.sqrt(math.factorial(n))*np.exp(-.5*sp.gammaln(n+a))
            *np.exp(a*np.asarray(y)/2-np.exp(y)/2)
            *sp.eval_genlaguerre(n,a-1,np.exp(y)))

def pair():
    return plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')

def finish(fig,stem,source,parameters,checks=None,scope='Closed formulas sampled on the displayed real grid.'):
    for ax in fig.axes:
        if ax.get_xlabel() or ax.get_ylabel(): ax.grid(alpha=.17)
    save_figure(fig,stem)
    AUDIT.append(dict(stem=stem,source=source,parameters=parameters,
                      checks=checks or {},scope=scope))

def main():
    AUDIT.clear()
    mp.mp.dps = 60
    # V01: normalization, including analytic probability tails of the crop.
    y=np.linspace(-7,3,600); shapes=[.5,1.5,4]
    fig,ax=pair()
    tails={}
    for a in shapes:
        ax[0].plot(y,window(a,y),label=rf'$\alpha={a}$')
        ax[1].plot(y,window(a,y)**2,label=rf'$\alpha={a}$')
        tails[str(a)]=float(sp.gammainc(a,np.exp(-7))+sp.gammaincc(a,np.exp(3)))
    ax[0].set(xlabel='Log position y',ylabel='Normalized window',title='Amplitude')
    ax[1].set(xlabel='Log position y',ylabel='Probability density',title='Squared amplitude')
    ax[0].legend(); ax[1].legend()
    finish(fig,'V01_log_gamma','V Definition 2.1; Proposition 2.2',dict(shapes=shapes,y=[-7,3]),
           {'exact_crop_omitted_probability':tails},'The full L² norm is exactly one; visible crop probabilities are not renormalized.')
    # V02: direct integral comparison on a finite y interval with a tail bound.
    a=1.5;h=1.4;e=.8;y=np.linspace(-6,3,600)
    product=window(a,y+h/2)*window(a,y-h/2)
    L,U=-30.,6.
    fr=lambda z: float(window(a,z+h/2)*window(a,z-h/2)*np.cos(e*z))
    fi=lambda z: float(window(a,z+h/2)*window(a,z-h/2)*np.sin(e*z))
    re,er=quad(fr,L,U,epsabs=2e-13,epsrel=2e-13);im,ei=quad(fi,L,U,epsabs=2e-13,epsrel=2e-13)
    numerical=re+1j*im; closed=complex(ambiguity(a,h,e))
    c=np.cosh(h/2)
    tail=float(np.exp(a*L)/(a*sp.gamma(a))+sp.gammaincc(a,c*np.exp(U))/c**a)
    fig,ax=pair()
    ax[0].plot(y,window(a,y+h/2),label='Left-shifted window')
    ax[0].plot(y,window(a,y-h/2),label='Right-shifted window')
    ax[0].plot(y,product,label='Their product',lw=2.7)
    ax[1].plot(y,product*np.cos(e*y),label='Real integrand')
    ax[1].plot(y,product*np.sin(e*y),label='Imaginary integrand')
    ax[0].set(xlabel='Centered log position y',ylabel='Amplitude',title='Build the integrand')
    ax[1].set(xlabel='Centered log position y',ylabel='Contribution',title='Integrate both parts')
    for x in ax:x.legend(fontsize=9)
    residual=abs(numerical-closed);assert residual<1e-11
    finish(fig,'V02_ambiguity_integral','V Theorem 3.1: Exact ambiguity formula',dict(alpha=a,h=h,eta=e,quadrature_interval=[L,U]),
           dict(closed_real=closed.real,closed_imag=closed.imag,residual=float(residual),quad_error_estimates=[er,ei],integral_tail_upper_bound=tail))
    # V03: magnitude and wrapped phase are different observables.
    h=np.linspace(-5,5,101);e=np.linspace(-4,4,101);H,E=np.meshgrid(h,e);A=ambiguity(1.5,H,E)
    fig,ax=pair()
    p=ax[0].pcolormesh(H,E,np.abs(A),shading='nearest',cmap='viridis',rasterized=True);fig.colorbar(p,ax=ax[0],label='Magnitude',shrink=.85)
    p=ax[1].pcolormesh(H,E,np.angle(A),shading='nearest',cmap='twilight',vmin=-np.pi,vmax=np.pi,rasterized=True);fig.colorbar(p,ax=ax[1],label='Phase, radians',shrink=.85)
    for x in ax:x.set(xlabel='Displacement h',ylabel='Modulation η')
    ax[0].set_title('No real zeros');ax[1].set_title('Wrapped phase')
    # Rasterize colored cells only: prevent viewer-dependent white cell seams.
    with plt.rc_context({'savefig.dpi':300}):
        finish(fig,'V03_phase_space','V Theorem 3.1; Corollary 3.2',dict(alpha=1.5,h=[-5,5],eta=[-4,4],grid=[101,101],
               rendering={'mesh_raster_dpi':300,'axes_and_labels':'vector','png_dpi':170}),
               dict(minimum_sampled_magnitude=float(abs(A).min())), 'Nonvanishing is a Gamma-function theorem. The finite positive grid minimum does not prove it; phase wraps are not zeros.')
    # V04: exact shape recurrence and non-self-adjoint complex Pöschl--Teller.
    h=np.linspace(-5,5,501);a=1.5;e=.8;nu=a+1j*e
    raised=ambiguity(a+1,h,e);rhs=(a+1j*e)/a/np.cosh(h/2)*ambiguity(a,h,e)
    V=-nu*(nu+1)/np.cosh(h/2)**2
    fig,ax=pair()
    ax[0].plot(h,raised.real,label='Raised shape, real');ax[0].plot(h,rhs.real,'--',label='Shift law, real')
    ax[0].plot(h,raised.imag,label='Raised shape, imaginary');ax[0].plot(h,rhs.imag,'--',label='Shift law, imaginary')
    ax[1].plot(h,V.real,label='Real potential');ax[1].plot(h,V.imag,label='Imaginary potential')
    ax[0].set(xlabel='Displacement h',ylabel='Ambiguity',title='Raise shape by one')
    ax[1].set(xlabel='Displacement h',ylabel='Potential coefficient',title='Complex Pöschl–Teller')
    for x in ax:x.legend(fontsize=9)
    F=ambiguity(a,h,e);Fsecond=(nu**2-nu*(nu+1)/np.cosh(h/2)**2)*F/4
    eq=-4*Fsecond+V*F+nu**2*F
    finish(fig,'V04_shift_differential','V Proposition 3.3; Theorem 3.4',dict(alpha=a,eta=e,h=[-5,5]),
           dict(shape_shift_max_residual=float(abs(raised-rhs).max()),analytic_differential_residual=float(abs(eq).max())),
           'Derivatives evaluated analytically, not by finite differences. For nonzero η the displayed potential and eigenvalue are complex.')
    # V05: Gamma Fourier envelope, checked by direct finite-window integration.
    a=1.5;w=np.linspace(-5,5,500);F=fourier(a,w)
    targets=[-2.,0.,2.];errors=[];est=[]
    L,U=-30.,6.
    amplitude_tail=(2*np.exp(a*L/2)/a+2**(a/2)*sp.gamma(a/2)*sp.gammaincc(a/2,np.exp(U)/2))/np.sqrt(2*np.pi*sp.gamma(a))
    for ww in targets:
        rr,er=quad(lambda yy:float(window(a,yy)*np.cos(ww*yy)/np.sqrt(2*np.pi)),L,U,epsabs=2e-12)
        ii,ei=quad(lambda yy:float(-window(a,yy)*np.sin(ww*yy)/np.sqrt(2*np.pi)),L,U,epsabs=2e-12)
        errors.append(float(abs(rr+1j*ii-fourier(a,ww))));est.append([er,ei])
    fig,ax=pair()
    ax[0].plot(w,F.real,label='Real');ax[0].plot(w,F.imag,label='Imaginary')
    ax[1].plot(w,abs(F)**2,label=r'$|\widehat g|^2$');ax[1].plot(w,rho(a,w),'--',label='Meixner formula')
    ax[0].set(xlabel='Fourier frequency ω',ylabel='Fourier amplitude',title='Unitary Fourier transform')
    ax[1].set(xlabel='Fourier frequency ω',ylabel='Probability density',title='Gamma spectral envelope')
    for x in ax:x.legend()
    assert max(errors)<1e-8
    finish(fig,'V05_fourier_gamma','V Theorem 4.1: Fourier transform of the log-Gamma packet',dict(alpha=a,frequency=[-5,5],quadrature_interval=[L,U]),
           dict(direct_quad_residuals=errors,quad_error_estimates=est,amplitude_tail_upper_bound=float(amplitude_tail)))
    # V06: characteristic functions and polynomial characteristic moments.
    h=np.linspace(-5,5,500);w=np.linspace(-5,5,500);fig,ax=pair()
    residuals=[]
    for a in [.5,1.5,4]:
        ax[0].plot(w,rho(a,w),label=rf'$\alpha={a}$')
        ax[1].plot(h,1/np.cosh(h/2)**a,label=rf'$\alpha={a}$')
        for hh in [0.,np.log(4)]:
            val,err=quad(lambda ww:float(rho(a,ww)*np.cos(hh*ww)),-np.inf,np.inf,epsabs=2e-11)
            residuals.append(float(abs(val-1/np.cosh(hh/2)**a)))
    ax[0].set(xlabel='Frequency ω',ylabel='Density',title='Meixner probability')
    ax[1].set(xlabel='Depth displacement h',ylabel='Characteristic function',title='Exact overlap law')
    for x in ax:x.legend()
    assert max(residuals)<1e-9
    finish(fig,'V06_meixner_overlap','V Corollary 4.2: Exact characteristic function',dict(shapes=[.5,1.5,4],h=[-5,5],frequency_crop=[-5,5]),
           dict(full_line_quad_max_residual=max(residuals),ratio_four_alpha_1_5=float(.8**1.5)),
           'Density panels are unrenormalized crops. Characteristic checks use adaptive full-line quadrature with epsabs 2e-11; estimates are numerical, not formal enclosures.')
    # V07: exact Bessel slices reveal Wigner negativity.
    w=np.linspace(0,4,241);ys=[-1.,0.,1.];fig,ax=pair();minimum=0.
    for yy in ys:
        W=np.array([float(mp.re(2*mp.exp(1.5*yy)*mp.besselk(2j*ww,mp.exp(yy))/(mp.pi*mp.gamma(1.5)))) for ww in w])
        minimum=min(minimum,float(W.min()))
        ax[0].plot(w,W,label=f'y = {yy:g}');ax[1].plot(w,W,label=f'y = {yy:g}')
    ax[0].set(xlabel='Frequency ω',ylabel='Wigner density',title='Exact Bessel slices')
    ax[1].set(xlabel='Frequency ω',ylabel='Wigner density',title='Resolve negative lobes',ylim=(-.012,.016),xlim=(.65,3.3))
    for x in ax:x.axhline(0,color='gray',lw=.8);x.legend()
    negative=float(mp.re(2*mp.besselk(4j,1)/(mp.pi*mp.gamma(1.5))))
    assert negative<0
    finish(fig,'V07_wigner_negative','V Theorem 5.1: Closed Wigner formula',dict(alpha=1.5,y_slices=ys,frequency=[0,4],points=241,mpmath_dps=60),
           dict(W_at_y0_omega2=negative,minimum_sampled=minimum),
           'Bessel formula evaluated directly at 60 decimal working precision. Curves interpolate finite samples; the Wigner function is not a probability density.')
    # V08: exact marginals, with an explicit cumulative probability crop.
    a=1.5;y=np.linspace(-7,3,600);w=np.linspace(-5,5,600);fig,ax=pair()
    ax[0].plot(y,window(a,y)**2,label='Position marginal');ax[1].plot(w,rho(a,w),label='Frequency marginal')
    ax[0].fill_between(y,window(a,y)**2,alpha=.12);ax[1].fill_between(w,rho(a,w),alpha=.12)
    ax[0].set(xlabel='Log position y',ylabel='Probability density',title='Integrate over frequency')
    ax[1].set(xlabel='Frequency ω',ylabel='Probability density',title='Integrate over position')
    q=lambda ww:float(rho(a,ww));mass,error=quad(q,-5,5,epsabs=1e-12)
    posmass=sp.gammainc(a,np.exp(3))-sp.gammainc(a,np.exp(-7))
    finish(fig,'V08_wigner_marginals','V Corollary 5.2: Exact marginals',dict(alpha=a,position_crop=[-7,3],frequency_crop=[-5,5]),
           dict(position_crop_mass=float(posmass),frequency_crop_mass=float(mass),quad_error_estimate=error),
           'Plots use the proved exact marginals, not a numerical integral of a truncated Wigner image. Marginal probability tails are explicitly recorded.')
    # V09: uncertainty and metric, with arithmetic shape in its own name.
    a=np.geomspace(.2,30,500);vy=sp.polygamma(1,a);vp=a/4;fig,ax=pair()
    ax[0].semilogx(a,.5*np.sqrt(a*vy),label='Uncertainty product');ax[0].axhline(.5,color=COLORS[1],ls='--',label='Heisenberg lower bound')
    ax[1].loglog(a,vp,label=r'Translation $g_{uu}$');ax[1].loglog(a,vy,label=r'Modulation $g_{\eta\eta}$')
    ax[0].set(xlabel='Continuous shape α',ylabel='ΔY ΔP',title='Strict at finite shape')
    ax[1].set(xlabel='Continuous shape α',ylabel='Metric coefficient',title='Weyl orbit geometry')
    for x in ax:x.legend(fontsize=9)
    finish(fig,'V09_uncertainty_metric','V Theorem 6.1; Proposition 6.2',dict(alpha_range=[.2,30]),
           dict(alpha_1_5_mean_y=float(sp.digamma(1.5)),alpha_1_5_variance_y=float(sp.polygamma(1,1.5)),alpha_1_5_variance_p=.375,alpha_1_5_product=float(.5*np.sqrt(1.5*sp.polygamma(1,1.5)))),
           'Metrics shown are for a fixed-shape translation/modulation orbit. This is not a claim that every mixed metric coefficient involving shape vanishes.')
    # V10: degree 0..4 Laguerre packets and exact-polynomial quadrature Gram.
    a=1.5;y=np.linspace(-5,3,600);nodes,weights=sp.roots_genlaguerre(48,a-1)
    P=np.array([np.sqrt(math.factorial(j)/sp.gamma(j+a))*sp.eval_genlaguerre(j,a-1,nodes) for j in range(5)])
    gram=(P*weights)@P.T;error=float(abs(gram-np.eye(5)).max());assert error<1e-11
    fig,ax=pair()
    for j in range(5):ax[0].plot(y,laguerre(a,j,y),label=f'n = {j}')
    im=ax[1].imshow(gram,vmin=0,vmax=1,cmap='viridis');fig.colorbar(im,ax=ax[1],label='Inner product',shrink=.85)
    ax[0].set(xlabel='Log position y',ylabel='Packet amplitude',title='Laguerre packet basis');ax[0].legend(ncol=2,fontsize=9)
    ax[1].set(xlabel='Degree m',ylabel='Degree n',title='Weighted quadrature Gram',xticks=range(5),yticks=range(5))
    finish(fig,'V10_laguerre_gram','V Theorem 7.1: Orthonormality',dict(alpha=a,degrees=list(range(5)),generalized_gauss_laguerre_nodes=48,position_crop=[-5,3]),
           dict(max_gram_residual=error),
           'Generalized Gauss–Laguerre quadrature is mathematically exact for the displayed polynomial products of degree ≤8 (48 nodes cover ≤95); residuals are floating-point implementation errors. Curves are cropped.')
    # V11: degree phases and common ladder without a falsely real transformed matrix.
    a=1.5;w=np.linspace(-4,4,600);fig,ax=pair()
    for j in range(4):
        F=(1j**j)*fourier(a,w)*poly(a,j,w)
        ax[0].plot(w,F.real,label=f'n = {j}')
    d=6;K0=np.diag(np.arange(d)+a/2);Kp=np.diag(np.sqrt(np.arange(1,d)*(np.arange(d-1)+a)),-1);Km=Kp.T
    JL=2*K0-Kp-Km;JM=(Kp+Km)/2
    indices=np.arange(d-1);ax[1].plot(indices,abs(np.diag(JL,1)),'o-',label='Laguerre neighbor weight')
    ax[1].plot(indices,abs(np.diag(JM,1)),'s-',label='Meixner neighbor weight')
    ax[0].set(xlabel='Frequency ω',ylabel='Real Fourier packet',title='Retain the degree phase');ax[0].legend(ncol=2,fontsize=9)
    ax[1].set(xlabel='Neighbor edge n ↔ n+1',ylabel='Absolute matrix entry',title='One ladder, two recurrences');ax[1].legend(fontsize=9)
    defect=Km@Kp-Kp@Km-2*K0
    # Finite truncations have a top-boundary defect, so test only interior rows.
    interior=float(abs(defect[:-1,:-1]).max());assert interior<1e-12
    finish(fig,'V11_fourier_ladder','V Theorem 8.1: Fourier duality; Theorem 9.1: su(1,1) relations',dict(alpha=a,plotted_degrees=[0,1,2,3],ladder_dimension=d,frequency_crop=[-4,4]),
           dict(interior_commutator_residual=interior,top_boundary_defect=float(defect[-1,-1])),
           'Algebra identities hold on the infinite finite-support basis. A 6×6 truncation fails at its top boundary; that defect is recorded rather than discarded as a global check.')
    # V12: fractional depth, including removal of the depth-zero unit packet.
    N=200_000;mu=mobius_sieve(N)[1:].astype(float);nn=np.arange(1,N+1,dtype=float);dn=1-nn**-2
    r=np.linspace(.2,5,80);C=np.array([np.sum(mu*nn**-2*dn**rr) for rr in r])
    zetas=[1/mp.zeta(2+2*j) for j in range(81)]
    rr=mp.mpf('2.5');direct=float(np.sum(mu*nn**-2*dn**2.5));J=np.arange(1,81)
    naive=[];centered=[]
    for jj in J:
        naive.append(float(mp.fsum([(-1)**k*mp.binomial(rr,k)*zetas[k] for k in range(jj+1)])))
        centered.append(float(mp.fsum([(-1)**k*mp.binomial(rr,k)*(zetas[k]-1) for k in range(jj+1)])))
    reference=float(mp.fsum([(-1)**k*mp.binomial(rr,k)*(zetas[k]-1) for k in range(81)]))
    fig,ax=pair()
    ax[0].plot(r,C,label='Direct Möbius cutoff');ax[0].scatter([1,2,3,4],[np.sum(mu*nn**-2*dn**j) for j in [1,2,3,4]],color=COLORS[1],label='Integer depths')
    ax[1].semilogy(J,np.maximum(abs(np.array(naive)-reference),1e-18),label='Original binomial sum')
    ax[1].semilogy(J,np.maximum(abs(np.array(centered)-reference),1e-18),label='Unit packet removed')
    ax[0].set(xlabel='Continuous arithmetic depth r',ylabel='Signed amplitude',title='Smooth beyond integers');ax[0].legend(fontsize=9)
    ax[1].set(xlabel='Last binomial index J',ylabel='Difference from J=80 reference',title='Two equivalent coordinates');ax[1].legend(fontsize=9)
    finish(fig,'V12_fractional_depth','V Theorems 10.1 and 10.2: Fractional binomial orbit and generator',dict(a=2,beta=2,N=N,r_range=[.2,5],example_depth=2.5,binomial_reference_last_index=80,mpmath_dps=60),
           dict(direct_example=direct,centered_reference=reference,difference=float(abs(direct-reference)),direct_signed_tail_upper_bound=1/N),
           'The direct sieve has absolute tail ≤1/N for all shown depths. Binomial references are finite 60-digit sums, not certified infinite enclosures; logarithmic difference curves are floored at 1e-18. Subtracting 1 is legitimate because the full generalized binomial coefficient sum is zero for r>0; it removes n=1.')
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence'/'figures_v_audit.json').write_text(json.dumps({'scope':'New closed-form and declared finite/quadrature figures; no universal computational proof.', 'entries':AUDIT},indent=2)+'\n')
    print(json.dumps({'paper':'V','figure_pairs':len(AUDIT),'audit':'evidence/figures_v_audit.json'}))

if __name__=='__main__':main()
