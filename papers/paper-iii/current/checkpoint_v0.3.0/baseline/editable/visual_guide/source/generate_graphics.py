#!/usr/bin/env python3
"""Generate 22 deterministic, editable TikZ plates from the exact models.

No artwork or external images. Integers and rationals are computed in models.py.
Only the display coordinates of vector drawings use floating point.
"""
from __future__ import annotations
from pathlib import Path
from itertools import product
import os
import tempfile
import time
import sympy as sp
import models as M
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics';OUT.mkdir(exist_ok=True)
plates=[]

def lab(x,y,text,opts=''):
    return rf'\node[{opts}] at ({float(x):.5f},{float(y):.5f}) {{{text}}};'+'\n'

def line(x1,y1,x2,y2,opts=''):
    return rf'\draw[{opts}] ({float(x1):.5f},{float(y1):.5f}) -- ({float(x2):.5f},{float(y2):.5f});'+'\n'

def cell(x,y,w,h,text='',shade=0,opts=''):
    result=rf'\draw[fill=black!{shade},draw=black!40,line width=.35pt,{opts}] ({float(x):.5f},{float(y):.5f}) rectangle ++({float(w):.5f},{float(h):.5f});'+'\n'
    if text:result+=lab(x+w/2,y+h/2,text,'text=white' if shade>65 else '')
    return result

def matrix(a,x,y,c=.62,title='',zero='0',high=None):
    a=sp.Matrix(a);result=''
    if title:result+=lab(x+a.cols*c/2,y+.55,title)
    for i in range(a.rows):
        for j in range(a.cols):
            v=a[i,j];txt='$'+sp.latex(v)+'$' if v else ('$0$' if zero=='0' else r'$\cdot$')
            result+=cell(x+j*c,y-(i+1)*c,c,c,txt,28 if high==(i,j) else 12 if v else 0)
    return result

def vertex(x,y,name,opts=''):
    return lab(x,y,name,'circle,draw,fill=white,minimum size=7mm,inner sep=1pt,'+opts)

def edge(x1,y1,x2,y2,text='',bend=None,opts=''):
    if bend:
        return rf'\draw[->,line width=.85pt,shorten <=4mm,shorten >=4mm,{opts}] ({x1},{y1}) to[bend left={bend}] node[sloped,above,font=\sffamily\footnotesize] {{{text}}} ({x2},{y2});'+'\n'
    return rf'\draw[->,line width=.85pt,shorten <=4mm,shorten >=4mm,{opts}] ({x1},{y1}) -- node[sloped,above,font=\sffamily\footnotesize] {{{text}}} ({x2},{y2});'+'\n'

def polygon(points,opts=''):
    return r'\draw['+opts+'] '+' -- '.join(f'({float(a):.5f},{float(b):.5f})' for a,b in points)+' -- cycle;\n'

def shear_plot(x,y,a=1,scale=1.35,title=''):
    # Exact image of the unit square under [[1,a],[0,1]].
    result=''
    result+=line(x-.2,y,x+(a+1)*scale+.3,y,'->,black!55')+line(x,y-.15,x,y+scale+.45,'->,black!55')
    result+=polygon([(x,y),(x+scale,y),(x+scale,y+scale),(x,y+scale)],'dashed,black!55')
    pts=[(x,y),(x+scale,y),(x+(1+a)*scale,y+scale),(x+a*scale,y+scale)]
    result+=polygon(pts,'fill=black!10,line width=1pt')
    result+=line(x,y,x+a*scale,y+scale,'->,line width=1.4pt')
    result+=lab(x+(a+1)*scale/2,y+scale+.95,title,r'font=\sffamily\bfseries')
    result+=lab(x+a*scale+.12,y+scale+.22,rf'$({a},1)$','anchor=west')
    return result

def save(name,s):
    destination=OUT/f'{name}.tex'
    old_mtime=destination.stat().st_mtime if destination.exists() else 0
    fd,temporary=tempfile.mkstemp(prefix=destination.name+'.',dir=OUT)
    os.close(fd)
    Path(temporary).write_text(r'\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,font=\sffamily\small,line cap=round,line join=round]'+'\n'+s+'\\end{tikzpicture}\n')
    os.replace(temporary,destination)
    stamp=max(time.time(),old_mtime+2)
    os.utime(destination,(stamp,stamp))
    plates.append(name)

# V1. Concrete previews of the three structures, rather than a process chart.
s=lab(2.0,3.7,r'EDGE\\ACTION',r'font=\sffamily\bfseries\footnotesize,align=center')+lab(6.5,3.7,r'EXACT\\COORDINATES',r'font=\sffamily\bfseries\footnotesize,align=center')+lab(11,3.7,r'CHOSEN\\CONNECTION',r'font=\sffamily\bfseries\footnotesize,align=center')
s+=matrix(sp.Matrix([[0,0,0],[2,0,0],[0,0,0]]),.8,2.85,.7)
s+=lab(1.85,-.05,r'$e_0\longmapsto2e_1$')
s+=lab(6.5,2.7,r'$(3,2)$')+lab(5.0,1.3,r'$(1,2)$')+lab(8,1.3,r'$(3/2,1/2)$')
s+=line(6.05,2.5,5.15,1.65,'->')+line(5.6,1.3,7.1,1.3,'->')+line(7.9,1.65,6.95,2.5,'->')
s+=lab(6.5,-.05,'one unchanged ambient vector')
s+=shear_plot(9.5,.45,1,1.05,'')+lab(11,-.05,r'$H=\begin{psmallmatrix}1&1\\0&1\end{psmallmatrix}\ne I$')
s+=line(4,-.35,4,3.95,'black!25')+line(9,-.35,9,3.95,'black!25')
save('three_structures',s)

# V3. Edge support and multiplication order.
e=M.Edge('e',0,1,2);f=M.Edge('f',1,2,3);le=M.edge_matrix(3,e);lf=M.edge_matrix(3,f)
s=''
for x,a,title in [(0,le,r'$L_e$'),(4.2,lf,r'$L_f$'),(8.4,lf*le,r'$L_fL_e$')]:
    s+=matrix(a,x,3.7,.72,title)
    for k in range(3):s+=lab(x+(k+.5)*.72,3.95,rf'${k}$',r'font=\sffamily\scriptsize')
    for k in range(3):s+=lab(x-.24,3.7-(k+.5)*.72,rf'${k}$',r'font=\sffamily\scriptsize')
s+=lab(5.3,.65,'row = target / column = source')
s+=vertex(1.1,-.3,'$0$')+vertex(5.3,-.3,'$1$')+vertex(9.5,-.3,'$2$')
s+=edge(1.1,-.3,5.3,-.3,r'$e:2$')+edge(5.3,-.3,9.5,-.3,r'$f:3$')
s+=lab(5.3,-1.2,r'$e\text{ first},\ f\text{ second};\qquad L_eL_f=0$')
save('edge_orientation',s)

# V4. Every length-two edge word, including parallel labels.
p=M.parallel_model();edges=p['edges'];s=''
pts={0:(.6,1.8),1:(4.7,1.8),2:(2.65,4.2)}
for i,pt in pts.items():s+=vertex(*pt,f'${i}$')
s+=edge(*pts[0],*pts[1],r'$a:2$',bend=18)+edge(*pts[0],*pts[1],r'$b:-1$',bend=-18)
s+=edge(*pts[1],*pts[2],r'$c:3$')+edge(*pts[2],*pts[0],r'$d:1$')
s+=lab(2.65,.5,r'$(T^2)_{20}=6-3=3$')
x0=7;y0=4.6;c=.9
for j,e0 in enumerate(edges):s+=lab(x0+(j+.5)*c,y0+.4,rf'${e0.name}$')
for i,f0 in enumerate(edges):
    s+=lab(x0-.3,y0-(i+.5)*c,rf'${f0.name}$')
    for j,e0 in enumerate(edges):
        good=M.composable((e0,f0));value=M.word_coefficient((e0,f0))
        s+=cell(x0+j*c,y0-(i+1)*c,c,c,'$'+sp.latex(value)+'$' if good else r'$\times$',22 if good else 0)
s+=lab(8.8,5.5,'first executed edge = column')+lab(8.8,.35,'second executed edge = row')
s+=lab(8.8,-.15,r'$\times$: broken packet interface')
save('all_word_interfaces',s)

# V5. Noncommutative coefficients kept in their actual order.
a=M.noncommutative_model();s=''
for x,key,title in [(0,'A','$A$'),(3.5,'B','$B$'),(7,'BA','$BA$'),(10.5,'AB','$AB$')]:
    s+=matrix(a[key],x,3.1,.7,title)
s+=line(9.55,.5,9.55,4,'black!30')
s+=lab(6.0,.15,r'$e:0\to1\text{ carries }A;\quad f:1\to2\text{ carries }B$')
s+=lab(6,-.65,r'$BA(1,0)^{\mathsf T}=(1,1)^{\mathsf T},\qquad AB(1,0)^{\mathsf T}=(2,1)^{\mathsf T}$')
save('ordered_matrix_coefficients',s)

# V6. Two real paths whose operator values cancel exactly.
s='';pts={0:(.7,2.2),1:(3.4,3.75),2:(3.4,.65),3:(6.1,2.2)}
for i,pt in pts.items():s+=vertex(*pt,f'${i}$')
for u,v,w in [(0,1,1),(0,2,1),(1,3,1),(2,3,-1)]:s+=edge(*pts[u],*pts[v],f'${w}$',opts='dashed' if w<0 else '')
s+=lab(3.4,4.7,'two walks of length two')
s+=line(7,-.1,7,4.75,'black!30')
s+=cell(8.2,3.4,3.0,.65,'unsigned count: $2$',10)
s+=cell(8.2,2.25,3.0,.65,r'upper route: $+1$',14)
s+=cell(8.2,1.1,3.0,.65,r'lower route: $-1$',14)
s+=lab(9.7,.2,r'$(T^2)_{30}=0$')
save('walk_cancellation',s)

# V7. Orbit columns and reachable coordinate support are different objects.
d=M.diamond_model();e0=sp.eye(5)[:,0];kry=sp.Matrix.hstack(e0,d['T']*e0,d['T']**2*e0)
s=matrix(kry,0,4.1,.69,title=r'$[e_0\ \ Te_0\ \ T^2e_0]$')
for i in range(5):s+=lab(-.3,4.1-(i+.5)*.69,f'${i}$')
s+=lab(1.05,-.15,r'rank $=2$')
s+=matrix(sp.Matrix([[1,0],[0,1],[0,1],[0,0],[0,0]]),4.0,4.1,.69,title='a basis of the orbit hull')
s+=lab(8.85,3.8,r'$\operatorname{Reach}(0)=\{0,1,2,3\}$')
s+=lab(8.85,2.75,r'$\operatorname{Hull}_T(e_0)=\{(a,b,b,0,0)\}$')
s+=lab(8.85,1.65,r'$e_3:\ \text{reachable but absent}$')
s+=lab(8.85,.6,r'$e_4:\ \text{unreachable and absent}$')
save('orbit_support',s)

# V8. A genuinely rectangular three-step example.
r=M.rectangular_model();s=''
for x,key,title in [(0,'A',r'$A:\QQ^2\to\QQ^3$'),(3.35,'B',r'$B:\QQ^3\to\QQ^2$'),(7.5,'C',r'$C:\QQ^2\to\QQ$')]:
    s+=matrix(r[key],x,4.0,.65,title)
s+=matrix(r['CBA'],10.4,4.0,.7,title='$CBA$')
headers=[r'$(j,k)=(0,0)$',r'$(0,1)$',r'$(0,2)$',r'$(1,0)$',r'$(1,1)$',r'$(1,2)$']
for col,h in enumerate(headers):s+=lab(1.35+col*1.65,1.35,h,r'font=\sffamily\footnotesize')
for row,vals in enumerate(r['contributions']):
    yy=.3-row*.7;s+=lab(-.05,yy+.27,f'$i={row}$','anchor=east')
    for col,val in enumerate(vals):s+=cell(.53+col*1.65,yy,1.65,.54,'$'+sp.latex(val)+'$',12 if val else 0)
    s+=lab(11.3,yy+.27,'$='+sp.latex(sum(vals))+'$')
save('rectangular_paths',s)

# V9. One ambient point in three actual coordinate planes.
fr=M.frame_model();s=''
for i,z in enumerate(fr['coordinates']):
    ox=.4+i*4.4;oy=.4;scale=.8
    for xx in range(4):s+=line(ox+xx*scale,oy,ox+xx*scale,oy+2.5*scale,'black!14')
    for yy in range(3):s+=line(ox,oy+yy*scale,ox+3.5*scale,oy+yy*scale,'black!14')
    s+=line(ox-.1,oy,ox+3.7*scale,oy,'->')+line(ox,oy-.1,ox,oy+2.8*scale,'->')
    s+=line(ox,oy,ox+float(z[0])*scale,oy+float(z[1])*scale,'->,line width=1.2pt')
    s+=lab(ox+1.45,3.55,rf'chart ${i}$',r'font=\sffamily\bfseries')
    s+=lab(ox+1.45,2.97,'$('+','.join(sp.latex(v) for v in z)+')$')
    s+=lab(ox+1.45,-.35,rf'$F_{i}u_{i}=(3,2)^\mathsf T$')
save('frame_coordinates',s)

# V10. The exact nonlinear shear maps a square to a curved band.
s=lab(2.1,4.45,r'$(x,y)$ chart',r'font=\sffamily\bfseries')+lab(9,4.45,r'$(u,v)=(x,y+x^2)$ chart',r'font=\sffamily\bfseries')
s+=line(.5,.3,4,.3,'->')+line(.5,.3,.5,3.8,'->')
s+=cell(.5,.3,2.8,2.8,'',12)
for h in [0,.25,.5,.75,1]:s+=line(.5,.3+2.8*h,3.3,.3+2.8*h,'black!40')
s+=lab(2.1,-.4,r'$0\le x,y\le1$')
s+=line(7,.3,11.1,.3,'->')+line(7,.3,7,3.9,'->')
for j in range(5):
    pts=[(7+3*float(sp.Rational(i,24)),.3+1.5*float(sp.Rational(j,4)+sp.Rational(i,24)**2)) for i in range(25)]
    path=' -- '.join(f'({a:.5f},{b:.5f})' for a,b in pts)
    s+='\\draw['+('line width=1pt' if j in [0,4] else 'black!50')+'] '+path+';\n'
s+=line(7,.3,7,1.8,'line width=1pt')+line(10,1.8,10,3.3,'line width=1pt')
s+=lab(9,-.4,r'$u^2\le v\le1+u^2$')
s+=lab(5.3,2.05,r'$\mathcal A$')
save('nonlinear_exact_chart',s)

# V11. Reverse normalization is a substantive hypothesis.
s='';rows=[('self normalization only',sp.Rational(1,6)),('reversible',sp.Rational(1,5))]
headers=['connection data',r'$\Gamma_{0\leftarrow2}$',r'$H$',r'$D^\times$',r'$\Gamma_{0\leftarrow2}\Gamma_{2\leftarrow0}$']
xs=[0,4.0,6.0,7.8,9.6];width=[4,2,1.8,1.8,3.1]
for x,w,h in zip(xs,width,headers):s+=cell(x,3.65,w,.75,h,10)
for row,(name,back) in enumerate(rows):
    g=M.scalar_connection(back);vals=[name,'$'+sp.latex(back)+'$','$'+sp.latex(M.loop(g,0,1,2))+'$',r'$6/5$','$'+sp.latex(back*5)+'$']
    yy=2.7-row*1.0
    for x,w,v in zip(xs,width,vals):s+=cell(x,yy,w,.8,v,0)
s+=lab(6.35,.5,r'$\Gamma_{1\leftarrow0}=2,\quad\Gamma_{2\leftarrow1}=3,\quad\Gamma_{2\leftarrow0}=5$')
s+=lab(6.35,-.2,'The first row has H = identity at this triangle, but fails its cocycle.')
save('reverse_hypothesis',s)

# V12. A reversible scalar triangle with incompatible routes.
s='';pts={0:(1,1),1:(5,1),2:(3,4)}
for i,p in pts.items():s+=vertex(*p,f'${i}$')
s+=edge(*pts[0],*pts[1],r'$2$')+edge(*pts[1],*pts[2],r'$3$')
s+=edge(*pts[0],*pts[2],r'$5$',opts='dashed')
s+=lab(3,4.8,r'reverse of direct edge: $1/5$')
s+=lab(3,.0,'forward routes: 5 versus 6')
s+=line(6,-.35,6,4.6,'black!25')
s+=lab(9.0,4.7,r'loop input $1$ returns $6/5$',r'font=\sffamily\bfseries')
for n in range(5):
    s+=cell(7.0,3.1-n*.78,1,.66,f'${n}$',8)+cell(8.0,3.1-n*.78,3,.66,'$'+sp.latex(sp.Rational(6,5)**n)+'$',16)
s+=lab(7.5,4.08,'loops')+lab(9.5,4.08,'returned value')
save('scalar_holonomy',s)

# V13. Shear is not identity even with identical trace, determinant and eigenvalues.
s=shear_plot(.6,.4,1,1.4,'The unit square under H')
s+=matrix(M.shear_model()['H'],6.2,3.0,.75,title='$H$')
s+=matrix(M.shear_model()['Ob'],9.7,3.0,.75,title='$H-I$')
s+=lab(8.7,.2,r'$\operatorname{tr}H=2,\quad\det H=1,\quad(H-I)e_1=e_0$')
save('shear_holonomy',s)

# V14. Gauge preserves obstruction, but not its numerical size in a chosen norm.
s=shear_plot(.4,.4,1,1.2,r'$H$')+shear_plot(6.7,.4,2,1.2,r'$DHD^{-1},\quad D=\operatorname{diag}(2,1)$')
s+=lab(2.2,-.3,r'$\|H-I\|_F^2=1$')+lab(8.7,-.3,r'$\|D(H-I)D^{-1}\|_F^2=4$')
s+=line(5.65,-.6,5.65,3.65,'black!25')
save('gauge_size',s)

# V15. A flat scalar pair connection need not equal the canonical identity.
s=''
for i,g in enumerate([1,2,3]):
    yy=3.4-i*1.15;s+=lab(.2,yy,rf'chart ${i}$','anchor=west')
    s+=line(2.2,yy,11,yy,'->,black!50')
    for n in range(4):
        xx=2.2+n*.8*g
        s+=line(xx,yy-.13,xx,yy+.13)+lab(xx,yy-.4,f'${n}$',r'font=\sffamily\scriptsize')
    s+=lab(12,yy,rf'$g_{i}={g}$')
s+=lab(6.3,-.3,r'$\Gamma_{1\leftarrow0}=2,\quad \Gamma_{2\leftarrow1}=3/2,\quad\Gamma_{2\leftarrow0}=3$')
save('flat_not_calibrated',s)

# V16. Every nonzero holonomy block gets an actual source-output label.
b=M.block_model();s=matrix(b['H'],0,3.75,.65,title='$H$')+matrix(b['Ob'],3.5,3.75,.65,title=r'$\Ob=H-I$')
for i in range(3):
    for j in range(3):
        xx=7+j*1.35;yy=3.15-i*1.05
        v=b['Ob'][i,j]
        s+=cell(xx,yy,1.25,.82,rf'${sp.latex(v)}E_{{{i}{j}}}$' if v else '$0$',25 if v else 0)
for j in range(3):s+=lab(7+.625+j*1.35,4.45,rf'$\nu={j}$',r'font=\sffamily\footnotesize')
for i in range(3):s+=lab(6.75,3.56-i*1.05,rf'$\mu={i}$',r'anchor=east,font=\sffamily\footnotesize')
s+=lab(2.75,.2,r'$\Ob(4,5,6)^\mathsf T=(10,18,0)^\mathsf T$')+lab(9,.2,'sum all nine blocks')
save('all_obstruction_blocks',s)

# V17. Incomplete versus complete and oblique packet resolutions.
sh=M.shear_model();ob=sh['Ob'];Q=sh['Q'];s=matrix(ob,0,3.7,.68,title=r'$\Ob$')
s+=matrix(sp.zeros(2),3.2,3.7,.68,title=r'$\sum_iP_i\Ob P_i$')
s+=lab(.68,.85,'nonzero',r'font=\sffamily\footnotesize')+lab(3.88,.85,r'diagonal test\\misses it',r'align=center,font=\sffamily\footnotesize')
s+=line(5.8,.4,5.8,4.4,'black!30')
s+=matrix(Q[0],6.7,3.7,.68,title='$Q_0$')+matrix(Q[1],10.0,3.7,.68,title='$Q_1$')
s+=lab(9.0,.85,r'$Q_0+Q_1=I,\quad Q_i^2=Q_i$')
s+=lab(6,-.1,r'$\sum_{i,j}Q_i\Ob Q_j=\Ob;\qquad Q_0^{\mathsf T}\ne Q_0$')
save('complete_not_just_diagonal',s)

# V18. Fixed labels do not survive a packet-mixing gauge.
s=matrix(sh['Ob'],0,3.2,.85,title=r'$\Ob$')+matrix(sh['G'],4.25,3.2,.85,title='$G$')+matrix(sh['Hm']-sp.eye(2),8.5,3.2,.85,title=r'$G\Ob G^{-1}$')
s+=lab(.85,.65,'one nonzero entry')+lab(5.1,.65,r'$GP_0\ne P_0G$')+lab(9.35,.65,'four nonzero entries')
s+=lab(5.5,-.2,r'fixed axes: different packet pattern / moving axes: conjugate labeled blocks')
save('mixing_gauge_patterns',s)

# V19. The residual of one candidate is not a theorem about every candidate.
s='';vals=[-2,-1,0,1,2]
for i,v in enumerate(vals):
    xx=2.5+i*1.8;s+=cell(xx,3.8,1.8,.6,f'${v}$',10)
    for row,val in enumerate(M.candidate_residual(v)):
        s+=cell(xx,2.9-row*.9,1.8,.7,'$'+sp.latex(val)+'$',0 if val==0 else 22)
    s+=lab(xx+.9,.55,'solution' if v==1 else 'rejected',r'font=\sffamily\footnotesize')
s+=lab(2.2,4.1,'candidate $x$','anchor=east')+lab(2.2,3.25,r'$r(x,0)=x^2-1$','anchor=east')+lab(2.2,2.35,r'$r(x,1)=x-1$','anchor=east')
s+=lab(7, -.1,r'$x=-1:\quad r(-1,0)=0,\quad r(-1,1)=-2$')
save('candidate_residual_table',s)

# V20. An actual syntax tree with slot order and evaluated values.
s='';nodes=[('r',5,4.1,r'$-\ :\ 2$'),('a',3.2,2.65,r'$+\ :\ 7$'),('y',7,2.65,r'$y=5$'),('u',1.8,1.1,r'$(\cdot)^2:\ 4$'),('c',4.6,1.1,r'$3$'),('x',1.8,-.4,r'$x=2$')]
for name,x,y,txt in nodes:s+=lab(x,y,txt,'draw,rounded corners=1pt,fill=black!4,minimum width=15mm,minimum height=7mm')
for x1,y1,x2,y2,label in [(3.2,3.0,4.65,3.75,'left'),(7,3,5.4,3.75,'right'),(1.8,1.45,2.85,2.3,''),(4.6,1.45,3.55,2.3,''),(1.8,-.05,1.8,.75,'')]:
    s+=line(x1,y1,x2,y2,'->')
    if label:s+=lab((x1+x2)/2,(y1+y2)/2+.23,label,r'font=\sffamily\scriptsize')
s+=line(8.0,-.7,8,4.5,'black!25')
s+=lab(10.2,3.7,r'$\operatorname{inputs}(t)=\{x,y\}$')
s+=lab(10.2,2.45,r'unused input: $-100$ or $100$')+lab(10.2,1.6,'same value: 2')
s+=lab(10.2,.3,r'$x-x:\ \{x\}\text{ syntactically}$')+lab(10.2,-.45,'but always zero')
save('tree_input_locality',s)

# V21. Exact polynomial route values; the canonical conjugate differs from reusing f.
s='';xx0=.6;yy0=.4
s+=line(xx0,yy0,xx0+5.2,yy0,'->')+line(xx0,yy0,xx0,yy0+4.2,'->')
for coef,opt in [(2,'line width=1pt'),(4,'line width=1pt,dashed')]:
    pts=[(xx0+2.1*float(sp.Rational(k,20)),yy0+.23*float(coef*sp.Rational(k,20)**2)) for k in range(41)]
    s+='\\draw['+opt+'] '+' -- '.join(f'({a:.4f},{b:.4f})' for a,b in pts)+';\n'
s+=lab(3.8,2.1,r'$2x^2$')+lab(3.8,4.2,r'$4x^2$')+lab(5.5,.1,'$x$')
s+=line(6.2,0,6.2,4.75,'black!25')
for row,(title,vals) in enumerate([('$x$',[0,1,2]),(r'$2f(x)$',[0,2,8]),(r'$f(2x)$',[0,4,16]),(r'$2f(x)-f(2x)$',[0,-2,-8])]):
    y=3.65-row*.85;s+=lab(8.75,y+.29,title,'anchor=east')
    for j,val in enumerate(vals):s+=cell(9+j*.87,y,.87,.58,f'${val}$',10 if row else 0)
s+=lab(9.65,-.05,r'correct chart formula: $f_b(v)=v^2/2$')
save('node_defect_not_coordinate_defect',s)

# V22. Four bilinear terms as literal rectangle areas.
s='';sx=.65;sy=.25;x=0;y=.5
# width a=2, b=3; height c=5, d=7
for col,(w,name) in enumerate([(2,'a'),(3,'b')]):
    ox=x+(0 if col==0 else 2*sx)
    for row,(h,hn) in enumerate([(5,'c'),(7,'d')]):
        oy=y+(0 if row==0 else 5*sy);value=w*h
        s+=cell(ox,oy,w*sx,h*sy,rf'${name}{hn}={value}$',10 if col==row else 25)
s+=lab(1.62,4.25,r'$(2+3)(5+7)=60$',r'font=\sffamily\bfseries')
s+=lab(.65,.15,'$a=2$')+lab(2.27,.15,'$b=3$')
s+=lab(-.25,1.1,'$c=5$','anchor=east')+lab(-.25,2.62,'$d=7$','anchor=east')
s+=line(4.1,-.3,4.1,4.65,'black!25')
s+=lab(8,4.1,'Diagonal pieces are not the whole product',r'font=\sffamily\bfseries')
s+=lab(8,3.1,r'$ac+bd=10+21=31$')+lab(8,2.25,r'$ad+bc=14+15=29$')
s+=lab(8,1.1,r'$(2+3)^2=25\ne2^2+3^2=13$')
s+=lab(8,.15,r'missing square term: $2\cdot2\cdot3=12$')
save('bilinear_vs_nonlinear',s)

# V23. One complete exact diagnosis and an actual change of connection.
c=M.capstone_model();s=''
for x,a,tit in [(0,c['A'],'$A$'),(3.0,c['B'],'$B$'),(6.0,c['H'],'$H=BA$'),(9.0,c['Ob'],'$H-I$')]:s+=matrix(a,x,3.8,.67,title=tit)
s+=lab(5.1,1.6,r'$e_0=(1,0)\ \mapsto\ (1,0)\ \mapsto\ (1,1)\ \mapsto\ (1,1)$')
s+=lab(5.1,.75,r'$P_1(H-I)e_0=e_1\ne0$')
s+=line(.0,.05,11,.05,'black!30')
s+=lab(5.1,-.6,r'replace direct edge $C=I$ by $C=BA$: then $C^{-1}BA=I$')
save('worked_holonomy_diagnosis',s)

print(f'Generated {len(plates)} editable vector plates.')
if len(plates)!=22:raise RuntimeError('Expected 22 vector plates.')
