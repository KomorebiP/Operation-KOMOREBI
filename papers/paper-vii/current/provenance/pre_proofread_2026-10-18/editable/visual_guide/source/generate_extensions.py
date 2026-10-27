#!/usr/bin/env python3
"""Deterministic exact-data vector plates. No image generation or curve sampling."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'graphics_extended';OUT.mkdir(exist_ok=True)
plates={
's3':('Isotypic dimensions in the S3 regular representation',r'''
\draw[fill=black!6] (0.5,0.6) rectangle (2.1,2.2);
\draw[fill=black!17] (2.4,0.6) rectangle (4,2.2);
\draw[fill=black!30] (4.3,0.6) rectangle (11.5,2.2);
\node at (1.3,1.4) {$1$};\node at (3.2,1.4) {$1$};\node at (7.9,1.4) {$2\otimes2=4$};
\node[font=\small] at (1.3,2.55) {trivial};\node[font=\small] at (3.2,2.55) {sign};\node[font=\small] at (7.9,2.55) {standard isotypic};
\node[font=\small] at (6,0.1) {$\CC[S_3]\cong\CC\oplus\CC\oplus(\CC^2\otimes\CC^2)$};'''),
'polar':('Exact rational packet rotation and polar normalization',r'''
\draw[->] (1,0.5)--(4,0.5);\draw[->] (1,0.5)--(1,3);
\draw[thick,->] (1,0.5)--(2.8,2.9);\node[font=\small] at (3.8,2.6) {$(3/5,4/5)$};
\node[draw,fill=black!6,align=center] at (8.4,2.3) {$S=(3/5)R$\\$S^*S=(9/25)I$};
\draw[->] (8.4,1.7)--(8.4,1.1);\node[draw,fill=black!18] at (8.4,0.7) {$S(S^*S)^{-1/2}=R$};'''),
'choi':('Choi parity blocks and coherence sectors',r'''
\node[draw,fill=black!8,align=center,minimum width=4cm,minimum height=1.5cm] at (3.2,1.8) {even Choi addresses $00,11$\\$\begin{pmatrix}1&4/5\\4/5&16/25\end{pmatrix}$};
\node[draw,fill=black!20,align=center,minimum width=4cm,minimum height=1.5cm] at (8.5,1.8) {odd Choi addresses $01,10$\\$\operatorname{diag}(9/25,0)$};
\node[font=\small] at (6,0.5) {$\Phi(\ket0\bra1)=(4/5)\ket0\bra1$};'''),
'gram':('One positive syndrome and a total recovery complement',r'''
\node[draw,fill=black!8,align=center] at (2,2) {Gram spectrum\\$(1,0,0)$};
\draw[->] (3.1,2)--(4.7,2);\node[draw,fill=black!20,align=center] at (6,2) {one syndrome\\$Q=P$, rank $2$};
\node[draw,align=center] at (10,2) {unused complement\\$I-P$, rank $1$};
\draw[->] (10,1.5)--(6,0.6);\node[draw,fill=black!8] at (6,0.35) {$\ket0\bra2$: replacement branch};'''),
'defect':('Exact smallest enclosing scalar on two spectral points',r'''
\draw[->] (1,1.6)--(11,1.6);\foreach \x/\t in {3/{9/10},6/{1},9/{11/10}} {\fill (\x,1.6) circle (0.08);\node[below] at (\x,1.5) {$\t$};}
\draw[<->] (3,2.5)--(6,2.5);\draw[<->] (6,2.5)--(9,2.5);
\node[above] at (4.5,2.5) {$1/10$};\node[above] at (7.5,2.5) {$1/10$};
\node[font=\small] at (6,0.45) {one pair: $1/10$; full family $\{I,A\}$: $1/5$};'''),
'stability':('A common spectral gap controls both hidden models',r'''
\node[draw,fill=black!8,align=center] at (2.6,2) {$B=1$, $D=2$\\$\Sigma(3)=1$};
\node[draw,fill=black!20,align=center] at (8.9,2) {$\widetilde B=9/8$, $\widetilde D=17/8$\\$\widetilde\Sigma(3)=81/56$};
\draw[<->] (4.2,2)--(6.9,2);\node[below] at (5.6,1.6) {$25/56\leq21/32$};
\node[font=\small] at (6,0.5) {common hypotheses: $g=9/8$, $\delta=3/4$};'''),
'memory_positive':('Memory coefficients form a hidden-space Gram factor',r'''
\node[draw,fill=black!7,align=center] at (3,2) {hidden energy $1$\\weight $9/25$};
\node[draw,fill=black!20,align=center] at (9,2) {hidden energy $2$\\weight $16/25$};
\draw[->] (3,1.4)--(5,0.6);\draw[->] (9,1.4)--(7,0.6);
\node[draw,align=center] at (6,0.4) {$K(t)=(9/25)e^{-it}+(16/25)e^{-2it}$};'''),
 'transfer_ground':('Three transfer eigenvalues and their exact ground error',r'''
\foreach \x/\h/\t in {2/2.4/{1},6/1.2/{1/2},10/0.6/{1/4}} {\draw[fill=black!15] (\x-0.8,0.5) rectangle (\x+0.8,\h+0.5);\node[above] at (\x,\h+0.5) {$\t$};}
\node[font=\small] at (6,0.1) {$T^n:\quad1,\ 2^{-n},\ 4^{-n}\qquad\|T^n-P_0\|=2^{-n}$};'''),
'heat_limits':('Two different orders of the heat limits',r'''
\node[draw,fill=black!8,align=center] (a) at (2.2,2.4) {fixed finite $N$\\$t\downarrow0$};
\node[draw,fill=black!8] (b) at (9.6,2.4) {$d_N(t)\longrightarrow0$};\draw[->] (a)--(b);
\node[draw,fill=black!20,align=center] (c) at (2.2,0.7) {fixed $t>0$\\$N\longrightarrow\infty$};
\node[draw,fill=black!20,align=center] (d) at (9.6,0.7) {then $t\downarrow0$\\$d_{\rm torus}(t)\longrightarrow1$};\draw[->] (c)--(d);'''),
'constraint_image':('Constraint transport controls the embedded image',r'''
\draw[fill=black!8] (1,0.6) rectangle (5,2.8);\node[align=center] at (3,1.7) {coarse $\CC^3$\\$0\oplus\sigma_a$};
\draw[fill=black!8] (7,0.6) rectangle (10.8,2.8);\draw[fill=black!25] (10.8,0.6) rectangle (12,2.8);
\draw[->] (5.2,1.7)--(6.8,1.7);\node[above] at (6,1.7) {$R$};
\node[align=center] at (8.9,1.7) {embedded image\\same constraints};\node[rotate=90,font=\small] at (11.4,1.7) {new coordinate};
\node[font=\small] at (6,0.15) {transported closure on $\operatorname{im}R$; new complement requires its own test};'''),
'tower_tail':('Exact bounded levels and a separate common-space tail',r'''
\node[draw,fill=black!7,align=center] (a) at (2,2.2) {$\CC^n$\\$H_n=\operatorname{diag}(0,1,1/2,\ldots)$};
\node[draw,fill=black!7,align=center] (b) at (9.5,2.2) {$\CC^{n+1}$\\old energies retained};\draw[->] (a)--node[above] {$R_n$}(b);
\node[draw,fill=black!20,align=center] at (6,0.6) {fixed $\CC^2$: $H_n=\operatorname{diag}(0,1+2^{-n})$\\tail $\|H_n-H\|=2^{-n}$};'''),
 'trace_topology':('Growing rank separates operator norm from trace norm',r'''
\node[draw,fill=black!8,align=center] at (2.8,1.9) {$A_n=P_n/n$\\$n$ equal eigenvalues $1/n$};
\node[draw,fill=black!20,align=center] at (8.8,1.9) {$\|A_n\|=1/n\to0$\\$\|A_n\|_1=\operatorname{Tr}A_n=1$};
\draw[->] (4.7,1.9)--(6.7,1.9);\node[font=\small] at (6,0.45) {positive trace-class control: norm convergence alone does not preserve a trace};''')
}
index=[]
for n,(title,body) in plates.items():
    txt=r'\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth,line cap=round,line join=round]'+'\n'+r'\path[use as bounding box] (0,-.15) rectangle (12.5,3.3);'+'\n'+body+'\n'+r'\end{tikzpicture}'+'\n'
    (OUT/(n+'.tex')).write_text(txt)
    index.append({'name':n,'title':title,'kind':'editable TikZ vector plate','scope':'exact algebraic data; no coordinate sampling as proof'})
(OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
print('Generated',len(index),'exact-data vector plates')
