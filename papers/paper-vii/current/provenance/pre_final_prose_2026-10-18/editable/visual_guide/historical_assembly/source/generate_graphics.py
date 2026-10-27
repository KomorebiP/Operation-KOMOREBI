#!/usr/bin/env python3
"""Deterministic, editable TikZ plates. Geometry samples are distinct from exact-check evidence."""
from __future__ import annotations
import json, math
from pathlib import Path
import sympy as s
from models import *
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
    X,Y,Z=paulis();h,cnot,middle,v,rho=bell();S,Ps,vs,L=cyclic4()
    p=Plate('three_objects','State amplitudes, observable coherence, and retained dynamics')
    p.matrix(.55,3.45,M([1,0,0,1]),cell=.62,title=r'$\sqrt2\,\psi$')
    p.text(2.75,2.5,r'Two amplitudes\\one pure state',r'font=\small')
    p.matrix(5.05,3.7,2*rho,cell=.75,title=r'$2\rho=2\psi\psi^*$')
    p.text(6.55,.2,'Off-diagonal entries retain phase.',r'font=\scriptsize')
    p.line(4.05,.2,4.05,4.35,'black!30');p.line(9.0,.2,9.0,4.35,'black!30')
    pt=p.axes(9.6,.75,3.8,2.65,math.pi,1,xticks=[0],yticks=[0,1],xlabel='time',ylabel='$|x(t)|^2$')
    tt=seq(0,math.pi);p.curve(pt,tt,[math.cos(t)**2 for t in tt]);p.text(11.5,4.3,'Hidden coupling returns.',r'font=\small');index.append(p.finish())
    p=Plate('addresses','Every Pauli address is a distinct computational basis vector')
    coords={0:(1,.65),1:(4.35,.65),2:(1,3.1),3:(4.35,3.1),4:(2.65,1.6),5:(6,1.6),6:(2.65,4.05),7:(6,4.05)}
    for j in range(8):
        for bit in (1,2,4):
            k=j^bit
            if j<k:p.line(*coords[j],*coords[k],('dashed,' if bit==4 else '')+'black!55,line width=.6pt')
    for j,(x,y) in coords.items():
        p.rect(x-.47,y-.3,.94,.6,'draw,fill=white');p.text(x,y,r'$\ket{'+format(j,'03b')+'}$')
    p.text(10.15,4.1,'Three actual words',r'font=\small')
    p.text(10.15,3.1,r'$W_{101}=X_1X_3$',r'font=\small')
    p.text(10.15,2.2,r'$W_{011}=X_2X_3$',r'font=\small')
    p.text(10.15,1.3,r'$W_{110}=X_1X_2$',r'font=\small')
    p.text(6.65,.1,r'$\dim\Span\{W_a\ket{000}\}=8$',r'font=\small');index.append(p.finish())
    p=Plate('local_orbits','Schmidt rank controls the linear span of local actions')
    p.matrix(.8,3.55,M([[1,0],[0,0]]),cell=1.05,title='Product seed matrix')
    p.matrix(7.6,3.55,s.eye(2),cell=1.05,title=r'Bell seed matrix $\sqrt2C$')
    p.text(4.75,2.5,r'row rank $1$\\orbit dimension $2$',r'font=\small')
    p.text(11.4,2.5,r'row rank $2$\\orbit dimension $4$',r'font=\small')
    p.text(7,.6,'$A$ acts on the left. It cannot invent a new direction in the row space.',r'font=\small');index.append(p.finish())
    p=Plate('seed_rank','Two seed row spaces fill a multiplicity space of dimension three')
    p.matrix(.6,3.7,M([[1,0,0],[0,1,0]]),cell=.95,title='$C_1$')
    p.matrix(5.5,3.7,M([[0,0,1],[0,0,0]]),cell=.95,title='$C_2$')
    p.text(11.5,3.4,r'$d=2,\ m=3$');p.text(11.5,2.35,r'$\lceil m/d\rceil=2$')
    for j in range(3):
        p.rect(1+j*4.3,.45,3.5,.75,'draw,fill='+('black!10' if j<2 else 'black!28'));p.text(2.75+j*4.3,.83,'multiplicity $'+str(j+1)+'$',r'font=\small')
    p.text(7,1.5,r'The stacked rows span $\CC^3$; their local orbits span $\CC^2\otimes\CC^3$.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('cyclic_four','Four shift eigenvectors carry exact Gaussian-rational phases')
    B=M.hstack(*vs)*2
    p.matrix(1,4,B,cell=.8,rows=['site 0','site 1','site 2','site 3'],cols=['$j=0$','$j=1$','$j=2$','$j=3$'],title='$2V$, with $V^*V=I$')
    for j in range(4):
        y=3.8-j*.85;p.text(8.05,y,'$S v_'+str(j)+'='+tex(I**j)+'v_'+str(j)+'$',r'font=\small');p.text(11.85,y,'$P_'+str(j)+'=v_'+str(j)+'v_'+str(j)+'^*$',r'font=\small')
    p.text(8.8,.12,'Each column has four entries of magnitude $1/2$.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('parity','Fine computational packets partition into total parity')
    groups=parity(3)[1]
    for a in range(2):
        y=3.1-a*2.05;p.text(.5,y,'even' if a==0 else 'odd',r'anchor=west,font=\small')
        for k,j in enumerate(groups[a]):
            x=3+k*3;p.rect(x-.78,y-.44,1.56,.88,'draw,fill=black!'+str(5+a*12));p.text(x,y,r'$\ket{'+format(j,'03b')+'}$')
    p.text(7,4.55,'Each coarse projector has rank four; all eight fine projectors have rank one.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('bell_circuit','Bell circuit amplitudes before and after its two gates')
    for stage,vec,label in [(0,basis(4,0),'seed'),(1,middle,r'after $H\otimes I$'),(2,v,'after CNOT')]:
        x=.7+4.5*stage;p.text(x+1.6,4.3,label)
        p.matrix(x+.25,3.7,vec,cell=.65,rows=['00','01','10','11'])
    p.text(2.1,.25,'even only',r'font=\scriptsize');p.text(6.75,.25,'both parity packets',r'font=\scriptsize');p.text(11.25,.25,'even only, with coherence',r'font=\scriptsize');index.append(p.finish())
    p=Plate('interference','The two paths to the opposite output cancel')
    for x,y,label in [(1.4,2.3,'$0$'),(6.6,3.6,'$0$'),(6.6,1,'$1$'),(12.3,2.3,'$1$')]:p.circ(x,y,.27,'draw,fill=white');p.text(x,y,label)
    for x1,y1,x2,y2,label,dy in [(1.7,2.4,6.25,3.5,r'$1/\sqrt2$',.35),(1.7,2.2,6.25,1.1,r'$1/\sqrt2$',-.35),(6.95,3.5,12,2.4,r'$1/\sqrt2$',.35),(6.95,1.1,12,2.2,r'$-1/\sqrt2$',-.35)]:
        p.line(x1,y1,x2,y2,'->,line width=.8pt');p.text((x1+x2)/2,(y1+y2)/2+dy,label,r'font=\small,fill=white,inner sep=1pt')
    p.text(6.7,4.6,'Two actual Hadamard paths, not classical alternatives',r'font=\scriptsize');p.text(6.8,-.18,r'$\text{amplitude}=1/2-1/2=0\quad\ne\quad\text{sum of path probabilities}=1/2$',r'font=\small');index.append(p.finish())
    HH,BB,HB=symmetry();p=Plate('hamiltonian','Parity rearranges the same Hamiltonian into two exact blocks')
    p.matrix(.7,4,HH,cell=.82,rows=['00','01','10','11'],cols=['00','01','10','11'],title='Computational order')
    p.matrix(8.7,4,HB,cell=.82,rows=['00','11','01','10'],cols=['00','11','01','10'],title='Parity order')
    p.text(6.8,2.7,r'same operator\\different order',r'font=\small');p.text(6.9,.2,r'Even eigenvalues: $\pm5/4$. Odd eigenvalues: $\pm1$.',r'font=\small');index.append(p.finish())
    p=Plate('leakage','An amplitude bound is not a probability curve')
    pt=p.axes(.8,.7,8.5,3.25,2.5,1.15,xticks=[0,.5,1,1.5,2,2.5],yticks=[0,.5,1],xlabel=r'$u=|\varepsilon t|$',ylabel='leakage amplitude')
    tt=seq(0,2.5);p.curve(pt,tt,[abs(math.sin(t)) for t in tt]);p.curve(pt,tt,[min(1,t) for t in tt],'dashed,line width=.8pt')
    p.text(11.7,3.95,r'$H=\varepsilon X$');p.text(11.7,2.95,r'solid: $|\sin u|$\\dashed: $\min(1,u)$',r'font=\small');p.text(11.7,1.5,r'Probability is $\sin^2u$,\\not $|\sin u|$.',r'font=\small');index.append(p.finish())
    p=Plate('moving_frame','A stationary laboratory vector has moving coordinates')
    for j,ang in enumerate([0,math.pi/6,math.pi/3]):
        x=2+j*4.65;y=2.3
        p.line(x-1.25,y,x+1.55,y,'black!25');p.line(x,y-1.35,x,y+1.4,'black!25')
        p.line(x,y,x+1.45,y,'->,line width=1.1pt')
        p.line(x,y,x+1.25*math.cos(ang),y+1.25*math.sin(ang),'->,dashed')
        p.line(x,y,x-1.05*math.sin(ang),y+1.05*math.cos(ang),'->,dashed')
        p.text(x,4.2,[r'$\theta=0$',r'$\theta=\pi/6$',r'$\theta=\pi/3$'][j]);p.text(x,.25,['$(1,0)$',r'$(\sqrt3/2,-1/2)$',r'$(1/2,-\sqrt3/2)$'][j],r'font=\small')
    p.text(7,4.75,'Solid vector: fixed in the laboratory. Dashed axes: rotating frame.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('connection','The derivative of a projector points between its two packets')
    p.matrix(.7,3.35,M([[1,0],[0,0]]),cell=1.02,title='$P(0)$')
    p.matrix(5.25,3.35,M([[0,1],[1,0]]),cell=1.02,title=r'$\dot P(0)$')
    p.matrix(9.8,3.35,M([[0,-1],[1,0]]),cell=1.02,title='$C$')
    p.text(7,.3,r'$P\dot P P=0,\qquad C^*=-C,\qquad[C,P]=\dot P$.',r'font=\small');index.append(p.finish())
    p=Plate('range_atlas','A chart can fail while the projector stays smooth')
    angles=[0,math.pi/6,math.pi/3,math.pi/2]
    for j,t in enumerate(angles):
        x=1.6+j*3.55;y=2.35;p.line(x-1,y,x+1,y,'black!30');p.line(x,y-1.1,x,y+1.1,'black!30')
        dx,dy=.95*math.cos(t),.95*math.sin(t);p.line(x-dx,y-dy,x+dx,y+dy,'line width=1.2pt')
        p.text(x,4.2,['$0$',r'$\pi/6$',r'$\pi/3$',r'$\pi/2$'][j]);p.text(x,.45,[r'$\det T=1$',r'$\det T=3/4$',r'$\det T=1/4$',r'$\det T=0$'][j],r'font=\small')
    p.text(7,4.8,r'Ranges of $P(\theta)$; the anchor is the horizontal line.',r'font=\scriptsize');p.text(7,-.15,'At the last position, use a new anchor. The fiber still has dimension one.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('bloch_curvature','Curvature is an area density, not merely a basis mismatch')
    # Deterministic projected sphere (orthographic outline plus latitude and meridian).
    cx,cy=2.8,2.45;p.circ(cx,cy,1.62,'draw,line width=.8pt')
    p.add(r'\draw[black!35] (2.8,2.45) ellipse (1.62 and .45);')
    p.add(r'\draw[black!35] (2.8,2.45) ellipse (.6 and 1.62);')
    p.add(r'\draw[dashed,black!65] (2.8,3.25) ellipse (1.4 and .31);')
    p.line(cx,cy,cx,4.08,'->');p.text(2.8,.2,r'Cap flux at $\theta=\pi/3$ is $\pi/2$.',r'font=\scriptsize')
    pt=p.axes(6.4,.85,6.7,2.8,math.pi,.6,xticks=[0],yticks=[0,.25,.5],xlabel=r'polar angle $\theta$',ylabel=r'$F_{\theta\phi}=\frac12\sin\theta$')
    ts=seq(0,math.pi);p.curve(pt,ts,[.5*math.sin(t) for t in ts]);p.text(13.1,.58,r'$\pi$',r'font=\scriptsize');p.text(9.7,4.45,'The density vanishes at coordinate poles.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('dephasing','Coarse parity dephasing and fine dephasing are different maps')
    dc=dephase(rho,parity(2)[0])
    p.matrix(.75,3.95,2*rho,cell=.75,rows=['00','01','10','11'],title=r'$2\rho$; also $2D_{\rm parity}(\rho)$')
    p.matrix(8.7,3.95,2*dc,cell=.75,rows=['00','01','10','11'],title=r'$2D_{\rm computational}(\rho)$')
    p.text(6.8,2.3,r'same diagonal\\different coherence',r'font=\small')
    p.text(7,.15,'Bell-projector outcome: $1$ on the left, $1/2$ on the right.',r'font=\small');index.append(p.finish())
    Ks,rh,output=damping();p=Plate('damping','Population transfer and coherence contraction in one exact channel')
    superop=M([[1,0,0,R(9,25)],[0,R(4,5),0,0],[0,0,R(4,5),0],[0,0,0,R(16,25)]])
    p.matrix(.7,4,superop,cell=.86,rows=['00','01','10','11'],cols=['00','01','10','11'],title='Superoperator on matrix entries')
    p.matrix(9.3,3.5,output,cell=1.07,title=r'Output from $\ket{+}$')
    p.text(7,2.65,r'$\gamma=9/25$');p.text(7,1.5,r'coherence factor\\$4/5$',r'font=\small');p.text(10.45,.35,r'$\Tr\rho=1,\quad\det\rho=36/625>0$',r'font=\small');index.append(p.finish())
    p=Plate('complete_positivity','An ancillary qubit exposes a negative direction')
    ptm=partial_transpose_second(rho)
    p.matrix(.8,3.95,2*ptm,cell=.84,rows=['00','01','10','11'],title=r'$2(\id\otimes{\mathsf T})(\rho_{\rm Bell})$')
    p.text(9.65,3.7,r'$w=(\ket{01}-\ket{10})/\sqrt2$');p.text(9.65,2.45,r'$w^*(\id\otimes{\mathsf T})(\rho)w=-1/2$');p.text(9.65,1.0,r'Transpose is positive on one system.\\It is not completely positive.',r'font=\small,text width=6cm');index.append(p.finish())
    E,V,PC,Qs,psi,rh,ww,corrupted,rec,recovered=code();p=Plate('syndromes','Four syndrome measurements each preserve a logical pair')
    labels=['no error','$X_1$','$X_2$','$X_3$'];pairs=[[0,7],[4,3],[2,5],[1,6]]
    for i,(a,b) in enumerate(pairs):
        x=.6+i*3.45;p.rect(x,.65,2.75,3.25,'draw,fill=black!4');p.text(x+1.375,3.45,labels[i]);p.text(x+1.375,2.6,r'$\ket{'+format(a,'03b')+'}$');p.text(x+1.375,1.8,r'$\ket{'+format(b,'03b')+'}$');p.text(x+1.375,1.03,'ratio $3:4$',r'font=\scriptsize')
    p.text(7,4.55,r'Channel probabilities: $1/10,\ 2/10,\ 3/10,\ 4/10$.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('logical_error','A phase error stays inside the syndrome but changes the logical state')
    p.matrix(.7,3.45,Z,cell=1.06,title='$V^*Z_1V$')
    p.text(7,3.65,'before: $(3,4)/5$');p.text(7,2.45,'after: $(3,-4)/5$');p.text(7,1.2,r'same code support\\different relative phase',r'font=\small')
    p.matrix(10.8,3.45,s.diag(s.Symbol('c'),s.Symbol('c')),cell=1.06,title='Required scalar form $cI$')
    p.text(7,.15,r'A trace of zero does not make $\diag(1,-1)$ the zero operator.',r'font=\small');index.append(p.finish())
    p=Plate('feshbach','The eliminated pole and the physical poles have different meanings')
    # Pole locations on a spectral line; exact values are labeled.
    x=lambda z:1.0+(z+1)*2.75
    p.line(.8,2.3,13.0,2.3,'->,line width=.8pt')
    for z,lab,sty,yy in [(1-math.sqrt(2),r'$1-\sqrt2$','fill=black',3.4),(1+math.sqrt(2),r'$1+\sqrt2$','fill=black',3.4),(2,'$2$','draw,fill=white',1.3),(3,'$3$','draw,fill=white',1.3)]:
        xx=x(z);p.circ(xx,2.3,.1,sty);p.line(xx,2.45 if yy>2 else 2.15,xx,yy-.25 if yy>2 else yy+.25,'black!50');p.text(xx,yy,lab)
    p.text(6.9,4.55,'Filled: full resolvent poles. Open at 2: only the eliminated inverse fails.',r'font=\scriptsize')
    p.text(6.9,.12,'At $z=3$: exact retained resolvent $1/2$, bare truncation $1/3$.',r'font=\small');index.append(p.finish())
    p=Plate('memory','Hidden-state return breaks the retained semigroup law')
    pt=p.axes(.8,.75,8.5,3.1,math.pi,1.1,xticks=[0],yticks=[0,.5,1],xlabel='time $t$',ylabel='probability')
    tt=seq(0,math.pi);p.curve(pt,tt,[math.cos(t)**2 for t in tt]);p.curve(pt,tt,[math.sin(t)**2 for t in tt],'dashed,line width=.8pt')
    p.text(11.7,3.8,r'solid: retained\\dashed: hidden',r'font=\small');p.text(11.7,2.4,'$K(t)=1$');p.text(11.7,1.2,r'The two probabilities\\sum to one.',r'font=\small');p.text(9.25,.47,r'$\pi$',r'font=\scriptsize');index.append(p.finish())
    p=Plate('euclidean','Positive spectrum does not mean nonnegative matrix entries')
    T=M([[R(3,4),R(1,4)],[R(1,4),R(3,4)]])
    p.matrix(1.1,3.5,T,cell=1.15,title=r'$T$ at $e^{-2\tau}=1/2$')
    p.matrix(9.2,3.5,Z*T*Z,cell=1.15,title='$ZTZ$ in another basis')
    p.text(6.5,2.4,r'Both have\\spectrum $\{1,1/2\}$.',r'font=\small');p.text(7,.4,r'Positive-definite operator: $v^*Tv>0$ for $v\ne0$. Not an entrywise test.',r'font=\small');index.append(p.finish())
    p=Plate('spectral_dimension','A finite heat-trace dimension returns to zero at both ends')
    xs=seq(-3,1.1,200);ts=[10**v for v in xs]
    pt=p.axes(.8,.8,8.7,3.15,1.1,2.4,xticks=[-3,-2,-1,0,1],yticks=[0,1,2],xlabel=r'$\log_{10}\tau$',ylabel=r'$d_s(\tau)$',xmin=-3)
    one=[8*t/(math.exp(2*t)+1) for t in ts];p.curve(pt,xs,one);p.curve(pt,xs,[2*v for v in one],'dashed,line width=.8pt')
    p.text(11.7,3.7,r'solid: four-cycle\\dashed: product of two',r'font=\small');p.text(11.7,2.2,r'No broad plateau is\\promised at four sites.',r'font=\small');p.text(11.7,.75,r'Finite diagnostic,\\not a dimension proof.',r'font=\small');index.append(p.finish())
    p=Plate('dispersion','Rational enclosures distinguish low-mode error from the theorem bound')
    hs=[R(1,4),R(1,8),R(1,16)];rows=[dispersion_row(v) for v in hs]
    for j,row in enumerate(rows):
        xx=2.2+4.8*j;p.text(xx,4.3,'$h='+tex(row['h'])+'$');p.text(xx,3.3,'error (approx.)',r'font=\small')
        mid=float((row['error_lower']+row['error_upper'])/2)
        p.text(xx,2.65,r'$\simeq '+f'{mid:.9f}'+'$',r'font=\small');p.text(xx,1.65,'bound $h^2/12$',r'font=\small');p.text(xx,1.0,'$'+tex(row['bound'])+'$')
    p.text(7,.05,'Successive error ratios lie strictly between $3.99$ and $4$.',r'font=\small');index.append(p.finish())
    c1,c2,pp,AA=constraints();p=Plate('constraints','Compression can hide a full operator obstruction')
    p.matrix(.7,3.75,AA,cell=.9,title='$[C_1,C_2]$')
    p.matrix(9.8,3.75,pp*AA*pp,cell=.9,title='$P[C_1,C_2]P$')
    p.text(6.9,2.7,r'$P=\diag(1,0,0)$');p.text(6.9,1.4,'$C_1P=C_2P=0$',r'font=\small');p.text(7,.3,'The right matrix is zero by the common-kernel choice, not by operator closure.',r'font=\scriptsize');index.append(p.finish())
    p=Plate('perfect_transfer','One excitation makes an exact four-site journey')
    coords=[(1.5,2.8),(4.5,2.8),(4.5,.7),(1.5,.7)]
    for j in range(4):p.line(*coords[j],*coords[(j+1)%4],'black!70,line width=.7pt')
    for j,(x,y) in enumerate(coords):p.circ(x,y,.24,'draw,fill=white');p.text(x,y,str(j),r'font=\small')
    p.line(*coords[0],*coords[2],'->,dashed,line width=.95pt');p.text(3,4.15,r'$e^{-\ii\pi L/2}=S^2$')
    p.matrix(8.6,3.55,M([1,0,0,0]),cell=.59,title='start')
    p.matrix(11.4,3.55,M([0,0,1,0]),cell=.59,title=r'time $\pi/2$')
    p.text(10.3,.5,r'Target probability after partial\\momentum dephasing: $1-3\eta/4$.',r'font=\small');index.append(p.finish())
    (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('Generated',len(index),'editable vector plates')
if __name__=='__main__':main()
