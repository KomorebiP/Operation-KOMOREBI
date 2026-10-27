"""Exact and explicitly schematic visual figures for the Hodge companion.
No numerical optimizer or generated imagery is used. Exact certificates are
checked before conversion to plotting coordinates. See figure_contract.json.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import gcd
import json, hashlib, platform, itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Ellipse
from matplotlib.colors import ListedColormap
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'shared/figures'; OUT.mkdir(parents=True,exist_ok=True)
REC=ROOT/'evidence/recovered'
T=REC/'Komorebi_Hodge_Carrier_Transfer_v0.2.0/Komorebi_Hodge_Carrier_Transfer_v0.2.0'
D=REC/'Komorebi_Hodge_Dual_and_Cycles_v0.2.0/Komorebi_Hodge_Dual_and_Cycles_v0.2.0'
AUG=REC/'Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source/Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source'
TEAL='#21676B'; COPPER='#A45C36'; INK='#243138'; GRAY='#627078'; SOFT='#E9F0EF'; GOLD='#CB9B55'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':17,'text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':GRAY,'xtick.color':GRAY,'ytick.color':GRAY,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
records=[];data={};used=[ROOT/'evidence/computation/verifieddata.json',ROOT/'evidence/computation/runs/weil/result.json',T/'results/transfer210.json',T/'results/verification.json',D/'results/capacity_certificates.json',D/'results/cycle_examples.json',AUG/'data/Fermat_Hodge_K23_CM_Type_Audit.json']
transfer=json.loads(used[2].read_text());verify=json.loads(used[3].read_text());caps=json.loads(used[4].read_text());cycles=json.loads(used[5].read_text());cm=json.loads(used[6].read_text())
source=transfer['source'];target=transfer['target'];carrier=caps[-1];A=sp.Matrix(carrier['matrix']);W=[10,6,3,3,3,8];B=210*A.inv();assert A*sp.Matrix(W)==sp.ones(6,1)*30
assert A.det()==-2100 and sum(A.inv()*sp.ones(6,1))==sp.Rational(11,10)
assert B*sp.ones(6,1)==7*sp.Matrix(W)
def units(m):return [u for u in range(1,m) if gcd(u,m)==1]
def residues(a,m,u=1):return [(u*x)%m for x in a]
def orbit(a,m):return sorted({tuple(residues(a,m,u)) for u in units(m)})
def check_balance(a,m):assert all(sum(residues(a,m,u))==len(a)*m//2 for u in units(m))
check_balance(carrier['character'],70);check_balance(source,210);check_balance(target,210)
def conductor(a,m):
 g=m
 for x in a:g=gcd(g,x)
 return m//g
left=Counter(target);right=Counter(source);L=[];R=[]
for term in transfer['certificate']:
 (right if term['coefficient']>0 else left).update(term['packet'])
 (R if term['coefficient']>0 else L).extend(term['packet'])
assert left==right and sum(left.values())==30 and len(L)==len(R)==24
assert Counter(L+[210-x for x in L])==Counter([x for a in L for x in [a,210-a]])
data.update(carrier_matrix=carrier['matrix'],carrier_weights=W,carrier_degree=30,carrier_determinant=-2100,carrier_B=[[int(x) for x in B.row(i)] for i in range(6)],source=source,target=target,transfer_left=dict(left),transfer_right=dict(right),left_auxiliary=L,right_auxiliary=R,source_conductor=conductor(source,210),target_conductor=conductor(target,210),source_dimension=len(orbit(source,210)),target_dimension=len(orbit(target,210)))
def canvas():
 fig,ax=plt.subplots(figsize=(11.5,7.0));fig.subplots_adjust(left=.13,right=.97,bottom=.17,top=.87);return fig,ax
def plain(ax):ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis('off')
def txt(ax,x,y,s,size=19,color=INK,ha='center',**kw):return ax.text(x,y,s,fontsize=size,color=color,ha=ha,va='center',**kw)
def box(ax,x,y,w,h,s,color=TEAL,size=19):
 ax.add_patch(Rectangle((x,y),w,h,edgecolor=color,facecolor=SOFT if color==TEAL else '#F5EAE3',lw=1.7,zorder=1));txt(ax,x+w/2,y+h/2,s,size,color)
def arrow(ax,a,b,label=None,color=GRAY,style='-|>',rad=0):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=19,lw=1.7,color=color,connectionstyle=f'arc3,rad={rad}'))
 if label:txt(ax,(a[0]+b[0])/2,(a[1]+b[1])/2+.28,label,15,color)
def save(fig,n,name,kind,desc,exact=None):
 stem=f'{n:02d}_{name}';fig.savefig(OUT/(stem+'.pdf'),bbox_inches='tight',pad_inches=.17);fig.savefig(OUT/(stem+'.png'),dpi=180,bbox_inches='tight',pad_inches=.17);plt.close(fig)
 rec={'id':n,'name':stem,'kind':kind,'meaning':desc,'exact_input':exact,'pdf_sha256':hashlib.sha256((OUT/(stem+'.pdf')).read_bytes()).hexdigest()};records.append(rec)
def heat(ax,matrix,cols=None,rows=None,cmap='Greens',fs=18):
 arr=np.array(matrix,dtype=float);ax.imshow(arr,cmap=cmap,aspect='auto',vmin=(-max(abs(arr).max(),1) if cmap=='RdBu' else 0),vmax=max(abs(arr).max(),1));ax.set_xticks(range(arr.shape[1]),cols or [str(i) for i in range(arr.shape[1])]);ax.set_yticks(range(arr.shape[0]),rows or [str(i) for i in range(arr.shape[0])]);ax.tick_params(length=0)
 for i in range(arr.shape[0]):
  for j in range(arr.shape[1]):txt(ax,j,i,str(matrix[i][j]),fs,INK if isinstance(cmap,ListedColormap) else ('white' if (abs(arr[i,j]) if cmap=='RdBu' else arr[i,j])>abs(arr).max()*.6 else INK))
 for spine in ax.spines.values():spine.set_visible(False)
# 1: target gap
fig,ax=canvas();plain(ax)
ax.add_patch(Ellipse((5,3.2),9.3,4.8,facecolor=SOFT,edgecolor=TEAL,lw=2));ax.add_patch(Ellipse((4.4,3.2),6.4,3.1,facecolor='white',edgecolor=TEAL,lw=2))
txt(ax,5,5.95,r'$\mathrm{Hdg}^{p}(X)=H^{2p}(X,\mathbf{Q})\cap H^{p,p}(X)$',23)
txt(ax,4.35,3.25,'Rational span of\nalgebraic cycle classes',23,TEAL);txt(ax,8.3,3.1,'?',45,COPPER);txt(ax,5,.6,'The conjecture asks whether the two spaces coincide.',20)
save(fig,1,'hodge_gap','schematic','Nested spaces illustrate known inclusion, not a measured codimension.')
#2 combination
fig,ax=canvas();plain(ax)
for x,y,w,h,s,c in [(0.5,2.4,2.3,2.4,'Algebraic\nsurfaces\n$Z_1,Z_2,Z_3$',TEAL),(3.9,2.4,2.3,2.4,'Cycle classes\n$[Z_i]$\nin $H^4$',TEAL),(7.4,2.4,2.1,2.4,'Rational\ncombination\nα',COPPER)]:box(ax,x,y,w,h,s,c)
arrow(ax,(2.8,3.6),(3.9,3.6),'cycle map');arrow(ax,(6.2,3.6),(7.4,3.6),'sum')
txt(ax,5,1.3,r'$\alpha=\frac{1}{2}[Z_1]-\frac{2}{3}[Z_2]+\frac{5}{6}[Z_3]$',25)
save(fig,2,'rational_cycle_combination','schematic','Illustrative coefficients show rational span, not effectivity.','coefficients 1/2,-2/3,5/6 are a definition of the example')
#3 fourfold positions
fig,ax=canvas();plain(ax)
for k in range(9):
 for p in range(5):
  q=k-p
  if 0<=q<=4:
   x=5+(p-q)*.72;y=5.6-k*.57
   ax.add_patch(Rectangle((x-.43,y-.22),.86,.44,facecolor=TEAL if (p,q)==(2,2) else SOFT,edgecolor=TEAL,lw=1))
   txt(ax,x,y,f'{p},{q}',13,'white' if (p,q)==(2,2) else INK)
txt(ax,1.1,3.1,r'$H^{4}$',25,TEAL);txt(ax,9.3,3.1,'Middle type\n$(2,2)$',20,TEAL);txt(ax,5,.2,'Coordinates are Hodge bidegrees, not Hodge numbers.',17,GRAY)
save(fig,3,'fourfold_middle','exact indexing diagram','All 25 bidegrees for complex dimension four are shown without claiming numerical Hodge dimensions.')
#4 diagnostic
fig,ax=canvas();plain(ax)
box(ax,.7,3.4,3.7,1.5,r'$P_{\mathrm{Hdg}}$',TEAL,27);box(ax,5.6,3.4,3.7,1.5,r'$P_{\mathrm{Alg}}$',COPPER,27)
txt(ax,5,4.15,'−',35);txt(ax,5,2.35,r'$O=P_{\mathrm{Hdg}}-P_{\mathrm{Alg}}$',27);txt(ax,5,1.1,'Equality is the target.\nDefining a projector does not construct its cycles.',23)
save(fig,4,'projector_diagnostic','schematic','Obstruction notation reformulates the target and is not itself an algorithm or an algebraic correspondence.')
#5 frame counterexample
fig,ax=canvas();ax.set_xlim(-.25,1.6);ax.set_ylim(-.25,1.4);ax.set_aspect('equal');ax.axhline(0,color=TEAL,lw=2);ax.axvline(0,color=GRAY,lw=1);ax.plot([-0.2,1.35],[-0.2,1.35],color=COPPER,lw=2)
arrow(ax,(0,0),(1,1),color=COPPER);arrow(ax,(0,0),(1,0),color=TEAL)
txt(ax,1.2,.08,'V = span(e₁)',17,TEAL);txt(ax,.8,1.18,'span(c)',17,COPPER);txt(ax,1.45,1.1,'c=(1,1)',17,COPPER)
txt(ax,.65,-.18,r'$\langle e_1,CC^*e_1\rangle=1>0$',21);ax.set_xticks([]);ax.set_yticks([])
save(fig,5,'frame_counterexample','exact rational example','Positive compression to V fails to imply containment in cycle span.',{'V':[1,0],'C':[[1],[1]],'positive_compression':1,'rank_C':1,'rank_C_plus_V':2})
#6 safe frame
C=sp.Matrix([[1,0,1],[0,1,1]]);alpha=sp.Matrix([2,3]);G=C*C.T;coeff=C.T*G.inv()*alpha;assert C*coeff==alpha
fig,axs=plt.subplots(1,2,figsize=(11.5,7.0),gridspec_kw={'width_ratios':[1.3,1]});fig.subplots_adjust(wspace=.3,left=.06,right=.95,bottom=.16,top=.88)
heat(axs[0],[[1,0,1],[0,1,1]],['c₁','c₂','c₃'],['e₁','e₂']);axs[0].set_title('Classes already lie in V',pad=20)
plain(axs[1]);txt(axs[1],5,4.7,r'$CC^*=\begin{pmatrix}2&1\\1&2\end{pmatrix}$',23) if False else txt(axs[1],5,4.7,'Frame S = [[2,1],[1,2]]',21)
txt(axs[1],5,3.5,'det S = 3',25,TEAL);txt(axs[1],5,2,'α=(2,3)\n= ⅓c₁ + ⁴⁄₃c₂ + ⁵⁄₃c₃',23);txt(axs[1],5,.6,'C λ = α exactly',20,TEAL)
save(fig,6,'corrected_rational_frame','exact rational example','A contained cycle frame gives exact rational reconstruction.',{'C':C.tolist(),'alpha':[2,3],'coefficients':[str(x) for x in coeff]})
#7 positive polyphase
s0=sp.Matrix([[1,0],[0,0]]);s1=sp.ones(2);parent=s0+s1;assert parent.det()==1
fig,axs=plt.subplots(1,3,figsize=(11.5,7));fig.subplots_adjust(wspace=.4,left=.05,right=.97,bottom=.2,top=.85)
for ax,mat,title in zip(axs,[s0,s1,parent],['child 0','child 1','parent = sum']):heat(ax,mat.tolist(),['e₁','e₂'],['e₁','e₂']);ax.set_title(title,pad=18)
fig.text(.5,.07,'Children need not be orthogonal. Their kernels intersect at zero.',ha='center',fontsize=21,color=INK)
save(fig,7,'positive_polyphase','exact rational example','Disjoint index sets partition frame terms, not necessarily orthogonal subspaces.',{'S0':s0.tolist(),'S1':s1.tolist(),'parent':parent.tolist()})
#8 support
fig,ax=canvas();plain(ax)
box(ax,.2,3.6,2.6,1.25,r'$H^{4}_{Z}(X)$');box(ax,3.7,3.6,2.6,1.25,r'$H^4(X)$');box(ax,7.1,3.6,2.7,1.25,r'$H^4(X\setminus Z)$');arrow(ax,(2.8,4.2),(3.7,4.2));arrow(ax,(6.3,4.2),(7.1,4.2),'restriction')
txt(ax,5,2.4,'Supported on Z  ⇔  restriction is zero',22);txt(ax,5,1.4,'If codimension-2 components supply the support:\nintersection matrix M q = b recovers rational coefficients.',19)
save(fig,8,'support_verification','schematic exact sequence','Exactness tests support; the cycle conclusion requires the stated purity and codimension hypotheses.')
#9 correspondence degree
fig,ax=canvas();plain(ax)
box(ax,.5,3.5,3.5,1.4,r'$H^{2p}(X)$',TEAL,27);box(ax,6,3.5,3.5,1.4,r'$H^2(Y)$',TEAL,27);arrow(ax,(4,4.35),(6,4.35),'Γ*');arrow(ax,(6,3.9),(4,3.9),'Λ*',COPPER)
txt(ax,2.3,2.2,r'$\Gamma\in CH^{n-p+1}(X\times Y)$',22);txt(ax,7.5,2.2,r'$\Lambda\in CH^{d+p-1}(Y\times X)$',22)
txt(ax,5,.75,'Example n=4, p=2: lowering codimension 3; return codimension d+1.',19)
save(fig,9,'correspondence_degrees','exact indexing diagram','Pushforward degree shift is 2(r-dim source).')
#10 inverse
M=sp.Matrix([[2,1],[1,2]]);assert M.inv()==(4*sp.eye(2)-M)/3
fig,ax=canvas();plain(ax)
box(ax,.5,3.6,3.4,1.2,'Algebraic operator T\nT = [[2,1],[1,2]]',TEAL,20);box(ax,6.1,3.6,3.4,1.2,'Rational inverse T⁻¹',TEAL,23);arrow(ax,(3.9,4.2),(6.1,4.2),'Cayley–Hamilton')
txt(ax,5,2.6,r'$T^2-4T+3I=0$',27);txt(ax,5,1.5,r'$T^{-1}=(4I-T)/3$',27,TEAL);txt(ax,5,.4,'Requires T to preserve the chosen packet and to be invertible.',19)
save(fig,10,'rational_inverse','exact rational example','A rational polynomial inverse preserves algebraicity if T is induced by algebraic correspondences.',{'T':M.tolist(),'inverse':[[str(x) for x in M.inv().row(i)] for i in range(2)]})
#11 balance
arr=[residues(carrier['character'],70,u) for u in units(70)];fig,ax=canvas();bottom=np.zeros(len(arr))
for j in range(6):vals=[r[j] for r in arr];ax.bar(range(len(arr)),vals,bottom=bottom,color=[TEAL,COPPER,GOLD,'#60969A','#D5B69F','#ABBFC1'][j],width=.87);bottom+=np.array(vals)
ax.axhline(210,color=INK,lw=1.8,ls='--');ax.set_ylim(0,245);ax.set_xticks(range(len(arr))[::2],units(70)[::2]);ax.set_xlabel('Unit multiplier u modulo 70');ax.set_ylabel('Sum of six least-positive residues');ax.text(1,226,'All 24 unit conjugates sum to 3m = 210',fontsize=20)
save(fig,11,'balanced_orbit70','exact measured certificate','Each stacked bar has exactly the target middle residue sum.',{'modulus':70,'units':units(70),'residue_rows':arr})
#12 conductor
fig,ax=canvas();plain(ax)
box(ax,.5,3,4,2.2,'s=(3,60,72,126,183,186)\ngcd(210,s)=3\nconductor = 70',TEAL,19);box(ax,5.5,3,4,2.2,'b=(2,9,129,142,168,180)\ngcd(210,b)=1\nconductor = 210',COPPER,19)
txt(ax,5,1.75,'Same Fermat degree, different exact conductors',23);txt(ax,5,.7,'A coordinate-cube pullback accounts for s, but does not account for b.',19)
save(fig,12,'conductor_descent','exact integer certificate','Conductor distinguishes inflated source and full-conductor target.',{'source_gcd':3,'source_conductor':70,'target_gcd':1,'target_conductor':210})
#13 dyadic SAT3
m=32;star=[1,9,17,20,25,24];stabilizers=[2,30,4,28,16,16];blocks=[[1,16,17,30],[2,9,25,28],[4,16,20,24]];assert Counter(star+stabilizers)==Counter(sum(blocks,[]))
for b in blocks:check_balance(b,32)
fig,ax=canvas();plain(ax)
box(ax,.4,3.5,3.3,1.65,'A₃₂\n(1,9,17,20,25,24)',COPPER,19);box(ax,.4,1,3.3,1.6,'Three Tate pairs\n(2,30), (4,28), (16,16)',TEAL,18)
for i,b in enumerate(blocks):box(ax,5.8,4.45-i*1.65,3.7,1.05,','.join(map(str,b)),TEAL,19)
arrow(ax,(3.7,3.1),(5.8,3.1),'equal multisets')
save(fig,13,'dyadic_sat3','exact multiset certificate','The four-star representative at m32 has an explicit SAT3 identity.',{'packet':star,'stabilizers':stabilizers,'blocks':blocks})
#14 tree
fig,ax=canvas();plain(ax);pos={4:(5,4.9),2:(2.8,3.25),6:(7.2,3.25),1:(1.2,1.55),7:(3.9,1.55),3:(6.1,1.55),5:(8.8,1.55)};selected={1,2,4,7}
for b,p in [(2,4),(6,4),(1,2),(7,2),(3,6),(5,6)]:ax.plot([pos[b][0],pos[p][0]],[pos[b][1],pos[p][1]],color=COPPER if b in selected and p in selected else GRAY,lw=3)
for b,(x,y) in pos.items():ax.add_patch(Circle((x,y),.33,facecolor=COPPER if b in selected else SOFT,edgecolor=INK,lw=1));txt(ax,x,y,str(b),19,'white' if b in selected else INK)
txt(ax,5,.35,'Selected star: four vertices, boundary size 4+2 = 6.',20)
save(fig,14,'dyadic_tree32','exact combinatorial diagram','Internal tree for m32 has p(b)=2b or2(q-b), root4. Zero boundary leaves omitted for clarity.',{'modulus':32,'q':8,'root':4,'parents':{'2':4,'6':4,'1':2,'7':2,'3':6,'5':6},'selected_vertices':[1,2,4,7],'boundary_size':6})
#15 degree33
fig,ax=canvas();plain(ax)
box(ax,.4,3.6,3.4,1.45,'Fermat X₃₃\npacket (7,10,13,19,22,28)',TEAL,18);box(ax,6.2,3.6,3.4,1.45,'Klein–Delsarte cubic Y\nFano variety of lines',TEAL,19);arrow(ax,(3.8,4.3),(6.2,4.3),'monomial map')
txt(ax,5,2.6,'Smith diagonal: (1,33,33,33,33)',23);txt(ax,5,1.4,'Generic torus degree = 33⁴\nCubic divisor lowering supplies the geometric branch.',21);txt(ax,5,.35,'Earlier symmetric surface: [W] = 242 h², with zero primitive part.',18,COPPER)
save(fig,15,'klein33_route','manuscript dependency diagram','Finite lattice identities and residue matching belong to a geometric manuscript proof, not a universal Fermat theorem.')
#16 K23 identity
cert=cm['orbit_records'][0]['selected_certificate'];a=cert['A'];cp=cert['CP'];st=cert['ST'];ell=cert['L'];stabs=[5,45,25,25];assert Counter(a+stabs)==Counter(cp+st+ell)
fig,ax=canvas();plain(ax)
box(ax,.25,3.6,3.6,1.5,'A=(1,7,27,30,41,44)',COPPER,18);box(ax,.25,1.05,3.6,1.6,'Two Tate pairs\n(5,45), (25,25)',TEAL,20)
for y,s in [(4.5,'Curve: (1,5,44)'),(2.9,'Surface: (7,25,27,41)'),(1.3,'Lower curve: (25,30,45)')]:box(ax,5.85,y-0.6,3.85,1.2,s,TEAL,18)
arrow(ax,(3.85,3.1),(5.85,3.1),'exact identity')
save(fig,16,'k23_factorization50','exact multiset certificate','The m50 example separates curve, surface and lower curve after two pair stabilizations.',{'modulus':50,'A':a,'stabilizers':stabs,'CP':cp,'ST':st,'L':ell})
#17 CM signs
ell7=[1,2,4];us=units(7);hs=[sum(residues(ell7,7,u))//7 for u in us];assert hs==[1,1,2,1,2,2]
fig,ax=canvas();ax.bar(us,[1 if h==2 else -1 for h in hs],color=[TEAL if h==2 else COPPER for h in hs],width=.64);ax.axhline(0,color=INK,lw=1);ax.set_ylim(-1.5,1.5);ax.set_yticks([-1,1],['negative\nimaginary','positive\nimaginary']);ax.set_xticks(us);ax.set_xlabel('Embedding σᵤ of Q(ζ₇)');ax.set_title('Δ=(1−ζ₇)(1−ζ₇²)(1−ζ₇⁴),   conjugate Δ = −Δ',pad=15,fontsize=21)
save(fig,17,'cm_imaginary_sign','exact sign diagram','Signs derived from integer residue sums, no floating evaluation of roots of unity.',{'lower_packet':ell7,'modulus':7,'units':us,'hodge_ages':hs,'imaginary_signs':[1 if h==2 else -1 for h in hs]})
#18 Chow missing
fig,ax=canvas();plain(ax)
box(ax,.35,3.4,3.65,1.5,'Lower Fermat curve\nrational orbit factor of H¹',TEAL,20);box(ax,6,3.4,3.65,1.5,'Tensor packet N(1)\nmatching Hodge type',TEAL,20)
arrow(ax,(4,4.1),(6,4.1),'desired Γ*',COPPER,style='-|>');txt(ax,5,2.75,'Chow correspondence still required',24,COPPER);txt(ax,5,1.45,'Character covariance + a nonzero projected coefficient\n+ rational reconstruction of the whole orbit',19)
txt(ax,5,.45,'CM sign matching identifies a candidate. It does not construct Γ.',18)
save(fig,18,'missing_chow_bridge','schematic open dependency','Half-plane signs do not select a rational half-orbit idempotent. Character rank one is a splitting-field statement.')
#19 A70
fig,ax=canvas();heat(ax,carrier['matrix'],['y₀','y₁','y₂','y₃','y₄','y₅'],['monomial 1','monomial 2','monomial 3','monomial 4','monomial 5','monomial 6']);ax.set_title('Rows: target monomials. Columns: invariant exponent vectors.',pad=18,fontsize=19)
save(fig,19,'carrier70_matrix','exact integer certificate','Selected6x6matrix has det−2100, Aᵀa=70(3,3,1,3,2,3).',{'A':carrier['matrix'],'determinant':-2100})
#20 weights
fig,ax=canvas();ax.bar(range(6),W,color=TEAL);ax.set_xticks(range(6),['y₀','y₁','y₂','y₃','y₄','y₅']);ax.set_ylim(0,12);ax.set_ylabel('Primitive integer weight Wᵢ');ax.set_title('AW = 30·1     sum Wᵢ = 33     normalized sum = 11/10',fontsize=20,pad=15)
for i,w in enumerate(W):ax.text(i,w+.25,str(w),ha='center',fontsize=21)
ax.text(2.5,10.7,'Kᵧ = (30−33)H = −3H',ha='center',fontsize=24,color=COPPER)
save(fig,20,'carrier70_weights','exact integer certificate','Negative canonical coefficient requires integral normal wellformed carrier hypotheses.',{'weights':W,'degree':30,'sum_weights':33,'canonical_coefficient':-3})
#21 singular strata
fig,ax=canvas();zero=[[1,1,1,1,0,0],[1,1,0,1,0,1],[1,1,0,0,1,1]];heat(ax,zero,['y₀','y₁','y₂','y₃','y₄','y₅'],['plane 1','plane 2','plane 3'],cmap=ListedColormap(['white',SOFT]));ax.set_title('1 means the coordinate is zero. Each affine plane has dimension 2.',pad=18,fontsize=20)
fig.text(.5,.02,'Cone dimension5, singular dimension2: codimension3. Normality is a separate geometric step.',ha='center',fontsize=18,color=INK)
save(fig,21,'carrier70_singular_locus','exact coordinate certificate','Gradient radical is(y0,y1,y2y5,y3y4,y3y5). Three component ideals shown.',{'zero_coordinate_rows':zero,'cone_dimension':5,'singular_locus_dimension':2})
#22 torus B
fig,ax=canvas();heat(ax,data['carrier_B'],['x₀','x₁','x₂','x₃','x₄','x₅'],['y₀','y₁','y₂','y₃','y₄','y₅'],cmap='RdBu',fs=16);ax.set_title('B = 210 A⁻¹. Negative exponents are used only on the torus.',pad=20,fontsize=20)
fig.text(.5,.015,'AB = 210 I       B1 = 7W       torus cover → descent → lowest-weight lift',ha='center',fontsize=20,color=INK)
save(fig,22,'carrier70_torus_matrix','exact integer certificate','Matrix certifies monomial torus identities. Compact geometric extension is an additional argument.',{'B':data['carrier_B'],'AB':'210I','B1':[7*w for w in W]})
#23 twoorbit dims
fig,ax=canvas();fig.subplots_adjust(left=.35,bottom=.18);ax.barh([1,0],[24,48],color=[TEAL,COPPER],height=.48);ax.set_yticks([1,0],['source s: conductor 70','target b: conductor 210']);ax.set_xlim(0,58);ax.set_xticks([0,12,24,36,48]);ax.set_xlabel('Distinct ordered Galois conjugates / rational packet dimension')
for y,n in [(1,24),(0,48)]:ax.text(n+1,y,str(n),va='center',fontsize=26)
ax.set_title('All conjugates have residue sum630 at Fermat degree210.',fontsize=20,pad=18)
save(fig,23,'transfer210_orbits','exact finite orbit count','Source24 and target48 ordered conjugates have disjoint orbits.',{'source_dimension':24,'target_dimension':48,'source_conductor':70,'target_conductor':210})
#24 transferincidences
ks=sorted(left);fig,ax=canvas();xs=np.arange(len(ks));ax.bar(xs-.18,[left[k] for k in ks],width=.35,color=TEAL,label='left');ax.bar(xs+.18,[right[k] for k in ks],width=.35,color=COPPER,label='right');ax.set_xticks(xs,ks,rotation=90,fontsize=14);ax.set_ylim(0,4.5);ax.set_ylabel('Multiplicity');ax.set_xlabel('Residue modulo210');ax.legend(frameon=False,ncol=2);ax.set_title('Every residue has identical multiplicity:30 entries on each side.',fontsize=20,pad=18)
save(fig,24,'transfer210_incidence','exact integer multiset certificate','14termidentity independently reconstructed from frozen transfer.',{'left':dict(left),'right':dict(right),'term_count':14,'total_each_side':30})
#25 stabilize
fig,ax=canvas();plain(ax)
box(ax,.4,3.7,3,1.6,'b ⊔ L = s ⊔ R\n30 entries',TEAL,20);box(ax,6.4,3.7,3.2,1.6,'Append −L\n54 entries',TEAL,20);arrow(ax,(3.4,4.5),(6.4,4.5),'+24')
box(ax,6.4,.9,3.2,1.5,'Remove 24 pairs\n6-entry packet b',COPPER,20);arrow(ax,(8,3.7),(8,2.4),'classical removal')
txt(ax,2.8,1.65,'s, R, −L are algebraic\nunder cited constructors.\n54 entries live on X₂₁₀⁵².',19)
save(fig,25,'transfer210_stabilization','exact count and dependency diagram','Geometric complementary-pair removal, not formal subtraction of unknown cycles.',{'left_auxiliary_length':24,'stabilized_length':54,'stabilized_dimension':52,'pairs_removed':24,'final_length':6})
#26 capacities
fig,ax=canvas();vals=[float(F(x['weight_sum'])) for x in caps]+[1];labels=[str(x['modulus']) for x in caps]+['210'];ax.bar(labels,vals,color=[TEAL if v>1 else COPPER for v in vals]);ax.axhline(1,color=INK,ls='--',lw=1.5);ax.set_ylim(0,2.4);ax.set_ylabel('Exact capacity of specified character');ax.set_xlabel('Modulus (one specified packet at each level)')
for i,x in enumerate(caps):ax.text(i,vals[i]+.08,x['weight_sum'],ha='center',fontsize=19)
ax.text(7,1.08,'1',ha='center',fontsize=19);ax.set_title('Capacity>1 does not alone prove a normal six-column carrier.',fontsize=20,pad=18)
save(fig,26,'capacity_values','exact primal dual values','Seven named certificates plus degree210 capacity, not census of all packets.',{'characters':[{'modulus':x['modulus'],'character':x['character'],'capacity':x['weight_sum']} for x in caps]+[{'modulus':210,'character':target,'capacity':'1'}]})
#27 globaldual
costs=[31,87,57,101,84,60];assert sum(costs)==420
fig,ax=canvas();plain(ax)
box(ax,.4,3.45,4.1,1.75,'Degrees1…13\n27,131 columns\n143 invariant columns',TEAL,22);box(ax,5.5,3.45,4.1,1.75,'Degree≥14\ncost≥14·31\n434>420',COPPER,22)
txt(ax,5,2.45,'η = (31,87,57,101,84,60)/420',24);txt(ax,5,1.45,'Every nonzero invariant column satisfies η·v≥1.',22);txt(ax,5,.45,'η·1 = 1  ⇒  total normalized matrix weight ≤1.',21)
save(fig,27,'global_dual210','exact finite premise plus uniform tail','Finite enumerator range combined with an all-degree lower bound.',{'dual_costs':costs,'denominator':420,'finite_degree_max':13,'finite_count':27131,'invariant_count':143,'uniform_tail_minimum':434})
#28 family obstruction
fig,ax=canvas();plain(ax)
box(ax,.4,3.6,9.2,1.6,'a=(b,b+q,b+2q,b+3q,b+4q,5(q−b)),  m=5q',TEAL,22)
txt(ax,5,2.75,'q>5,  1≤b<q,  gcd(b,q)=1',22);txt(ax,5,1.75,'y=(1,1,1,1,1,q−5)/q,    y·1=1',24,COPPER);txt(ax,5,.65,'Invariant column ⇒ positive integer y·v≥1 ⇒ capacity exactly1.',20)
save(fig,28,'fivephase_capacity_obstruction','symbolic theorem diagram','Uniform congruence proof excludes one matrix criterion, not algebraicity or Hodge.')
#29 holomorphic power
a110=[1,24,62,71,81,91];c110=residues(a110,110,11);assert c110==[11,44,22,11,11,11] and sum(c110)==110;check_balance(a110,110)
fig,ax=canvas();ax.bar(range(6),a110,color=TEAL,width=.4,label='a (sum330)');ax.bar(np.arange(6)+.4,c110,color=COPPER,width=.4,label='11a mod110 (sum110)');ax.set_xticks(np.arange(6)+.2,['0','1','2','3','4','5']);ax.set_ylabel('Least-positive coordinate residue');ax.legend(frameon=False,fontsize=18);ax.set_title('A nonunit power creates a full-support holomorphic character.',fontsize=20,pad=20)
save(fig,29,'holomorphic_power_obstruction','exact character witness','A direct diagonal quotient capturing a also captures11a. Nonunit11 does not contradict unit balance.',{'modulus':110,'a':a110,'k':11,'ka':c110,'source_sum':330,'power_sum':110})
#30 cycle containment
fig,ax=canvas();plain(ax)
for y,s in [(4.6,r'$e_1(x_0^q,\ldots,x_4^q)=0$'),(3.3,r'$e_2(x_0^q,\ldots,x_4^q)=0$'),(2.0,r'$P-\kappa z^5=0,\quad\kappa^q=-1/5$')]:box(ax,.45,y-.5,5.3,1,s,TEAL,22)
box(ax,6.6,2,3,2.6,'Newton identity\n'+r'$p_5=5P^q$'+'\n'+r'$F=5P^q+z^{5q}=0$',COPPER,20);arrow(ax,(5.75,3.3),(6.6,3.3))
txt(ax,5,.6,'Complete-intersection degrees q,2q,5. Surface degree10q².',21)
save(fig,30,'explicit_fivephase_surface','symbolic construction diagram','Standard Aoki family reconstructed directly. Surface integral, not assumed smooth.')
#31 socle
q=7;b=1;m=35;a=[1,8,15,22,29,30];dexp=[x-1 for x in a];qexp=[m-x-1 for x in a];assert [x+y for x,y in zip(dexp,qexp)]==[m-2]*6
fig,axs=plt.subplots(1,3,figsize=(11.5,7),gridspec_kw={'width_ratios':[1,1,1]});fig.subplots_adjust(wspace=.42,left=.07,right=.98,bottom=.2,top=.85)
for ax,vals,title in zip(axs,[dexp,qexp,[33]*6],['determinant term','dual numerator Q','socle product']):ax.barh(range(6),vals,color=COPPER if title=='dual numerator Q' else TEAL);ax.set_xlim(0,36);ax.set_yticks(range(6),['x₀','x₁','x₂','x₃','x₄','z']);ax.set_title(title,pad=18,fontsize=20);ax.invert_yaxis();
fig.text(.5,.08,'Coefficient 10,504,375 κ⁶ ≠0.   Exact period = (2πi)² κ⁶ /350.',ha='center',fontsize=22,color=INK)
save(fig,31,'socle_pairing35','exact exponent and coefficient certificate','Unique complementary determinant term survives the Jacobian ideal.',{'determinant_exponents':dexp,'dual_exponents':qexp,'socle_exponents':[33]*6,'coefficient_integer':10504375,'kappa_exponent':6,'period_denominator':350})
#32 orbit reconstruction
fig,ax=canvas();plain(ax)
box(ax,.35,3.5,3.25,1.65,'Rational cycle class\nξ=[Zκ]−2q h²',TEAL,22);box(ax,6.4,3.5,3.25,1.65,'Rational group span\nQ[Gₘ]·ξ',TEAL,22);arrow(ax,(3.6,4.3),(6.4,4.3),'translates')
txt(ax,5,2.45,'Nonzero support in every listed eigenline\n+ multiplicity-one decomposition = whole rational packet',21)
txt(ax,5,1.1,'At q=7: one ordered packet dimension24;\nall first-five permutation sectors dimension720.',22,COPPER)
save(fig,32,'rational_orbit_reconstruction','exact dimension and dependency diagram','120(q−1) is standard-family sector dimension for fixed last coordinate, not all Hodge classes.',{'q':7,'packet_dimension':24,'permutation_sector_dimension':720})
#33 Weil tangent
fig,ax=canvas();fig.subplots_adjust(left=.35,bottom=.18);ax.barh([2,1,0],[18,6,12],color=[GRAY,COPPER,TEAL],height=.55);ax.set_yticks([2,1,0],['ambient real tangent','chosen nonsplit graph','split control graph']);ax.set_xlim(0,21);ax.set_xticks([0,6,12,18]);ax.set_xlabel('Real tangent dimension')
for y,n in [(2,18),(1,6),(0,12)]:ax.text(n+.5,y,str(n),fontsize=24,va='center')
ax.set_title('A smaller tangent space for one graph does not bound all cycles.',fontsize=20,pad=20)
save(fig,33,'weil_graph_tangent_boundary','exact linearized audit','Finite tangent ranks are about a selected graph. Replacement factors invalidate proposed nonalgebraicity inference.',{'ambient_real_dimension':18,'nonsplit_graph_real_dimension':6,'split_control_real_dimension':12,'not_claimed':'Hodge counterexample or all-cycle rank bound'})
#34 ledger
fig,ax=canvas();plain(ax)
rows=[('Degree70 carrier','special-case manuscript + exact replay',TEAL),('Degree210 transfer','conditional on carrier + classical maps',TEAL),('Five-phase standard surfaces','known family, explicit determinant',TEAL),('Universal matrix constructor','false: capacity-one family',COPPER),('K23 Chow correspondence','construction remains open',COPPER),('Universal mixed-prime grammar','coverage remains open',COPPER)]
for i,(name,status,col) in enumerate(rows):y=5.6-i*.92;ax.add_patch(Rectangle((.3,y-.36),9.4,.72,facecolor=SOFT if col==TEAL else '#F5EAE3',edgecolor='white'));txt(ax,.55,y,name,17,col,ha='left');txt(ax,4.6,y,status,16,INK,ha='left')
save(fig,34,'status_and_targets','status matrix','Keeps finite replay, special geometry, known families, false constructor and universal gaps distinct.')
# reproducibility manifests
used.append(ROOT/'evidence/literature/source_contracts.json')
pins=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in used]
contract={'edition':'1.0','date':'2026-10-09','author':'Komorebi P.','arithmetic':'integer/Fraction/SymPy exact assertions before float display coordinates','figure_count':len(records),'python':platform.python_version(),'matplotlib':matplotlib.__version__,'input_pins':pins,'figures':records,'boundaries':['Schematics have no measured geometric scale.','Finite examples are not universal proof.','Matplotlib converts exact certificate values only for display.','No generated imagery.','General rational Hodge conjecture is not proved.']}
(ROOT/'visual/figure_contract.json').write_text(json.dumps(contract,indent=2,default=str)+'\n')
(ROOT/'visual/figure_data.json').write_text(json.dumps(data,indent=2,default=str)+'\n')
print(f'{len(records)} figures generated with pinned input certificates')
