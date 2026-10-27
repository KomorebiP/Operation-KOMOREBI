"""Eight exact or explicitly finite introductory visual lessons."""
from fractions import Fraction as F
from math import factorial
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from guide_style import ROOT, COLORS, INK, MUTED, PALE, save_figure

def box(ax,xy,text,w=1.5,h=.55,color=PALE):
    x,y=xy
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.04',
        edgecolor=COLORS[0],facecolor=color,linewidth=1.2))
    ax.text(x,y,text,ha='center',va='center',fontsize=12,color=INK)

def main():
    checks={}
    fig,ax=plt.subplots(figsize=(8.1,4.2),layout='constrained')
    for r in range(3):
        for m in range(6):
            n=3*m+r
            ax.scatter(m,r,s=670,color=COLORS[r],alpha=.14)
            ax.text(m,r,str(n),ha='center',va='center',fontsize=16,color=COLORS[r])
    ax.set(xlim=(-.55,5.55),ylim=(2.6,-.6),xticks=range(6),yticks=range(3),
        xlabel='Packet index m',ylabel='Residue address r',title='Each exponent n has exactly one address n = 3m + r')
    ax.set_yticklabels(['r = 0','r = 1','r = 2']);ax.grid(axis='x')
    save_figure(fig,'F01_coefficient_addresses')
    checks['F01']={'exponents':list(range(18)),'unique_addresses':len({(n//3,n%3) for n in range(18)})}

    fig,ax=plt.subplots(figsize=(8.1,4.2),layout='constrained')
    for r,y in [(0,2.5),(1,.4)]:
        box(ax,(.5,y),f'Parent r = {r}',w=1.65)
        for ell in range(3):
            cy=y+.65*(1-ell)
            child=r+2*ell
            box(ax,(4.4,cy),f'Child {child}:  n = 6j + {child}',w=2.6,h=.46)
            ax.annotate('',xy=(3.05,cy),xytext=(1.4,y),arrowprops={'arrowstyle':'->','color':COLORS[r],'lw':1.6})
            ax.text(2.05,(y+cy)/2+.13,f'ell = {ell}',color=COLORS[r],fontsize=11)
    ax.set(xlim=(-.5,6),ylim=(-.8,3.6),title='Refine modulus 2 by a factor of 3');ax.axis('off')
    save_figure(fig,'F02_refinement_addresses')
    checks['F02']={'child_addresses':[[r+2*ell for ell in range(3)] for r in range(2)]}

    fig,axs=plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')
    mat=np.array([[0,0,.4],[1,0,0],[0,1,0]])
    axs[0].imshow(mat,cmap='Blues',vmin=0,vmax=1)
    for i in range(3):
        for j in range(3):axs[0].text(j,i,['0','1','u = 0.4'][0 if mat[i,j]==0 else (1 if mat[i,j]==1 else 2)],ha='center',va='center',color='white' if mat[i,j]>.65 else INK)
    axs[0].set(xticks=range(3),yticks=range(3),xlabel='Input address',ylabel='Output address',title='Carry matrix C(u)')
    x=np.array([1.,2.,3.]);y=mat@x;idx=np.arange(3)
    axs[1].bar(idx-.17,x,width=.34,label='Input',color=COLORS[0]);axs[1].bar(idx+.17,y,width=.34,label='After carry',color=COLORS[1])
    axs[1].set(xticks=idx,xlabel='Address',ylabel='Coefficient',ylim=(0,3.7),title='Wraparound brings one factor of u');axs[1].legend()
    save_figure(fig,'F03_carry_matrix')
    assert np.allclose(y,[1.2,1,2]);checks['F03']={'u':'2/5','input':[1,2,3],'output':['6/5',1,2]}

    b=np.array([1.,2.,4.,1.]);W=np.fft.fft(b)/2;energy=np.abs(W)**2
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')
    axs[0].bar(range(4),b,color=COLORS[0]);axs[0].set(xticks=range(4),xlabel='Child ell',ylabel='Amplitude',title='Children: 1, 2, 4, 1',ylim=(0,4.9))
    axs[1].bar(range(4),energy,color=[COLORS[0],COLORS[1],COLORS[1],COLORS[1]])
    for j,e in enumerate(energy):axs[1].text(j,e+.35,f'{e:g}',ha='center',fontsize=12)
    axs[1].set(xticks=range(4),xlabel='DFT channel j',ylabel='Squared amplitude',title='DC and details share total energy 22',ylim=(0,19))
    save_figure(fig,'F04_unitary_detail_bank')
    assert np.isclose(energy.sum(),22);checks['F04']={'children':[1,2,4,1],'channel_energies':energy.tolist(),'total':22}

    z=np.linspace(0,2,300);poly=sum(z**n/factorial(n) for n in range(13));tail=np.exp(z)-poly;bound=np.exp(z)*z**13/factorial(13)
    reconstructed=sum(z**r*sum((z**3)**m/factorial(3*m+r) for m in range(5) if 3*m+r<=12) for r in range(3))
    assert np.allclose(poly,reconstructed,atol=5e-15)
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')
    axs[0].plot(z,np.exp(z),label='exp(z)');axs[0].plot(z,poly,ls='--',color=COLORS[1],label='Degree 12 / reconstructed')
    axs[0].set(xlabel='Real z',ylabel='Function value',title='The finite routing identity is exact');axs[0].legend()
    axs[1].plot(z,tail*1e6,label='Actual remainder');axs[1].plot(z,bound*1e6,ls='--',label='Taylor bound')
    axs[1].set(xlabel='Real z',ylabel='Remainder in millionths',title='The analytic truncation is a different question');axs[1].legend()
    save_figure(fig,'F05_identity_and_truncation')
    checks['F05']={'degree':12,'real_domain':[0,2],'max_routing_error':float(np.max(np.abs(poly-reconstructed))),'uniform_taylor_bound':float(np.exp(2)*2**13/factorial(13))}

    phase=np.linspace(-np.pi,np.pi,401);power=np.abs(.8+.6*np.exp(1j*phase))**2
    fig,ax=plt.subplots(figsize=(8.1,4.2),layout='constrained')
    ax.plot(phase,power,label='Coherent power');ax.axhline(1,color=COLORS[1],ls='--',label='Diagonal energy = 1')
    ax.set(xlabel='Relative phase phi (radians)',ylabel='Squared magnitude',title='The same component energies can interfere differently',ylim=(0,2.2),xticks=[-np.pi,-np.pi/2,0,np.pi/2,np.pi])
    ax.set_xticklabels(['-pi','-pi/2','0','pi/2','pi']);ax.legend();ax.grid()
    save_figure(fig,'F06_phase_and_power')
    checks['F06']={'amplitudes':['4/5','3/5'],'diagonal_energy':1,'minimum':'1/25','maximum':'49/25'}

    nodes=[F(0),F(2,5),F(17,20)];weights=[F(1,5),F(3,10),F(1,2)]
    moments=[sum(w*x**k for x,w in zip(nodes,weights)) for k in range(9)]
    H=np.array([[float(moments[i+j]) for j in range(3)] for i in range(3)])
    det=weights[0]*weights[1]*weights[2]*np.prod([nodes[j]-nodes[i] for i in range(3) for j in range(i+1,3)])**2
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')
    axs[0].vlines([float(x) for x in nodes],0,[float(w) for w in weights],color=COLORS[0],lw=3)
    axs[0].scatter([float(x) for x in nodes],[float(w) for w in weights],s=60,color=COLORS[0])
    axs[0].set(xlabel='Atom x',ylabel='Weight',title='A finite positive measure',xlim=(-.07,1),ylim=(0,.6))
    axs[1].plot(range(9),[float(v) for v in moments],marker='o');axs[1].set(xlabel='Moment index k',ylabel='E(k)',title='Moments sample the same measure',xticks=range(9));axs[1].grid()
    save_figure(fig,'F07_measure_and_moments')
    assert np.linalg.eigvalsh(H).min()>0
    checks['F07']={'nodes':list(map(str,nodes)),'weights':list(map(str,weights)),'moments':list(map(str,moments)),'H3_determinant':str(det),'H3_min_eigenvalue':float(np.linalg.eigvalsh(H).min()),'finite_support_rank':3}

    a=np.linspace(.51,3,250)
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.2),layout='constrained')
    for beta in [1,2,3]:axs[0].plot(a,(2*a-1)/beta,label=f'beta = {beta}')
    axs[0].axvspan(.5,1,color=COLORS[1],alpha=.09);axs[0].axvline(1,color=MUTED,ls=':')
    axs[0].set(xlabel='Arithmetic decay a',ylabel='Shape alpha',title='Energy domain: a > 1/2',xlim=(.5,3));axs[0].legend()
    axs[1].axis('off')
    table=axs[1].table(cellText=[['2','2','3/2','3/4'],['3/2','1','2','1'],['5/4','3','1/2','1/4']],colLabels=['a','beta','alpha','kappa'],loc='center',cellLoc='center')
    table.auto_set_font_size(False);table.set_fontsize(13);table.scale(1,2.2)
    axs[1].set_title('Shape bridge\nalpha = 2 kappa')
    save_figure(fig,'F08_parameter_domains')
    checks['F08']={'parameter_examples':[['2','2','3/2','3/4'],['3/2','1','2','1'],['5/4','3','1/2','1/4']],'signed_absolute_domain':'a>1','positive_energy_domain':'a>1/2'}
    (ROOT/'evidence/foundation_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps({'foundation_figures':8,'checks':'passed'}))

if __name__=='__main__':main()
