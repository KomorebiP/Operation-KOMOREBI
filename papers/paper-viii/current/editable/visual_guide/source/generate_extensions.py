#!/usr/bin/env python3
"""Produce four editable TikZ plates from exact, displayed finite data."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'graphics'
PLATES={
'complex_core':r'''\begin{tikzpicture}[font=\sffamily\small]
\node[anchor=west] at (0,3) {$A^*A=\operatorname{diag}(25,4)$};
\draw[->] (0,0)--(8,0) node[right] {retained singular directions};
\draw[->] (0,0)--(0,2.5) node[above] {squared error};
\draw[thick,black!65] (1,2.03)--(3.5,.28)--(6,0);
\foreach \x/\y/\n/\v in {1/2.03/0/29,3.5/.28/1/4,6/0/2/0}{
\fill (\x,\y) circle (2pt);\node[below] at (\x,0) {$\n$};\node[above] at (\x,\y) {$\v$};}
\node[anchor=west] at (0,-.9) {$Q_L^*Q_L=I\qquad Q_L^TQ_L=\operatorname{diag}(-7/25,1)$};
\end{tikzpicture}''',
'inverse_closure':r'''\begin{tikzpicture}[font=\sffamily\small,>=Latex]
\foreach \x/\y/\n in {0/1/0,2/2/1,2/0/2,4/1/3}
\node[draw,circle,minimum size=8mm] (n\n) at (\x,\y) {$\n$};
\draw[->,thick] (n0)--node[above left] {$1$}(n1);
\draw[->,thick] (n0)--node[below left] {$1$}(n2);
\draw[->,thick] (n1)--node[above right] {$1$}(n3);
\draw[->,thick] (n2)--node[below right] {$-1$}(n3);
\draw[->,dashed,rounded corners=5pt] (n0.north)--(0,2.6)--(4,2.6)--(n3.north);
\node[anchor=south] at (2,2.8) {closure permits $0\to3$};
\node[anchor=west] at (5,1.8) {$K^2=0$};
\node[anchor=west] at (5,1) {$A^{-1}=I-K$};
\node[anchor=west] at (5,.2) {$(A^{-1})_{30}=0$};
\end{tikzpicture}''',
'shared_family':r'''\begin{tikzpicture}[font=\sffamily\small,>=Latex]
\draw[->] (0,0)--(7,0) node[right] {$r_2$};
\draw[->] (0,0)--(0,4.5) node[above] {modeled cost};
\draw[thick] (0,.6)--(4,3.4) node[right] {$6+7r_2$ : keep};
\draw[thick,dashed] (0,1)--(4,1.8) node[right] {$10+2r_2$ : split};
\draw[dotted] (.8,0)--(.8,1.16);\fill (.8,1.16) circle (2pt);
\node[below] at (.8,0) {$4/5$};
\foreach \x in {0,2,3,4}{\draw (\x,0)--(\x,-.08);\node[below] at (\x,-.1) {$\x$};}
\draw[dotted] (3,0)--(3,2.7);\fill (3,2.7) circle (2pt);\fill (3,1.6) circle (2pt);
\node[above left] at (3,2.7) {$27$};\node[below right] at (3,1.6) {$16$};
\end{tikzpicture}''',
'quantization':r'''\begin{tikzpicture}[font=\sffamily\small]
\node[anchor=west] at (0,2.7) {actual error sum\quad versus\quad ceiling envelope};
\draw[->] (0,0)--(8,0) node[right] {error};
\foreach \x/\v in {0/0,2/{1/10},4/{1/5}}{\draw (\x,0)--(\x,-.1);\node[below] at (\x,-.1) {$\v$};}
\draw[dotted] (2,0)--(2,2.2);\node[above] at (2,2.2) {budget};
\draw[very thick] (0,1.6)--(2.8,1.6);\fill (2.8,1.6) circle (2pt);
\node[right] at (4.3,1.6) {$7/50>1/10$};
\draw[very thick] (0,.8)--(1.6,.8);\fill (1.6,.8) circle (2pt);
\node[right] at (4.3,.8) {$2/25\le1/10$};
\draw[thick,dashed] (0,1.3)--(4,1.3);\draw[thick,dashed] (0,.5)--(4,.5);
\node[anchor=west] at (0,-1.1) {Both ceiling envelopes are $h(1+1)=1/5$.};
\end{tikzpicture}'''}
def main():
    OUT.mkdir(exist_ok=True);rows=[]
    for page,(name,src) in enumerate(PLATES.items(),29):
        p=OUT/(name+'.tex');p.write_text(src+'\n');rows.append({'name':name,'visual_page':page,'kind':'editable TikZ vector plate','drawing_coordinates':'exact rational scaling of displayed finite data','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'source/EXTENSION_FIGURE_INDEX.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Generated four exact-data vector plates.')
if __name__=='__main__':main()
