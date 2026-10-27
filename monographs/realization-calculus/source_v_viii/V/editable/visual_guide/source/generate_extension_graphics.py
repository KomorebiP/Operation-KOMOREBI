#!/usr/bin/env python3
"""Generate exact-coordinate TikZ diagrams for visual pages 28--39. No model imagery."""
from pathlib import Path
from fractions import Fraction as F
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'graphics'
plates=[]
def put(name,body,options='x=1cm,y=1cm'):
 text='\\begin{tikzpicture}['+options+',>=Stealth,font=\\sffamily\\small]\n'+body+'\n\\end{tikzpicture}\n'
 (OUT/(name+'.tex')).write_text(text);plates.append(name)
def coord(q):
 return str(float(q))
def path(points):
 return ' -- '.join(f'({coord(x)},{coord(y)})' for x,y in points)
body=''
colors=['teal!14','blue!12','orange!17','teal!35','blue!28','orange!35']
for j in range(6):
 for i in range(6):
  k=(i%2)*3+j%3
  body+=f'\\filldraw[fill={colors[k]},draw=white] ({i},{j}) rectangle ({i+1},{j+1});\n'
  body+=f'\\node[font=\\scriptsize] at ({i+.5},{j+.5}) {{$({i%2},{j%3})$}};\n'
body+='\\draw[->] (0,0)--(6.5,0) node[right]{$i$};\\draw[->](0,0)--(0,6.5)node[above]{$j$};'
body+='\\node[anchor=west] at (6.7,4.4){$i=2q_1+r_1$};\\node[anchor=west]at(6.7,3.5){$j=3q_2+r_2$};'
put('ext_lattice',body,'x=.9cm,y=.7cm')
put('ext_frame',r'''
\draw[->] (0,0)--(9.4,0) node[right]{singular value};
\draw[line width=6pt,teal!35] (3,1)--(9,1);
\draw[line width=6pt,black!35] (4,2)--(8,2);
\node[anchor=east]at(2.7,2){original};\node[anchor=east]at(2.7,1){perturbed};
\foreach \x/\s in {3/{3/4},4/1,8/2,9/{9/4}} {\draw(\x,-.12)--(\x,.12);\node[below]at(\x,-.15){$\s$};}
\fill (4,2)circle(2pt);\fill(8,2)circle(2pt);\fill[teal](3,1)circle(2pt);\fill[teal](9,1)circle(2pt);
\draw[<->] (3,2.5)--(4,2.5)node[midway,above]{$\delta$};
\node at (6,-1.0){squared bounds: $9/16\ \le\ \|\widetilde Ex\|^2/\|x\|^2\ \le\ 81/16$};
''','x=.75cm,y=.7cm')
put('ext_tree',r'''
\node[draw,fill=black!4,align=center] (r) at (4,3){root\\$[A,B]=[1/2,2]$};
\node[draw,fill=teal!12,align=center] (l) at (1,1.5){retained\\$[a,b]=[1,1]$};
\node[draw,fill=black!4,align=center] (s) at (7,1.5){split\\$[A,B]=[3/4,5/4]$};
\node[draw,fill=teal!12] (a)at(5.7,0){retained};\node[draw,fill=teal!12](b)at(8.3,0){retained};
\draw[->](r)--(l);\draw[->](r)--(s);\draw[->](s)--(a);\draw[->](s)--(b);
''','x=.9cm,y=.9cm')
body=r'\draw[->](0,0)--(8.4,0)node[right]{$t$};\draw[->](0,0)--(0,4.1)node[above]{value};'
for a,b,jump in [(F(0),F(1,3),False),(F(1,3),F(2,3),True),(F(2,3),F(1),True)]:
 pts=[]
 for k in range(31):
  t=a+(b-a)*F(k,30); val=t*t+(2 if jump else 0)-3*max(F(0),t-F(2,3));pts.append((8*t,F(6,5)*val))
 body+='\\draw[teal,very thick] '+path(pts)+';\n'
pts=[(8*F(k,60),F(6,5)*F(k,60)**2)for k in range(61)]
body+='\\draw[black!65,dashed,thick] '+path(pts)+';\n'
body+=r'\draw[dotted](8/3,0)--(8/3,3.2);\draw[dotted](16/3,0)--(16/3,3.2);\node[below]at(8/3,0){$1/3$};\node[below]at(16/3,0){$2/3$};\node[below]at(8,0){$1$};\node[teal]at(7.6,3.3){$f$};\node[black!65]at(6.7,.4){$s=t^2$};'
put('ext_trace',body,'x=1cm,y=.85cm')
put('ext_amplification',r'''
\draw[->](-3.2,0)--(2,0);\draw[->](0,-.3)--(0,1.8);
\draw[->,line width=1.8pt,teal](0,0)--(0,1)node[above right]{$e=(0,1)$};
\draw[->,line width=1.8pt,orange!85!black](0,0)--(-2,1)node[above left]{$(I-Q)e=(-2,1)$};
\draw[dashed](-2,0)--(-2,1)--(0,1);\node[below]at(-2,0){$-2$};
\node[anchor=west,align=left]at(2.3,.7){$\|e\|=1$\\[5pt]$\|(I-Q)e\|=\sqrt5$};
''','x=1cm,y=1cm')
body=''
M=[[3,1,0],[0,2,1],[1,0,4]];weights=[[0,4,25],[4,0,9],[25,9,0]]
for i in range(3):
 for j in range(3):
  x=j*1.4;y=(2-i)*1.0;col='teal!12'if i==j else('orange!25'if M[i][j]else'black!3')
  body+=f'\\filldraw[fill={col},draw=white]({x},{y})rectangle({x+1.4},{y+1});\\node at({x+.7},{y+.5}){{$ {M[i][j]} $}};\n'
 body+=f'\\node[left]at(0,{2.5-i}){{$a_{i}={ [0,2,5][i]}$}};\n'
for j in range(3):body+=f'\\node[above]at({j*1.4+.7},3){{$b_{j}={[0,2,5][j]}$}};'
body+=r'\node[anchor=west,align=left] at(5,2){off-diagonal squared error\\[6pt]$1\cdot 2^2+1\cdot 3^2+1\cdot 5^2$\\[6pt]$=38$};'
put('ext_overlap',body)
put('ext_location',r'''
\draw[->](0,2.2)--(8.5,2.2)node[right]{$t$};\draw[->](0,2.2)--(0,3.7);
\fill[orange!20](2,2.2)rectangle(2.5,3.4);\draw[very thick,orange!85!black](0,2.2)--(2,2.2)--(2,3.4)--(2.5,3.4)--(2.5,2.2)--(8,2.2);
\node[left]at(0,3.4){$1$};\node[orange!85!black,anchor=west]at(3.2,3.1){step error};
\draw[->](0,0)--(8.5,0)node[right]{$t$};\draw[->](0,0)--(0,1.5);
\draw[very thick,teal](0,0)--(2,0)--(2.5,1.2)--(8,1.2);
\node[left]at(0,1.2){$1/16$};\node[teal,anchor=west]at(3.2,.6){ramp error};
\foreach \y in {0,2.2} {\node[below]at(2,\y){$1/4$};\node[below]at(2.8,\y){$5/16$};\node[below]at(8,\y){$1$};}
''')
put('ext_threshold',r'''
\draw[->](0,0)--(9.4,0)node[right]{$|D_k|$};
\draw[line width=10pt,teal!35](0,.7)--(.5953125,.7);
\draw[line width=10pt,orange!35](7.4046875,.7)--(9,.7);
\draw[dashed,thick](4,-.2)--(4,2.1)node[above]{$\theta=1/25$};
\node[above,align=center]at(.6,1){no-jump\\contrasts};\node[above,align=center]at(8,1){jump\\contrasts};
\draw(.5953125,-.12)--(.5953125,.12);\draw(7.4046875,-.12)--(7.4046875,.12);
\node[below]at(.5953125,-.15){$b_h$};\node[below]at(7.4046875,-.15){$a_{\min}-b_h$};

''','x=.9cm,y=.7cm')
body=r'\draw[->](0,0)--(8.7,0)node[right]{$R$};\draw[->](0,0)--(0,3.2)node[above]{noise term bound};'
for idx,R in enumerate([1,4,16,64]):
 x=1.1+idx*2;v=F(32,125)/[1,2,4,8][idx];y=float(v*10)
 body+=f'\\filldraw[fill=teal!30,draw=teal]({x-.45},0)rectangle({x+.45},{y});\\node[above]at({x},{y}){{$ {v.numerator}/{v.denominator} $}};\\node[below]at({x},0){{$ {R} $}};'
body+=r'\draw[dashed,orange!90!black](0,.8)--(8,.8);\node[anchor=west,orange!90!black]at(8.1,.8){$a_{\min}=2/25$};'
put('ext_repetition',body,'x=.8cm,y=.85cm')
put('ext_haar_margin',r'''
\draw[->](0,0)--(9.4,0)node[right]{coefficient magnitude};
\draw[line width=9pt,teal!35](0,.7)--(2.9,.7);
\draw[line width=9pt,orange!35](7.1,.7)--(9,.7);
\draw[dashed,thick](5,-.2)--(5,2)node[above]{$50/800$};
\node[above]at(1.4,1){no-jump support};\node[above]at(8,1){jump support};
\node[below]at(2.9,-.15){$29/800$};\node[below]at(7.1,-.15){$71/800$};
\draw(2.9,-.1)--(2.9,.1);\draw(7.1,-.1)--(7.1,.1);
''','x=.9cm,y=.75cm')
body=r'\draw[->](0,0)--(8.5,0)node[right]{$u$};\draw[->](0,0)--(0,2.5);\node[anchor=west]at(0,3.5){boundary distance};'
body+=r'\draw[teal,very thick](0,0)--(4,2)--(8,0);\draw[orange!85!black,very thick](0,2)--(4,0)--(8,2);\draw[dashed](0,1)--(8,1);\node[left]at(0,1){$1/4$};\node[left]at(0,2){$1/2$};'
body+=r'\node[below]at(2,0){$1/4$};\node[below]at(4,0){$1/2$};\node[below]at(6,0){$3/4$};\node[below]at(8,0){$1$};\node[teal]at(2.1,2.7){integer grid};\node[orange!85!black]at(6.2,2.7){half-shifted grid};'
put('ext_two_grids',body)
body=r'\draw[->](0,0)--(7,0)node[right]{$n$};\draw[->](0,0)--(0,3.2)node[above]{$x(n)$};'
for n,x in enumerate([0,1,2,3,6,9,12]):
 body+=f'\\draw[teal,thick]({n},0)--({n},{x/4});\\fill[teal]({n},{x/4})circle(2pt);\\node[above]at({n},{x/4}){{$ {x} $}};'
body+=r'\node[anchor=west,align=left]at(7.4,2){$\Delta^2x(2)=2$\\[5pt]all other displayed\\second differences vanish};'
put('ext_differences',body,'x=.85cm,y=.75cm')
(OUT/'EXTENSION_PLATE_INDEX.json').write_text(json.dumps({'generated_tikz':plates,'count':len(plates),'reused_vector_pdf':'annals_gibbs_comparison.pdf','numeric_coordinates':'Exact rational data converted to decimal plotting coordinates; labels and checker retain exact fractions.','notable_display_scale':'ext_location: two distinct labeled vertical axes; upper unit1, lower unit1/16.'},indent=2)+'\n')
print(f'Generated {len(plates)} extension TikZ plates.')
