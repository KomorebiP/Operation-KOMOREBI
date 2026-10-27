"""Eight deterministic visual experiments; finite checks accompany the pictures.

Run from the publication root: python tools/visual_companion/foundations.py
The checks concern these explicit examples, not the monograph's general results.
"""
from pathlib import Path
import itertools, json, sys, platform, hashlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from style import ROOT, PINE, INK, OCHRE, BLUE, MUTED, PALE, RED, GRID, tidy, save

plt.rcParams.update({'font.size':11, 'xtick.labelsize':10, 'ytick.labelsize':10,
                     'legend.fontsize':10, 'axes.labelsize':11})
SCENES=[]; CHECKS=[]; FIGURES=[]

def record(ident,title,setup,reading,experiment,labels,name):
    SCENES.append(dict(id=ident,title=title,setup_tex=setup,reading_tex=reading,
                       experiment_tex=experiment,monograph_labels=labels,figure=name+'.pdf'))

def check(name,passed,details):
    CHECKS.append(dict(name=name,passed=bool(passed),details=details))
    if not passed: raise AssertionError(name)

def base(title,subtitle=None):
    fig=plt.figure(figsize=(7,4.8))
    fig.suptitle(title,x=.05,y=.97,ha='left',fontsize=16,fontweight='medium')
    if subtitle: fig.text(.05,.895,subtitle,fontsize=11,color=MUTED)
    return fig

def done(fig,name): FIGURES.append(save(fig,name))

def spatial(ax,limits,labels=('x','y','z'),elev=22,azim=-55):
    ax.view_init(elev=elev,azim=azim)
    ax.set_xlim(*limits[0]);ax.set_ylim(*limits[1]);ax.set_zlim(*limits[2])
    ax.set_xlabel(labels[0],labelpad=4);ax.set_ylabel(labels[1],labelpad=4);ax.set_zlabel(labels[2],labelpad=4)
    ax.tick_params(pad=1,labelsize=10)
    ax.set_box_aspect([1,1,1])
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
        axis.pane.set_facecolor((1,1,1,0));axis.pane.set_edgecolor(GRID)
        axis._axinfo['grid']['color']=GRID
    return ax

def f01():
    name='f01_overlapping_views';p=np.array([2,1,3])
    fig=base('Which appearances belong to one point?','Shared coordinates are the overlap checks.')
    ax=fig.add_axes([.015,.11,.59,.70],projection='3d')
    spatial(ax,((0,4.3),(0,3.5),(0,4)),elev=23,azim=-60)
    planes=[[(0,0,0),(4,0,0),(4,3,0),(0,3,0)],[(0,0,0),(0,3,0),(0,3,4),(0,0,4)],[(0,0,0),(4,0,0),(4,0,4),(0,0,4)]]
    ax.add_collection3d(Poly3DCollection(planes,facecolors=[PINE,BLUE,OCHRE],alpha=.035,edgecolors=GRID,lw=.6))
    for q,col in [(np.array([2,1,0]),PINE),(np.array([0,1,3]),BLUE),(np.array([2,0,3]),OCHRE)]:
        ax.plot(*np.array([p,q]).T,ls='--',color=col,lw=1.4)
        ax.scatter(*q,s=45,color=col,depthshade=False)
    ax.scatter(*p,s=65,color=INK,depthshade=False);ax.text(2.1,1.1,3.25,'P',fontsize=12)
    ax.scatter(4,0,3,s=70,marker='x',color=RED,depthshade=False)
    ax.plot([2,4],[0,0],[3,3],color=RED,lw=1.5,ls=':')
    ax.set_xticks([0,2,4]);ax.set_yticks([0,1,3]);ax.set_zticks([0,1,3])
    tab=fig.add_axes([.64,.25,.32,.52]);tab.axis('off')
    rows=[('view','coherent','changed'),('xy','(2, 1)','(2, 1)'),('yz','(1, 3)','(1, 3)'),('xz','(2, 3)','(4, 3)')]
    for i,row in enumerate(rows):
        y=.96-.18*i
        for xx,text in zip([0,.25,.70],row):tab.text(xx,y,text,fontsize=10.5,color=RED if i==3 and xx==.70 else INK,ha='left')
        if i==0:tab.plot([0,1],[y-.06,y-.06],color=GRID,lw=1)
    tab.set_xlim(0,1.15);tab.set_ylim(0,1.05)
    fig.text(.66,.24,'One changed x-value\nbreaks the overlap.',fontsize=11,color=RED)
    fig.text(.05,.055,r'Coherent family: $(xy,yz,xz)=((2,1),(1,3),(2,3))$.',fontsize=11)
    check('f01 coordinate overlap',p[[0,1]].tolist()==[2,1] and p[[1,2]].tolist()==[1,3] and 2!=4,{'point':[2,1,3],'coherent_views':[[2,1],[1,3],[2,3]],'changed_xz':[4,3],'conflicting_coordinate':'x'})
    record('f01','Read the overlaps',r'Take three views of a point in $\mathbb R^3$: its $xy$, $yz$, and $xz$ coordinates. The picture follows $P=(2,1,3)$ into the three coordinate planes.',r'Each pairwise view omits one coordinate. The three displayed pairs agree wherever a coordinate is shared, so they describe the same point. Replacing $(2,3)$ in the $xz$ view by $(4,3)$ creates a conflict: the $xy$ view still requires $x=2$.',r'Keep only the $xy$ appearance $(2,1)$. The compatible points are the whole line $(2,1,z)$. Restoring the $yz$ appearance $(1,3)$ selects $z=3$.',['sec:views','sec:glue'],name)
    done(fig,name)

def f02():
    name='f02_integer_fibers';fig=base('When does the prescribed slice meet the lattice?','Exact families have integer coordinates and satisfy k = 2m.')
    for j,k in enumerate([2,3]):
        ax=fig.add_axes([.005+.50*j,.14,.48,.65],projection='3d')
        spatial(ax,((-.2,4.3),(-.2,2.3),(-1.4,1.4)),labels=('k','m','z'),elev=20,azim=-58)
        ax.set_title('k = '+str(k)+(': feasible' if k==2 else ': blocked'),pad=4,color=PINE if k==2 else RED)
        ax.add_collection3d(Poly3DCollection([[(k,-.1,-1.3),(k,2.2,-1.3),(k,2.2,1.3),(k,-.1,1.3)]],facecolors=PINE if k==2 else RED,alpha=.08,edgecolors=PINE if k==2 else RED,lw=.7))
        for m in range(3):
            zs=np.arange(-1,2)
            ax.plot([2*m]*2,[m]*2,[-1.3,1.3],color=GRID,lw=1)
            ax.scatter([2*m]*3,[m]*3,zs,color=PINE if k==2 and m==1 else MUTED,s=42,depthshade=False)
        if k==2:ax.scatter(2,1,0,s=130,facecolors='none',edgecolors=INK,lw=1.5,depthshade=False)
        ax.set_xticks([0,2,4]);ax.set_yticks([0,1,2]);ax.set_zticks([-1,0,1]);ax.set_zlabel('')
        ax.text2D(.94,.59,'z',transform=ax.transAxes,fontsize=11)
    fig.text(.08,.07,r'$\{(2,1,z):z\in\mathbb{Z}\}$',fontsize=13,color=PINE)
    fig.text(.63,.07,r'No integer solves $3=2m$.',fontsize=12,color=RED)
    check('f02 finite lattice slices',all((2==2*m)==(m==1) for m in range(-3,4)) and not any(3==2*m for m in range(-3,4)),{'displayed_m':[0,1,2],'displayed_z':[-1,0,1],'feasible_slice_k':2,'displayed_feasible_points':[[2,1,z] for z in [-1,0,1]],'obstructed_slice_k':3,'algebraic_condition':'k is twice an integer'})
    record('f02','Slice the extension fiber',r'Use integer variables with $k=2m$ and an independent coordinate $z$. Prescribe $k$, then look for lattice points in that slice. Only three values of $z$ are displayed.',r'The slice $k=2$ contains $(2,1,z)$ for every integer $z$. The slice $k=3$ misses the lattice because the required $m=3/2$ is not an integer. The free vertical coordinate changes the number of answers, while the parity condition still determines whether any answer exists.',r'Prescribe $z=0$ as well as $k=2$. The circled point $(2,1,0)$ is now the unique answer. Prescribing $z=0$ cannot rescue the blocked slice $k=3$.',['sec:obstruction','sec:prescription'],name)
    done(fig,name)

def f03():
    name='f03_boundary_comparisons';fig=base('Which comparison survives the boundary mark?','All labels are bits; addition and subtraction are modulo two.')
    headings=['Unmarked','Boundary identified','Both gauges frozen']
    for i,heading in enumerate(headings):
        ax=fig.add_axes([.045+.32*i,.19,.28,.60]);ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
        ax.text(.5,.98,heading,ha='center',fontsize=11.5,fontweight='medium')
        for xx,label in [(.10,'r = 1'),(.90,"r′ = 0")]:
            ax.text(xx,.58,label,ha='center',va='center',fontsize=11,bbox=dict(boxstyle='round,pad=.3',fc=PALE,ec=GRID))
        if i==0:
            for rad,y,label in [(-.35,.82,'(0, 1)'),(.35,.31,'(1, 0)')]:
                ax.add_patch(FancyArrowPatch((.20,.59),(.80,.59),connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',mutation_scale=13,lw=1.5,color=BLUE))
                ax.text(.5,y,label,ha='center',fontsize=11,color=BLUE)
            ax.text(.5,.07,'2 gauges',ha='center',fontsize=12,color=BLUE)
        elif i==1:
            ax.add_patch(FancyArrowPatch((.21,.60),(.79,.60),arrowstyle='-|>',mutation_scale=13,lw=1.8,color=PINE))
            ax.text(.5,.72,'(1, 0)',ha='center',fontsize=11,color=PINE)
            ax.text(.10,.38,'φ = 0',ha='center',fontsize=11);ax.text(.90,.38,'ψ = 1',ha='center',fontsize=11)
            ax.text(.5,.07,'1 compatible gauge',ha='center',fontsize=11.5,color=PINE)
        else:
            ax.plot([.25,.75],[.60,.60],color=RED,lw=1.5,ls=':');ax.text(.5,.60,'×',ha='center',va='center',fontsize=23,color=RED,bbox=dict(fc='white',ec='none',pad=1))
            ax.text(.5,.76,'only (0, 0) allowed',ha='center',fontsize=10.5,color=RED)
            ax.text(.5,.07,'0 compatible gauges',ha='center',fontsize=11.5,color=RED)
    fig.text(.05,.08,r'Label equation: $0=a_0+1-a_1$.     Boundary equation: $1+a_0=0$.',fontsize=11)
    gauges=[list(a) for a in itertools.product(range(2),repeat=2) if (a[0]+1-a[1])%2==0]
    marked=[a for a in gauges if (1+a[0])%2==0]
    check('f03 all four binary gauges',gauges==[[0,1],[1,0]] and marked==[[1,0]] and [0,0] not in gauges,{'all_candidate_gauges':4,'unmarked_gauges':gauges,'marked_gauges':marked,'frozen_gauge_valid':False})
    record('f03','Retain the comparison that matters',r'Duplicate a view and use the coefficient group $C_2$. A gauge $(a_0,a_1)$ changes the transition label by $r^{\prime}=a_0+r-a_1$. Compare $r=1$ with $r^{\prime}=0$. All arithmetic in this example is modulo two.',r'Two gauges relate the unmarked labels. The boundary marks $\phi=0$ and $\psi=1$ impose $\psi+a_0=\phi$, leaving one compatible comparison. Freezing both representative gauges instead allows only $(0,0)$, which cannot change the transition label. The three panels retain different data.',r'Change the target mark to $\psi=0$ while keeping $\phi=0$. The boundary equation then selects $(0,1)$: a comparison still exists, but the chosen mark determines which one.',['sec:boundary-lab','sec:relative'],name)
    done(fig,name)

def f04():
    name='f04_composition_cover';fig=base('Was the composition equation checked anywhere?','Bits label arrows i → j for i < j.')
    ax=fig.add_axes([.055,.24,.39,.53]);ax.axis('off');ax.set_xlim(-.2,1.2);ax.set_ylim(-.1,1.05)
    xy=np.array([[0,0],[1,0],[.5,.8]])
    # Arrangement is 0 left, 1 top, 2 right.
    pos={0:xy[0],1:xy[2],2:xy[1]}
    for i,j,v,offset in [(0,1,0,(-.07,.025)),(1,2,0,(.065,.025)),(0,2,1,(0,-.10))]:
        a,b=pos[i],pos[j];ax.annotate('',b,a,arrowprops=dict(arrowstyle='->',color=RED if v else BLUE,lw=1.6,shrinkA=14,shrinkB=14))
        mid=(a+b)/2+offset;ax.text(*mid,str(v),ha='center',va='center',fontsize=13,color=RED if v else BLUE,bbox=dict(fc='white',ec='none',pad=2))
    for i,p in pos.items():ax.text(*p,str(i),ha='center',va='center',fontsize=12,bbox=dict(boxstyle='circle,pad=.25',fc=PALE,ec=GRID))
    ax.set_title('Each pair can pass',fontsize=12,pad=12)
    fig.text(.085,.16,r'Together: $1\ne0+0$ (mod 2).',color=RED,fontsize=11)
    bx=fig.add_axes([.54,.22,.40,.58],projection='3d')
    v=np.array([[0,0,0],[1,0,0],[.5,.866,0],[.5,.2887,.95]])
    faces=[[v[i] for i in face] for face in itertools.combinations(range(4),3)]
    bx.add_collection3d(Poly3DCollection(faces,facecolors=PINE,edgecolors='none',alpha=.045))
    bits=[0,1,0,1]
    for i,j in itertools.combinations(range(4),2):
        bx.plot(*v[[i,j]].T,color=PINE,lw=1.4)
        mid=(v[i]+v[j])/2
        bx.text(*mid,str(bits[i]^bits[j]),fontsize=11,color=PINE,bbox=dict(fc='white',ec='none',pad=1))
    for i,p in enumerate(v):bx.text(*(p+np.array([0,0,.045 if i==3 else -.09])),str(i),fontsize=12,fontweight='bold')
    bx.view_init(elev=23,azim=-90);bx.set_box_aspect([1,1,1]);bx.set_axis_off()
    bx.set_title('All four faces checked',fontsize=12,pad=8)
    fig.text(.56,.16,'Every triangular equation closes.',color=PINE,fontsize=11)
    fig.text(.05,.055,'Left: pair patches miss one equation.   Right: triple patches cover every composition.',fontsize=10.5)
    triples=list(itertools.combinations(range(4),3));eq=[(bits[i]^bits[k])==((bits[i]^bits[j])^(bits[j]^bits[k])) for i,j,k in triples]
    check('f04 face equations',all(eq) and 1!=(0^0),{'failed_triangle_labels':[0,0,1],'tetrahedron_vertex_bits':bits,'face_vertex_sets':[list(t) for t in triples],'all_four_equations_hold':all(eq),'cover_scope':'ordered category on four objects; full three-object patches'})
    record('f04','Find the missing equation',r'On three ordered views, assign bit labels $c_{01}=0$, $c_{12}=0$, and $c_{02}=1$. Each two-view patch contains its own arrow, but no patch contains the full composition.',r'The left triangle exposes the unchecked equation: the direct label is one, while the two-step label is zero. On the right, use four ordered views and all four three-view patches. Labels $c_{ij}=a_i+a_j$ from $a=(0,1,0,1)$ satisfy every face equation.',r'Replace the left direct label by zero. Its composition equation then holds. This repairs that example; the pair-patch cover still provides no general guarantee that composition was checked locally.',['sec:descent','sec:stack'],name)
    done(fig,name)

def f05():
    name='f05_order_phase';fig=base('What survives when the order is reversed?','Apply the same two matrices to v = (1, 2).')
    X=np.array([[0,1],[1,0]]);Z=np.diag([1,-1]);v=np.array([1,2])
    routes=[([v,X@v,Z@X@v],'X then Z',PINE),([v,Z@v,X@Z@v],'Z then X',OCHRE)]
    for j,(route,title,col) in enumerate(routes):
        ax=fig.add_axes([.075+.48*j,.21,.39,.56]);tidy(ax)
        ax.axhline(0,color=GRID,lw=1);ax.axvline(0,color=GRID,lw=1)
        ax.set(xlim=(-2.7,2.7),ylim=(-2.7,2.7),xticks=[-2,0,2],yticks=[-2,0,2],xlabel='first coordinate',ylabel='second coordinate')
        ax.set_aspect('equal');ax.set_title(title,fontsize=12,pad=10)
        if j==1:ax.set_ylabel('')
        for i in [0,1]:ax.annotate('',route[i+1],route[i],arrowprops=dict(arrowstyle='->',color=BLUE if i==0 else col,lw=2,shrinkA=5,shrinkB=5))
        for i,p in enumerate(route):
            c=MUTED if i==0 else BLUE if i==1 else col
            ax.scatter(*p,color=c,s=42,zorder=4)
            offset={0:(-6,10),1:(5,-17),2:(-5,-18)}[i]
            if j==1 and i==2:offset=(-4,10)
            ax.annotate(f'({p[0]}, {p[1]})',p,xytext=offset,textcoords='offset points',ha='right' if i==0 else 'left',fontsize=10.5,color=c)
    fig.text(.075,.085,r'$ZXv=(2,-1)$',color=PINE,fontsize=12)
    fig.text(.555,.085,r'$XZv=(-2,1)=-ZXv$',color=OCHRE,fontsize=12)
    fig.text(.05,.027,r'$X(x,y)=(y,x)$;  $Z(x,y)=(x,-y)$.  The two-bit sum is the same; the sign differs.',fontsize=10.5)
    G=list(itertools.product(range(2),repeat=2));add=lambda a,b:tuple(x^y for x,y in zip(a,b));c=lambda a,b:a[1]*b[0]
    triplechecks=[(c(a,b)^c(add(a,b),d))==(c(b,d)^c(a,add(b,d))) for a,b,d in itertools.product(G,repeat=3)]
    flatten=[]
    for vals in itertools.product(range(2),repeat=4):
        f=dict(zip(G,vals))
        if all(c(a,b)==(f[a]^f[b]^f[add(a,b)]) for a,b in itertools.product(G,repeat=2)):flatten.append(vals)
    check('f05 exact bit and matrix calculations',all(triplechecks) and not flatten and np.array_equal(Z@X,-X@Z),{'coefficient_domain':'F2 for phase; integer matrices for action','phase_triples_checked':64,'scalar_functions_checked':16,'flattening_functions':0,'ZXv':(Z@X@v).tolist(),'XZv':(X@Z@v).tolist(),'phase_convention':'c(x,y)=x_2*y_1'})
    record('f05','Reverse the order',r'Label the coordinate swap $X$ by $(1,0)$ and the second-coordinate reflection $Z$ by $(0,1)$. Start at $v=(1,2)$ and follow both orders. Matrix products act from right to left.',r'Both routes use the same two-bit labels, whose sum is $(1,1)$. Their final vectors are negatives because $ZX=-XZ$. In this model the phase $c(x,y)=x_2y_1$ records that sign. The composition law remains associative; reversing these two factors is the operation that changes the result.',r'Attach a sign bit to the two-bit label. These two routes then end at different sign bits over the same label $(1,1)$, retaining the distinction that the four labels alone omit.',['sec:phase'],name)
    done(fig,name)

def f06():
    name='f06_hidden_detail';fig=base('What disappears between the sampled levels?','Identity scalar bonds: an adjacent defect is the next value minus the current value.')
    n=np.arange(5);f=(-1.)**n;g=np.ones(5);r=np.diff(f)
    ax=fig.add_axes([.10,.54,.83,.27]);tidy(ax)
    ax.plot(n,g,color=BLUE,lw=1.8,marker='s',ms=5,label='constant candidate')
    ax.plot(n,f,color=OCHRE,lw=1.8,marker='o',ms=5,label='alternating candidate')
    ax.scatter(n[::2],f[::2],s=100,facecolors='none',edgecolors=PINE,lw=1.8,zorder=5,label='kept levels')
    ax.set(xlim=(-.2,4.2),ylim=(-1.45,1.6),xticks=n,yticks=[-1,0,1],ylabel='value')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.40),ncol=3,frameon=False,columnspacing=1,handlelength=1.2)
    bx=fig.add_axes([.10,.19,.83,.24]);tidy(bx)
    bx.axhline(0,color=GRID,lw=1)
    bx.vlines(np.arange(4),0,r,color=OCHRE,lw=2);bx.scatter(np.arange(4),r,color=OCHRE,s=45)
    bx.set(xlim=(-.2,4.2),ylim=(-2.8,3.2),xticks=n,yticks=[-2,0,2],xlabel='level / adjacent edge index',ylabel='defect')
    for left in [0,2]:
        bx.plot([left,left,left+1,left+1],[2.35,2.55,2.55,2.35],color=PINE,lw=1.2)
        bx.text(left+.5,2.70,'sum 0',ha='center',fontsize=10,color=PINE)
    fig.text(.10,.055,r'$Cr=(0,0)$, but $Hr=r-JCr=(-2,2,-2,2)$.',fontsize=12)
    coarse=r.reshape(2,2).sum(axis=1);lift=np.array([0,coarse[0],0,coarse[1]]);detail=r-lift
    check('f06 exact sample and detail',np.array_equal(f[::2],g[::2]) and np.array_equal(coarse,[0,0]) and np.array_equal(detail,r),{'input_values':f.astype(int).tolist(),'adjacent_residual':r.astype(int).tolist(),'even_samples':[1,1,1],'coarse_residual':coarse.astype(int).tolist(),'retained_detail':detail.astype(int).tolist(),'lift_convention':'J(c0,c1)=(0,c0,0,c1)'})
    record('f06','Keep the discarded detail',r'Compare constant values $g_n=1$ with alternating values $f_n=(-1)^n$ on identity scalar towers. Keep only even levels. The plot displays levels zero through four and their four adjacent defects.',r'The sampled values agree, and each pair of alternating defects sums to zero. The coarse residual therefore cannot distinguish the candidates. The detail does: with $J(c_0,c_1)=(0,c_0,0,c_1)$, the zero coarse residual lifts to zero, leaving the entire alternating residual in $Hr=r-JCr$.',r'Restore the omitted odd values. The alternating candidate has defects $-2,2,-2,2$ while the constant candidate has zero defects. Exact coherent points are unaffected by this example of cancellation in raw candidates.',['sec:towers','sec:cascade'],name)
    done(fig,name)

def f07():
    name='f07_recovery_depth';fig=base('Does recovery move outward, or does the error shrink?','At depth N, the first N coordinates vanish; the rest retain their values.')
    for j,q in enumerate([1,.5]):
        ax=fig.add_axes([.005+.50*j,.22,.47,.58],projection='3d')
        spatial(ax,((0,6.2),(-.2,3.4),(0,1.15)),labels=('index i','depth N',''),elev=25,azim=-61)
        for N in range(4):
            xx=np.arange(7);zz=np.where(xx>=N,q**xx,0.)
            # Connecting lines guide the eye; markers are the actual integer-coordinate values.
            ax.plot(xx,[N]*7,zz,color=PINE if q<1 else OCHRE,lw=1.4,alpha=.85)
            ax.scatter(xx,[N]*7,zz,color=PINE if q<1 else OCHRE,s=16,depthshade=False)
            ax.plot([N,N],[N,N],[0,q**N],color=MUTED,lw=.6,ls=':')
        ax.set_xticks([0,2,4,6]);ax.set_yticks([0,1,2,3]);ax.set_zticks([0,.5,1])
        ax.text2D(.67,.97,'remainder',transform=ax.transAxes,fontsize=10)
        ax.set_title(r'$x_i=1$' if q==1 else r'$x_i=2^{-i}$',fontsize=13,pad=4)
    fig.text(.075,.09,r'$\|Q_Nx\|_\infty=1$',color=OCHRE,fontsize=13)
    fig.text(.57,.09,r'$\|Q_Nx\|_\infty=2^{-N}$',color=PINE,fontsize=13)
    fig.text(.05,.035,'The formulas describe infinite tails; the plot shows only indices 0 through 6.',fontsize=10.5)
    check('f07 displayed shift remainders',all(max([0 if i<N else 2**(-i) for i in range(7)])==2**(-N) for N in range(4)),{'displayed_indices':[0,1,2,3,4,5,6],'displayed_depths':[0,1,2,3],'constant_displayed_maxima':[1,1,1,1],'geometric_displayed_maxima':[1,.5,.25,.125],'infinite_tail_norm_basis':'exact monotonicity of the displayed geometric formula, not finite extrapolation'})
    record('f07','Follow the remainder',r'For the shift cascade, $Q_Nx$ sets the first $N$ coordinates to zero and leaves the tail in its original positions. Compare the constant sequence with $x_i=2^{-i}$.',r'The recovered region grows in both panels: every fixed coordinate eventually becomes zero in the remainder. The constant tail keeps height one, so its uniform error never decreases. The geometric tail starts at $2^{-N}$ and then decreases further, giving exactly the norm printed beneath the right panel.',r'At depth $N=3$, coordinates zero, one, and two are recovered in both examples. Their infinite remainder norms are nevertheless $1$ and $1/8$, respectively.',['sec:cascade'],name)
    done(fig,name)

def f08():
    name='f08_restricted_descent';fig=base('Does the second repair preserve the first equation?','Local exactness: z = 0.   Matching: y = z.   Joint exactness: the x-axis.')
    ax=fig.add_axes([.09,.12,.83,.70],projection='3d')
    spatial(ax,((0,3.2),(-.35,3),(0,3.5)),elev=22,azim=-57)
    planes=[[(0,0,0),(3.1,0,0),(3.1,2.8,0),(0,2.8,0)],[(0,0,0),(3.1,0,0),(3.1,2.8,2.8),(0,2.8,2.8)]]
    ax.add_collection3d(Poly3DCollection(planes,facecolors=[BLUE,OCHRE],alpha=.055,edgecolors=[BLUE,OCHRE],lw=.65))
    x=np.array([2,2,3]);local=np.array([2,2,0]);joint=np.array([2,0,0]);wrong=np.array([2,1,1])
    ax.plot([0,3.1],[0,0],[0,0],color=PINE,lw=3)
    for a,b,c in [(x,local,BLUE),(local,joint,PINE),(local,wrong,RED)]:
        ax.plot(*np.array([a,b]).T,color=c,lw=2.3,ls='--' if c==RED else '-')
    for p,c in [(x,INK),(local,BLUE),(joint,PINE),(wrong,RED)]:ax.scatter(*p,color=c,s=47,depthshade=False)
    ax.text(2.05,2.1,3.15,'raw (2, 2, 3)',fontsize=11,color=INK)
    ax.text(2.02,2.08,.10,'local (2, 2, 0)',fontsize=11,color=BLUE)
    ax.text(2.04,-.15,.12,'joint (2, 0, 0)',fontsize=11,color=PINE)
    ax.text(.15,.66,1.15,'unrestricted\n(2, 1, 1)',fontsize=11,color=RED)
    ax.plot([.9,2],[.9,1],[1.08,1],color=RED,lw=.7)
    ax.set_xticks([0,1,2,3]);ax.set_yticks([0,1,2]);ax.set_zticks([0,1,2,3])
    fig.text(.05,.05,r'Inside $z=0$: squared moves $9+4=13$.    Unrestricted: matching holds, but $z=1$.',fontsize=10.5)
    n=np.array([0,1,-1]);proj=local-n*(np.dot(n,local)/np.dot(n,n))
    check('f08 Euclidean projections',np.array_equal(proj,wrong) and np.dot(x-local,local-joint)==0 and np.dot(x-joint,x-joint)==13 and wrong[2]==1 and wrong[1]-wrong[2]==0,{'raw':x.tolist(),'local_projection':local.tolist(),'restricted_joint_projection':joint.tolist(),'unrestricted_matching_projection':proj.tolist(),'squared_local_move':9,'squared_restricted_matching_move':4,'squared_total_move':13,'wrong_local_defect':1,'wrong_matching_defect':0,'metric':'standard Euclidean inner product on R3'})
    record('f08','Repair within the exact plane',r'In Euclidean $\mathbb R^3$, take $D(x,y,z)=z$ and $C(x,y,z)=y-z$. Starting at $(2,2,3)$, first project to the locally exact plane $z=0$. The two planes encode different constraints on the same raw point.',r'The local correction reaches $(2,2,0)$. Solving the matching problem inside that plane reaches $(2,0,0)$, with perpendicular squared movements $9$ and $4$. Projecting instead onto the entire plane $y=z$ reaches $(2,1,1)$: matching is repaired, but the local equation has been broken.',r'At the unrestricted answer, evaluate both defects: $C(2,1,1)=0$ and $D(2,1,1)=1$. The joint answer has both defects zero and total squared correction $13$.',['sec:quantitative'],name)
    done(fig,name)

def main():
    for fn in [f01,f02,f03,f04,f05,f06,f07,f08]:fn()
    (ROOT/'records').mkdir(exist_ok=True);(ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'records/foundations_scenes.json').write_text(json.dumps(SCENES,indent=2)+'\n')
    manifest={'schema':'visual-companion-finite-checks-v1','scope':'Eight explicitly specified finite illustrations. The recorded checks do not prove any general monograph theorem or infer infinite behavior from truncation.','command':'python tools/visual_companion/foundations.py','arithmetic':'integer and F2 exact calculations; IEEE float for Euclidean coordinates and plot geometry','python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__,'seed':None,'deterministic':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':CHECKS,'figures':FIGURES,'all_passed':all(c['passed'] for c in CHECKS)}
    (ROOT/'build/foundations_checks.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{len(SCENES)} scenes; {len(CHECKS)} finite checks passed; {len(FIGURES)} PDF/PNG pairs generated.')

if __name__=='__main__':main()
