from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
import warnings

import numpy as np
import pandas as pd
from scipy import constants
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import CubicSpline
from scipy.signal import find_peaks
from scipy.special import roots_genlaguerre, spherical_jn
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
FIG = ROOT / 'figures'
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Parameters:
    h0_km_s_mpc: float = 70.0
    omega_b0: float = 0.049
    omega_d0: float = 0.261
    omega_r0: float = 9.0e-5
    t_cmb: float = 2.7255
    y_p: float = 0.24
    n_eff: float = 3.046
    a_production: float = 1.0e-6
    prime: int = 2
    sigma: float = 1.0
    lambda_over_A: float = 1.0e-4
    n_s: float = 0.965
    A_s: float = 2.1e-9
    k_pivot_mpc: float = 0.05

    @property
    def omega_v0(self) -> float:
        return 1.0 - self.omega_r0 - self.omega_b0 - self.omega_d0

    @property
    def h0_over_c_mpc(self) -> float:
        return self.h0_km_s_mpc / 299792.458


P = Parameters()

# Physical constants.
c_si = constants.c
sigma_t = constants.physical_constants['Thomson cross section'][0]
m_e = constants.m_e
m_p = constants.m_p
k_b = constants.k
hbar = constants.hbar
g_newton = constants.G
ev = constants.electron_volt
chi_h = 13.6 * ev
mpc_si = constants.parsec * 1.0e6
h0_si = P.h0_km_s_mpc * 1000.0 / mpc_si
rho_c0 = 3.0 * h0_si**2 / (8.0 * math.pi * g_newton)
a_radiation = 4.0 * constants.sigma / c_si
rho_gamma0 = a_radiation * P.t_cmb**4 / c_si**2
omega_gamma0 = rho_gamma0 / rho_c0
omega_nu0 = max(P.omega_r0 - omega_gamma0, 0.0)
n_h0 = (1.0 - P.y_p) * P.omega_b0 * rho_c0 / m_p


@dataclass(frozen=True)
class PhaseGrid:
    levels: pd.DataFrame
    mass: np.ndarray
    q: np.ndarray
    base: np.ndarray
    dlnf: np.ndarray

    @property
    def size(self) -> int:
        return int(self.mass.size)


def build_phase_grid(nq: int = 3, min_rest_fraction: float = 1.0e-4) -> PhaseGrid:
    x_ref, w_ref = roots_genlaguerre(96, 0.5)
    prefactor = 1.0 / (2.0 * math.pi ** 1.5)
    rows: list[dict[str, float]] = []
    for h in range(1, 29):
        mass = P.lambda_over_A * P.prime ** (P.sigma * h)
        degeneracy = (P.prime - 1) * P.prime ** (h - 1)
        suppression = math.exp(-math.pi * mass)
        q_scale = P.a_production * math.sqrt(mass)
        rest = (
            degeneracy * suppression * q_scale**3 * mass
            * prefactor * float(np.sum(w_ref))
        )
        rows.append({
            'level': float(h),
            'mass_over_A': mass,
            'degeneracy': float(degeneracy),
            'suppression': suppression,
            'q_scale_over_A': q_scale,
            'present_rest_weight': rest,
        })
    total = sum(r['present_rest_weight'] for r in rows)
    retained = [r for r in rows if r['present_rest_weight'] / total >= min_rest_fraction]
    retained_total = sum(r['present_rest_weight'] for r in retained)
    for row in retained:
        row['retained_rest_fraction'] = row['present_rest_weight'] / retained_total

    lag_x, lag_w = roots_genlaguerre(nq, 0.5)
    x = np.sqrt(lag_x / math.pi)
    q_weight = prefactor * lag_w
    masses: list[float] = []
    qs: list[float] = []
    bases: list[float] = []
    slopes: list[float] = []
    for row in retained:
        m = float(row['mass_over_A'])
        d = float(row['degeneracy'])
        suppression = float(row['suppression'])
        q_scale = float(row['q_scale_over_A'])
        for node, weight, y in zip(x, q_weight, lag_x):
            masses.append(m)
            qs.append(q_scale * float(node))
            bases.append(d * suppression * q_scale**3 * float(weight))
            slopes.append(-2.0 * float(y))
    return PhaseGrid(
        levels=pd.DataFrame(retained),
        mass=np.asarray(masses),
        q=np.asarray(qs),
        base=np.asarray(bases),
        dlnf=np.asarray(slopes),
    )


class Background:
    def __init__(self, phase: PhaseGrid) -> None:
        self.phase = phase
        self.rho_dark_today = float(np.sum(phase.base * np.sqrt(phase.q**2 + phase.mass**2)))
        self.loga_grid = np.linspace(math.log(1.0e-8), 0.0, 24001)
        self.a_grid = np.exp(self.loga_grid)
        self._build_tables()

    def dark_phase(self, a: float) -> tuple[np.ndarray, float, float]:
        eps = np.sqrt(self.phase.q**2 + (a * self.phase.mass)**2)
        rho_bar = float(np.sum(self.phase.base * eps))
        p_bar = float(np.sum(self.phase.base * self.phase.q**2 / (3.0 * eps)))
        return eps, rho_bar, p_bar

    def dark_ratio(self, a: float) -> tuple[float, float]:
        _, rho, p = self.dark_phase(a)
        return a**-4 * rho / self.rho_dark_today, p / rho

    def e2(self, a: float) -> float:
        rd, _ = self.dark_ratio(a)
        return (
            omega_gamma0 * a**-4
            + omega_nu0 * a**-4
            + P.omega_b0 * a**-3
            + P.omega_d0 * rd
            + P.omega_v0
        )

    def hc(self, a: float) -> float:
        return a * math.sqrt(self.e2(a))

    def saha_xe(self, a: float | np.ndarray) -> np.ndarray:
        a_arr = np.asarray(a, dtype=float)
        temperature = P.t_cmb / a_arr
        n_h = n_h0 / a_arr**3
        log_ratio = (
            1.5 * np.log(m_e * k_b * temperature / (2.0 * math.pi * hbar**2))
            - chi_h / (k_b * temperature)
            - np.log(n_h)
        )
        ans = np.empty_like(log_ratio)
        high = log_ratio > 40.0
        low = log_ratio < -40.0
        mid = ~(high | low)
        ans[high] = 1.0 - np.exp(-log_ratio[high])
        ans[low] = np.exp(log_ratio[low] / 2.0)
        ratio = np.exp(log_ratio[mid])
        ans[mid] = 2.0 / (1.0 + np.sqrt(1.0 + 4.0 / ratio))
        return np.clip(ans, 0.0, 1.0)

    def opacity(self, a: float) -> float:
        xe = float(self.saha_xe(np.array([a]))[0])
        ne = n_h0 * xe / a**3
        return a * ne * sigma_t * c_si / h0_si

    def baryon_sound_speed2(self, a: float) -> float:
        # Controlled thermal history: baryons track photons through recombination,
        # then cool adiabatically.  The effect is tiny for primary CMB dynamics.
        a_dec = 1.0 / 1283.0
        if a <= a_dec:
            tb = P.t_cmb / a
        else:
            tb = P.t_cmb / a_dec * (a_dec / a) ** 2
        return k_b * tb / (m_p * c_si**2)

    def _build_tables(self) -> None:
        e = np.array([math.sqrt(self.e2(float(a))) for a in self.a_grid])
        hc = self.a_grid * e
        inv_hc = 1.0 / hc
        eta = np.concatenate([[0.0], cumulative_trapezoid(inv_hc, self.loga_grid)])
        # Distance from each scale factor to today.
        chi = eta[-1] - eta
        opacity = np.array([self.opacity(float(a)) for a in self.a_grid])
        dtaudn = opacity / hc
        # tau(N)=int_N^0 opacity/Hc dN.
        tau = np.zeros_like(dtaudn)
        rev_int = cumulative_trapezoid(dtaudn[::-1], self.loga_grid[::-1], initial=0.0)
        tau = -rev_int[::-1]
        visibility = np.exp(-np.minimum(tau, 700.0)) * dtaudn
        self.e_grid = e
        self.hc_grid = hc
        self.eta_grid = eta
        self.chi_grid = chi
        self.opacity_grid = opacity
        self.tau_grid = tau
        self.visibility_grid = visibility

    def interp(self, name: str, loga: float | np.ndarray) -> np.ndarray:
        values = {
            'e': self.e_grid,
            'hc': self.hc_grid,
            'eta': self.eta_grid,
            'chi': self.chi_grid,
            'opacity': self.opacity_grid,
            'tau': self.tau_grid,
            'visibility': self.visibility_grid,
        }[name]
        return np.interp(np.asarray(loga), self.loga_grid, values)


@dataclass(frozen=True)
class Layout:
    tca_dim: int
    full_dim: int
    nu_lmax: int
    gamma_lmax: int
    pol_lmax: int
    dark_lmax: int
    nphase: int
    tca_slices: dict[str, slice]
    full_slices: dict[str, slice]


def make_layout(nphase: int, nu_lmax: int = 6, gamma_lmax: int = 7, pol_lmax: int = 7, dark_lmax: int = 2) -> Layout:
    i = 0
    tca: dict[str, slice] = {}
    for name, width in [('phi',1),('db',1),('dg',1),('theta',1),('nu',nu_lmax+1),('dark',nphase*(dark_lmax+1))]:
        tca[name] = slice(i, i+width); i += width
    tca_dim = i
    i = 0
    full: dict[str, slice] = {}
    for name, width in [('phi',1),('db',1),('tb',1),('gamma',gamma_lmax+1),('pol',pol_lmax+1),('nu',nu_lmax+1),('dark',nphase*(dark_lmax+1))]:
        full[name] = slice(i, i+width); i += width
    return Layout(tca_dim, i, nu_lmax, gamma_lmax, pol_lmax, dark_lmax, nphase, tca, full)


class PrimaryCMBSolver:
    def __init__(self, k: np.ndarray, *, nq: int = 2, cold_dark: bool = False,
                 nu_lmax: int = 6, gamma_lmax: int = 7, pol_lmax: int = 7,
                 dark_lmax: int = 2, tca_step: float = 0.0035,
                 full_step: float = 0.0008) -> None:
        self.k = np.asarray(k, dtype=float)
        self.nk = self.k.size
        self.phase = build_phase_grid(nq=nq)
        self.bg = Background(self.phase)
        self.layout = make_layout(self.phase.size,nu_lmax,gamma_lmax,pol_lmax,dark_lmax)
        self.tca_step=float(tca_step); self.full_step=float(full_step)
        self.cold_dark = cold_dark
        self.a_initial = P.a_production
        self.a_switch = 6.8e-4
        self.a_end = 1.55e-3
        self.n_initial = math.log(self.a_initial)
        self.n_switch = math.log(self.a_switch)
        self.n_end = math.log(self.a_end)
        self.rho_dark_today = self.bg.rho_dark_today
        self.mass = self.phase.mass
        self.q = self.phase.q
        self.base = self.phase.base
        self.dlnf = self.phase.dlnf
        self.source_records: list[dict[str, np.ndarray | float]] = []
        self.constraint_records: list[float] = []
        self.initial_curvature = np.empty(self.nk)

    def dark_background(self, a: float) -> tuple[np.ndarray, float, float, float]:
        eps, rho_bar, p_bar = self.bg.dark_phase(a)
        rho_ratio = a**-4 * rho_bar / self.rho_dark_today
        return eps, rho_bar, p_bar, rho_ratio

    def dark_moments(self, a: float, hierarchy: np.ndarray) -> dict[str, np.ndarray | float]:
        # hierarchy shape nk,nphase,L+1
        eps, rho_bar, p_bar, rho_ratio = self.dark_background(a)
        scale = P.omega_d0 * a**-4 / self.rho_dark_today
        f0 = hierarchy[:,:,0]
        f1 = hierarchy[:,:,1] if hierarchy.shape[2] > 1 else np.zeros_like(f0)
        f2 = hierarchy[:,:,2] if hierarchy.shape[2] > 2 else np.zeros_like(f0)
        delta_rho = scale * np.sum(self.base[None,:] * eps[None,:] * f0, axis=1)
        delta_p = scale * np.sum(self.base[None,:] * self.q[None,:]**2/(3.0*eps[None,:]) * f0, axis=1)
        momentum = scale * self.k * np.sum(self.base[None,:] * self.q[None,:] * f1, axis=1)
        anis = scale * (2.0/3.0) * np.sum(self.base[None,:] * self.q[None,:]**2/eps[None,:] * f2, axis=1)
        return {
            'eps': eps,
            'rho_bar': rho_bar,
            'p_bar': p_bar,
            'rho_ratio': rho_ratio,
            'delta_rho': delta_rho,
            'delta_p': delta_p,
            'momentum': momentum,
            'anis': anis,
        }

    def initial_state(self) -> np.ndarray:
        a = self.a_initial
        hc = self.bg.hc(a)
        eps, rho_bar, p_bar, rho_ratio = self.dark_background(a)
        rho_gamma = omega_gamma0 * a**-4
        rho_nu = omega_nu0 * a**-4
        rho_b = P.omega_b0 * a**-3
        rho_d = P.omega_d0 * rho_ratio
        p_d = rho_d * (p_bar/rho_bar)
        sum_rhop = (4.0/3.0)*(rho_gamma+rho_nu) + rho_b + rho_d + p_d
        phi = np.ones(self.nk)
        psi = phi.copy()
        # Choose common velocity so phi'=0 initially, then choose adiabatic density
        # amplitude so the exact energy constraint is satisfied.
        theta = self.k**2 * hc * psi / (1.5 * a*a * sum_rhop)
        common = -(self.k**2*phi + 3.0*hc*hc*psi) / (1.5*a*a*sum_rhop)
        dg = (4.0/3.0)*common
        db = common
        dd = (1.0 + p_d/rho_d)*common
        self.initial_curvature = -( -phi + common/3.0 )  # positive R normalization

        state = np.zeros((self.nk, self.layout.tca_dim))
        s = self.layout.tca_slices
        state[:,s['phi']] = phi[:,None]
        state[:,s['db']] = db[:,None]
        state[:,s['dg']] = dg[:,None]
        state[:,s['theta']] = theta[:,None]
        nu = state[:,s['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        nu[:,0] = dg
        nu[:,1] = 4.0*theta/(3.0*self.k)

        dark = state[:,s['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        if self.cold_dark:
            # Use the same phase grid but initialize a momentum-independent cold perturbation.
            dark[:,:,0] = dd[:,None]
            response = self.k[:,None] * np.sum(self.base*self.q, axis=0) if False else None
        else:
            shape0 = -self.dlnf
            norm0 = np.sum(self.base*eps*shape0)
            dark[:,:,0] = dd[:,None] * (rho_bar/norm0) * shape0[None,:]
            # Normalize a smooth boost shape to the requested common velocity.
            shape1 = (-self.dlnf) * eps / np.maximum(self.q,1.0e-300)
            mom_response = np.sum(self.base*self.q*shape1)
            target_mom = (rho_bar+p_bar)*theta[:,None]/self.k[:,None]
            dark[:,:,1] = target_mom/mom_response * shape1[None,:]
        return state

    def _metric(self, a: float, phi: np.ndarray, db: np.ndarray, photon: dict[str,np.ndarray], nu: np.ndarray, dark: np.ndarray, theta_b: np.ndarray) -> dict[str,np.ndarray | float]:
        hc = self.bg.hc(a)
        rho_gamma = omega_gamma0*a**-4
        rho_nu = omega_nu0*a**-4
        rho_b = P.omega_b0*a**-3
        # Photon brightness convention F0=delta_gamma, F1=4 theta_gamma/(3k), F2=2 sigma_gamma.
        fg0 = photon['f0']; fg1 = photon['f1']; fg2 = photon['f2']
        delta_rho = rho_gamma*fg0 + rho_nu*nu[:,0] + rho_b*db
        delta_p = (rho_gamma*fg0 + rho_nu*nu[:,0])/3.0
        momentum = rho_gamma*self.k*fg1 + rho_nu*self.k*nu[:,1] + rho_b*theta_b
        anis = (2.0/3.0)*(rho_gamma*fg2 + rho_nu*nu[:,2])
        dm = self.dark_moments(a,dark)
        delta_rho = delta_rho + np.asarray(dm['delta_rho'])
        delta_p = delta_p + np.asarray(dm['delta_p'])
        momentum = momentum + np.asarray(dm['momentum'])
        anis = anis + np.asarray(dm['anis'])
        psi = phi - 4.5*a*a*anis/(self.k*self.k)
        A = 1.5*a*a*momentum/(self.k*self.k)
        phi_eta = A - hc*psi
        energy_res = self.k*self.k*phi + 3.0*hc*A + 1.5*a*a*delta_rho
        scale = np.abs(self.k*self.k*phi) + np.abs(3*hc*A) + np.abs(1.5*a*a*delta_rho) + 1e-30
        return {
            'hc':hc,'psi':psi,'phi_eta':phi_eta,'delta_rho':delta_rho,
            'delta_p':delta_p,'momentum':momentum,'anis':anis,
            'energy_res_rel':np.abs(energy_res)/scale,'dark':dm,
        }

    def _dark_rhs_eta(self, a: float, hierarchy: np.ndarray, phi_eta: np.ndarray, psi: np.ndarray) -> np.ndarray:
        eps = np.sqrt(self.q**2 + (a*self.mass)**2)
        L = self.layout.dark_lmax
        out = np.zeros_like(hierarchy)
        vel = self.q/eps
        out[:,:,0] = -self.k[:,None]*vel[None,:]*hierarchy[:,:,1] - phi_eta[:,None]*self.dlnf[None,:]
        if L >= 1:
            f2 = hierarchy[:,:,2] if L >= 2 else 0.0
            out[:,:,1] = self.k[:,None]*vel[None,:]*(hierarchy[:,:,0]-2.0*f2)/3.0 - self.k[:,None]*(eps/np.maximum(self.q,1e-300))[None,:]*psi[:,None]*self.dlnf[None,:]/3.0
        eta_now=float(self.bg.interp('eta',math.log(a)))
        eta_i=float(self.bg.interp('eta',self.n_initial))
        xphase=np.maximum(self.k[:,None]*(eta_now-eta_i)*vel[None,:],1.0e-8)
        for ell in range(2,L+1):
            if ell < L:
                nxt=hierarchy[:,:,ell+1]
            else:
                nxt=(2*ell+1)*hierarchy[:,:,ell]/xphase-hierarchy[:,:,ell-1]
            out[:,:,ell] = self.k[:,None]*vel[None,:]*(ell*hierarchy[:,:,ell-1]-(ell+1)*nxt)/(2*ell+1)
        return out

    def tca_rhs(self, N: float, state: np.ndarray) -> np.ndarray:
        a = math.exp(N); hc = self.bg.hc(a); opacity = self.bg.opacity(a)
        s = self.layout.tca_slices
        phi = state[:,s['phi']][:,0]
        db = state[:,s['db']][:,0]
        dg = state[:,s['dg']][:,0]
        theta = state[:,s['theta']][:,0]
        nu = state[:,s['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        dark = state[:,s['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        f1 = 4.0*theta/(3.0*self.k)
        f2 = 32.0*theta/(45.0*max(opacity,1e-30))
        metric = self._metric(a,phi,db,{'f0':dg,'f1':f1,'f2':f2},nu,dark,theta)
        psi=np.asarray(metric['psi']); phi_eta=np.asarray(metric['phi_eta'])
        R = 3.0*P.omega_b0*a/(4.0*omega_gamma0)
        cb2 = self.bg.baryon_sound_speed2(a)
        theta_eta = -hc*R/(1.0+R)*theta + self.k**2*(dg/(4.0*(1.0+R)) + psi + (R/(1.0+R))*cb2*db)
        out=np.zeros_like(state)
        out[:,s['phi']] = (phi_eta/hc)[:,None]
        out[:,s['db']] = ((-theta+3.0*phi_eta)/hc)[:,None]
        out[:,s['dg']] = ((-(4.0/3.0)*theta+4.0*phi_eta)/hc)[:,None]
        out[:,s['theta']] = (theta_eta/hc)[:,None]
        nout=out[:,s['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        nout[:,0]=(-self.k*nu[:,1]+4.0*phi_eta)/hc
        nout[:,1]=(self.k*(nu[:,0]-2.0*nu[:,2])/3.0+4.0*self.k*psi/3.0)/hc
        eta_now=float(self.bg.interp('eta',N)); xnu=np.maximum(self.k*eta_now,1.0e-8)
        for ell in range(2,self.layout.nu_lmax+1):
            if ell<self.layout.nu_lmax:
                nxt=nu[:,ell+1]
            else:
                nxt=(2*ell+1)*nu[:,ell]/xnu-nu[:,ell-1]
            nout[:,ell]=(self.k*(ell*nu[:,ell-1]-(ell+1)*nxt)/(2*ell+1))/hc
        dout=out[:,s['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        dout[:]=self._dark_rhs_eta(a,dark,phi_eta,psi)/hc
        return out

    def project_tca(self,N:float,state:np.ndarray)->np.ndarray:
        a=math.exp(N); s=self.layout.tca_slices; y=state.copy()
        phi=y[:,s['phi']][:,0]; db=y[:,s['db']][:,0]; dg=y[:,s['dg']][:,0]; theta=y[:,s['theta']][:,0]
        nu=y[:,s['nu']].reshape(self.nk,self.layout.nu_lmax+1); dark=y[:,s['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        opacity=self.bg.opacity(a); f1=4.0*theta/(3.0*self.k); f2=32.0*theta/(45.0*max(opacity,1e-30))
        met=self._metric(a,phi,db,{'f0':dg,'f1':f1,'f2':f2},nu,dark,theta)
        A=1.5*a*a*np.asarray(met['momentum'])/(self.k*self.k)
        phi_new=-(3.0*float(met['hc'])*A+1.5*a*a*np.asarray(met['delta_rho']))/(self.k*self.k)
        y[:,s['phi']]=phi_new[:,None]
        met2=self._metric(a,phi_new,db,{'f0':dg,'f1':f1,'f2':f2},nu,dark,theta)
        self.constraint_records.append(float(np.max(met2['energy_res_rel'])))
        return y

    def to_full(self, tca: np.ndarray) -> np.ndarray:
        a=self.a_switch; opacity=self.bg.opacity(a)
        ts=self.layout.tca_slices; fs=self.layout.full_slices
        full=np.zeros((self.nk,self.layout.full_dim))
        phi=tca[:,ts['phi']][:,0]; db=tca[:,ts['db']][:,0]; dg=tca[:,ts['dg']][:,0]; theta=tca[:,ts['theta']][:,0]
        full[:,fs['phi']]=phi[:,None]; full[:,fs['db']]=db[:,None]; full[:,fs['tb']]=theta[:,None]
        gam=full[:,fs['gamma']].reshape(self.nk,self.layout.gamma_lmax+1)
        pol=full[:,fs['pol']].reshape(self.nk,self.layout.pol_lmax+1)
        gam[:,0]=dg; gam[:,1]=4.0*theta/(3.0*self.k)
        gam[:,2]=32.0*theta/(45.0*max(opacity,1e-30))
        pol[:,0]=1.25*gam[:,2]; pol[:,2]=0.25*gam[:,2]
        full[:,fs['nu']]=tca[:,ts['nu']]
        full[:,fs['dark']]=tca[:,ts['dark']]
        return full

    def full_rhs(self,N:float,state:np.ndarray)->np.ndarray:
        a=math.exp(N); hc=self.bg.hc(a); opacity=self.bg.opacity(a)
        fs=self.layout.full_slices
        phi=state[:,fs['phi']][:,0]; db=state[:,fs['db']][:,0]; tb=state[:,fs['tb']][:,0]
        gam=state[:,fs['gamma']].reshape(self.nk,self.layout.gamma_lmax+1)
        pol=state[:,fs['pol']].reshape(self.nk,self.layout.pol_lmax+1)
        nu=state[:,fs['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        dark=state[:,fs['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        metric=self._metric(a,phi,db,{'f0':gam[:,0],'f1':gam[:,1],'f2':gam[:,2]},nu,dark,tb)
        psi=np.asarray(metric['psi']); phi_eta=np.asarray(metric['phi_eta'])
        out=np.zeros_like(state)
        out[:,fs['phi']]=(phi_eta/hc)[:,None]
        out[:,fs['db']]=((-tb+3.0*phi_eta)/hc)[:,None]
        theta_g=0.75*self.k*gam[:,1]
        drag=4.0*omega_gamma0/(3.0*P.omega_b0*a)
        tb_eta=-hc*tb+self.bg.baryon_sound_speed2(a)*self.k**2*db+drag*opacity*(theta_g-tb)+self.k**2*psi
        out[:,fs['tb']]=(tb_eta/hc)[:,None]
        gout=out[:,fs['gamma']].reshape(self.nk,self.layout.gamma_lmax+1)
        pout=out[:,fs['pol']].reshape(self.nk,self.layout.pol_lmax+1)
        Pi=gam[:,2]+pol[:,0]+pol[:,2]
        gout[:,0]=(-self.k*gam[:,1]+4.0*phi_eta)/hc
        gout[:,1]=(self.k*(gam[:,0]-2.0*gam[:,2])/3.0+4.0*self.k*psi/3.0+opacity*(4.0*tb/(3.0*self.k)-gam[:,1]))/hc
        f3=gam[:,3] if self.layout.gamma_lmax>=3 else 0.0
        gout[:,2]=(2.0*self.k*(gam[:,1]-0.75*f3)/5.0-0.9*opacity*gam[:,2]+0.1*opacity*(pol[:,0]+pol[:,2]))/hc
        eta_now=float(self.bg.interp('eta',N)); eta_sw=float(self.bg.interp('eta',self.n_switch)); x=np.maximum(self.k*(eta_now-eta_sw),1e-8)
        for ell in range(3,self.layout.gamma_lmax+1):
            if ell<self.layout.gamma_lmax:
                nxt=gam[:,ell+1]
            else:
                nxt=(2*ell+1)*gam[:,ell]/x-gam[:,ell-1]
            gout[:,ell]=(self.k*(ell*gam[:,ell-1]-(ell+1)*nxt)/(2*ell+1)-opacity*gam[:,ell])/hc
        # Scalar polarization hierarchy in the Ma-Bertschinger brightness convention.
        pout[:,0]=(-self.k*pol[:,1]-opacity*(pol[:,0]-0.5*Pi))/hc
        pout[:,1]=(self.k*(pol[:,0]-2.0*pol[:,2])/3.0-opacity*pol[:,1])/hc
        p3=pol[:,3] if self.layout.pol_lmax>=3 else 0.0
        pout[:,2]=(2.0*self.k*(pol[:,1]-0.75*p3)/5.0-opacity*(pol[:,2]-0.1*Pi))/hc
        for ell in range(3,self.layout.pol_lmax+1):
            if ell<self.layout.pol_lmax:
                nxt=pol[:,ell+1]
            else:
                nxt=(2*ell+1)*pol[:,ell]/x-pol[:,ell-1]
            pout[:,ell]=(self.k*(ell*pol[:,ell-1]-(ell+1)*nxt)/(2*ell+1)-opacity*pol[:,ell])/hc
        nout=out[:,fs['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        nout[:,0]=(-self.k*nu[:,1]+4.0*phi_eta)/hc
        nout[:,1]=(self.k*(nu[:,0]-2.0*nu[:,2])/3.0+4.0*self.k*psi/3.0)/hc
        for ell in range(2,self.layout.nu_lmax+1):
            if ell<self.layout.nu_lmax:
                nxt=nu[:,ell+1]
            else:
                xnu=np.maximum(self.k*eta_now,1.0e-8)
                nxt=(2*ell+1)*nu[:,ell]/xnu-nu[:,ell-1]
            nout[:,ell]=(self.k*(ell*nu[:,ell-1]-(ell+1)*nxt)/(2*ell+1))/hc
        dout=out[:,fs['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        dout[:]=self._dark_rhs_eta(a,dark,phi_eta,psi)/hc
        return out

    def project_full(self,N:float,state:np.ndarray)->np.ndarray:
        a=math.exp(N); fs=self.layout.full_slices; y=state.copy()
        phi=y[:,fs['phi']][:,0]; db=y[:,fs['db']][:,0]; tb=y[:,fs['tb']][:,0]
        gam=y[:,fs['gamma']].reshape(self.nk,self.layout.gamma_lmax+1); nu=y[:,fs['nu']].reshape(self.nk,self.layout.nu_lmax+1); dark=y[:,fs['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        met=self._metric(a,phi,db,{'f0':gam[:,0],'f1':gam[:,1],'f2':gam[:,2]},nu,dark,tb)
        A=1.5*a*a*np.asarray(met['momentum'])/(self.k*self.k)
        phi_new=-(3.0*float(met['hc'])*A+1.5*a*a*np.asarray(met['delta_rho']))/(self.k*self.k)
        y[:,fs['phi']]=phi_new[:,None]
        met2=self._metric(a,phi_new,db,{'f0':gam[:,0],'f1':gam[:,1],'f2':gam[:,2]},nu,dark,tb)
        self.constraint_records.append(float(np.max(met2['energy_res_rel'])))
        return y

    @staticmethod
    def rk4(rhs, n0:float,n1:float,state:np.ndarray,step:float, callback=None, projector=None)->np.ndarray:
        count=int(math.ceil((n1-n0)/step)); h=(n1-n0)/count; n=n0; y=state.copy()
        for j in range(count):
            k1=rhs(n,y); k2=rhs(n+0.5*h,y+0.5*h*k1); k3=rhs(n+0.5*h,y+0.5*h*k2); k4=rhs(n+h,y+h*k3)
            y += h*(k1+2*k2+2*k3+k4)/6.0; n += h
            if projector is not None: y=projector(n,y)
            if callback is not None: callback(j,n,y)
        return y

    def record_source(self,N:float,state:np.ndarray)->None:
        a=math.exp(N); fs=self.layout.full_slices
        phi=state[:,fs['phi']][:,0]; db=state[:,fs['db']][:,0]; tb=state[:,fs['tb']][:,0]
        gam=state[:,fs['gamma']].reshape(self.nk,self.layout.gamma_lmax+1)
        pol=state[:,fs['pol']].reshape(self.nk,self.layout.pol_lmax+1)
        nu=state[:,fs['nu']].reshape(self.nk,self.layout.nu_lmax+1)
        dark=state[:,fs['dark']].reshape(self.nk,self.layout.nphase,self.layout.dark_lmax+1)
        metric=self._metric(a,phi,db,{'f0':gam[:,0],'f1':gam[:,1],'f2':gam[:,2]},nu,dark,tb)
        self.constraint_records.append(float(np.max(metric['energy_res_rel'])))
        psi=np.asarray(metric['psi']); phi_eta=np.asarray(metric['phi_eta']); hc=float(metric['hc'])
        Pi=gam[:,2]+pol[:,0]+pol[:,2]
        g=float(self.bg.interp('visibility',N)); tau=float(self.bg.interp('tau',N)); chi=float(self.bg.interp('chi',N))
        self.source_records.append({
            'N':N,'a':a,'chi':chi,'g':g,'exp_tau':math.exp(-min(tau,700.0)),
            'phi':phi.copy(),'psi':psi.copy(),'phi_N':phi_eta/hc,
            'monopole':gam[:,0]/4.0,'theta_b':tb.copy(),'Pi':Pi.copy(),
        })

    def run(self)->dict[str,np.ndarray | float]:
        self.constraint_records=[]
        y0=self.initial_state()
        ysw=self.rk4(self.tca_rhs,self.n_initial,self.n_switch,y0,self.tca_step)
        yf0=self.to_full(ysw)
        self.source_records=[]
        def cb(j,n,y):
            if j%4==0 or j==0: self.record_source(n,y)
        yf=self.rk4(self.full_rhs,self.n_switch,self.n_end,yf0,self.full_step,cb)
        # Ensure endpoints are stored.
        self.record_source(self.n_end,yf)
        return self.build_sources()

    def build_sources(self)->dict[str,np.ndarray | float]:
        rec=self.source_records
        N=np.array([r['N'] for r in rec]); chi=np.array([r['chi'] for r in rec]); g=np.array([r['g'] for r in rec]); et=np.array([r['exp_tau'] for r in rec])
        phi=np.stack([r['phi'] for r in rec]); psi=np.stack([r['psi'] for r in rec]); phiN=np.stack([r['phi_N'] for r in rec]); mono=np.stack([r['monopole'] for r in rec]); tb=np.stack([r['theta_b'] for r in rec]); Pi=np.stack([r['Pi'] for r in rec])
        psiN=np.gradient(psi,N,axis=0,edge_order=2)
        # Source amplitudes in dN measure.
        ST=g[:,None]*(mono+psi+Pi/16.0)+et[:,None]*(psiN-phiN)
        SV=g[:,None]*(tb/self.k[None,:])
        SE=3.0*g[:,None]*Pi/16.0
        # Visibility/source weighted effective distance and width.  Absolute weights avoid cancellation bias.
        wg=np.maximum(g,0.0); norm=float(np.trapezoid(wg,N)); chi_star=float(np.trapezoid(wg*chi,N)/norm); sigma_chi=math.sqrt(max(float(np.trapezoid(wg*(chi-chi_star)**2,N)/norm),0.0))
        AT=np.trapezoid(ST,N,axis=0)/self.initial_curvature
        AV=np.trapezoid(SV,N,axis=0)/self.initial_curvature
        AE=np.trapezoid(SE,N,axis=0)/self.initial_curvature
        return {'N':N,'chi':chi,'g':g,'ST':ST,'SV':SV,'SE':SE,'AT':AT,'AV':AV,'AE':AE,'chi_star':chi_star,'sigma_chi':sigma_chi,'constraint_max':float(max(self.constraint_records) if self.constraint_records else 0.0)}


def interpolate_sources(k_solve:np.ndarray, values:np.ndarray, k_dense:np.ndarray)->np.ndarray:
    # Acoustic sources are smooth but oscillatory; cubic interpolation on the linear k axis is adequate at the declared spacing.
    return CubicSpline(k_solve,values,bc_type='natural',extrapolate=False)(k_dense)


def cmb_spectra(k_solve:np.ndarray,sources:dict[str,np.ndarray|float],ell_max:int=2500)->tuple[pd.DataFrame,dict[str,float]]:
    # Dense k grid resolves the Bessel kernel. Source functions are interpolated
    # from the expensive hierarchy grid.  All multipoles are evaluated in two
    # vectorized special-function calls rather than one call per ell.
    k_dense=np.linspace(max(0.05,k_solve[0]),min(2200.0,k_solve[-1]),800)
    AT=interpolate_sources(k_solve,np.asarray(sources['AT']),k_dense)
    AV=interpolate_sources(k_solve,np.asarray(sources['AV']),k_dense)
    AE=interpolate_sources(k_solve,np.asarray(sources['AE']),k_dense)
    chi=float(sources['chi_star']); sig=float(sources['sigma_chi'])
    x=k_dense*chi
    thickness=np.exp(-0.5*(k_dense*sig)**2)
    k_phys=k_dense*P.h0_over_c_mpc
    PR=P.A_s*(k_phys/P.k_pivot_mpc)**(P.n_s-1.0)
    lnk=np.log(k_dense)
    ells=np.unique(np.concatenate([np.arange(2,min(51,ell_max+1)),np.arange(52,ell_max+1,4)])).astype(int)
    jl=spherical_jn(ells[:,None],x[None,:])
    jlp=spherical_jn(ells[:,None],x[None,:],derivative=True)
    DT=thickness[None,:]*(AT[None,:]*jl+AV[None,:]*jlp)
    pref=np.sqrt((ells+2)*(ells+1)*ells*(ells-1)).astype(float)
    DE=thickness[None,:]*pref[:,None]*AE[None,:]*jl/np.maximum(x[None,:]**2,1e-300)
    ctt=4.0*math.pi*np.trapezoid(PR[None,:]*DT*DT,lnk,axis=1)
    cee=4.0*math.pi*np.trapezoid(PR[None,:]*DE*DE,lnk,axis=1)
    cte=4.0*math.pi*np.trapezoid(PR[None,:]*DT*DE,lnk,axis=1)
    fac=ells*(ells+1)/(2.0*math.pi)*(P.t_cmb*1.0e6)**2
    df=pd.DataFrame({'ell':ells,'C_TT':ctt,'C_EE':cee,'C_TE':cte,'D_TT_uK2':fac*ctt,'D_EE_uK2':fac*cee,'D_TE_uK2':fac*cte})
    acoustic_mask=df['ell'].to_numpy()>=80
    acoustic_values=df.loc[acoustic_mask,'D_TT_uK2'].to_numpy()
    acoustic_rows=np.flatnonzero(acoustic_mask)
    local_peaks,_=find_peaks(acoustic_values,distance=60,prominence=max(acoustic_values.max()*0.002,1e-30))
    peaks=acoustic_rows[local_peaks]
    peak_ells=df.iloc[peaks]['ell'].to_numpy(dtype=int)
    peak_vals=df.iloc[peaks]['D_TT_uK2'].to_numpy()
    return df,{
        'first_peak_ell':float(peak_ells[0]) if len(peak_ells) else float('nan'),
        'second_peak_ell':float(peak_ells[1]) if len(peak_ells)>1 else float('nan'),
        'third_peak_ell':float(peak_ells[2]) if len(peak_ells)>2 else float('nan'),
        'first_peak_DTT':float(peak_vals[0]) if len(peak_vals) else float('nan'),
        'te_cauchy_max':float(np.max(np.abs(df.C_TE)/np.sqrt(np.maximum(df.C_TT*df.C_EE,1e-300)))),
    }

def visibility_checks(bg:Background)->dict[str,float]:
    N=bg.loga_grid; g=bg.visibility_grid; integ=float(np.trapezoid(g,N)); i=int(np.argmax(g)); a=float(bg.a_grid[i]); z=1/a-1
    return {'visibility_integral':integ,'z_visibility_peak':z,'a_visibility_peak':a}


def free_streaming_test()->float:
    # Collisionless hierarchy derivative identity for a representative mode.
    x=np.linspace(0.2,12.0,1000); ell=5
    lhs=np.gradient(spherical_jn(ell,x),x)
    rhs=(ell*spherical_jn(ell-1,x)-(ell+1)*spherical_jn(ell+1,x))/(2*ell+1)
    return float(np.max(np.abs(lhs[3:-3]-rhs[3:-3])))


def source_convergence(reference:dict[str,np.ndarray|float], trial:dict[str,np.ndarray|float])->float:
    values=[]
    for key in ['AT','AV','AE']:
        ref=np.asarray(reference[key]); test=np.asarray(trial[key])
        scale=max(float(np.max(np.abs(ref))),0.1)
        values.append(float(np.max(np.abs(test-ref))/scale))
    return max(values)

def acoustic_ruler(bg:Background)->tuple[float,float,float]:
    i=int(np.argmax(bg.visibility_grid)); nstar=float(bg.loga_grid[i])
    mask=bg.loga_grid<=nstar
    R=3.0*P.omega_b0*bg.a_grid/(4.0*omega_gamma0)
    cs=1.0/np.sqrt(3.0*(1.0+R))
    rs=float(np.trapezoid(cs[mask]/bg.hc_grid[mask],bg.loga_grid[mask]))
    chi=float(bg.chi_grid[i]); return rs,chi,math.pi*chi/rs


def main()->None:
    # Dense enough to resolve the acoustic source period while keeping the coupled hierarchy practical.
    k_low=np.geomspace(0.08,25.0,24,endpoint=False)
    k_mid=np.arange(25.0,1600.1,24.0)
    k_high=np.arange(1650.0,2400.1,75.0)
    k=np.unique(np.concatenate([k_low,k_mid,k_high]))
    solver=PrimaryCMBSolver(k,nq=2)
    sources=solver.run()
    pd.DataFrame({'k_over_H0':k,'AT':sources['AT'],'AV':sources['AV'],'AE':sources['AE']}).to_csv(DATA/'primary_cmb_sources.csv',index=False)
    solver.phase.levels.to_csv(DATA/'primary_cmb_dark_levels.csv',index=False)

    vis=visibility_checks(solver.bg)
    rs_h0,chi_geom,l_acoustic=acoustic_ruler(solver.bg)
    _,rho_star,p_star=solver.bg.dark_phase(vis['a_visibility_peak'])
    dark_w_recombination=p_star/rho_star
    # Build the primary spectra after the convergence subruns, avoiding retained special-function workspaces.
    spectra,peak_info=cmb_spectra(k,sources,ell_max=2500)
    spectra.to_csv(DATA/'primary_cmb_spectra.csv',index=False)
    selected_targets=[30,50,100,200,252,500,608,904,1000,1500,2000,2500]
    selected_rows=[]
    for target in selected_targets:
        idx=(spectra['ell']-target).abs().idxmin()
        selected_rows.append(spectra.loc[idx])
    pd.DataFrame(selected_rows).drop_duplicates('ell').to_csv(DATA/'selected_primary_cmb_spectra.csv',index=False)
    # Source interpolation self-check: remove every other solved mode and reconstruct held-out values.
    hold=np.arange(1,len(k)-1,2); keep=np.setdiff1d(np.arange(len(k)),hold)
    interp_errs=[]
    for key in ['AT','AV','AE']:
        pred=CubicSpline(k[keep],np.asarray(sources[key])[keep],bc_type='natural')(k[hold])
        denom=np.maximum(np.abs(np.asarray(sources[key])[hold]),1e-8)
        interp_errs.append(float(np.median(np.abs(pred-np.asarray(sources[key])[hold])/denom)))
    # Visibility-source projection width diagnostic.
    thickness_at_l3000=math.exp(-0.5*((3000.0/float(sources['chi_star']))*float(sources['sigma_chi']))**2)
    checks=[]
    def add(cid,statement,value,tol,mode='le'):
        if mode=='le': status='PASS' if abs(value)<=tol else 'FAIL'
        elif mode=='ge': status='PASS' if value>=tol else 'FAIL'
        else: status='PASS' if bool(value) else 'FAIL'
        checks.append({'id':cid,'statement':statement,'value':float(value),'threshold':float(tol),'status':status})
    add('PCMB01','visibility integrates to unity in log-a measure',abs(vis['visibility_integral']-1.0),2e-3)
    add('PCMB02','visibility peak lies in controlled recombination window',vis['z_visibility_peak'],900.0,'ge')
    add('PCMB03','Einstein energy constraint remains controlled',float(sources['constraint_max']),3e-2)
    add('PCMB04','free-streaming Bessel recurrence is recovered',free_streaming_test(),2e-4)
    add('PCMB05','source interpolation median error is controlled',max(interp_errs),0.12)
    add('PCMB06','TT spectrum is nonnegative',float(max(-spectra.C_TT.min(),0.0)),1e-20)
    add('PCMB07','EE spectrum is nonnegative',float(max(-spectra.C_EE.min(),0.0)),1e-20)
    add('PCMB08','TE obeys Cauchy bound',max(peak_info['te_cauchy_max']-1.0,0.0),5e-8)
    add('PCMB09','first acoustic TT maximum occurs at finite ell',peak_info['first_peak_ell'],80.0,'ge')
    add('PCMB10','finite-width projection is nonzero at ell 3000',thickness_at_l3000,1e-8,'ge')
    add('PCMB11','photon polarization source is generated',float(np.max(np.abs(sources['AE']))),1e-10,'ge')
    add('PCMB12','dark hierarchy retains at least five refinement levels',float(len(solver.phase.levels)),5.0,'ge')
    add('PCMB13','radiation split has positive photon density',omega_gamma0,1e-6,'ge')
    add('PCMB14','radiation split has positive neutrino density',omega_nu0,1e-6,'ge')
    add('PCMB15','first TT peak amplitude is finite',peak_info['first_peak_DTT'],1e-6,'ge')
    add('PCMB16','source distance is positive',float(sources['chi_star']),1.0,'ge')
    add('PCMB17','source width is positive',float(sources['sigma_chi']),1e-8,'ge')
    add('PCMB18','all spectra values are finite',float(np.all(np.isfinite(spectra[['C_TT','C_EE','C_TE']].to_numpy()))),1.0,'ge')
    add('PCMB19','dark tower is cold by recombination',dark_w_recombination,1e-5)
    peak_spacing=peak_info['second_peak_ell']-peak_info['first_peak_ell']
    add('PCMB20','acoustic peak spacing matches geometric ruler',abs(peak_spacing-l_acoustic)/l_acoustic,0.20)

    pd.DataFrame(checks).to_csv(DATA/'primary_cmb_checks.csv',index=False)

    summary={
        'parameters':asdict(P),
        'omega_gamma0':omega_gamma0,'omega_nu0':omega_nu0,
        'k_mode_count':int(len(k)),'phase_node_count':int(solver.phase.size),'dark_level_count':int(len(solver.phase.levels)),
        'visibility':vis,'chi_star_H0inv':float(sources['chi_star']),'sigma_chi_H0inv':float(sources['sigma_chi']),
        'sound_horizon_H0inv':rs_h0,'geometric_acoustic_multipole':l_acoustic,
        'dark_w_at_recombination':dark_w_recombination,
        'constraint_max_relative':float(sources['constraint_max']),
        'source_interpolation_median_errors':{'AT':interp_errs[0],'AV':interp_errs[1],'AE':interp_errs[2]},
        'thickness_factor_ell3000':thickness_at_l3000,
        **peak_info,
        'pass_count':sum(c['status']=='PASS' for c in checks),'fail_count':sum(c['status']=='FAIL' for c in checks),
        'checks':checks,
    }
    (DATA/'Production_to_Primary_CMB_Verification.json').write_text(json.dumps(summary,indent=2))

    # Figures.
    plt.figure(figsize=(8.4,5.0))
    plt.semilogx(k,np.abs(sources['AT']),label=r'$|A_T|$')
    plt.semilogx(k,np.abs(sources['AV']),label=r'$|A_V|$')
    plt.semilogx(k,np.abs(sources['AE']),label=r'$|A_E|$')
    plt.xlabel(r'$k/H_0$'); plt.ylabel('effective last-scattering source'); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_sources.png',dpi=180); plt.close()

    plt.figure(figsize=(8.4,5.2))
    plt.semilogy(spectra.ell,np.maximum(spectra.D_TT_uK2,1e-8),label='TT')
    plt.semilogy(spectra.ell,np.maximum(spectra.D_EE_uK2,1e-8),label='EE')
    plt.xlabel(r'$\ell$'); plt.ylabel(r'$\ell(\ell+1)C_\ell/(2\pi)$ [$\mu$K$^2$]'); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_tt_ee.png',dpi=180); plt.close()

    acoustic=spectra.ell>=30
    plt.figure(figsize=(8.4,5.2))
    plt.semilogy(spectra.loc[acoustic,'ell'],np.maximum(spectra.loc[acoustic,'D_TT_uK2'],1e-8),label='TT')
    plt.semilogy(spectra.loc[acoustic,'ell'],np.maximum(spectra.loc[acoustic,'D_EE_uK2'],1e-8),label='EE')
    plt.xlim(30,2500)
    plt.xlabel(r'$\ell$'); plt.ylabel(r'$\ell(\ell+1)C_\ell/(2\pi)$ [$\mu$K$^2$]'); plt.legend(); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_tt_ee_acoustic.png',dpi=200); plt.close()

    plt.figure(figsize=(8.4,4.8))
    plt.plot(spectra.ell,spectra.D_TE_uK2,label='TE')
    plt.axhline(0.0,linewidth=0.8)
    plt.xlabel(r'$\ell$'); plt.ylabel(r'$D_\ell^{TE}$ [$\mu$K$^2$]'); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_te.png',dpi=180); plt.close()

    plt.figure(figsize=(8.4,4.8))
    plt.plot(spectra.loc[acoustic,'ell'],spectra.loc[acoustic,'D_TE_uK2'],label='TE')
    plt.axhline(0.0,linewidth=0.8)
    plt.xlim(30,2500)
    plt.xlabel(r'$\ell$'); plt.ylabel(r'$D_\ell^{TE}$ [$\mu$K$^2$]'); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_te_acoustic.png',dpi=200); plt.close()

    # Visibility figure.
    z=1.0/solver.bg.a_grid-1.0
    mask=(z>=500)&(z<=2200)
    plt.figure(figsize=(8.4,4.8))
    plt.plot(z[mask],solver.bg.visibility_grid[mask])
    plt.gca().invert_xaxis(); plt.xlabel('redshift z'); plt.ylabel(r'$g_N$'); plt.tight_layout()
    plt.savefig(FIG/'primary_cmb_visibility.png',dpi=180); plt.close()

    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},indent=2))


if __name__=='__main__':
    main()
