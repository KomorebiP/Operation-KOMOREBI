#!/usr/bin/env python3
"""Generate editable TikZ plates from the exact models. No external assets."""
from __future__ import annotations
from pathlib import Path
import math
import sympy as sp
import models as M
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics';OUT.mkdir(exist_ok=True)
plates=[]

def lab(x,y,text,opts=''):
    return rf'\node[{opts}] at ({x:.5f},{y:.5f}) {{{text}}};'+'\n'

def line(x1,y1,x2,y2,opts=''):
    return rf'\draw[{opts}] ({x1:.5f},{y1:.5f}) -- ({x2:.5f},{y2:.5f});'+'\n'

def cell(x,y,w,h,text='',shade=0,opts=''):
    s=rf'\draw[fill=black!{shade},draw=black!45,line width=.35pt,{opts}] ({x:.5f},{y:.5f}) rectangle ++({w:.5f},{h:.5f});'+'\n'
    if text: s+=lab(x+w/2,y+h/2,text,'text=white' if shade>65 else '')
    return s

def matrix(a,x,y,c=.52,cuts=(),title='',zero='.'):
    a=sp.Matrix(a);s=''
    if title:s+=lab(x+a.cols*c/2,y+.55,title)
    for i in range(a.rows):
        for j in range(a.cols):
            v=a[i,j];txt=('$'+sp.latex(v)+'$') if v else (r'$\cdot$' if zero=='.' else '$0$')
            s+=cell(x+j*c,y-(i+1)*c,c,c,txt,12 if v else 0)
    for k in cuts:
        s+=line(x+k*c,y,x+k*c,y-a.rows*c,'line width=1.3pt')
        s+=line(x,y-k*c,x+a.cols*c,y-k*c,'line width=1.3pt')
    return s

def save(name,s):
    pre=r'\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,font=\sffamily\small,line cap=round]'+'\n'
    (OUT/f'{name}.tex').write_text(pre+s+'\\end{tikzpicture}\n')
    plates.append(name)

# 1. Three exact finite objects, no generic flowchart.
s=lab(2,2.9,'ADDRESS',r'font=\sffamily\bfseries')+lab(6.2,2.9,'WEIGHT',r'font=\sffamily\bfseries')+lab(10.4,2.9,'SEPARATION',r'font=\sffamily\bfseries')
for i,v in enumerate([0,2,4,6]):s+=cell(.3+i*.8,1.65,.8,.6,f'${v}$',12)
for i,v in enumerate([0,4,2,6]):s+=cell(.3+i*.8,.65,.8,.6,f'${v}$',28 if i<2 else 5)
s+=lab(1.9,-.15,r'$4\text{ coordinates at both levels}$',r'font=\sffamily\footnotesize')
for i,(w,name) in enumerate([(1,'a'),(2,'b'),(4,'aba')]):
 s+=cell(4.5,.55+i*.6,.42*w,.43,f'${name}$',15+15*i)+lab(4.5+.42*w+.2,.76+i*.6,f'${w}$','anchor=west')
s+=lab(6.15,-.15,r'$W(aba)=1+2+1=4$',r'font=\sffamily\footnotesize')
s+=matrix(sp.Matrix([[1,sp.Rational(1,2)],[0,0]]),9.1,2.3,c=.65,zero='0')
s+=lab(10.4,-.15,r'\shortstack{$2E_+$ integral\\$E_+$ not integral}',r'font=\sffamily\footnotesize')
s+=line(4.0,-.4,4.0,3.2,'black!25')+line(8.25,-.4,8.25,3.2,'black!25')
save('three_resolutions',s)

# 3. A genuine coefficient regrouping rail: each address appears exactly once.
s=''
orders=[[r for r in range(16) if r%2==j] for j in (0,1)]
for row,(q,residues) in enumerate([(2,[0,1]),(4,[0,2,1,3]),(8,[0,4,2,6,1,5,3,7])]):
 y=3.8-row*1.65;s+=lab(-.22,y+.33,f'$N={q}$','anchor=east');x=0
 for group,r in enumerate(residues):
  inds=list(range(r,16,q));start=x
  for v in inds:
   s+=cell(x,y,.72,.62,f'${v}$',10 if group%2==0 else 27);x+=.72
  s+=line(start,y+.68,x,y+.68,'line width=1.0pt')
  s+=lab((start+x)/2,y+1.0,rf'$r={r}$',r'font=\sffamily\scriptsize')
 s+=lab(12.0,y+.32,'16','anchor=west')
s+=lab(5.76,-.18,'Each cell is an address n; its coefficient travels with it.')
save('coefficient_tower',s)

# 4. Component storage versus scalar summaries.
s=matrix(sp.diag(1,2,3,4),0,3.4,c=.57,title='Fine packet vectors',zero='0')
s+=matrix(sp.Matrix([[1,0,3,0],[0,2,0,4]]),4.0,3.4,c=.57,title='Coarse packet vectors',zero='0')
s+=lab(3.15,2.2,r'$\sum_{\rm children}$')
s+=lab(1.14,.1,r'$4\times1=4\text{ free coordinates}$')+lab(5.14,.1,r'$2\times2=4\text{ free coordinates}$')
s+=line(7.35,-.35,7.35,4.0,'black!30')
s+=matrix(sp.Matrix([[1,0,1,0],[0,1,0,1]]),8.6,3.4,c=.57,title='Scalar incidence only',zero='0')
s+=lab(9.74,1.55,r'$(x_0+x_2,\ x_1+x_3)$')
s+=lab(9.74,.1,r'$4\longrightarrow2\text{ scalars: loss}$')
save('regrouping_not_averaging',s)

# 5. True permutation and operator matrices.
a=M.refinement_model();s=''
for x,key,title,cuts in [(0,'T2',r'$\widehat T_2$',(4,)),(4.6,'J',r'$J_{4,2}$',()),(9.2,'T4',r'$\widehat T_4$',(2,4,6))]:
 s+=matrix(a[key],x,3.7,c=.46,cuts=cuts,title=title)
s+=lab(6.45,-.6,r'$J_{4,2}\widehat T_2=\widehat T_4J_{4,2}$')
save('operator_naturality',s)

# 6. Masks over F2.
x=[1,1,0,1,1,0,1,1]
s=''
for row,(title,values) in enumerate([(r'$x$',x),(r'$P_{2,0}x$',[v if i%2==0 else 0 for i,v in enumerate(x)]),(r'$P_{2,1}x$',[v if i%2 else 0 for i,v in enumerate(x)]),(r'$(P_{2,0}+P_{2,1})x$',x)]):
 y=3.4-row*.85;s+=lab(-.2,y+.3,title,'anchor=east')
 for i,v in enumerate(values):s+=cell(i*.75,y,.75,.6,f'${v}$',22 if v else 0)
for i in range(8):s+=lab(i*.75+.375,4.38,f'${i}$',r'font=\sffamily\scriptsize')
s+=lab(8.2,3.65,r'$\text{Coefficient address }n$')
s+=lab(8.2,2.25,r'$\text{No division by }2$')
s+=lab(8.2,.55,r'$\text{All arithmetic in }\mathbb F_2$')
save('division_free_masks',s)

# 7. Exact finite Fourier table and its failure in a product ring.
s=matrix(3*sp.eye(3),0,3.2,c=.7,title=r'$\sum_k4^{jk}2^{rk}\pmod7$',zero='0')
s+=lab(3.7,2.05,r'$\times\,5$')
s+=matrix(sp.eye(3),5,3.2,c=.7,title=r'$P_j(z^r):\ 5=3^{-1}\pmod7$',zero='0')
s+=lab(10.15,3.05,r'$\omega=2,\quad\omega^3=1$')
s+=lab(10.15,2.15,r'$\omega^{-1}=4,\quad\eta=5$')
s+=lab(10.15,1.25,r'$j,r\in\{0,1,2\}$')
s+=line(0,.25,12.2,.25,'black!35')
s+=lab(6,-.4,r'In $\mathbb F_3\times\mathbb F_3$: order two does not imply orthogonality.')
s+=lab(6,-1.15,r'$\omega=(-1,1),\quad\eta=(2,2),\quad \eta(1+\omega)=(0,1)\ne(0,0)$')
save('finite_fourier_table',s)

# 8. Exact CRT address rectangle.
g=M.crt_grid();s=''
for b,row in enumerate(g):
 y=2.3-b*.85;s+=lab(-.15,y+.4,f'$b={b}$','anchor=east')
 for a,n in enumerate(row):s+=cell(a*1.15,y,1.15,.8,f'${n}$',85 if n==7 else 9)
for a in range(4):s+=lab(a*1.15+.575,3.55,f'$a={a}$')
s+=lab(2.3,4.15,r'$a=n\bmod4$')
s+=lab(7.5,3.2,r'$b=n\bmod3$')+lab(7.5,2.25,r'$(a,b)=(3,1)\ \Longleftrightarrow\ n=7\pmod{12}$')
s+=lab(7.5,1.25,r'$7,\ 19,\ 31,\ldots$')
s+=lab(7.5,.15,r'$P_{12,7}=P_{4,3}P_{3,1}$')
save('crt_address_grid',s)

# 9. All nonzero retained words and the first discarded word.
s=''; rows=[('1',0,r'$I$',True),('a',1,r'$-2E_{01}$',True),('b',2,r'$-4E_{10}$',True),('ab',3,r'$+8E_{00}$',True),('ba',3,r'$+8E_{11}$',True),('aba',4,r'$-16E_{01}$',True),('bab',5,r'$-32E_{10}$',False)]
for i,(word,wt,value,keep) in enumerate(rows):
 y=4.2-i*.68
 s+=lab(.1,y,rf'${word}$','anchor=west')+cell(1.3,y-.23,max(.15,wt*.73),.46,'',20 if keep else 5,opts='' if keep else 'pattern=north east lines,pattern color=black!35')
 s+=lab(5.9,y,f'${wt}$')+lab(7.85,y,value)+lab(10.3,y,'keep' if keep else 'zero mod 32')
s+=lab(.1,4.85,'word','anchor=west')+lab(3.1,4.85,'cumulative weight')+lab(7.85,4.85,'signed contribution')
s+=line(1.3+5*.73,-.15,1.3+5*.73,4.55,'dashed,line width=1pt')
s+=lab(1.3+5*.73,-.5,r'$L=5$')
save('weighted_word_cutoff',s)

# 10. Actual inverse multiplications and rejected order.
w=M.weighted_model();s=''
for x,a,title in [(0,w['T'],r'$T$'),(3.4,M.matrix_mod(M.pruned_inverse(5)[1],32),r'$K$'),(6.8,sp.eye(2),r'$TK\pmod{32}$'),(10.2,sp.eye(2),r'$KT\pmod{32}$')]:
 s+=matrix(a,x,2.5,c=.7,title=title,zero='0')
s+=lab(6.0,-.05,r'$S=\begin{pmatrix}9&-18\\-4&9\end{pmatrix},\qquad K=SD^{-1}\pmod{32}$')
save('modular_inverse',s)

# 11. Exact valuation profile of residuals.
s=''
vals=[1,3,4,6,7,9,10]
for i,v in enumerate(vals):
 x=.6+i*1.35
 s+=line(x,0,x,v*.35,'line width=2pt')+lab(x,v*.35+.25,f'${v}$')+lab(x,-.4,f'${i+1}$')
s+=line(0,5*.35,9.3,5*.35,'dashed')+lab(9.35,5*.35,r'$L=5$','anchor=west')
s+=line(0,0,9.3,0)+lab(4.6,-1,r'number $N$ of geometric terms')
s+=lab(4.6,4.4,r'valuation of the residual $(-A)^N$')
save('inverse_residual_depth',s)

# 12. Distinct parallel edges and exact walk words.
s=lab(1.4,2.0,'$0$','circle,draw,minimum size=9mm')+lab(5.0,2.0,'$1$','circle,draw,minimum size=9mm')
s+=r'\draw[->] (1.5,2.45) to[out=100,in=170,looseness=6] node[above] {$\ell:1$} (1.05,2.2);'+'\n'
s+=r'\draw[->] (1.85,2.25) to[bend left=25] node[above] {$a:2$} (4.55,2.25);'+'\n'
s+=r'\draw[->] (1.85,1.97) -- node[above] {$b:2$} (4.55,1.97);'+'\n'
s+=r'\draw[->] (4.6,1.7) to[bend left=30] node[below] {$r:1$} (1.8,1.7);'+'\n'
s+=lab(3.1,.0,'Edge labels carry positive integer weights.')
s+=line(6.15,-.45,6.15,4.0,'black!35')
s+=lab(9.25,3.6,'All walks from 0 to 1 of weight 5',r'font=\sffamily\bfseries')
for i,word in enumerate([r'\ell\ell\ell a',r'\ell\ell\ell b','ara','arb','bra','brb']):
 s+=cell(7.1+(i%2)*2.3,2.5-(i//2)*.85,1.8,.58,f'${word}$',10)
save('weighted_multigraph',s)

# 13. An actual recurrence table.
c=M.walk_counts(12);s=''
for i in range(13):
 s+=cell(i*.87,1.75,.87,.65,f'${i}$',8)+cell(i*.87,1.0,.87,.65,f'${c[i]}$',20)
s+=lab(-.15,2.075,'$n$','anchor=east')+lab(-.15,1.325,'$a_n$','anchor=east')
s+=lab(5.65,3.1,r'$Z_{0,1}(t)=\dfrac{2t^2}{1-t-2t^3}$')
s+=lab(5.65,.0,rf'$a_8=a_7+2a_5={c[7]}+2\cdot{c[5]}={c[8]}$')
save('zeta_recurrence',s)

# 14. Evaluated Bezout numerator, scaling and exact range.
a=M.sign_model();s=matrix(a['A'],0,2.5,c=.7,title='$A$',zero='0')
s+=matrix(a['N'],3.6,2.5,c=.7,title='$N=I+A$',zero='0')
s+=matrix(a['Eplus'],7.2,2.5,c=.7,title='$E_+=N/2$',zero='0')
s+=lab(11.0,2.1,r'$N^2=2N$')+lab(11.0,1.2,r'$E_+^2=E_+$')
s+=lab(6.0,-.05,r'$E_+(1,0)=(1,0),\qquad E_+(-1,2)=(0,0)$')
save('bezout_normalization',s)

# 15. Integral eigenlattice is index two.
s=''
for x in range(-3,4):
 for y in range(-2,4):
  s+=rf'\draw[fill={"black" if y%2==0 else "white"},draw=black!65] ({x*.65:.3f},{y*.65:.3f}) circle (.045);'+'\n'
s+=line(-2.2,0,2.5,0,'->')+line(0,-1.5,0,2.45,'->')
s+=line(0,0,.65,0,'->,line width=1.1pt')+lab(1.15,.30,r'$(1,0)$')
s+=line(0,0,-.65,1.3,'->,line width=1.1pt')+lab(-1.22,1.48,r'$(-1,2)$')
s+=r'\draw[fill=white,line width=1.2pt] (.325,0) circle (.095);'+'\n'
s+=lab(.0,-2.03,r'$E_+(0,1)=(\frac12,0)$')
s+=lab(6.45,1.6,r'$B=\begin{pmatrix}1&-1\\0&2\end{pmatrix},\quad\det B=2$')
s+=lab(6.45,.6,r'Filled: $B\mathbb Z^2=\{(x,y):y\text{ is even}\}$')
s+=lab(6.45,-.35,'Unfilled: the other lattice coset.')
s+=lab(6.45,-1.25,r'$B^{-1}$ is integral at odd primes, not at $2$.')
save('dyadic_eigenlattice',s)

# 16. A sharp arithmetic example, no approximation.
s=''
headers=['input pair','difference','same mod 8?','$E_+$ difference','same mod 8?']
xs=[0,2.5,5.0,7.5,10.0]
for x,h in zip(xs,headers):s+=lab(x+1.05,3.1,h)
for row,data in enumerate([['$0,(0,8)$','$(0,8)$','yes','$(4,0)$','no'],['$0,(0,16)$','$(0,16)$','yes','$(8,0)$','yes']]):
 for x,v in zip(xs,data):s+=cell(x,1.95-row*1.0,2.1,.75,v,10 if row==0 else 22)
s+=lab(6.0,-.05,r'$m=3:\quad 3\text{ input digits fail; }4\text{ input digits suffice.}$')
save('precision_delay',s)

# Grid helper for modular inputs and fibres.
def modgrid(points,ox,oy,q=8,title='',labels=False):
 s=lab(ox+(q-1)*.44/2,oy+q*.44+.4,title)
 points=set(points)
 for a in range(q):
  for b in range(q):
   yes=(a,b) in points
   s+=rf'\draw[draw=black!45,fill={"black" if yes else "white"}] ({ox+a*.44:.5f},{oy+b*.44:.5f}) circle ({.075 if yes else .023});'+'\n'
 for a in range(q):s+=lab(ox+a*.44,oy-.3,f'${a}$',r'font=\sffamily\scriptsize')
 for b in range(q):s+=lab(ox-.3,oy+b*.44,f'${b}$',r'font=\sffamily\scriptsize')
 if labels:s+=lab(ox+q*.44+.35,oy+1.6,'second\ncoordinate')
 return s

# 17. Image set versus all input points.
fib=M.smith_fibres(2,3,(1,2))
s=modgrid([(x,y) for x in range(8) for y in range(8)],0,0,title=r'64 inputs $(x,y)$')
s+=modgrid(fib.keys(),7,0,title=r'8 attainable targets $(2x,4y)$')
s+=lab(5.1,2.0,r'$\diag(2,4)$')+lab(5.1,1.15,r'$\bmod 8$')
s+=lab(5.3,-1.0,r'Every filled target has exactly $2\cdot4=8$ preimages.')
save('smith_fibre_grid',s)

# 18. Actual supplied Smith-coordinate transform.
st=M.smith_transport_model()
ypts=[tuple(y) for y in __import__('itertools').product(range(8),repeat=2) if M.matrix_mod(st['D']*sp.Matrix(y),8)==st['rhs']]
xpts=[tuple(M.matrix_mod(st['V']*sp.Matrix(y),8)) for y in ypts]
s=modgrid(ypts,0,0,title=r'$Dy=(2,4)$')+modgrid(xpts,7,0,title=r'$Mx=(2,4)$')
s+=lab(5.1,2.3,r'$x=Vy$')+lab(5.1,1.3,r'$x_0=y_0-y_1$')+lab(5.1,.5,r'$x_1=y_1$')
s+=lab(5.4,-1.0,'The eight solutions are permuted, not created or discarded.')
save('smith_coordinate_transport',s)

# 19. Directional depth and fibre cardinality.
s=''
for L in range(1,7):
 x=.75+(L-1)*1.45; total=0
 for i,weight in enumerate((0,1,3)):
  h=min(L,weight)*.53
  if h:s+=cell(x,total,.78,h,'',15+30*i);total+=h
 s+=lab(x+.39,total+.28,f'${2**sum(min(L,v) for v in (0,1,3))}$')
 s+=lab(x+.39,-.4,f'${L}$')
s+=line(.3,0,9.3,0)+lab(4.7,-1.0,'precision depth $L$')
s+=lab(4.7,3.4,r'Bar height $=W(L)$; label $=2^{W(L)}$ solutions.')
s+=lab(10.5,2.35,r'$s_2=3$')+lab(10.5,1.15,r'$s_1=1$')+lab(10.5,.4,r'$s_0=0$')
save('smith_depth_budget',s)

# 20. Actual finite convolution and phase output arrays.
g=M.signal_model();s=''
for row,(label,vals) in enumerate([('$x$',g['x']),('$h*x$',g['y']),(r'$y_{\rm even}$',g['y'][::2]),(r'$y_{\rm odd}$',g['y'][1::2])]):
 y=3.6-row*.93;s+=lab(-.15,y+.3,label,'anchor=east')
 for i,v in enumerate(vals):s+=cell(i*.85,y,.85,.62,f'${v}$',10 if (row==0 and i%2==0) or row==2 else 25)
s+=lab(9.35,3.15,r'$h=(1,2,1)$')+lab(9.35,2.1,'zero extension')+lab(9.35,1.05,'no periodic wrap')
save('finite_polyphase_filter',s)

# 21. Exact algebraic phase orbit; decimal coordinates only at drawing boundary.
points=M.smith_chart_points();s=''
# Reflection disk drawn at scale 3.2; inner radius 1/2 -> radius 1.6.
s+=r'\draw[black!35] (0,0) circle (3.2);\draw[dashed] (0,0) circle (1.6);'+'\n'
s+=line(-3.4,0,3.4,0,'black!45')+line(0,-3.4,0,3.4,'black!45')
s+=lab(0,3.9,r'$\Gamma_k=\frac12e^{ik\pi/4}$')
for p in points:
 x=float(sp.re(p['gamma']))*3.2;y=float(sp.im(p['gamma']))*3.2
 s+=rf'\fill ({x:.5f},{y:.5f}) circle (.075);'+'\n'
 s+=lab(x*1.22,y*1.22,rf'${p["k"]}$')
# z circle under the Cayley map.
ox=8.2;sc=1.85;cx=ox+5/3*sc;r=4/3*sc
s+=rf'\draw[dashed] ({cx:.5f},0) circle ({r:.5f});'+'\n'
s+=line(ox-.3,0,ox+3.25*sc,0,'black!45')+line(ox,-2.85,ox,2.85,'black!45')
s+=lab(cx,3.9,r'$z_k=(1+\Gamma_k)/(1-\Gamma_k)$')
for p in points:
 x=ox+float(sp.re(p['z']))*sc;y=float(sp.im(p['z']))*sc
 s+=rf'\fill ({x:.5f},{y:.5f}) circle (.075);'+'\n'
 s+=lab(x+(x-cx)*.095,y*1.1,rf'${p["k"]}$')
# Values 3 and 1/3 are stated in the prose; labels k=0,4 remain unambiguous.
s+=lab(cx,-3.65,'Equal phase steps do not become equal impedance steps.')
save('smith_chart_orbit',s)

# 22. Power defect exact gains and certified norm majorants.
s=''
for i,n in enumerate(range(1,7)):
 x=.5+i*1.65;actual=2**n-1;bound=n*2**(n-1)
 s+=cell(x,0,.48,actual*.016,'',75)+cell(x+.52,0,.48,bound*.016,'',6)
 s+=lab(x+.24,actual*.016+.22,f'${actual}$',r'font=\sffamily\scriptsize')
 s+=lab(x+.76,bound*.016+.22,f'${bound}$',r'font=\sffamily\scriptsize')
 s+=lab(x+.5,-.38,f'${n}$')
s+=line(0,0,10.5,0)+lab(5.2,-.95,'number of applications $n$')
s+=lab(5.2,3.9,r'Black: $16\|\text{actual defect}\|_\infty$; pale: certified majorant.')
save('power_defect_growth',s)

# 23. Amplification approaching a pole from the right.
s=''
for row,z in enumerate([sp.Rational(5,2),sp.Rational(11,5),sp.Rational(21,10),sp.Rational(41,20),sp.Rational(201,100)]):
 gain=sp.cancel(1/((z-1)*(z-2)));y=3.8-row*.92
 s+=lab(-.2,y+.23,'$'+sp.latex(z)+'$','anchor=east')
 s+=cell(0,y,float(gain)*.075,.46,'',65)
 s+=lab(float(gain)*.075+.2,y+.23,'$'+sp.latex(gain)+'$','anchor=west')
s+=lab(-.2,4.65,'$z$','anchor=east')+lab(4,4.65,r'$\|C R_f-R_c C\|_\infty/\varepsilon$')
s+=lab(4.7,-1.15,'Exact rational samples; the point $z=2$ itself is excluded.')
save('resolvent_amplification',s)
print(f'Generated {len(plates)} exact-data vector plates: '+', '.join(plates))
