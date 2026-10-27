"""Exact data and explicitly schematic mathematical figures for Series 07."""
from pathlib import Path
import json, sys, importlib.util, math
from collections import defaultdict
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'shared/figures'
OUT.mkdir(parents=True,exist_ok=True)
DAT=json.loads((ROOT/'evidence/computation/tau_plot_data_512.json').read_text())
TAU={r['n']:r['tau'] for r in DAT['rows']}
P=[r for r in DAT['rows'] if r['prime']]
PATH=ROOT/'historical/Lehmer_Final_Push_2026-09-26/lehmer_final_push/checks/packet_core.py'
spec=importlib.util.spec_from_file_location('packet_core',PATH)
pc=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)
INK='#243138'; TEAL='#21676B'; COPPER='#A45C36'; GRAY='#627078'; SOFT='#E9F0EF'; RED='#A04444'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':INK,'text.color':INK,'axes.edgecolor':GRAY,'xtick.color':GRAY,'ytick.color':GRAY,'pdf.fonttype':42,'ps.fonttype':42})
MAP=[]
def canvas(name,wide=False):
    f,ax=plt.subplots(figsize=(6.8,4.25))
    f.subplots_adjust(left=.12,right=.97,bottom=.17,top=.95)
    MAP.append(name)
    return f,ax

def save(f,name):
    f.savefig(OUT/(name+'.pdf'),facecolor='white')
    f.savefig(OUT/(name+'.png'),dpi=170,facecolor='white')
    plt.close(f)

def clean(ax):
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')

def box(ax,x,y,w,h,text,color=TEAL,size=12):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.016,rounding_size=.015',linewidth=1,edgecolor=color,facecolor=SOFT if color==TEAL else '#F5EDE8'))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,color=INK,linespacing=1.5)

def arrow(ax,a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':GRAY,'lw':1.6})

def note(ax,s,y=.02):ax.text(.5,y,s,ha='center',va='bottom',fontsize=10,color=GRAY)

def chi(n):return 0 if n%5==0 else (1 if n%5 in [1,4] else -1)
def vp(n,p):
    if n==0:return None
    k=0
    while n%p==0:n//=p;k+=1
    return k

def residual(n):
    return sum(pc.weight(v) for v in pc.shell(n) if math.gcd(*v)==1)

def orbits(n):
    d={}
    for v in pc.shell(n):
        key=min(v,pc.involution(v));d[key]=d.get(key,0)+pc.weight(v)
    assert sum(d.values())==TAU[n]
    return d

f,ax=canvas('tau_product');clean(ax)
box(ax,.05,.68,.90,.22,r'$\Delta(q)=q\prod_{m\geq1}(1-q^m)^{24}$',size=20)
arrow(ax,(.5,.66),(.5,.53))
box(ax,.08,.30,.84,.20,r'$q-24q^2+252q^3-1472q^4+\cdots$',size=17)
ax.text(.5,.16,r'$\tau(n)=[q^n]\Delta(q)$',ha='center',fontsize=19)
note(ax,'Fixed modular form. Positive integer index n.')
save(f,'tau_product')

f,ax=canvas('coefficient_methods');clean(ax)
for x,t in [(0.03,'Defining product\nExact binomial factors'),(.35,'Triangular recurrence\nJacobi identity'),(.67,'Divisor recurrence\nLogarithmic derivative')]:box(ax,x,.60,.27,.27,t,size=11)
for x in [.16,.48,.80]:arrow(ax,(x,.57),(.48,.31))
box(ax,.21,.12,.57,.19,'512 identical integer coefficients\n512 nonzero values',size=14)
save(f,'coefficient_methods')

f,ax=canvas('coefficients512');ns=np.arange(1,513);vals=[math.copysign(math.log10(abs(TAU[n])+1),TAU[n]) for n in ns]
ax.scatter(ns,vals,s=10,c=[TEAL if v>0 else COPPER for v in vals],alpha=.75)
ax.axhline(0,color=GRAY,lw=.8);ax.set_xlabel('Integer index n');ax.set_ylabel(r'$\mathrm{sgn}(\tau(n))\log_{10}(1+|\tau(n)|)$')
ax.text(.03,.94,'Exact integer inputs, transformed for display',transform=ax.transAxes,fontsize=10)
save(f,'coefficients512')

f,ax=canvas('prime_bound');ps=[r['n'] for r in P];norm=[r['plot_normalized_tau'] for r in P]
ax.scatter(ps,norm,s=18,c=TEAL);ax.axhline(1,color=COPPER,lw=1);ax.axhline(-1,color=COPPER,lw=1);ax.axhline(0,color=GRAY,lw=.8)
ax.set_ylim(-1.16,1.16);ax.set_xlabel('Prime p, through 512');ax.set_ylabel(r'$\tau(p)/(2p^{11/2})$');ax.text(.03,.995,'Deligne: absolute value at most 1',transform=ax.transAxes,va='top',fontsize=10)
save(f,'prime_bound')

f,ax=canvas('multiplicativity');clean(ax)
box(ax,.33,.76,.34,.15,r'$12=2^2\cdot3$',size=19)
arrow(ax,(.39,.73),(.23,.53));arrow(ax,(.61,.73),(.77,.53))
box(ax,.04,.30,.38,.21,r'$\tau(4)=-1472$',size=16);box(ax,.58,.30,.38,.21,r'$\tau(3)=252$',size=16)
arrow(ax,(.23,.28),(.40,.15));arrow(ax,(.77,.28),(.60,.15))
ax.text(.5,.08,r'$\tau(12)=(-1472)(252)=-370944$',ha='center',fontsize=16)
assert TAU[12]==-370944
save(f,'multiplicativity')

f,ax=canvas('hecke_recurrence');clean(ax)
box(ax,.03,.73,.25,.15,r'$T_{r-2}$',size=20);box(ax,.375,.73,.25,.15,r'$T_{r-1}$',size=20);box(ax,.72,.73,.25,.15,r'$T_r$',size=20)
arrow(ax,(.62,.70),(.78,.46));arrow(ax,(.15,.70),(.64,.46))
box(ax,.20,.28,.75,.18,r'$T_r=aT_{r-1}-p^{11}T_{r-2}$',size=17)
ax.text(.5,.14,r'$T_0=1,\quad T_1=a=\tau(p)$',ha='center',fontsize=16)
note(ax,'Fixed prime p. Recurrence varies the exponent r, not the prime.')
save(f,'hecke_recurrence')

f,ax=canvas('prime_reduction');clean(ax)
box(ax,.04,.70,.92,.20,r'$\tau(p^m)=0\ \Longrightarrow\ \alpha/\beta=\zeta$'+'\nHecke root ratio is a root of unity',size=15)
arrow(ax,(.5,.67),(.5,.54))
box(ax,.04,.30,.92,.20,r'$\tau(p)^2/p^{11}=2+\zeta+\zeta^{-1}\in\{0,1,2,3,4\}$',size=16)
arrow(ax,(.5,.28),(.5,.17))
ax.text(.5,.09,r'$\tau(p)=0$'+'   (nonzero alternatives excluded)',ha='center',fontsize=16)
save(f,'prime_reduction')

f,ax=canvas('parity');ns=range(1,82);odd=[n for n in ns if TAU[n]%2];assert odd==[1,9,25,49,81]
ax.set_xlim(0,82);ax.set_ylim(-.5,1.5);ax.set_yticks([0,1],['even','odd']);ax.scatter(list(ns),[TAU[n]%2 for n in ns],c=[COPPER if TAU[n]%2 else TEAL for n in ns],s=22)
for n in odd:ax.text(n,1.12,str(n),ha='center',fontsize=10)
ax.set_xticks([0,20,40,60,80]);ax.set_xlabel('Index n through 81');ax.text(.5,.95,'Odd coefficients occur exactly at odd squares',transform=ax.transAxes,ha='center',fontsize=12)
save(f,'parity')

f,ax=canvas('fivecore_hooks');clean(ax)
def young(x,y,rows,scale=.065):
    for i,row in enumerate(rows):
        for j in range(row):
            h=row-j+sum(1 for lower in rows[i+1:] if lower>j)
            ax.add_patch(Rectangle((x+j*scale,y-i*scale),scale,scale,fc=SOFT if h!=5 else '#F2D5C4',ec=GRAY,lw=1))
            ax.text(x+(j+.5)*scale,y+(.5-i)*scale,str(h),ha='center',va='center',fontsize=11)
young(.11,.70,[4,1,1],.105);young(.10,.27,[6],.105)
ax.text(.59,.72,'(4,1,1) is a 5-core\nNo hook has length 5',fontsize=12,va='center')
ax.text(.12,.18,'(6) has a hook of length 5',fontsize=12)
ax.text(.50,.03,r'At $z=25$:  $\prod_{h}(1-25/h^2)$',ha='center',fontsize=16)
save(f,'fivecore_hooks')

v2=list(pc.shell(2))[0];assert pc.weight(v2)==-24
f,ax=canvas('shell_coordinates');xs=np.arange(5)
ax.bar(xs,v2,color=[TEAL if x>=0 else COPPER for x in v2],width=.6)
for i,x in enumerate(v2):ax.text(i,x+(.3 if x>=0 else -.3),str(x),ha='center',va='bottom' if x>=0 else 'top',fontsize=12)
ax.axhline(0,color=GRAY,lw=.8);ax.set_xticks(xs,[r'$v_0$',r'$v_1$',r'$v_2$',r'$v_3$',r'$v_4$']);ax.set_ylabel('Integer coordinate')
ax.set_ylim(min(v2)-2,max(v2)+2);ax.text(.03,.95,r'$\sum v_i=0,\quad \sum v_i^2=20$',transform=ax.transAxes,va='top',fontsize=13)
ax.text(.03,.86,r'$v_i\equiv i\ (\mathrm{mod}\ 5)$',transform=ax.transAxes,va='top',fontsize=12)
save(f,'shell_coordinates')

f,ax=canvas('vandermonde');clean(ax)
box(ax,.04,.68,.92,.22,r'$W(v)=\frac{\prod_{i<j}(v_i-v_j)}{1!\,2!\,3!\,4!}$',size=20)
ax.text(.5,.50,r'$W(v)=\det\!\left[\binom{v_i}{j}\right]_{i,j=0}^{4}\in\mathbb{Z}$',ha='center',fontsize=19)
ax.text(.5,.31,'Distinct residues modulo 5 make every factor nonzero',ha='center',fontsize=12)
ax.text(.5,.15,r'$W(v)\equiv1\ (\mathrm{mod}\ 5)$',ha='center',fontsize=18)
save(f,'vandermonde')

for n,name in [(7,'orbit7'),(31,'orbit31')]:
    d=orbits(n);m=list(d.values());f,ax=canvas(name)
    if n==31:f.subplots_adjust(left=.18)
    ax.set_xticks([1,2,3] if n==7 else [1,4,8,12,16])
    ax.bar(range(1,len(m)+1),np.array(m)/1000,color=[TEAL if x>0 else COPPER for x in m]);ax.axhline(0,color=GRAY,lw=.8)
    ax.set_xlabel('J-orbit in lexicographic representative order');ax.set_ylabel('Exact orbit mass / 1000')
    ax.text(.03,.96,f'{len(m)} orbits. Total = {TAU[n]:,}',transform=ax.transAxes,va='top',fontsize=11)
    if n==7:
        for i,x in enumerate(m,1):ax.text(i,x/1000+(1 if x>0 else -1),f'{x:,}',ha='center',va='bottom' if x>0 else 'top',fontsize=10)
        ax.margins(y=.27)
    save(f,name)

f,ax=canvas('packet_count');pp=[r['n'] for r in P if r['n']!=5];de=[chi(p) for p in pp]
ax.scatter(pp,de,c=[TEAL if x>0 else COPPER for x in de],s=20);ax.set_yticks([-1,1]);ax.set_ylim(-1.5,1.5);ax.set_xlabel('Prime p, with p not equal to 5');ax.set_ylabel('Packet count minus p')
ax.text(.5,.95,r'$|\mathcal{V}_p|=p+\chi_5(p)$',transform=ax.transAxes,ha='center',va='top',fontsize=17)
save(f,'packet_count')

f,ax=canvas('content121');m1=-25439104668;m11=25937424601;assert m1+m11==TAU[121]
ax.bar([0,1,2],[m1/1e9,m11/1e9,TAU[121]/1e9],color=[COPPER,TEAL,GRAY],width=.55)
ax.axhline(0,color=GRAY,lw=.8);ax.set_xticks([0,1,2],['Content 1','Content 11','Total']);ax.set_ylabel('Exact mass / billion');ax.set_ylim(-33,34)
for i,x in enumerate([m1,m11,TAU[121]]):ax.text(i,x/1e9+(2 if x>=0 else -2),f'{x:,}',ha='center',va='bottom' if x>=0 else 'top',fontsize=10)
save(f,'content121')

f,ax=canvas('mobius_residual');clean(ax)
box(ax,.03,.67,.94,.22,r'$\tau(n)=\sum_{g^2\mid n}\chi_5(g)g^{10}R(n/g^2)$',size=18)
arrow(ax,(.5,.52),(.5,.46))
ax.text(.5,.58,'Möbius inversion on square divisors',ha='center',fontsize=12)
box(ax,.03,.20,.94,.22,r'$R(n)=\sum_{d^2\mid n}\mu(d)\chi_5(d)d^{10}\tau(n/d^2)$',size=17)
note(ax,r'$R(p)=\tau(p)$ at every prime. Extraction preserves the prime target.')
save(f,'mobius_residual')

f,ax=canvas('local_factor');clean(ax)
box(ax,.04,.63,.92,.25,r'$\sum_{r\geq0}R(p^r)X^r=\frac{1-\chi_5(p)p^{10}X^2}{1-\tau(p)X+p^{11}X^2}$',size=19)
ax.text(.5,.44,'Numerator removes the square-content contribution',ha='center',fontsize=12)
ax.text(.5,.26,r'$R(p^r)=\tau(p^r)-\chi_5(p)p^{10}\tau(p^{r-2})$'+'\nfor r at least 2',ha='center',fontsize=15)
note(ax,'Formal series in X at one fixed prime p.')
save(f,'local_factor')

f,ax=canvas('square_residuals');ss=list(range(1,23));vv=[residual(s*s) for s in ss];assert all(vv)
ax.scatter(ss,[math.copysign(math.log10(abs(x)+1),x) for x in vv],c=[TEAL if x>0 else COPPER for x in vv],s=35)
ax.axhline(0,color=GRAY,lw=.8);ax.set_xlabel('Square root s, through 22');ax.set_ylabel(r'$\mathrm{sgn}(R(s^2))\log_{10}(1+|R(s^2)|)$')
ax.text(.03,.96,'Project theorem: all squares have nonzero R',transform=ax.transAxes,va='top',fontsize=11)
save(f,'square_residuals')

f,ax=canvas('null_transfer');clean(ax)
# exact illustrative mass transfer, not packet data
for x,t,col in [(.06,'+6',TEAL),(.39,'−4',COPPER),(.72,'+1',TEAL)]:box(ax,x,.70,.22,.15,t,col,size=19)
ax.text(.5,.60,'Constructed mass vector. Conserved total = 3',ha='center',fontsize=12)
for x in [.17,.50,.83]:arrow(ax,(x,.46),(x,.31))
for x in [.06,.39,.72]:box(ax,x,.12,.22,.17,'+1',TEAL,size=19)
ax.text(.5,.50,'Allowed zero-total change: (−5, +5, 0)',ha='center',fontsize=12)
save(f,'null_transfer')

f,ax=canvas('interpolation');clean(ax)
box(ax,.04,.71,.92,.19,'Finite shell: prescribe values at every J-orbit',size=15)
arrow(ax,(.5,.68),(.5,.57))
box(ax,.10,.35,.80,.20,'Rational symmetric polynomial interpolation\nDegree 10(N − 1) is sufficient',size=13)
arrow(ax,(.5,.32),(.5,.19))
ax.text(.5,.08,'Universal nullness on every shell remains a separate condition',ha='center',fontsize=12,color=COPPER)
save(f,'interpolation')

f,ax=canvas('dyadic_tree');clean(ax)
box(ax,.37,.76,.26,.13,'Depth 0: all packets',size=11)
for x,t in [(.12,'Sector A'),(.63,'Sector B')]:
    box(ax,x,.46,.25,.14,t,size=12);arrow(ax,(.50,.73),(x+.125,.63))
for x,t in [(.02,'A1'),(.25,'A2'),(.51,'B1'),(.74,'B2')]:box(ax,x,.13,.20,.15,t,size=13)
for a,b in [((.245,.43),(.12,.31)),((.245,.43),(.35,.31)),((.755,.43),(.61,.31)),((.755,.43),(.84,.31))]:arrow(ax,a,b)
note(ax,'Schematic refinement. Actual child counts depend on the shell.')
save(f,'dyadic_tree')

f,ax=canvas('mixed_threshold');ks=list(range(1,9));N=[pc.threshold(k) for k in ks]
ax.plot(ks,N,'o-',color=TEAL);ax.set_yscale('log');ax.set_xlabel('Dyadic depth k');ax.set_ylabel('First mixed-sign shell Nₖ')
for k,n in zip(ks,N):ax.annotate(str(n),(k,n),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
ax.set_ylim(7,500000);ax.text(.05,.93,'Exact formula, not an empirical fit',transform=ax.transAxes,fontsize=11)
save(f,'mixed_threshold')

f,ax=canvas('sector7');d=defaultdict(int);q=defaultdict(int)
for v in pc.shell(7):s=pc.sector(v,2);d[s]+=pc.weight(v);q[s]+=pc.weight(v)*pc.q8(v)
keys=sorted(d);m=[d[k] for k in keys];assert m==[-1848,-17248,2352]
ax.bar(range(3),np.array(m)/1000,color=[COPPER,COPPER,TEAL]);ax.axhline(0,color=GRAY,lw=.8);ax.set_ylabel('Sector mass / 1000');ax.set_xticks(range(3),['00000','10010','11000']);ax.set_xlabel('Depth-1 residue key c modulo 2, modulo J')
for i,x in enumerate(m):ax.text(i,x/1000+(1 if x>0 else -1),f'{x:,}',ha='center',va='bottom' if x>0 else 'top',fontsize=11)
ax.margins(y=.3);save(f,'sector7')

f,ax=canvas('ranks31');deg=[14,20,22];rank=[5,14,15];ax.step(deg,rank,where='mid',color=TEAL,lw=2);ax.scatter(deg,rank,c=TEAL,s=40);ax.axhline(15,color=COPPER,lw=1,linestyle='--')
ax.set_xticks(deg);ax.set_ylim(0,17);ax.set_xlabel('Invariant degree cutoff in constructed family');ax.set_ylabel('Exact orbit transfer rank');ax.text(.02,.96,'p = 31: 16 orbits, 15 zero-total directions',transform=ax.transAxes,fontsize=11,va='top')
for x,y in zip(deg,rank):ax.text(x,y+.6,str(y),ha='center',fontsize=12)
save(f,'ranks31')

f,ax=canvas('auxiliary_roots');clean(ax)
box(ax,.03,.67,.94,.20,r'$P_n(5)=288\tau(n),\quad G_n(U)=5^{-\mu_n}P_n(5U)$',size=17)
box(ax,.03,.21,.44,.27,r'$p=499$'+'\n'+r'$\overline{G}(U)=2+3U^2$'+'\nSimple root at 1',size=14)
box(ax,.53,.21,.44,.27,r'$p=16249$'+'\n'+r'$\overline{G}(U)=(U-1)^2(U-2)$'+'\nDouble root at 1',size=13)
note(ax,'Auxiliary variable U. The target coefficient is evaluated at U = 1.')
save(f,'auxiliary_roots')

f,ax=canvas('lifting_failures');ells=['2 at p=81919','3 at p=8747','5 at p=499','5 at p=1249'];a=[20,8,4,3];b=[14,7,3,4];x=np.arange(4)
ax.bar(x-.16,a,.32,label=r'$v_\ell(\tau(p))$',color=TEAL);ax.bar(x+.16,b,.32,label=r'$v_\ell(p+1)$',color=COPPER)
ax.set_xticks(x,ells,rotation=16,ha='right',fontsize=10);ax.set_ylabel('Exact valuation');ax.legend(fontsize=11,frameon=False)
for xx,aa,bb in zip(x,a,b):ax.text(xx-.16,aa+.4,str(aa),ha='center',fontsize=11);ax.text(xx+.16,bb+.4,str(bb),ha='center',fontsize=11)
ax.set_ylim(0,24);save(f,'lifting_failures')

f,ax=canvas('trace_phi');clean(ax)
box(ax,.03,.68,.94,.21,r'$\varphi(e_1)=e_2,\qquad\varphi(e_2)=-p^{11}e_1$',size=17)
ax.text(.5,.48,r'$\operatorname{tr}\varphi=0,\quad\det\varphi=p^{11}$',ha='center',fontsize=17)
box(ax,.03,.16,.44,.19,'Hodge jumps\n0 and 11',size=14);box(ax,.53,.16,.44,.19,'Newton slopes\n11/2 and 11/2',size=14)
note(ax,'Constructed local filtered module. No global identification with Δ.')
save(f,'trace_phi')

f,ax=canvas('actual_survivors');clean(ax)
box(ax,.03,.73,.94,.15,'Choose a fixed modulus M',size=16)
arrow(ax,(.5,.69),(.5,.57))
box(ax,.03,.31,.94,.23,'Actual joint finite Galois image\nComplex conjugation: trace 0, cyclotomic value −1',size=13)
arrow(ax,(.5,.27),(.5,.16))
ax.text(.5,.08,r'$p\equiv-1\ (\mathrm{mod}\ 5M),\quad\tau(p)\equiv0\ (\mathrm{mod}\ M)$',ha='center',fontsize=17)
save(f,'actual_survivors')

f,ax=canvas('synthetic_model');clean(ax)
box(ax,.03,.71,.43,.18,'Actual prime parameters\naₚ = τ(p)',size=15)
box(ax,.54,.71,.43,.18,'Constructed parameters\n'+r'$a_q = 0,\ q > B$',color=COPPER,size=15)
arrow(ax,(.47,.80),(.52,.80))
ax.text(.5,.58,r'$q\equiv-1\ (\mathrm{mod}\ 50M),\quad\tau(q)\equiv0\ (\mathrm{mod}\ 10M)$',ha='center',fontsize=12)
box(ax,.08,.28,.84,.22,'Same coefficients through B\nSame residues modulo 10M at every n\nSame Hecke recurrence and size bound',size=13)
arrow(ax,(.50,.555),(.50,.525))
ax.text(.5,.09,'The weaker retained premises permit a prime zero',ha='center',fontsize=14,color=COPPER)
save(f,'synthetic_model')

f,ax=canvas('quantifiers');clean(ax)
box(ax,.03,.63,.94,.24,r'$\forall M\ \exists p:\quad M\mid\tau(p)$'+'\nDifferent moduli may use different primes',size=17)
ax.text(.5,.49,'does not imply',ha='center',fontsize=15,color=COPPER)
box(ax,.03,.13,.94,.24,r'$\exists p\ \forall M:\quad M\mid\tau(p)$'+'\nThis would force the same integer τ(p) to be zero',color=COPPER,size=16)
save(f,'quantifiers')

(OUT/'figure_map.json').write_text(json.dumps({'figure_names':MAP,'exact_data_source':'evidence/computation/tau_plot_data_512.json','plot_bound':512,'figure_count':len(MAP),'labels':'Every figure is identified as exact data, theorem illustration, or constructed schematic in the guide.'},indent=2)+'\n')
print(f'Wrote {len(MAP)} mathematical figures')
