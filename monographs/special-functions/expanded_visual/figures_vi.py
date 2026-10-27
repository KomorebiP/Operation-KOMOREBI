"""Twelve exact-formula visual lessons for Special Functions VI.

All plots use new Matplotlib PDF output with vector axes and labels. Dense
colored meshes use 300 dpi raster layers to avoid viewer-dependent cell seams.
Numerical quadrature is separated from analytic identities and finite refinements.
"""
from fractions import Fraction
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.special import (gammaln, loggamma, gammainc, gammaincc,
                           betainc, expit, polygamma)
from guide_style import ROOT, COLORS, INK, MUTED, PALE, apply_style, save_figure


def logcosh(x):
    x = np.asarray(x, dtype=float)
    return np.logaddexp(x, -x) - math.log(2)


def window(a, y):
    y = np.asarray(y)
    return np.exp((a*y-np.exp(y)-gammaln(a))/2)


def affinity(a, b):
    return np.exp(gammaln((a+b)/2)-(gammaln(a)+gammaln(b))/2)


def ambiguity(a, b, h, eta):
    z = (a+b)/2+1j*np.asarray(eta)
    return np.exp((a-b)*np.asarray(h)/4+loggamma(z)
                  -(gammaln(a)+gammaln(b))/2-z*logcosh(np.asarray(h)/2))


def beta_logit(a, b, h):
    h = np.asarray(h)
    return np.exp(gammaln(a+b)-gammaln(a)-gammaln(b)
                  -(a+b)*math.log(2)+(a-b)*h/2-(a+b)*logcosh(h/2))


def rho(s, x):
    return np.exp((s-1)*math.log(2)-math.log(math.pi)-gammaln(s)
                  +2*np.real(loggamma(s/2+1j*np.asarray(x))))


def packet(s, n, x):
    x = np.asarray(x, dtype=float)
    if n == 0:
        return np.ones_like(x)
    prev, curr = np.ones_like(x), 2*x/math.sqrt(s)
    for k in range(1, n):
        prev, curr = curr, (x*curr-.5*math.sqrt(k*(k+s-1))*prev)/(.5*math.sqrt((k+1)*(k+s)))
    return curr


def coeff(n, r, a, b):
    return np.exp(.5*(gammaln(n+1)-gammaln(r+1)-gammaln(n-r+1)
        +gammaln(a+r)-gammaln(a)+gammaln(b+n-r)-gammaln(b)
        -gammaln(a+b+n)+gammaln(a+b)))


def multi_coeff(degrees, shapes):
    n, total = sum(degrees), sum(shapes)
    return math.exp(.5*(gammaln(n+1)-sum(gammaln(r+1) for r in degrees)
        +sum(gammaln(a+r)-gammaln(a) for a, r in zip(shapes, degrees))
        -gammaln(total+n)+gammaln(total)))


def sigma(s, t, n):
    n = np.asarray(n)
    return np.exp(.5*(gammaln(s+n)-gammaln(s)-gammaln(s+t+n)+gammaln(s+t)))


def meixner_tail_bound(s, L):
    """Optimized symmetric Chernoff; M(t)=sec(t/2)^s, |t|<pi."""
    t = 2*math.atan(2*L/s)
    return min(1., math.exp(math.log(2)-s*math.log(math.cos(t/2))-t*L))


def beta_outside(a, b, lo, hi):
    return float(betainc(a, b, expit(lo))+1-betainc(a, b, expit(hi)))


def make_axes():
    return plt.subplots(1, 2, figsize=(8.1, 4.2), layout='constrained')


def main():
    apply_style()
    audit = {'source': 'Projector-Generated Special Functions VI',
             'method': 'exact closed forms sampled in floating point; finite refinements include all allocations',
             'displayed_shape_notation': {'first_shape':'alpha','second_shape':'gamma',
                 'many_child_shapes':'alpha_j','semigroup_parameters':['s','t'],
                 'Euler_constant':'gamma_E','change_scope':'notation only; numerical parameters and formulas unchanged'},
             'lessons': {}, 'checks': {}}
    C = audit['checks']; L = audit['lessons']

    y=np.linspace(-6,4,1201); u=np.linspace(.001,20,1201)
    fig, axs=make_axes()
    for a,col in zip([1,2,4,8],COLORS):
        axs[0].plot(y,window(a,y)**2,color=col,label=rf'$\alpha={a}$')
        axs[1].plot(u,np.exp((a-1)*np.log(u)-u-gammaln(a)),color=col)
    axs[0].set(xlabel='Log coordinate y',ylabel='Probability density',title=r'Log-Gamma: mode at $\log\alpha$')
    axs[1].set(xlabel='Positive coordinate u = exp(y)',ylabel='Probability density',title='The Jacobian changes the mode')
    axs[0].legend(fontsize=10);save_figure(fig,'VI01_normalized_shape')
    L['VI01']={'shapes':[1,2,4,8],'log_domain':[-6,4],'gamma_domain':[.001,20],
        'log_density_omitted_mass':{str(a):float(gammainc(a,math.exp(-6))+gammaincc(a,math.exp(4))) for a in [1,2,4,8]},
        'gamma_density_omitted_mass':{str(a):float(gammainc(a,.001)+gammaincc(a,20)) for a in [1,2,4,8]},
        'source':'VI Proposition 1.1, Normalization'}
    C['normalization_shape_2']={'quadrature':quad(lambda z:float(window(2,z)**2),-30,8,epsabs=1e-12)[0],
        'analytic_omitted_mass':float(gammainc(2,math.exp(-30))+gammaincc(2,math.exp(8)))}

    b=np.linspace(.2,8,501); d=np.linspace(-.8,.8,401)
    fig,axs=make_axes()
    axs[0].plot(b,affinity(2,b));axs[0].scatter([2,4],[1,math.sqrt(2/3)],color=COLORS[1],zorder=4)
    axs[0].set(xlabel=r'Second shape $\gamma$; first shape $\alpha=2$',ylabel=r'Origin overlap $F(2,\gamma)$',title='Only equal shapes reach one',ylim=(0,1.06))
    axs[1].plot(d,affinity(2,2+d),label='Exact affinity')
    axs[1].plot(d,1-polygamma(1,2)*d*d/8,ls='--',label='Local quadratic')
    axs[1].set(xlabel='Shape increment d',ylabel='F(2,2+d)',title='Trigamma gives local curvature');axs[1].legend(fontsize=10)
    save_figure(fig,'VI02_shape_affinity')
    L['VI02']={'shape':2,'second_shape_domain':[.2,8],'increment_domain':[-.8,.8],
        'scope':'origin affinity; quadratic is a local expansion, not a global bound',
        'source':'VI Proposition 2.2, Strict shape affinity'}
    C['affinity_exact_example']=float(abs(affinity(2,4)-math.sqrt(2/3)))

    h=np.linspace(-3,3,161);eta=np.linspace(-3,3,161);hh,ee=np.meshgrid(h,eta,indexing='ij');A=ambiguity(2,4,hh,ee)
    fig,axs=make_axes()
    im=axs[0].pcolormesh(h,eta,np.abs(A).T,shading='auto',cmap='viridis',rasterized=True);fig.colorbar(im,ax=axs[0],label='Magnitude')
    im=axs[1].pcolormesh(h,eta,np.angle(A).T,shading='auto',cmap='twilight',vmin=-math.pi,vmax=math.pi,rasterized=True);fig.colorbar(im,ax=axs[1],label='Principal phase')
    for ax in axs:ax.set(xlabel='Translation gap h',ylabel='Modulation gap eta')
    axs[0].set_title(r'Different shapes: $\alpha=2$, $\gamma=4$');axs[1].set_title('The complex overlap has phase')
    axs[0].plot([-math.log(2)],[0],marker='+',color='white',ms=12,mew=2)
    # Rasterize colored cells only: retain vector axes, labels and origin marker.
    with plt.rc_context({'savefig.dpi':300}):
        save_figure(fig,'VI03_cross_ambiguity')
    L['VI03']={'shapes':[2,4],'h_domain':[-3,3],'eta_domain':[-3,3],
        'scope':'finite-domain amplitude and principal phase, with phase wrap distinguished from zeros',
        'source':'VI Theorem 2.1, Cross-shape Gamma-sech formula',
        'rendering':{'mesh_raster_dpi':300,'axes_and_labels':'vector','png_dpi':170}}
    ah,ae=.7,.4
    re=quad(lambda z:float((window(2,z+ah/2)*window(4,z-ah/2)*np.exp(1j*ae*z)).real),-30,8,epsabs=1e-12)[0]
    im=quad(lambda z:float((window(2,z+ah/2)*window(4,z-ah/2)*np.exp(1j*ae*z)).imag),-30,8,epsabs=1e-12)[0]
    C['cross_ambiguity_quadrature_residual']=float(abs(re+1j*im-ambiguity(2,4,ah,ae)))
    mass_a=gammainc(2,math.exp(-30+ah/2))+gammaincc(2,math.exp(8+ah/2))
    mass_b=gammainc(4,math.exp(-30-ah/2))+gammaincc(4,math.exp(8-ah/2))
    C['cross_ambiguity_quadrature_tail_upper_bound']=float(math.sqrt(mass_a*mass_b))

    h=np.linspace(-6,5,701);eta=np.linspace(-5,5,701)
    fig,axs=make_axes()
    axs[0].plot(h,beta_logit(2,4,h),label=r'$(\alpha,\gamma)=(2,4)$');axs[0].plot(h,beta_logit(4,2,h),ls='--',label=r'$(\alpha,\gamma)=(4,2)$')
    axs[0].set(xlabel='Displacement h',ylabel='Probability density',title='Swap shapes: reflect position');axs[0].legend(fontsize=10)
    axs[1].plot(eta,rho(6,eta));axs[1].set(xlabel='Frequency eta',ylabel='Probability density',title=r'Total shape $\alpha+\gamma=6$')
    save_figure(fig,'VI04_factorization')
    hh,ee=np.meshgrid(np.linspace(-3,3,61),np.linspace(-3,3,61),indexing='ij')
    C['cross_spectrogram_factorization_residual']=float(np.max(np.abs(abs(ambiguity(2,4,hh,ee))**2/(2*math.pi)-beta_logit(2,4,hh)*rho(6,ee))))
    L['VI04']={'shapes':[2,4],'h_domain':[-6,5],'eta_domain':[-5,5],
        'position_omitted_mass':beta_outside(2,4,-6,5),'frequency_omitted_mass_upper_bound':meixner_tail_bound(6,5),
        'source':'VI Theorem 3.1, Exact cross-spectrogram factorization'}

    x=np.linspace(-4,4,241)
    conv=np.array([quad(lambda v:float(rho(1,v)*rho(1,z-v)),-8,8,epsabs=1e-11)[0] for z in x])
    fig,axs=make_axes()
    axs[0].plot(x,rho(2,x),label=r'Exact $s+t=2$');axs[0].plot(x,conv,ls='--',label=r'Convolution: $s=t=1$')
    axs[0].set(xlabel='Frequency x',ylabel='Probability density',title='Convolution adds shape');axs[0].legend(fontsize=9)
    axs[1].plot(x,rho(3,x),label=r'Exact $s+2=3$');axs[1].plot(x,(1+4*x*x)*rho(1,x)/2,ls='--',label=r'Quadratic times $s=1$')
    axs[1].set(xlabel='Frequency x',ylabel='Probability density',title='Quadratic multiplication: +2');axs[1].legend(fontsize=9)
    save_figure(fig,'VI05_shape_convolution')
    tail=4/math.pi*math.atan(math.exp(-8*math.pi))
    C['convolution_shape_1_plus_1']={'max_plot_residual':float(np.max(abs(conv-rho(2,x)))),
        'integration_window':[-8,8],'analytic_uniform_omitted_integral_bound':tail,
        'bound_reason':'rho_1 <= 1; omitted convolution integral <= omitted rho_1 mass'}
    C['two_step_ladder_residual']=float(np.max(abs(rho(3,x)-(1+4*x*x)*rho(1,x)/2)))
    L['VI05']={'plot_domain':[-4,4],'shapes':[1,2,3],
        'source':'VI Theorem 4.1, Meixner shape semigroup; Proposition 4.2, Two-step density ladder'}

    xis=np.linspace(0,4,61)
    def levy_integral(xi):
        def integrand(v):
            if v==0:return -xi*xi/(2*math.pi)
            return -2*math.sin(xi*v/2)**2/(v*math.sinh(math.pi*v))
        return quad(integrand,0,10,epsabs=1e-12)[0]
    symbols=np.array([levy_integral(z) for z in xis]);s=np.linspace(.2,8,201)
    fig,axs=make_axes()
    axs[0].plot(xis,-logcosh(xis/2),label='Exact -log cosh(xi/2)');axs[0].plot(xis,symbols,ls='--',label='Levy integral')
    axs[0].set(xlabel='Dual frequency xi',ylabel='Generator symbol',title='Shape has a nonlocal generator');axs[0].legend(fontsize=9)
    for factor,label in [(.25,'Cumulant 2'),(.125,'Cumulant 4'),(.25,'Cumulant 6')]:
        axs[1].plot(s,factor*s,ls='--' if label.endswith('6') else '-',label=label)
    axs[1].set(xlabel='Shape s',ylabel='Even cumulant',title='Cumulants grow linearly');axs[1].legend(fontsize=10)
    save_figure(fig,'VI06_levy_bernoulli')
    C['levy_symbol_residual']=float(np.max(abs(symbols+logcosh(xis/2))))
    L['VI06']={'dual_domain':[0,4],'shape_domain':[.2,8],'integral_domain':[0,10],
        'levy_integral_tail_upper_bound':4*math.exp(-10*math.pi)/(math.pi*10*(1-math.exp(-20*math.pi))),
        'scope':'second-difference cancellation at zero; cumulants 2 and 6 coincide here',
        'source':'VI Theorems 5.1 and 5.2, Levy-Khintchine representation and Bernoulli cumulant law'}

    n=4;a=2;b=3;rs=np.arange(n+1);weights=coeff(n,rs,a,b)**2;x=np.linspace(-2,2,501);yy=.85
    parent=packet(5,4,x+yy);split=sum(coeff(4,r,2,3)*packet(2,r,x)*packet(3,4-r,yy) for r in rs)
    fig,axs=make_axes()
    axs[0].bar(rs,weights,color=COLORS[0]);axs[0].set(xlabel=r'Degree assigned to $\alpha=2$',ylabel='Squared coefficient',xticks=rs,title='All five allocations sum to one')
    for r,w in enumerate(weights):axs[0].text(r,w+.01,f'{[15,20,18,12,5][r]}/70',ha='center',fontsize=10)
    axs[0].set_ylim(0,.35)
    axs[1].plot(x,parent,label=r'Parent: $\alpha+\gamma=5$');axs[1].plot(x,split,ls='--',label=r'Children: $\alpha=2$, $\gamma=3$')
    axs[1].set(xlabel='First child x; second child y = 0.85',ylabel='Normalized degree-4 polynomial',title='Children reconstruct a parent');axs[1].legend(fontsize=9)
    save_figure(fig,'VI07_two_child_refinement')
    C['two_child_energy_residual']=float(abs(weights.sum()-1));C['two_child_reconstruction_residual']=float(np.max(abs(parent-split)))
    L['VI07']={'shapes':[2,3],'degree':4,'x_domain':[-2,2],'second_coordinate':.85,
        'energy_exact':['15/70','20/70','18/70','12/70','5/70'],'scope':'complete finite sum over r=0,...,4; no degree truncation',
        'source':'VI Theorem 6.1, Two-child packet refinement'}

    triples=[(r1,r2,4-r1-r2) for r1 in range(5) for r2 in range(5-r1)]
    direct=np.array([multi_coeff(r,(2,3,1)) for r in triples])
    left=np.array([coeff(4,r[0]+r[1],5,1)*coeff(r[0]+r[1],r[0],2,3) for r in triples])
    right=np.array([coeff(4,r[0],2,4)*coeff(r[1]+r[2],r[1],3,1) for r in triples])
    xx=np.array([(r[1]+.5*r[2])/4 for r in triples]);zz=np.array([math.sqrt(3)*r[2]/8 for r in triples])
    fig,axs=make_axes()
    axs[0].plot([0,1,.5,0],[0,0,math.sqrt(3)/2,0],color=MUTED,lw=1)
    im=axs[0].scatter(xx,zz,s=70+1700*direct**2,c=direct**2,cmap='viridis',edgecolors='white')
    fig.colorbar(im,ax=axs[0],label='Energy')
    for xy,text in [((0,-.08),'(4,0,0)'),((1,-.08),'(0,4,0)'),((.5,.95),'(0,0,4)')]:axs[0].text(*xy,text,ha='center',fontsize=10)
    axs[0].set(xlim=(-.13,1.13),ylim=(-.16,1.03),title=r'$(\alpha_1,\alpha_2,\alpha_3)=(2,3,1)$');axs[0].axis('off')
    idx=np.arange(len(triples));axs[1].plot(idx,direct,label='Direct three-child coefficient')
    axs[1].scatter(idx,left,s=42,facecolors='none',edgecolors=COLORS[1],label='Left bracketing')
    axs[1].scatter(idx,right,s=22,marker='+',color=COLORS[2],label='Right bracketing')
    axs[1].set(xlabel='Allocation index (lexicographic order)',ylabel='Transfer amplitude',title='Both trees give the same law',ylim=(0,.55));axs[1].legend(fontsize=8,loc='upper left')
    save_figure(fig,'VI08_coassociative_refinement')
    C['multinomial_energy_residual']=float(abs(np.sum(direct**2)-1))
    C['coassociativity_residual']=float(max(np.max(abs(direct-left)),np.max(abs(direct-right))))
    L['VI08']={'shapes':[2,3,1],'degree':4,'allocations':[list(r) for r in triples],
        'scope':'all 15 compositions; marker area is affine in energy, color is energy',
        'example_squared_coefficient':'2/21','source':'VI Theorem 7.1, Multinomial packet refinement; Corollary 7.2, Coassociativity'}

    ns=np.arange(1,61);x=np.linspace(-2,2,501)
    fig,axs=make_axes()
    for t in [1,2,3]:axs[0].loglog(ns,sigma(2,t,ns),label=f'increment {t}')
    axs[0].set(xlabel='Polynomial degree n (n >= 1)',ylabel='Singular value',title='Higher degrees contract');axs[0].legend(fontsize=10)
    standard=(2*x*x-1)/math.sqrt(3);transferred=(2*x*x-1)/math.sqrt(15)
    axs[1].plot(x,standard,label=r'Degree-2 packet: $s=2$');axs[1].plot(x,transferred,label=r'Conditional packet: $s+t=5$')
    axs[1].set(xlabel='Current value x',ylabel='Polynomial value',title='Degree two contracts by 0.4472');axs[1].legend(fontsize=9)
    save_figure(fig,'VI09_martingale_spectrum')
    q=quad(lambda y:float(packet(5,2,1+y)*rho(3,y)),-20,20,epsabs=1e-11)[0]
    C['conditional_transfer_degree_2_residual']=float(abs(q-1/math.sqrt(15)))
    C['conditional_transfer_degree_2_tail_upper_bound']=float(
        2*math.cos(1.25)**-3*math.exp(-40)*(2*2/.5**2+4/.5+.5)/math.sqrt(15))
    C['singular_cocycle_residual']=float(np.max(abs(sigma(2,1,ns)*sigma(3,2,ns)-sigma(2,3,ns))))
    L['VI09']={'initial_shape':2,'increments':[1,2,3],'degrees':[1,60],
        'rank_61_transfer_tail_norm_increment_3':float(sigma(2,3,61)),
        'scope':'n=0,...,60 retained; omitted operator norm is sigma_61; thresholds rely on Gamma-ratio asymptotics',
        'source':'VI Theorem 8.1, Polynomial martingale law; Proposition 8.2, Cocycle and compactness'}

    y=np.linspace(-6,5,1001);H=np.linspace(0,5,501)
    fig,axs=make_axes()
    for u,eta,col in [(0,0,COLORS[0]),(1,0,COLORS[1]),(0,2,COLORS[2])]:
        state=np.exp(1j*eta*(y-u/2))*window(2,y-u)
        axs[0].plot(y,state.real,color=col,label=f'u={u}, eta={eta}')
    axs[0].set(xlabel='Position y',ylabel='Real part of coherent state',title=r'Coherent orbit: $\alpha=2$');axs[0].legend(fontsize=9)
    strip=betainc(2,2,expit(H))-betainc(2,2,expit(-H));axs[1].plot(H,strip)
    axs[1].scatter([math.log(3)],[11/16],color=COLORS[1],zorder=4)
    axs[1].axhline(1,ls='--',color=MUTED);axs[1].set(xlabel='Strip half-width H',ylabel='Captured frame energy',title='Full frame energy is one',ylim=(0,1.05))
    save_figure(fig,'VI10_coherent_frame')
    C['frame_strip_exact_example_residual']=float(abs(betainc(2,2,.75)-betainc(2,2,.25)-11/16))
    L['VI10']={'shape':2,'displayed_states':[[0,0],[1,0],[0,2]],'position_domain':[-6,5],
        'frame_test_function':'g_2','strip_half_width_domain':[0,5],
        'scope':'strip calculation integrates frequency on all R; no finite lattice is claimed to be a tight frame',
        'source':'VI Theorem 9.1, Cross-shape coherent overlap; Theorem 9.2, Continuous tight frame'}

    xi=np.linspace(0,6,501)
    def multiplier(a,xi,x):
        return np.exp(2*np.real(loggamma(a+1j*np.asarray(xi)))-2*gammaln(a)-2*a*logcosh(np.asarray(x)/2))
    fig,axs=make_axes()
    for x,col in [(0,COLORS[0]),(2,COLORS[1])]:axs[0].semilogy(xi,multiplier(2,xi,x),color=col,label=f'dual frequency x={x}')
    axs[0].set(xlabel='Dual displacement frequency xi',ylabel='Positive multiplier',title=r'$\alpha=2$: positive multiplier');axs[0].legend(fontsize=9)
    modes=[(0,0),(1,0),(3,0),(1,2)];vals=[float(multiplier(2,z,w)) for z,w in modes]
    axs[1].bar(range(4),vals,color=[COLORS[0],COLORS[1],COLORS[2],COLORS[3]])
    for i,v in enumerate(vals):axs[1].text(i,v+.035,f'{v:.3f}',ha='center',fontsize=11)
    axs[1].set(xticks=range(4),xticklabels=['(0,0)','(1,0)','(3,0)','(1,2)'],xlabel='Dual mode (xi,x)',ylabel='Remaining cosine amplitude',ylim=(0,1.17),title='Cosine modes lose amplitude')
    save_figure(fig,'VI11_berezin_inverse')
    C['berezin_multiplier_closed_form_residual']=float(abs(multiplier(2,1,0)-2*math.pi/math.sinh(math.pi)))
    L['VI11']={'shape':2,'dual_displacement_domain':[0,6],'dual_frequency_slices':[0,2],'modes':[list(z) for z in modes],
        'attenuations':vals,'scope':'cosine symbols are bounded mode examples; unbounded L2 inversion is the source operator result',
        'source':'VI Theorem 10.1, Exact Berezin factorization; Corollary 10.2, Injectivity and ill-posed inversion'}

    z=np.linspace(-4,4,801);normal=np.exp(-z*z/2)/math.sqrt(2*math.pi)
    fig,axs=make_axes()
    for a,col in zip([2,8,32],COLORS):
        sp=math.sqrt(2/a);sq=math.sqrt(a/2)
        axs[0].plot(z,sp*beta_logit(a,a,sp*z),color=col,label=rf'$\alpha={a}$')
        axs[1].plot(z,sq*rho(2*a,sq*z),color=col,label=rf'$\alpha={a}$')
    for ax,title in zip(axs,['Standardized displacement Z','Standardized frequency W']):
        ax.plot(z,normal,color=INK,ls='--',label='Standard normal');ax.set(xlabel='Standardized coordinate',ylabel='Probability density',title=title);ax.legend(fontsize=9)
    save_figure(fig,'VI12_gaussian_heat')
    ga=[]
    for a in [2,8,32]:
        scale_p=math.sqrt(2/a);scale_q=math.sqrt(a/2)
        ga.append({'shape':a,'position_omitted_mass':beta_outside(a,a,-4*scale_p,4*scale_p),
            'frequency_omitted_mass_upper_bound':meixner_tail_bound(2*a,4*scale_q),
            'variance_Z':float(a*polygamma(1,a)),'variance_W':1.,
            'scaled_multiplier_at_1_1':float(multiplier(a,math.sqrt(a/2),math.sqrt(2/a)))})
    L['VI12']={'standardized_domain':[-4,4],'data':ga,
        'normal_omitted_mass':math.erfc(4/math.sqrt(2)),
        'scope':'finite-shape density plots illustrate weak marginal limits; all-Schwartz-seminorm heat convergence is inherited from the source proof, not certified by these plots',
        'source':'VI Theorem 11.1, Gaussian marginal limits; Corollary 11.2, Heat-operator limit'}
    C['heat_multiplier_convergence_example']={'shape_128':float(multiplier(128,8,1/8)),
        'limit_at_1_1':math.exp(-1),'absolute_difference':float(abs(multiplier(128,8,1/8)-math.exp(-1)))}

    assert C['cross_ambiguity_quadrature_residual']<1e-10
    assert C['cross_spectrogram_factorization_residual']<1e-12
    assert C['two_child_reconstruction_residual']<1e-10
    assert C['coassociativity_residual']<1e-12
    assert C['conditional_transfer_degree_2_residual']<1e-9
    assert C['convolution_shape_1_plus_1']['max_plot_residual']<2e-10
    assert abs(C['normalization_shape_2']['quadrature']-1)<1e-10
    assert C['levy_symbol_residual']<1e-10
    for key in ['affinity_exact_example','two_step_ladder_residual',
                'two_child_energy_residual','multinomial_energy_residual',
                'singular_cocycle_residual','frame_strip_exact_example_residual',
                'berezin_multiplier_closed_form_residual']:
        assert C[key]<1e-12, (key,C[key])
    audit['status']='PASS'
    audit['meixner_tail_bound_formula']='2 sec(t/2)^s exp(-t L), t=2 arctan(2L/s); clipped at one'
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence'/'figures_vi_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'volume':'VI','figures':12,'status':'PASS','audit_entries':len(C)}))


if __name__=='__main__':
    main()
