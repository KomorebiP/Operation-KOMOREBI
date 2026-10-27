#!/usr/bin/env python3
"""Exact finite data and reproducible scientific figures for the q=12 bridge.

Integer/Fraction assertions and floating rendering diagnostics are separate.
No random trials, hardware simulation, circuit synthesis, or universal claim.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, platform, sys
from fractions import Fraction as Q
from pathlib import Path
from math import gcd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
INK, TEAL, CORAL, GOLD, BLUE = '#182a3b','#087f80','#d35642','#b27e16','#5869af'
PALETTE = [INK,GOLD,BLUE,CORAL,'#6c9682',TEAL]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.labelsize':14,
    'axes.titlesize':16,'xtick.labelsize':12,'ytick.labelsize':12,
    'text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':INK,
    'xtick.color':INK,'ytick.color':INK,'pdf.fonttype':42,'svg.fonttype':'none',
    'savefig.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})

def style(ax, xlab='', ylab='', ticks=True):
    ax.set_xlabel(xlab); ax.set_ylabel(ylab); ax.grid(axis='y',alpha=.14)
    if ticks: ax.set_xticks(np.arange(12))

def stem(ax, y, color=TEAL, labels=False, offset=0, marker='o'):
    xx=np.arange(len(y))+offset
    ax.vlines(xx,0,y,color=color,lw=2.2); ax.scatter(xx,y,s=48,color=color,marker=marker,zorder=4)
    ax.axhline(0,color=INK,lw=.7,alpha=.5)
    if labels:
        for x,v in zip(xx,y):
            if v != 0: ax.annotate(f'{v:g}',(x,v),xytext=(0,7 if v>0 else -18),textcoords='offset points',ha='center',fontsize=12)

def matrix_product(A,B):
    return [[sum((A[i][k]*B[k][j] for k in range(12)),Q(0)) for j in range(12)] for i in range(12)]

def main(out):
    original=ROOT/'inputs/Komorebi_Quantum_Arithmetic_Reproducibility/Arithmetic_Becomes_Interference/verify_bridge.py'
    spec=importlib.util.spec_from_file_location('source_bridge',original)
    bridge=importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)
    inherited=bridge.main()
    counts={}
    def check(name,ok):
        if not ok: raise AssertionError(name)
        counts[name]=counts.get(name,0)+1
    N=12; n=np.arange(N); U=[1,5,7,11]; ds=[1,2,3,4,6,12]
    c=[bridge.ramanujan(12,k) for k in range(12)]
    noise=[5,2,-1,2,5,2,-1,2,5,2,-1,2]
    x=[c[i]+noise[i] for i in range(12)]
    orders=[N//gcd(i,N) for i in range(N)]
    Pd={d:[[Q(bridge.ramanujan(d,i-j),N) for j in range(N)] for i in range(N)] for d in ds}
    components={d:[sum((Pd[d][i][j]*x[j] for j in range(N)),Q(0)) for i in range(N)] for d in ds}
    energies={d:sum(v*v for v in components[d]) for d in ds}
    ranks={d:sum(Pd[d][i][i] for i in range(N)) for d in ds}
    for d in ds:
        check('rank_equals_order_class_size',ranks[d]==orders.count(d))
        for e in ds:
            product=matrix_product(Pd[d],Pd[e])
            for i in range(N):
                for j in range(N):
                    check('independent_fraction_shell_products',product[i][j]==(Pd[d][i][j] if d==e else Q(0)))
    for i in range(N):
        check('independent_component_completeness',sum(components[d][i] for d in ds)==x[i])
        for j in range(N):check('independent_fraction_completeness',sum(Pd[d][i][j] for d in ds)==(1 if i==j else 0))
    check('order_class_energy_assignment',energies=={1:Q(48),2:Q(0),3:Q(0),4:Q(54),6:Q(0),12:Q(48)})
    check('orthogonal_packet_energy_sum',sum(energies.values())==150)
    check('normalized_filter_success_probability',Q(48,150)==Q(8,25))
    chi_abs=[abs(v) for v in c]
    plus=[max(v,0) for v in c]; minus=[max(-v,0) for v in c]
    check('phase_family_disjoint_support',sum(a*b for a,b in zip(plus,minus))==0)
    check('phase_family_equal_half_energies',sum(v*v for v in plus)==sum(v*v for v in minus)==24)
    check('phase_family_orthogonal_endpoints',sum(a*b for a,b in zip(c,chi_abs))==0)
    # Exact quarter-turn probabilities in Q(i), using P v+ = c/2 and P v- = -c/2.
    for vec,sgn in [(plus,1),(minus,-1)]:
        check('phase_family_projected_halves', [sum(Pd[12][i][j]*vec[j] for j in range(12)) for i in range(12)]==[Q(sgn*v,2) for v in c])
    for re,im,prob in [(1,0,Q(0)),(0,1,Q(1,2)),(-1,0,Q(1)),(0,-1,Q(1,2))]:
        check('phase_family_exact_quadrants',Q((1-re)**2+im**2,4)==prob)
    powers=[bridge.ONE]
    for _ in range(11): powers.append(bridge.times_z(powers[-1]))
    dft_abs=[]
    for k in range(12):
        z=bridge.ZERO
        for t in range(12):z=bridge.add(z,bridge.scale(chi_abs[t],powers[(-k*t)%12]))
        check('phase_erased_DFT_real',z[1:]==(0,0,0)); dft_abs.append(z[0])
    check('phase_erased_DFT_full_table',dft_abs==[16,0,4,0,4,0,16,0,4,0,4,0])
    p_psi=[Q(v*v,48) for v in c]; p_u=[Q(1,4) if k in U else Q(0) for k in range(12)]
    p_chi_f=[Q(v*v,576) for v in dft_abs]
    check('phase_erased_transformed_total',sum(p_chi_f)==1)
    check('phase_erased_transformed_selected_mass',sum(p_chi_f[k] for k in U)==0)
    lanes=[[x[r+3*m] for m in range(4)] for r in range(3)]
    check('polyphase_interleave_exact',[lanes[i%3][i//3] for i in range(12)]==x)
    F=np.exp(2j*np.pi*np.outer(n,n)/12)/np.sqrt(12)
    psi=np.array(c)/np.sqrt(48); chi=np.abs(psi); u=np.array([.5 if k in U else 0 for k in n])
    P=np.array(Pd[12],dtype=float)
    theta=np.linspace(0,2*np.pi,401)
    family=np.array(plus)[None,:]/np.sqrt(48)+np.exp(1j*theta[:,None])*np.array(minus)[None,:]/np.sqrt(48)
    selected=np.sum(np.abs(family@P.T)**2,axis=1)
    numerical={
        'phase_family_probability_max_error':float(np.max(np.abs(selected-np.sin(theta/2)**2))),
        'phase_family_norm_max_error':float(np.max(np.abs(np.sum(np.abs(family)**2,axis=1)-1))),
        'polyphase_alias_max_error':float(np.max(np.abs(np.fft.fft(x)-np.array([sum(np.exp(-2j*np.pi*k*r/12)*np.fft.fft(lanes[r])[k%4] for r in range(3)) for k in range(12)])))),
        'selected_projector_state_residual':float(np.max(np.abs(P@psi-psi))),
        'erased_projector_state_residual':float(np.max(np.abs(P@chi))),
    }
    tolerance=1e-12
    if max(numerical.values())>tolerance:raise AssertionError(numerical)
    figures=[]; figdir=ROOT/'figures'; figdir.mkdir(exist_ok=True)
    def save(name,fig):
        for ext in ('pdf','svg','png'):
            path=figdir/f'{name}.{ext}'
            fig.savefig(path,dpi=240,bbox_inches='tight',pad_inches=.15)
        plt.close(fig); figures.append(name)
    # 01: actual root geometry, selected coprime roots highlighted.
    fig,ax=plt.subplots(figsize=(8.6,5.8),layout='constrained')
    angle=np.linspace(0,2*np.pi,401); ax.plot(np.cos(angle),np.sin(angle),color=INK,alpha=.2,lw=1)
    z=np.exp(2j*np.pi*n/12)
    for k in n:
        sel=k in U; ax.scatter(z[k].real,z[k].imag,s=130 if sel else 65,color=TEAL if sel else '#c9d2d9',edgecolor='white',lw=1,zorder=4)
        ax.text(1.15*z[k].real,1.15*z[k].imag,str(k),ha='center',va='center',color=TEAL if sel else INK,fontsize=15,fontweight='bold' if sel else 'normal')
    ax.axhline(0,color=INK,lw=.7,alpha=.2);ax.axvline(0,color=INK,lw=.7,alpha=.2)
    ax.set(xlim=(-1.4,1.4),ylim=(-1.35,1.35),xlabel='Real part',ylabel='Imaginary part');ax.set_aspect('equal')
    ax.set_title('Coprimality selects four primitive twelfth roots',pad=16)
    save('01_primitive_roots',fig)
    # 02: all arrows are primitive phases, not stochastic outcomes.
    fig,axs=plt.subplots(1,3,figsize=(11,4.4),layout='constrained')
    for ax,t in zip(axs,[0,1,6]):
        ax.plot(np.cos(angle),np.sin(angle),color=INK,alpha=.15)
        # Tiny parallel offsets expose coincident arrows at n=0,6 without changing vector directions.
        for idx,k in enumerate(U):
            w=np.exp(2j*np.pi*k*t/12);shift=(idx-1.5)*.045
            ax.arrow(0,shift,w.real,w.imag,width=.01,head_width=.09,length_includes_head=True,color=[TEAL,BLUE,CORAL,GOLD][idx],alpha=.8)
        ax.set_aspect('equal');ax.set(xlim=(-1.25,1.25),ylim=(-1.25,1.25));ax.set_xticks([-1,0,1]);ax.set_yticks([-1,0,1]);ax.set_title(f'n = {t}   ·   sum = {c[t]}',pad=12)
        ax.set_xlabel('Real phase');ax.set_ylabel('Imaginary phase' if t==0 else '')
    save('02_phase_addition',fig)
    # 03
    fig,ax=plt.subplots(figsize=(10,4.9),layout='constrained');stem(ax,c,labels=True);style(ax,'Sample n','Integer value');ax.set_ylim(-5.2,5.2);ax.set_title('The four phases produce one exact integer signal',pad=15);save('03_ramanujan_signal',fig)
    # 04
    spectrum=[12 if k in U else 0 for k in n]
    fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');stem(ax,spectrum,BLUE,labels=True);style(ax,'Frequency label k','Unnormalized DFT coefficient');ax.set_ylim(-1,15);ax.set_title('The spectrum returns the original arithmetic selection',pad=15);save('04_exact_spectrum',fig)
    # 05
    cmap=LinearSegmentedColormap.from_list('bridge',[CORAL,'#f7f9fa',TEAL])
    fig,axs=plt.subplots(1,2,figsize=(10,5.5),layout='constrained')
    D=np.diag([1 if k in U else 0 for k in n]);axs[0].imshow(D,cmap=cmap,vmin=-1,vmax=1);axs[0].set_title('D: selector in frequency basis');axs[0].set_xlabel('Input frequency');axs[0].set_ylabel('Output frequency')
    im=axs[1].imshow(P,cmap=cmap,vmin=-1/3,vmax=1/3);axs[1].set_title('P: rational sample-basis operator');axs[1].set_xlabel('Input sample');axs[1].set_ylabel('Output sample')
    for ax in axs:ax.set_xticks([0,3,6,9,11]);ax.set_yticks([0,3,6,9,11])
    cb=fig.colorbar(im,ax=axs[1],shrink=.8,ticks=[-1/3,-1/6,0,1/6,1/3]);cb.ax.set_yticklabels(['−1/3','−1/6','0','1/6','1/3']);save('05_transported_projector',fig)
    # 06
    fig,axs=plt.subplots(3,1,figsize=(10,7.5),sharex=True,layout='constrained')
    for ax,vals,col,title in zip(axs,[x,c,noise],[INK,TEAL,CORAL],['Input x = selected component + complementary component','Retained Px = c₁₂','Residual (I − P)x = 3 cos(πn/2) + 2']):
        stem(ax,vals,col);style(ax,'','Value');ax.set_title(title,loc='left',fontsize=14)
    axs[-1].set_xlabel('Sample n');save('06_filter_components',fig)
    # 07
    fig,axs=plt.subplots(1,2,figsize=(10,5.3),layout='constrained')
    axs[0].bar(['Input','Retained','Residual'],[150,48,102],color=[INK,TEAL,CORAL],width=.6)
    for i,v in enumerate([150,48,102]):axs[0].text(i,v+4,str(v),ha='center',fontweight='bold',fontsize=16)
    axs[0].set_ylim(0,174);style(axs[0],'','Squared norm',False);axs[0].set_title('Exact energy bookkeeping')
    axs[1].barh(['Normalized input'],[Q(8,25)],color=TEAL,height=.35,label='Selected: 8/25')
    axs[1].barh(['Normalized input'],[Q(17,25)],left=[Q(8,25)],color=CORAL,height=.35,label='Complement: 17/25');axs[1].set_xlim(0,1)
    axs[1].set_xlabel('Share of total squared norm');axs[1].set_title('Projection retains 32% of this input');axs[1].legend(loc='lower center',bbox_to_anchor=(.5,-.28),frameon=False,fontsize=12)
    save('07_energy_and_loss',fig)
    # 08
    fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained')
    for k,d in enumerate(orders):
        color=PALETTE[ds.index(d)];ax.bar(k,1,color=color,width=.88);ax.text(k,.5,str(d),ha='center',va='center',color='white',fontsize=15,fontweight='bold')
    ax.set_xticks(n);ax.set_xlabel('Frequency label k');ax.set_yticks([]);ax.set_ylim(0,1.08);ax.set_title('Every frequency belongs to exactly one root-order class',pad=18)
    save('08_order_partition',fig)
    # 09
    fig,axs=plt.subplots(3,2,figsize=(10,8),sharex=True,layout='constrained')
    for ax,d,color in zip(axs.flat,ds,PALETTE):
        vals=[bridge.ramanujan(d,int(t)) for t in n];stem(ax,vals,color);style(ax,'','c_d(n)');ax.set_title(f'd = {d}   ·   rank {int(ranks[d])}',loc='left',fontsize=14);ax.set_xticks([0,3,6,9,11])
    for ax in axs[-1]:ax.set_xlabel('Sample n')
    save('09_six_rational_kernels',fig)
    # 10
    fig,axs=plt.subplots(1,2,figsize=(10,5.3),layout='constrained')
    axs[0].bar([str(d) for d in ds],[int(ranks[d]) for d in ds],color=PALETTE);axs[0].set_title('Subspace dimensions sum to 12');style(axs[0],'Order d','Rank φ(d)',False);axs[0].set_ylim(0,5)
    axs[1].bar([str(d) for d in ds],[float(energies[d]) for d in ds],color=PALETTE);axs[1].set_title('This input occupies only three shells');style(axs[1],'Order d','Component squared norm',False);axs[1].set_ylim(0,65)
    for i,d in enumerate(ds):axs[0].text(i,float(ranks[d])+.12,str(int(ranks[d])),ha='center');axs[1].text(i,float(energies[d])+1.5,str(int(energies[d])),ha='center')
    save('10_dimensions_and_shell_energies',fig)
    # 11
    fig,axs=plt.subplots(2,1,figsize=(10,6.4),layout='constrained')
    stem(axs[0],u,BLUE);style(axs[0],'Frequency-basis label k','Amplitude');axs[0].set_ylim(-.12,.7);axs[0].set_title('u: four amplitudes of 1/2',loc='left')
    stem(axs[1],psi,TEAL);style(axs[1],'Sample-basis label n','Amplitude');axs[1].set_ylim(-.75,.75);axs[1].set_title('ψ = Fu: coherent arithmetic signal',loc='left')
    save('11_same_state_two_bases',fig)
    # 12
    fig,axs=plt.subplots(2,1,figsize=(10,6.4),layout='constrained')
    for ax,vals,col,title,xlabel in zip(axs,[p_psi,p_u],[TEAL,BLUE],['Measure ψ in the sample basis','Apply F†, then measure a fresh preparation'],['Outcome n','Outcome k']):
        ax.bar(n,np.array(vals,dtype=float),color=col,width=.67);style(ax,xlabel,'Probability');ax.set_ylim(0,.4);ax.set_title(title,loc='left');ax.set_yticks([0,1/12,1/4,1/3]);ax.set_yticklabels(['0','1/12','1/4','1/3'])
    save('12_alternative_measurements',fig)
    # 13
    fig,axs=plt.subplots(2,1,figsize=(10,6.4),layout='constrained')
    stem(axs[0],psi,TEAL,offset=-.10);stem(axs[0],chi,CORAL,offset=.10,marker='s');style(axs[0],'Sample label n','Amplitude');axs[0].set_ylim(-.75,.8);axs[0].set_title('Signed ψ and unsigned χ have different coherent amplitudes',loc='left');axs[0].plot([],[],color=TEAL,marker='o',label='ψ: signed');axs[0].plot([],[],color=CORAL,marker='s',label='χ: signs erased');axs[0].legend(frameon=False,loc='upper right',fontsize=12)
    axs[1].bar(n,np.array(p_psi,dtype=float),color=GOLD,width=.65);style(axs[1],'Sample outcome n','Shared probability');axs[1].set_ylim(0,.4);axs[1].set_title('Their sample-basis measurement probabilities are identical',loc='left')
    save('13_same_histogram_distinct_states',fig)
    # 14
    fig,axs=plt.subplots(2,1,figsize=(10,6.4),layout='constrained')
    for ax,vals,col,title in zip(axs,[p_u,p_chi_f],[TEAL,CORAL],['F†ψ: all probability on coprime labels','F†χ: zero probability on coprime labels']):
        ax.bar(n,np.array(vals,dtype=float),color=col,width=.65);style(ax,'Frequency-basis outcome k','Probability');ax.set_ylim(0,.52);ax.set_title(title,loc='left')
        for k in U:ax.axvspan(k-.45,k+.45,color=TEAL,alpha=.055)
    save('14_phase_changes_measurement',fig)
    # 15
    fig,ax=plt.subplots(figsize=(10,5.4),layout='constrained');ax.plot(theta,np.sin(theta/2)**2,color=TEAL,lw=3);ax.scatter([0,np.pi/2,np.pi,3*np.pi/2,2*np.pi],[0,.5,1,.5,0],color=INK,s=45,zorder=4)
    ax.set_xticks([0,np.pi/2,np.pi,3*np.pi/2,2*np.pi]);ax.set_xticklabels(['0','π/2','π','3π/2','2π']);ax.set(xlabel='Relative phase θ on the negative-amplitude support',ylabel='Selected probability',ylim=(-.04,1.08));ax.grid(alpha=.15);ax.set_title('A continuous phase change moves selected mass from 0 to 1',pad=14)
    ax.annotate('Unsigned χ',(0,0),xytext=(35,25),textcoords='offset points',fontsize=13);ax.annotate('Signed ψ',(np.pi,1),xytext=(0,-34),textcoords='offset points',ha='center',fontsize=13)
    save('15_phase_probability',fig)
    # 16: true complex-amplitude trajectory, not a decorative embedding.
    fig=plt.figure(figsize=(10,6.6),layout='constrained');ax=fig.add_subplot(111,projection='3d');amp=np.exp(1j*theta)/np.sqrt(3)
    ax.plot(theta,amp.real,amp.imag,color=TEAL,lw=2.7)
    for t,col in [(0,CORAL),(np.pi,BLUE),(2*np.pi,CORAL)]:ax.scatter([t],[np.cos(t)/np.sqrt(3)],[np.sin(t)/np.sqrt(3)],color=col,s=65)
    ax.set_xlabel('Relative phase θ',labelpad=12);ax.set_ylabel('Re χθ(6)',labelpad=12);ax.set_zlabel('');ax.set_xticks([0,np.pi,2*np.pi]);ax.set_xticklabels(['0','π','2π']);ax.set_yticks([-.5,0,.5]);ax.set_zticks([-.5,0,.5]);ax.set_title('One amplitude traces a circle as phase advances',pad=15);ax.view_init(22,-58);ax.set_box_aspect((2.0,1,1));ax.text2D(.96,.70,'Im χθ(6)',transform=ax.transAxes,rotation=90,ha='center',va='center',fontsize=14);save('16_complex_amplitude_trajectory',fig)
    # 17
    fig,axs=plt.subplots(3,1,figsize=(10,7),sharex=True,layout='constrained')
    for r,ax,col in zip(range(3),axs,[TEAL,BLUE,CORAL]):
        ax.vlines(range(4),0,lanes[r],color=col,lw=2);ax.scatter(range(4),lanes[r],color=col,s=55);ax.axhline(0,color=INK,lw=.6);ax.set_xticks(range(4));ax.set_ylabel('Lane value');ax.set_title(f'Lane r = {r}: original addresses {r}, {r+3}, {r+6}, {r+9}',loc='left',fontsize=14);ax.grid(axis='y',alpha=.13)
        ax.set_ylim(min(0,min(lanes[r]))-1.8,max(0,max(lanes[r]))+2.0)
        for m,v in enumerate(lanes[r]):ax.annotate(str(v),(m,v),xytext=(0,7 if v>=0 else -16),textcoords='offset points',ha='center',fontsize=12)
    axs[-1].set_xlabel('Within-lane index m');save('17_polyphase_lanes',fig)
    # 18
    fig,axs=plt.subplots(1,2,figsize=(10,5.4),layout='constrained')
    lane_spectra=np.array([np.fft.fft(lane) for lane in lanes]);full=np.fft.fft(x)
    for r,col in zip(range(3),[TEAL,BLUE,CORAL]):
        axs[0].plot(range(4),np.abs(lane_spectra[r]),marker='o',lw=2,color=col,label=f'Lane {r}')
    axs[0].set_xticks(range(4));style(axs[0],'Local frequency j','DFT magnitude',False);axs[0].set_title('Three lane transforms');axs[0].legend(frameon=False,fontsize=12)
    axs[1].bar(n,np.abs(full),color=INK,width=.65);style(axs[1],'Global frequency k','DFT magnitude');axs[1].set_title('Phase-weighted assembly recovers x̂')
    save('18_polyphase_alias_assembly',fig)
    # 19
    fig,axs=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    for ax,q in zip(axs.flat,[5,8,12,15]):
        vals=[bridge.ramanujan(q,t) for t in range(q)];stem(ax,vals,TEAL);ax.set_xticks(list(range(0,q,max(1,q//5))));style(ax,'Sample n','Integer value',False);ax.set_title(f'q = {q}   ·   φ(q) = {sum(gcd(k,q)==1 for k in range(q))}',loc='left',fontsize=14)
    save('19_other_arithmetic_signals',fig)
    # 20: projection geometry on the 2D span of the two known orthogonal states.
    fig,ax=plt.subplots(figsize=(9,5.8),layout='constrained');ax.plot(np.cos(angle),np.sin(angle),color=INK,alpha=.2);a=np.sqrt(48/150);b=np.sqrt(102/150)
    ax.arrow(0,0,a,b,color=INK,width=.012,head_width=.065,length_includes_head=True);ax.arrow(0,0,a,0,color=TEAL,width=.012,head_width=.065,length_includes_head=True);ax.plot([a,a],[0,b],ls='--',color=CORAL,lw=2);ax.scatter([a],[b],color=INK,s=70)
    ax.text(a+.05,b,'x / √150',fontsize=15);ax.text(a/2,-.13,'Px / √150',color=TEAL,ha='center',fontsize=14);ax.text(a+.05,b/2,'Discarded component',color=CORAL,fontsize=13)
    ax.set_aspect('equal');ax.set(xlim=(-1.1,1.65),ylim=(-1.05,1.15));ax.axhline(0,color=INK,lw=.7);ax.axvline(0,color=INK,lw=.7);ax.set_xlabel('Along c₁₂ / √48');ax.set_ylabel('Along noise / √102');ax.set_title('Projection contracts this vector; the Fourier transform does not',pad=15);save('20_projection_geometry',fig)
    assets={}
    for name in figures:
        for ext in ('pdf','svg','png'):
            path=figdir/f'{name}.{ext}';assets[str(path.relative_to(ROOT))]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    result={'status':'PASS','source_verifier':inherited,
      'new_exact_assertions':counts,'new_exact_assertion_count':sum(counts.values()),
      'numeric_rendering_diagnostics':{'status':'PASS','tolerance':tolerance,'theta_sample_count':401,**numerical},
      'exact_data':{'orders':orders,'ranks':{str(d):str(ranks[d]) for d in ds},'shell_energies':{str(d):str(energies[d]) for d in ds},'lanes':lanes,'unsigned_DFT':dft_abs,'unsigned_Fourier_probabilities':[str(v) for v in p_chi_f]},
      'figures':figures,'figure_count':len(figures),'assets':assets,
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
      'non_claims':['Finite checks are not universal proofs.','Plots render exact formulas at floating-point coordinates.','No fresh Lean compilation is performed by this script.','No quantum hardware, gate synthesis, or complexity advantage is claimed.','Continuous relative-phase illustration is a prose derivation, not an added Lean theorem.']}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','source_exact_assertions':inherited['exact_assertion_count'],'new_exact_assertions':sum(counts.values()),'figures':len(figures),'largest_numeric_residual':max(numerical.values())},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();main(args.output)
