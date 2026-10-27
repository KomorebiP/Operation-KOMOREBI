"""Twelve exact-formula or explicitly finite arithmetic lessons for Paper IV."""
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import mpmath as mp
from scipy.integrate import quad
from scipy.special import loggamma, gammaln, digamma, polygamma, gammainc
from guide_style import ROOT, COLORS, INK, MUTED, PALE, save_figure, apply_style, mobius_sieve


def axes2():
    return plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')


def gamma_ratio(tau):
    return np.exp(loggamma(1.5+.5j*np.asarray(tau))-gammaln(1.5))


def principal_signed_moments(count):
    return [mp.fsum((-1)**r*mp.binomial(j,r)/mp.zeta(2+2*r) for r in range(j+1)) for j in range(count)]


def positive_moments(count):
    return [mp.fsum((-1)**r*mp.binomial(j,r)*mp.zeta(4+2*r)/mp.zeta(8+4*r) for r in range(j+1)) for j in range(count)]


def pade(moments,m=4,count=12):
    mat=mp.matrix([[moments[m+i-j-1] for j in range(m)] for i in range(m)])
    rhs=mp.matrix([-moments[m+i] for i in range(m)])
    q=[mp.mpf(1)]+list(mp.lu_solve(mat,rhs))
    p=[mp.fsum(q[j]*moments[k-j] for j in range(k+1)) for k in range(m)]
    out=[]
    for k in range(count):
        out.append((p[k] if k<m else mp.mpf(0))-mp.fsum(q[j]*out[k-j] for j in range(1,min(k,m)+1)))
    nodes=np.roots([float(v) for v in q])
    H=mp.matrix([[moments[i+j] for j in range(m)] for i in range(m)])
    return p,q,out,nodes,mp.det(H)


def main():
    apply_style();mp.mp.dps=90
    N=200000;full=np.arange(1,N+1,dtype=float);mu_full=mobius_sieve(N)[1:]
    mask=mu_full!=0;n=full[mask];mu=mu_full[mask].astype(float);ln=np.log(n)
    logy=np.full(len(n),-np.inf);logy[n>1]=np.log1p(-1/n[n>1]**2)
    sw=mu/n**2;pw=1/n**4;delta=6/math.pi**2;alpha=1.5
    def filt(depth):return np.ones(len(n)) if depth==0 else np.exp(depth*logy)
    def signed(depth,t=0):return np.sum(sw*filt(depth)*np.exp(-1j*t*ln))
    def kernel(depth,tau=0):return np.sum(pw*filt(depth)*np.exp(-1j*tau*ln))
    def kernel_grid(depths,taus):
        ws=np.asarray([pw*filt(d) for d in depths]);out=np.empty((len(depths),len(taus)),complex)
        for j,t in enumerate(taus):out[:,j]=np.sum(ws*np.exp(-1j*t*ln),axis=1)
        return out
    audit={'source':'Projector-Generated Special Functions IV','number_cutoff':N,
        'arithmetic_parameters':{'a':2,'beta':2,'shape_alpha':1.5},
        'uniform_signed_tail_bound':1/N,'uniform_positive_kernel_tail_bound':1/(3*N**3),
        'method':'portable number-basis sums, exact finite sinc averages, and 90-dps zeta/Padé coordinates',
        'lessons':{},'checks':{}}
    L=audit['lessons'];C=audit['checks']

    ns=np.arange(1,31); mus=mu_full[:30]; nf=np.arange(1,81);yf=1-1/nf**2
    fig,axs=axes2()
    axs[0].vlines(ns,0,mus/ns**2,color=COLORS[0]);axs[0].scatter(ns,mus/ns**2,s=20,color=COLORS[0]);axs[0].axhline(0,color=MUTED,lw=.7)
    axs[0].set(xlabel='Integer n',ylabel='Signed amplitude mu(n) / n²',title='The seed retains its signs')
    for k in [0,5,50]:axs[1].plot(nf,yf**k,label=f'depth k={k}')
    axs[1].set(xlabel='Integer n',ylabel='Depth filter',title='Depth suppresses small integers');axs[1].legend(fontsize=10)
    save_figure(fig,'IV01_signed_seed')
    L['IV01']={'seed_domain':[1,30],'filter_domain':[1,80],'depths':[0,5,50],
        'scope':'n=1 has filter 1 at k=0 and zero at every k>0',
        'source':'IV Chapter 1, One signed seed and two exact evolutions'}

    moments=principal_signed_moments(12);posmom=positive_moments(12);ks=np.arange(11)
    direct=np.array([signed(int(k)).real for k in ks]);exact=np.array([float(moments[k]) for k in ks])
    fig,axs=axes2();axs[0].plot(ks,exact,'o-',label='90-digit reciprocal-zeta coordinate');axs[0].plot(ks,direct,'x',ms=6,label=f'Number sum through {N:,}')
    axs[0].set(xlabel='Integer depth k',ylabel='Signed coefficient C(k,0)',title='Two signed coordinates');axs[0].legend(fontsize=8)
    errs=abs(direct-exact);axs[1].plot(ks,errs,marker='o');axs[1].axhline(1/N,color=COLORS[1],ls='--',label='Uniform cutoff bound 1/N')
    axs[1].set(xlabel='Integer depth k',ylabel='Absolute coordinate difference',title='A controlled number tail');axs[1].legend(fontsize=9)
    save_figure(fig,'IV02_finite_difference')
    C['signed_coordinate_max_residual']=float(errs.max());assert errs.max()<1/N
    L['IV02']={'depths':[0,10],'mpmath_decimal_digits':90,'tail_bound':1/N,
        'source':'IV Chapter 1 signed finite-difference identity; Worked example 1.1, Principal Bernoulli-zeta orbit'}

    small=np.arange(1,41,dtype=float);mu40=mu_full[:40];log40=np.log(small);yy=1-small**-2
    a=mu40/small**2*yy**3*np.exp(-.5j*log40);b=mu40/small**2*yy**3
    dif=log40[:,None]-log40[None,:];amp=a[:,None]*b[None,:]
    Ts=np.geomspace(.25,1024,151);av=np.array([np.sum(amp*np.sinc(T*dif/math.pi)) for T in Ts]);diag=np.sum(a*b)
    fig,axs=axes2()
    for ax,values,target,title in [(axs[0],av.real,diag.real,'Real part of finite correlation'),(axs[1],av.imag,diag.imag,'Imaginary part keeps lag phase')]:
        ax.semilogx(Ts,values);ax.axhline(target,color=COLORS[1],ls='--',label='Finite diagonal target');ax.set(xlabel='Observation half-width T',ylabel='Finite averaged correlation',title=title);ax.legend(fontsize=9)
    save_figure(fig,'IV03_finite_time_average')
    def product(t):return np.sum(a*np.exp(-1j*t*log40))*np.conj(np.sum(b*np.exp(-1j*t*log40)))
    integral=(quad(lambda t:product(t).real,-2,2,epsabs=1e-12)[0]+1j*quad(lambda t:product(t).imag,-2,2,epsabs=1e-12)[0])/4
    finite=np.sum(amp*np.sinc(2*dif/math.pi));C['finite_sinc_integral_residual']=float(abs(integral-finite));assert abs(integral-finite)<1e-10
    L['IV03']={'finite_number_cutoff':40,'depths':[3,3],'lag':.5,'half_width_domain':[.25,1024],
        'scope':'exact finite 40-by-40 sinc formula; no infinite-model finite-time rate is claimed',
        'source':'IV Theorem 2.1, Exact time-average identity'}

    points=[(k,t) for k in [0,10,100,1000] for t in [0,1]]
    V=np.asarray([mu/n**2*filt(k)*np.exp(-1j*t*ln) for k,t in points]);norm=np.sqrt(np.sum(abs(V)**2,axis=1));V=V/norm[:,None];G=V@V.conj().T;eigs=np.linalg.eigvalsh(G)
    fig,axs=axes2();im=axs[0].imshow(abs(G),cmap='viridis',vmin=0,vmax=1);fig.colorbar(im,ax=axs[0],label='Magnitude')
    axs[0].set(xlabel='Packet index',ylabel='Packet index',title='Normalized complex Gram')
    axs[1].bar(range(len(eigs)),eigs,color=COLORS[0]);axs[1].set(xlabel='Ordered eigenvalue index',ylabel='Eigenvalue',title='Nonnegative finite eigenvalues')
    save_figure(fig,'IV04_positive_gram')
    C['gram_hermitian_residual']=float(np.max(abs(G-G.conj().T)));C['gram_min_eigenvalue']=float(eigs.min());assert eigs.min()>-1e-12
    L['IV04']={'points':[[k,t] for k,t in points],'eigenvalues':eigs.tolist(),
        'unnormalized_entry_tail_bound':1/(3*N**3),'scope':'PSD is exact from the finite feature representation; eigenvalues are floating-point diagnostics',
        'source':'IV Theorem 2.2, Positive-definite packet kernel'}

    depths=np.unique(np.rint(np.geomspace(10,100000,40)).astype(int));values=np.array([kernel(int(m)).real for m in depths]);scaled=values*depths**1.5/(delta/2)
    beta=np.exp(gammaln(1.5)+gammaln(depths+1)-gammaln(depths+2.5))*depths**1.5
    taus=np.linspace(-2,2,61);ds=[100,1000,10000];grid=kernel_grid(ds,taus)
    fig,axs=axes2();axs[0].semilogx(depths,scaled,label='Arithmetic kernel');axs[0].semilogx(depths,beta,ls='--',label='Beta main term');axs[0].axhline(math.gamma(1.5),color=COLORS[2],ls=':',label='Gamma limit')
    axs[0].set(xlabel='Combined depth m = k + ell',ylabel='m^alpha K(m,0) / (delta/2)',title='Beta interpolates toward Gamma');axs[0].legend(fontsize=9)
    for m,row in zip(ds,grid):axs[1].plot(taus,(row*np.exp((1.5+.5j*taus)*math.log(m))/(delta/2)).real,label=f'm={m:,}')
    axs[1].plot(taus,np.exp(loggamma(1.5+.5j*taus)).real,color=INK,ls='--',label='Gamma limit')
    axs[1].set(xlabel='Lag tau on a compact interval',ylabel='Real part of scaled kernel',title='A complex law across lag');axs[1].legend(fontsize=8)
    save_figure(fig,'IV05_beta_gamma_depth')
    L['IV05']={'combined_depth_domain':[10,100000],'compact_lag_domain':[-2,2],'displayed_depths':ds,
        'source':'IV Theorem 4.1, Uniform complex packet asymptotic',
        'scope':'finite arithmetic records illustrate the source theorem; its asymptotic constants are not estimated from the plot'}

    taus=np.linspace(-4,4,101);depths_k=[100,1000,10000];grid=kernel_grid([2*k for k in depths_k],taus)
    fig,axs=axes2()
    for k,row in zip(depths_k,grid):
        dephased=np.exp(.5j*taus*math.log(2*k))*row/kernel(2*k).real
        axs[0].plot(taus,dephased.real,label=f'k={k:,}');axs[1].plot(taus,dephased.imag,label=f'k={k:,}')
    for ax,component,title in [(axs[0],gamma_ratio(taus).real,'Carrier removed: real part'),(axs[1],gamma_ratio(taus).imag,'Carrier removed: imaginary part')]:
        ax.plot(taus,component,color=INK,ls='--',label='Gamma ratio');ax.set(xlabel='Lag tau',ylabel='Normalized correlation',title=title);ax.legend(fontsize=8)
    save_figure(fig,'IV06_carrier_dephasing')
    L['IV06']={'equal_depths':depths_k,'compact_lag_domain':[-4,4],
        'scope':'carrier uses 2k, not k; normalization is finite positive energy',
        'normalized_kernel_tail_bounds':{str(k):float(2/(3*N**3)/kernel(2*k).real) for k in depths_k},
        'source':'IV Corollary 5.1, Equal-depth dephasing'}

    taus=np.linspace(0,8,401);closed=(1+taus**2)/np.cosh(math.pi*taus/2);gam=abs(gamma_ratio(taus))**2;variance=float(polygamma(1,1.5)/4)
    fig,axs=axes2();axs[0].plot(taus,gam,label='Squared Gamma-ratio modulus');axs[0].plot(taus,closed,ls='--',label='Elementary closed envelope')
    axs[0].set(xlabel='Lag tau',ylabel='Squared modulus',title='The principal envelope is exact');axs[0].legend(fontsize=8)
    axs[1].semilogy(taus,closed,label='Principal envelope');axs[1].semilogy(taus,np.exp(-variance*taus**2),ls='--',label='Gaussian with matching variance')
    axs[1].set(xlabel='Lag tau',ylabel='Squared modulus (log scale)',title='Equal variance, different tails');axs[1].legend(fontsize=8)
    save_figure(fig,'IV07_principal_envelope')
    C['principal_envelope_residual']=float(np.max(abs(gam-closed)));assert C['principal_envelope_residual']<1e-12
    L['IV07']={'lag_domain':[0,8],'Gaussian_comparison_variance':variance,
        'scope':'closed principal envelope is exact; variance-matched Gaussian is an explicit teaching comparison',
        'source':'IV Worked example 5.2, Closed principal envelope'}

    bins=np.linspace(-1.5,2.5,51);centers=(bins[1:]+bins[:-1])/2;z=np.linspace(-1.5,2.5,501)
    mlist=np.unique(np.rint(np.geomspace(100,100000,30)).astype(int));means=[];variances=[]
    fig,axs=axes2()
    for m,col in zip([1000,10000],COLORS):
        zvals=ln-.5*math.log(m);weights=pw*filt(m);weights/=weights.sum();hist=np.histogram(zvals,bins,weights=weights)[0]/np.diff(bins)
        axs[0].stairs(hist,bins,color=col,label=f'm={m:,}')
    density=2*np.exp(-3*z-np.exp(-2*z)-gammaln(1.5));axs[0].plot(z,density,color=INK,ls='--',label='Limiting log-Gamma density')
    axs[0].set(xlabel='Centered log frequency Z',ylabel='Probability density',title='Remove the drifting log scale');axs[0].legend(fontsize=8)
    for m in mlist:
        w=pw*filt(int(m));w/=w.sum();zv=ln-.5*math.log(m);mean=np.sum(w*zv);means.append(mean);variances.append(np.sum(w*(zv-mean)**2))
    meanlim=-float(digamma(1.5))/2;varlim=float(polygamma(1,1.5))/4
    axs[1].semilogx(mlist,means,label='Finite mean');axs[1].semilogx(mlist,variances,label='Finite variance')
    axs[1].axhline(meanlim,color=COLORS[0],ls='--');axs[1].axhline(varlim,color=COLORS[1],ls='--')
    axs[1].set(xlabel='Combined depth m',ylabel='Moment value',title='Polygamma gives moment targets');axs[1].legend(fontsize=9)
    save_figure(fig,'IV08_centered_log_frequency')
    L['IV08']={'histogram_depths':[1000,10000],'histogram_domain':[-1.5,2.5],'moment_depth_domain':[100,100000],
        'limiting_mean':meanlim,'limiting_variance':varlim,
        'scope':'weighted histograms use full finite normalization; moment convergence requires the source proviso, not weak convergence alone',
        'source':'IV Corollary 6.1, Polygamma cumulants'}

    ratios=np.geomspace(1/16,16,81);profile=(2*np.sqrt(ratios)/(1+ratios))**1.5
    ellgrid=np.unique(np.rint(np.geomspace(10,100000,35)).astype(int));ovs=[]
    fig,axs=axes2();axs[0].semilogx(ratios,profile,color=INK,ls='--',label='Universal scale law')
    for ell,col in zip([100,1000,10000],COLORS):
        kk=np.maximum(1,np.rint(ratios*ell).astype(int));ov=np.array([kernel(int(k+ell)).real/math.sqrt(kernel(2*int(k)).real*kernel(2*ell).real) for k in kk])
        axs[0].semilogx(kk/ell,ov,color=col,label=f'ell={ell:,}')
    axs[0].set(xlabel='Depth ratio r = k / ell',ylabel='Normalized overlap',title='Depth ratio controls overlap');axs[0].legend(fontsize=8)
    for ell in ellgrid:ovs.append(kernel(5*int(ell)).real/math.sqrt(kernel(8*int(ell)).real*kernel(2*int(ell)).real))
    axs[1].semilogx(ellgrid,ovs);axs[1].axhline((4/5)**1.5,color=COLORS[1],ls='--',label='Four-to-one limit')
    axs[1].set(xlabel='Smaller depth ell; k = 4 ell',ylabel='Normalized overlap',title='Increasing absolute scale');axs[1].legend(fontsize=9)
    save_figure(fig,'IV09_cross_depth_overlap')
    L['IV09']={'ratio_domain':[1/16,16],'smaller_depths':[100,1000,10000],'four_to_one_depth_domain':[10,100000],
        'limiting_four_to_one':(4/5)**1.5,'scope':'ratios remain in a compact positive interval; sampled k is rounded to an integer',
        'source':'IV Theorem 7.1, Universal scale overlap; Worked example 7.2, A four-to-one depth ratio'}

    exponent_map=np.array([0,0,1,3,2]);residues=n.astype(np.int64)%5
    chars=np.array([np.where(residues!=0,np.exp(.5j*math.pi*j*exponent_map[residues]),0) for j in range(4)])
    fig,axs=axes2();char_records=[]
    for ax,k in zip(axs,[10,10000]):
        F=chars*np.sqrt(pw*filt(2*k));GG=F@F.conj().T;GG/=GG[0,0].real
        im=ax.imshow(abs(GG),cmap='viridis',vmin=0,vmax=1);ax.set(xticks=range(4),yticks=range(4),xlabel='Character j',ylabel='Character j',title=f'Actual modulus 5; depth {k:,}')
        char_records.append({'depth':k,'max_off_diagonal':float(np.max(abs(GG-np.eye(4))))})
    fig.colorbar(im,ax=axs,label='Normalized magnitude');save_figure(fig,'IV10_character_sectors')
    C['character_modulus_zero_check']=bool(np.all(chars[:,residues==0]==0));assert C['character_modulus_zero_check']
    L['IV10']={'actual_modulus':5,'generator':2,'unit_cycle':[1,2,4,3],'depths':[10,10000],'records':char_records,
        'scope':'all four characters are modulo 5; principal conductor 1 does not remove its modulo-5 zero restriction',
        'source':'IV Theorem 8.1, Character depth-time decoherence; corrected actual-modulus convention from the consolidation review'}

    zs=np.linspace(-.6,.8,241);R2=np.array([np.sum(sw/(1-z*(1-n**-2))) for z in zs]);R4=np.array([np.sum(mu/n**4/(1-z*(1-n**-2))) for z in zs]);shift=(1-zs)*R2+zs*R4
    xs=np.linspace(0,8,161);cutmom=np.array([signed(k).real for k in range(41)]);terms=np.ones_like(xs);egf=cutmom[0]*terms
    for k in range(1,41):terms=terms*xs/k;egf+=cutmom[k]*terms
    borel=np.exp(-xs)*egf;riesz=np.array([np.sum(sw*np.exp(-x/n**2)) for x in xs])
    fig,axs=axes2();axs[0].plot(zs,R2,label=r'$\mathcal{C}_2(z)$');axs[0].plot(zs,R4,label=r'$\mathcal{C}_4(z)$');axs[0].plot(zs,shift,color=INK,ls='--',label='Shifted combination')
    axs[0].set(xlabel='Real z, away from the cut',ylabel='Signed resolvent value',title='The shift returns C(0,0)');axs[0].legend(fontsize=8);axs[0].ticklabel_format(axis='y',style='plain',useOffset=False)
    axs[1].plot(xs,borel,label='Normalized depth EGF, k <= 40');axs[1].plot(xs,riesz,ls='--',label='Riesz coordinate R(x)/x')
    axs[1].set(xlabel='Real continuous depth x',ylabel='Normalized Borel/Riesz value',title='Normalize the Borel coordinate');axs[1].legend(fontsize=8)
    save_figure(fig,'IV11_resolvent_borel')
    C['finite_resolvent_shift_residual']=float(np.max(abs(shift-cutmom[0])));C['normalized_borel_riesz_residual']=float(np.max(abs(borel-riesz)))
    assert C['normalized_borel_riesz_residual']<1e-12
    L['IV11']={'z_domain':[-.6,.8],'x_domain':[0,8],'EGF_retained_degree':40,
        'normalized_EGF_tail_bound':float(math.pi**2/6*gammainc(41,8)),
        'signed_number_tail_bound':1/N,'scope':'R(x)/x is evaluated by its continuous extension at zero; no zero-free signed-resolvent assertion',
        'source':'IV Theorem 9.1, Parameter-shift equation; Chapter 10, The Borel-Riesz bridge'}

    signed_pade=pade(moments);positive_pade=pade(posmom);fig,axs=axes2();axs[0].axvspan(0,1,color=PALE)
    for row,result,label,col in [(0,positive_pade,'Positive order 4',COLORS[0]),(1,signed_pade,'Signed order 4',COLORS[1])]:
        axs[0].scatter(result[3].real,np.full(4,row),s=60,color=col,label=label)
    first=float(moments[1]/moments[0]);axs[0].scatter([first],[1],marker='*',s=170,color=COLORS[2],label='Signed order 1')
    axs[0].set(xlabel='Effective node xi',ylabel='Moment model',yticks=[0,1],yticklabels=['Positive','Signed'],xlim=(-.65,1.06),ylim=(-.35,1.55),title='Signed nodes leave the interval');axs[0].legend(fontsize=8,loc='upper left')
    rows=[]
    for result,inputmom,label,col in [(signed_pade,moments,'Signed',COLORS[1]),(positive_pade,posmom,'Positive',COLORS[0])]:
        errors=[abs(result[2][j]-inputmom[j]) for j in range(12)];axs[1].semilogy(range(12),[max(float(v),1e-90) for v in errors],'o-',color=col,label=label)
        rows.append({'model':label,'hankel_determinant':mp.nstr(result[4],50),'denominator_degree':4,
            'q4':mp.nstr(result[1][-1],50),'effective_nodes':[[float(v.real),float(v.imag)] for v in result[3]],
            'node_minimum_separation':float(min(abs(v-w) for i,v in enumerate(result[3]) for j,w in enumerate(result[3]) if j>i)),
            'max_contracted_moment_residual':mp.nstr(max(errors[:8]),12),'max_later_moment_difference':mp.nstr(max(errors[8:]),12)})
        assert max(errors[:8])<mp.mpf('1e-70')
    axs[1].axvspan(-.5,7.5,color=PALE,zorder=-1);axs[1].set(xlabel='Moment index j',ylabel='Absolute difference (90-digit arithmetic)',title='Eight moments form the contract');axs[1].legend(fontsize=9)
    save_figure(fig,'IV12_signed_positive_pade')
    C['pade_models']=rows
    L['IV12']={'pade_order':4,'input_moments':8,'displayed_moments':12,'mpmath_decimal_digits':90,'first_signed_node':first,'plotted_error_floor':1e-90,
        'scope':'rational contract assumes Hankel nonbreakdown; simple packets additionally require full denominator degree and simple zeros; no universal nonbreakdown or signed physical support is asserted',
        'source':'IV Theorem 11.1, Finite signed Pade reduction, with the consolidation correction; Worked example 11.2, The first signed packet leaves the physical interval'}
    audit['status']='PASS';(ROOT/'evidence').mkdir(exist_ok=True);(ROOT/'evidence/figures_iv_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'volume':'IV','figures':12,'status':'PASS','audit_entries':len(C)}))


if __name__=='__main__':main()
