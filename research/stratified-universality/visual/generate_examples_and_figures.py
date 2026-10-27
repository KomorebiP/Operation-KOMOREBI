#!/usr/bin/env python3
"""Reproduce the guide's exact finite examples and vector figures.

Exact claims use fractions.Fraction. NumPy is used only for metric illustrations.
Run with a Python environment containing matplotlib and numpy.
"""
from fractions import Fraction as F
from pathlib import Path
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'; FIG.mkdir(exist_ok=True)
OUT = ROOT / 'validation'; OUT.mkdir(exist_ok=True)
checks=[]
def check(name, condition, source):
    assert condition, name
    checks.append({'check':name,'source_label':source,'passed':True})
def mat(a): return [[F(x) for x in row] for row in a]
def eye(n): return mat([[int(i==j) for j in range(n)] for i in range(n)])
def zero(n,m): return mat([[0]*m for _ in range(n)])
def add(a,b): return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def sub(a,b): return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def mul(a,b): return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def rank(a):
    a=[r[:] for r in a]; r=0
    for c in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]; t=a[r][c]; a[r]=[x/t for x in a[r]]
        for i in range(len(a)):
            if i!=r:
                t=a[i][c]; a[i]=[x-t*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a): break
    return r
def determinant(a):
    a=[r[:] for r in a]; d=F(1)
    for c in range(len(a)):
        p=next((i for i in range(c,len(a)) if a[i][c]),None)
        if p is None: return F(0)
        if p!=c: a[c],a[p]=a[p],a[c]; d=-d
        t=a[c][c]; d*=t
        for i in range(c+1,len(a)):
            k=a[i][c]/t
            a[i]=[x-k*y for x,y in zip(a[i],a[c])]
    return d
def mask(a,E): return [[x if (i,j) in E else F(0) for j,x in enumerate(row)] for i,row in enumerate(a)]
def encode(a): return [[str(x) for x in r] for r in a]

P=mat([[1,1],[0,0]]); Q=mat([[0,-1],[0,1]]); I=eye(2)
for name,c in [('p1 idempotent',mul(P,P)==P),('p2 idempotent',mul(Q,Q)==Q),('annihilation',mul(P,Q)==zero(2,2) and mul(Q,P)==zero(2,2)),('reconstruction',add(P,Q)==I)]:
    check(name,c,'ex:oblique-packets')
V=mat([[1,-1],[0,1]]); W=mat([[1,1],[0,1]])
check('oblique analysis synthesis',mul(V,W)==I and mul(W,V)==I,'thm:exact-packet-coordinate-expanded')
f=mat([[2,3],[5,7]]); g=mat([[1,2],[3,4]])
hf=mul(mul(W,f),V); hg=mul(mul(W,g),V)
check('oblique lane matrix',hf==mat([[7,3],[5,2]]),'thm:transfer-reconstruction-expanded')
check('matrix contraction',mul(hg,hf)==mul(mul(W,mul(g,f)),V),'thm:transfer-reconstruction-expanded')
E={(0,0),(1,1)}; Fset={(0,0),(0,1)}
for a in [f,g,hf,hg]:
    check('selector idempotence '+str(len(checks)),mask(mask(a,E),E)==mask(a,E),'prop:block-selector-algebra')
    check('selector intersection '+str(len(checks)),mask(mask(a,E),Fset)==mask(a,E&Fset),'prop:block-selector-algebra')
fe=mask(f,E); gf=mask(g,E); rf=sub(f,fe); rg=sub(g,gf)
res=sub(mul(g,f),mul(gf,fe))
check('three residual terms',res==add(add(mul(rg,fe),mul(gf,rf)),mul(rg,rf)),'prop:exact-residual-product')
check('numeric composite residual',res==mat([[10,17],[26,9]]),'prop:exact-residual-product')

A=mat([[1,2,3],[4,5,6],[7,8,9]])
coarse=[[ [A[i][j] for j in cols] for i in rows] for rows in [[0,1],[2]] for cols in [[0,1],[2]]]
recovered=[r[:] for r in A]
check('coarse corners retain 9 entries',sum(len(r) for b in coarse for r in b)==9,'prop:block15-certified-coarsening')
check('fold kernel witness',mul(mat([[1,1]]),mat([[1],[-1]]))==mat([[0]]),'thm:block15-abelian-fold-exact-sequence')

S=mat([[0,1],[1,0]]); D=mat([[1,0],[0,-1]])
for a,b in [(2,3),(-1,4),(0,1),(5,0)]:
    H=mat([[a,b],[b,a]])
    check('C2 equivariance '+str((a,b)),mul(S,H)==mul(H,S),'ex:block16-c2-swap')
check('individual lane does not descend',mul(mul(S,mat([[1,0],[0,0]])),S)!=mat([[1,0],[0,0]]),'thm:block16-orbit-descent')
check('orbital path square',mul(S,S)==I,'thm:block16-permutation-orbital-calculus')
for a,b in [(2,3),(-1,4),(0,1)]:
    H=mat([[a,0],[0,b]])
    check('twisted support can act as zero '+str((a,b)),mul(D,H)==mul(H,D) and mask(H,{(0,1)})==zero(2,2),'thm:block16-orbit-descent')
check('flat core defect rank',rank(sub(S,I))==1,'thm:maximal-flat-core')

# Descending partition refinement, one continuation generator.
states=list('ABCDEF'); obs=dict(zip(states,[0,0,0,1,1,1])); nxt=dict(zip(states,list('DABFDD')))
part=[set('ABC'),set('DEF')]; trace=[]
while True:
    trace.append([''.join(sorted(s)) for s in part]); ids={s:i for i,p in enumerate(part) for s in p}
    buckets={}
    for s in states: buckets.setdefault((obs[s],ids[nxt[s]]),set()).add(s)
    new=list(buckets.values())
    if {frozenset(s) for s in new}=={frozenset(s) for s in part}: break
    part=new
check('finite partition trace',trace==[['ABC','DEF'],['A','BC','DEF'],['A','B','C','DEF']],'cor:block17-finite-certification')
check('partition stable',all(ids[nxt[s]]==ids[nxt[t]] and obs[s]==obs[t] for p in part for s in p for t in p),'thm:block17-behavioral-core')

T=mat([[0,1,0],[0,0,0],[0,0,1]]); o=mat([[1,0,0]])
O=o+mul(o,T)+mul(mul(o,T),T)
check('linear future kernel dimension',3-rank(O)==1,'cor:block17-finite-certification')
check('stable invisible e3',mul(o,mat([[0],[0],[1]]))==mat([[0]]) and mul(T,mat([[0],[0],[1]]))==mat([[0],[0],[1]]),'thm:block17-behavioral-core')
s=mat([[1,0,0],[0,1,0]]); t=mat([[0,1,0],[0,0,1]])
alpha=mat([[1,0,0],[0,1,0],[0,1,0],[0,0,1]]); beta=mat([[0,1,-1,0]])
check('semantic diamond exactness',rank(alpha)==3 and rank(beta)==1 and mul(beta,alpha)==zero(1,3),'thm:block17-semantic-diamond')
check('semantic diamond compatibility witness',mul(beta,mat([[2],[3],[3],[5]]))==mat([[0]]) and mul(beta,mat([[2],[3],[4],[5]]))==mat([[-1]]),'thm:block17-semantic-diamond')
evalmap=mat([[1,0,1],[0,1,1]])
check('observer relation',mul(evalmap,mat([[1],[1],[-1]]))==mat([[0],[0]]) and rank(evalmap)==2,'thm:block18-observer-base-change')

# Exact polyphase / Hankel family for a declared finite parameter grid.
poly=[]
for N in range(1,7):
    for z in [F(1,2),F(1),F(2),F(-1)]:
        shift=zero(N,N)
        for j in range(N-1): shift[j+1][j]=F(1)
        shift[0][N-1]=z
        M=add(eye(N),shift); powers=[eye(N)]
        for k in range(1,2*N): powers.append(mul(powers[-1],M))
        seq=[p[0][0] for p in powers]
        H=[[seq[i+j] for j in range(N)] for i in range(N)]
        det=determinant(H)
        check('Hankel determinant N='+str(N)+' z='+str(z),abs(det)==abs(z**(N-1)),'thm:block18-polyphase-hankel-separation')
        poly.append({'N':N,'z':str(z),'determinant':str(det)})
check('N2 z1 prefix', [sum(math.comb(n,2*r) for r in range(n//2+1)) for n in range(6)]==[1,1,2,4,8,16],'thm:block18-polyphase-hankel-separation')
check('Haar signed versus max',[F(1,2)+F(1,2),F(1,2)-F(1,2)]==[F(1),F(0)] and [max(F(1,2),F(1,2)),max(F(1,2),-F(1,2))]==[F(1,2),F(1,2)],'ex:block18-haar-cancellation')

# Polynomial identity for the sharp quadratic-class separation on exact test grid.
for a in range(1,6):
    for b in range(1,6):
        for c in [F(-1,2),F(0),F(1,2)]:
            d=a*b-c*c
            lhs=a*b*((a+b)**2-4*c*c)-4*d*d
            rhs=a*b*(a-b)**2+4*c*c*d
            check('quadratic identity '+str((a,b,c)),lhs==rhs and rhs>=0,'thm:block19-convex-quadratic-separation')

data={'status':'PASS','method':'exact rational arithmetic for finite examples; floating point only for drawn metric curve','checks':len(checks),'records':checks,'partition_trace':trace,'polyphase_trials':poly,'examples':{'oblique_lane_matrix':encode(hf),'composite_residual':encode(res)}}
(OUT/'visual_example_checks.json').write_text(json.dumps(data,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
blue='#184e77'; teal='#168a89'; orange='#cd6b36'; ink='#183345'; pale='#eef4f7'
def save(fig,name):
    fig.savefig(FIG/(name+'.pdf')); fig.savefig(FIG/(name+'.png'),dpi=170); plt.close(fig)
def blank(w=8,h=3.5):
    fig,ax=plt.subplots(figsize=(w,h)); ax.set_xlim(0,10); ax.set_ylim(-.25,5.1); ax.axis('off'); return fig,ax
def box(ax,x,y,w,h,txt,color=blue,fontsize=12):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.13',facecolor=pale,edgecolor=color,lw=1.5)); ax.text(x+w/2,y+h/2,txt,ha='center',va='center',color=ink,fontsize=fontsize)
def arrow(ax,x,y,u,v,txt=''):
    ax.add_patch(FancyArrowPatch((x,y),(u,v),arrowstyle='-|>',mutation_scale=15,color=blue,lw=1.5));
    if txt: ax.text((x+u)/2,(y+v)/2+.25,txt,ha='center',va='bottom',fontsize=10,color=ink)

fig,ax=blank(h=4)
for x,y,txt in [(0.4,3.0,'Ambient category\nC'),(3.55,3.0,'Verified constructors\nΠ'),(6.7,3.0,'Admissible models\nM'),(0.4,.6,'Normalized models\nN'),(3.55,.6,'Native semantics\nSem'),(6.7,.6,'Invariant target\nI : Core(N) → D')]: box(ax,x,y,2.6,1.35,txt)
save(fig,'passport')

fig,ax=blank(h=3)
box(ax,.35,1.5,2.5,1.45,'Proof support\n{sum, compose,\nsplit}',fontsize=11)
box(ax,3.7,1.5,2.55,1.45,'Verified bridge\nprofile Π\nDeclared constructors',fontsize=11)
box(ax,7.15,1.5,2.5,1.45,'Target hypotheses\nchecked locally',fontsize=11)
arrow(ax,2.95,2.2,3.55,2.2);arrow(ax,6.4,2.2,7,2.2)
ax.text(5,.45,'Transport gate: Supp(proof) ⊆ Π, plus target hypotheses',ha='center',color=teal,fontsize=13)
save(fig,'profile_gate')

fig,ax=plt.subplots(figsize=(7,4));ax.set_aspect('equal');ax.set_xlim(-1.4,3.5);ax.set_ylim(-.4,2.0)
for p,c,l in [((2,0),blue,'p₁x = (2,0)'),((-1,1),orange,'p₂x = (−1,1)'),((1,1),teal,'x = (1,1)')]:
    ax.arrow(0,0,*p,width=.012,head_width=.1,length_includes_head=True,color=c);ax.text(p[0]+.07,p[1]+.09,l,color=c)
ax.axhline(0,color='#ccd4da');ax.axvline(0,color='#ccd4da');ax.set_xlabel('First coordinate');ax.set_ylabel('Second coordinate');save(fig,'oblique')

fig,axs=plt.subplots(1,3,figsize=(8,3.2))
for ax,a,title in zip(axs,[f,fe,rf],['f','Retained diagonal C_E(f)','Named residual R_E(f)']):
    ax.imshow(np.array(a,dtype=float),cmap='Blues',vmin=0,vmax=7)
    for i in range(2):
        for j in range(2):ax.text(j,i,str(a[i][j]),ha='center',va='center',color='white' if a[i][j]>4 else ink,fontsize=20)
    ax.set_title(title,fontsize=11);ax.set_xticks([]);ax.set_yticks([])
fig.tight_layout();save(fig,'selector')

fig,ax=plt.subplots(figsize=(6.4,4));ax.imshow(np.array(A,dtype=float),cmap='Blues',vmin=0,vmax=9)
for i in range(3):
    for j in range(3):ax.text(j,i,str(A[i][j]),ha='center',va='center',fontsize=20,color='white' if A[i][j]>=6 else ink)
ax.axhline(1.5,color=orange,lw=4);ax.axvline(1.5,color=orange,lw=4);ax.set_xticks([.5,2],['Coarse source {1,2}','Source {3}']);ax.set_yticks([.5,2],['Target {1,2}','Target {3}']);save(fig,'coarse_corners')

fig,ax=blank(h=3.3)
box(ax,.6,1.5,2.8,1.4,'Local labels\n1     2');box(ax,6.5,1.5,2.8,1.4,'After a chart loop\n2     1');arrow(ax,3.6,2.2,6.3,2.2,'swap holonomy')
ax.text(5,.5,'Individual labels move; the orbit sum p₁ + p₂ is fixed.',ha='center',color=teal,fontsize=13);save(fig,'holonomy')

fig,axs=plt.subplots(1,2,figsize=(7,3.2))
for ax,m,title in zip(axs,[[[0,1],[1,0]],[[0,0],[0,0]]],['C₂ swap: diagonal / off-diagonal pair orbits','Sign twist: off-diagonal selector has zero action']):
    ax.imshow(m,cmap='Blues',vmin=0,vmax=1)
    for i in range(2):
        for j in range(2):
            label=('b' if ax is axs[1] and i==j==1 else 'a') if i==j else ('b' if ax is axs[0] else '0')
            ax.text(j,i,label,ha='center',va='center',fontsize=24,color=ink if m[i][j]==0 else 'white')
    ax.set_title(title,fontsize=10);ax.set_xticks([]);ax.set_yticks([])
fig.tight_layout();save(fig,'pair_orbits')

fig,ax=blank(h=3.7)
for y,row in zip([3.6,2.15,.7],trace):
    x=1.1
    for group in row:
        w=1.1+.55*len(group);box(ax,x,y,w,.7,' '.join(group));x+=w+.25
ax.text(.1,3.95,'r = 0',ha='left',fontsize=10);ax.text(.1,2.5,'r = 1',ha='left',fontsize=10);ax.text(.1,1.05,'r = 2',ha='left',fontsize=10)
save(fig,'partition')

fig,ax=blank(h=4.4)
box(ax,3.3,3.55,3.4,.85,'Joint view J = (x,y,z)')
box(ax,.45,1.8,3.05,.85,'S = (x,y)');box(ax,6.5,1.8,3.05,.85,'T = (y,z)');box(ax,3.45,.1,3.1,.85,'Shared view C = y')
arrow(ax,3.5,3.55,2.3,2.8);arrow(ax,6.5,3.55,7.7,2.8);arrow(ax,2.4,1.7,3.85,1.05);arrow(ax,7.6,1.7,6.15,1.05)
save(fig,'diamond')

fig,ax=blank(h=3.2)
box(ax,.3,1.75,2.4,1.05,'Raw expressions\nR');box(ax,3.8,2.9,2.5,1.05,'Source carrier S');box(ax,3.8,.4,2.5,1.05,'Target carrier T');box(ax,7.2,1.7,2.4,1.2,'Joint image\nJ = im(s,t)')
arrow(ax,2.85,2.4,3.65,3.3,'s');arrow(ax,2.85,2.15,3.65,.95,'t');arrow(ax,7.05,2.55,6.45,3.3);arrow(ax,7.05,2.0,6.45,.95);arrow(ax,2.85,2.3,7.05,2.3);ax.text(5,2.04,'(s,t)',ha='center',va='top',fontsize=10,color=ink)
save(fig,'carrier')

fig,ax=plt.subplots(figsize=(7,3.5));points=np.array([[1,0],[0,1],[1,1]])
for i,p in enumerate(points):ax.arrow(0,0,*p,width=.01,head_width=.07,length_includes_head=True,color=[blue,orange,teal][i]);ax.text(p[0]+.03,p[1]+.03,'e'+str(i+1))
ax.set_xlim(-.1,1.5);ax.set_ylim(-.1,1.4);ax.set_aspect('equal');ax.set_xlabel('First future coordinate');ax.set_ylabel('Second future coordinate');ax.text(.4,.3,'e₃ = e₁ + e₂',color=ink,fontsize=14);save(fig,'relations')

fig,ax=plt.subplots(figsize=(7,3.5));square=np.array([[-1,-1],[1,-1],[1,1],[-1,1],[-1,-1]])
theta=np.linspace(0,2*np.pi,300);ax.plot(square[:,0],square[:,1],color=teal,lw=2,label='Unit ball of ||·||∞');ax.plot(np.cos(theta),np.sin(theta),color=blue,lw=2,label='Euclidean unit circle')
ax.arrow(1,0,0,1,head_width=.07,color=orange,length_includes_head=True);ax.scatter([1],[1],color=orange);ax.text(1.08,.65,'A₁(1,0) = (1,1)\n∞ norm: 1\nEuclidean norm: √2',fontsize=11)
ax.set_xlim(-1.3,2.5);ax.set_ylim(-1.3,1.3);ax.set_aspect('equal');ax.legend(loc='lower right',fontsize=10);save(fig,'geometry')

fig,ax=plt.subplots(figsize=(7,3.7));ss=np.geomspace(1e-4,1,150);cond=[]
for v in ss:
    sing=np.linalg.svd(np.array([[1,v],[0,1.0]]),compute_uv=False);cond.append(sing[0]/sing[-1])
ax.semilogx(ss,cond,color=blue,lw=2);ax.axhline(1,color=teal,ls='--',label='Infimum 1, unattained');ax.set_xlabel('Metric parameter s');ax.set_ylabel('D_Qs(H)');ax.legend();save(fig,'escape')

fig,ax=blank(h=4.1)
box(ax,.5,2.7,3.4,1.05,'Weak task\nLarger invisible kernel');box(ax,6.1,2.7,3.4,1.05,'Strong task\nSmaller invisible kernel');arrow(ax,4.1,3.2,5.9,3.2,'add observations')
box(ax,.5,.45,3.4,1.05,'Restricted class Γ\nLarger optimized defect');box(ax,6.1,.45,3.4,1.05,'Enlarged class Γ′\nSmaller optimized defect');arrow(ax,4.1,1,5.9,1,'add realizations')
save(fig,'two_orders')
print(json.dumps({'status':'PASS','exact_checks':len(checks),'vector_figures':len(list(FIG.glob('*.pdf')))}))
