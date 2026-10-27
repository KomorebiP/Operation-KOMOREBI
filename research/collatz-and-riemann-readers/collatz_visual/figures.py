"""Exact Collatz visual atlas. All claim data use integers or Fraction.

Run: python conjecture_set/collatz_visual/figures.py
Floating coordinates are used only by matplotlib to draw exact saved objects.
"""
from pathlib import Path
from fractions import Fraction
from itertools import product
from math import comb
from datetime import datetime, timezone
import hashlib, json, platform, time, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
START = datetime.now(timezone.utc).isoformat()
T0 = time.perf_counter()
INK='#203747'; TEAL='#147d87'; GOLD='#cd8b2a'; RED='#b35252'; PALE='#e5f0f1'; GRAY='#73818c'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.labelsize':15,
                     'xtick.labelsize':14,'ytick.labelsize':14,'text.color':INK,
                     'axes.labelcolor':INK,'axes.edgecolor':'#bdc9ce',
                     'savefig.facecolor':'white','pdf.fonttype':42})
DATA={'conventions':'A removes all factors of two after 3n+1; S is cumulative valuation; C starts at zero.'}
DATA['figure_notes']={}
COUNTS={}
FIGURE_LAYOUT=[]

def v2(x):
    assert x>0
    return (x & -x).bit_length()-1
def step(n):
    a=v2(3*n+1)
    return (3*n+1)>>a,a
def packet(word):
    s=c=0
    out=[(s,c)]
    for a in word:
        c=3*c+(1<<s);s+=a;out.append((s,c))
    return len(word),s,c,out
def orbit(n,cap=200):
    xs=[n];word=[]
    while xs[-1]!=1 and len(word)<cap:
        x,a=step(xs[-1]);xs.append(x);word.append(a)
    assert xs[-1]==1
    return xs,word
def frac(f):
    return {'numerator':f.numerator,'denominator':f.denominator}
def base():
    f,a=plt.subplots(figsize=(7.5,5));f.subplots_adjust(left=.10,right=.98,bottom=.17,top=.94)
    return f,a
def canvas():
    f,a=base();a.set(xlim=(0,10),ylim=(0,7));a.axis('off');return f,a
def clean(a):
    a.spines[['top','right']].set_visible(False);a.grid(axis='y',alpha=.18,zorder=0)
def card(a,x,y,w,h,text,color=PALE,size=15,edge=None):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.09,rounding_size=.13',
                              facecolor=color,edgecolor=edge or color,linewidth=1.3))
    a.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,color=INK)
def arrow(a,p,q,color=GRAY):
    a.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=16,color=color,lw=1.7,
                              connectionstyle='arc3,rad=0'))
def footer(f,text):
    f.text(.10,.015,textwrap.fill(text,61),fontsize=14,color=GRAY,ha='left',va='bottom')
def save(f,key,note=None):
    # Reading notes live in the adjacent guide column, keeping plots free of a second footer.
    if note: DATA['figure_notes'][key]=note
    if any(ax.axison for ax in f.axes):
        f.tight_layout(pad=1.2)
    f.canvas.draw()
    renderer=f.canvas.get_renderer()
    # Matplotlib retains tick artists outside the view interval even though it does not draw them.
    outside_tick_artists=set()
    for ax in f.axes:
        for axis in [ax.xaxis,ax.yaxis]:
            lo,hi=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not lo<=tick.get_loc()<=hi:
                    outside_tick_artists.update([id(tick.label1),id(tick.label2)])
    for artist in f.findobj(matplotlib.text.Text):
        if not artist.get_visible() or not artist.get_text() or id(artist) in outside_tick_artists: continue
        box=artist.get_window_extent(renderer)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > f.bbox.x1+1 or box.y1 > f.bbox.y1+1:
            FIGURE_LAYOUT.append({'figure':key,'text':artist.get_text(),'bbox':list(box.bounds)})
    f.savefig(OUT/(key+'.pdf'));f.savefig(OUT/(key+'.png'),dpi=150);plt.close(f)

xs27,w27=orbit(27);k,S,C,p27=packet(w27)
assert len(w27)==41 and xs27[37]==23 and p27[37]==(59,1100931843921811423)
assert all(x>=27 for x in xs27[:37])
DATA['orbit27']={'states':xs27,'valuations':w27,'prefixes':p27,'first_descent':37}
def clock_orbit(n,shortcut=False):
    result=[n]
    while n!=1 and len(result)<500:
        n=(3*n+1)//2 if n%2 and shortcut else 3*n+1 if n%2 else n//2
        result.append(n)
    assert n==1
    return result
classical27=clock_orbit(27);shortcut27=clock_orbit(27,True)
assert len(classical27)-1==111 and len(shortcut27)-1==70 and max(classical27)==9232
DATA['orbit27']['classical_states']=classical27
DATA['orbit27']['shortcut_states']=shortcut27
COUNTS['complete_clock_controls']=2
xs151,w151=orbit(151);assert xs151==[151,227,341,1] and w151==[1,1,10]
DATA['orbit151']={'states':xs151,'valuations':w151}

# Independent finite checks: enumerate actual states and compare to residue and affine data.
total=0
for length in range(1,4):
    for word in product(range(1,4),repeat=length):
        k,s,c,_=packet(word);mod=1<<(s+1);u=(((1<<s)-c)*pow(3**k,-1,mod))%mod
        for n in range(1,4096,2):
            x=n;actual=[]
            for _ in word:
                x,a=step(x);actual.append(a)
            yes=tuple(actual)==word
            assert yes==(n%mod==u)
            if yes:assert (1<<s)*x==3**k*n+c
            total+=1
COUNTS['cylinder_instances']=total

# 01 The logical route, with exact claims rather than status decoration.
f,a=canvas()
for y,t in [(5.4,'Odd integer source  n'),(3.9,'Actual valuations  (a₀, …, aₖ₋₁)'),
            (2.4,r'$2^S x_k = 3^k n + C$'),(.9,r'$(2^S-3^k)n>C$  ⇒  $x_k<n$')]:
    card(a,1.0,y,8,1,t)
for y in [5.4,3.9,2.4]:arrow(a,(5,y-.04),(5,y-.48))
save(f,'01_route','Exact coordinates preserve order, admissibility, and the original source.')

# 02 Clock comparison, seed 3.
f,a=canvas(); seqs=[[3,10,5,16,8,4,2,1],[3,5,8,4,2,1],[3,5,1]]
assert seqs==[clock_orbit(3),clock_orbit(3,True),orbit(3)[0]]
DATA['clock3']={'classical':seqs[0],'shortcut':seqs[1],'odd':seqs[2]}
COUNTS['seed3_clock_controls']=3
for y,label,seq in zip([5.5,3.5,1.5],['Classical: 7 steps','Shortcut: 5 steps','Odd map: 2 steps'],seqs):
    a.text(.2,y+.65,label,fontsize=16,weight='bold')
    pos=np.linspace(.6,9.3,len(seq))
    for j,(p,n) in enumerate(zip(pos,seq)):
        if j:arrow(a,(pos[j-1]+.34,y),(p-.34,y))
        a.scatter([p],[y],s=820,color=PALE,edgecolor=TEAL,zorder=3)
        a.text(p,y,str(n),ha='center',va='center',fontsize=15,zorder=4)
save(f,'02_clocks','All three paths are finite portions of the same orbit. Each has its own clock.')

# 03 First valuations for all positive odd n<=31.
f,a=base();ns=list(range(1,32,2));vals=[v2(3*n+1) for n in ns]
a.bar(range(len(ns)),vals,color=[TEAL if x==1 else GOLD for x in vals],width=.75)
a.set_xticks(range(len(ns)),ns);a.set_xlabel('Odd source n');a.set_ylabel(r'$a(n)=\nu_2(3n+1)$')
a.set_ylim(0,6.4);a.set_yticks(range(1,7));clean(a)
for i,v in enumerate(vals):a.text(i,v+.12,str(v),ha='center',fontsize=14)
DATA['first_valuations']={'sources':ns,'valuations':vals}
save(f,'03_valuations','Exact integer arithmetic. Higher bars mean more divisions by two in one odd step.')

# 04 The affine identity for 27 after two steps, as exact balanced bars.
f,a=base();a.barh([1], [248], color=PALE,height=.5,edgecolor=TEAL)
a.barh([0],[243],color=TEAL,height=.5);a.barh([0],[5],left=[243],color=GOLD,height=.5)
a.text(124,1,'8 × 31 = 248',ha='center',va='center',fontsize=19)
a.text(121.5,0,'9 × 27 = 243',ha='center',va='center',fontsize=19,color='white')
a.annotate('offset C = 5',xy=(245.5,.0),xytext=(150,-.65),arrowprops={'arrowstyle':'->','color':GOLD},fontsize=16)
a.set(xlim=(0,275),ylim=(-1.05,1.75),yticks=[],xlabel='Exact integer amount');a.spines[['left','top','right']].set_visible(False)
a.text(10,1.55,r'$2^S x_2 = 3^2 n + C$  with  $S=3$',fontsize=20)
save(f,'04_affine','The offset is part of the equality. Removing it changes the descent decision.')

# 05 Same total depth, ordered offsets.
f,a=canvas()
for x,word in [(0.2,(1,3)),(5.3,(3,1))]:
    k,s,c,_=packet(word);u=(((1<<s)-c)*pow(9,-1,32))%32
    card(a,x,5.5,4.3,.8,str(word),size=22)
    card(a,x,3.7,4.3,1.3,f'S = {s}    C = {c}\nsource ≡ {u} (mod 32)',size=17)
    card(a,x,1.8,4.3,1.1,rf'$x_2=(9n+{c})/16$',size=20)
    arrow(a,(x+2.15,5.35),(x+2.15,5.12));arrow(a,(x+2.15,3.55),(x+2.15,3.05))
    DATA['word_'+''.join(map(str,word))]={'word':word,'S':s,'C':c,'residue':u,'modulus':32}
a.text(5,.65,'Same k and S. Different C and different sources.',ha='center',fontsize=17)
save(f,'05_order','Every transfer shown is restricted to its actual integer cylinder.')

# 06 The extra endpoint bit for word(2).
f,a=canvas();a.text(.25,6.3,r'Word (2):  $4x=3n+1$',fontsize=21)
for row,(n,x,ok) in enumerate([(1,1,True),(5,4,False),(9,7,True),(13,10,False),(17,13,True)]):
    y=5.05-row*.95
    card(a,.3,y,1.4,.65,str(n),size=19);arrow(a,(1.85,y+.33),(3.2,y+.33))
    card(a,3.35,y,1.4,.65,str(x),size=19,color=PALE if ok else '#f3e7e7')
    a.text(5.2,y+.33,'odd endpoint: exact a = 2' if ok else 'even endpoint: a > 2',va='center',fontsize=17)
a.text(.35,.2,'n ≡ 1 (mod 4): integral quotient\nn ≡ 1 (mod 8): exact oddness',fontsize=16)
save(f,'06_endpoint_bit','An integral quotient is not enough to certify the selected valuation.')

# 07 Cylinder refinement ladder, the itinerary of 27.
f,a=canvas();words=[(1,),(1,2),(1,2,1),(1,2,1,1)]
for i,w in enumerate(words):
    k,s,c,_=packet(w);mod=1<<(s+1);u=(((1<<s)-c)*pow(3**k,-1,mod))%mod;y=5.6-i*1.45
    card(a,.5,y,2.55,.85,str(w),size=17)
    arrow(a,(3.15,y+.42),(4.1,y+.42));card(a,4.25,y,5.2,.85,f'n ≡ {u} (mod {mod})',size=19)
    if i:arrow(a,(6.85,y+1.3),(6.85,y+.97),color=TEAL)
save(f,'07_residue_ladder','Nested exact cylinders expose more of the itinerary. Each still contains infinitely many integers.')

# 08 Concatenation controls the transformed offset.
f,a=canvas();card(a,.25,5.45,3.2,1,'w = (1)\n(k,S,C) = (1,1,1)',size=17)
card(a,6.5,5.45,3.2,1,'v = (3)\n(ℓ,U,D) = (1,3,1)',size=17)
arrow(a,(3.55,5.95),(6.4,5.95));a.text(5,6.3,'then',ha='center',fontsize=15)
card(a,1,3.45,8,1.15,r'$C_{wv}=3^\ell C+2^S D = 3+2 = 5$',size=21)
arrow(a,(5,5.25),(5,4.82));card(a,1,1.5,8,1.2,r'$F_v(F_w(n))=(9n+5)/16$',size=22)
arrow(a,(5,3.22),(5,2.89))
save(f,'08_composition','The first offset is multiplied by the second block. Offsets are not simply added.')

# 09 Local fall compared with the same source floor.
f,a=base();xx=[27,41,31];a.plot([0,1,2],xx,'o-',color=TEAL,lw=3,ms=10)
a.axhline(27,color=GOLD,lw=2,ls='--');a.text(1.25,27.9,'source floor: 27',fontsize=16,color=GOLD)
for r,n in enumerate(xx):a.annotate(str(n),(r,n),xytext=(0,13),textcoords='offset points',ha='center',fontsize=20)
a.annotate('local fall',xy=(1.75,33.5),xytext=(1.45,40),arrowprops={'arrowstyle':'->','color':GRAY},fontsize=16)
a.set(xlim=(-.2,2.2),ylim=(23,46),xticks=[0,1,2],xlabel='Odd accelerated step',ylabel='Actual state');clean(a)
save(f,'09_source_floor','31 is below 41 and above 27. A reset from the peak has not yet proved source descent.')

# 10 Full exact odd orbit of 27, with three coherent phases.
f,a=base();a.plot(range(42),xs27,color=TEAL,lw=2.5);a.scatter(range(42),xs27,s=23,color=TEAL)
a.axhline(27,color=GOLD,lw=1.8,ls='--');a.set_yscale('log');a.set(xlabel='Odd accelerated step',ylabel='Actual odd state',xlim=(-.5,41.5),ylim=(.8,6000))
a.scatter([37,41],[23,1],s=80,color=RED,zorder=5)
a.annotate('first descent\n37 → 23',xy=(37,23),xytext=(25,6),arrowprops={'arrowstyle':'->','color':RED},fontsize=15)
a.annotate('largest odd state\n3077',xy=(xs27.index(max(xs27)),max(xs27)),xytext=(2,850),arrowprops={'arrowstyle':'->','color':GRAY},fontsize=15)
clean(a);save(f,'10_orbit27','Exact orbit: 41 odd steps, 70 shortcut steps, 111 classical steps to 1. Log scale changes only the drawing.')

# 11 Counterexample to dropping the offset, actual word from 165.
f,a=canvas();x=165;ww=[]
for _ in range(17):x,b=step(x);ww.append(b)
k,s,c,_=packet(ww);g=(1<<s)-3**k
assert x==167 and s==27 and c==1106233681 and g==5077565 and c//g==217
assert step(165)==(31,4)
DATA['contracting_word165']={'source':165,'word':ww,'k':k,'S':s,'C':c,'G':g,'endpoint':x,'threshold':217}
card(a,.3,5.4,9.4,1,r'$2^{27}>3^{17}$: the coefficient contracts',size=21)
card(a,.3,3.7,4.3,1.1,'Source n = 165\nendpoint x₁₇ = 167',size=19)
card(a,5.4,3.7,4.3,1.1,'Descent threshold\nfloor(C/G) = 217',size=18)
card(a,.3,1.4,9.4,1.35,f'G × 165 = {g*165:,}\nC = {c:,}   (larger)',size=20)
arrow(a,(5,5.2),(5,4.96));arrow(a,(5,3.45),(5,2.98))
save(f,'11_contraction_threshold','This source already descends at its first step. The 17-step word tests only the finite-word implication.')

# 12 Strong induction: a real chain from 7 with chosen strict descents.
f,a=canvas();chain=[7,5,1];ys=[5.2,3.2,1.2]
for n,y in zip(chain,ys):card(a,2,y,6,1.1,f'odd source {n}',size=23)
for y,t in zip([5.2,3.2],['A⁴(7) = 5 < 7','A(5) = 1 < 5']):
    arrow(a,(5,y-.05),(5,y-.72));a.text(5.45,y-.48,t,va='center',fontsize=17)
a.text(5,.45,'Every smaller odd source is available to strong induction.',ha='center',fontsize=16)
save(f,'12_induction','Example chain. The theorem needs strict descent for every positive odd source above 1.')

# 13 No fixed horizon, five exact unit-valuation prefixes.
f,a=base();seeddata=[]
for K in [1,3,5,8,12]:
    n=(1<<(K+2))-1;pts=[(1<<(K+2-t))*3**t-1 for t in range(K+1)]
    cur=n
    for t in range(K+1):
        assert cur==pts[t] and cur>=n
        if t<K:cur,b=step(cur);assert b==1
    a.plot(range(K+1),[Fraction(v,n) for v in pts],'-o',lw=2,ms=4,label=f'K = {K}')
    seeddata.append({'K':K,'source':n,'prefix':pts})
a.axhline(1,color=GOLD,ls='--');a.set(xlabel='Odd step t',ylabel='State / original source',yscale='log',xlim=(-.3,12.3));a.legend(frameon=False,fontsize=14);clean(a)
DATA['horizon_prefixes']=seeddata;COUNTS['horizon_prefix_checks']=sum(z['K']+1 for z in seeddata)
save(f,'13_fixed_horizon','Displayed ratios are exact Fractions before plotting. The general unit-run formula proves the unbounded claim.')

# 14 An exact run exit at 151.
f,a=base();a.plot(range(4),xs151,'o-',color=TEAL,lw=3,ms=9)
a.axhline(151,color=GOLD,ls='--',lw=2)
for i,n in enumerate(xs151):
    a.annotate(str(n),(i,n),xytext=(0,14),textcoords='offset points',ha='center',fontsize=19)
for i,b in enumerate(w151):
    a.text(i+.5,(xs151[i]+xs151[i+1])/2+15,f'a = {b}',ha='center',fontsize=17)
a.text(.1,395,r'$3^3\cdot19=2^9+1$',fontsize=21)
a.text(.12,128,'source floor: 151',fontsize=16,color=GOLD)
a.set(xlim=(-.2,3.2),ylim=(-25,430),xticks=range(4),xlabel='Odd accelerated step',ylabel='Actual odd state');clean(a)
save(f,'14_run151','Exact first descent time: 3. The large final valuation is 10, not 9.')

# 15 Four delayed seeds. Area encodes exact digit count, not approximate seed size.
f,a=canvas();seeds=[]
for j,y in zip(range(1,5),[5.6,4.2,2.8,1.4]):
    q=((1<<(3**j))+1)//3**(j+1);n=(1<<(j+1))*q-1;cur=n;states=[n]
    for t in range(j+1):cur,b=step(cur);states.append(cur);assert (b==1 if t<j else b==3**j+1)
    assert cur==1 and all(z>=n for z in states[:-1]);seeds.append({'j':j,'q':q,'source':n,'states':states})
    card(a,.3,y,1.2,.85,f'j={j}',size=19);card(a,1.9,y,6.2,.85,f'{n:,}',size=17 if j<4 else 14)
    a.text(8.55,y+.42,f'{j+1} steps',va='center',fontsize=17)
DATA['delayed_seeds']=seeds;COUNTS['delayed_seed_checks']=sum(z['j']+1 for z in seeds)
save(f,'15_delayed_seeds','Each displayed seed reaches 1 at its first strict descent. The written formula supplies every j ≥ 1.')

# 16 Uniform lift, exact arithmetic progression slopes.
f,a=base();pars=list(range(7));sources=[151+8192*s for s in pars];targets=[1+54*s for s in pars]
for s,n,m in zip(pars,sources,targets):
    cur=n
    for _ in range(3):cur,_a=step(cur)
    assert cur==m
a.plot(pars,sources,'o-',color=TEAL,lw=2.8,label='source: 151 + 8192s')
a.plot(pars,targets,'s-',color=GOLD,lw=2.8,label='exit: 1 + 54s')
a.set_yscale('symlog',linthresh=1)
a.set(xlabel='Integer parameter s',ylabel='Exact integer value',xticks=pars,ylim=(.7,80000));clean(a);a.legend(frameon=False,fontsize=14,loc='upper left')
DATA['lift151']={'parameters':pars,'sources':sources,'targets':targets}
COUNTS['lift151_cases']=len(pars)
save(f,'16_cylinder_lift','Exact first descent at step 3 for every s ≥ 0. Termination of arbitrary exits is a separate obligation.')

# 17 The 1087 progression, varying last valuation.
f,a=base();pars=list(range(17));initial=[];upper=[];actual=[];lastval=[]
for t in pars:
    n=4096*t+1087;x=n;ww=[]
    for _ in range(7):x,b=step(x);ww.append(b)
    assert ww[:6]==[1,1,1,1,1,4] and x<=2187*t+581<n
    initial.append(n);upper.append(2187*t+581);actual.append(x);lastval.append(ww[-1])
a.plot(pars,initial,color=TEAL,lw=2.6,label='original source')
a.plot(pars,upper,color=GOLD,lw=2.6,label='unstripped upper bound')
a.scatter(pars,actual,color=RED,s=55,label='actual odd exit',zorder=5)
a.set(xlabel='Integer parameter t',ylabel='Exact integer value',xticks=[0,4,8,12,16]);clean(a);a.legend(frameon=False,fontsize=14)
DATA['progression1087']={'parameters':pars,'sources':initial,'upper_bounds':upper,'exits':actual,'last_valuations':lastval}
COUNTS['progression1087_cases']=len(pars)
save(f,'17_progression1087','Final valuations vary. Every actual exit is at most 2187t + 581, strictly below the source.')

# 18 Historical coverage, exact aggregate waffle with counts, no implied residue order.
f,a=base();a.axis('off');cols=64;rows=32
for i in range(2048):
    x=i%cols;y=rows-1-i//cols
    a.add_patch(Rectangle((x,y),.86,.86,facecolor=TEAL if i<1804 else GOLD,edgecolor='none'))
a.set(xlim=(-1,65),ylim=(-9,34));a.text(0,-3.5,'1804 covered',color=TEAL,fontsize=19,weight='bold')
a.text(36,-3.5,'244 residual',color=GOLD,fontsize=19,weight='bold')
a.text(0,-7,'2048 odd classes modulo 4096',fontsize=18)
DATA['historical_coverage']={'covered':1804,'residual':244,'total':2048,'status':'saved historical aggregate; not replayed'}
save(f,'18_historical_coverage','Each square is one class count. Squares are grouped by status, not arranged by residue address. Historical receipt only.')

# 19 Deficit coordinates for the actual noncrossing prefix of 27.
f,a=base();rs=list(range(37));ss=[p27[r][0] for r in rs];critical=[(3**r).bit_length()-1 for r in rs];ds=[h-s for h,s in zip(critical,ss)]
assert all(d>=0 for d in ds)
a.step(rs,critical,where='mid',color=GOLD,lw=2.5,label=r'$\lfloor r\log_2 3\rfloor$')
a.step(rs,ss,where='mid',color=TEAL,lw=2.5,label=r'$S_r$')
a.fill_between(rs,ss,critical,step='mid',color=PALE)
a.annotate('deficit dᵣ',xy=(25,critical[25]-ds[25]/2),xytext=(11,43),arrowprops={'arrowstyle':'->','color':GRAY},fontsize=17)
a.set(xlabel='Odd accelerated step r',ylabel='Exact integer dyadic depth',xlim=(0,36));clean(a);a.legend(frameon=False,fontsize=14,loc='upper left')
DATA['deficit27_prefix']={'steps':rs,'S':ss,'critical_depth':critical,'deficit':ds}
save(f,'19_deficit_coordinates','This is a finite actual prefix, not a simulation of a permanently noncrossing orbit.')

# 20 Rare cylinder density: exact positive-word sum and exact rational bound.
f,a=base();ell=list(range(1,25));densitydata=[]
for D,color in [(0,TEAL),(3,GOLD)]:
    exact=[];bound=[]
    for l in ell:
        k=5*l;h=8*l+D+1;e=sum((Fraction(comb(s-1,k-1),1<<(s+1)) for s in range(k,h+1)),Fraction(0))
        b=Fraction(1,2)*Fraction(4,3)**(D+1)*Fraction(65536,84375)**l
        assert e<=b;exact.append(e);bound.append(b)
    a.plot(ell,[float(z) for z in bound],color=color,lw=2.4,label=f'bound, D = {D}')
    a.scatter(ell,[float(z) for z in exact],color=color,s=22,marker='o')
    densitydata.append({'D':D,'ell':ell,'exact_sums':[frac(z) for z in exact],'bounds':[frac(z) for z in bound]})
a.set(xlabel='Block parameter ℓ  (length = 5ℓ)',ylabel='Absolute integer density bound',yscale='log',xlim=(.5,24.5));clean(a);a.legend(frameon=False,fontsize=14)
DATA['density_decay']=densitydata;COUNTS['density_inequality_checks']=48
save(f,'20_density_decay','Dots: exact finite sums. Lines: exact rational upper bounds. All arithmetic is Fraction before rendering.')

# 21 Capacity argument: explicitly schematic because no such orbit is claimed.
f,a=base();r=np.arange(0,101);a.plot(r,r,color=TEAL,lw=3,label='required distinct states: R − N')
a.plot(r,.42*r+12,color=GOLD,lw=3,label='rare-cylinder capacity: ε H_R + W')
a.fill_between(r,.42*r+12,r,where=r>.42*r+12,color=PALE)
a.set(xlabel='Increasing orbit horizon R',ylabel='Number of states',xlim=(0,100),ylim=(0,105));clean(a);a.legend(frameon=False,fontsize=14,loc='upper left')
a.text(50,23,'Schematic constants\nε · 2ᴰ⁺¹ / 3 < 1',fontsize=17,ha='center')
save(f,'21_common_height','Proof schematic. Its lines are not data from a hypothetical counterexample or a newly observed orbit.')

# 22 Divisibility requirements for a cycle and same-word smaller source.
f,a=canvas();card(a,.3,5.25,9.4,1.1,r'Cycle:  $(2^S-3^k)n=C>0$',size=22)
card(a,.3,3.25,9.4,1.1,r'Same word, $n>m$:  $3^k(n-m)=2^S(y-x)$',size=20)
arrow(a,(5,3.02),(5,2.64));card(a,.3,1.3,9.4,1.1,r'$2^S\mid(n-m)$  ⇒  $n-m\geq2^S$',size=22)
a.text(5,.65,'If 2ˢ ≥ n, no smaller positive m can share that word.',ha='center',fontsize=17)
save(f,'22_divisibility','The necessary cycle equation does not eliminate cycles. A changed-word merger needs a separate existence theorem.')

# 23 The remaining global split, precise enough to carry the theorem.
f,a=canvas();card(a,1.8,5.5,6.4,1.1,'Infinite orbit\nabove its original source',size=18)
arrow(a,(3.7,5.36),(2.5,4.75));arrow(a,(6.3,5.36),(7.5,4.75))
card(a,.2,3.5,4.6,1.1,'Coefficient crossing\nat some r: ρᵣ > 1',size=17)
card(a,5.2,3.5,4.6,1.1,'Permanent noncrossing\nρᵣ ≤ 1 for every r',size=17)
arrow(a,(2.5,3.3),(2.5,2.7));arrow(a,(7.5,3.3),(7.5,2.7))
card(a,.2,1.5,4.6,1.0,'Still overcome C\nto force source descent',color='#f3ead9',size=17)
card(a,5.2,1.5,4.6,1.0,'Bounded deficit excluded\nunbounded branch remains',color='#f3ead9',size=16)
a.text(5,.5,'No branch is closed by finite coverage alone.',ha='center',fontsize=17)
save(f,'23_open_branches','Logical dependency map. The bottom obligations are open in this work.')

# 24 Reader checks, three arithmetic tasks with exact results.
f,a=canvas()
for y,left,right in [(5.2,'Word (1, 2), source 27','8 × 31 = 9 × 27 + 5'),
                      (3.15,'Lift parameter s = 1','8343 → 12515 → 18773 → 55'),
                      (1.1,'Progression parameter t = 1','5183 → ⋯ → 173 < 5183')]:
    card(a,.3,y,9.4,1.45,left+'\n'+right,size=19)
cur=5183
for _ in range(7):cur,_a=step(cur)
assert cur==173
DATA['reader_checks']={'lift_s1':[8343,12515,18773,55],'progression_t1_exit':173}
save(f,'24_reader_checks','Exact answers. Recover the word, modulus, original floor, and valuation at the final step.')

(ROOT/'data.json').write_text(json.dumps(DATA,indent=2)+'\n')
(ROOT/'FIGURE_LAYOUT_CHECK.json').write_text(json.dumps({'outside_canvas_text':FIGURE_LAYOUT,'status':'pass' if not FIGURE_LAYOUT else 'needs inspection'},indent=2)+'\n')
paths=[ROOT/'figures.py',ROOT/'data.json',ROOT/'FIGURE_LAYOUT_CHECK.json']+sorted(OUT.glob('*.pdf'))+sorted(OUT.glob('*.png'))
outputs=[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
report={'schema_version':1,'claim_id':'collatz-visual-atlas-finite-checks',
 'repository':{'commit':'not a Git checkout','dirty':True},'command':'python conjecture_set/collatz_visual/figures.py',
 'environment':{'software':[f'Python {platform.python_version()}',f'matplotlib {matplotlib.__version__}',f'NumPy {np.__version__}'],
                'hardware':platform.machine()+' '+platform.system()},
 'mathematics':{'assertion_tested':'Exact finite orbit, affine cylinder, delayed seed, lift, progression and density identities.',
  'coefficient_domain':'Python integers and fractions.Fraction; float coordinates only for rendering',
  'conventions':DATA['conventions'],'inputs':['27','151','165','odd integers 1 through 4095','words length 1 through 3 with valuations 1 through 3'],
  'bounds':{'cylinder_seed_max':4095,'cylinder_lengths':[1,2,3],'cylinder_exponents':[1,2,3],
            'delayed_seed_parameters':[1,2,3,4],'lift_parameters':[0,6],'progression_parameters':[0,16],
            'density_ell':[1,24],'density_D':[0,3],'odd_orbit_cap':200,'classical_shortcut_control_cap':500},
  'non_claims':['No universal conjecture proof is inferred from a finite run.','Historical 1804/2048 coverage is not replayed.',
                'The common-height diagram is schematic; there is no constructed permanent noncrossing orbit.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':START,'runtime_seconds':time.perf_counter()-T0,'exit_status':0},
 'outputs':outputs,'checks':[{'name':key,'status':'pass','instances':val} for key,val in COUNTS.items()],
 'result':'implementation and finite assertion verified in the stated range',
 'residual_risks':['Matplotlib coordinates are floating approximations of exact objects.','Historical receipt values are sourced, not recomputed.',
                   'Version 1 manifest has manual provenance rather than a bounded-runner transcript.']}
(ROOT/'COMPUTATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'COMPUTATION_REPORT.md').write_text('# Collatz visual atlas computation audit\n\n'
 'The figures use exact Python integers and `Fraction` for every claim-supporting value. Floating point is used only to place marks on the page.\n\n'
 + '\n'.join(f'- {key}: {value} finite checks passed.' for key,value in COUNTS.items())+'\n\n'
 'The seed ranges, word ranges, software versions, hashes and actual runtime are recorded in `COMPUTATION_REPORT.json`. The deterministic regeneration command is `python conjecture_set/collatz_visual/figures.py`.\n\n'
 'The cylinder test independently iterates each actual odd map, then compares its word with the residue computed by the affine formula. It also checks the affine endpoint equality for realized words. Density sums use exact binomial coefficients and rational powers.\n\n'
 'No failure was observed in these finite checks. This does not certify the Collatz conjecture. The 1804 covered and 244 residual classes are historical aggregate counts and were not replayed. The common-height packing figure is an explicitly declared proof schematic, not orbit data. The source formulas are proved in the companion monograph.\n\n'
 'Every positive odd map iteration is capped at 200 steps in complete-orbit plots. Independent classical and shortcut controls are capped at 500 iterations. A cap violation raises an assertion rather than silently marking the source convergent. No random sampling is used.\n\n'
 '## Resolved authoring failures\n\n'
 '- The first rendering run stopped at spread 16 because `linthresh` was passed to `Axes.set`. It was moved to `Axes.set_yscale` and the complete run passed.\n'
 '- The initial peak arrow used a manually entered step 17 for the value 3077. Independent review found the correct step 32. The arrow now derives its location from the exact maximum index.\n'
 '- Initial chart footers collided with axis labels. Footer prose was moved into the reading columns and retained in `data.json`. Plot margins are now fitted automatically, and the final figures are checked visually.\n')
print(json.dumps({'figures':len(list(OUT.glob('*.pdf'))),'checks':COUNTS,'runtime_seconds':report['run']['runtime_seconds']},indent=2))
