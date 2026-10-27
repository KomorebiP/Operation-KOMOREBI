#!/usr/bin/env python3
"""Write exact, editable TikZ schematics for the new visual explanations.
No symbolic engine, raster asset, or external fetch is used.
"""
from pathlib import Path
from math import log
ROOT=Path(__file__).resolve().parent.parent
START=r'''\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth,font=\sffamily\small,
 box/.style={draw=black!60,fill=black!3,rounded corners=2pt,align=center,minimum height=.68cm,inner sep=7pt},
 arrow/.style={->,line width=.8pt},note/.style={font=\sffamily\scriptsize,align=center}]
'''
END='\n\\end{tikzpicture}\n'
P={}
P['ext_paths']=r'''
\node[box] (a) at (0,1.3) {packet 0};\node[box] (b) at (3.6,1.3) {packet 1};\node[box] (c) at (7.2,1.3) {packet 2};
\draw[arrow] (a)--node[above]{$2$}(b);\draw[arrow] (b)--node[above]{$3$}(c);
\node at (0,0){$1$};\node at (3.6,0){$2t$};\node at (7.2,0){$3t^2$};
\node[note] at (3.6,-.9){At $t=1$: $(1,2,3)$\quad\quad At $t=2$: $(1,4,12)$};
'''
P['ext_closure']=r'''
\draw[->,black!40] (-1.8,0)--(1.8,0);\draw[->,black!40] (0,-.25)--(0,1.75);
\draw[arrow,line width=1.2pt] (1.4,0) arc (0:90:1.4);\draw[arrow,line width=1.2pt] (0,1.4) arc (90:180:1.4);
\fill (1.4,0) circle(2pt) node[below]{$(1,0)$};\fill (0,1.4) circle(2pt) node[above]{$(0,1)$};\fill(-1.4,0)circle(2pt)node[below]{$(-1,0)$};
\node[box] at (5.1,1.2){full two-step return: $-1$};
\node[box] at (5.1,-.2){project after each step: $0$};
'''
P['ext_tails']=''
for n in range(6):
 x=n*1.45;h=2.4/(2**n)
 P['ext_tails']+=f'\\fill[black!25] ({x:.3f},0) rectangle ({x+.7:.3f},{h:.4f});\n'
 P['ext_tails']+=f'\\node at ({x+.35:.3f},-.35) {{$n={n}$}};\\node[above] at ({x+.35:.3f},{h:.4f}) {{$'+('1' if n==0 else f'1/{2**n}')+'$};\n'
P['ext_obstruction']=r'''
\node[box] (a) at (0,1.5){$w=e_0-e_1$};\node[box] (b) at (6.1,1.5){$K_\varepsilon w$};
\node[box] (c) at (0,-.2){$Cw=0$};\node[box] (d) at (6.1,-.2){$CK_\varepsilon w=(-1,1)^T/16$};
\draw[arrow](a)--node[above]{$K_\varepsilon$}(b);\draw[arrow](a)--node[left]{$C$}(c);\draw[arrow](b)--node[right]{$C$}(d);
\draw[dashed,arrow](c)--node[above]{?}(d);
\node[note]at(3.05,-1.15){No linear coarse map can make this step: $0$ must map to $0$.};
'''
P['ext_hermite']=r'''
\node[anchor=east] at(-.25,1.7){$t=0$};\node[anchor=east]at(-.25,.5){$t=\log2$};
\fill[black!55](0,1.35)rectangle(2,2.05);\fill[black!20](2,1.35)rectangle(6,2.05);
\node[white]at(1,1.7){$1$};\node at(4,1.7){$2$};
\fill[black!55](0,.15)rectangle(.5,.85);\fill[black!20](.5,.15)rectangle(.75,.85);
\node[note,anchor=west]at(1.1,.5){$1/4+1/8=3/8$};
\node[note]at(3,-.45){Dark: degree 1 energy\qquad Light: degree 2 energy};
'''
P['ext_profiles']=r'''
\node[box] (a) at(0,1.3){state 0\\$(2,1)$};\node[box](b)at(2,1.3){state 1\\$(2,1)$};
\node[box](c)at(4.8,1.3){state 2\\$(1,3)$};\node[box](d)at(7.2,1.3){state 3\\$(1,1)$};
\draw[decorate,decoration={brace,mirror,amplitude=5pt}](-.7,.55)--(2.7,.55)node[midway,below=8pt]{one packet};
\node[note]at(4.8,.1){separate packet};\node[note]at(7.2,.1){separate packet};
\node[note]at(3.6,-.75){Joint likelihood profile $=(\lambda^{(1)}_i,\lambda^{(2)}_i)$};
'''
a=(.75*log(3)-log(2))/(.25*log(2))*8
P['ext_information']=rf'''
\fill[black!25](0,0)rectangle({a:.8f},.7);\fill[black!60]({a:.8f},0)rectangle(8,.7);
\node[above]at(4,.85){{$D(p\Vert q)=\frac14\log2$}};
\node[note]at({a/2:.8f},-.6){{coarse information\\$\frac34\log3-\log2$}};
\node[note]at({(a+8)/2:.8f},-.6){{conditional information\\$\frac54\log2-\frac34\log3$}};
'''
P['ext_cumulants']=r'''
\draw[->](0,0)--(7.8,0);\node[note,anchor=west]at(7.8,0){score};
\fill[black!30](.65,0)rectangle(1.35,.6);\fill[black!45](3.15,0)rectangle(3.85,1.2);\fill[black!60](5.65,0)rectangle(6.35,2.4);
\node[below]at(1,0){$0$};\node[below]at(3.5,0){$1$};\node[below]at(6,0){$2$};
\node[above]at(1,.6){$1/7$};\node[above]at(3.5,1.2){$2/7$};\node[above]at(6,2.4){$4/7$};
\node[note]at(4,-.7){At $t=\log2$: mean $10/7$, variance $26/49$};
'''
P['ext_selection']=r'''
\node[anchor=east]at(0,1.9){rate 2, Jordan};\fill[black!60](.2,1.6)rectangle(6.2,2.2);\node[anchor=west]at(6.35,1.9){$2$};
\node[anchor=east]at(0,.9){rate 1};\fill[black!35](.2,.6)rectangle(.95,1.2);\node[anchor=west]at(1.1,.9){$1/4$};
\node[anchor=east]at(0,-.1){rate 3};\fill[black!20](.2,-.4)rectangle(.533333,.2);\node[anchor=west]at(.7,-.1){$1/9$};
'''
P['ext_trajectory']=r'''
\draw[->](0,0)--(4.6,0)node[right]{$t$};\draw[->](0,0)--(0,2)node[above]{error};
\draw[thick,domain=0:4,samples=35]plot(\x,{(\x/4)^2*1.6});
\node[below]at(4,0){$T$};\node[anchor=west]at(4.15,1.6){$T^2/2$};
\node[box]at(7.3,1.35){interval certificate\\$T^2e^{T^2}$};
\node[note]at(2,-.65){Exact error curve: $t^2/2$};
'''
P['ext_auxiliary']=r'''
\node[box](x)at(0,1){$x$};\node[box](b)at(3.7,1){$y_2$};\node[box](a)at(7.4,1){$y_1$};
\draw[arrow](x)--node[above]{input $1$}(b);\draw[arrow](b)--node[above]{link $1$}(a);
\draw[arrow](a.south)--(7.4,-.5)--node[below]{feedback $1$}(0,-.5)--(x.south);
\node[note]at(3.7,2){decay rate $2$};\node[note]at(7.4,2){decay rate $2$};
'''
P['ext_risks']=r'''
\fill[black!15](0,0)rectangle(3,1);\fill[black!40](3,0)rectangle(5,1);\fill[black!65](5,0)rectangle(8,1);
\node at(1.5,.5){$3/8$};\node at(4,.5){$1/4$};\node[white]at(6.5,.5){$3/8$};
\node[note]at(1.5,-.5){surviving};\node[note]at(4,-.5){cause 1 absorbed};\node[note]at(6.5,-.5){cause 2 absorbed};
\node[note]at(4,1.55){At $t=\log2$: surviving mixture $(2/3,1/3)$};
'''
P['ext_substitution']=r'''
\node[box](a)at(0,1.2){operator defect\\$\Delta_{13}=7\eta$};
\node[box](b)at(6.2,1.2){rational-calculus defect\\$-7\eta/30$};
\draw[arrow](a)--node[above]{$F(z)=(1+z)^{-1}$}(b);
\node[note]at(3.1,-.15){Left inverse factor $1/3$\quad Right inverse factor $1/10$\quad Sign $-$};
\node[note]at(3.1,-.85){At $\eta=0$: both defects vanish exactly};
'''
P['ext_evidence']=r'''
\node[box,text width=2.65cm]at(0,1){inherited formal\\33 scoped results\\saved Lean logs};
\node[box,text width=2.65cm]at(3.45,1){fresh examples\\rational checks\\false controls};
\node[box,text width=2.65cm]at(6.9,1){fresh edition\\PDF build\\page review};
\node[note,text width=9cm]at(3.45,-.5){Separate claims, separate evidence records.\quad No combined proof count.};
'''
(ROOT/'graphics').mkdir(exist_ok=True)
for name,body in P.items(): (ROOT/'graphics'/f'{name}.tex').write_text(START+body+END)
print(f'Wrote {len(P)} extension vector plates.')
