#!/usr/bin/env python3
"""Deterministic, editable TikZ plates. Geometry samples are distinct from exact-check evidence."""
from __future__ import annotations
import json, math
from pathlib import Path
import sympy as s
from models import R,M,chain,transfer,expectation,bayes,coarse_effective,filter_model,green,fk_paths,norm1,basis
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'graphics'

def F(x):return f'{float(x):.6f}'.rstrip('0').rstrip('.') or '0'
def tex(x):return s.latex(s.sympify(x))
class Plate:
    def __init__(self,name,title):
        self.name=name;self.title=title;self.parts=[r'\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth,line cap=round,line join=round]',r'\path[use as bounding box] (0,-.6) rectangle (14,4.8);']
    def add(self,t):self.parts.append(t)
    def text(self,x,y,t,opts=''):
        self.add(r'\node[font=\small,align=center'+(','+opts if opts else '')+'] at ('+F(x)+','+F(y)+') {'+t+'};')
    def line(self,x1,y1,x2,y2,opts=''):
        self.add(r'\draw['+opts+'] ('+F(x1)+','+F(y1)+') -- ('+F(x2)+','+F(y2)+');')
    def rect(self,x,y,w,h,opts='draw,fill=black!7'):
        self.add(r'\path['+opts+'] ('+F(x)+','+F(y)+') rectangle ('+F(x+w)+','+F(y+h)+');')
    def circ(self,x,y,r=.11,opts='fill=black'):
        self.add(r'\path['+opts+'] ('+F(x)+','+F(y)+') circle ('+F(r)+');')
    def axes(self,x,y,w,h,xmax,ymax,xticks=(),yticks=(),xlabel='',ylabel='',xmin=0,ymin=0):
        def pt(a,b):return (x+w*(float(a)-xmin)/(xmax-xmin),y+h*(float(b)-ymin)/(ymax-ymin))
        for a in xticks:
            xx,_=pt(a,ymin);self.line(xx,y,xx,y+h,'black!13,line width=.25pt');self.line(xx,y-.06,xx,y+.06);self.text(xx,y-.26,str(a),'font=\\scriptsize')
        for b in yticks:
            _,yy=pt(xmin,b);self.line(x,yy,x+w,yy,'black!13,line width=.25pt');self.text(x-.16,yy,str(b),'anchor=east,font=\\scriptsize')
        self.line(x,y,x+w+.12,y,'->,line width=.6pt');self.line(x,y,x,y+h+.12,'->,line width=.6pt')
        if xlabel:self.text(x+w/2,y-.55,xlabel,'font=\\scriptsize')
        if ylabel:self.text(x,y+h+.4,ylabel,'anchor=west,font=\\scriptsize')
        return pt
    def curve(self,pt,xs,ys,style='line width=1.1pt'):
        coords=[]
        for a,b in zip(xs,ys):
            xx,yy=pt(a,b)
            if not(math.isfinite(xx) and math.isfinite(yy)):raise ValueError('Nonfinite plotting coordinate')
            coords.append('('+F(xx)+','+F(yy)+')')
        self.add(r'\draw['+style+'] plot coordinates {'+' '.join(coords)+'};')
    def matrix(self,x,y,A,cell=.68,rows=None,cols=None,title=''):
        if title:self.text(x+A.cols*cell/2,y+.7,title,'font=\\small')
        for i in range(A.rows):
            for j in range(A.cols):
                self.rect(x+j*cell,y-(i+1)*cell,cell,cell,'draw=black!30,fill='+('white' if A[i,j]==0 else 'black!8'))
                self.text(x+(j+.5)*cell,y-(i+.5)*cell,'$'+tex(A[i,j])+'$','font=\\small')
        if rows:
            for i,a in enumerate(rows):self.text(x-.15,y-(i+.5)*cell,a,'anchor=east,font=\\scriptsize')
        if cols:
            for j,a in enumerate(cols):self.text(x+(j+.5)*cell,y+.23,a,'font=\\scriptsize')
    def bars(self,x,y,vals,labels,width=4.4,height=2.7,maxv=1,title='',annotate=True):
        n=len(vals);pitch=width/n;bw=pitch*.52
        self.line(x,y,x+width,y,'line width=.6pt')
        if title:self.text(x+width/2,y+height+.75,title)
        for j,v in enumerate(vals):
            hh=float(v)/float(maxv)*height;xx=x+(j+.24)*pitch
            self.rect(xx,y,bw,hh,'draw=black,fill=black!12,line width=.6pt')
            self.text(xx+bw/2,y-.3,labels[j],'font=\\scriptsize')
            if annotate:self.text(xx+bw/2,y+hh+.22,'$'+tex(v)+'$','font=\\scriptsize')
    def finish(self):
        self.add(r'\end{tikzpicture}');(OUT/(self.name+'.tex')).write_text('\n'.join(self.parts)+'\n');return {'name':self.name,'title':self.title,'kind':'editable TikZ vector drawing','numerical_geometry_only':True}

def seq(a,b,n=101):return [a+(b-a)*i/(n-1) for i in range(n)]
def main():
    OUT.mkdir(parents=True,exist_ok=True);index=[]
    Q,K,C,Kc,H,Ps,bad=chain()
    p=Plate('three_views','Coordinates, aggregation, and elimination')
    p.bars(.2,.55,[R(1,2),0,R(1,4),R(1,4)],['0','1','2','3'],width=4,height=2.5,maxv=R(1,2),title='Keep the full state')
    p.bars(5.2,.55,[R(1,2),R(1,2)],['packet A','packet B'],width=3.1,height=2.5,maxv=R(1,2),title='Retain only masses')
    p.line(4.65,.3,4.65,4.4,'black!30');p.line(9.0,.3,9.0,4.4,'black!30')
    pt=p.axes(9.7,.55,3.9,2.7,3,1,xticks=[0,1,2,3],yticks=[0,.5,1],xlabel='time',ylabel='')
    tt=seq(0,3);p.curve(pt,tt,[(1+math.exp(-2*t))/2 for t in tt]);p.curve(pt,tt,[math.exp(-t) for t in tt],'densely dashed,line width=.8pt')
    p.text(11.7,4.05,'Eliminate a hidden state');p.text(11.7,3.62,'solid: exact; dashed: omit coupling','font=\\scriptsize')
    index.append(p.finish())
    p=Plate('clock','A two-state clock')
    ts=[0,math.log(2)/2,math.log(2)];vals=[[1,0],[R(3,4),R(1,4)],[R(5,8),R(3,8)]]
    for j,(values,title) in enumerate(zip(vals,['$t=0$','$t=\\log(2)/2$','$t=\\log(2)$'])):
        p.bars(.5+j*4.5,.8,values,['state 0','state 1'],width=3.5,height=2.6,maxv=1,title=title)
    p.text(7,4.6,'Each bar pair is an exact probability vector','font=\\scriptsize');index.append(p.finish())
    p=Plate('generator_modes','Rates and eigenmodes of a four-state generator')
    pos=[(1.3,3.5),(4,3.5),(1.3,1.1),(4,1.1)]
    p.rect(.5,2.9,4.3,1.25,'draw=black!35,dashed');p.rect(.5,.45,4.3,1.25,'draw=black!35,dashed')
    for (a,b,label) in [(0,1,'1'),(2,3,'1'),(0,2,'2'),(1,3,'2')]:
        x,y=pos[a];xx,yy=pos[b];p.line(x,y,xx,yy,'<->,line width=.8pt');p.text((x+xx)/2+(.25 if x==xx else 0),(y+yy)/2+(.23 if y==yy else 0),label,'fill=white,inner sep=2pt')
    for i,(x,y) in enumerate(pos):p.circ(x,y,.22,'draw,fill=white');p.text(x,y,str(i),'font=\\scriptsize')
    p.text(2.65,4.55,'Off-diagonal rates of $Q$');p.text(2.65,.05,'Top pair A; bottom pair B','font=\\scriptsize')
    mode=M([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]])
    p.matrix(7.2,3.95,mode,cell=.79,rows=['constant','within','between','mixed'],cols=['0','1','2','3'],title='Mode signs (each divided by 2)')
    for i,val in enumerate([0,-2,-4,-6]):p.text(11.7,3.95-(i+.5)*.79,'$'+str(val)+'$','font=\\small')
    p.text(11.7,4.18,'rate','font=\\scriptsize');index.append(p.finish())
    p=Plate('lumpability','Identical aggregate columns, different fine columns')
    p.matrix(.65,3.75,8*K,cell=.76,rows=['0','1','2','3'],cols=['0','1','2','3'],title='$8K$')
    p.matrix(5.4,3.65,C*K,cell=1.08,rows=['A','B'],cols=['0','1','2','3'],title='$CK$: aggregate transition columns')
    p.text(7.55,.6,'Columns 0 and 1 agree; columns 2 and 3 agree.','font=\\small')
    p.text(12,3.55,'$\\bar K=\\begin{pmatrix}3/4&1/4\\\\1/4&3/4\\end{pmatrix}$')
    p.text(12,1.6,'Fine trajectories differ.\\\\Coarse predictions agree.','text width=2.5cm,font=\\small');index.append(p.finish())
    p=Plate('defect_budget','Finite-horizon lumping defect and norm certificate')
    D=C*bad-Kc*C;xx=list(range(9));yy=[norm1(C*bad**n-Kc**n*C) for n in xx]
    pt=p.axes(.9,.6,8,3.3,8,1,xticks=[0,2,4,6,8],yticks=[0,.25,.5,.75,1],xlabel='number of steps $n$',ylabel='induced $\\ell^1$ operator norm')
    p.curve(pt,xx,yy);p.curve(pt,xx,[R(n,8) for n in xx],'dashed,line width=.85pt')
    for a,b in zip(xx,yy):p.circ(*pt(a,b),r=.045)
    p.text(11.3,3.75,'$\\|\\Delta\\|_1=1/8$');p.text(11.3,2.8,'solid: exact defect\\\\dashed: $n/8$','font=\\small')
    p.text(11.3,1.55,'The bound is a guarantee,\\\\not a fitted trend.','font=\\small');index.append(p.finish())
    weights,W,E,E0,Ds,f,energies=expectation()
    p=Plate('weighted_projection','Conditional expectation as weighted projection')
    p.bars(.4,.65,list(f),['0','1','2','3'],width=5.7,height=2.45,maxv=5,title='Observable $f$')
    p.bars(7.6,.65,list(E*f),['0','1','2','3'],width=5.7,height=2.45,maxv=5,title='Conditional expectation $Ef$')
    p.text(7,4.45,'Weights $\\pi=(1,2,3,4)/10$; the block values are 2 and $26/7$.','font=\\scriptsize');index.append(p.finish())
    p=Plate('variance','Orthogonal martingale energy accounting')
    colors=['black!8','black!20','black!36'];x=.7;centers=[]
    for val,fill in zip(energies,colors):
        w=12.5*float(val)/13;p.rect(x,2.05,w,.75,'draw=black,fill='+fill);centers.append(x+w/2);x+=w
    for mid,lx,label,val in zip(centers,[3,9.2,12.25],['mean','between blocks','within blocks'],energies):
        p.line(mid,2.8,mid,3.05,'black!60');p.line(mid,3.05,lx,3.28,'black!60')
        p.text(lx,3.73,label+r'\\$'+tex(val)+'$','font=\\small')
    p.text(7,4.55,'Weighted squared norms: total $13$','font=\\scriptsize')
    for i,d in enumerate(Ds):p.text(2.3+i*4.6,.7,'$D_'+str(i)+'f='+tex(d*f)+'$','font=\\scriptsize')
    index.append(p.finish())
    p=Plate('evidence','Posterior mass and conditional packet shape')
    p.bars(.6,.65,[R(1,4)]*4,['0','1','2','3'],width=5.4,height=2.45,maxv=R(4,7),title='Prior $p$')
    p.bars(7.7,.65,[R(4,7),R(1,7),R(1,7),R(1,7)],['0','1','2','3'],width=5.4,height=2.45,maxv=R(4,7),title='Posterior $\\mathcal B_\\lambda(p)$')
    p.text(7,4.45,'$\\lambda=(4,1,1,1)$; evidence $Z=7/4$','font=\\scriptsize');index.append(p.finish())
    p=Plate('insufficiency','Identical coarse priors, incompatible coarse posteriors')
    p.bars(.5,.65,[R(1,2),R(1,2)],['A','B'],width=3.5,height=2.45,maxv=1,title='Both coarse priors')
    p.bars(5.15,.65,[R(4,5),R(1,5)],['A','B'],width=3.5,height=2.45,maxv=1,title='From $p^{(a)}$')
    p.bars(9.8,.65,[R(1,2),R(1,2)],['A','B'],width=3.5,height=2.45,maxv=1,title='From $p^{(b)}$')
    p.text(7,4.5,'Hidden redistribution changes the packet-A posterior from $1/2$ to $4/5$.','font=\\scriptsize');index.append(p.finish())
    p=Plate('loss_vector','An exact posterior defect on the coarse simplex')
    p.line(1.4,2.4,12.7,2.4,'line width=1.3pt');p.text(1.4,1.85,'$(0,1)$');p.text(12.7,1.85,'$(1,0)$')
    x0=1.4+11.3*.5;x1=1.4+11.3*5/7
    p.circ(x0,2.4,.09,'draw,fill=white');p.circ(x1,2.4,.09);p.line(x0,2.85,x1,2.85,'->,line width=1pt')
    p.text(x0,3.55,'declared coarse update\\\\$(1/2,1/2)$','font=\\small');p.text(x1+.4,1.0,'fine then coarse\\\\$(5/7,2/7)$','font=\\small')
    p.text((x0+x1)/2,3.1,'$3/14$','font=\\scriptsize');p.text(7,4.4,'Simplex coordinate: posterior mass in packet A','font=\\scriptsize')
    index.append(p.finish())
    p=Plate('odds','A normalized exponential flow on the two-state simplex')
    tt=seq(0,4);pt=p.axes(.8,.6,8.7,3.3,4,1,xticks=[0,1,2,3,4],yticks=[0,.5,1],xlabel='time $t$',ylabel='probability')
    pp=[math.exp(t)/(1+math.exp(t)) for t in tt];p.curve(pt,tt,pp);p.curve(pt,tt,[1-v for v in pp],'dashed,line width=.8pt')
    p.text(11.6,3.7,'$p_0(t)=\\dfrac{e^t}{1+e^t}$');p.text(11.6,2.7,'$p_1(t)=\\dfrac{1}{1+e^t}$');p.text(11.6,1.5,'$\\dot p_0=p_0(1-p_0)$');p.text(11.6,.65,'Mass stays one.\\\\Mixtures are not preserved.','font=\\scriptsize');index.append(p.finish())
    p=Plate('filter_order','Changing the order of prediction and updating changes the result')
    p.bars(.6,.7,[R(6,7),R(1,7)],['0','1'],width=5.4,height=2.45,maxv=1,title='Predict, then update')
    p.bars(7.7,.7,[R(3,4),R(1,4)],['0','1'],width=5.4,height=2.45,maxv=1,title='Update, then predict')
    p.text(7,4.5,'Same prior $e_0$, transition $K_2$, and likelihood $(1,1/2)$','font=\\scriptsize');index.append(p.finish())
    p=Plate('beta','Polynomial conjugate densities and exact evidence')
    xx=seq(0,1);pt=p.axes(.8,.65,8.8,3.25,1,2.4,xticks=[0,.25,.5,.75,1],yticks=[0,1,2],xlabel='$\\theta$',ylabel='density')
    p.curve(pt,xx,[12*x*(1-x)**2 for x in xx],'dashed,line width=.8pt');p.curve(pt,xx,[140*x**3*(1-x)**3 for x in xx])
    p.text(11.65,3.75,'Prior: $\\mathrm{Beta}(2,3)$','font=\\small');p.text(11.65,2.95,'Posterior: $\\mathrm{Beta}(4,4)$','font=\\small');p.text(11.65,1.8,'ordered data: $3/35$\\\\count data: $9/35$','font=\\small');p.text(11.65,.6,'Same posterior,\\\\different evidence.','font=\\small');index.append(p.finish())
    p=Plate('fractional','A square root creates a long-range coupling')
    S=sum([s.sqrt(2*j)*Ps[j] for j in range(4)],s.zeros(4))
    pos=[(1,3.6),(4,3.6),(1,1),(4,1)]
    for a,b in [(0,1),(0,2),(1,3),(2,3)]:p.line(*pos[a],*pos[b],'line width=.85pt')
    for a,b in [(0,3),(1,2)]:p.line(*pos[a],*pos[b],'dashed,line width=1pt')
    for i,(x,y) in enumerate(pos):p.circ(x,y,.21,'draw,fill=white');p.text(x,y,str(i),'font=\\scriptsize')
    p.text(2.5,4.5,'Solid: $L$; dashed: new in $\\sqrt L$','font=\\scriptsize')
    pt=p.axes(6.6,.65,6.6,2.8,2.5,1,xticks=[0,.5,1,1.5,2,2.5],yticks=[0,.5,1],xlabel='time $t$',ylabel='fastest mode amplitude')
    tt=seq(0,2.5);p.curve(pt,tt,[math.exp(-math.sqrt(6)*t) for t in tt]);p.curve(pt,tt,[math.exp(-6*t) for t in tt],'dashed,line width=.8pt');p.text(10,4.45,'solid: $e^{-t\\sqrt6}$; dashed: $e^{-6t}$','font=\\scriptsize');index.append(p.finish())
    p=Plate('gap','Square-root sensitivity is different at zero and away from zero')
    xx=seq(0,1);pt=p.axes(.8,.65,8.6,3.25,1,1,xticks=[0,.25,.5,.75,1],yticks=[0,.25,.5,.75,1],xlabel='generator perturbation $\\varepsilon$',ylabel='square-root difference')
    p.curve(pt,xx,[math.sqrt(x) for x in xx]);p.curve(pt,xx,[math.sqrt(1+x)-1 for x in xx],'dashed,line width=1pt');p.curve(pt,xx,[x/2 for x in xx],'densely dotted,line width=.75pt')
    p.text(11.8,3.85,'no gap: $\\sqrt{\\varepsilon}$','font=\\small');p.text(11.8,2.8,'gap one: $\\sqrt{1+\\varepsilon}-1$','font=\\small');p.text(11.8,1.75,'certificate: $\\varepsilon/2$','font=\\small');p.text(11.8,.65,'No uniform linear bound\\\\can hold at zero.','font=\\scriptsize');index.append(p.finish())
    p=Plate('random_clock','The Poisson clock mixes diffusion times')
    xx=seq(.012,2,240);pt=p.axes(.8,.65,8.7,2.8,2,1.05,xticks=[0,.5,1,1.5,2],yticks=[0,.25,.5,.75,1],xlabel='diffusion time $s$',ylabel='clock density $\\eta_1(s)$')
    fun=lambda v:math.exp(-1/(4*v))/(2*math.sqrt(math.pi)*v**1.5)
    p.curve(pt,xx,[fun(x) for x in xx]);p.line(*pt(1/6,0),*pt(1/6,fun(1/6)),'densely dotted');p.text(3,4.45,'Clock mode at $s=1/6$','font=\\scriptsize')
    p.text(11.8,3.8,'$\\displaystyle\\int_0^\\infty\\eta_t(s)\\,ds=1$');p.text(11.8,2.7,'$\\displaystyle\\int_0^\\infty s\\eta_t(s)\\,ds=\\infty$');p.text(11.8,1.2,'A probability clock\\\\need not have a finite mean.','font=\\small');index.append(p.finish())
    p=Plate('green','A continuum Green hat through exact discrete nodes')
    xx=seq(0,1);pt=p.axes(.8,.65,7.3,3.2,1,.3,xticks=[0,.25,.5,.75,1],yticks=[0,.125,.25],xlabel='$x$',ylabel='$G(x,1/2)$')
    p.curve(pt,xx,[min(x,.5)-x*.5 for x in xx]);
    for x in [.25,.5,.75]:p.circ(*pt(x,min(x,.5)-x*.5),r=.07)
    p.matrix(10,3.35,M([[3,2,1],[2,4,2],[1,2,3]]),cell=.86,title='$64 L_h^{-1}$, $h=1/4$');p.text(11.3,.4,'$L_h^{-1}=hG_{\\rm nodes}$','font=\\small');index.append(p.finish())
    p=Plate('mesh','A nonzero second-order error known exactly')
    xx=seq(0,1);pt=p.axes(.8,.65,7.6,3.1,1,R(1,60),xticks=[0,.25,.5,.75,1],yticks=[0],xlabel='$x$',ylabel='$|u_h-u|=h^2x(1-x)$')
    for h,style in [(R(1,4),'line width=1.1pt'),(R(1,8),'dashed,line width=.9pt'),(R(1,16),'dotted,line width=.9pt')]:p.curve(pt,xx,[float(h*h)*x*(1-x) for x in xx],style)
    p.text(11.35,3.95,'grid spacing $h$\\qquad maximum error','font=\\small')
    for y,h in zip([3,2,1],[R(1,4),R(1,8),R(1,16)]):p.text(11.35,y,'$'+tex(h)+'$\\qquad $'+tex(h*h/4)+'$')
    index.append(p.finish())
    p=Plate('paths','All eight Feynman-Kac paths')
    Kf,w,f,rows=fk_paths()
    for x,label in zip([1.6,4.4,7,9.5,12],['Path','probability','weight','terminal','contribution']):p.text(x,4.4,label,'font=\\small')
    for i,row in enumerate(rows):
        y=3.8-i*.47;path=''.join(map(str,row['path']))
        p.text(1.6,y,r'\texttt{'+path+'}','font=\\small');p.text(4.4,y,'$'+str(row['probability'])+'$');p.text(7,y,'$'+str(row['potential'])+'$');p.text(9.5,y,'$'+str(row['terminal'])+'$');p.text(12,y,'$'+str(row['contribution'])+'$')
        if i%2==0:p.line(.6,y-.22,13.4,y-.22,'black!18,line width=.3pt')
    p.text(7,-.22,'Total probability $=1$; weighted terminal expectation $=311/256$.','font=\\scriptsize');index.append(p.finish())
    p=Plate('resolvent','The retained resolvent differs from the resolvent of the retained generator')
    zz=seq(.2,4);pt=p.axes(.8,.65,8.5,3.25,4,3,xticks=[0,1,2,3,4],yticks=[0,1,2,3],xlabel='$z>0$',ylabel='resolvent coefficient')
    p.curve(pt,zz,[(x+1)/(x*(x+2)) for x in zz]);p.curve(pt,zz,[1/(x+1) for x in zz],'dashed,line width=.8pt')
    p.text(11.7,3.7,'exact: $\\dfrac{z+1}{z(z+2)}$');p.text(11.7,2.5,'omit hidden state: $\\dfrac1{z+1}$');p.text(11.7,1.0,'The pole at zero survives\\\\through hidden feedback.','font=\\small');index.append(p.finish())
    p=Plate('memory','Exact retained dynamics and naive hidden-state deletion')
    tt=seq(0,4);pt=p.axes(.8,.65,8.5,3.2,4,1,xticks=[0,1,2,3,4],yticks=[0,.5,1],xlabel='time $t$',ylabel='retained state $x(t)$')
    p.curve(pt,tt,[(1+math.exp(-2*t))/2 for t in tt]);p.curve(pt,tt,[math.exp(-t) for t in tt],'dashed,line width=.8pt')
    p.text(11.7,3.75,'exact: $\\dfrac{1+e^{-2t}}2$');p.text(11.7,2.7,'naive deletion: $e^{-t}$');p.text(11.7,1.25,'$\\displaystyle K(t)=e^{-t}$\\\\returns hidden excursions.','font=\\small');index.append(p.finish())
    p=Plate('jordan','The nilpotent part of a Jordan block survives in memory')
    tt=seq(0,3);pt=p.axes(.8,.65,8.5,3.15,3,.21,xticks=[0,.5,1,1.5,2,2.5,3],yticks=[0,.1,.2],xlabel='time $t$',ylabel='memory coefficient $t e^{-2t}$')
    p.curve(pt,tt,[t*math.exp(-2*t) for t in tt]);p.circ(*pt(.5,.5/math.e),r=.065)
    p.text(11.7,3.9,'$J=-2I+N,\\quad N^2=0$');p.text(11.7,2.8,'$e^{tJ}=e^{-2t}(I+tN)$');p.text(11.7,1.35,'$\\widehat K(z)=\\dfrac1{(z+2)^2}$');p.text(11.7,.4,'A repeated pole carries a jet.','font=\\scriptsize');index.append(p.finish())
    p=Plate('survival','Transient mass, absorbed mass, and a changing hazard')
    tt=seq(0,5);pt=p.axes(.8,.65,8.5,3.2,5,1,xticks=[0,1,2,3,4,5],yticks=[0,.5,1],xlabel='time $t$',ylabel='probability or rate')
    p.curve(pt,tt,[(1+t)*math.exp(-t) for t in tt]);p.curve(pt,tt,[1-(1+t)*math.exp(-t) for t in tt],'dashed,line width=.8pt');p.curve(pt,tt,[t/(1+t) for t in tt],'densely dotted,line width=.9pt')
    p.text(11.7,3.8,'solid: survival $S(t)$');p.text(11.7,2.8,'dashed: absorbed mass');p.text(11.7,1.8,'dotted: hazard $h(t)$');p.text(11.7,.6,'$h(0)=0$, but eventual exit\\\\has probability one.','font=\\scriptsize');index.append(p.finish())
    p=Plate('naturality','A function acts on both eigenvalues and Jordan directions')
    p.matrix(.8,3.6,M([[2,1,0],[0,2,0],[0,0,9]]),cell=.92,title='$A_f$')
    p.matrix(5.4,3.6,M([[R(1,3),-R(1,9),0],[0,R(1,3),0],[0,0,R(1,10)]]),cell=.92,title='$F(A_f)$ for $F(z)=(1+z)^{-1}$')
    p.rect(5.38,1.73,1.88,1.9,'draw=black,dashed,line width=1pt')
    p.text(11.7,3.6,'$F(2)=1/3$');p.text(11.7,2.65,"$F'(2)=-1/9$");p.text(11.7,1.25,'The dashed block is\\\\$F(A_c)$, not just $F(2)I$.','font=\\small');index.append(p.finish())
    p=Plate('integrated_filter','The full and coarse two-observation filters agree')
    rows,joint=filter_model()
    p.bars(.4,.6,list(rows[0]['posterior']),['0','1','2','3'],width=4.2,height=2.45,maxv=R(3,4),title='First posterior')
    p.bars(5.2,.6,list(rows[1]['posterior']),['0','1','2','3'],width=4.2,height=2.45,maxv=R(3,4),title='Second posterior')
    p.bars(10.3,.6,list(rows[1]['coarse']),['A','B'],width=3.2,height=2.45,maxv=R(3,4),title='Coarse posterior')
    p.text(7,4.45,'Evidence $Z_1=5/8$, $Z_2=13/20$, and $Z_1Z_2=13/32$','font=\\scriptsize');index.append(p.finish())
    p=Plate('summability','Summable generator differences need not have summable square roots')
    xx=list(range(1,17));y1=[];y2=[];v1=s.S.Zero;v2=s.S.Zero
    for n in xx:v1+=R(1,n);v2+=R(1,n*n);y1.append(v1);y2.append(v2)
    pt=p.axes(.8,.65,8.5,3.2,16,3.5,xticks=[0,4,8,12,16],yticks=[0,1,2,3],xlabel='partial-sum cutoff $N$',ylabel='sum of defect norms')
    p.curve(pt,xx,y1);p.curve(pt,xx,y2,'dashed,line width=.9pt');p.curve(pt,xx,[v/2 for v in y2],'densely dotted,line width=.9pt')
    p.text(11.7,3.95,r'solid: $\sum_{n\le N}n^{-1}$','font=\\small')
    p.text(11.7,2.95,r'dashed: $\sum_{n\le N}n^{-2}$','font=\\small')
    p.text(11.7,1.95,r'dotted: $\frac12\sum_{n\le N}n^{-2}$','font=\\small')
    p.text(11.7,.55,r'The infinite-series conclusion\\uses the exact formulas.','font=\\scriptsize')
    index.append(p.finish())
    (OUT/'PLATE_INDEX.json').write_text(json.dumps({'plates':index,'count':len(index),'convention':'Exact quantities in labels; numeric curve geometry sampled from declared exact expressions; no external images.'},indent=2)+'\n')
    print(f'Generated {len(index)} editable TikZ plates.')
if __name__=='__main__':main()
