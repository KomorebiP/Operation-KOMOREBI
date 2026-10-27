#!/usr/bin/env python3
"""Generate 28 editable, deterministic vector plates from Paper X's exact models."""
from pathlib import Path
import json,math
import sympy as s
from models import *
from drawing import Plate,tex,F,seq,OUT
OUT.mkdir(parents=True,exist_ok=True);plates=[]
def done(p):plates.append(p.finish())

p=Plate('01_three_questions','A root, a branch, and an occupied carrier')
for x in [4.55,9.25]:p.line(x,0,x,4.45,'black!25')
p.text(2.1,4.35,'A residual root');p.text(2.1,3.55,r'$x^2+1=0$ over $\mathbb F_2$');p.circ(2.1,2.55,.24,'draw,fill=black!12');p.text(2.1,2.55,'$1$');p.text(2.1,1.45,'one point mod $2$');p.text(2.1,.55,'no point mod $4$',r'font=\footnotesize')
p.text(6.9,4.35,'A coherent branch');p.text(6.9,3.55,r'$x^2+1=0$ over $\mathbb Z_5$')
for j,a in enumerate([2,7,57,182]):
 x=5.3+j*1.08;p.circ(x,2.5,.29,'draw,fill=white');p.text(x,2.5,'$'+str(a)+'$',r'font=\scriptsize');p.text(x,1.9,'$5^{'+str(j+1)+'}$',r'font=\scriptsize')
 if j:p.line(x-.31,2.5,x-.77,2.5,'->')
p.text(6.9,.55,'reductions agree',r'font=\footnotesize')
p.text(11.65,4.35,'An occupied packet');p.matrix(10.8,3.15,s.diag(1,0),cell=.83);p.text(11.65,1.05,r'$\operatorname{rank}E=1$');p.text(11.65,.4,'positivity needs a carrier',r'font=\footnotesize');done(p)

p=Plate('03_residual_grid','Residual fibers in a finite coefficient ring')
for j in range(9):p.text(2.2+j*1.16,4.15,'$'+str(j)+'$',r'font=\scriptsize')
for r in range(3):
 y=3.65-r*1.05;p.text(.85,y-.4,'$r='+str(r)+'$',r'font=\small')
 for j in range(9):
  p.rect(1.65+j*1.16,y-.82,1.1,.8,'draw=black!35,fill='+('black!10' if r==1 else 'white'))
  p.text(2.2+j*1.16,y-.42,'$'+str(3*j+r)+'$')
p.text(7,4.65,r'$x=3q+r\pmod{27}$: columns are higher-digit addresses $q$')
p.text(7,.05,'Adding $3$ moves within one row. Adding $1$ can change the row.',r'font=\footnotesize');done(p)

p=Plate('04_digits','A compatible stream for one quarter in Z5')
rs=quarter_branch()
for k in range(6):p.text(4.2+k*1.15,4.45,'$5^{'+str(k)+'}$',r'font=\scriptsize')
for m,a in enumerate(rs,1):
 y=4.08-(m-1)*.62;p.text(2.4,y-.23,'$x_{'+str(m)+'}='+str(a)+'$','anchor=east')
 for k in range(6):
  p.rect(3.65+k*1.15,y-.5,1.1,.48,'draw=black!25,fill='+('black!12' if k<m else 'white'))
  p.text(4.2+k*1.15,y-.25,('$'+str((a//5**k)%5)+'$') if k<m else r'\textemdash',r'font=\scriptsize')
p.text(11.95,3,r'$4x_m-1$\\$=3\cdot5^m$');p.text(11.95,1.25,r'digits already\\fixed never change',r'font=\scriptsize');done(p)

p=Plate('05_smooth_grid','All points of a two-parameter smooth chart at depth three')
cell=.41
for a in range(9):
 for b in range(9):
  p.rect(1.25+a*cell,.4+b*cell,cell,cell,'draw=black!25,fill=white')
  p.circ(1.25+(a+.5)*cell,.4+(b+.5)*cell,.038,'fill=black!65')
for a in [0,3,6,8]:p.text(1.25+(a+.5)*cell,.12,'$'+str(3*a)+'$',r'font=\scriptsize');p.text(1.04,.4+(a+.5)*cell,'$'+str(3*a)+'$',r'font=\scriptsize,anchor=east')
p.text(3.1,4.45,r'$(t_1,t_2)\in(3\mathbb Z/27\mathbb Z)^2$')
p.text(9.55,3.6,r'$9\times9=81$ points');p.text(9.55,2.55,r'$(t_1,t_2)\mapsto(t_1,t_2)\bmod9$');p.text(9.55,1.5,'Each parent has $3^2=9$ children.');p.text(9.55,.45,'The chart hypothesis supplies independent digits.',r'font=\footnotesize');done(p)

p=Plate('06_weights','Delayed activation of weighted coordinates')
weights=(1,2,4)
for m in range(1,8):p.text(3.25+(m-1)*1.35,4.4,'$m='+str(m)+'$',r'font=\scriptsize')
for i,w in enumerate(weights):
 y=3.9-i*.9;p.text(1.75,y-.34,'$w_'+str(i+1)+'='+str(w)+'$','anchor=east')
 for m in range(1,8):
  x=2.6+(m-1)*1.35;n=max(m-w,0);p.rect(x,y-.7,1.3,.67,'draw=black!35,fill='+('black!14' if n else 'white'));p.text(x+.65,y-.35,'$'+str(n)+'$')
p.text(1.75,.65,'count','anchor=east')
for m in range(1,8):p.text(3.25+(m-1)*1.35,.65,'$'+str(weighted_count(2,weights,m))+'$',r'font=\scriptsize')
p.text(7,-.05,'Cell = number of free binary digits, not first separation depth.',r'font=\footnotesize');done(p)

p=Plate('07_singular_forest','Actual reductions of square-zero residues')
levels=[roots_mod(3,m,lambda x:x*x) for m in range(1,5)];pos={}
for m,xs in enumerate(levels,1):
 y=4.15-(m-1)*1.18
 for j,a in enumerate(xs):pos[m,a]=((7 if len(xs)==1 else 1.0+j*11.8/(len(xs)-1)),y)
for m in range(2,5):
 for a in levels[m-1]:
  x,y=pos[m,a];xx,yy=pos[m-1,a%3**(m-1)];p.line(x,y+.13,xx,yy-.13,'->,black!45,line width=.5pt')
for (m,a),(x,y) in pos.items():
 p.circ(x,y,.23,'draw,fill='+('black!15' if a==0 else 'white'));p.text(x,y,'$'+str(a)+'$',r'font=\scriptsize')
for m in range(1,5):p.text(.15,4.15-(m-1)*1.18,'$3^{'+str(m)+'}$',r'anchor=east,font=\scriptsize')
for a in [3,6]:x,y=pos[2,a];p.text(x,y+.36,'no child',r'font=\scriptsize')
p.text(7,-.2,'More finite roots, but only the zero stream persists through every precision.',r'font=\footnotesize');done(p)

p=Plate('08_prime_forests','One scalar equation gives different local forests')
pr=[2,3,5,7,13]
for j,q in enumerate(pr):p.text(3+j*2.05,4.4,'$p='+str(q)+'$')
for m in [1,2,3]:
 p.text(1.4,3.5-(m-1), '$m='+str(m)+'$','anchor=east')
 for j,q in enumerate(pr):
  n=len(roots_mod(q,m));p.rect(2.2+j*2.05,3.05-(m-1),1.6,.85,'draw=black!35,fill='+('black!12' if n else 'white'));p.text(3+j*2.05,3.48-(m-1),'$'+str(n)+'$')
p.text(7,.15,r'Counts of $x\in\mathbb Z/p^m\mathbb Z$ with $x^2+1=0$.',r'font=\footnotesize');done(p)

p=Plate('09_infinite_tail','Nonempty infinite levels can have no compatible branch')
for n in range(1,11):p.text(2.3+(n-1)*.97,4.5,'$'+str(n)+'$',r'font=\scriptsize')
for m in range(1,7):
 y=4.18-(m-1)*.61;p.text(1.25,y-.25,'$X_'+str(m)+'$','anchor=east')
 for n in range(1,11):
  p.rect(1.85+(n-1)*.97,y-.5,.92,.48,'draw=black!25,fill='+('black!16' if n>=m else 'white'))
  if n>=m:p.circ(2.3+(n-1)*.97,y-.25,.055)
 p.text(12.1,y-.25,r'$\cdots$')
p.text(7,-.05,r'$X_m=\{n\in\mathbb N:n\ge m\}$; every reduction is an inclusion.',r'font=\footnotesize');done(p)

p=Plate('10_cohomology','Cycles and boundaries in an exact packet complex')
d0,d1,ps=complex_model()
p.matrix(1.4,3.95,d0,cell=.66,title=r'$d_0:C^0\to C^1$',rows=['$u_0$','$u_1$','$u_2$','$u_3$'],cols=['$e_0$','$e_1$'])
p.matrix(5.1,3.3,d1,cell=.69,title=r'$d_1:C^1\to C^2$',rows=['$f_0$','$f_1$'],cols=['$u_0$','$u_1$','$u_2$','$u_3$'])
p.text(11,3.7,'$d_1d_0=0$');p.text(11,2.65,r'$H^0=\langle[e_1]\rangle$');p.text(11,1.85,r'$H^1=\langle[u_2],[u_3]\rangle$');p.text(11,1.05,r'$H^2=\langle[f_1]\rangle$');p.text(6.8,.2,'Packet A is exact. Packet B has zero differentials and carries all cohomology.',r'font=\footnotesize');done(p)

p=Plate('11_chain_defect','Degreewise projectors need not define a subcomplex')
p.matrix(1.25,4,ps[1],cell=.61,title='valid $P_A^1$');p.matrix(5.0,4,s.diag(0,1,0,0),cell=.61,title='invalid $Q^1$');defect=d0*ps[0]-s.diag(0,1,0,0)*d0
p.matrix(9.55,4,defect,cell=.61,title='$d_0P_A^0-Q^1d_0$');p.text(7,.65,'$e_0$ is retained at the source but its image $u_0$ is deleted at the target.',r'font=\footnotesize');p.text(7,.0,'All displayed degreewise maps are idempotent. The differential test distinguishes them.',r'font=\footnotesize');done(p)

p=Plate('12_source_scc','Minimum seeds in the actual seven-vertex transport graph')
pos={'A':(1.0,3.8),'B':(3.2,3.8),'D':(1.0,1.0),'E':(3.2,1.0),'C':(7,3.8),'F':(11.7,2.4),'G':(7,.65)}
for u,v in EDGES:
 x,y=pos[u];xx,yy=pos[v]
 if (v,u) in EDGES:p.add(r'\draw[->] ('+F(x)+','+F(y)+') to[bend left=19] ('+F(xx)+','+F(yy)+');')
 else:p.line(x,y,xx,yy,'->')
for x,y,rx,ry in [(2.1,3.8,1.65,.55),(2.1,1,1.65,.55),(7,.65,.62,.48)]:p.add(r'\draw[dashed,black!60] ('+F(x)+','+F(y)+') ellipse ('+F(rx)+' and '+F(ry)+');')
for v,(x,y) in pos.items():p.circ(x,y,.22,'draw,fill=white');p.text(x,y,v)
p.text(11.1,4.35,'three source components');p.text(11.5,.7,r'$\operatorname{srank}=3$');p.text(7,-.1,'A minimum set meets each dashed source component.',r'font=\footnotesize');done(p)

p=Plate('13_transport','An actual horizontal map must preserve the equations')
for j,(a,b) in enumerate(zip([2,7,57,182],[3,18,68,443])):
 x=2+j*3.15;p.text(x,4.4,'mod $5^{'+str(j+1)+'}$');p.circ(x,3.3,.3,'draw,fill=white');p.text(x,3.3,'$'+str(a)+'$',r'font=\scriptsize');p.circ(x,1.5,.3,'draw,fill=white');p.text(x,1.5,'$'+str(b)+'$',r'font=\scriptsize');p.line(x,3.05,x,1.75,'<->');p.text(x+.45,2.4,'$-x$',r'font=\scriptsize')
 if j:p.line(x-.25,3.3,x-2.9,3.3,'->');p.line(x-.25,1.5,x-2.9,1.5,'->')
p.text(7,.3,r'Negation commutes with reduction. Translation by $1$ fails already at $2\mapsto3\mapsto4$ mod $5$.',r'font=\footnotesize');done(p)

p=Plate('14_spine','A common polynomial does not mean identical residue coefficients')
p.text(7,4.3,'$P(T)=T^2-5T+6=(T-2)(T-3)$')
M=s.Matrix([[1,-5,6],[1,0,1],[1,2,6]])
p.matrix(4.9,3.25,M,cell=.86,cellw=1.45,rows=[r'$\mathbb Z$',r'$\mathbb F_5$',r'$\mathbb F_7$'],cols=['$T^2$','$T$','$1$'],title='coefficient images under the declared maps')
p.text(7,.25,'Different residue rows come from the same algebraic polynomial.',r'font=\footnotesize');done(p)

p=Plate('15_separator','Finite character evaluations recover a multiplicity vector')
C,m,b,c=s3_data();p.matrix(2.1,3.85,C,cell=.8,rows=['$1$','$(12)$','$(123)$'],cols=['trivial','sign','standard'],title='$C$: actual $S_3$ character table')
p.matrix(6.15,3.85,m,cell=.8,title=r'$\boldsymbol m$');p.text(7.45,2.6,'$=$');p.matrix(8.05,3.85,b,cell=.8,title=r'$\boldsymbol b$');p.text(11.65,3.2,r'$\det C=6$');p.text(11.65,1.95,r'$C^{-1}\boldsymbol b$\\$=(2,0,1)^T$');p.text(7,.2,'Class representatives are finite group elements, not a proof that suitable Frobenius primes occur.',r'font=\footnotesize');done(p)

p=Plate('16_multiplicities','A unique rational solution can fail the carrier test')
rows=[([4,2,1],[2,0,1],'allowed'),([1,0,0],list(C.inv()*s.Matrix([1,0,0])),'nonintegral'),(list(C*s.Matrix([-1,1,1])),[-1,1,1],'negative'),(list(C*s.Matrix([3,0,1])),[3,0,1],'over capacity')]
p.text(3,4.4,r'trace data $\boldsymbol b$');p.text(7.4,4.4,r'$C^{-1}\boldsymbol b$');p.text(11.5,4.4,'capacity $(2,1,1)$')
for i,(bb,mm,status) in enumerate(rows):
 y=3.55-i*.9;p.line(.8,y-.4,13.3,y-.4,'black!25');p.text(3,y,'$('+','.join(tex(x) for x in bb)+')$');p.text(7.4,y,'$('+','.join(tex(x) for x in mm)+')$');p.text(11.5,y,status,r'font=\footnotesize')
done(p)

p=Plate('17_precision','One digit is lost by the separating lattice')

p.matrix(2.4,3.85,s.Matrix([4,4,0]),cell=.74,title=r'multiplicity difference $\delta m$');p.matrix(9,3.85,s.Matrix([8,0,8]),cell=.74,title=r'trace difference $C\delta m$');p.line(4.35,2.8,7.65,2.8,'->,line width=.8pt');p.text(6.0,3.3,'multiply by $C$')
p.text(3.2,1.15,'nonzero modulo $8$');p.text(10,1.15,'zero modulo $8$');p.text(7,.25,r'Modulo $16$, the traces separate them. $v_2(\det C)=v_2(6)=1$.',r'font=\footnotesize');done(p)

p=Plate('18_occupancy','Pairwise occupancy can conceal an empty joint packet')
labels,ops=occupancy_data()
for j,row in enumerate(labels):p.text(3.7+j*1.53,4.4,'$'+''.join(map(str,row))+'$')
conds=[('all states',lambda row:True),('$T_1=0$',lambda row:row[0]==0),('$T_1=T_2=0$',lambda row:row[:2]==(0,0)),('$T_1=T_2=T_3=0$',lambda row:row==(0,0,0)),('target $011$',lambda row:row==(0,1,1))]
for i,(name,f) in enumerate(conds):
 y=3.9-i*.76;p.text(2.65,y-.25,name,r'anchor=east,font=\scriptsize')
 for j,row in enumerate(labels):p.rect(3+j*1.53,y-.51,1.4,.49,'draw=black!35,fill='+('black!18' if f(row) else 'white'))
 p.text(13,y-.25,'$'+str(sum(f(row) for row in labels))+'$')
p.text(7,-.2,'Each pair of requirements from $011$ is occupied. Their triple intersection is empty.',r'font=\footnotesize');done(p)

p=Plate('19_hypotheses','Trace and ordinary eigenspaces have different boundaries')
p.matrix(1.5,3.95,s.eye(5),cell=.48,title=r'$I_5$ over $\mathbb F_5$');p.text(2.7,.8,'rank $5$, trace $0$');p.line(6.1,.1,6.1,4.45,'black!25')
p.matrix(7.6,3.5,s.Matrix([[0,1],[0,0]]),cell=.8,title='$N^2=0$');p.text(11.6,2.95,'only eigenvalue $0$');p.text(11.6,2.1,r'$\dim\ker N=1$');p.text(10.4,.8,'sole-eigenvalue product $=I_2$');p.text(7,-.05,'Keep characteristic zero for trace detection, and split semisimplicity for the Lagrange formula.',r'font=\footnotesize');done(p)

p=Plate('20_closedness','Nonzero values can converge to zero p-adically')
for j in range(7):p.text(3.5+j*1.23,4.45,'$3^{'+str(j)+'}$',r'font=\scriptsize')
for k in range(6):
 y=4.1-k*.63;p.text(1.95,y-.25,'$a_k=3^{'+str(k)+'}$','anchor=east')
 for j in range(7):
  p.rect(2.93+j*1.23,y-.5,1.15,.48,'draw=black!25,fill='+('black!18' if j==k else 'white'));p.text(3.5+j*1.23,y-.25,'$'+str(int(k==j))+'$',r'font=\scriptsize')
p.add(r'\draw[dashed,line width=.9pt] (2.88,.18) rectangle (6.59,4.2);');p.text(7,-.15,'Every $a_k$ is nonzero. Every fixed finite digit window eventually reads only zeros.',r'font=\footnotesize');done(p)

p=Plate('21_signed_norm','Congruent generators can have different absolute norms')
pt=p.axes(1.5,2.75,10.5,.01,6,1,xticks=[-5,-3,0,2,5],xmin=-5,xlabel='integer generators')
for a in [-3,2]:x,_=pt(a,0);p.circ(x,2.75,.12,'draw,fill=black!15');p.line(x,2.55,6.55,1.75,'->')
p.text(6.55,1.45,r'same residue $2\pmod5$');p.text(3.0,4.35,r'$N_{\mathbb Q/\mathbb Q}(-3)=-3$');p.text(10.5,4.35,r'$N_{\mathbb Q/\mathbb Q}(2)=2$')
p.text(3.0,.45,'$N((-3))=3$');p.text(10.5,.45,'$N((2))=2$');p.text(7,-.15,'The ideal norm is positive. Passing to absolute values must retain the real sign.',r'font=\footnotesize');done(p)

p=Plate('22_norm_table','The determinant norm on a 25-element quotient algebra')
M=s.Matrix([[f25_norm((a,b)) for b in range(5)] for a in range(5)])
p.matrix(1.45,4.0,M,cell=.62,rows=['$a='+str(a)+'$' for a in range(5)],cols=['$b='+str(b)+'$' for b in range(5)],title=r'$N(a+bu)=a^2-2b^2\pmod5$')
p.text(9.6,4.25,r'$u^2=2$ in $\mathbb F_{25}$');p.text(9.6,3.2,r'$M_{a+bu}=\begin{pmatrix}a&2b\\b&a\end{pmatrix}$')
p.text(9.6,2.0,r'$\#N^{-1}(0)=1$');p.text(9.6,1.05,r'$\#N^{-1}(r)=6$ for $r\ne0$');p.text(7,-.1,'All 25 elements are shown. Every nonzero element is a unit.',r'font=\footnotesize');done(p)

p=Plate('23_mean_cancellation','A nonscalar unit pairs positive and negative character weights')
for j,orb in enumerate(unit_orbits()):
 cx=2.2+j*4.65;cy=2.45;R=1.15
 for k,z in enumerate(orb):
  th=2*math.pi*k/8;x=cx+R*math.cos(th);y=cy+R*math.sin(th);th2=2*math.pi*(k+1)/8;xx=cx+R*math.cos(th2);yy=cy+R*math.sin(th2)
  p.line(x,y,xx,yy,'->,black!55,line width=.45pt');sign=chi5(f25_norm(z));p.circ(x,y,.1,'draw,fill='+('black' if sign>0 else 'white'));p.text(cx+1.64*math.cos(th),cy+1.64*math.sin(th),'$('+str(z[0])+','+str(z[1])+')$',r'font=\scriptsize')
 p.text(cx,cy,'sum $=0$',r'font=\scriptsize')
p.text(7,.1,r'Multiply by $v=2u$. Its norm is $2$, so $\chi(N(vz))=-\chi(N(z))$.',r'font=\footnotesize');p.text(7,-.4,'Filled node: $+1$. Open node: $-1$. The omitted zero element has weight $0$.',r'font=\scriptsize');done(p)

p=Plate('24_scalar_exception','Exactly when does a scalar witness exist?')
for d in range(1,7):p.text(4+(d-1)*1.5,4.4,'$d='+str(d)+'$')
names=['trivial','quartic','quadratic','conjugate quartic']
for k,name in enumerate(names):
 y=3.9-k*.85;p.text(2.8,y-.3,name,r'anchor=east,font=\footnotesize')
 for d in range(1,7):
  x=3.3+(d-1)*1.5;yes=scalar_witness(k,d);p.rect(x,y-.6,1.4,.58,'draw=black!30,fill='+('black!16' if yes else 'white'));p.text(x+.7,y-.3,'yes' if yes else 'no',r'font=\scriptsize')
p.text(7,.05,r'For $\chi_k(2)=i^k$, a witness exists exactly when $kd\not\equiv0\pmod4$.',r'font=\footnotesize');done(p)

p=Plate('25_avoidance','Avoiding several primes is a simultaneous residue problem')
for n in range(30):
 col=n%6;row=n//6;x=1+col*.78;y=4.05-row*.69;p.rect(x,y-.61,.72,.58,'draw=black!25,fill='+('black!17' if gcd(n,30)==1 else 'white'));p.text(x+.36,y-.3,'$'+str(n)+'$',r'font=\scriptsize')
 if n==29:p.rect(x-.03,y-.64,.78,.64,'draw,line width=1pt')
p.text(9.8,4.2,'Choose one residue in each quotient');p.text(9.8,3.2,r'$a\equiv1\pmod2$');p.text(9.8,2.45,r'$a\equiv2\pmod3$');p.text(9.8,1.7,r'$a\equiv4\pmod5$');p.text(9.8,.75,r'$a=29,\quad\gcd(29,30)=1$');p.text(7,-.1,'Shaded values avoid $2$, $3$, and $5$ simultaneously.',r'font=\footnotesize');done(p)

p=Plate('26_boundary_count','Complete residue cells cancel; the boundary remains')
cell=.3;xx=1.2;yy=.35
for a in range(12):
 for b in range(12):
  boundary=(a>=10 or b>=10);p.rect(xx+a*cell,yy+b*cell,cell,cell,'draw=black!22,fill='+('black!13' if boundary else 'white'))
  v=chi5(f25_norm((a%5,b%5)))
  if v:p.circ(xx+(a+.5)*cell,yy+(b+.5)*cell,.035,'draw,fill='+('black' if v>0 else 'white'))
for a in [0,5]:
 for b in [0,5]:p.rect(xx+a*cell,yy+b*cell,5*cell,5*cell,'draw,line width=.8pt')
p.text(3,4.4,r'$[0,12)^2\cap\mathbb Z^2$');p.text(9.8,3.75,r'four full $5\times5$ cells');p.text(9.8,2.85,'$100$ bulk points: sum $0$');p.text(9.8,1.95,'$44$ boundary points');p.text(9.8,1.05,'actual total $S_{12}=1$');p.text(7,-.1,r'$|S_L|\le L^2-(L-(L\bmod5))^2$ for this square-lattice model.',r'font=\footnotesize');done(p)

p=Plate('27_mellin','Power saving leaves a regular endpoint at s = 1')
pt=p.axes(1.1,.8,5,3.0,1.5,4,xticks=[.75,1,1.25,1.5],yticks=[1,2,3,4],xmin=.7,xlabel='$s$',ylabel='$I(s)=s/(s-1/2)$')
xs=seq(.7,1.5);p.curve(pt,xs,[x/(x-.5) for x in xs]);x,y=pt(1,2);p.circ(x,y,.06)
qt=p.axes(8.2,.8,4.6,3, .25,1.05,xticks=[-.25,0,.25],yticks=[0,.5,1],xmin=-.25,xlabel='$h$',ylabel='endpoint difference')
hs=seq(-.25,.25);p.curve(qt,hs,[abs(-h/(h+.5)) for h in hs]);p.curve(qt,hs,[4*abs(h) for h in hs],'dashed,line width=.8pt');p.text(10.5,-.28,r'solid: exact\quad dashed: $4|h|$',r'font=\scriptsize');done(p)

p=Plate('28_frobenius_boundary','Having samples is not the same as sampling every class')
pr=[3,5,7,11,13,17,19,23]
for j,q in enumerate(pr):
 x=1.25+j*.6;p.text(x,4.0,'$'+str(q)+'$',r'font=\scriptsize');p.text(x,3.3,'$'+str(len(roots_mod(q,1)))+'$',r'font=\scriptsize')
p.text(3.4,4.65,'odd primes $p$');p.text(3.4,2.7,r'roots of $x^2+1$ in $\mathbb F_p$',r'font=\scriptsize');p.text(3.4,1.5,r'two factorization types\\already appear in this finite list',r'font=\footnotesize')
p.matrix(8.0,3.7,s.Matrix([[1,1,2]]*3),cell=.77,title='repeat one class');p.text(10.2,.8,'three rows, rank one');p.text(7,-.1,'Finite character separation needs enough different evaluations, not just more evaluations.',r'font=\footnotesize');done(p)

p=Plate('29_coefficients','No scalar root is not the absence of every representation')
p.text(2.2,4.3,r'Scalar over $\mathbb F_3$');p.text(2.2,3.25,'$x=0,1,2$');p.text(2.2,2.35,'$x^2+1=1,2,2$');p.text(2.2,1.25,'no solution')
p.line(4.45,.3,4.45,4.45,'black!25');p.text(7,4.3,r'Matrix over $\mathbb F_3$');p.matrix(6.2,3.45,s.Matrix([[0,-1],[1,0]]),cell=.8);p.text(7,.85,'$A^2+I=0$')
p.line(9.3,.3,9.3,4.45,'black!25');p.text(11.7,4.3,r'Scalar over $\mathbb F_9$');p.text(11.7,3.25,'$u^2=-1$');p.text(11.7,2.2,'roots $u,-u$');p.text(11.7,1.15,'coefficient extension')
p.text(7,-.05,'Fix the coefficient field, dimension, and point category before declaring an occupancy failure.',r'font=\footnotesize');done(p)

(OUT/'FIGURE_INDEX.json').write_text(json.dumps(plates,indent=2)+'\n');print('Generated',len(plates),'editable vector plates')
