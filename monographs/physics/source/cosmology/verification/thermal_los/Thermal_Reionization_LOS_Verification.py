from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json, math

import numpy as np
import pandas as pd
from scipy import constants
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from scipy.signal import find_peaks
from scipy.special import spherical_jn
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'; FIG = ROOT / 'figures'
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

@dataclass(frozen=True)
class Params:
    h0_km_s_mpc: float = 70.0
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    omega_r0: float = 9.0e-5
    t_cmb: float = 2.7255
    y_p: float = 0.24
    n_eff: float = 3.046
    n_s: float = 0.965
    A_s: float = 2.1e-9
    k_pivot_mpc: float = 0.05
    tau_reio: float = 0.054
    delta_z_reio: float = 0.5

P = Params()
omega_m0 = P.omega_b0 + P.omega_d0
omega_v0 = 1.0 - P.omega_r0 - omega_m0

c_si = constants.c
sigma_t = constants.physical_constants['Thomson cross section'][0]
m_e = constants.m_e; m_p = constants.m_p; k_b = constants.k; hbar = constants.hbar
g_newton = constants.G; ev = constants.electron_volt
mpc_si = constants.parsec * 1.0e6
h0_si = P.h0_km_s_mpc * 1000.0 / mpc_si
h0_over_c_mpc = (P.h0_km_s_mpc / 299792.458)
rho_c0 = 3.0 * h0_si**2 / (8.0 * math.pi * g_newton)
n_h0 = (1.0 - P.y_p) * P.omega_b0 * rho_c0 / m_p
f_he = P.y_p / (4.0 * (1.0 - P.y_p))

LAMBDA_LYA = 121.567e-9
LAMBDA_2S = 8.22458
E_H_GROUND = 13.6 * ev
E_H_N2 = 3.4 * ev
E_LYA = 10.2 * ev


def e2(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    return P.omega_r0 * aa**-4 + omega_m0 * aa**-3 + omega_v0


def alpha_case_b(T: np.ndarray | float) -> np.ndarray:
    t = np.asarray(T, dtype=float) / 1.0e4
    return 4.309e-19 * t**(-0.6166) / (1.0 + 0.6703 * t**0.5300)


def saha_hydrogen(a: np.ndarray | float) -> np.ndarray:
    aa = np.asarray(a, dtype=float)
    T = P.t_cmb / aa
    nh = n_h0 / aa**3
    lr = 1.5 * np.log(m_e * k_b * T / (2.0 * math.pi * hbar**2)) - E_H_GROUND/(k_b*T) - np.log(nh)
    out = np.empty_like(lr)
    hi = lr > 40.; lo = lr < -40.; mid = ~(hi|lo)
    out[hi] = 1.0 - np.exp(-lr[hi]); out[lo] = np.exp(0.5*lr[lo])
    r = np.exp(lr[mid]); out[mid] = 2.0/(1.0 + np.sqrt(1.0 + 4.0/r))
    return np.clip(out, 0.0, 1.0)


class ThermalHistory:
    def __init__(self, ngrid: int = 42001) -> None:
        self.N = np.linspace(math.log(1.0e-8), 0.0, ngrid)
        self.a = np.exp(self.N); self.z = 1.0/self.a - 1.0
        self.E = np.sqrt(e2(self.a)); self.Hc = self.a*self.E
        self.eta = np.concatenate([[0.0], cumulative_trapezoid(1.0/self.Hc, self.N)])
        self.chi = self.eta[-1] - self.eta
        self._solve_recombination(); self._calibrate_reionization(); self._build_visibility()

    def peebles_rhs(self, N: float, y: np.ndarray) -> np.ndarray:
        a = math.exp(N); T = P.t_cmb/a; nh=n_h0/a**3
        H = h0_si*math.sqrt(float(e2(a))); x=min(max(float(y[0]),1e-12),1.0)
        alpha=float(alpha_case_b(T))
        beta=alpha*(m_e*k_b*T/(2*math.pi*hbar**2))**1.5*math.exp(-E_H_N2/(k_b*T))
        K=LAMBDA_LYA**3/(8*math.pi*H)
        C=(1+K*LAMBDA_2S*nh*(1-x))/(1+K*(LAMBDA_2S+beta)*nh*(1-x))
        ion=beta*(1-x)*math.exp(-E_LYA/(k_b*T)); rec=nh*alpha*x*x
        return np.array([C*(ion-rec)/H])

    def _solve_recombination(self) -> None:
        zscan=np.linspace(3000.,800.,9001); ascan=1/(1+zscan); xs=saha_hydrogen(ascan)
        i=int(np.argmin(np.abs(xs-0.99)))
        self.z_peebles_start=float(zscan[i]); ns=math.log(float(ascan[i])); ne=math.log(0.02)
        sol=solve_ivp(self.peebles_rhs,(ns,ne),[float(xs[i])],method='Radau',rtol=1e-9,atol=1e-12,max_step=0.008,dense_output=True)
        if not sol.success: raise RuntimeError(sol.message)
        x=np.empty_like(self.a); before=self.N<ns; after=self.N>ne; middle=~(before|after)
        x[before]=saha_hydrogen(self.a[before]); x[middle]=sol.sol(self.N[middle])[0]; x[after]=sol.y[0,-1]
        self.xH=np.clip(x,0,1); self.residual_xH=float(sol.y[0,-1])
        # Controlled smooth helium transitions (not a precision multilevel He calculation).
        he3=0.5*(1+np.tanh((self.z-6000.)/500.)); he2=0.5*(1+np.tanh((self.z-2500.)/250.))
        self.xe_rec=self.xH+f_he*(he2+he3)

    def _reionized_xe(self,zre:float)->np.ndarray:
        y=(1+self.z)**1.5; yr=(1+zre)**1.5; dy=1.5*math.sqrt(1+zre)*P.delta_z_reio
        rh=0.5*(1+np.tanh((yr-y)/dy))
        yhe=(1+3.5)**1.5; dyhe=1.5*math.sqrt(1+3.5)*0.5
        rhe=0.5*(1+np.tanh((yhe-y)/dyhe))
        return self.xe_rec+rh*((1+f_he)-self.xe_rec)+f_he*rhe

    def _extra_tau(self,zre:float)->float:
        extra=np.maximum(self._reionized_xe(zre)-self.xe_rec,0)
        pref=self.a*(n_h0/self.a**3)*sigma_t*c_si/h0_si/self.Hc
        return float(np.trapezoid(extra*pref,self.N))

    def _calibrate_reionization(self)->None:
        self.z_re=float(brentq(lambda z:self._extra_tau(z)-P.tau_reio,4,20))
        self.xe=self._reionized_xe(self.z_re); self.tau_reio_actual=self._extra_tau(self.z_re)

    def _build_visibility(self)->None:
        pref=self.a*(n_h0/self.a**3)*sigma_t*c_si/h0_si/self.Hc
        dtdN=pref*self.xe; dtdNrec=pref*self.xe_rec
        self.tau=-cumulative_trapezoid(dtdN[::-1],self.N[::-1],initial=0)[::-1]
        self.tau_rec=-cumulative_trapezoid(dtdNrec[::-1],self.N[::-1],initial=0)[::-1]
        self.g=np.exp(-np.minimum(self.tau,700))*dtdN
        self.g_rec=np.exp(-np.minimum(self.tau,700))*dtdNrec
        self.g_re=np.maximum(self.g-self.g_rec,0)

    def shell(self,w:np.ndarray)->tuple[float,float,float]:
        norm=float(np.trapezoid(w,self.N)); chi=float(np.trapezoid(w*self.chi,self.N)/norm)
        sig=math.sqrt(max(float(np.trapezoid(w*(self.chi-chi)**2,self.N)/norm),0))
        return norm,chi,sig


def growth_history(hist:ThermalHistory,nmin:float=-9.0,npts:int=601)->dict[str,np.ndarray]:
    N=np.linspace(nmin,0,npts)
    def rhs(n,y):
        a=math.exp(n); E2=float(e2(a)); dlnH=-0.5*(4*P.omega_r0*a**-4+3*omega_m0*a**-3)/E2
        om=omega_m0*a**-3/E2
        return [y[1],-(2+dlnH)*y[1]+1.5*om*y[0]]
    a0=math.exp(nmin); sol=solve_ivp(rhs,(nmin,0),[a0,a0],t_eval=N,rtol=1e-10,atol=1e-12)
    D=sol.y[0]; DN=sol.y[1]; g=(D/np.exp(N))/(D[0]/a0); gN=g*(DN/D-1)
    return {'N':N,'a':np.exp(N),'D':D,'DN':DN,'g':g,'gN':gN}


def transfer_simple(k:np.ndarray)->np.ndarray:
    # Smooth equality-scale transfer used only for late potential decay.
    keq=45.0
    return 1.0/(1.0+(k/keq)**2)


def production_matching(level_masses:np.ndarray)->pd.DataFrame:
    return pd.DataFrame({
        'level':np.arange(1,len(level_masses)+1),
        'mass_over_A':level_masses,
        'dln_n_dln_A_independent':1.5+math.pi*level_masses,
        'single_clock_relative_entropy':np.zeros(len(level_masses)),
    })


def project_spectra(hist:ThermalHistory, sources:pd.DataFrame, *, kpoints:int=12000, ell_max:int=2500, selected_only:np.ndarray|None=None):
    ks=sources.k_over_H0.to_numpy(); ATs=sources.AT.to_numpy(); AVs=sources.AV.to_numpy(); AEs=sources.AE.to_numpy()
    splAT=CubicSpline(ks,ATs,bc_type='natural'); splAV=CubicSpline(ks,AVs,bc_type='natural'); splAE=CubicSpline(ks,AEs,bc_type='natural')
    kmin=max(0.05,float(ks.min())); kmax=min(2200.,float(ks.max()))
    kd=np.unique(np.concatenate([np.geomspace(kmin,2,350,endpoint=False),np.linspace(2,kmax,kpoints)]))
    lnk=np.log(kd); kphys=kd*h0_over_c_mpc; PR=P.A_s*(kphys/P.k_pivot_mpc)**(P.n_s-1)
    AT=splAT(kd); AV=splAV(kd); AE=splAE(kd)
    gre_int,chi_re,sig_re=hist.shell(hist.g_re)
    grec_int,chi_rec,sig_rec_rms=hist.shell(hist.g_rec)
    # The long residual-ionization tail inflates the global RMS width.  The
    # finite-thickness acoustic projection uses the central FWHM-equivalent
    # Gaussian width, while the complete visibility remains archived.
    ip=int(np.argmax(hist.g_rec)); half=0.5*hist.g_rec[ip]; ilo=ip; ihi=ip
    while ilo>0 and hist.g_rec[ilo]>half: ilo-=1
    while ihi<len(hist.g_rec)-1 and hist.g_rec[ihi]>half: ihi+=1
    sig_rec=abs(float(hist.chi[ilo]-hist.chi[ihi]))/2.354820045
    rs=float(np.trapezoid((1/np.sqrt(3*(1+3*P.omega_b0*hist.a/(4*(P.omega_r0/(1+0.2271*P.n_eff))))))/hist.Hc*(hist.N<=hist.N[np.argmax(hist.g_rec)]),hist.N))
    # Early sources are attenuated by late rescattering.
    att=math.exp(-P.tau_reio)
    tr=np.exp(-0.5*(kd*sig_rec)**2); tre=np.exp(-0.5*(kd*sig_re)**2)
    xrec=kd*chi_rec; xre=kd*chi_re; dchi=chi_rec-chi_re
    theta0=AT*spherical_jn(0,kd*dchi)+AV*spherical_jn(0,kd*dchi,derivative=True)
    theta2=AT*spherical_jn(2,kd*dchi)+AV*spherical_jn(2,kd*dchi,derivative=True)
    Pi=4*theta2
    psi_re=0.6*transfer_simple(kd)
    are=1/(1+hist.z_re); Hcre=are*math.sqrt(float(e2(are)))
    theta_over_k=-(2/5)*Hcre*are*kd/omega_m0*transfer_simple(kd)
    LT=gre_int*(theta0+psi_re+Pi/16); LV=gre_int*theta_over_k; LE=3*gre_int*Pi/16

    # Late ISW transfer on a low-k subset.
    gh=growth_history(hist); Ni=gh['N']; ai=gh['a']; gN=gh['gN']
    chi_i=np.interp(Ni,hist.N,hist.chi); tau_i=np.interp(Ni,hist.N,hist.tau)
    kisw=np.unique(np.concatenate([np.geomspace(kmin,1.5,180,endpoint=False),np.linspace(1.5,140,420)]))
    Tisw=transfer_simple(kisw)
    sisw=2*np.exp(-np.minimum(tau_i,700))[:,None]*(0.6*gN[:,None]*Tisw[None,:])

    if selected_only is None:
        parts=[np.arange(2,min(51,ell_max+1))]
        if ell_max>=52: parts.append(np.arange(52,min(302,ell_max+1),6))
        if ell_max>=306: parts.append(np.arange(306,min(1202,ell_max+1),12))
        if ell_max>=1210: parts.append(np.arange(1210,ell_max+1,24))
        ells=np.unique(np.concatenate(parts)).astype(int)
    else: ells=np.unique(np.asarray(selected_only,dtype=int))
    ctt=np.zeros(len(ells));cee=np.zeros(len(ells));cte=np.zeros(len(ells));ctt0=np.zeros(len(ells));cee0=np.zeros(len(ells));cte0=np.zeros(len(ells))
    trans=[]
    for off in range(0,len(ells),24):
        es=ells[off:off+24]
        jr=spherical_jn(es[:,None],xrec[None,:]); jpr=spherical_jn(es[:,None],xrec[None,:],derivative=True)
        je=spherical_jn(es[:,None],xre[None,:]); jpe=spherical_jn(es[:,None],xre[None,:],derivative=True)
        pref=np.sqrt((es+2)*(es+1)*es*(es-1)).astype(float)
        dt0=att*tr[None,:]*(AT[None,:]*jr+AV[None,:]*jpr)
        de0=att*tr[None,:]*pref[:,None]*AE[None,:]*jr/np.maximum(xrec[None,:]**2,1e-300)
        dtr=tre[None,:]*(LT[None,:]*je+LV[None,:]*jpe)
        der=tre[None,:]*pref[:,None]*LE[None,:]*je/np.maximum(xre[None,:]**2,1e-300)
        for j,ell in enumerate(es):
            disw=np.zeros_like(kd)
            if ell<=90:
                jj=spherical_jn(int(ell),kisw[:,None]*chi_i[None,:])
                val=np.trapezoid(sisw.T*jj,Ni,axis=1)
                disw=np.interp(kd,kisw,val,left=val[0],right=0)
            dt=dt0[j]+dtr[j]+disw; de=de0[j]+der[j]
            i=off+j
            ctt[i]=4*math.pi*np.trapezoid(PR*dt*dt,lnk); cee[i]=4*math.pi*np.trapezoid(PR*de*de,lnk); cte[i]=4*math.pi*np.trapezoid(PR*dt*de,lnk)
            ctt0[i]=4*math.pi*np.trapezoid(PR*dt0[j]*dt0[j],lnk); cee0[i]=4*math.pi*np.trapezoid(PR*de0[j]*de0[j],lnk); cte0[i]=4*math.pi*np.trapezoid(PR*dt0[j]*de0[j],lnk)
            if int(ell) in {2,5,10,20,50,100,200,500,1000,1500,2000,2500}:
                st=max(1,len(kd)//100)
                for kk,tt,eev in zip(kd[::st],dt[::st],de[::st]): trans.append({'ell':int(ell),'k_over_H0':float(kk),'Delta_T':float(tt),'Delta_E':float(eev)})
    fac=ells*(ells+1)/(2*math.pi)*(P.t_cmb*1e6)**2
    df=pd.DataFrame({'ell':ells,'C_TT':ctt,'C_EE':cee,'C_TE':cte,'D_TT_uK2':fac*ctt,'D_EE_uK2':fac*cee,'D_TE_uK2':fac*cte})
    ctrl=pd.DataFrame({'ell':ells,'C_TT':ctt0,'C_EE':cee0,'C_TE':cte0,'D_TT_uK2':fac*ctt0,'D_EE_uK2':fac*cee0,'D_TE_uK2':fac*cte0})
    mask=df.ell>=150; vals=df.loc[mask,'D_TT_uK2'].to_numpy(); rows=np.flatnonzero(mask); pi,_=find_peaks(vals,distance=15,prominence=max(vals.max()*0.002,1e-30)); prow=rows[pi]
    pell=df.iloc[prow].ell.to_numpy(int); pval=df.iloc[prow].D_TT_uK2.to_numpy()
    info={'z_rec':float(hist.z[np.argmax(hist.g_rec)]),'z_re_mid':hist.z_re,'z_re_peak':float(hist.z[np.argmax(hist.g_re)]),'tau_reio':hist.tau_reio_actual,'vis_integral':float(np.trapezoid(hist.g,hist.N)),'chi_rec':chi_rec,'sigma_rec':sig_rec,'sigma_rec_rms':sig_rec_rms,'chi_re':chi_re,'sigma_re':sig_re,'sound_horizon_H0inv':rs,'ell_A':math.pi*chi_rec/rs,'first_peak_ell':float(pell[0]) if len(pell) else float('nan'),'second_peak_ell':float(pell[1]) if len(pell)>1 else float('nan'),'third_peak_ell':float(pell[2]) if len(pell)>2 else float('nan'),'first_peak_DTT':float(pval[0]) if len(pval) else float('nan'),'te_cauchy_max':float(np.max(np.abs(cte)/np.sqrt(np.maximum(ctt*cee,1e-300)))),'k_grid_points':len(kd)}
    return df,ctrl,info,pd.DataFrame(trans)


def sample(df:pd.DataFrame,ell:int,col:str)->float:
    return float(df.iloc[np.argmin(np.abs(df.ell.to_numpy()-ell))][col])


def main(kpoints:int=3000, suffix:str=''):
    hist=ThermalHistory(); src=pd.read_csv(DATA/'primary_cmb_sources.csv')
    spectra,ctrl,info,transfer=project_spectra(hist,src,kpoints=kpoints)
    spectra.to_csv(DATA/f'thermal_reionization_los_spectra{suffix}.csv',index=False); ctrl.to_csv(DATA/f'early_only_control{suffix}.csv',index=False); transfer.to_csv(DATA/f'los_transfer_samples{suffix}.csv',index=False)
    pd.DataFrame({'N':hist.N,'a':hist.a,'z':hist.z,'xH':hist.xH,'xe_recombination':hist.xe_rec,'xe_total':hist.xe,'tau':hist.tau,'visibility':hist.g,'visibility_recombination':hist.g_rec,'visibility_reionization':hist.g_re}).to_csv(DATA/f'effective_thermal_history{suffix}.csv',index=False)
    masses=np.array([2e-4,4e-4,8e-4,1.6e-3,3.2e-3,6.4e-3,1.28e-2])
    match=production_matching(masses); match.to_csv(DATA/f'production_surface_matching{suffix}.csv',index=False)
    checks=[]
    def add(cid,stmt,val,thr,mode='le'):
        ok=(abs(val)<=thr if mode=='le' else val>=thr if mode=='ge' else 0<=val<=thr)
        checks.append({'id':cid,'statement':stmt,'value':float(val),'threshold':float(thr),'status':'PASS' if ok else 'FAIL'})
    high=(hist.z>=1600)&(hist.z<=2200); saha_err=float(np.max(np.abs(hist.xH[high]-saha_hydrogen(hist.a[high]))))
    add('TRL01','hydrogen ionization remains bounded',max(hist.xH.max()-1,-hist.xH.min(),0),1e-12)
    add('TRL02','pre-freezeout solution matches Saha',saha_err,0.012)
    add('TRL03','visibility normalizes to unity',abs(info['vis_integral']-1),2e-3)
    add('TRL04','recombination peak is physical',info['z_rec'],900,'ge')
    add('TRL05','reionization optical depth matches target',abs(info['tau_reio']-P.tau_reio),2e-6)
    add('TRL06','reionization midpoint is physical',info['z_re_mid'],5,'ge')
    add('TRL07','reionization visibility peak is low redshift',info['z_re_peak'],20,'between')
    add('TRL08','TT spectrum nonnegative',max(-spectra.C_TT.min(),0),1e-20)
    add('TRL09','EE spectrum nonnegative',max(-spectra.C_EE.min(),0),1e-20)
    add('TRL10','TE obeys Cauchy inequality',max(info['te_cauchy_max']-1,0),2e-7)
    ee_ratio=sample(spectra,5,'D_EE_uK2')/max(sample(ctrl,5,'D_EE_uK2'),1e-30)
    tt_change=abs(sample(spectra,10,'D_TT_uK2')/max(sample(ctrl,10,'D_TT_uK2'),1e-30)-1)
    acoustic=sample(spectra,500,'D_TT_uK2')/max(sample(ctrl,500,'D_TT_uK2'),1e-30)
    add('TRL11','reionization creates low-ell EE enhancement',ee_ratio,1.05,'ge')
    add('TRL12','late sources change low-ell TT',tt_change,0.01,'ge')
    add('TRL13','late sources preserve acoustic TT',acoustic,0.7,'ge')
    add('TRL14','first acoustic peak resolved',info['first_peak_ell'],80,'ge')
    add('TRL15','single-clock matching has zero relative entropy',match.single_clock_relative_entropy.abs().max(),1e-15)
    add('TRL16','independent modulation response is nonzero',match.dln_n_dln_A_independent.min(),1,'ge')
    add('TRL17','all spectra finite',float(np.all(np.isfinite(spectra[['C_TT','C_EE','C_TE']]))),1,'ge')
    add('TRL18','sound horizon is positive',info['sound_horizon_H0inv'],0,'ge')
    add('TRL19','effective acoustic ruler is finite',float(np.isfinite(info['ell_A'])),1,'ge')
    add('TRL20','residual hydrogen fraction positive',hist.residual_xH,0,'ge')
    cdf=pd.DataFrame(checks); cdf.to_csv(DATA/f'thermal_reionization_los_checks{suffix}.csv',index=False)
    selected=[]
    for l in [2,5,10,20,50,100,200,int(info['first_peak_ell']),500,int(info['second_peak_ell']),int(info['third_peak_ell']),1000,1500,2000,2500]:
        i=int(np.argmin(abs(spectra.ell-l))); r=spectra.iloc[i].to_dict(); r['control_D_TT_uK2']=sample(ctrl,int(r['ell']),'D_TT_uK2');r['control_D_EE_uK2']=sample(ctrl,int(r['ell']),'D_EE_uK2');selected.append(r)
    pd.DataFrame(selected).drop_duplicates('ell').to_csv(DATA/f'selected_spectra{suffix}.csv',index=False)
    summary={**asdict(P),**info,'residual_hydrogen_fraction':hist.residual_xH,'low_ell_EE_enhancement':ee_ratio,'low_ell_TT_fractional_change':tt_change,'acoustic_TT_ratio':acoustic,'pass_count':int((cdf.status=='PASS').sum()),'fail_count':int((cdf.status=='FAIL').sum()),'checks':checks}
    (DATA/f'Thermal_Reionization_LOS_Verification{suffix}.json').write_text(json.dumps(summary,indent=2))
    if suffix=='':
        # Figures.
        m=(hist.z>=500)&(hist.z<=2200); plt.figure(figsize=(8.2,4.7));plt.plot(hist.z[m],hist.g_rec[m]);plt.gca().invert_xaxis();plt.xlabel('redshift z');plt.ylabel('visibility per d ln a');plt.tight_layout();plt.savefig(FIG/'effective_recombination_visibility.png',dpi=190);plt.close()
        m=hist.z<=30;plt.figure(figsize=(8.2,4.7));plt.plot(hist.z[m],hist.g_re[m]);plt.gca().invert_xaxis();plt.xlabel('redshift z');plt.ylabel('reionization visibility');plt.tight_layout();plt.savefig(FIG/'reionization_visibility.png',dpi=190);plt.close()
        plt.figure(figsize=(8.2,4.7));plt.semilogx(1+hist.z,hist.xe,label='total');plt.semilogx(1+hist.z,hist.xe_rec,label='without reionization');plt.xlabel('1+z');plt.ylabel('electrons per H nucleus');plt.legend();plt.tight_layout();plt.savefig(FIG/'effective_ionization_history.png',dpi=190);plt.close()
        plt.figure(figsize=(8.6,5.0));plt.semilogy(spectra.ell,np.maximum(spectra.D_TT_uK2,1e-8),label='TT');plt.semilogy(spectra.ell,np.maximum(spectra.D_EE_uK2,1e-8),label='EE');plt.xlabel('multipole ell');plt.ylabel('D_ell [microK^2]');plt.legend();plt.tight_layout();plt.savefig(FIG/'thermal_reionization_tt_ee.png',dpi=200);plt.close()
        low=spectra.ell<=60;lowc=ctrl.ell<=60;plt.figure(figsize=(8.6,5));plt.semilogy(spectra.loc[low,'ell'],np.maximum(spectra.loc[low,'D_EE_uK2'],1e-12),label='with reionization');plt.semilogy(ctrl.loc[lowc,'ell'],np.maximum(ctrl.loc[lowc,'D_EE_uK2'],1e-12),label='early only');plt.xlabel('multipole ell');plt.ylabel('D_ell^EE [microK^2]');plt.legend();plt.tight_layout();plt.savefig(FIG/'low_ell_ee_bump.png',dpi=200);plt.close()
        plt.figure(figsize=(8.6,5));plt.plot(spectra.ell,spectra.D_TE_uK2);plt.axhline(0,color='black',lw=.7);plt.xlabel('multipole ell');plt.ylabel('D_ell^TE [microK^2]');plt.tight_layout();plt.savefig(FIG/'thermal_reionization_te.png',dpi=200);plt.close()
    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},indent=2))

if __name__=='__main__': main()
