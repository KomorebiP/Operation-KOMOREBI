#!/usr/bin/env python3
"""Generate editable monochrome TikZ plates from models.py.

Algebraic labels use exact SymPy rationals. Smooth curves are sampled with
mpmath, and use floating point only for display coordinates. Root brackets
come from independent rational Taylor certificates. No external images.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction
import json,math
import sympy as sp
import mpmath as mp
import models as M
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics';OUT.mkdir(exist_ok=True)
mp.mp.dps=50
plates=[]

def tex(a):return '$'+sp.latex(a)+'$'
def lab(x,y,t,opts=''):
    return rf'\node[{opts}] at ({float(x):.5f},{float(y):.5f}) {{{t}}};'+'\n'
def line(x1,y1,x2,y2,opts=''):
    return rf'\draw[{opts}] ({float(x1):.5f},{float(y1):.5f}) -- ({float(x2):.5f},{float(y2):.5f});'+'\n'
def dot(x,y,opts='fill=black',rad=.055):
    return rf'\draw[{opts}] ({float(x):.5f},{float(y):.5f}) circle ({rad});'+'\n'
def cell(x,y,w,h,text='',shade=0):
    t=rf'\draw[fill=black!{shade},draw=black!40,line width=.35pt] ({x:.5f},{y:.5f}) rectangle ++({w:.5f},{h:.5f});'+'\n'
    return t+(lab(x+w/2,y+h/2,text) if text else '')
def matrix(a,x,y,c=.68,title=''):
    a=sp.Matrix(a);s=lab(x+a.cols*c/2,y+.48,title) if title else ''
    for i in range(a.rows):
        for j in range(a.cols):s+=cell(x+j*c,y-(i+1)*c,c,c,tex(a[i,j]),12 if a[i,j]!=0 else 0)
    return s

def save(name,text):
    (OUT/f'{name}.tex').write_text(r'\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,font=\sffamily\small,line cap=round,line join=round]'+'\n'+text+'\\end{tikzpicture}\n')
    plates.append(name)

def chart(x0,y0,W,H,xlim,ylim,xticks,yticks):
    xa,xb=xlim;ya,yb=ylim
    def point(x,y):return x0+W*(float(x)-xa)/(xb-xa),y0+H*(float(y)-ya)/(yb-ya)
    s=''
    for x,t in xticks:
        X,_=point(x,ya);s+=line(X,y0,X,y0+H,'black!13')+lab(X,y0-.31,str(t),r'font=\sffamily\footnotesize')
    for y,t in yticks:
        _,Y=point(xa,y);s+=line(x0,Y,x0+W,Y,'black!13')+lab(x0-.16,Y,str(t),r'anchor=east,font=\sffamily\footnotesize')
    s+=line(x0,y0,x0+W+.15,y0,'->')+line(x0,y0,x0,y0+H+.15,'->')
    return s,point

def curve(point,coords,opts='line width=1pt'):
    return '\\draw['+opts+'] plot coordinates {'+' '.join(f'({point(a,b)[0]:.5f},{point(a,b)[1]:.5f})' for a,b in coords)+'};\n'

# V1: previews of concrete objects, not a flow chart.
s=''
for c,title in enumerate(['COEFFICIENT LANES','RECIPROCAL COEFFICIENTS','ZERO ORBITS']):
    s+=lab(2+4.5*c,3.9,title,r'font=\sffamily\bfseries\footnotesize')
for j in range(3):
    for n in range(4):s+=cell(.25+n*.9,2.6-j*.75,.9,.65,rf'$z^{{{3*n+j}}}$',10 if j==0 else 0)
s+=lab(2,-.1,r'$m\equiv j\pmod 3$')
s+=matrix([[1,0,0],[sp.Rational(-1,2),1,0],[sp.Rational(1,24),sp.Rational(-1,2),1]],5.1,3.2,.85)
s+=lab(6.5,-.1,r'$1,\quad\frac12,\quad\frac5{24},\ldots$')
for a in [0,math.pi/2,math.pi,3*math.pi/2]:
    s+=line(11,1.6,11+1.45*math.cos(a),1.6+1.45*math.sin(a),'black!50')
    for rad in [.7,1.35]:s+=dot(11+rad*math.cos(a),1.6+rad*math.sin(a))
s+=lab(11,-.1,r'$\{\rho,i\rho,-\rho,-i\rho\}$')
s+=line(4.25,-.4,4.25,4.1,'black!25')+line(8.7,-.4,8.7,4.1,'black!25')
save('three_views',s)
# V3: finite complex averaging for an actual polynomial.
s=lab(2.5,4.4,r'Four weighted votes for $z^m$')
for j,a in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
    s+=line(2.5,2,2.5+1.45*math.cos(a),2+1.45*math.sin(a),'->,line width=1pt')
    s+=lab(2.5+1.9*math.cos(a),2+1.9*math.sin(a),['$1$','$i$','$-1$','$-i$'][j])
s+=lab(2.5,-.3,r'$\frac14\sum_{\ell=0}^3 i^{(m-j)\ell}$')
for j in range(4):
    s+=lab(6.1,3.7-j*.85,rf'$j={j}$','anchor=east')
    for n in range(3):s+=cell(6.45+n*1.7,3.4-j*.85,1.7,.6,rf'$z^{{{4*n+j}}}$',18 if j==2 else 0)
s+=lab(9.1,-.3,'only the matching phase survives')
save('root_filter',s)
# V4: cyclic product with actual contributions.
f=1+2*M.z+3*M.z**2+M.z**3;g=2+M.z+M.z**2
s='';x0=2.4;y0=3.8;W=2.65;H=.85
for j in range(3):s+=lab(x0+(j+.5)*W,y0+.42,tex(M.project(g,3,j)))
for i in range(3):
    s+=lab(x0-.25,y0-(i+.5)*H,tex(M.project(f,3,i)),'anchor=east')
    for j in range(3):
        v=sp.expand(M.project(f,3,i)*M.project(g,3,j));s+=cell(x0+j*W,y0-(i+1)*H,W,H,tex(v),18 if (i+j)%3==0 else 0)
s+=lab(6.2,.25,r'$\mathcal B_{3,0}(FG)=2+7z^3$')
s+=lab(6.2,-.4,'shaded cells: $(0,0), (1,2), (2,1)$ all land in residue $0$')
save('cyclic_product',s)
# V5: signed shift and first jets.
J=M.signed_shift(3);D0,D1,D2=sp.symbols('D_0 D_1 D_2')
s=matrix(J,.6,3.3,.8,title='$J_3$')
s+=matrix([[D0,-D2,-D1],[D1,D0,-D2],[D2,D1,D0]],5.1,3.3,1.05,title='$e^{zJ_3}$')
s+=lab(10.8,2.9,r'$J_3^3=-I$')+lab(10.8,1.7,r'$\mathbf D_3(0)=e_0$')+lab(10.8,.6,r'$\det e^{zJ_3}=1$')
s+=lab(6.1,-.8,r'$D_0\mapsto-D_2,\qquad D_1\mapsto D_0,\qquad D_2\mapsto D_1$')
save('signed_shift',s)
# V6: multiplication table in the actual quotient algebra.
s='';heads=['$1$',r'$\xi$',r'$\xi^2$'];xx=1.1;yy=3.75;WW=2.25
for j,h in enumerate(heads):s+=lab(xx+(j+.5)*WW,yy+.35,h)
for i,h in enumerate(heads):
    s+=lab(xx-.25,yy-(i+.5)*.82,h,'anchor=east')
    for j in range(3):
        k=i+j;t=('' if k<3 else '-')+['1',r'\xi',r'\xi^2'][k%3]
        s+=cell(xx+j*WW,yy-(i+1)*.82,WW,.82,'$'+t+'$',20 if k>=3 else 0)
s+=lab(10.25,3.2,r'$\xi^3=-1$')+lab(10.25,2.1,'wrap once: change sign')+lab(10.25,1.0,r'$\xi^2\xi^2=-\xi$')
s+=lab(6.3,.15,r'$D_{3,0}(z+w)=D_{3,0}(z)D_{3,0}(w)-D_{3,1}(z)D_{3,2}(w)-D_{3,2}(z)D_{3,1}(w)$',r'font=\sffamily\footnotesize')
save('signed_addition',s)
# V7: grouping factorials into exact residue columns.
s=lab(6.4,4.5,r'$N=3,\ j=1,\ n=2:\quad 7!=1!\,3^6\,2!\,(2/3)_2(4/3)_2$')
vals=[[sp.Rational(2,3),sp.Rational(5,3)],[1,2],[sp.Rational(4,3),sp.Rational(7,3)]]
for row,vs in enumerate(vals):
    for col,v in enumerate(vs):s+=cell(.8+col*1.6,3.15-row*.9,1.6,.7,tex(v),20 if row==1 else 0)
    s+=lab(4.5,3.5-row*.9,[r'$(2/3)_2$',r'$(1)_2=2!$',r'$(4/3)_2$'][row],'anchor=west')
s+=lab(9.3,3.3,r'$A_{3,1}=\{2/3,4/3\}$')
s+=lab(9.3,2.0,r'$\displaystyle E_{3,1}(z)=z\,{}_0F_2\!\left(;\frac23,\frac43;\frac{z^3}{27}\right)$')
s+=lab(6.3,-.05,'The omitted unit parameter is already the hypergeometric $n!$.')
save('hypergeometric',s)
# V8: orbit reduction, normalized so plotted positions are exact rational data.
s='';cx,cy=2.7,2.5
for a in [0,math.pi/2,math.pi,3*math.pi/2]:
    s+=line(cx,cy,cx+2*math.cos(a),cy+2*math.sin(a),'black!45')
    for rad in [.6,1.8]:s+=dot(cx+rad*math.cos(a),cy+rad*math.sin(a))
s+=lab(cx,5.0,r'$u=z/(\sqrt2\pi)$')+lab(cx,-.3,r'$u=\tfrac12 i^k,\ \tfrac32 i^k$')
s+=line(5.3,2.5,7.0,2.5,'->,line width=.9pt')+lab(6.15,3,r'$v=u^4$')
s+=line(7.5,2.5,12.8,2.5,'->')
for xx,t in [(7.65,r'$1/16$'),(12.1,r'$81/16$')]:s+=dot(xx,2.5,rad=.09)+lab(xx,1.95,t)+lab(xx,3.1,'one zero')
s+=lab(10.2,5.0,r'$v=w/(4\pi^4)$')+lab(10.2,-.3,'four points per orbit become one')
save('orbit_reduction',s)
# V9: inverse triangular convolution.
s=matrix([[1,0,0,0],[-sp.Rational(1,2),1,0,0],[sp.Rational(1,24),-sp.Rational(1,2),1,0],[-sp.Rational(1,720),sp.Rational(1,24),-sp.Rational(1,2),1]],.8,4.15,.88,title='denominator convolution')
s+=matrix([[1],[sp.Rational(1,2)],[sp.Rational(5,24)],[sp.Rational(61,720)]],5.35,4.15,.88,title='$b$')
s+=lab(7.0,2.4,'$=$')+matrix([[1],[0],[0],[0]],7.65,4.15,.88,title='unit series')
s+=lab(10.85,3.6,r'$b_1=\frac12$')+lab(10.85,2.45,r'$b_2=\frac14-\frac1{24}$')+lab(10.85,1.2,r'$b_3=\frac{61}{720}$')
s+=lab(6.5,-.3,r'$P_{2,n}(1)=(2n)!b_n:\qquad 1,\ 1,\ 5,\ 61$')
save('triangular_inverse',s)
# V10: Bell partitions rather than a decorative tree.
s=''
for j,(sizes,title,term) in enumerate([([1,1,1],'three singletons',r'$r^3\kappa_1^3$'),([2,1],'one pair, one singleton',r'$3r^2\kappa_1\kappa_2$'),([3],'one triple',r'$2r\kappa_3$')]):
    ox=.2+j*4.35;s+=lab(ox+1.95,4.0,title,r'font=\sffamily\footnotesize')
    px=ox+.25
    for size in sizes:
        width=.66*size;s+=cell(px,2.45,width,.75,'',12)
        for k in range(size):s+=dot(px+.33+k*.66,2.82,rad=.085)
        px+=width+.16
    s+=lab(ox+1.95,1.4,term)+lab(ox+1.95,.4,[r'$15r^3$',r'$30r^2$',r'$16r$'][j])
s+=lab(6.5,-.5,r'$P_{2,3}(r)=\frac{6!}{3!}\,B_3(r\kappa_1,r\kappa_2,2r\kappa_3)$')
save('bell_partitions',s)
# V11: two recurrences + complete addition example.
s=matrix([[sp.Rational(1,2)*M.r,-1,0],[M.r/6,M.r/2,-2],[M.r/15,M.r/6,M.r/2]],.4,4.0,.95,title='$n!b_n(r)$ for $n=3$')
s+=lab(2.0,.25,r'$\det /6=P_{2,3}(r)/720$')
values=[61,75,75,61];xx=5.4
for i,v in enumerate(values):
    h=3*v/75;s+=cell(xx+i*1.65,1.0,1.05,h,str(v),16)
    s+=lab(xx+.525+i*1.65,.55,f'$q={i}$')
s+=lab(8.4,4.6,r'$P_{2,3}(2)=61+75+75+61=272$')
s+=lab(8.4,-.15,r'block weights: $1,15,15,1$')
save('newton_addition',s)
# V12: derivative cycle compressed into Riccati on the zero-free region.
s=lab(3.0,4.5,'LINEAR EQUATION')+lab(9.3,4.5,'LOGARITHMIC DERIVATIVE')
s+=lab(3,3.25,r'$D_2^{\prime\prime}=-D_2$')+lab(9.3,3.25,r'$T_2^{\prime}=1+T_2^2$')
s+=lab(3,1.85,r'$D_3^{\prime\prime\prime}=-D_3$')+lab(9.3,1.85,r'$T_3^{\prime\prime}-3T_3T_3^{\prime}+T_3^3=1$')
s+=lab(6.15,.5,r'$T_N=-D_N^{\prime}/D_N\quad\text{only where }D_N\ne0$')
s+=line(6.1,1.1,6.1,4.65,'black!25')
s+=lab(6.1,-.4,r'$T_4(z)=\frac{z^3}{3!}+34\frac{z^7}{7!}+\cdots$')
save('riccati',s)
# V13: zero-free disk and a loop around a simple zero.
s='';cx,cy=2.8,2.3
s+=rf'\draw[fill=black!4,draw=black!45] ({cx},{cy}) circle (1.6);'+'\n'
s+=line(.65,cy,5.2,cy,'->')+line(cx,.3,cx,4.4,'->')+dot(cx,cy)
s+=lab(cx,4.65,r'fixed-log domain about $0$')
s+=dot(cx+1.6,cy,'fill=white,line width=1pt',.09)+lab(cx+1.8,1.7,r'$\rho=\pi/2$')
s+=rf'\draw[->,line width=1.1pt] ({cx+2.08},{cy}) arc[start angle=0,end angle=330,radius=.48];'+'\n'
s+=lab(cx,.1,'the loop is not inside the disk')
s+=lab(9.2,4.1,r'$D(z)\sim D^{\prime}(\rho)(z-\rho)$')
s+=lab(9.2,2.9,r'$\log D\longmapsto\log D+2\pi i$')
s+=lab(9.2,1.65,r'$D^{-r}\longmapsto e^{-2\pi i r}D^{-r}$')
s+=lab(9.2,.4,r'$r=1/2:\ -1\qquad r\in\mathbb Z:\ 1$')
save('branch_domain',s)
# V14: exact distinct normalized reciprocals.
headers=['function','$1$','$z^2/2!$','$z^4/4!$','$z^6/6!$'];rows=[[r'$\sec z$',1,1,5,61],[r'$\operatorname{sech}z$',1,-1,5,-61],[r'$z/\sinh z$',1,-sp.Rational(1,3),sp.Rational(7,15),-sp.Rational(31,21)]]
s='';widths=[3.4,1.6,2.1,2.1,2.1];xx=0
for h,ww in zip(headers,widths):s+=cell(xx,3.9,ww,.7,h,12);xx+=ww
for i,row in enumerate(rows):
    xx=0
    for j,(a,ww) in enumerate(zip(row,widths)):
        s+=cell(xx,3.05-i*.9,ww,.8,str(a) if j==0 else tex(a),8 if j in [2,4] else 0);xx+=ww
s+=lab(5.65,-.15,r'$E_{2,1}(z)=\sinh z=z\Phi_{2,1}(z^2),\qquad C_{2,1}(0)=1$')
save('different_reciprocals',s)
# V15: Appell polynomial deformation and finite inverse.
s,p=chart(.7,.5,11.6,3.5,(-2.5,2.5),(-5,20),[(v,f'${v}$') for v in [-2,-1,0,1,2]],[(-5,'$-5$'),(0,'$0$'),(5,'$5$'),(10,'$10$'),(20,'$20$')])
s+='\\begin{scope}\n\\clip (.7,.5) rectangle (12.3,4);\n'
pts=[-2.5+5*i/200 for i in range(201)]
s+=curve(p,[(a,a**4-6*a*a+5) for a in pts])+curve(p,[(a,a**4) for a in pts],'dashed,line width=.8pt')+'\\end{scope}\n'
for a in [-math.sqrt(5),-1,1,math.sqrt(5)]:s+=dot(*p(a,0))
s+=lab(3.2,4.65,r'solid: $E_4(x)=x^4-6x^2+5$')+lab(9.8,4.65,r'dashed: $x^4$')
s+=lab(6.5,-.4,r'$\cosh(\partial_x)E_4=E_4+\frac12E_4^{\prime\prime}+\frac1{24}E_4^{(4)}=x^4$')
save('appell_operator',s)
# V16: theta uses both argument scale and reciprocal order.
s,p=chart(.7,.55,11.6,3.5,(-1.5,1.5),(-5,5),[(-1,'$-1$'),(0,'$0$'),(1,'$1$')],[(-4,'$-4$'),(-2,'$-2$'),(0,'$0$'),(2,'$2$'),(4,'$4$')])
pts=[-1.5+3*i/160 for i in range(161)]
s+=curve(p,[(a,-a*(a+1)) for a in pts])+curve(p,[(a,-a**3-a) for a in pts],'dashed,line width=.9pt')
s+=dot(*p(-1,0),rad=.08)+dot(*p(-1,2),rad=.08)
s+=lab(3,4.65,r'solid: $\Theta_{2,1}(u)=-u(u+1)$')+lab(9.5,4.65,r'dashed: $\Theta_{3,1}(u)=-(u^3+u)$')
s+=lab(6.5,-.35,'at $u=-1$: even order cancels, odd order need not')
save('theta',s)
# V17: exponent polygon together with its projection support function.
s='';cx,cy=2.35,2.6;rad=1.5
pts=[(cx+rad*math.cos((2*k+1)*math.pi/4),cy+rad*math.sin((2*k+1)*math.pi/4)) for k in range(4)]
s+='\\draw[fill=black!7] '+' -- '.join(f'({a:.5f},{b:.5f})' for a,b in pts)+' -- cycle;\n'
s+=line(.4,cy,4.3,cy,'->')+line(cx,.65,cx,4.55,'->')
for i,(a,b) in enumerate(pts):s+=dot(a,b,rad=.08)
s+=lab(cx,5.0,r'$\eta^4=-1$')+lab(cx,.05,'exponent plane')
c,p=chart(5.2,1.0,7.3,3,(0,2*math.pi),(.65,1.05),[(0,'$0$'),(math.pi/2,r'$\pi/2$'),(math.pi,r'$\pi$'),(3*math.pi/2,r'$3\pi/2$'),(2*math.pi,r'$2\pi$')],[(1/math.sqrt(2),r'$1/\sqrt2$'),(1,'$1$')]);s+=c
s+=curve(p,[(a,(abs(math.cos(a))+abs(math.sin(a)))/math.sqrt(2)) for a in [2*math.pi*i/240 for i in range(241)]])
s+=lab(8.9,4.65,r'$h_4(\theta)=\frac{|\cos\theta|+|\sin\theta|}{\sqrt2}$')+lab(8.9,.05,'minima: two dominant exponentials tie')
save('indicator',s)
# V18: actual normalized D3 and the two-term cosine model.
s,p=chart(.65,.6,11.7,3.4,(0,10),(-1.15,1.6),[(a,f'${a}$') for a in range(0,11,2)],[(-1,'$-1$'),(0,'$0$'),(1,'$1$')])
pts=[mp.mpf(10)*i/400 for i in range(401)]
s+=curve(p,[(t,mp.cos(mp.sqrt(3)*t/2)+mp.exp(-3*t/2)/2) for t in pts])
s+=curve(p,[(t,mp.cos(mp.sqrt(3)*t/2)) for t in pts],'dashed,line width=.7pt')
for m in range(3):
    tm=float(2*mp.pi/mp.sqrt(3)*(m+mp.mpf('.5')));xx,yy=p(tm,0);s+=dot(xx,yy,'fill=white',.07)
s+=lab(6.5,4.7,r'$\frac32e^{-t/2}D_3(t)=\cos(\sqrt3t/2)+\frac12e^{-3t/2}$')
s+=lab(6.5,-.25,'solid: full expression; dashed: two-term model; circles: model zeros')
save('two_term',s)
def sci(v,digits):
    mant, exponent=f'{v:+.{digits}e}'.split('e')
    return mant+r'\times10^{'+str(int(exponent))+'}'

# V19: certified root brackets and the measured leading correction.
cert=json.loads((ROOT/'checks/EXACT_CHECKS.json').read_text())['cubic_brackets']
s='';ys=[3.65,2.7,1.75,.8]
for c,y in zip(cert,ys):
    m=c['model_index'];b=c['display_only'];sgn='+' if m%2==0 else '-'
    s+=lab(.45,y,f'$m={m}$','anchor=west')
    s+=lab(3.75,y,'$'+c['lower_decimal']+'$')
    s+=lab(8.3,y,'$'+sci(float(b["delta"]),5)+'$')
    err=float(b['relative_displacement_error']);s+=lab(11.5,y,'$'+sci(err,3)+'$')
for a,t in [(3.75,'certified lower endpoint'),(8.3,r'$\tau_m-t_m$'),(11.5,r'$\delta_m/\delta_m^{(1)}-1$')]:s+=lab(a,4.5,t,r'font=\sffamily\footnotesize')
s+=line(.2,4.1,12.9,4.1,'black!50')
s+=lab(6.5,-.1,r'Each upper endpoint is the displayed lower endpoint plus $10^{-20}$.')
s+=lab(6.5,-.7,'Root intervals: exact rational certificates. Displacement columns: numerical diagnostics.',r'font=\sffamily\footnotesize')
save('cubic_certificates',s)
# V20: exact fourth-order counting under the power map.
s='';
for y,title,vals,den in [(3.2,r'$u=|z|/(\sqrt2\pi)$',[.5,1.5,2.5],1),(1.0,r'$v=|w|/(4\pi^4)$',[1/16,81/16,625/16],1)]:
    s+=lab(6.4,y+1.0,title)
    maxv=3 if y>2 else 40;s+=line(.7,y,12.3,y,'->')
    for k,v in enumerate(vals):
        xx=.8+11.0*v/maxv;s+=line(xx,y-.12,xx,y+.12,'line width=1pt')+dot(xx,y)
        s+=lab(xx,y-.42,('$'+str(sp.Rational(str(v)))+'$') if y>2 else ['$1/16$','$81/16$','$625/16$'][k])
        s+=lab(xx,y+.45,f'count {4*(k+1) if y>2 else k+1}',r'font=\sffamily\footnotesize')
s+=lab(6.5,-.05,r'$n_{D_4}(\sqrt2\pi u)=4\lfloor u+1/2\rfloor,\quad n_{\Delta_4}(4\pi^4 v)=\lfloor v^{1/4}+1/2\rfloor$')
save('counting',s)
# V21: product truncations are approximations, not the entire product.
s,p=chart(.7,.5,11.5,3.4,(0,2),(.1,1),[(0,'$0$'),(.5,'$1/2$'),(1,'$1$'),(1.5,'$3/2$'),(2,'$2$')],[(.2,'$.2$'),(.4,'$.4$'),(.6,'$.6$'),(.8,'$.8$'),(1,'$1$')])
pts=[mp.mpf(2)*i/160 for i in range(161)]
s+=curve(p,[(t,mp.cos(mp.sqrt(t))) for t in pts],'line width=1.35pt')
for n,sty in [(1,'dotted'),(3,'dashed'),(10,'dash dot')]:
    s+=curve(p,[(t,mp.fprod(1-t/(mp.pi**2*(k+mp.mpf('.5'))**2) for k in range(n))) for t in pts],sty+',line width=.7pt')
s+=lab(6.5,4.6,r'$\Delta_2(w)=\cos\sqrt w,\qquad P_L(w)=\prod_{m=0}^{L-1}(1-w/\lambda_m)$')
s+=lab(6.5,-.35,'thick: entire function; dotted $L=1$; dashed $L=3$; dash-dot $L=10$')
save('product',s)
# V22: shares of exact power sums, plot values only.
s=''
for q in [1,2,3]:
    y=4.1-(q-1)*1.3;full=mp.mpf(str(M.kappa(2,q)[q].p))/int(M.kappa(2,q)[q].q);acc=0
    s+=lab(.3,y+.3,f'$q={q}$','anchor=west')
    for m in range(5):
        share=(mp.pi**2*(m+mp.mpf('.5'))**2)**(-q)/full
        width=10.8*float(share);s+=cell(1.5+10.8*float(acc),y,width,.62,'',8+12*m);acc+=share
    s+=cell(1.5+10.8*float(acc),y,10.8*float(1-acc),.62,'',75)
    s+=lab(6.8,y-.32,r'$\sigma_{2,'+str(q)+'}='+sp.latex(M.kappa(2,q)[q])+r'$; first zero share $'+f'{float((mp.pi/2)**(-2*q)/full):.6f}'+'$')
s+=lab(6.8,-.55,'five finite contributions plus the remaining tail; higher moments emphasize the nearest zero')
save('moments',s)
# V23: certified ratio convergence plotted via enclosed values.
rat=[]
for n in range(1,9):
    lo,hi=M.secant_ratio_interval(n);mid=(lo+hi)/2;val=mp.mpf(mid.numerator)/mid.denominator
    rat.append((n,float(mp.log10(1-val))))
s,p=chart(.8,.6,11.4,3.6,(1,8),(-9,0),[(n,f'${n}$') for n in range(1,9)],[(-8,'$-8$'),(-6,'$-6$'),(-4,'$-4$'),(-2,'$-2$'),(0,'$0$')])
s+=curve(p,rat)
for a,b in rat:s+=dot(*p(a,b))
s+=lab(6.5,4.9,r'$\log_{10}(1-R_n),\quad R_n=\frac{P_{2,n}(1)}{2(2n)!(2/\pi)^{2n+1}}$')
s+=lab(6.5,-.25,r'Each ratio is enclosed with a rational Machin-formula bound for $\pi$.')
save('pole_asymptotic',s)
# V24: convergence half-planes, not zero diagrams.
s=''
for i,(a,label,pole) in enumerate([(0.5,r'$N=2$','$1/2$'),(.25,r'$N=4$','$1/4$')]):
    xx=.5+6.7*i;yy=.7;W=5.4;H=3.5
    s+=cell(xx+W*a/1.3,yy,W*(1.3-a)/1.3,H,'',10)
    s+=line(xx,yy+H/2,xx+W+.2,yy+H/2,'->')+line(xx+.4,yy,xx+.4,yy+H+.2,'->')
    X=xx+W*a/1.3;s+=line(X,yy,X,yy+H,'dashed')+dot(X,yy+H/2,'fill=white,line width=1pt',.09)
    s+=lab(X,yy+H/2-.4,pole)+lab(xx+W*.7,yy+H*.72,'series converges',r'font=\sffamily\footnotesize')
    s+=lab(xx+W/2,4.85,label+r': $\mathfrak Z_N^{\rm red}(s)$')
    s+=lab(xx+W/2,.0,r'single continued pole at $s='+pole.strip('$')+'$')
save('zeta_plane',s)
# V25: exact end-to-end N4 coefficient identities, no process boxes.
s='';rows=[('denominator',r'$1-w/24+w^2/40320+\cdots$'),('negative logarithm',r'$w/24+(17/20160)w^2+\cdots$'),('zero moments',r'$\sigma_1=1/24,\quad\sigma_2=17/10080$'),('reciprocal',r'$1+w/24+69w^2/40320+\cdots$'),('tangent',r'$z^3/3!+34z^7/7!+\cdots$')]
for i,(name,value) in enumerate(rows):
    y=4.3-i*.95;s+=lab(.35,y,name,'anchor=west')+lab(8.0,y,value)
    if i<4:s+=line(.35,y-.43,12.3,y-.43,'black!15')
s+=lab(6.5,-.55,r'$69=8!\,\frac{\sigma_1^2+\sigma_2}{2},\qquad34=4\cdot7!\,\sigma_2$')
save('worked_circuit',s)
(ROOT/'graphics/PLATE_INDEX.json').write_text(json.dumps({'plates':plates,'count':len(plates),'source':'deterministic Python -> editable TikZ','display_coordinates':'sampled numerical curves and exact model positions; see page captions'},indent=2)+'\n')
print(f'Generated {len(plates)} editable vector plates.')
