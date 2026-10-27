"""Exact mathematical vector artwork for Paper XI; no generated raster imagery.

Run with --output-dir PATH. Underlying finite data are serialized to figure_data.json.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.colors import ListedColormap

BLUE='#173e58'; TEAL='#087f8c'; GOLD='#bd873a'; RED='#aa4d45'; LIGHT='#edf3f5'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'pdf.fonttype':42,
 'ps.fonttype':42,'axes.unicode_minus':False,'figure.facecolor':'white',
 'savefig.facecolor':'white','text.color':BLUE,'axes.labelcolor':BLUE,
 'xtick.color':BLUE,'ytick.color':BLUE})

def canvas(h=4):
    fig, ax=plt.subplots(figsize=(8.8,h)); ax.set_xlim(0,10); ax.set_ylim(0,h)
    ax.axis('off'); return fig,ax
def box(ax,x,y,w,h,txt,color=BLUE,fill=LIGHT,size=12):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',
       edgecolor=color,facecolor=fill,linewidth=1.5))
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=size)
def arrow(ax,a,b,color=TEAL,style='-|>',rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,color=color,mutation_scale=15,
      linewidth=1.6,connectionstyle=f'arc3,rad={rad}'))
def save(fig,out,name):
    fig.tight_layout(pad=.35)
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)
def mobius(n):
    c=0; p=2
    while p*p<=n:
        if n%p==0:
            n//=p;c+=1
            if n%p==0:return 0
        p+=1
    if n>1:c+=1
    return (-1)**c
def orbit_count(q,n):
    return sum(mobius(d)*(q**(n//d)-1) for d in range(1,n+1) if n%d==0)//n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=Path(__file__).parent/'figures')
    out=ap.parse_args().output_dir;out.mkdir(parents=True,exist_ok=True); data={}

    f,a=canvas(4.5)
    for x,y,t in [(1,3.1,'Weil atoms'),(6.2,3.1,'Monodromy chains'),(1,1.1,'Finite packet comparison'),(6.2,1.1,'Actual arithmetic realization')]:box(a,x,y,2.8,.9,t,size=11)
    arrow(a,(3.8,3.55),(6.1,3.55));arrow(a,(2.4,3),(2.4,2.05));
    arrow(a,(3.85,1.55),(6.1,1.55),color=GOLD)
    a.text(5,2.08,'Conjectural realization',ha='center',fontsize=10,color=GOLD)
    a.text(5,.45,'The finite comparison does not create the arithmetic witness.',ha='center',fontsize=12)
    save(f,out,'01_three_objects')

    f,a=canvas(4.3)
    for j in range(5):
        x=.55+j*1.9;box(a,x,1.6,1.25,.9,rf'$V_{j}$'+'\n'+rf'$q^{j}$')
        if j>0:arrow(a,(x-.08,2.05),(x-.62,2.05))
    a.text(5,3.5,r'$F=\mathrm{diag}(1,q,q^2,q^3,q^4),\qquad FNF^{-1}=q^{-1}N$',ha='center')
    a.text(5,.65,r'$N(V_j)\subseteq V_{j-1};\qquad N^5=0$',ha='center');save(f,out,'02_monodromy')

    f,a=plt.subplots(figsize=(7,5));a.set_aspect('equal');a.axis('off');a.set_xlim(-1.8,1.8);a.set_ylim(-1.5,1.5)
    pts=[(math.cos(2*math.pi*j/4),math.sin(2*math.pi*j/4)) for j in range(4)]
    for j,(x,y) in enumerate(pts):
        a.add_patch(Circle((x,y),.23,edgecolor=BLUE,facecolor=LIGHT,lw=1.5));a.text(x,y,str([1,2,4,8][j]),ha='center',va='center')
        v=pts[(j+1)%4];arrow(a,(.78*x+.22*v[0],.78*y+.22*v[1]),(.22*x+.78*v[0],.22*y+.78*v[1]))
    a.text(0,0,'× 2\nmod 15',ha='center',va='center');save(f,out,'03_tame_orbit')

    data['orbit_counts']={str(q):[orbit_count(q,n) for n in range(1,9)] for q in [2,3,5]}
    f,a=plt.subplots(figsize=(8.8,4.3))
    for q,c in zip([2,3,5],[TEAL,BLUE,GOLD]):a.plot(range(1,9),data['orbit_counts'][str(q)],'o-',label=f'q={q}',color=c,lw=2)
    a.set_yscale('log');a.set_xticks(range(1,9));a.set_xlabel('Exact Frobenius orbit length n');a.set_ylabel('Number of regular orbits');a.grid(alpha=.2);a.legend();save(f,out,'04_orbit_counts')

    grid=[[(i-j)%2 for j in range(6)] for i in range(4)];data['tensor_4_6']=grid
    f,a=plt.subplots(figsize=(8.8,4.8));a.imshow(grid,cmap=ListedColormap([LIGHT,'#acd6d6']),vmin=0,vmax=1)
    for i in range(4):
        for j in range(6):a.text(j,i,str(grid[i][j]),ha='center',va='center',fontsize=15)
    a.set_xticks(range(6));a.set_yticks(range(4));a.set_xlabel('Z/6Z');a.set_ylabel('Z/4Z');a.set_xticks([j-.5 for j in range(7)],minor=True);a.set_yticks([i-.5 for i in range(5)],minor=True);a.grid(which='minor',color='white',lw=2);a.tick_params(which='minor',bottom=False,left=False);save(f,out,'05_tensor_grid')

    f,a=canvas(4)
    for j in range(4):box(a,.6+2.25*j,1.6,1.3,.75,rf'$e_{j}$')
    for j in range(3):arrow(a,(1.95+2.25*j,1.98),(2.75+2.25*j,1.98))
    arrow(a,(8.85,1.5),(1.2,1.5),color=GOLD,rad=-.10)
    a.text(5,.55,r'Closing edge $a$:  characteristic polynomial $X^4-a$',ha='center');save(f,out,'06_cycle_scalar')

    f,a=canvas(5)
    box(a,.7,3.35,3.5,1,r'$X$ translations'+'\n'+r'$T_x f(u)=f(u+x)$')
    box(a,5.8,3.35,3.5,1,r'$X^*$ multipliers'+'\n'+r'$M_\xi f(u)=\psi(\xi(u))f(u)$')
    box(a,2.7,1.2,4.6,1.2,r'$\mathcal{H}=\mathbf{C}^X$'+'\n'+r'$T_xM_\xi=\psi(\xi(x))M_\xi T_x$')
    arrow(a,(2.45,3.2),(4.05,2.6));arrow(a,(7.55,3.2),(5.95,2.6));a.text(5,.45,'Noncommuting operators generate the full matrix algebra.',ha='center');save(f,out,'07_heisenberg')

    f,a=canvas(4)
    box(a,.4,1.7,2.8,.95,'Projective action\n'+r'$T_aT_b=c(a,b)T_{a+b}$',size=11)
    box(a,3.7,1.7,2.6,.95,'Scalar commutator\n'+r'$b_c(a,b)$',size=11)
    box(a,6.9,1.7,2.7,.95,'Symplectic quotient\n'+r'$A/\mathrm{rad}(b_c)$',size=11)
    arrow(a,(3.25,2.17),(3.6,2.17));arrow(a,(6.35,2.17),(6.8,2.17));a.text(5,.55,'Radical directions commute with every projective generator.',ha='center');save(f,out,'08_radical')

    f,a=canvas(5)
    box(a,.7,3.55,3.2,.85,r'$(V_\rho,b_\rho)$');box(a,6.1,3.55,3.2,.85,r'$(V_\theta,h_\theta)$')
    box(a,.7,1.15,3.2,.85,r'$\omega_\rho$');box(a,6.1,1.15,3.2,.85,r'$\omega_\theta$')
    arrow(a,(3.95,3.98),(6.0,3.98));a.text(5,4.35,r'$\iota$: equivariant isometry',ha='center',fontsize=11)
    arrow(a,(2.3,3.4),(2.3,2.15));arrow(a,(7.7,3.4),(7.7,2.15))
    arrow(a,(3.95,1.57),(6.0,1.57));a.text(5,2.05,r'$U$: unique up to scalar',ha='center',fontsize=11)
    a.text(5,.35,'A cyclic generator phase removes the discrepancy character.',ha='center');save(f,out,'09_bridge')

    data['quadratic_planes']=[{'x':x,'y':y,'q0':x*y%2,'q1':(x*y+x+y)%2} for x,y in [(0,0),(1,0),(0,1),(1,1)]]
    f,axs=plt.subplots(1,2,figsize=(8.8,4))
    for ax,k,title in zip(axs,['q0','q1'],[r'$q_0(x,y)=xy$',r'$q_1(x,y)=xy+x+y$']):
        ax.set_xlim(-.5,1.5);ax.set_ylim(-.5,1.5);ax.set_aspect('equal');ax.set_xticks([0,1]);ax.set_yticks([0,1]);ax.set_xlabel('x');ax.set_ylabel('y');ax.set_title(title,pad=15)
        for z in data['quadratic_planes']:
            ax.scatter(z['x'],z['y'],s=1000,color=TEAL if z[k]==0 else RED,zorder=3);ax.text(z['x'],z['y'],str(z[k]),ha='center',va='center',color='white',fontsize=16)
        ax.grid(alpha=.2)
    save(f,out,'10_quadratic_planes')

    data['arf_counts']=[{'r':r,'zero':2**(r-1)*(2**r+1),'one':2**(r-1)*(2**r-1)} for r in range(1,6)]
    f,a=plt.subplots(figsize=(8.8,4.2));r=range(1,6)
    a.bar([i-.18 for i in r],[z['zero'] for z in data['arf_counts']],width=.36,color=TEAL,label='Arf 0')
    a.bar([i+.18 for i in r],[z['one'] for z in data['arf_counts']],width=.36,color=GOLD,label='Arf 1')
    a.set_yscale('log');a.set_xticks(list(r));a.set_xlabel('Half dimension r');a.set_ylabel('Number of refinements');a.legend();save(f,out,'11_arf_counts')

    f,a=canvas(5.3);pts={'r':(1,2.65),'u':(4.3,4),'v':(8.6,3.2),'w':(5.2,.85)}
    edges=[('r','u'),('u','v'),('r','w')]
    for s,t in edges:
        x,y=pts[s];u,v=pts[t];a.plot([x,u],[y,v],color=TEAL,lw=3,zorder=1)
    for s,t in [('v','w'),('u','w')]:
        x,y=pts[s];u,v=pts[t];a.plot([x,u],[y,v],color=GOLD,lw=2,ls='--',zorder=1)
    for z,(x,y) in pts.items():a.add_patch(Circle((x,y),.28,facecolor=LIGHT,edgecolor=BLUE,lw=1.5,zorder=3));a.text(x,y,z,ha='center',va='center',zorder=4)
    a.text(5,4.85,'Solid tree: fix gauges.  Dashed chords: test cycles.',ha='center',fontsize=12);save(f,out,'12_holonomy')

    f,a=canvas(4.5)
    for j in range(3):
        box(a,.6+j*3.2,2.55,2.4,.9,rf'$V_{{s_{j+1}}}$'+'\n'+rf'$\omega_{{s_{j+1}}}$')
    a.text(5,1.55,r'$V=V_{s_1}\perp V_{s_2}\perp V_{s_3}$',ha='center',fontsize=15)
    a.text(5,.65,r'$\omega_V\simeq\omega_{s_1}\otimes\omega_{s_2}\otimes\omega_{s_3}$',ha='center',fontsize=15);save(f,out,'13_break_tensor')

    f,a=canvas(5)
    box(a,.65,3.25,3.5,1.0,'Native parameter field\n'+r'$E=L(\alpha)$')
    box(a,5.85,3.25,3.5,1.0,'Derived parameter\n'+r'$C\in M_m(E)$')
    box(a,2.7,1.0,4.6,1.1,'Actual ambient matrix\n'+r'$B=\alpha I_m+\mathrm{Lift}_E(C)$')
    arrow(a,(2.4,3.1),(4.15,2.25));arrow(a,(7.6,3.1),(5.85,2.25))
    a.text(5,.35,'The derived field and the final field are not identified.',ha='center');save(f,out,'14_recursive_parameter')

    data['levels']={'dyadic':[60,18,3],'odd_p3':[144,24,4]}
    f,axs=plt.subplots(1,2,figsize=(8.8,4.5))
    for ax,levels,base,title in zip(axs,[[60,18,3],[144,24,4]],[2,3],[r'$p=2,\ h=(1,3,5)$',r'$p=3,\ h=(1,2,4)$']):
        ax.plot([base,base**2,base**3],levels,'o-',color=TEAL,lw=2);ax.set_xticks([base,base**2,base**3]);ax.set_xlabel('Approximation-field degree');ax.set_ylabel('Critical level');ax.set_title(title);ax.grid(alpha=.2)
        for x,y in zip([base,base**2,base**3],levels):ax.annotate(str(y),(x,y),xytext=(5,5),textcoords='offset points',fontsize=11)
    save(f,out,'15_degree_levels')

    f,a=canvas(4.7)
    box(a,.55,2.6,2.7,1.0,r'$\mathrm{tr}\delta=0$'+'\n'+'odd trace-zero tower')
    box(a,6.75,2.6,2.7,1.0,r'$\mathrm{tr}\delta=1$'+'\n'+'dyadic native tower')
    box(a,2.8,.75,4.4,1.1,r'$v_F(\mathrm{tr}\delta)+s\geq1$'+'\n'+r'$\psi_F((u-1)\mathrm{tr}\delta)=1$')
    arrow(a,(1.9,2.45),(3.65,2));arrow(a,(8.1,2.45),(6.35,2));save(f,out,'16_scalar_depth')

    f,a=canvas(4.4)
    for j in range(3):
        box(a,.55+3.2*j,2.65,2.4,.75,rf'Native rank ${2**(j+1)}$: trace $1$')
        box(a,.55+3.2*j,1.25,2.4,.75,rf'In rank $8$: trace ${[0,0,1][j]}$')
        arrow(a,(1.75+3.2*j,2.5),(1.75+3.2*j,2.1))
    a.text(5,.35,'Native trace and amplified ambient trace have different roles.',ha='center');save(f,out,'17_native_ambient_trace')

    data['dyadic_capacity']=[{'d':d,'rank':2**d,'host_symplectic':2**d-2,'source_symplectic':2*d,'host_carrier':2**(2**(d-1)-1),'source_carrier':2**d} for d in range(1,6)]
    f,a=plt.subplots(figsize=(8.8,4.7));xs=list(range(1,6))
    a.bar([x-.2 for x in xs],[2**x-2 for x in xs],width=.4,color=TEAL,label=r'Original quotient $N-2$')
    a.bar([x+.2 for x in xs],[2*x for x in xs],width=.4,color=GOLD,label=r'Whole source $2d$')
    a.set_xticks(xs,[f'd={d}\nN={2**d}' for d in xs]);a.set_ylabel('Symplectic dimension over F₂');a.legend();a.grid(axis='y',alpha=.2);save(f,out,'18_capacity')

    f,a=canvas(5)
    box(a,.55,3.25,2.6,1.0,'Original compact type\n'+r'$(J,\eta)$')
    box(a,6.85,3.25,2.6,1.0,'Enlarged compact group\n'+r'$(P,E=\mathrm{Ind}_J^P\eta)$',size=11)
    box(a,2.6,.8,4.8,1.1,'Same supercuspidal candidate\n'+r'$\pi=\mathrm{c\!-\!Ind}_{K^\times J}^G\Lambda$',size=11)
    arrow(a,(3.25,3.75),(6.7,3.75));a.text(5,4.1,r'$[P:J]=2$',ha='center',fontsize=11)
    arrow(a,(1.9,3.1),(3.8,2.1));arrow(a,(8.1,3.1),(6.2,2.1));save(f,out,'19_enlarged_carrier')

    f,a=canvas(4.8)
    box(a,.55,3.15,2.6,.85,r'$\mathcal{N}=K^\times J$')
    box(a,6.85,3.15,2.6,.85,r'$\mathcal{M}=K^\times P$')
    box(a,.55,.9,2.6,.85,r'$\Lambda$');box(a,6.85,.9,2.6,.85,r'$\Sigma=\mathrm{Ind}_{\mathcal{N}}^{\mathcal{M}}\Lambda$',size=11)
    arrow(a,(3.25,3.58),(6.7,3.58));arrow(a,(3.25,1.32),(6.7,1.32))
    a.text(5,2.35,r'$\pi\simeq\mathrm{c\!-\!Ind}_{\mathcal{M}}^G\Sigma$',ha='center',fontsize=15);save(f,out,'20_induction_stages')

    f,a=canvas(4.6)
    box(a,.55,2.7,3.6,1.0,'Marked source extension\n'+'finite subgroup + lifts + squares')
    box(a,5.85,2.7,3.6,1.0,'Marked image in scalar pushout\n'+r'$F_0(a)^2=F_0(a^2)$',size=11)
    arrow(a,(4.3,3.2),(5.7,3.2));a.text(5,1.55,'The whole finite subgroup travels through the map.',ha='center')
    a.text(5,.65,'A separately fixed native marking needs its own comparison.',ha='center',color=GOLD);save(f,out,'21_marked_extension')

    f,a=canvas(4.8)
    box(a,.6,3.15,3.3,1.0,'Finite compact packet\n'+r'$d_\rho$')
    box(a,6.1,3.15,3.3,1.0,'Noncompact completion\n'+'central character + root')
    box(a,2.7,.9,4.6,1.15,'One actual candidate\n'+r'$R(d_\rho,\pi)$')
    arrow(a,(2.25,3),(4.05,2.2));arrow(a,(7.75,3),(5.95,2.2));save(f,out,'22_completion')

    f,a=canvas(5.1)
    box(a,.6,3.55,3.5,1.0,'H1–H4 finite datum\n'+r'$d_\rho$')
    box(a,5.9,3.55,3.5,1.0,'Arithmetic witness\n'+r'$R(d_\rho,\pi)$',color=GOLD)
    box(a,.6,.95,3.5,1.0,'H5 for this same candidate\n'+'tested pair factors')
    box(a,5.9,.95,3.5,1.0,'Conditional comparison\n'+r'$\pi\simeq\mathrm{LLC}(\rho)$')
    arrow(a,(4.25,4.05),(5.75,4.05),color=GOLD);a.text(5,4.6,'Conjecture 66',ha='center',color=GOLD,fontsize=11)
    arrow(a,(7.65,3.4),(7.65,2.1));arrow(a,(4.25,1.45),(5.75,1.45));save(f,out,'23_conjecture_boundary')
    (out/'figure_data.json').write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':main()
