"""Exact data and deterministic vector figures for the ABC visual atlas.

Run python3 abc_set/visual/figures.py --paper-only for five early paper assets.
Run python3 abc_set/visual/figures.py --range 1 6 for a bounded export batch.
Run without arguments for all 24 figures. Integer and Fraction data are exact.
Logs, plotted coordinates and display decimals are approximate rendering only.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from math import prod, factorial, comb, gcd, log, lcm
import argparse, hashlib, json, platform, time, shutil, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'; OUT.mkdir(parents=True,exist_ok=True)
SHARED=ROOT.parent/'shared'/'figures'; SHARED.mkdir(parents=True,exist_ok=True)
INK='#243138'; TEAL='#21676B'; COPPER='#A45C36'; PALE='#E9F0EF'; GRAY='#627078'; RED='#A55050'; GOLD='#B67E35'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.labelsize':14,
 'xtick.labelsize':12,'ytick.labelsize':12,'text.color':INK,'axes.labelcolor':INK,
 'pdf.fonttype':42,'savefig.facecolor':'white','mathtext.fontset':'dejavusans'})
DATA={'conventions':{'triple':'positive a+b=c, gcd(a,b)=1',
 'radical':'product of distinct prime divisors, rad(1)=1',
 'defect':'Q=abc/R; correct balanced defect Q/(ab)=c/R',
 'exact_arithmetic':'Python int and fractions.Fraction',
 'display':'logs, chart coordinates, and display decimals use floating point only',
 'scope':'finite examples and diagrams do not prove ABC or construct a global witness'},'figures':{}}
LAYOUT=[]

def factor(n):
 out={}; p=2
 while p*p<=n:
  while n%p==0:out[p]=out.get(p,0)+1;n//=p
  p+=1
 if n>1:out[n]=out.get(n,0)+1
 return out
def rad(n):return prod(factor(n))
def triple(a,b):
 c=a+b;assert gcd(a,b)==1
 R=rad(a*b*c);Q=F(a*b*c,R)
 assert Q.denominator==1 and Q/F(a*b)==F(c,R)
 return {'a':a,'b':b,'c':c,'R':R,'Q':int(Q),'balanced':str(F(c,R)),
 'quality_approx':log(c)/log(R),'factors':[factor(v)for v in(a,b,c)]}
def hankel_coeff(r,n,K=None):
 ans=F(0)
 for kk in combinations(range(1,min(n,K or n)+1),r):
  if sum(kk)!=n:continue
  ans+=F(prod((b-a)**2 for a,b in combinations(kk,2)),prod(k**(2*r-1) for k in kk))
 return ans
def lead(r):return prod(F(1,k**(2*k-1))for k in range(1,r+1))
def vp(n,p):
 assert n!=0
 n=abs(n);v=0
 while n%p==0:v+=1;n//=p
 return v
def depleted(p,r):
 uu=[];k=1
 while len(uu)<r:
  if k%p:uu.append(k)
  k+=1
 E=sum(vp(b-a,p)for a,b in combinations(uu,2))
 return uu,sum(uu),E
def canvas():
 f,a=plt.subplots(figsize=(9,5.7));f.subplots_adjust(left=.04,right=.96,bottom=.07,top=.95)
 a.set(xlim=(0,10),ylim=(0,7));a.axis('off');return f,a
def chart():
 f,a=plt.subplots(figsize=(9,5.7));f.subplots_adjust(left=.12,right=.96,bottom=.19,top=.9)
 a.spines[['top','right']].set_visible(False);return f,a
def title(a,s):a.text(5,6.63,s,ha='center',va='center',fontsize=17,color=TEAL)
def card(a,x,y,w,h,s,color=PALE,size=16,edge=None):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.06,rounding_size=.1',facecolor=color,edgecolor=edge or color,lw=1.1))
 t=a.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=size)
 if not hasattr(a,'_cards'):a._cards=[]
 a._cards.append((t,(x,y,w,h)))
 return t
def arrow(a,p,q,color=GRAY,dashed=False):
 a.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=15,color=color,lw=1.6,linestyle='--'if dashed else '-',connectionstyle='arc3,rad=0'))
def save(f,key,domain,values=None):
 f.canvas.draw();renderer=f.canvas.get_renderer();texts=[];cards=[]
 for ax in f.axes:
  for t,(x,y,w,h)in getattr(ax,'_cards',[]):
   tb=t.get_window_extent(renderer);p0=ax.transData.transform((x+.025,y+.025));p1=ax.transData.transform((x+w-.025,y+h-.025))
   good=tb.x0>=p0[0]-1 and tb.x1<=p1[0]+1 and tb.y0>=p0[1]-1 and tb.y1<=p1[1]+1
   cards.append({'text':t.get_text(),'text_bounds_pixels':list(tb.bounds),'inner_bounds_pixels':[p0.tolist(),p1.tolist()],'passed':bool(good)})
   assert good,(key,'card containment',t.get_text(),tb.bounds,p0,p1)
 ignored=set()
 for ax in f.axes:
  for axis in[ax.xaxis,ax.yaxis]:
   lo,hi=sorted(axis.get_view_interval())
   for tick in axis.get_major_ticks()+axis.get_minor_ticks():
    if not lo<=tick.get_loc()<=hi:ignored.update([id(tick.label1),id(tick.label2)])
 for t in f.findobj(matplotlib.text.Text):
  if not t.get_visible()or not t.get_text()or id(t)in ignored:continue
  b=t.get_window_extent(renderer);good=b.x0>=-1 and b.y0>=-1 and b.x1<=f.bbox.width+1 and b.y1<=f.bbox.height+1
  assert good,(key,'canvas containment',t.get_text(),b.bounds)
  texts.append({'text':t.get_text(),'bounds_pixels':list(b.bounds)})
 f.savefig(OUT/(key+'.pdf'),metadata={'CreationDate':None,'ModDate':None,'Creator':'Operation Komorebi exact visual atlas'});f.savefig(OUT/(key+'.png'),dpi=160);plt.close(f)
 DATA['figures'][key]={'domain':domain,'values':values or{}}
 LAYOUT.append({'figure':key,'canvas_inches':[9,5.7],'text_bounds_passed':True,'card_text_bounds_passed':True,'text_bounds':texts,'card_text_bounds':cards})

def fig01():
 f,a=canvas();title(a,'The radical counts each active prime once')
 labels=[('8',2,3),('9',3,2),('72',None,None)]
 for row,(name,p,e)in enumerate(labels[:2]):
  y=4.85-row*1.4;a.text(.3,y,name,fontsize=24,va='center')
  for j in range(e):card(a,1.65+1.4*j,y-.37,1.1,.75,str(p),size=22,color='#BDDBD7'if j==0 else PALE)
  a.text(6.6,y,f'power = {p}^{e}\nradical = {p}',fontsize=18,va='center')
 card(a,.6,.65,8.8,1.1,'72 = 2³ · 3²     →     rad(72) = 2 · 3 = 6',size=20)
 save(f,'01_radical','exact integer factorization',{'n':72,'factors':factor(72),'radical':rad(72)})
def fig03():
 t=triple(2,109*3**10);assert t['c']==23**5 and t['R']==15042
 f,a=canvas();title(a,'2 + 109 · 3¹⁰ = 23⁵')
 for x,n,s in[(.2,'a = 2','one factor 2'),(3.5,'b = 6,436,341','3¹⁰ · 109'),(6.8,'c = 6,436,343','five factors 23')]:
  card(a,x,4.1,3,1.1,n+'\n'+s,size=16)
 arrow(a,(2.15,3.88),(4.4,2.95),TEAL);arrow(a,(7.85,3.88),(5.6,2.95),TEAL)
 card(a,2.3,1.65,5.4,1.2,'R = 2 · 3 · 109 · 23 = 15,042\nquality q = log(c) / log(R) ≈ 1.629912',size=16)
 a.text(5,.6,'A large quality example. A finite exception is allowed by ABC.',ha='center',fontsize=15,color=COPPER)
 save(f,'03_high_quality','exact primitive triple; quality decimal is approximate',t)
def fig09():
 t=triple(1,8);assert t['Q']==12
 f,a=canvas();title(a,'Keep the input factor ab in the normalization')
 card(a,.35,4.1,4.2,1.25,'Q = abc/R = 72/6 = 12\nRepeated depth in all sectors',size=16)
 card(a,5.45,4.1,4.2,1.25,'ab = 8\nInput scale',size=19)
 arrow(a,(2.45,3.9),(4.2,2.8));arrow(a,(7.55,3.9),(5.8,2.8))
 card(a,2.05,1.45,5.9,1.3,'Q/(ab) = c/R = 9/6 = 3/2\nABC controls this balanced ratio',size=19)
 a.text(5,.5,'Q alone cannot be uniformly subpolynomial in R.',ha='center',fontsize=17,color=RED)
 save(f,'09_balanced_defect','exact normalization for (1,8,9)',t)
def fig16():
 rows=[]
 for r in range(1,6):
  s=r*(r+1)//2;co=lead(r);assert hankel_coeff(r,s)==co
  rows.append({'r':r,'s_r':s,'leading':str(co)})
 f,a=canvas();title(a,'Cauchy–Binet gives a unique first nonzero term')
 for x,h in[(.9,'rank r'),(3.6,'first indices'),(6.3,'contact sᵣ'),(8.6,'coefficient')]:a.text(x,5.85,h,ha='center',fontsize=15)
 for i,row in enumerate(rows):
  y=4.9-i*.9;a.text(.9,y,str(row['r']),ha='center',fontsize=20)
  a.text(3.6,y,'{'+', '.join(str(k)for k in range(1,row['r']+1))+'}',ha='center',fontsize=17)
  card(a,5.5,y-.3,1.6,.6,str(row['s_r']),size=20)
  a.text(8.6,y,row['leading'],ha='center',fontsize=15)
 a.text(5,.25,'sᵣ = 1 + 2 + ⋯ + r = r(r+1)/2',ha='center',fontsize=19,color=TEAL)
 save(f,'16_contact_order','exact rational leading coefficients of H_r, ranks 1 through 5',{'rows':rows})
def fig24():
 f,a=canvas();title(a,'The corrected global bridge is an interface specification')
 card(a,.25,4.45,4.25,1.2,'Nonzero integer W\nQˢ divides W',color='#EFE1CB',size=20)
 card(a,5.5,4.45,4.25,1.2,'Global height bound\n|W| ≤ C (ab)ˢ Rᴱ (log 3c)ᴬ',color='#EFE1CB',size=17)
 arrow(a,(2.4,4.2),(4.35,3.23),GOLD,True);arrow(a,(7.6,4.2),(5.65,3.23),GOLD,True)
 card(a,2.1,2.0,5.8,1.1,'(c/R)ˢ ≤ C Rᴱ (log 3c)ᴬ\nThe factor ab cancels exactly',size=18)
 arrow(a,(5,1.82),(5,1.18),TEAL)
 a.text(5,.72,'E/s → 0, with constants independent of the triple → ABC',ha='center',fontsize=16,color=TEAL)
 save(f,'24_global_bridge','conditional implication; witness, divisibility and global bound are unproved',{'normalization':'Q/(ab)=c/R','open_hypotheses':['nonzero integer W','Q^s divides W','all-place global height bound','E/s tends to zero']})

def fig02():
 t=triple(1,8);f,a=canvas();title(a,'1 + 8 = 9: small enough to check by hand')
 for x,name,facts in[(.3,'a = 1','no prime support'),(3.5,'b = 8','2³'),(6.7,'c = 9','3²')]:
  card(a,x,4.35,3,1.05,name+'\n'+facts,size=20)
 card(a,.6,2.3,8.8,1.05,'R = 2 · 3 = 6     c/R = 3/2     Q = 12',size=22)
 a.text(5,1.2,'q = log 9 / log 6 ≈ 1.226294',ha='center',fontsize=23,color=TEAL)
 a.text(5,.5,'Primitive means gcd(1,8) = 1. The prime sectors are disjoint.',ha='center',fontsize=15)
 save(f,'02_small_triple','exact triple; quality decimal approximate',t)
def fig04():
 p=ROOT.parent/'evidence/computation/controls_run/abc_census_high_quality.csv'
 rows=[]
 for row in csv.DictReader(p.open()):
  d={k:int(row[k])for k in['a','b','c','R']};assert d['a']+d['b']==d['c'] and gcd(d['a'],d['b'])==1 and d['c']>d['R']
  assert rad(d['a'])*rad(d['b'])*rad(d['c'])==d['R'];rows.append(d)
 assert len(rows)==121 and max(d['c']for d in rows)<=10000
 f,a=chart();a.scatter([log(d['R'])for d in rows],[log(d['c'])for d in rows],s=25,color=TEAL,alpha=.72)
 a.plot([1.3,9.2],[1.3,9.2],color=GRAY,lw=1.3,label='c = R reference')
 high=max(rows,key=lambda d:log(d['c'])/log(d['R']));a.scatter([log(high['R'])],[log(high['c'])],s=65,color=COPPER)
 a.annotate('1 + 4,374 = 4,375\nq ≈ 1.567887',xy=(log(high['R']),log(high['c'])),xytext=(2.1,8.7),fontsize=13,arrowprops={'arrowstyle':'-','color':COPPER})
 a.set(xlabel='log R  (display coordinates)',ylabel='log c  (display coordinates)',xlim=(1.3,9.3),ylim=(1.3,9.6))
 a.set_title('121 triples with c > R in the complete c ≤ 10,000 census',fontsize=15,color=TEAL,pad=12);a.legend(loc='lower right',fontsize=12)
 save(f,'04_bounded_census','exact complete integer census; chart logs approximate',{'source_csv_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'primitive_triples':15198743,'c_max':10000,'a_le_b':True,'high_quality_triples':rows,'plotted_count':121})
def fig05():
 rows=[]
 for n in range(1,7):
  c=3**(2**n);b=c-1;assert vp(b,2)==n+2
  rows.append({'n':n,'b':b,'c':c,'v2_b':n+2,'lower_bound_c_over_R':str(F(2**(n+1)*c,3*b))})
 f,a=chart();a.plot([d['n']for d in rows],[float(F(d['lower_bound_c_over_R']))for d in rows],'o-',color=COPPER,lw=2)
 a.set(xlabel='n in (1, 3^(2^n) − 1, 3^(2^n))',ylabel='Proved lower bound for c/R',xticks=list(range(1,7)),ylim=(0,46))
 a.set_title('The bound grows: c/R > 2^(n+1)/3',fontsize=18,color=TEAL,pad=15)
 a.text(2.4,37,'No fixed K can give c ≤ K R\nfor every primitive triple.',fontsize=17,color=COPPER)
 save(f,'05_epsilon_zero','exact LTE family and rational lower bound; no large-integer factorization needed',{'rows':rows,'bound':'R <= 3b/2^(n+1)','unbounded':'c/R > 2^(n+1)/3'})
def fig06():
 f,a=canvas();title(a,'The quantifier order carries the conjecture')
 card(a,.2,4.3,3,1.2,'Choose ε > 0\nOnce',size=19)
 card(a,3.5,4.3,3,1.2,'Choose Kε\nDepends only on ε',size=18)
 card(a,6.8,4.3,3,1.2,'Every primitive triple\nUniformly',size=16)
 arrow(a,(3.3,4.9),(3.42,4.9),TEAL);arrow(a,(6.6,4.9),(6.72,4.9),TEAL)
 card(a,.5,1.7,4.2,1.25,'Fixed prime set S\nOnly finitely many triples',size=19)
 card(a,5.3,1.7,4.2,1.25,'All prime sets\nRadical-scale uniformity',color='#EFE1CB',size=19)
 a.text(5,.65,'The fixed-support conclusion is weaker than the uniform bound.',ha='center',fontsize=16,color=COPPER)
 save(f,'06_quantifiers','logical diagram; fixed-support finiteness follows from known unconditional radical bounds',{'abc_quantifiers':['forall epsilon>0','exists K_epsilon','forall primitive triples'],'fixed_support_is_not_uniform_abc':True})
def fig07():
 f,a=canvas();title(a,'Mason–Stothers sees repeated roots through a derivative')
 card(a,.4,4.5,9.2,1.0,'A = X³     B = 1 − X³     C = 1     A + B = C',size=23)
 card(a,.4,2.45,4.3,1.15,'A′B − AB′ = 3X²\nNonzero in characteristic 0',size=18)
 card(a,5.3,2.45,4.3,1.15,'rad(ABC): degree 4\nOne root at 0, three at X³ = 1',size=17)
 arrow(a,(2.5,4.25),(2.5,3.85),TEAL);arrow(a,(7.5,4.25),(7.5,3.85),TEAL)
 a.text(5,1.35,'max(deg A, deg B, deg C) = 3 ≤ 4 − 1',ha='center',fontsize=23,color=TEAL)
 a.text(5,.45,'The theorem needs the derivative and nonconstant hypotheses.',ha='center',fontsize=16)
 save(f,'07_mason','exact characteristic-zero polynomial example over C',{'A':'X^3','B':'1-X^3','C':'1','wronskian':'3X^2','radical_degree':4,'maximum_degree':3})
def fig08():
 f,a=canvas();title(a,'An integer derivation cannot supply the polynomial mechanism')
 card(a,.4,4.3,4.3,1.2,'Polynomials\nCharacteristic 0\nd/dX is nonzero',size=17)
 card(a,5.3,4.3,4.3,1.2,'Integers\nEvery derivation\nD: ℤ → ℤ is zero',size=16)
 a.text(2.55,3.35,'D(X³) = 3X²',ha='center',fontsize=24,color=TEAL)
 a.text(7.45,3.35,'D(1) = 0\nD(n) = nD(1) = 0',ha='center',fontsize=21,color=COPPER)
 card(a,1.1,1.1,7.8,1.2,'Integer ABC needs another global mechanism\nLocal divisibility still needs a height comparison',color='#EFE1CB',size=19)
 arrow(a,(2.55,2.7),(3.4,2.55),GRAY,True);arrow(a,(7.45,2.7),(6.6,2.55),GRAY,True)
 save(f,'08_integer_gap','algebraic fact about additive Leibniz derivations on Z, not an impossibility theorem for ABC',{'D_one':0,'D_n':'n*D(1)=0'})
def fig10():
 f,a=canvas();title(a,'Prime contact separates three disjoint sectors')
 for x,name,facts,mm in[(.25,'input a = 2',r'$R_a = 2$',r'$M_a = 1$'),(3.5,'input b = 109 · 3¹⁰',r'$R_b = 3\cdot109$',r'$M_b = 3^9$'),(6.75,'output c = 23⁵',r'$R_c = 23$',r'$M_c = 23^4$')]:
  card(a,x,4.15,3,1.6,name+'\n'+facts+'\n'+mm,size=15)
 card(a,1,1.7,8,1.2,r'Output target:  $M_c\leq K_\varepsilon R_a R_b R^\varepsilon$'+'\nExactly the same ABC inequality',size=21)
 arrow(a,(5,3.9),(5,3.1),TEAL)
 a.text(5,.55,'Repeated output depth must be compared with input prime support.',ha='center',fontsize=15)
 save(f,'10_prime_sectors','exact factorizations for (2,109*3^10,23^5)',triple(2,109*3**10))
def fig11():
 counts=[0]*13;assignments=[]
 for u in[-1,0,1]:
  for v in[-1,0,1]:
   h=(u+2*v)%13;counts[h]+=1;assignments.append([u,v,h])
 assert counts[1]==2 and counts[6]==0 and sum(counts)==9
 f,a=chart();colors=[TEAL]*13;colors[1]=COPPER;colors[6]=RED
 a.bar(range(13),counts,color=colors,width=.7);a.set(xlabel='Residue h modulo 13',ylabel='Exact ternary assignment count N(h)',xticks=list(range(13)),ylim=(0,2.7))
 a.set_title('Toy cyclic model: h = u + 2v,  u,v ∈ {−1,0,1}',fontsize=17,color=TEAL,pad=14)
 a.text(1.2,2.25,'N(1) = 2\nPositive control',fontsize=15,color=COPPER)
 a.text(6.2,1.2,'N(6) = 0\nZero control',fontsize=15,color=RED)
 save(f,'11_cyclic_controls','fully enumerated toy cyclic model, not an ABC arithmetic channel or a historical signed-filter replay',{'modulus':13,'steps':[1,2],'assignments':assignments,'counts':counts,'positive_target':1,'zero_target':6})
def fig12():
 f,a=canvas();title(a,'A short kernel vector cannot bound an arbitrary index')
 a.text(5,5.7,'ΛN = {(x,y) ∈ ℤ² : x − y ≡ 0 mod N}',ha='center',fontsize=22)
 for x,n in[(.4,3),(3.6,30),(6.8,3000)]:
  card(a,x,3.25,2.8,1.5,f'N = {n:,}\nindex = {n:,}\n(1,1) ∈ ΛN',size=20)
 card(a,.9,1.05,8.2,1.25,'The actual logarithmic rows need arithmetic rigidity\nA generic lattice estimate does not supply it',color='#EFE1CB',size=18)
 save(f,'12_arithmetic_gate','exact index-N congruence lattice family; abstract obstruction to a generic short-vector argument',{'Ns':[3,30,3000],'row':[1,-1],'kernel_vector':[1,1],'index':'N'})
def fig13():
 mm=list(range(4,25));naive=[F(1,m)for m in mm];canonical=[F(m-3,m)for m in mm]
 f,a=chart();a.plot(mm,list(map(float,naive)),color=TEAL,lw=2,label='Projective coefficient 1/M')
 a.plot(mm,list(map(float,canonical)),color=COPPER,lw=2,label='Canonical coefficient (M−3)/M')
 a.set(xlabel='Fermat exponent M',ylabel='Coefficient of log c in the height',ylim=(0,1),xlim=(4,24));a.set_title('The full Fermat curve restores geometric cost',fontsize=18,color=TEAL,pad=14);a.legend(fontsize=13,loc='center right')
 save(f,'13_fermat_cost','exact height coefficients; canonical comparison has its stated O(1) normalization term',{'M':mm,'projective_coefficients':list(map(str,naive)),'canonical_coefficients':list(map(str,canonical)),'line_bundle':'K_F = O_F(M-3)'})
def fig14():
 rows=[]
 for m in range(5):
  cc=[0,1]
  for j in range(1,m+1):
   nxt=[0]*(len(cc)+1)
   for i,c in enumerate(cc):nxt[i]-=c;nxt[i+1]+=j*c
   cc=nxt
  assert sum(map(abs,cc))==factorial(m+1) and cc[1]==(-1)**m
  rows.append({'m':m,'P_coefficients_ascending':cc,'contact':m+1,'leading':str(F((-1)**m,(m+1)**(m+2)))})
 f,a=canvas();title(a,'The jet filter has a real Taylor zero of order m+1')
 for x,h in[(.8,'m'),(3.5,'numerator coefficients'),(6.6,'first power'),(8.6,'leading coefficient')]:a.text(x,5.85,h,ha='center',fontsize=13)
 for i,d in enumerate(rows):
  y=4.9-i*.9;a.text(.8,y,str(d['m']),ha='center',fontsize=20)
  a.text(3.5,y,str(d['P_coefficients_ascending'][1:]),ha='center',fontsize=18)
  card(a,5.9,y-.3,1.4,.6,f't^{d["contact"]}',size=20)
  a.text(8.6,y,d['leading'],ha='center',fontsize=19)
 a.text(5,.2,'Normalized coefficient ℓ¹ norm = 1. Arithmetic period height is separate.',ha='center',fontsize=14,color=COPPER)
 save(f,'14_jet_series','exact polynomial jet-filter coefficients, m 0 through 4',{'rows':rows})
def fig15():
 f,a=canvas();title(a,'Rank 2 packages independent moment directions')
 card(a,.5,4.05,4.2,1.5,'Moment matrix\n[ Li₁(t)   Li₂(t) ]\n[ Li₂(t)   Li₃(t) ]',size=21)
 card(a,5.3,4.05,4.2,1.5,'H₂(t)\nLi₁(t) Li₃(t) − Li₂(t)²',size=21)
 arrow(a,(4.9,4.8),(5.12,4.8),TEAL)
 a.text(5,2.85,'Each pair 1 ≤ i < j contributes',ha='center',fontsize=18)
 a.text(5,1.9,'t^(i+j) · (j−i)² / (i³ j³)',ha='center',fontsize=27,color=TEAL)
 a.text(5,.7,'The first pair is {1,2}:  H₂(t) = t³/8 + ⋯',ha='center',fontsize=21)
 assert hankel_coeff(2,3)==F(1,8)
 save(f,'15_rank_two','exact formal determinant and Cauchy-Binet pair formula',{'rank':2,'first_indices':[1,2],'first_power':3,'first_coefficient':'1/8'})
def fig17():
 vals=[]
 for i,j in combinations(range(1,7),2):vals.append({'indices':[i,j],'term':str(F((j-i)**2,2**(i+j)*i**3*j**3))})
 total=sum(F(d['term'])for d in vals);assert total>0
 f,a=chart();a.bar(range(15),[float(F(d['term']))for d in vals],color=TEAL)
 a.set(xlabel='Pairs {i,j} from the first six moment nodes',ylabel='Exact positive term (decimal display)',xticks=range(15),xticklabels=[f'{d["indices"][0]},{d["indices"][1]}'for d in vals])
 a.tick_params(axis='x',labelsize=10);a.set_title('H₂,₆(1/2): every Cauchy–Binet contribution is positive',fontsize=16,color=TEAL,pad=15)
 a.text(5,.012,'Finite sum ≈ '+f'{float(total):.6f}'+'\nFull Hᵣ(t) > 0 for 0 < t < 1',fontsize=15,color=COPPER)
 save(f,'17_positive_moments','exact rational terms for the finite rank-2 determinant with K=6 at t=1/2; theorem for full positive t is separately proved',{'terms':vals,'finite_determinant':str(total),'r':2,'K':6,'t':'1/2'})
def fig18():
 f,a=canvas();title(a,'The universal series has exact contact at sufficiently large primes')
 for x,r,p in[(.35,2,7),(3.55,3,11),(6.75,4,13)]:
  s=r*(r+1)//2;assert p>3*r-1
  card(a,x,3.7,2.9,1.8,f'r = {r},  p = {p}\np > 3r − 1\nvₚ(Hᵣ(t)) = {s}e',size=20)
 card(a,.85,1.05,8.3,1.25,'vₚ(t) = e ≥ 1\nUnique initial coefficient is a p-adic unit',size=20)
 save(f,'18_good_primes','universal local theorem illustrated at three valid rank/prime pairs',{'examples':[{'r':r,'p':p,'contact':r*(r+1)//2}for r,p in[(2,7),(3,11),(4,13)]],'threshold':'p>3r-1'})
def fig19():
 m=3;p=2;ks=list(range(1,10));survive=[k for k in ks if k%p];assert 4 not in survive and 5 in survive
 f,a=canvas();title(a,'Depletion removes indices divisible by p')
 for k in ks:
  x=.2+(k-1)*1.07;col='#E5CACA'if k%2==0 else PALE
  card(a,x,4.55,.92,.75,str(k),size=22,color=col)
  if k%2==0:a.plot([x+.15,x+.77],[4.65,5.15],color=RED,lw=2)
 a.text(5,3.5,'m = 3: the first jet index 4 is removed at p = 2',ha='center',fontsize=18)
 card(a,.6,1.4,8.8,1.2,'The next surviving index is 5\nv₂(Φ₃,₂(t)) = 5e when v₂(t) = e ≥ 1',size=22)
 save(f,'19_depletion','exact jet p-depletion at m=3,p=2',{'m':m,'p':p,'original_contact':4,'depleted_contact':5,'first_surviving_coefficient':'-1/625','visible_surviving_indices':survive})
def fig20():
 rows=[]
 for p,r in[(2,4),(3,4),(5,4)]:
  uu,S,E=depleted(p,r);rows.append({'p':p,'r':r,'unit_indices':uu,'S':S,'E':E,'valuation_e1':S+2*E})
 assert [d['valuation_e1']for d in rows]==[32,16,10]
 f,a=canvas();title(a,'First unit indices minimize both index sum and residue energy')
 for x,h in[(.7,'p'),(3.2,'first 4 unit indices'),(6,'Sₚ,₄'),(7.5,'Eₚ,₄'),(9,'v for e=1')]:a.text(x,5.7,h,ha='center',fontsize=13)
 for i,d in enumerate(rows):
  y=4.55-i*1.3;a.text(.7,y,str(d['p']),ha='center',fontsize=24)
  a.text(3.2,y,str(d['unit_indices']),ha='center',fontsize=21)
  for x,k in[(6,'S'),(7.5,'E'),(9,'valuation_e1')]:card(a,x-.55,y-.38,1.1,.76,str(d[k]),size=24)
 a.text(5,.62,'vₚ(Hᵣ,ₚ(t)) = e Sₚ,ᵣ + 2 Eₚ,ᵣ',ha='center',fontsize=25,color=TEAL)
 save(f,'20_residue_energy','exact integer unit-index and Vandermonde valuation data, r=4',{'rows':rows})
def fig21():
 p=ROOT.parent/'evidence/computation/jet_replay/run/results.json';d=json.loads(p.read_text());budgets=d['raw_small_prime_budgets']
 row=next(x for x in budgets if x['rank']==2);assert prod(int(p)**e for p,e in row['C_p'].items())==3456
 # The proof's explicit safe correction is 2^7 * 3^3, not a minimality claim.
 f,a=chart();a.bar([2,3,5],[7,3,0],color=[COPPER,COPPER,PALE],width=.6)
 a.set(xlabel='Prime p',ylabel='Exponent C₂,ₚ in the safe denominator budget',xticks=[2,3,5],ylim=(0,8.7));a.set_title('B₂ = 2⁷ · 3³ = 3,456',fontsize=23,color=TEAL,pad=15)
 a.text(3.2,6.45,'vₚ(B₂ H₂(t)) ≥ 3e\nwhen vₚ(t) = e ≥ 1',fontsize=19,color=TEAL)
 a.text(3.7,2,'A local series correction\nNo global algebraic witness yet',fontsize=16,color=COPPER)
 save(f,'21_small_prime_budget','exact safe raw-series denominator correction at rank 2; no minimality or motivic denominator claim',{'rank':2,'C_p':{'2':7,'3':3},'B':3456,'source_result_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
def fig22():
 f,a=canvas();title(a,'Rational truncation can destroy the required output contact')
 card(a,.4,4.3,9.2,1.2,'H₂,₃(t) = t³(27 + 32t + t²)/216',size=25)
 arrow(a,(5,4.08),(5,3.45),TEAL)
 card(a,.4,2.05,9.2,1.1,'W(a,c) = a³(27c² + 32ac + a²)',size=25)
 a.text(5,.92,'p > 3,  p | c,  p ∤ a    →    W ≡ a⁵ ≠ 0 (mod p)',ha='center',fontsize=21,color=RED)
 assert[hankel_coeff(2,n,K=3)for n in[3,4,5]]==[F(1,8),F(4,27),F(1,216)]
 save(f,'22_truncation_loss','exact K=3 rank-2 truncation and congruence obstruction',{'r':2,'K':3,'coefficients':{'3':'1/8','4':'4/27','5':'1/216'},'scalar':'a^3(27c^2+32ac+a^2)','output_contact':'zero at p>3 dividing c'})
def fig23():
 f,a=canvas();title(a,'ABC status: distinguish proof claim, publication and later review')
 for x,y,w,h,txt,col in[(.3,4.1,4.35,1.35,'2021 / IUT published\nRIMS special issue\nA publication record',PALE),(5.35,4.1,4.35,1.35,'July 2026 / LANA report\nJudgment suspended\nComparison not reconstructed','#EFE1CB')]:card(a,x,y,w,h,txt,color=col,size=16)
 card(a,.8,1.15,8.4,1.65,'Local results and finite checks do not settle ABC\nGlobal witness and radical-scale bound remain open\nEach source must be read on its own terms',size=18)
 a.text(5,3.2,'These are different kinds of evidence.',ha='center',fontsize=21,color=COPPER)
 save(f,'23_evidence_status','source-based status diagram dated 8 October 2026; no full IUT proof audit or global consensus survey',{'IUT_publication':2021,'LANA_report_announcement':'2026-07-17','LANA_position':'suspend judgment whether IUT proves abc','unclear_step':'IUT III Theorem 3.11 to Corollary 3.12'})

FIGURES={1:fig01,2:fig02,3:fig03,4:fig04,5:fig05,6:fig06,7:fig07,8:fig08,9:fig09,10:fig10,11:fig11,12:fig12,13:fig13,14:fig14,15:fig15,16:fig16,17:fig17,18:fig18,19:fig19,20:fig20,21:fig21,22:fig22,23:fig23,24:fig24}
PAPER=[1,3,9,16,24]
def main():
 p=argparse.ArgumentParser();p.add_argument('--paper-only',action='store_true');p.add_argument('--range',nargs=2,type=int);p.add_argument('--result-dir');args=p.parse_args()
 selected=PAPER if args.paper_only else list(range(args.range[0],args.range[1]+1))if args.range else sorted(FIGURES)
 started=time.time()
 for n in selected:
  assert n in FIGURES,f'Figure {n} is not yet implemented'
  FIGURES[n]()
 for n in PAPER:
  if n not in selected:continue
  key=next(k for k in DATA['figures']if k.startswith(f'{n:02d}_'))
  shutil.copy2(OUT/(key+'.pdf'),SHARED/(key+'.pdf'))
 (ROOT/'data.json').write_text(json.dumps(DATA,indent=2)+'\n')
 (ROOT/'FIGURE_LAYOUT_CHECK.json').write_text(json.dumps({'all_passed':True,'figures':LAYOUT},indent=2)+'\n')
 report={'status':'bounded exact data verified',
  'command':['python3','abc_set/visual/figures.py']+(['--paper-only']if args.paper_only else ['--range',*map(str,args.range)]if args.range else[])+(['--result-dir',args.result_dir]if args.result_dir else[]),
  'python':platform.python_version(),'matplotlib':matplotlib.__version__,'runtime_seconds':time.time()-started,
  'exact_domain':'integers and rational fractions','exported_numbers':selected,'nonclaim':'not a proof of ABC or an arithmetic realization of local series',
  'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'output_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest()for x in OUT.iterdir()if x.suffix in['.pdf','.png']}}
 (ROOT/'COMPUTATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 if args.result_dir:
  d=ROOT/args.result_dir;d.mkdir(parents=True,exist_ok=True)
  for name in['data.json','FIGURE_LAYOUT_CHECK.json','COMPUTATION_REPORT.json']:shutil.copy2(ROOT/name,d/name)
  assets=d/'figures';assets.mkdir(exist_ok=True)
  for key in DATA['figures']:
   for ext in['.pdf','.png']:shutil.copy2(OUT/(key+ext),assets/(key+ext))
  (d/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f'Exported {len(selected)} figures. Native canvas and card containment passed.')
if __name__=='__main__':main()
