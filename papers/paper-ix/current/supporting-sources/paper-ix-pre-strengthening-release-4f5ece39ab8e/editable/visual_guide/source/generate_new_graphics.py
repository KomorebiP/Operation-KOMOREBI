#!/usr/bin/env python3
"""Four additional exact, deterministic TikZ plates; no raster assets."""
from __future__ import annotations
import json
from drawing import Plate, OUT
from generate_graphics import grid

def main():
    plates=[]
    p=Plate('31_transported_selectors','One projector in two coordinate systems')
    raw=[[1,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,0,0]]
    trans=[[1,0,0,0],[1,0,0,0],[2,-2,1,0],[6,-6,3,0]]
    p.matrix(.8,3.5,raw,cell=.65,cellw=.8,title=r'$P_{2,0}$')
    p.matrix(5.8,3.5,trans,cell=.65,cellw=.8,title=r'$\widehat P_{2,0}=TP_{2,0}T^{-1}$')
    p.text(11.5,3.0,r'$T:a_n\mapsto a_n+na_{n-1}$','font=\\scriptsize')
    p.text(11.5,2.1,r'$\widehat P^2=\widehat P$')
    p.text(11.5,1.1,r'$\widehat P\ne P$')
    p.text(7,.1,r'A residue projector is conjugated when coordinates change; its raw mask is not reused.','font=\\small')
    plates.append(p.finish())
    p=Plate('32_recurrence_packets','A compressed sequence needs the correct jump')
    grid(p,1.8,3.6,['$q$','$F_{2q}$','$F_{2q+1}$'],['']*7,
         [[f'${q}$' for q in range(7)],['$0$','$1$','$3$','$8$','$21$','$55$','$144$'],['$1$','$2$','$5$','$13$','$34$','$89$','$233$']],cw=1.4,ch=.68)
    p.text(7,4.4,r'$F_{n+2}=F_{n+1}+F_n$')
    p.text(4.2,.65,r'$C=\begin{pmatrix}1&1\\1&0\end{pmatrix}$')
    p.text(9.8,.65,r'$C^2=\begin{pmatrix}2&1\\1&1\end{pmatrix}$')
    p.text(7,-.2,r'Both packets satisfy $b_{q+2}-3b_{q+1}+b_q=0$.','font=\\small')
    plates.append(p.finish())
    p=Plate('33_equation_presentations','The root set does not determine the raw cokernel')
    for x,title,formula,rank,coker in [(.5,'One equation',r'$F(Y)=Y$',r'$J=(1)$',r'$\operatorname{coker}J=0$'),(7.5,'One redundant equation',r'$G(Y)=(Y,0)$',r'$J=\begin{pmatrix}1\\0\end{pmatrix}$',r'$\operatorname{coker}J\cong\mathbb F_5$')]:
        p.rect(x,.4,6,3.7,'draw=black!40,fill=black!3')
        p.text(x+3,3.7,title,'font=\\small\\bfseries')
        p.text(x+3,2.8,formula)
        p.text(x+3,1.95,rank)
        p.text(x+3,.95,coker)
    p.text(7,-.1,r'Both root sets are $Y=0$, but the residual ambient spaces differ.','font=\\small')
    plates.append(p.finish())
    p=Plate('34_compatible_root_path','One parameter, eight compatible residue roots')
    grid(p,1.0,3.55,['$L$','$2^L$','$y_L$'],['']*8,
         [[f'${L}$' for L in range(1,9)],['$2$','$4$','$8$','$16$','$32$','$64$','$128$','$256$'],['$0$','$2$','$2$','$10$','$26$','$26$','$90$','$90$']],cw=1.5,ch=.8)
    p.text(7,4.4,r'$y_L+y_L^2+2=0\pmod{2^L},\qquad y_L\equiv0\pmod2$')
    p.text(7,.45,r'$y_{L+1}\equiv y_L\pmod{2^L}$; the derivative $1+2y_L$ is odd.')
    p.text(7,-.2,r'Repeated representatives are compatible digits, not termination of the completed root.','font=\\small')
    plates.append(p.finish())
    (OUT/'NEW_FIGURE_INDEX.json').write_text(json.dumps({'count':len(plates),'plates':plates,'arithmetic':'Exact integer/Fraction examples; geometry is schematic.'},indent=2)+'\n')
    print('Generated',len(plates),'additional editable vector plates.')

if __name__=='__main__':main()
