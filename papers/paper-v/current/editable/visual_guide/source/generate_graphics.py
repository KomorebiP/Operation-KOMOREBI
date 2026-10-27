#!/usr/bin/env python3
"""Editable monochrome vector plates from exact models.
Rational labels and algebra are exact; trigonometric curve positions are sampled
only for display, not for verification. No external or generated artwork.
"""
from pathlib import Path
import json,math
import sympy as s
import models as M
Q=M.Q
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics';OUT.mkdir(exist_ok=True)
plates=[]
def tex(v):return '$'+s.latex(s.sympify(v))+'$'
def lab(x,y,t,opts=''):
    return rf'\node[{opts}] at ({float(x):.5f},{float(y):.5f}) {{{t}}};'+'\n'
def line(x,y,a,b,opts=''):
    return rf'\draw[{opts}] ({float(x):.5f},{float(y):.5f}) -- ({float(a):.5f},{float(b):.5f});'+'\n'
def dot(x,y,opts='fill=black',rad=.05):
    return rf'\draw[{opts}] ({float(x):.5f},{float(y):.5f}) circle ({rad});'+'\n'
def cell(x,y,w,h,t='',shade=0):
    v=rf'\draw[fill=black!{shade},draw=black!40,line width=.35pt] ({float(x):.5f},{float(y):.5f}) rectangle ++({float(w):.5f},{float(h):.5f});'+'\n'
    return v+(lab(x+w/2,y+h/2,t) if t else '')
def matrix(a,x,y,c=.72,title=''):
    a=s.Matrix(a);v=lab(x+a.cols*c/2,y+.42,title) if title else ''
    for i in range(a.rows):
        for j in range(a.cols):v+=cell(x+j*c,y-(i+1)*c,c,c,tex(a[i,j]),14 if a[i,j]!=0 else 0)
    return v

def save(name,v):
    (OUT/(name+'.tex')).write_text(r'\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,font=\sffamily\small,line cap=round,line join=round]'+'\n'+v+'\\end{tikzpicture}\n')
    plates.append(name)
def chart(x0,y0,W,H,xlim,ylim,xticks,yticks):
    a,b=xlim;c,d=ylim
    def p(x,y):return x0+W*(float(x)-a)/(b-a),y0+H*(float(y)-c)/(d-c)
    v=''
    for x,t in xticks:
        X,_=p(x,c);v+=line(X,y0,X,y0+H,'black!12')+lab(X,y0-.27,str(t),r'font=\sffamily\footnotesize')
    for y,t in yticks:
        _,Y=p(a,y);v+=line(x0,Y,x0+W,Y,'black!12')+lab(x0-.14,Y,str(t),r'anchor=east,font=\sffamily\footnotesize')
    return v+line(x0,y0,x0+W+.13,y0,'->')+line(x0,y0,x0,y0+H+.13,'->'),p

def curve(p,data,opts='line width=1pt'):
    return '\\draw['+opts+'] plot coordinates {'+' '.join(f'({p(x,y)[0]:.5f},{p(x,y)[1]:.5f})' for x,y in data)+'};\n'
def stems(p,data,opts='line width=.65pt',open_dot=False):
    out=''
    for x,y in data:
        a,b=p(x,0);c,d=p(x,y);out+=line(a,b,c,d,opts)+dot(c,d,'fill=white,line width=.7pt' if open_dot else 'fill=black',.045)
    return out

# V1: three material objects rather than an architecture flow chart.
v=''
for i,title in enumerate(['SIGNAL COORDINATES','FINITE TREE CHOICES','REFLECTION ORBIT']):v+=lab(2.05+4.55*i,4.1,title,r'font=\sffamily\bfseries\footnotesize')
v+=line(.35,1.35,3.9,1.35,'black!40')
for i,a in enumerate(M.SIGNAL):v+=line(.45+i*.21,1.35,.45+i*.21,1.35+float(a)*.54)+dot(.45+i*.21,1.35+float(a)*.54,rad=.03)
v+=lab(2.1,.2,r'$f=s+j\quad\text{in }\QQ^{16}$')
for row,cut in enumerate([('',),('0','1'),('00','01','100','101','11')]):
    for a in cut:
        width=3.9/2**len(a);left=4.6+(int(a,2)/2**len(a)*3.9 if a else 0)
        v+=cell(left,2.9-row*.85,width,.57,'',14)
        v+=lab(left+width/2,2.9-row*.85+.57/2,'$'+(a or r'\varnothing')+'$',r'font=\tiny' if len(a)==3 else '')
v+=lab(6.55,.2,'26 complete prunings')
for radius in [1.5,.75]:v+=rf'\draw[black!35] (11.0,2.25) circle ({radius});'+'\n'
for k in range(4):v+=dot(11+.75*math.cos(k*math.pi/2),2.25+.75*math.sin(k*math.pi/2),rad=.065)
v+=lab(11,.2,r'$\Gamma=\tfrac12 i^k$')+line(4.25,-.1,4.25,4.45,'black!25')+line(8.6,-.1,8.6,4.45,'black!25')
save('three_worlds',v)
# V3 permutation of sixteen sample addresses.
v=lab(6.4,4.85,'FOUR PHASES: EVERY ADDRESS APPEARS ONCE')
for r in range(4):
    v+=lab(.75,3.75-r*.8,f'$r={r}$','anchor=east')
    for q in range(4):
        n=4*q+r;v+=cell(1.1+q*2.2,3.42-r*.8,2.2,.65,rf'$n={n}:\ {s.latex(M.SIGNAL[n])}$',12 if 6<=n<12 else 0)
v+=lab(11.9,3.7,r'$n=4q+r$')+lab(11.9,2.5,r'$-1=4(-1)+3$')+lab(11.9,1.35,r'$-5=4(-2)+3$')
for q in range(4):v+=lab(2.2+q*2.2,-.2,f'$q={q}$')
save('addresses',v)
# V4 common-lattice refinement: mask cells, not improperly added decimated arrays.
v='';rows=[('coarse $P_{2,0}$',lambda n:n%2==0),('fine $P_{4,0}$',lambda n:n%4==0),('fine $P_{4,2}$',lambda n:n%4==2)]
for row,(title,test) in enumerate(rows):
    y=3.5-row*1.15;v+=lab(.2,y+.28,title,'anchor=west')
    for n in range(12):v+=cell(3.0+n*.76,y,.76,.56,tex(n) if test(n) else '',22 if test(n) else 0)
for n in range(12):v+=lab(3.38+n*.76,.55,f'{n}',r'font=\sffamily\footnotesize')
v+=lab(7.45,4.45,r'$P_{2,0}=P_{4,0}+P_{4,2}$')+lab(7.45,-.05,'same original-sample axis $n$')
save('refinement',v)
# V5 FIR entries.
v=lab(6.3,4.6,r'$h=(1,2,-1,1),\qquad D:\ u[n]\mapsto u[n-1]$')
for row in range(2):
    v+=lab(1.8,3.1-row*1.25,f'output {row}','anchor=east')
    for col in range(2):v+=cell(2.2+col*4.1,2.55-row*1.25,4.1,1.05,tex(s.expand(M.H[row,col])),14 if row!=col else 0)
for col in range(2):v+=lab(4.25+col*4.1,3.95,f'input {col}')
v+=lab(6.4,.15,r'$y_0=(1-D)x_0+(2D+D^2)x_1$')
save('fir_transfer',v)
# V6 one-sample shift example.
v=matrix([[0,M.D],[1,0]],.7,3.6,1.05,title='one original sample')
v+=lab(4.2,2.6,r'$J(D)^2=$')+matrix([[M.D,0],[0,M.D]],5.4,3.6,1.05,title='two original samples')
v+=lab(10.6,3.5,r'$\delta_0\mapsto\delta_1$')+lab(10.6,2.25,r'$\delta_0\mapsto\delta_2$')
v+=lab(6.4,.35,r'$y_0[n]=x_1[n-1],\quad y_1[n]=x_0[n]$')
v+=lab(6.4,-.25,r'channel delay $1$ at $N=2$ is original-sample delay $2$')
save('sample_delay',v)
# V7 polynomial identity vs one evaluation.
v=matrix([[1,M.D],[0,1]],.6,3.7,1.0,title='$E(D)$')+matrix([[1,-M.D],[0,1]],4.7,3.7,1.0,title='$R(D)$')
v+=lab(9.5,3.1,r'$R(D)E(D)=I$')+lab(9.5,1.9,'every impulse is recovered')
v+=line(.5,1.1,12.6,1.1,'black!30')+lab(6.5,.45,r'$B(D)=\operatorname{diag}(D,1):\quad B(1)=I,\quad B(D)\ne I$')
v+=lab(6.5,-.2,'testing one frequency cannot detect a channel delay')
save('perfect_reconstruction',v)
# V8 aligned edge and tiny first-level detail.
a=M.one_level(16,0)*M.SIGNAL;d=M.one_level(16,1)*M.SIGNAL
v,p=chart(.65,1.05,11.4,3.05,(-.4,7.4),(-.75,7),[(i,str(i)) for i in range(8)],[(0,'0'),(3,'3'),(6,'6')])
v+=stems(p,[(i,s.sqrt(2)*a[i]) for i in range(8)])
v+=stems(p,[(i+.17,s.sqrt(2)*d[i]) for i in range(8)],'dashed',True)
v+=lab(6.1,4.65,r'solid: $\sqrt2\,a[n]$\qquad open: $\sqrt2\,d[n]$')
v+=lab(6.1,.25,r'$\|f\|^2=57=\frac{227}{4}+\frac14$')
save('haar_alignment',v)
# V9 shear map turns a square to a parallelogram, same area, different lengths.
v=''
for ox in [.8,7.1]:v+=line(ox-.2,2.25,ox+4.4,2.25,'->')+line(ox,0.1,ox,4.5,'->')
scale=.5
points=[s.Matrix([0,0]),s.Matrix([4,0]),s.Matrix([4,4]),s.Matrix([0,4])]
for ox,mat,title in [(.8,s.eye(2),'input $(e,o)$'),(7.1,M.LIFT,'output $(s,d)$')]:
    pp=[mat*q for q in points];coords=[(ox+float(q[0])*scale,2.25+float(q[1])*scale) for q in pp]
    v+='\\draw[fill=black!8,line width=.9pt] '+' -- '.join(f'({x:.3f},{y:.3f})' for x,y in coords)+' -- cycle;\n'
    v+=lab(ox+1.8,4.85,title)
v+=lab(3,-.4,r'$(2,6):\quad 2^2+6^2=40$')+lab(9.4,-.4,r'$(4,4):\quad 4^2+4^2=32$')
save('lifting_geometry',v)
# V10 actual complete depth-two matrix of coefficients.
v='';co=M.packet_coefficients()
for row,(address,cs) in enumerate(co.items()):
    v+=lab(1.1,3.75-row*.9,'$'+address+'$','anchor=east')
    for i,c in enumerate(cs):v+=cell(1.4+i*1.8,3.42-row*.9,1.8,.65,tex(c),18 if c!=0 else 0)
    v+=lab(10.9,3.75-row*.9,tex(M.energy(cs)))
v+=lab(5,4.6,'coefficient positions within each packet')+lab(10.9,4.6,'energy')
v+=lab(6.25,-.3,r'$\sum_{\alpha\in\{0,1\}^2}W_\alpha^*W_\alpha=I_{16}$')
save('depth_two',v)
# V11 exact coefficient tail.
_,_,_=M.best_coefficients(4)
entries=[(aa,i,c) for aa,cs in co.items() for i,c in enumerate(cs)];entries.sort(key=lambda q:(-q[2]**2,q[0],q[1]))
v,p=chart(.65,.8,11.6,3.5,(.5,16.5),(0,44),[(1,'1'),(4,'4'),(8,'8'),(12,'12'),(16,'16')],[(0,'0'),(10,'10'),(20,'20'),(40,'40')])
for i,(_,_,c) in enumerate(entries):
    X,Y=p(i+1,c*c);xx,yy=p(i+1,0);v+=cell(X-.16,yy,.32,Y-yy,'',45 if i<4 else 13)
v+=lab(6.2,4.75,'squared coefficient magnitude, sorted')+lab(6.2,.08,r'keep 4: discarded energy $=11/16$; keep 12: exact recovery')
save('sparse_tail',v)
# V12 antichains tile terminal packet addresses (not sample intervals).
v='';leafs=M.addresses(3)
for n,a in enumerate(leafs):v+=lab(2.2+(n+.5)*1.25,4.25,'$'+a+'$')
for row,(name,cut) in enumerate([('complete',('0','10','11')),('overlap',('0','00','1')),('gap',('00','01','10'))]):
    y=3.25-row*1.25;v+=lab(.2,y+.3,name,'anchor=west')
    for i,a in enumerate(cut):
        left=2.2+int(a,2)/2**len(a)*10;width=10/2**len(a)
        off=.27 if row==1 and a=='00' else 0
        v+=cell(left,y+off,width,.55,'$'+a+'$',22)
    v+=line(2.2,y-.15,12.2,y-.15,'black!25')
v+=lab(7.2,-.3,'each terminal packet path must be covered exactly once')
save('complete_cuts',v)
# V13 exact DP on actual 15-node tree with costs and chosen cut.
val,chosen=M.optimum();positions={}
for depth in range(4):
    for k,a in enumerate(M.addresses(depth)):positions[a]=(.8+(k+.5)*11.4/(2**depth),4.7-depth*1.25)
v=''
for a,(x,y) in positions.items():
    if a:v+=line(*positions[a[:-1]],x,y,'black!35')
for a,(x,y) in positions.items():
    c=M.COSTS[a];vv=M.optimum(a)[0]
    v+=rf'\node[draw,fill=black!{18 if a in chosen else 0},line width={.9 if a in chosen else .35}pt,inner sep=2pt,font=\sffamily\scriptsize,align=center] at ({x:.4f},{y:.4f}) {{$'+(a or r'\varnothing')+rf'$\\ ${c}\,|\,{vv}$}};'+'\n'
v+=lab(6.5,-.15,r'node labels: stop cost $c_v$ $|$ optimal subtree cost $V(v)$')
save('dynamic_program',v)
# V14 exhaustive values and strict margin.
ranks=M.ranked_prunings();v,p=chart(.6,.9,7.4,3.5,(0,25),(8,21),[(0,'0'),(5,'5'),(10,'10'),(15,'15'),(20,'20'),(25,'25')],[(9,'9'),(10,'10'),(15,'15'),(20,'20')])
v+=curve(p,[(i,a) for i,(a,_) in enumerate(ranks)],'black!40,line width=.6pt')
for i,(a,_) in enumerate(ranks):v+=dot(*p(i,a),rad=.045)
v+=lab(4.3,4.85,'all 26 complete pruning costs')
v+=lab(10.45,4.2,r'$\Gamma=10-9=1$')+lab(10.45,3.05,r'$E(\varnothing)=8/32$')+lab(10.45,1.9,r'$2E=1/2<\Gamma$')+lab(10.45,.75,'selector certified stable')
v+=lab(4.3,.12,'pruning rank')
save('selector_margin',v)
# V15 exact known packet vs smoothing whole signal.
v,p=chart(.65,.9,11.7,3.5,(-.4,15.4),(-.85,3.9),[(0,'0'),(4,'4'),(8,'8'),(12,'12'),(15,'15')],[(0,'0'),(1,'1'),(2,'2'),(3,'3')])
v+=curve(p,list(enumerate(M.SIGNAL)),'line width=.7pt')
v+=curve(p,list(enumerate(M.smooth_periodic(M.SIGNAL))),'dashed,line width=1pt')
v+=stems(p,list(enumerate(M.smooth_periodic(M.SMOOTH)+M.JUMP)),'black!45,line width=.45pt',True)
v+=lab(6.5,4.8,r'solid: $f$\quad dashed: $Qf$\quad open: $Qs+j$')+lab(6.5,.1,'periodic 16-sample model; $Q=(S^{-1}+2I+S)/4$')
save('known_edge',v)
# V16 actual Fourier pulse partial sum; one chart.
def partial(x,m):return .5+2/math.pi*sum(math.sin(math.pi*n/2)/n*math.cos(2*math.pi*n*x) for n in range(1,m+1))
v,p=chart(.65,.8,11.7,3.8,(-.5,.5),(-.2,1.25),[(-.5,'$-1/2$'),(-.25,'$-1/4$'),(0,'$0$'),(.25,'$1/4$'),(.5,'$1/2$')],[(0,'0'),(.5,'$1/2$'),(1,'1')])
v+=curve(p,[(-.5,0),(-.25,0),(-.25,1),(.25,1),(.25,0),(.5,0)],'black!60,line width=1.35pt')
xs=[-.5+i/500 for i in range(501)]
v+=curve(p,[(x,partial(x,5)) for x in xs],'dashed,line width=.95pt')+curve(p,[(x,partial(x,15)) for x in xs],'line width=.8pt')
for x in [-.25,.25]:v+=dot(*p(x,.5),rad=.065)
v+=lab(6.5,5.03,'pulse, cutoff $m=5$ (dashed), cutoff $m=15$ (thin solid)')+lab(6.5,.05,r'$2m+1$ signed frequency bins; marked values are exactly $1/2$')
save('fourier_jump',v)
# V17 translated interval and exact norms.
v='';base=1.0;scale=11.5
for row,title in enumerate([r'$\Omega$',r'$\widehat\Omega$',r'$\Omega\triangle\widehat\Omega$']):
    y=3.5-row*1.1;v+=lab(.65,y+.28,title,'anchor=east');v+=line(base,y-.1,base+scale,y-.1,'black!25')
    intervals=[(Q(1,4),Q(3,4))] if row==0 else ([(Q(5,16),Q(13,16))] if row==1 else [(Q(1,4),Q(5,16)),(Q(3,4),Q(13,16))])
    for a,b in intervals:v+=cell(base+float(a)*scale,y,float(b-a)*scale,.56,'',30 if row==2 else 14)
for a in [0,Q(1,4),Q(5,16),Q(3,4),Q(13,16),1]:v+=lab(base+float(a)*scale,.37,tex(a),r'font=\sffamily\scriptsize')
v+=lab(6.7,4.6,r'$\delta=1/16,\qquad\mu(\Omega\triangle\widehat\Omega)=2\delta=1/8$')
v+=lab(6.7,-.28,r'$\|j-\widehat j\|_1=3/8,\qquad\|j-\widehat j\|_2^2=9/8,\qquad\|j-\widehat j\|_\infty=3$')
save('mask_translation',v)
# V18 finite mask and amplitude error by sample, plus exact L1 decomposition.
A=set(range(6,12));B=set(range(7,13));v=''
for row,(title,func) in enumerate([('$j$',lambda n:3*int(n in A)),(r'$\widehat j$',lambda n:Q(5,2)*int(n in B)),(r'$j-\widehat j$',lambda n:3*int(n in A)-Q(5,2)*int(n in B))]):
    y=3.55-row*1.05;v+=lab(.7,y+.31,title,'anchor=east')
    for n in range(4,15):v+=cell(1.1+(n-4)*1.02,y,1.02,.64,tex(func(n)),20 if func(n)!=0 else 0)
for n in range(4,15):v+=lab(1.61+(n-4)*1.02,.5,str(n),r'font=\sffamily\footnotesize')
v+=lab(6.6,4.6,r'$a=3,\quad\widehat a=5/2,\quad |\Omega|=6,\quad|\Omega\triangle\widehat\Omega|=2$')
v+=lab(6.6,-.1,r'$\|j-\widehat j\|_1=3+5(1/2)+5/2=8$')
save('error_budget',v)
# V19 exact 8x8 mask shifts and a noisy boundary ambiguity.
ca,cb=M.circle_masks();v=''
for q,(title,mask) in enumerate([(r'$\Omega$',ca),(r'$\widehat\Omega$',cb),(r'$\Omega\triangle\widehat\Omega$',ca^cb)]):
    ox=.6+q*4.3;v+=lab(ox+1.7,4.5,title)
    for i in range(8):
        for j in range(8):v+=cell(ox+i*.42,.65+j*.42,.42,.42,'',38 if (i,j) in mask else 0)
    v+=lab(ox+1.7,.12,f'{len(mask)} pixels')
save('mask_geometry',v)
# V20 product conventions side by side with actual polynomials.
v=lab(3,4.6,'POINTWISE SIGNAL PRODUCT')+lab(9.7,4.6,'CAUCHY COEFFICIENT PRODUCT')
for row,mask in enumerate([lambda n:n%2==0,lambda n:n%2==1]):
    for n in range(6):v+=cell(.4+n*.84,3.25-row*.9,.84,.6,tex(n) if mask(n) else '',20 if mask(n) else 0)
v+=lab(2.9,1.6,r'$(P_{2,0}x)\,(P_{2,1}y)=0$')
for i in range(3):
    for j in range(3):v+=cell(7.3+j*1.5,3.6-i*.78,1.5,.78,'$'+str((i+j)%3)+'$',22 if (i+j)%3==0 else 0)
v+=lab(9.5,.7,r'output label $(i+j)\bmod 3$')+line(6.25,.5,6.25,4.8,'black!25')
v+=lab(6.3,-.2,r'$A=1+2t+3t^2,\ B=2+t^2:\qquad P_{3,0}(AB)=2+2t^3$')
save('product_conventions',v)
# V21 nonlinear phase coordinates and exact local values.
v=lab(6.5,4.6,r'$F(x)[n]=x[n]+\tfrac12x[n]x[n-1]$')
v+=cell(.6,2.7,5.7,1.0,r'$F_0[n]=e[n]+\tfrac12e[n]o[n-1]$',10)
v+=cell(6.8,2.7,5.7,1.0,r'$F_1[n]=o[n]+\tfrac12o[n]e[n]$',10)
v+=lab(3.45,1.65,r'$e[1]=1/2,\quad o[0]=1/4$')+lab(9.65,1.65,r'$o[1]=1/4,\quad e[1]=1/2$')
v+=lab(3.45,.65,r'$F(x)[2]=9/16$')+lab(9.65,.65,r'$F(x)[3]=5/16$')
v+=lab(6.5,-.2,'phase wrap changes the neighbor address; it does not remove the mixed term')
save('nonlinear_shift',v)
# V22 exact Cayley orbit with metric coordinates on both planes.
v='';cx,cy=2.85,2.8
v+=line(cx-2,cy,cx+2.15,cy,'->')+line(cx,cy-2,cx,cy+2.15,'->')
for rad in [1.6,.8]:v+=rf'\draw[black!35] ({cx},{cy}) circle ({rad});'+'\n'
for k,txt in enumerate([r'$1/2$',r'$i/2$',r'$-1/2$',r'$-i/2$']):
    a=k*math.pi/2;v+=dot(cx+.8*math.cos(a),cy+.8*math.sin(a),rad=.06)+lab(cx+1.15*math.cos(a),cy+1.15*math.sin(a),txt,r'font=\sffamily\footnotesize,fill=white,inner sep=1pt')
v+=lab(cx,5.6,r'reflection coordinate $\Gamma$')
vv,p=chart(7.3,.5,4.8,4.5,(0,3.2),(-1.5,1.5),[(0,'0'),(1,'1'),(2,'2'),(3,'3')],[(-1,'$-i$'),(0,'0'),(1,'$i$')]);v+=vv
zz=[(3,0),(.6,.8),(1/3,0),(.6,-.8)]
v+=curve(p,[(5/3+4/3*math.cos(k*2*math.pi/240),4/3*math.sin(k*2*math.pi/240)) for k in range(241)],'black!45,line width=.7pt')
for x,y in zz:v+=dot(*p(x,y),rad=.065)
v+=lab(9.8,5.6,'normalized impedance $z$')+lab(6.4,-.4,r'$3,\quad \tfrac35+\tfrac45i,\quad\tfrac13,\quad\tfrac35-\tfrac45i$')
save('cayley_orbit',v)
# V23 homogeneous pairs, including pole.
v=''
items=[(r'$[0:1]$',r'$z=0$',r'$\Gamma=-1$'),(r'$[-i:1]$',r'$z=-i$',r'$\Gamma=-i$'),(r'$[1:0]$',r'$z=\infty$',r'$\Gamma=1$'),(r'$[i:1]$',r'$z=i$',r'$\Gamma=i$')]
for k,(a,b,c) in enumerate(items):
    ox=.25+k*3.35;v+=cell(ox,2.7,2.8,1.0,a,20 if k==2 else 4)+lab(ox+1.4,1.95,b)+lab(ox+1.4,1.05,c)
    if k<3:v+=line(ox+2.85,3.2,ox+3.25,3.2,'->')
v+=lab(6.6,4.55,r'$A(i)=\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix}$')
v+=lab(6.6,.1,r'$A(i)^4=I:\quad$ the fourth step returns to $[0:1]$')
save('projective_poles',v)
# V24 actual CRT label table and nested disk samples.
v='';x0=.7;y0=4.2
for r in range(4):
    v+=lab(x0-.2,y0-(r+.5)*.8,str(r),'anchor=east')
    for j in range(3):
        k=next(n for n in range(12) if n%4==r and n%3==j)
        v+=cell(x0+j*1.2,y0-(r+1)*.8,1.2,.8,str(k),20 if k%3==0 else 0)
for j in range(3):v+=lab(x0+(j+.5)*1.2,y0+.35,str(j))
v+=lab(2.5,.32,r'row $j\bmod4$, column $j\bmod3$')
cx,cy=9,2.6;v+=rf'\draw[black!35] ({cx},{cy}) circle (1.65);'+'\n'
for k in range(12):
    a=k*math.pi/6;v+=dot(cx+1.65*math.cos(a),cy+1.65*math.sin(a),'fill=black' if k%3==0 else 'fill=white',.075 if k%3==0 else .05)
    v+=lab(cx+2.05*math.cos(a),cy+2.05*math.sin(a),str(k),r'font=\sffamily\scriptsize')
v+=lab(9,-.08,'filled: the four coarse rays; open: the eight new rays')
save('crt_refinement',v)
# V25 symmetric coordinate sensitivity, not claimed optimality.
v,p=chart(.65,.85,7.55,3.55,(-.96,.96),(0,3),[(-.9,'$-.9$'),(-.5,'$-.5$'),(0,'0'),(.5,'$.5$'),(.9,'$.9$')],[(0,'$1$'),(1,'$10$'),(2,'$100$'),(3,'$1000$')])
xs=[-.95+i*1.9/400 for i in range(401)]
v+=curve(p,[(g,math.log10(1/(1-g)**2+1/(1+g)**2)) for g in xs])
v+=lab(4.4,4.9,r'symmetric sensitivity $w_{\rm Smith}$ (log scale)')
for row,(g,d) in enumerate([(r'$1/2$','8'),(r'$9/10$','200'),(r'$99/100$','20000')]):
    v+=lab(9.55,3.85-row*.95,g)+lab(11.8,3.85-row*.95,d)
v+=lab(9.55,4.7,r'$\Gamma$')+lab(11.8,4.7,r'$|dz/d\Gamma|$')
v+=lab(10.7,.55,r'$\Delta z=20/9\ne2$')+lab(4.4,.1,r'real reflection coefficient $\Gamma$')
save('sensitivity',v)
(OUT/'PLATE_INDEX.json').write_text(json.dumps({'plates':plates,'count':len(plates),'arithmetic':'Exact symbolic labels; float display coordinates only.'},indent=2)+'\n')
print('Generated',len(plates),'editable vector plates')
