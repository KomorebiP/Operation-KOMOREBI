#!/usr/bin/env python3
"""Exact-data, deterministic TikZ plates for Paper IX's visual appendix.

All input mathematics is computed in models.py and checked independently in
checks/verify_examples.py. Plot positions are illustrative real coordinates,
not embeddings of the p-adic metric. No external images or random inputs.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from drawing import Plate,tex,OUT
from models import *


def grid(p,x,y,rows,cols,entries,cw=.62,ch=.45,shade=None):
    """Top-left indexed table; entries are already typeset strings."""
    for j,c in enumerate(cols):p.text(x+(j+.5)*cw,y+.25,str(c),'font=\\scriptsize')
    for i,r in enumerate(rows):
        p.text(x-.13,y-(i+.5)*ch,str(r),'anchor=east,font=\\scriptsize')
        for j in range(len(cols)):
            fill=shade(i,j) if shade else 'black!4'
            p.rect(x+j*cw,y-(i+1)*ch,cw,ch,'draw=black!25,fill='+fill+',line width=.3pt')
            p.text(x+(j+.5)*cw,y-(i+.5)*ch,entries[i][j],'font=\\scriptsize')


def main():
    OUT.mkdir(parents=True,exist_ok=True);plates=[]
    def done(p):plates.append(p.finish())
    p=Plate('01_three_precisions','Three distinct kinds of precision')
    for x,title,formula,second in [(0.3,'Sequence address',r'$k=Nq+r$',r'$k\bmod N=r$'),(4.95,'Arithmetic depth',r'$a\equiv b\pmod{p^L}$',r'$v_p(a-b)\ge L$'),(9.6,'Lifting depth',r'$x_{L+1}=x_L+p^Lt$',r'$r_L+J_Lt=0\quad\text{in }\mathbb F_p$')]:
        p.rect(x,.6,4.1,3.5,'draw=black!50,fill=black!3')
        p.text(x+2.05,3.7,title,'font=\\small\\bfseries')
        p.text(x+2.05,2.5,formula)
        p.text(x+2.05,1.25,second,'font=\\scriptsize')
    p.text(7,0,r'An address is not a modulus. A one-step lift is not yet an infinite branch.','font=\\small')
    done(p)
    p=Plate('03_residue_balls','Dyadic balls are shared low-order digits')
    vals=[1,9,13]
    for i,n in enumerate(vals):
        p.text(.6,3.55-i*1.02,f'$n={n}$','anchor=west')
        for j in range(5):
            p.rect(2+j*.9,3.18-i*1.02,.85,.72,'draw=black!40,fill='+('black!15' if (n>>j)&1 else 'white'))
            p.text(2.425+j*.9,3.54-i*1.02,str((n>>j)&1))
    for j in range(5):p.text(2.425+j*.9,4.22,f'$2^{j}$','font=\\scriptsize')
    p.text(4.3,-.03,'Read low-order digits from left to right.','font=\\scriptsize')
    p.text(10.1,3.8,r'$v_2(9-1)=3$')
    p.text(10.1,3.05,r'$|9-1|_2=1/8$')
    p.text(10.1,1.9,r'$v_2(13-1)=2$')
    p.text(10.1,1.15,r'$|13-1|_2=1/4$')
    p.text(10.1,.3,r'$1,9\in 1+8\mathbb Z_2$','font=\\small')
    done(p)
    p=Plate('04_selectors','Twelve addresses and their dyadic-odd coordinates')
    rows=[r'$r\bmod4=0$','$1$','$2$','$3$'];cols=[r'$r\bmod3=0$','$1$','$2$']
    a=[[f'${crt_pair(i,4,j,3)}$' for j in range(3)] for i in range(4)]
    grid(p,1.7,3.65,rows,cols,a,cw=1.3,ch=.72)
    p.text(8.5,3.35,r'$\mathbb Z/12\mathbb Z\cong\mathbb Z/4\mathbb Z\times\mathbb Z/3\mathbb Z$')
    p.text(8.6,2.2,r'$P_{2,1}=P_{4,1}+P_{4,3}$')
    p.text(8.6,1.15,r'$P_{12,7}=P_{4,3}P_{3,1}$')
    p.text(7,.05,'Every address appears exactly once; the selectors keep the original index set.','font=\\small')
    done(p)
    p=Plate('05_hurwitz','Ordinary versus Hurwitz multiplication')
    grid(p,1.15,3.55,['ordinary','Hurwitz'],[f'${n}$' for n in range(7)],[[f'${n+1}$' for n in range(7)],[f'${2**n}$' for n in range(7)]],cw=1.4,ch=.85)
    p.text(6.6,4.3,r'$a_n=b_n=1\qquad\text{coefficient index }n$')
    p.text(4,.95,r'$[t^n](A B)=\sum_{r=0}^n a_r b_{n-r}$')
    p.text(10,.95,r'$(a\star b)_n=\sum_{r=0}^n\binom nr a_r b_{n-r}$')
    p.text(7,-.05,r'At $n=3$, the weights $1,3,3,1$ produce $8$, not $4$.','font=\\small')
    done(p)
    p=Plate('06_triangular','The actual Euler-packet recurrence')
    N,j=6,3
    A=[[choose(N*n+j,N*q) if q<=n else 0 for q in range(3)]for n in range(3)]
    p.matrix(.7,3.65,A,cell=.78,cellw=1.18,title=r'$T_{nq}=\binom{6n+3}{6q}$')
    p.text(4.55,2.45,r'$\cdot$','font=\\Large')
    p.matrix(5,3.65,[[v] for v in euler_packet(6,3,2)],cell=.78,cellw=2,title=r'$(C_{6,3}(q))$')
    p.text(7.6,2.45,'$=$','font=\\Large')
    p.matrix(8.2,3.65,[[1],[0],[0]],cell=.78,cellw=1,title='target')
    p.text(11.5,3.1,r'$C(0)=1$')
    p.text(11.5,2.2,r'$U(0)=3!=6$')
    p.text(7,.2,r'Positive diagonal entries permit rational division; they need not be units modulo $p$.','font=\\small')
    done(p)
    p=Plate('07_normalization','One factorial changes the precision')
    p.text(3.8,4.05,'Normalized packet','font=\\small\\bfseries')
    p.text(10.3,4.05,'Original coefficients','font=\\small\\bfseries')
    p.text(3.8,3.1,r'$C_{6,3}(2)-C_{6,3}(1)=\dfrac{64}{455}$')
    p.text(10.3,3.1,r'$U_{6,3}(2)-U_{6,3}(1)=\dfrac{384}{455}$')
    p.text(3.8,2.15,r'$v_3=0$','font=\\Large')
    p.text(10.3,2.15,r'$v_3=1$','font=\\Large')
    for x,digits in [(1.8,0),(8.3,1)]:
        for r in range(3):
            p.rect(x+r*1.05,.95,.95,.7,'draw=black!40,fill='+('black!22' if r<digits else 'white'))
            p.text(x+r*1.05+.475,1.3,f'${r+1}$','font=\\scriptsize')
    p.text(7,.15,r'$U=3!C\quad\Longrightarrow\quad v_3(\Delta U)=v_3(\Delta C)+1$')
    done(p)
    p=Plate('08_newton','A finite difference triangle')
    a=[3**n for n in range(6)];tri=difference_table(a)
    for k,row in enumerate(tri):
        p.text(.8,3.85-k*.65,rf'$\Delta^{k}$','anchor=east,font=\\scriptsize')
        for j,x in enumerate(row):
            xx=1.55+k*.43+j*1.15
            p.rect(xx-.44,3.59-k*.65,.89,.52,'draw=black!30,fill='+('black!17' if j==0 else 'white'))
            p.text(xx,3.85-k*.65,f'${x}$','font=\\scriptsize')
    p.text(10.7,3.1,r'$c_k=2^k$')
    p.text(10.7,2.1,r'$3^n=\sum_{k=0}^n2^k\binom nk$')
    p.text(10.7,.8,r'Left edge: Newton coefficients.\\Each next row: adjacent difference.','font=\\scriptsize')
    done(p)
    p=Plate('09_cancellation','The least summand valuation is only a bound')
    p.text(3.7,3.8,'Cancellation in arithmetic','font=\\small\\bfseries')
    p.text(3.7,2.8,r'$2+6=8$','font=\\Large')
    p.text(3.7,1.8,r'$\min\{v_2(2),v_2(6)\}=1$')
    p.text(3.7,.95,r'$v_2(8)=3$')
    p.line(7,.6,7,4.2,'black!30')
    p.text(10.6,3.8,'The affine Mahler kernel','font=\\small\\bfseries')
    p.text(10.6,2.7,r'$\Theta_{2,1}(3,2)=[z^3](1+z)(2z+z^2)^2$','font=\\scriptsize')
    p.text(10.6,1.8,r'$=4+4=8$')
    p.text(10.6,.85,r'candidate lower bound $2$; actual order $3$','font=\\scriptsize')
    done(p)
    p=Plate('10_standard_window','The standard address window')
    data=[[f'${residue(c,5,1)}$'for c in euler_packet(10,j,8)]for j in range(5)]
    grid(p,1.1,3.8,[f'$j={j}$'for j in range(5)],[f'${n}$'for n in range(9)],data,cw=1.22,ch=.62,shade=lambda i,j:'black!18' if j==0 else('black!7'if j%2 else'white'))
    p.text(6.7,4.45,r'$p=5,\ m=2,\ N=10\qquad C_{10,j}(n)\pmod5$')
    p.text(7,-.05,r'All five addresses agree. The sufficient row period $h=2$ begins at $n=1$, not $n=0$.','font=\\small')
    done(p)
    p=Plate('11_two_indices','A row period must be converted to ordinary degree')
    for n in range(7):
        xx=1+n*1.75;p.circ(xx,2.75,.07)
        p.text(xx,3.23,f'${n}$');p.text(xx,2.1,f'${6*n}$')
    p.text(.55,3.92,'packet row $n$','anchor=west,font=\\scriptsize')
    p.text(.55,1.45,'ordinary degree $6n$','anchor=west,font=\\scriptsize')
    p.line(2.75,3.65,8,3.65,'<->,line width=1pt');p.text(5.38,4.2,r'$T=3$ rows')
    p.line(2.75,1.15,8,1.15,'<->,line width=1pt');p.text(5.38,.55,r'$NT=18=\operatorname{lcm}(2,2)\,3^2$ degrees')
    p.text(12.3,.5,r'$p=3$\\$m=2$\\$r=2$','font=\\scriptsize')
    done(p)
    p=Plate('12_unit_coordinates','Finite units have different odd and dyadic coordinates')
    p.text(3.5,4,'Odd-prime modulus $125$','font=\\small\\bfseries')
    p.text(3.5,3,r'$2=57\cdot11\pmod{125}$')
    p.text(3.5,2,r'$57^4=1\pmod{125}$')
    p.text(3.5,1,r'$57\equiv2,\quad11\equiv1\pmod5$')
    p.line(7,.5,7,4.2,'black!30')
    p.text(10.55,4,'Dyadic modulus $32$','font=\\small\\bfseries')
    p.text(10.55,3,r'$3=(-1)\cdot29\pmod{32}$')
    p.text(10.55,2,r'$29\equiv1\pmod4$')
    p.text(10.55,1,r'$+1\equiv-1\pmod2$')
    p.text(7,.03,'Modulo four retains the sign that modulo two cannot distinguish.','font=\\small')
    done(p)
    p=Plate('13_displacements','Exact displacement orders across four addresses')
    Ts=[1,2,3,4,8,16];d=[1,1,5,3]
    entries=[[f'${val(T,2)+dj}$'for T in Ts]for dj in d]
    grid(p,1.4,3.65,[f'$j={j}$'for j in range(4)],[f'$T={T}$'for T in Ts],entries,cw=1.55,ch=.72)
    p.text(7,4.35,r'$v_2(U_j(n+T)-U_j(n))=d_j+v_2(T)$')
    p.text(7,.2,r'$d=(1,1,5,3)\qquad\text{every row }n\ge0,\text{ every }T>0$')
    done(p)
    p=Plate('14_periods','How precision changes the least positive packet period')
    d=[1,1,5,3];entries=[[f'${2**max(0,r-dj)}$'for r in range(1,11)]for dj in d]
    grid(p,1.25,3.6,[f'$j={j}$'for j in range(4)],[f'${r}$'for r in range(1,11)],entries,cw=1.17,ch=.73,shade=lambda i,j:'black!18'if j+1<=d[i]else'white')
    p.text(7,4.38,r'Modulus $2^r$; columns show $r$, cells show the least positive row period.')
    p.text(7,.15,r'$j=2:\quad U_2(n)\equiv2\pmod{32}\quad\text{but period grows beyond that precision.}$','font=\\small')
    done(p)
    p=Plate('15_isometries','Four finite shadows of dyadic isometries')
    for j in range(4):
        x=.65+j*3.4;data=scaled_packet_map(j,3)
        p.text(x+1.28,4.23,f'$j={j}$')
        for n,a in enumerate(data):
            for b in range(8):p.rect(x+b*.32,3.78-(n+1)*.37,.32,.37,'draw=black!20,fill='+('black!60'if b==a else'white'))
            p.text(x-.08,3.78-(n+.5)*.37,str(n),'anchor=east,font=\\tiny')
        p.text(x+1.28,.38,r'row $n$, column $f_j(n)$','font=\\scriptsize')
    p.text(7,-.12,r'$f_j(n)=(U_j(n)-j!)/2^{d_j}\pmod8$; each row and column has one selected entry.','font=\\small')
    done(p)
    p=Plate('16_odd_tower','Alternating-power reconstruction of the classical Euler number')
    terms=odd_terms(3,4);partial=[];v=0
    for a in terms:v+=a;partial.append(v)
    rows=[f'$m={m}$'for m in range(5)]
    entries=[[f'${terms[m]}$',f'${partial[m]}$']for m in range(5)]
    grid(p,2.1,3.85,rows,['summand','partial sum'],entries,cw=3.2,ch=.6)
    p.text(11.0,3.2,r'$p=3,\ n=4$')
    p.text(11,2.15,r'$E_8=1385$')
    p.text(11,.95,r'$v_3(\text{tail})\ge2M+2$','font=\\scriptsize')
    p.text(7,.05,'Large ordinary magnitudes can still agree to high prime-adic precision.','font=\\small')
    done(p)
    p=Plate('17_sharp_tower','Each retained classical dyadic layer buys four guaranteed digits')
    rows=[f'$M={m}$'for m in range(6)]
    es=[[f'${m+1}$',f'${4*m+3}$',f'${tex(kappa(m+1))}$']for m in range(6)]
    grid(p,1.35,4.0,rows,['first omitted row',r'$v_2(\mathrm{error})$','exact first omitted error'],es,cw=3.7,ch=.58)
    p.text(7,-.05,r'At $n=M+1$ only one term is missing: $E_{2M+2}-T_M(M+1)=\kappa_{M+1}$.','font=\\small')
    done(p)
    p=Plate('18_row_weights','Row-dependent weights improve the uniform precision')
    for n in range(1,9):
        p.text(.55,4.13-(n-.5)*.48,f'${n}$','font=\\scriptsize')
        for m in range(1,9):
            w=4*m-1+val(choose(2*n,2*m),2)if m<=n else None
            p.rect(1+(m-1)*.61,4.13-n*.48,.61,.48,'draw=black!25,fill='+('white'if w is None else f'black!{min(45,6+w)}'))
            if w is not None:p.text(1+(m-.5)*.61,4.13-(n-.5)*.48,f'${w}$','font=\\scriptsize')
    for m in range(1,9):p.text(1+(m-.5)*.61,4.46,f'${m}$','font=\\scriptsize')
    p.text(9.9,4.25,'Actual tails at row $n=6$','font=\\small\\bfseries')
    vals=[val(classical_euler(6)[6]-dyadic_truncation(6,M),2)for M in range(6)]
    grid(p,7.2,3.65,['$M$','$v_2$'],['']*6,[[f'${i}$'for i in range(6)],[f'${v}$'for v in vals]],cw=.95,ch=.75)
    p.text(9.9,1.25,r'Uniform: $4M+3$.\\Full depth $M\ge6$: error $0$.','font=\\small')
    p.text(7,-.25,r'Left: $v_2(S_m(n))=4m-1+v_2\binom{2n}{2m}$. Blank cells have $m>n$.','font=\\scriptsize')
    done(p)
    p=Plate('19_root_digits','The next root digit is a linear residual correction')
    rows=lift_univariate([-2,0,1],7,3,1,5)
    entries=[[f'${r[k]}$'for k in ['depth','x','residual','jacobian','digit','next']]for r in rows]
    grid(p,.85,3.7,['']*5,['$L$','$x_L$',r'$r_L\bmod7$',r'$J\bmod7$','$t$','$x_{L+1}$'],entries,cw=2,ch=.62)
    p.text(7,4.43,r'$F(X)=X^2-2,\quad p=7,\quad x_1=3$')
    p.text(7,.15,r'$x_{L+1}=x_L+7^Lt,\qquad r_L+6t=0\pmod7$')
    done(p)
    p=Plate('20_torsors','Nine correcting digits form one affine kernel fiber')
    J=[[1,1,0],[0,0,0]];fiber=correction_fiber(J,[-1,0],3)
    for a,b,c in fiber:
        x=1.5+a*1.6;y=1+c*.93;p.circ(x,y,.22,'draw,fill=black!15');p.text(x,y,f'${a}{b}{c}$','font=\\scriptsize')
    p.text(3.1,4.05,r'$t=(a,1-a,c)\quad\text{in }\mathbb F_3^3$')
    p.text(10.1,3.7,r'$J=\begin{pmatrix}1&1&0\\0&0&0\end{pmatrix}$')
    p.text(10.1,2.6,r'$r=(-1,0):\quad \#T_r=3^{3-1}=9$')
    p.text(10.1,1.7,r'$r=(-1,1):\quad T_r=\varnothing$')
    p.text(10.1,.8,r'$\#\operatorname{coker}J=3^{2-1}=3$')
    p.text(3.1,.25,'Rows vary $c$; columns vary $a$.','font=\\scriptsize')
    done(p)
    p=Plate('21_shared','Separately attainable observations need a common label')
    # Reorder by common b to reveal exact three-block fiber product.
    aa=[(a,b)for b in range(3)for a in range(3)];bb=[(b,c)for b in range(3)for c in range(3)]
    for i,(a,b)in enumerate(aa):
        for j,(bp,c)in enumerate(bb):p.rect(.85+j*.39,3.83-(i+1)*.39,.39,.39,'draw=black!25,fill='+('black!50'if b==bp else'white'))
    p.text(2.6,4.3,r'$J(a,b,c)=(a,b),\quad K(a,b,c)=(b,c)$','font=\\scriptsize')
    p.text(9.7,3.4,r'$\ker J+\ker K=\{(a,0,c)\}$')
    p.text(9.7,2.5,r'$C(J,K)\cong\mathbb F_3\quad\text{via }b$')
    p.text(9.7,1.45,r'$27$ of $81$ output pairs are compatible.')
    p.text(9.7,.45,'A common correction requires equal middle coordinates.','font=\\scriptsize')
    done(p)
    p=Plate('22_dead_branches','A finite root can lead to a dead branch')
    for x,title in [(3.8,r'$X^2-5$'),(10.3,r'$X^2-17$')]:p.text(x,4.15,title,'font=\\small\\bfseries')
    p.text(.1,3.3,'mod $2$','anchor=west,font=\\scriptsize');p.text(.1,2.1,'mod $4$','anchor=west,font=\\scriptsize');p.text(.1,.8,'mod $8$','anchor=west,font=\\scriptsize')
    p.circ(3.8,3.3,.25,'draw,fill=black!10');p.text(3.8,3.3,'$1$')
    for xx,n in[(2.8,1),(4.8,3)]:
        p.line(3.8,3.03,xx,2.37);p.circ(xx,2.1,.25,'draw,fill=black!10');p.text(xx,2.1,f'${n}$');p.line(xx,1.83,xx,1.1,'dashed');p.text(xx,.75,r'$\varnothing$')
    p.circ(10.3,3.3,.25,'draw,fill=black!10');p.text(10.3,3.3,'$1$')
    for xx,n in[(9.3,1),(11.3,3)]:
        p.line(10.3,3.03,xx,2.37);p.circ(xx,2.1,.25,'draw,fill=black!10');p.text(xx,2.1,f'${n}$')
        for xxx,m in[(xx-.6,n),(xx+.6,n+4)]:p.line(xx,1.83,xxx,1.03);p.circ(xxx,.78,.24,'draw,fill=black!10');p.text(xxx,.78,f'${m}$','font=\\scriptsize')
    p.text(7,-.15,'Same initial parity and derivative; different later residual obstructions.','font=\\small')
    done(p)
    p=Plate('23_prescribed','A prescribed parameter can be the entire obstruction')
    p.text(7,4.1,r'$F(Y,T)=T,\quad p=2,\quad x=(0,0),\quad L=1$')
    p.text(7,3.25,r'$DF=(\,0\ \ 1\,),\qquad J_Y=0,\qquad K_T=1$')
    for x,v in[(1.25,0),(8.2,1)]:
        p.rect(x,.45,4.7,2.2,'draw=black!40,fill=black!3');p.text(x+2.35,2.15,f'parameter digit $v={v}$')
        p.text(x+2.35,1.35,r'$T=0:\ (Y,T)=(0,0),(2,0)$'if v==0 else r'$T=2:\ F(Y,T)=2\ne0\pmod4$','font=\\small')
        p.text(x+2.35,.77,'two next roots'if v==0 else'no next root','font=\\small\\bfseries')
    done(p)
    p=Plate('24_root_chart','A finite root chart remembers every parameter residue')
    a=graph_roots(32)
    for t,y in a:
        xx=1.4+t/2*.3;yy=3.95-y/2*.23
        p.rect(xx,yy-.22,.29,.22,'fill=black!55,draw=black!55')
    for z in [0,8,16,24,30]:
        p.text(1.55+z/2*.3,4.2,f'${z}$','font=\\scriptsize');p.text(1.2,3.84-z/2*.23,f'${z}$','anchor=east,font=\\scriptsize')
    p.text(3.7,-.08,r'columns $t$, rows even $y$; modulus $32$','font=\\scriptsize')
    p.text(10.2,3.7,r'$y+y^2+t=0$')
    p.text(10.2,2.65,r'$\psi(T)=-T-T^2-2T^3-5T^4-\cdots$','font=\\small')
    p.text(10.2,1.45,r'$D\psi(0)=-1$')
    p.text(10.2,.55,'The grid is not a real-plane curve.','font=\\scriptsize')
    done(p)
    p=Plate('25_weighted_lift','A nonunit derivative costs digits but can still lift')
    p.text(7,4.2,r'$F(X)=X^2-17,\quad a=1,\quad J=2,\quad s=1,\quad r=4>2s$')
    p.text(3.4,3.35,r'$x=105\pmod{256}$');p.text(10.4,3.35,r'$x=233\pmod{256}$')
    for xc,nums in[(3.4,[105,361]),(10.4,[233,489])]:
        for xx,x in[(xc-1,nums[0]),(xc+1,nums[1])]:
            p.line(xc,2.98,xx,2.1,'->');p.text(xx,1.7,f'${x}$');p.text(xx,.97,'fails mod $512$'if x*x%512!=17 else'root mod $512$','font=\\scriptsize')
    p.text(7,.07,r'Unique root in $1+4\mathbb Z_2$ does not mean a unique finite residue at each depth.','font=\\small')
    done(p)
    p=Plate('26_root_motion','First-order motion must include the parameter forcing')
    p.text(7,4.12,r'$F(Y,T)=Y+T,\quad G=F+4,\quad T=4$')
    rows=['correct','omit parameter','reverse parameter sign']
    entries=[[r'$-4(1+1)=-8$',r'$0$'],[r'$-4$',r'$4\notin16\mathbb Z_2$'],[r'$0$',r'$8\notin16\mathbb Z_2$']]
    grid(p,4.4,3.25,rows,['predicted $y$','error from exact root'],entries,cw=3.8,ch=.82)
    p.text(7,.05,r'$\delta y=-p^M J^{-1}(H(a)+Kv)+\varepsilon$; both forcing terms are required.','font=\\small')
    done(p)
    p=Plate('27_inverse_weight','Augmentation preserves the inverse weight')
    B=[[2,0,1],[0,8,3],[0,0,1]];C=[[4,0,-4],[0,1,-3],[0,0,8]]
    p.matrix(.5,3.35,B,cell=.7,cellw=.86,title=r'$B=\begin{pmatrix}J&K\\0&1\end{pmatrix}$')
    p.matrix(4.5,3.35,C,cell=.7,cellw=.86,title=r'$C=8B^{-1}$')
    p.text(10.8,3.15,r'$CB=BC=8I$')
    p.text(10.8,2.25,r'$s=3$')
    p.text(10.8,1.25,r'$v_2(\det J)=4$')
    p.text(7,.15,'The largest inverse-denominator weight, not the sum, controls this certificate.','font=\\small')
    done(p)
    p=Plate('28_crt_limit','Every finite test passes without a single global integer')
    ns=[crt_pair(0,2**r,1,3**r)for r in range(1,7)]
    grid(p,1.2,3.65,['$2^r$','$3^r$','$n_r$'],[f'$r={r}$'for r in range(1,7)],[[f'${2**r}$'for r in range(1,7)],[f'${3**r}$'for r in range(1,7)],[f'${x}$'for x in ns]],cw=1.92,ch=.79)
    p.text(7,4.38,r'$n_r\equiv0\pmod{2^r},\qquad n_r\equiv1\pmod{3^r}$')
    p.text(7,.15,r'Compatible residues converge to $(0,1)\in\mathbb Z_2\times\mathbb Z_3$, not to a diagonal integer.','font=\\small')
    done(p)
    p=Plate('29_synthesis','From an Euler approximation to a polynomial residue root')
    vals=[('exact target',r'$E_8=1385$'),('depth-one truncation',r'$T_1(4)=-91019/45$'),('common forcing',r'$2E_8\equiv2T_1(4)\equiv210\pmod{256}$'),('solved residue',r'$y=14:\quad y+y^2=210$')]
    for i,(lab,eq)in enumerate(vals):
        yy=3.7-i*.97;p.text(.6,yy,lab,'anchor=west,font=\\scriptsize');p.rect(4.15,yy-.34,9.0,.7,'draw=black!25,fill=black!4');p.text(8.65,yy,eq)
    p.text(7,-.2,'The even root is unique modulo 256. The odd root belongs to a different residue ball.','font=\\small')
    done(p)
    (OUT/'FIGURE_INDEX.json').write_text(json.dumps({'count':len(plates),'plates':plates,'provenance':'Exact finite data from models.py. TikZ coordinate placements are schematic, not extra mathematical evidence.'},indent=2)+'\n')
    print('Generated',len(plates),'editable vector plates.')
if __name__=='__main__':main()
