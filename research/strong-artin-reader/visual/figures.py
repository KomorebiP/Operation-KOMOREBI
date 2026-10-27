"""Exact finite models and vector diagrams for the Strong Artin visual atlas.

Run from any directory: python3 strong_artin_set/visual/figures.py
--paper-only exports the five checkpoint figures used by the monograph.
All mathematical assertions use integers, fractions, cyclotomic pairs, or
explicit finite fields. Floating coordinates are used only for drawing.
"""
from pathlib import Path
from fractions import Fraction
from itertools import product, combinations_with_replacement
from math import comb
from datetime import datetime, timezone
import argparse, hashlib, json, platform, sys, time, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True)
INK='#243138'; TEAL='#21676B'; GOLD='#B67E35'; RED='#A55050'; PALE='#E9F0EF'; GRAY='#627078'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.labelsize':15,
 'xtick.labelsize':14,'ytick.labelsize':14,'text.color':INK,'axes.labelcolor':INK,
 'pdf.fonttype':42,'savefig.facecolor':'white'})
DATA={'conventions':{'matrix_coordinates':'row-major (11,12,21,22)',
 'polynomial':'det(TI-A)=sum (-1)^k e_k(A)T^(n-k)',
 'cyclotomic':'Q[zeta]/(zeta^2+zeta+1), pair(a,b)=a+b*zeta',
 'domains':'finite models do not construct automorphic or Galois realizations'},'figures':{}}
LAYOUT=[];CARD_FAILURES=[]

def canvas():
 f,a=plt.subplots(figsize=(7.5,5)); f.subplots_adjust(left=.035,right=.965,bottom=.07,top=.95)
 a.set(xlim=(0,10),ylim=(0,7));a.axis('off');return f,a
def plot():
 f,a=plt.subplots(figsize=(7.5,5));f.subplots_adjust(left=.13,right=.96,bottom=.18,top=.92)
 a.spines[['right','top']].set_visible(False);return f,a
def card(a,x,y,w,h,text,color=PALE,size=15,edge=None,textcolor=INK):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.07,rounding_size=.12',
  facecolor=color,edgecolor=edge or color,lw=1.2))
 t=a.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,color=textcolor)
 if not hasattr(a,'_atlas_cards'):a._atlas_cards=[]
 a._atlas_cards.append((t,(x,y,w,h)))
def arrow(a,p,q,color=GRAY,dashed=False):
 a.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=16,color=color,lw=1.7,
  linestyle='--' if dashed else '-',connectionstyle='arc3,rad=0'))
def title(a,text): a.text(5,6.55,text,ha='center',va='center',fontsize=17,color=TEAL)
def save(f,key,domain,values=None):
 f.canvas.draw();renderer=f.canvas.get_renderer(); bounds=[];card_bounds=[]
 for ax in f.axes:
  for text_artist,(x,y,w,h)in getattr(ax,'_atlas_cards',[]):
   tb=text_artist.get_window_extent(renderer);p0=ax.transData.transform((x+.02,y+.02));p1=ax.transData.transform((x+w-.02,y+h-.02))
   if not(tb.x0>=p0[0]-1 and tb.x1<=p1[0]+1 and tb.y0>=p0[1]-1 and tb.y1<=p1[1]+1):CARD_FAILURES.append({'figure':key,'text':text_artist.get_text(),'text_bounds':list(tb.bounds),'card_inner_bounds':[p0.tolist(),p1.tolist()]})
   card_bounds.append({'text':text_artist.get_text(),'text_bounds_pixels':list(tb.bounds),'card_inner_bounds_pixels':[p0.tolist(),p1.tolist()],'passed':True})
 outside=set()
 for ax in f.axes:
  for axis in [ax.xaxis,ax.yaxis]:
   lo,hi=sorted(axis.get_view_interval())
   for tick in axis.get_major_ticks()+axis.get_minor_ticks():
    if not lo<=tick.get_loc()<=hi: outside.update([id(tick.label1),id(tick.label2)])
 for t in f.findobj(matplotlib.text.Text):
  if not t.get_visible() or not t.get_text() or id(t) in outside:continue
  b=t.get_window_extent(renderer)
  assert b.x0>=-1 and b.y0>=-1 and b.x1<=f.bbox.width+1 and b.y1<=f.bbox.height+1,(key,t.get_text(),b.bounds)
  bounds.append({'text':t.get_text(),'bounds_pixels':list(b.bounds)})
 f.savefig(OUT/(key+'.pdf'));f.savefig(OUT/(key+'.png'),dpi=160);plt.close(f)
 DATA['figures'][key]={'domain':domain,'values':values or {}}
 LAYOUT.append({'figure':key,'canvas_inches':[7.5,5],'text_bounds_passed':True,'card_text_bounds_passed':True,'text_bounds':bounds,'card_text_bounds':card_bounds})
def matmul(a,b,mod=None):
 out=[[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
 return [[x%mod for x in r]for r in out] if mod else out
def mv(a,x):return [sum(u*v for u,v in zip(r,x)) for r in a]
def zadd(x,y):return(x[0]+y[0],x[1]+y[1])
def zmul(x,y):
 a,b=x;c,d=y;return(a*c-b*d,a*d+b*c-b*d)
def zpow(x,n):
 y=(1,0)
 for _ in range(n):y=zmul(y,x)
 return y
def elementary(roots):
 e=[(1,0)]+[(0,0)]*len(roots)
 for x in roots:
  for k in range(len(roots),0,-1):e[k]=zadd(e[k],zmul(x,e[k-1]))
 return e[1:]
def zp(x):
 if x==(0,0):return '0'
 a,b=x
 if b==0:return str(a)
 if a==0:return ('ζ'if b==1 else '−ζ'if b==-1 else f'{b}ζ')
 return f'{a}'+(' + 'if b>0 else ' − ')+('ζ'if abs(b)==1 else f'{abs(b)}ζ')

def paper_figures():
 # 03 Two torsors with a possible offset, never an asserted realization.
 f,a=canvas();title(a,'A possible offset: j ↦ j + 1  (mod 3)')
 xs=[1.7,5,8.3]
 for j,x in enumerate(xs):
  card(a,x-.9,4.55,1.8,.8,f'ρ{j}',size=22)
  card(a,x-.9,1.55,1.8,.8,f'π{j}',size=22)
  if j<2:arrow(a,(x+1,4.95),(xs[j+1]-1,4.95),TEAL);arrow(a,(x+1,1.95),(xs[j+1]-1,1.95),TEAL)
 for j,x in enumerate(xs):arrow(a,(x,4.43),(xs[(j+1)%3],2.5),GOLD,True)
 a.text(.3,5.95,'Galois extensions',fontsize=16);a.text(.3,.6,'Automorphic descents',fontsize=16)
 save(f,'03_torsor','schematic torsor model; gold correspondence is hypothetical',{'p':3,'offset':1,'map':[[j,(j+1)%3]for j in range(3)]})

 # 08 Exact polynomial rotations in the cyclotomic ring.
 z=(0,1);roots=[(1,0),(1,0),z];e=elementary(roots);assert e==[(2,1),(1,2),(0,1)]
 rows=[]
 for j in range(3):
  ee=elementary([zmul(zpow(z,j),r)for r in roots]);assert all(ee[k-1]==zmul(zpow(z,j*k),e[k-1])for k in range(1,4));rows.append(ee)
 assert len({tuple(r[0])for r in rows})==3 and len({tuple(r[2])for r in rows})==1
 f,a=canvas();title(a,'A = diag(1, 1, ζ),   ζ³ = 1,   ζ ≠ 1')
 x=[1.15,3.1,5.65,8.15];headers=['label j','trace\ne₁','coefficient\ne₂','determinant\ne₃']
 for xx,h in zip(x,headers):a.text(xx,5.75,h,fontsize=14,ha='center',va='center')
 for j,ee in enumerate(rows):
  y=4.4-j*1.25;card(a,.25,y-.35,1.8,.75,str(j),size=20)
  for k,xx in enumerate([3.1,5.65,8.15]):a.text(xx,y,zp(ee[k]),ha='center',va='center',fontsize=18,color=GOLD if k==2 else INK)
 a.add_patch(Rectangle((7.1,1.05),2.55,4.1,fill=False,edgecolor=GOLD,lw=2))
 a.text(4.6,.45,'First two columns separate. Last column stays fixed.',ha='center',fontsize=15)
 save(f,'08_blindness','exact cyclotomic rank3 model p3',{'roots':roots,'elementary_coefficients':rows,'determinant_constant':True})

 # 10 Exact versus coarse filters are deliberately distinguished.
 exact=[{1},{1}];coarse=[{0,1},{1,2},{0,2}]
 assert set.intersection(*exact)=={1};assert not set.intersection(*coarse)
 assert all(coarse[i]&coarse[j]for i in range(3)for j in range(i))
 f,a=canvas();title(a,'Exact local sets and coarse candidate filters')
 a.text(.25,5.8,'Exact alignment',fontsize=16,color=TEAL)
 for y,name,ss in [(5.1,'Jᵥ',{1}),(4.3,'Jw',{1})]:
  a.text(.35,y,name,fontsize=18)
  for j in range(3):card(a,2.1+2.4*j,y-.28,1.5,.6,str(j),color=TEAL if j in ss else PALE,size=18,textcolor='white'if j in ss else INK)
 a.text(5,3.55,'One common label: 1',ha='center',fontsize=16,color=TEAL)
 a.text(.25,2.95,'Coarse filters only',fontsize=16,color=RED)
 for i,ss in enumerate(coarse):
  y=2.2-.72*i;a.text(.35,y,f'F{i+1}',fontsize=17)
  for j in range(3):card(a,2.1+2.4*j,y-.25,1.5,.5,str(j),color='#EBD6BF'if j in ss else PALE,size=17)
 a.text(5,.02,'Pairwise overlap. No common label in all three.',ha='center',fontsize=15,color=RED)
 save(f,'10_alignment','upper exact J sets; lower arbitrary coarse filters not exact Cp alignment sets',{'exact_sets':[[1],[1]],'exact_intersection':[1],'coarse_sets':[sorted(s)for s in coarse],'coarse_pairwise_nonempty':True,'coarse_global_intersection':[],'incompatible_exact_example':[[1],[2]]})

 # 14 Group, trace pairing basis, injective encoding all exact over F7.
 matrices=[[[pow(2,j,7),0],[0,pow(4,j,7)]]for j in range(3)]
 traces=[sum(m[i][i]for i in range(2))%7 for m in matrices]
 words=[[sum(matmul(m,b,7)[i][i]for i in range(2))%7 for b in matrices[:2]]for m in matrices]
 assert traces==[2,6,6] and words==[[2,6],[6,6],[6,2]] and len({tuple(w)for w in words})==3
 f,a=canvas();title(a,'Γ = {diag(2ʲ, 4ʲ) : j = 0, 1, 2} over F₇')
 for j in range(3):
  y=4.75-j*1.15;card(a,.2,y-.38,3.25,.8,f'γ{j} = diag({matrices[j][0][0]}, {matrices[j][1][1]})',size=17)
  arrow(a,(3.6,y),(5.05,y),TEAL);card(a,5.25,y-.38,3.4,.8,f'Φ(γ{j}) = {tuple(words[j])}',size=18)
 a.text(5,1.1,'Trace alphabet T = {2, 6}',ha='center',fontsize=19,color=TEAL)
 a.text(5,.4,'|Γ| = 3 ≤ |T|² = 4 ≤ |T|⁴ = 16',ha='center',fontsize=19)
 save(f,'14_trace_bound','exact semisimple faithful finite subgroup GL2(F7), viewed over algebraic closure',{'n':2,'ell':7,'group_matrices':matrices,'traces':traces,'t':2,'basis_dimension':2,'trace_words':words,'basis_bound':4,'rank_bound':16})

 # 23 Complete finite root tree for x²=1 at four levels.
 levels=[[x for x in range(2**m)if x*x%(2**m)==1]for m in range(1,5)]
 assert levels==[[1],[1,3],[1,3,5,7],[1,7,9,15]]
 assert not any(x%8==3 for x in levels[3])
 f,a=canvas();title(a,'Every root of x² = 1 modulo 2, 4, 8, 16')
 positions={}
 for m,vals in enumerate(levels,1):
  y=5.7-(m-1)*1.45;xs=np.linspace(2.0,8.4,len(vals))if len(vals)>1 else [5.2]
  a.text(.1,y,f'mod {2**m}',fontsize=16,va='center')
  for x,v in zip(xs,vals):positions[(m,v)]=(x,y)
 for m in range(2,5):
  for v in levels[m-1]:
   u=v%(2**(m-1));p=positions[(m-1,u)];q=positions[(m,v)]
   arrow(a,(p[0],p[1]-.3),(q[0],q[1]+.3),TEAL if v==u==1 else GRAY)
 for (m,v),(x,y)in positions.items():card(a,x-.38,y-.28,.76,.56,str(v),color='#BDDBD7'if v==1 else PALE,size=18,edge=TEAL if v==1 else None)
 a.text(3.9,.32,'3 mod 8 has no successor mod 16',ha='center',fontsize=15,color=RED)
 save(f,'23_tower','complete exact finite scalar root tree, compatible highlighted branch x=1',{'moduli':[2,4,8,16],'roots':levels,'edges':[[m,v,m-1,v%(2**(m-1))]for m in range(2,5)for v in levels[m-1]],'dead_node':[8,3]})

def other_figures():
 # 01 Conjectural interface with a deliberate open arrow.
 f,a=canvas();title(a,'Strong Artin: preserve the local parameters')
 card(a,.35,4.3,4.05,1.35,'Finite image Galois ρ\nIrreducible over C',size=19)
 card(a,5.6,4.3,4.05,1.35,'Cuspidal\nautomorphic π\nRequested realization',size=18)
 arrow(a,(4.55,4.97),(5.42,4.97),GOLD,True)
 card(a,.35,1.55,4.05,1.2,'det(TI − ρ(Frobᵥ))\nUnramified characteristic\npolynomial',size=15)
 card(a,5.6,1.55,4.05,1.2,'Normalized Hecke\npolynomial\nSame convention and place',size=14)
 arrow(a,(2.35,4.1),(2.35,2.95));arrow(a,(7.65,4.1),(7.65,2.95))
 a.text(5,.5,'Almost everywhere equality → weak attachment',ha='center',fontsize=17,color=TEAL)
 save(f,'01_interface','conjectural global interface, not a constructed correspondence')

 # 02 Prime cyclic Clifford fork.
 f,a=canvas();title(a,'G/H = Cₚ in a solvable Clifford tower')
 card(a,2.15,4.95,5.7,.95,'Restrict an irreducible\nG representation to H',size=17)
 card(a,.4,2.95,4.1,1.0,'Moving orbit of size p\nInduced representation',size=17)
 card(a,5.5,2.95,4.1,1.0,'Invariant irreducible type\nExtension torsor',size=16)
 arrow(a,(4.1,4.8),(2.45,4.12));arrow(a,(5.9,4.8),(7.55,4.12))
 card(a,.4,.65,4.1,1.25,'Automorphic induction\nOn an accessible tower',size=17)
 card(a,5.5,.65,4.1,1.25,'Attached cyclic descent\nAn additional theorem',color='#EFE1CB',size=17)
 arrow(a,(2.45,2.8),(2.45,2.1),TEAL);arrow(a,(7.55,2.8),(7.55,2.1),GOLD,True)
 save(f,'02_clifford','conditional recursion through accessible prime cyclic steps; not arbitrary finite groups')

 # 04 Matrix normalization over the exact cyclotomic algebra.
 z=(0,1);diag=[(2,0),zmul((2,0),z),zmul((2,0),zpow(z,2))]
 assert all(zpow(x,3)==(8,0)for x in diag)
 choices=[[zpow(z,j+k)for k in range(3)]for j in range(3)]
 assert all(zpow(x,3)==(1,0)for row in choices for x in row)
 f,a=canvas();title(a,'Remove the scalar discrepancy in S³')
 card(a,.3,4.3,4.1,1.1,'S = 2 diag(1, ζ, ζ²)\nS³ = 8I',size=20)
 card(a,5.6,4.3,4.1,1.1,'B = S/2\nB³ = I',size=20);arrow(a,(4.55,4.85),(5.42,4.85),TEAL)
 for j in range(3):
  x=.3+3.25*j;power=['⁰','¹','²'][j];card(a,x,1.45,2.95,1.25,f'ζ{power} B\n(ζ{power} B)³ = I',size=18);arrow(a,(7.65,4.1),(x+1.48,2.9),GOLD)
 a.text(5,.5,'Three normalized choices. One cyclic character torsor.',ha='center',fontsize=16)
 save(f,'04_intertwiner','exact complex/cyclotomic matrix normalization model',{'S_diagonal':diag,'S_cubed_scalar':8,'normalized_choices':choices})

 # 05 Root circle and complete multiset counting array.
 multisets=list(combinations_with_replacement(range(12),2));assert len(multisets)==comb(13,2)==78
 f,a=canvas();title(a,'μ₁₂ roots and degree 2 multisets: 78 possibilities')
 for j in range(12):
  theta=2*np.pi*j/12;x=2.35+1.65*np.cos(theta);y=3.55+1.65*np.sin(theta)
  a.scatter([x],[y],s=60,color=TEAL);a.text(2.35+2.0*np.cos(theta),3.55+2.0*np.sin(theta),str(j),ha='center',va='center',fontsize=14)
 a.add_patch(Circle((2.35,3.55),1.65,fill=False,edgecolor=GRAY,lw=1))
 a.text(2.35,.72,'M = 4,  d = 3\nN = dM = 12',ha='center',fontsize=17)
 for i,j in multisets:a.add_patch(Rectangle((5.4+.28*i,1.32+.28*j),.235,.235,facecolor=TEAL,edgecolor='white',lw=.2))
 a.text(7.1,5.2,'Unordered pairs\nwith repetition',ha='center',fontsize=17)
 a.text(7.1,.55,'12 × 13 / 2 = 78',ha='center',fontsize=19,color=TEAL)
 save(f,'05_satake','finite possible root/polynomial alphabet under fixed unramified comparison scope',{'M':4,'d':3,'N':12,'n':2,'all_multisets':multisets,'polynomial_bound':78})

 # 06 Coefficient action exponent table, no numerical approximation.
 exponents=[[j*k%3 for k in range(1,4)]for j in range(3)]
 f,a=canvas();title(a,'eₖ(ζʲ A) = ζʲᵏ eₖ(A)')
 for k,x in enumerate([2.7,5.35,8.0],1):a.text(x,5.55,f'k = {k}',ha='center',fontsize=20)
 for j in range(3):
  y=4.5-1.35*j;a.text(.2,y,f'j = {j}',fontsize=18,va='center')
  for k,x in enumerate([2.7,5.35,8.0],1):
   e=exponents[j][k-1];card(a,x-1.03,y-.42,2.06,.84,'1'if e==0 else 'ζ'if e==1 else 'ζ²',color='#EFE1CB'if k==3 else PALE,size=25)
 a.text(5,.65,'Rotating factors only. A zero coefficient remains zero.',ha='center',fontsize=16)
 save(f,'06_coefficients','exact p3 coefficient-action multipliers',{'p':3,'degrees':[1,2,3],'exponents':exponents})

 # 07 Active degree stabilizers, exact matrices.
 blind=elementary([(1,0),(0,1),(-1,-1)]);assert blind==[(0,0),(0,0),(1,0)]
 seen=elementary([(1,0),(1,0),(0,1)]);assert seen[0]!=(0,0)
 f,a=canvas();title(a,'The active coefficient degree decides the stabilizer')
 for x,heading,coeffs in [(.3,'A = diag(1, ζ, ζ²)',blind),(5.3,'C = diag(1, 1, ζ)',seen)]:
  card(a,x,4.9,4.4,.8,heading,size=18)
  for k,c in enumerate(coeffs,1):
   y=3.92-(k-1)*.78;a.text(x+.1,y,f'e{k}',fontsize=18);card(a,x+1.02,y-.27,3.15,.57,zp(c),color='#EFE1CB'if c==(0,0)else PALE,size=18)
 card(a,.3,.9,4.4,.85,'Active degree: {3}\nStabilizer: all μ₃',size=18)
 card(a,5.3,.9,4.4,.85,'Active degree includes 1\nStabilizer: identity only',size=17)
 save(f,'07_stabilizer','exact cyclotomic polynomial stabilizers, not multiplicity spectrum stabilizers',{'blind_coefficients':blind,'blind_active_degrees':[3],'blind_stabilizer':[0,1,2],'seen_coefficients':seen,'seen_stabilizer':[0]})

 # 09 Multiplicity spectrum cyclic shift, exact nonnegative integer counts.
 f,a=plot();f.subplots_adjust(left=.11,right=.96,bottom=.2,top=.92)
 counts=[2,1,0];rotations=[[counts[(i-j)%3]for i in range(3)]for j in range(3)]
 for j,row in enumerate(rotations):a.bar(np.arange(3)+(j-1)*.24,row,width=.22,label=f'twist j={j}',color=[TEAL,GOLD,GRAY][j])
 a.set(xticks=range(3),xticklabels=['label 0','label 1','label 2'],ylim=(0,3.05),yticks=[0,1,2],ylabel='Exact multiplicity');a.grid(axis='y',alpha=.18);a.legend(loc='upper center',ncol=3,fontsize=14,frameon=False)
 a.text(1,2.52,'zʲ(2 + z) in Z[z]/(z³ − 1)',ha='center',fontsize=17)
 save(f,'09_spectrum','exact stable multiplicity-spectrum rotations, integer coefficients',{'p':3,'base':counts,'rotations':rotations,'rotation_invariant_regular':[1,1,1]})

 # 11 Direct-sum histogram forgets starting label.
 packets=[[(j+k)%3 for k in range(3)]for j in range(3)];assert all(sorted(x)==[0,1,2]for x in packets)
 f,a=canvas();title(a,'Σ over all twists: one copy of every quotient label')
 for j,row in enumerate(packets):
  y=4.9-1.35*j;a.text(.2,y,f'origin {j}',fontsize=17,va='center')
  for k,v in enumerate(row):card(a,2.3+2.35*k,y-.37,1.65,.74,'ζ'+['⁰','¹','²'][v],size=21,color=[PALE,'#EFE1CB','#DFE5ED'][v])
 a.text(5,.72,'Each row has the same multiset {1, ζ, ζ²}',ha='center',fontsize=18,color=TEAL)
 save(f,'11_induction','exact finite one-dimensional quotient-character direct-sum model',{'p':3,'origin_packets':packets,'total_multiplicities':[1,1,1]})

 # 12 Quotient-prime collapse and a separating coefficient place above7.
 z=(0,1);roots=[(1,0),(1,0),z]
 rows=[elementary([zmul(zpow(z,j),r)for r in roots])for j in range(3)]
 reductions={str(p):[[(u+v*zvalue)%p for u,v in row]for row in rows]for p,zvalue in [(3,1),(7,2)]}
 assert reductions['3']==[[0,0,1]]*3 and reductions['7']==[[4,5,2],[1,6,2],[2,3,2]]
 f,a=canvas();title(a,'Reduction of the same three rank 3 polynomials')
 for xx,h in [(1,'j'),(3.75,'(e₁, e₂, e₃) mod 3'),(7.8,'(e₁, e₂, e₃) mod 7')]:a.text(xx,5.6,h,ha='center',fontsize=16)
 for j in range(3):
  y=4.5-1.3*j;card(a,.45,y-.34,1.1,.7,str(j),size=21)
  card(a,2.1,y-.34,3.4,.7,str(tuple(reductions['3'][j])),size=20,color='#EFE1CB')
  card(a,6.1,y-.34,3.4,.7,str(tuple(reductions['7'][j])),size=20)
 a.text(3.75,.45,'ζ ↦ 1\nAll labels collapse',ha='center',fontsize=18,color=GOLD)
 a.text(7.8,.45,'ζ ↦ 2\nLabels separate',ha='center',fontsize=18,color=TEAL)
 save(f,'12_collapse','exact cyclotomic reduction at chosen places above3 and7',{'reduced_elementary_coefficients':reductions,'cube_roots_mod3':[1],'cube_roots_mod7':[1,2,4]})

 # 13 Two integral polynomials, all declared reductions exact.
 polynomial_vectors=[[1,-2,1],[1,2,1]];primes=[2,3,5,7]
 reduced={str(p):[[x%p for x in row]for row in polynomial_vectors]for p in primes}
 assert reduced['2'][0]==reduced['2'][1]
 assert all(reduced[str(p)][0]!=reduced[str(p)][1]for p in primes[1:])
 f,a=canvas();title(a,'P = (T − 1)²   and   Q = (T + 1)²')
 card(a,.6,4.65,3.9,1.1,'P coefficients:\n(1, −2, 1)',size=18)
 card(a,5.5,4.65,3.9,1.1,'Q coefficients:\n(1, 2, 1)',size=18)
 a.text(5,3.9,'Nonzero middle coefficient difference: 4',ha='center',fontsize=18)
 for i,p in enumerate(primes):
  x=.2+i*2.5;card(a,x,1.3,2.2,1.8,f'mod {p}\nP: {reduced[str(p)][0][1]}\nQ: {reduced[str(p)][1][1]}',size=18,color='#EFE1CB'if p==2 else PALE)
  a.text(x+1.1,.65,'collapse'if p==2 else 'separate',ha='center',fontsize=16,color=GOLD if p==2 else TEAL)
 save(f,'13_separation','exact integer polynomial alphabet reduced at2,3,5,7',{'polynomials_high_to_low':polynomial_vectors,'primes':primes,'reduced_vectors':reduced,'coefficient_difference':4})

 # 15 Counterexample to the pointwise-alphabet implication.
 I=[[1,0],[0,1]];A=[[2,0],[0,4]];A2=matmul(A,A,7)
 assert A2==[[4,0],[0,2]] and A2!=I and matmul(A2,A,7)==I
 f,a=canvas();title(a,'A polynomial assignment on C₂ that is not a homomorphism')
 card(a,.4,4.6,3.3,1.0,'Group relation\ng² = e',size=21)
 card(a,5.6,4.6,3.9,1.0,'Assigned over F₇\nf(g) = diag(2, 4)',size=18)
 arrow(a,(3.9,5.1),(5.4,5.1),GOLD,True)
 card(a,.4,2.2,3.3,1.1,'f(e) = I\nEigenvalues in μ₃',size=18)
 card(a,5.6,2.2,3.9,1.1,'f(g)² = diag(4, 2)\nDifferent from I',color='#EEDCDC',size=20)
 arrow(a,(7.55,4.45),(7.55,3.5),RED)
 a.text(5,.75,'Finite local spectra do not enforce g² = e',ha='center',fontsize=18,color=RED)
 save(f,'15_multiplication','exact finite C2 polynomial assignment counterexample over F7; not automorphic data',{'domain_group':'C2','assigned_identity':I,'assigned_generator':A,'generator_square':A2,'homomorphism':False,'assigned_eigenvalues_in_mu3':True})

 # 16 Semisimple l-adic rigidity and exact unipotent scope control.
 f,a=canvas();title(a,'Finite traces + semisimplicity: a rigidity implication')
 card(a,.2,4.675,3.0,1.35,'Existing l adic\nsemisimple\nrealization',size=17)
 card(a,3.7,4.85,2.6,1.0,'Finite trace\nalphabet',size=17)
 card(a,6.9,4.85,2.9,1.0,'Finite image\nTheorem output',size=17)
 arrow(a,(3.3,5.35),(3.55,5.35),TEAL);arrow(a,(6.4,5.35),(6.75,5.35),TEAL)
 card(a,1.3,2.9,7.4,.95,'Reductive connected monodromy\nhas trivial torus weights',size=17)
 arrow(a,(5,4.7),(5,4.03),TEAL)
 card(a,.45,.75,9.1,1.25,'Nonsemisimple control on Zℓ: t ↦ [[1, t], [0, 1]]\nTrace is always 2. The image is infinite.',color='#EEDCDC',size=17)
 save(f,'16_monodromy','conditional on existing semisimple l-adic realization; nonsemisimple profinite-group control',{'unipotent_trace':2,'unipotent_domain':'additive Z_l','unipotent_infinite_image':True,'semisimplicity_required':True})

 # 17 The cyclic norm and coboundary maps on row-major matrix units.
 T=[1,2,2,1];D=[(x-1)%3 for x in T];norms={q:[sum(pow(t,i,3)for i in range(q))%3 for t in T]for q in [2,6]}
 dims={q:sum(v==0 for v in norms[q])-sum(v!=0 for v in D)for q in norms}
 assert norms[2]==[2,0,0,2] and norms[6]==[0,0,0,0] and dims=={2:0,6:2}
 f,a=canvas();title(a,'Conjugation by diag(1, −1) on M₂(F₃)')
 headers=['coordinate','T − I','N for C₂','N for C₆'];xs=[1.2,3.5,5.9,8.3]
 for x,h in zip(xs,headers):a.text(x,5.7,h,ha='center',fontsize=16)
 for i,name in enumerate(['E₁₁','E₁₂','E₂₁','E₂₂']):
  y=4.9-i*.8;a.text(xs[0],y,name,ha='center',fontsize=18)
  for j,vals in enumerate([D,norms[2],norms[6]],1):card(a,xs[j]-.78,y-.28,1.56,.57,str(vals[i]),size=19,color=PALE if vals[i]else '#EFE1CB')
 a.text(3.1,.85,'C₂: dim ker N = 2\ndim H¹ = 0',ha='center',fontsize=18,color=TEAL)
 a.text(7.4,.85,'C₆: dim ker N = 4\ndim H¹ = 2',ha='center',fontsize=18,color=GOLD)
 save(f,'17_h1','exact finite cyclic cohomology operators overF3, fullmatrixmodule',{'T_diagonal':T,'T_minus_I_diagonal':D,'norm_diagonals':norms,'H1_dimensions':dims,'coboundary_dimension':2})

 # 18 Compatible target versus image, and an actual square-zero correction.
 errors=list(product(range(3),repeat=2));correctable=[x for x in errors if x[1]==0]
 A=[[1,1],[0,1]];corrected=[[3,1],[0,1]];I=[[1,0],[0,1]]
 assert matmul(A,A,4)==[[1,2],[0,1]] and matmul(corrected,corrected,4)==I
 f,a=canvas();title(a,'Compatibility does not replace the correction image')
 a.text(2.25,5.72,'Model over F₃: B = 0',ha='center',fontsize=17)
 for x,y in errors:a.scatter([.9+1.1*x],[2.35+1.1*y],s=145,color=TEAL if y==0 else RED)
 a.text(2.25,1.25,'All 9 errors satisfy Be = 0\nOnly 3 lie in im J = {(a, 0)}',ha='center',fontsize=16)
 card(a,5.15,3.925,4.5,1.4,'Lift over Z/4\nA = [[1, 1], [0, 1]]\nA² − I = 2E₁₂',size=17)
 card(a,5.15,1.525,4.5,1.4,'Corrected A + 2 diag(1, 0)\n[[3, 1], [0, 1]]\nIts square is I modulo 4',size=17)
 arrow(a,(7.4,3.85),(7.4,3.02),TEAL)
 save(f,'18_h2','left exact linear correction modelF3; right genuine square-zero ring liftZ4',{'compatible_errors':errors,'correctable_errors':correctable,'square_zero_lift':A,'corrected_lift':corrected,'lift_square':matmul(A,A,4),'corrected_square':I})

 # 19 Moving syzygy and an augmented-system negative control.
 assert (-2*2+4)%8==0 and (0*2+4)%8!=0
 original_roots=[x for x in range(4)if(x*x+1)%4==0];augmented=[(x,y)for x in range(4)for y in range(4)if(x*x+1+y)%4==0]
 assert original_roots==[] and (1,2)in augmented
 f,a=canvas();title(a,'Follow the moving relation and keep the original target')
 card(a,.25,4.3,4.45,1.45,'F(2) = (2, 4) mod 8\nMoving row: (−2, 1)\n(−2, 1) · (2, 4) = 0',size=18)
 card(a,5.3,4.3,4.45,1.45,'Leading layer mod 2\nF(2)/2 = (1, 2) ↦ (1, 0)\nResidual Jacobian image',size=16)
 arrow(a,(4.85,5.02),(5.12,5.02),TEAL)
 card(a,.25,1.25,4.45,1.45,'Original: x² + 1 = 0 mod 4\nSquares are 0 or 1\nNo root',color='#EEDCDC',size=16)
 card(a,5.3,1.25,4.45,1.45,'Augmented equation\nx² + 1 + y = 0 mod 4\n(1, 2) works, but y ≠ 0',color='#EFE1CB',size=17)
 save(f,'19_syzygy','exact movingrelationmod8 plus original/augmentedsystemsmod4 negativecontrol',{'F_at_2_mod8':[2,4],'moving_row':[-2,1],'frozen_row':[0,1],'leading_layer_mod2':[1,0],'original_roots_mod4':original_roots,'augmented_roots_mod4':augmented})

 # 20 Exact rational Newton iterates, 5-adic valuation.
 def vp(n,p):
  assert n!=0
  v=0
  while n%p==0:n//=p;v+=1
  return v
 xs=[Fraction(1)];errors=[xs[0]*xs[0]-6]
 for _ in range(4):
  prev=xs[-1];nxt=prev-(prev*prev-6)/(2*prev)
  assert nxt*nxt-6==(prev*prev-6)**2/(4*prev*prev)
  assert nxt.denominator%5!=0 and nxt.numerator%5!=0
  xs.append(nxt);errors.append(nxt*nxt-6)
 valuations=[vp(e.numerator,5)-vp(e.denominator,5)for e in errors];assert valuations==[1,2,4,8,16]
 f,a=plot();a.bar(range(5),valuations,width=.55,color=TEAL)
 for i,v in enumerate(valuations):a.text(i,v+.42,str(v),ha='center',fontsize=18)
 a.set(xticks=range(5),xticklabels=['x₀','x₁','x₂','x₃','x₄'],ylabel='ν₅(xᵣ² − 6)',ylim=(0,20),yticks=[0,4,8,12,16],xlabel='Exact Newton iterate');a.grid(axis='y',alpha=.15)
 a.text(.05,.92,'x₀ = 1\nx₁ = 7/2\nx₂ = 73/28\nx₃ = 10033/4088',transform=a.transAxes,fontsize=15,va='top')
 save(f,'20_hensel_scalar','exact rational scalar Newton iterates with5-adic unitdenominators',{'p':5,'target':6,'iterates':[[x.numerator,x.denominator]for x in xs],'errors':[[e.numerator,e.denominator]for e in errors],'error_valuations':valuations,'steps':4})

 # 21 Exact 4x4 inverse certificate and local target tests.
 A=[[1,1],[0,1]];D=[[2,0,1,0],[1,2,0,1],[0,0,2,0],[0,0,1,2]]
 B=[[2,0,-1,0],[-1,2,1,-1],[0,0,2,0],[0,0,-1,2]]
 fourI=[[4 if i==j else 0 for j in range(4)]for i in range(4)]
 assert matmul(B,D)==matmul(D,B)==fourI
 F=[[1,1],[8,1]];U=matmul(F,F);assert U==[[9,2],[16,9]]
 A2=matmul(A,A);delta=[U[i][j]-A2[i][j]for i in range(2)for j in range(2)]
 good=mv(B,delta);bad=mv(B,[0,8,0,0]);assert good==[0,0,32,0] and bad==[0,16,0,0]
 def matrix_grid(a,x,y,mat,name):
  a.text(x+1.6,y+2.55,name,ha='center',fontsize=20)
  for i,row in enumerate(mat):
   for j,v in enumerate(row):card(a,x+.8*j,y+.58*(3-i),.72,.5,str(v),size=17,color='#EFE1CB'if v else PALE)
 f,a=canvas();title(a,'Ordered derivative D(X) = AX + XA,   Q = B/4')
 matrix_grid(a,.65,2.85,D,'D');matrix_grid(a,6.1,2.85,B,'B')
 a.text(5,2.18,'BD = DB = 4I',ha='center',fontsize=21,color=TEAL)
 card(a,.3,.32,4.35,1.3,'Passing: Bδ = (0, 0, 32, 0)\nAll coordinates\ndivisible by 32',size=16)
 card(a,5.35,.42,4.35,1.12,'Failing: Bδ = (0, 16, 0, 0)\nNot divisible by 32',color='#EEDCDC',size=16)
 save(f,'21_matrix_hensel','exact integer inversecertificate and finite2-adic matrixcriterion p2d2s2m3',{'A':A,'D':D,'B':B,'BD':fourI,'p':2,'d':2,'s':2,'m':3,'test_modulus':32,'root':F,'target':U,'delta':delta,'passing_B_delta':good,'failing_target':[[1,10],[0,1]],'failing_B_delta':bad})

 # 22 Singular contrast and inverse denominator scope.
 singular=[[1,0],[0,-1]];multipliers=[[2,0],[0,-2]]
 assert matmul(singular,[[0,1],[0,0]])==[[0,1],[0,0]]
 assert matmul([[0,1],[0,0]],singular)==[[0,-1],[0,0]]
 f,a=canvas();title(a,'Square derivatives: singular modulo 2 or over Q₂?')
 card(a,.3,4.3,4.35,1.4,'Unipotent center\nA = [[1, 1], [0, 1]]\nD is invertible over Q₂',size=17)
 card(a,5.35,4.3,4.35,1.4,'Diagonal center\nA = diag(1, −1)\nD is singular over Q₂',color='#EEDCDC',size=17)
 card(a,.3,1.7,4.35,1.7,'Scalar degree valuation: 1\nInverse denominator\nexponent: 2\nUse m > s = 2',size=16)
 for i,row in enumerate(multipliers):
  for j,v in enumerate(row):card(a,6.0+1.3*j,2.45-.8*i,1.1,.65,str(v),size=21,color='#EEDCDC'if v==0 else PALE)
 a.text(7.45,1.14,'D(Eᵢⱼ) = shown scalar × Eᵢⱼ',ha='center',fontsize=15)
 a.text(5,.5,'An invertible matrix center can have a singular power derivative.',ha='center',fontsize=16,color=RED)
 save(f,'22_singular','exact squaremap derivative contrast overQ2, no inverseatgenuinelysingularcenter',{'unipotent_inverse_exponent':2,'scalar_degree_valuation':1,'singular_center':singular,'singular_derivative_on_matrix_units':multipliers,'singular_rank':2})

 # 24 Open application gates, all dashed links are unproved application input.
 f,a=canvas();title(a,'Open arithmetic inputs and proved generic tools')
 card(a,.2,4.55,2.8,1.35,'Finite Satake\nautomorphic\ndescent',size=16)
 card(a,3.85,4.55,2.8,1.35,'Actual residual\ncarrier or l adic\nrealization',color='#EFE1CB',size=16)
 card(a,7.5,4.4,2.2,1.5,'Weak\nattachment\nLocal checks\nremain',size=14)
 arrow(a,(3.18,5.28),(3.66,5.28),GOLD,True);arrow(a,(6.82,5.28),(7.32,5.28),TEAL)
 card(a,.2,1.6,2.8,1.4,'Actual arithmetic\ndeformation\nproblem',color='#EFE1CB',size=16)
 card(a,3.85,1.6,2.8,1.4,'Correct\ncomparison and\nimage exactness',color='#EFE1CB',size=16)
 card(a,7.5,1.6,2.2,1.4,'Controlled\nlocal lifting\ntheorems',size=16)
 arrow(a,(3.18,2.3),(3.66,2.3),GOLD,True);arrow(a,(6.82,2.3),(7.32,2.3),TEAL)
 arrow(a,(8.6,3.12),(8.6,4.27),GOLD,True)
 a.text(5,.7,'Dashed arrows require arithmetic application theorems.',ha='center',fontsize=17,color=GOLD)
 save(f,'24_open_gate','researchroute schematic; actualrealizationandcomparisoninputs remain open')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--paper-only',action='store_true');parser.add_argument('--result-dir',default=None);args=parser.parse_args()
 start=datetime.now(timezone.utc).isoformat();t0=time.perf_counter();paper_figures()
 if not args.paper_only:other_figures()
 (ROOT/'data.json').write_text(json.dumps(DATA,indent=2)+'\n')
 (ROOT/'FIGURE_LAYOUT_CHECK.json').write_text(json.dumps(LAYOUT,indent=2)+'\n')
 if not args.paper_only:assert len(LAYOUT)==24
 if CARD_FAILURES:
  print(json.dumps({'card_text_overflows':CARD_FAILURES},indent=2));raise AssertionError('Card text bounds failed. See exact diagnostics above.')
 report={'status':'checkpoint'if args.paper_only else 'passed','figure_count':len(LAYOUT),'started_at':start,'runtime_seconds':time.perf_counter()-t0,'domain':'exact finite examples and explicit schematic diagrams','non_claims':['Strong Artin is not proved','No automorphic carrier is constructed','No new Lean replay is claimed'],'software':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},'figure_keys':[x['figure']for x in LAYOUT]}
 (ROOT/'COMPUTATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 if args.result_dir:
  d=ROOT/args.result_dir;d.mkdir(parents=True,exist_ok=True)
  for name in ['data.json','FIGURE_LAYOUT_CHECK.json','COMPUTATION_REPORT.json']:shutil.copy2(ROOT/name,d/name)
  asset_dir=d/'figures';asset_dir.mkdir(exist_ok=True)
  hashes={}
  for item in LAYOUT:
   for suffix in ['.pdf','.png']:
    src=OUT/(item['figure']+suffix);shutil.copy2(src,asset_dir/src.name);hashes['figures/'+src.name]=hashlib.sha256(src.read_bytes()).hexdigest()
  report['scientific_output_hashes']=hashes
  (d/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report))

if __name__=='__main__':main()
