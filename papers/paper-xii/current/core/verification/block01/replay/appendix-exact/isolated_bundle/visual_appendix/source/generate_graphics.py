#!/usr/bin/env python3
"""Deterministic TikZ drawings of explicit mathematical objects. No raster assets."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'graphics';G.mkdir(exist_ok=True)

def save(name,body,scale='1'):
    (G/f'{name}.tex').write_text(r'\begin{tikzpicture}[x=1cm,y=1cm,font=\small,>=Stealth]'+'\n'+body+'\n'+r'\end{tikzpicture}'+'\n')

def mono(i,j):
    p=[]
    for var,e in [('x',i),('y',j)]:
        if e:p.append(var+(f'^{{{e}}}' if e>1 else ''))
    return ''.join(p) or '1'
# Before/after monomial window, total degree <6 over O.
s=[]
for pos,title,after in [(0,'Before imposing the ideals',False),(6.35,'After imposing $(x^2,y)$',True)]:
    s.append(rf'\node[anchor=west,font=\sffamily\small\bfseries] at ({pos},5.10) {{{title}}};')
    for j in range(6):
        for i in range(6-j):
            X=pos+.75*i;Y=.75*j;keep=i<2 and j==0
            fill='black!12' if (after and keep) else 'white'
            s.append(rf'\draw[fill={fill},draw=black!35] ({X},{Y}) rectangle ++(.69,.69);')
            if after and not keep:
                s.append(rf'\draw[black!25] ({X+.13},{Y+.13}) -- ({X+.56},{Y+.56});\draw[black!25] ({X+.13},{Y+.56}) -- ({X+.56},{Y+.13});')
            else:s.append(rf'\node[font=\scriptsize] at ({X+.345},{Y+.345}) {{${mono(i,j)}$}};')
    s.append(rf'\node[anchor=west,font=\footnotesize] at ({pos},-.46) {{$i+j<6$ shown; coefficients lie in $\mathcal O$.}};')
save('monomial_quotient','\n'.join(s))

# Finite test-ring coefficient arrays.
for name,xlab,ylab,criterion in [('points_slopes','a','c',lambda i,j:i==0 and j==0),('points_curvatures','b','d',lambda i,j:i==j)]:
 s=[]
 for j in range(5):
  for i in range(5):
   X=i*.67;Y=j*.67
   s.append(rf'\draw[black!35,fill={"black!18" if criterion(i,j) else "white"}] ({X},{Y}) rectangle ++(.6,.6);')
   if criterion(i,j):s.append(rf'\fill ({X+.3},{Y+.3}) circle (.055);')
   else:s.append(rf'\node[text=black!35] at ({X+.3},{Y+.3}) {{$\times$}};')
 for j in range(5):
  s.append(rf'\node[font=\footnotesize] at ({j*.67+.3},-.30) {{{j}}};')
  s.append(rf'\node[font=\footnotesize] at (-.30,{j*.67+.3}) {{{j}}};')
 s.append(rf'\node at (1.64,-.72) {{${xlab}$}};\node at (-.72,1.64) {{${ylab}$}};')
 save(name,'\n'.join(s))

s=[]
for row,label,fun in [(1,r'\alpha_j',lambda j:(j*j+1)%5),(0,r'\beta_j',lambda j:(2*j+1)%5)]:
 s.append(rf'\node[anchor=east] at (-.18,{row*.76+.34}) {{${label}$}};')
 for j in range(10):
  s.append(rf'\draw[black!35,fill=black!{4+fun(j)*4}] ({j*.88},{row*.76}) rectangle ++(.80,.67);')
  s.append(rf'\node at ({j*.88+.4},{row*.76+.335}) {{{fun(j)}}};')
for j in range(10):s.append(rf'\node[font=\scriptsize] at ({j*.88+.4},1.87) {{$5^{{{j}}}$}};')
for n in [3,6]:
 x=.88*n-.04
 s.append(rf'\draw[dashed] ({x},-.12)--({x},1.52);\node[font=\scriptsize,anchor=north] at ({x},-.17) {{cut at $5^{n}$}};')
save('adic_digits','\n'.join(s))

# Exact real closed-point shadows, not pictures of all prime ideals.
for name,rot in [('support_axes',False),('support_rotated',True)]:
 s=[r'\draw[->,black!30] (-2.65,0)--(2.7,0);\draw[->,black!30] (0,-2.45)--(0,2.55);']
 if not rot:
  s += [r'\draw[line width=1.4pt] (-2.4,0)--(2.4,0);\draw[line width=1.4pt] (0,-2.2)--(0,2.2);',
        r'\fill (0,0) circle (.085);\node[anchor=west] at (.18,.35) {$\mu=2$};',
        r'\fill (1.65,0) circle (.065);\node[anchor=north] at (1.65,-.15) {$\mu=1$};',
        r'\draw[fill=white] (1.25,1.3) circle (.065);\node[anchor=west] at (1.4,1.3) {$\mu=0$};',
        r'\node[anchor=west,font=\footnotesize] at (.15,-1.7) {$V(x)$};\node[anchor=south,font=\footnotesize] at (-1.6,.1) {$V(y)$};',
        r'\node[anchor=west] at (2.72,0) {$x$};\node[anchor=south] at (0,2.57) {$y$};']
 else:
  s += [r'\draw[line width=1.4pt] (-2.1,-2.1)--(2.1,2.1);\draw[line width=1.4pt] (-2.1,2.1)--(2.1,-2.1);',
        r'\fill (0,0) circle (.085);\node[anchor=west] at (.2,0) {$\mu=2$};',
        r'\node[font=\footnotesize,anchor=south west] at (1.1,1.2) {$a=b$};\node[font=\footnotesize,anchor=south east] at (-1.1,1.2) {$a=-b$};',
        r'\node[anchor=west] at (2.72,0) {$a$};\node[anchor=south] at (0,2.57) {$b$};']
 save(name,'\n'.join(s))

# A diagonal base change intersects both support branches at once.
save('diagonal_slice',r'''
\draw[->,black!30] (-2.25,0)--(2.4,0) node[right] {$x$};
\draw[->,black!30] (0,-2.25)--(0,2.4) node[above] {$y$};
\draw[line width=1.1pt] (-2,0)--(2,0);\draw[line width=1.1pt] (0,-2)--(0,2);
\draw[dashed,line width=.9pt] (-1.85,-1.85)--(1.85,1.85);
\node[anchor=south east,font=\footnotesize] at (1.45,1.6) {$x=y=t$};
\fill (0,0) circle (.08);
\node[anchor=north west,font=\footnotesize] at (.12,-.25) {both relations vanish at $t=0$};
''')
# Exact spectrum of a complete node.
save('node_spectrum',r'''
\node[font=\sffamily\small\bfseries] at (1.6,3.15) {$\operatorname{Spec}R$};
\draw[->,line width=1.1pt] (.1,2.1)--(1.6,.35);
\draw[->,dashed] (3.1,2.1)--(1.6,.35);
\fill (.1,2.1) circle (.09);\draw[fill=white] (3.1,2.1) circle (.09);\fill (1.6,.35) circle (.09);
\node[above=6pt] at (.1,2.1) {$(x)$};\node[above=6pt] at (3.1,2.1) {$(y)$};
\node[below=6pt] at (1.6,.35) {$(x,y)$};
\node[font=\footnotesize,align=center] at (1.6,-.7) {Filled points: support of $R/(x)$.\\Arrows: specialization of prime ideals.};
\node[font=\sffamily\small\bfseries] at (7.6,3.15) {$\operatorname{Spec}T$};
\draw[->,line width=1.1pt] (7.6,2.1)--(7.6,.35);\fill (7.6,2.1) circle (.09);\fill (7.6,.35) circle (.09);
\node[right=8pt] at (7.6,2.1) {$(0)$};\node[right=8pt] at (7.6,.35) {$(y)$};
\node[font=\footnotesize,align=center] at (7.6,-.7) {The quotient retains one generic point\\and the common closed point.};
''')
save('patching_branches',r'''
\draw[->,black!30] (-2.5,0)--(2.7,0) node[right] {$t$};
\draw[->,black!30] (0,-2.1)--(0,2.6) node[above] {$x$};
\draw[line width=1.7pt] (-2.25,0)--(2.25,0);
\draw[dashed,line width=1.05pt] (-1.9,-1.9)--(2.15,2.15);
\draw[densely dotted,line width=1.1pt] (0,-2.0)--(0,2.25);
\fill (0,0) circle (.08);
\node[font=\footnotesize,anchor=north] at (1.7,-.16) {occupied: $x=0$};
\node[font=\footnotesize,anchor=south east] at (1.9,2.08) {missed: $x=t$};
\node[font=\footnotesize,anchor=east] at (-.14,1.2) {slice $t=0$};
''')
save('derived_fibers',r'''
\node[anchor=east] at (-.3,2.25) {point $a$};
\node[anchor=east] at (-.3,1.4) {$\dim H^0(C_a)$};
\node[anchor=east] at (-.3,.55) {$\dim H^1(C_a)$};
\foreach \x/\a in {0/-2,1.5/-1,3/0,4.5/1,6/2}{
\node at (\x+.4,2.25) {$\a$};
\draw[black!35] (\x,1.05) rectangle ++(.8,.7);\draw[black!35] (\x,.2) rectangle ++(.8,.7);
}
\foreach \x in {0,1.5,4.5,6}{\node[text=black!45] at (\x+.4,1.4) {$0$};\node[text=black!45] at (\x+.4,.55) {$0$};}
\fill[black!12] (3,1.05) rectangle ++(.8,.7);\fill[black!12] (3,.2) rectangle ++(.8,.7);
\node at (3.4,1.4) {$1$};\node at (3.4,.55) {$1$};
\draw[decorate,decoration={brace,mirror,amplitude=4pt}] (3,-.05)--(3.8,-.05);
\node[anchor=north,font=\footnotesize] at (3.4,-.27) {the zero differential creates two cohomology groups};
''')
# Actual Jordan chains, separated by the canonical projector.
save('jordan_packets',r'''
\node[font=\sffamily\small\bfseries] at (1.6,2.35) {packet at $z=1$};
\node[font=\sffamily\small\bfseries] at (8.0,2.35) {packet at $z=-1$};
\node at (0,1.45) {$1$};\node at (1.6,1.45) {$\varepsilon$};\node at (3.2,1.45) {$0$};
\draw[->] (.28,1.45)--(1.32,1.45) node[midway,above,font=\scriptsize] {$H-1$};
\draw[->] (1.88,1.45)--(2.92,1.45) node[midway,above,font=\scriptsize] {$H-1$};
\node at (5.5,1.45) {$1$};\node at (7.1,1.45) {$\eta$};\node at (8.7,1.45) {$\eta^2$};\node at (10.3,1.45) {$0$};
\draw[->] (5.78,1.45)--(6.82,1.45) node[midway,above,font=\scriptsize] {$H+1$};
\draw[->] (7.38,1.45)--(8.42,1.45) node[midway,above,font=\scriptsize] {$H+1$};
\draw[->] (8.98,1.45)--(10.02,1.45) node[midway,above,font=\scriptsize] {$H+1$};
\draw[decorate,decoration={brace,mirror,amplitude=5pt}] (-.25,.85)--(1.85,.85);
\draw[decorate,decoration={brace,mirror,amplitude=5pt}] (5.25,.85)--(8.95,.85);
\node[font=\footnotesize] at (.8,.24) {two independent basis vectors};
\node[font=\footnotesize] at (7.1,.24) {three independent basis vectors};
''')
# Stable-core image basis arrays.
for name,kind in [('core_projection','P'),('core_nilpotent','N')]:
 s=[]
 for h in range(5):
  d=3 if h==0 else (1 if kind=='P' else max(3-h,0))
  Y=(4-h)*.65
  s.append(rf'\node[anchor=east,font=\footnotesize] at (-.2,{Y+.27}) {{$h={h}$}};')
  for j in range(3):
   X=.66*j
   s.append(rf'\draw[black!35,fill={"black!16" if j<d else "white"}] ({X},{Y}) rectangle ++(.55,.55);')
   if j<d:s.append(rf'\fill ({X+.275},{Y+.275}) circle (.045);')
   else:s.append(rf'\node[text=black!30] at ({X+.275},{Y+.275}) {{$\times$}};')
 for j in range(3):s.append(rf'\node[font=\footnotesize] at ({.66*j+.275},3.3) {{$e_{j+1}$}};')
 save(name,'\n'.join(s))
# Fixed carrier versus infinite tails.
for name,tail in [('nested_finite',False),('infinite_tail',True)]:
 s=[];dims=[5,4,4,2,1,1]
 cols=8 if tail else 5
 for m in range(1,7):
  Y=(6-m)*.53
  s.append(rf'\node[anchor=east,font=\scriptsize] at (-.12,{Y+.20}) {{$m={m}$}};')
  for j in range(1,cols+1):
   active=(j>=m) if tail else (j<=dims[m-1]);X=(j-1)*.47
   s.append(rf'\draw[black!35,fill={"black!18" if active else "white"}] ({X},{Y}) rectangle ++(.39,.39);')
   if active:s.append(rf'\fill ({X+.195},{Y+.195}) circle (.03);')
  if tail:s.append(rf'\node at ({cols*.47+.1},{Y+.20}) {{$\cdots$}};')
 for j in range(1,cols+1):s.append(rf'\node[font=\scriptsize] at ({(j-1)*.47+.195},3.34) {{$e_{j}$}};')
 save(name,'\n'.join(s))
print(f'Generated {len(list(G.glob("*.tex")))} vector figure sources.')
