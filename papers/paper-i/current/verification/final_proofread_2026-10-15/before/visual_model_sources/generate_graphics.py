#!/usr/bin/env python3
"""Write deterministic TikZ plates from the exact models (no generated artwork)."""
from pathlib import Path
import math
import sympy as sp
from models import data,krylov,unit,orbit,matrix_unit
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'visual_graphics'; OUT.mkdir(exist_ok=True)
d=data()
STYLE=r'''\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,
 every node/.style={font=\sffamily\small},line cap=round,line join=round]
'''
def save(name,lines):
    (OUT/(name+'.tex')).write_text(STYLE+'\n'.join(lines)+'\n\\end{tikzpicture}\n')
def node(x,y,text,opts=''):
    return rf'\node[{opts}] at ({x:.4f},{y:.4f}) {{{text}}};'
def line(x,y,u,v,opts=''):
    return rf'\draw[{opts}] ({x:.4f},{y:.4f}) -- ({u:.4f},{v:.4f});'
def grid(a,x=0,y=0,c=.58,labels=None,top=None):
    a=sp.Matrix(a); L=[]
    for i in range(a.rows):
        for j in range(a.cols):
            v=a[i,j]; gray='black!5' if v==0 else ('black!22' if v<0 else 'black!78')
            txt='black!45' if v==0 else ('black' if v<0 else 'white')
            xx=x+j*c;yy=y-i*c
            L.append(rf'\filldraw[fill={gray},draw=white,line width=.8pt] ({xx:.4f},{yy:.4f}) rectangle ++({c:.4f},-{c:.4f});')
            L.append(node(xx+c/2,yy-c/2,'$'+sp.latex(v)+'$',f'text={txt},font=\\scriptsize'))
    L.append(rf'\draw[black!60,line width=.5pt] ({x},{y}) rectangle ++({a.cols*c},-{a.rows*c});')
    if top:L.append(node(x+a.cols*c/2,y+.48,top,'font=\\sffamily\\bfseries\\small'))
    if labels:
        for j,t in enumerate(labels):L.append(node(x+(j+.5)*c,y+.19,'$'+t+'$','font=\\scriptsize'))
    return L
# A horizontal seed-rank comparison, not a timing or benchmark plot.
L=[]
for i,(label,n) in enumerate([(r'$\QQ I$',6),(r'$\QQ[N]$',2),(r'$\QQ\langle N,P_e,P_f\rangle$',1),(r'$M_6(\QQ)$',1)]):
    y=-i*.86;L.append(node(-.3,y,label,'anchor=east'))
    for j in range(6):
        L.append(rf'\filldraw[draw=black!35,fill={"black!75" if j<n else "white"}] ({j*.67},{y-.20}) rectangle ++(.48,.40);')
    L.append(node(4.5,y,str(n),'font=\\sffamily\\bfseries'))
L.append(node(1.9,.72,'Minimum seeds for the same space $X=\\QQ^6$','font=\\sffamily\\small'))
save('grammar_budget',L)
# Two chains and their linked coefficients.
L=[]
for y,b in [(1.5,'e'),(0,'f')]:
    for j in range(3):
        x=1+3*j;L.append(node(x,y,rf'${b}_{j}$','circle,draw,minimum size=9mm,fill=white'))
        if j<2:L.append(line(x+.5,y,x+2.5,y,'->,line width=1pt'))
    L.append(line(7.5,y,8.65,y,'->,black!45'));L.append(node(9,y,'$0$','text=black!65'))
for j,coef in enumerate(['a','b','c']):
    L.append(line(1+3*j,.48,1+3*j,1.02,'dashed,black!50'))
    L.append(node(1+3*j,-.92,rf'${coef}e_{j}+{coef}f_{j}$'))
L.append(node(4,2.45,r'$N e_j=e_{j+1},\qquad N f_j=f_{j+1}$','font=\\sffamily\\small'))
save('linked_chains',L)
L=grid(d['Q'],c=.85,labels=['e_0','e_1','e_2','f_0','f_1','f_2'],top='The quotient keeps only the two chain heads')
L.append(node(2.55,-2.18,r'$q(a_0,a_1,a_2,b_0,b_1,b_2)=(a_0,b_0)$'))
save('quotient_heads',L)
L=grid(sp.Matrix([[0,1],[0,0]]),0,0,.85,top='$C=E_{12}$')+grid(sp.Matrix([[0,0],[1,0]]),3.2,0,.85,top='$B=E_{21}$')+grid(sp.diag(1,0),6.4,0,.85,top='$CB=E_{11}$')
L += [node(2.48,-.8,'$\\times$'),node(5.65,-.8,'$=$'),node(.85,-2.1,'$Ce_1=0$'),node(7.25,-2.1,'$CBe_1=e_1$')]
save('left_ideal',L)
L=[]
for row,(lab,active) in enumerate([('Seed at $U$',4),('Add $v_3$',5),('One mixed seed',5)]):
    y=-row*.85;L.append(node(-.35,y,lab,'anchor=east'))
    for j,n in enumerate(['u_1','u_2','v_1','v_2','v_3']):
        x=j*.95;sty='fill=black!8' if j>=active else 'fill=black!75'
        L.append(rf'\filldraw[{sty},draw=white] ({x},{y-.27}) rectangle ++(.80,.54);')
        L.append(node(x+.4,y,'$'+n+'$',f'text={"black!60" if j>=active else "white"}'))
    L.append(node(4.95,y,rf'$\dim H={active}$','anchor=west'))
L.append(line(1.775,.6,1.775,-2.12,'dashed,black!50'))
L.append(node(.875,.6,'$U$'));L.append(node(3.3,.6,'$V$'))
save('typed_spaces',L)
# Euclidean plot in actual coordinates; no nonlinear schematic spectrum.
L=[line(-.4,0,4.1,0,'->,black!40'),line(0,-.35,0,3.05,'->,black!40'),line(-.3,-.3,2.85,2.85,'black!45,dashed'),line(-.3,0,3.8,0,'black!65')]
for j in [1,2,3]:L += [line(j,-.04,j,.04,'black!40'),node(j,-.21,str(j),'font=\\scriptsize')]
L += [line(0,0,1,0,'->,very thick'),line(0,0,2,2,'->,thick'),line(0,0,3,2,'->,line width=1.2pt'),line(1,0,3,2,'dashed,black!55'),line(2,2,3,2,'dashed,black!55'),node(1,-.58,'$Px=(1,0)$'),node(1.47,2.2,'$Qx=(2,2)$','anchor=east'),node(3.08,2.17,'$x=(3,2)$','anchor=west'),node(3.6,.28,r'$\operatorname{im}P$','font=\\scriptsize'),node(2.95,2.85,r'$\operatorname{im}Q$','anchor=west,font=\\scriptsize')]
save('oblique_vectors',L)
L=grid(d['T'],0,0,.82,top='$T$')+grid(d['T']**2,4.6,0,.82,top='$T^2$')
L += [node(3.55,-1.13,r'$T\cdot T$','font=\\small'),node(1.23,-3.0,'input column; output row','font=\\scriptsize'),node(5.83,-3.0,'sum over intermediate packets','font=\\scriptsize')]
save('block_square',L)
L=[]
pos=[(0,0),(2,1.25),(2,-1.25),(4,0)]
for i,(x,y) in enumerate(pos):L.append(node(x,y,f'$e_{i+1}$','circle,draw,minimum size=8mm,fill=white'))
for i,j,w in [(0,1,'+1'),(0,2,'+1'),(1,3,'+1'),(2,3,'-1')]:
    x,y=pos[i];u,v=pos[j];L.append(rf'\draw[->,thick,shorten <=5mm,shorten >=5mm] ({x},{y}) -- node[above,sloped,font=\scriptsize] {{${w}$}} ({u},{v});')
L+=grid(krylov(d['D'],[unit(4,0)],3),6.1,1.65,.63,top='$[e_1,De_1,D^2e_1]$')
L.append(node(7.045,-1.35,'rank $=2$'));L.append(node(2,-2.05,r'$(D^2)_{41}=1-1=0$'))
save('cancelled_paths',L)
allow=sp.eye(3)+matrix_unit(3,1,0)+matrix_unit(3,2,1)
closure=sp.Matrix([[1,0,0],[1,1,0],[1,1,1]])
L=grid(allow,0,0,.7,top='Allowed support')+grid(matrix_unit(3,2,0),3.7,0,.7,top='$E_{32}E_{21}$')+grid(closure,7.4,0,.7,top='Transitive closure')
L +=[node(1.05,-2.6,'missing $(3,1)$'),node(4.75,-2.6,'outside the pattern'),node(8.45,-2.6,'closed under products')]
save('support_closure',L)
L=grid(sp.diag(1,2),0,0,.8,top='$T$')+grid(d['U'],3.1,0,.8,top='$U$')+grid(d['U']*sp.diag(1,2)*d['U'].inv(),6.2,0,.8,top='$UTU^{-1}$')
L+=grid(d['P'],1.55,-2.9,.8,top='$Q_1=UP_1U^{-1}$')+grid(d['Qob'],4.65,-2.9,.8,top='$Q_2=UP_2U^{-1}$')
save('transported_packets',L)
L=[]
for x0,label in [(0,'Shared scalar action'),(5.3,'Independent coordinate action')]:
    L.append(node(x0+1.5,2.6,label,'font=\\sffamily\\bfseries\\small'))
    L+= [line(x0-.2,0,x0+3.2,0,'->,black!40'),line(x0, -.2,x0,2.3,'->,black!40')]
    if x0==0:L.append(line(x0-.2,-.2,x0+2.2,2.2,'very thick'))
    else:L.append(rf'\fill[black!9] ({x0+.05},.05) rectangle ++(2.4,1.95);')
    L.append(line(x0,0,x0+1.3,1.3,'->,thick'))
    L.append(node(x0+1.46,1.32,'$(1,1)$','anchor=west,font=\\scriptsize'))
    L.append(node(x0+1.5,-.68,r'$\{(a,a):a\in\RR\}$' if x0==0 else r'$\{(a,b):a,b\in\RR\}$'))
save('shared_independent',L)
L=[]
for i,v in enumerate(d['Vs']):L+=grid(v,i*3.3,0,.48,top=f'$V_{i+1}$')
for i,n in enumerate([4,8,10]):L.append(node(i*3.3+1.2,-1.55,rf'cumulative rank ${n}$','font=\\scriptsize'))
L.append(node(4.5,.95,'Each row is one direction in the five-dimensional multiplicity space.','font=\\small'))
save('row_budget',L)
L=grid(krylov(d['N'],[d['s']]),0,0,.54,top='Equal primary labels')+grid(krylov(d['Tsep'],[d['s']]),5.0,0,.54,top='Distinct primary labels')
L += [node(1.62,-3.85,'Krylov rank $3$'),node(6.62,-3.85,rf'Krylov determinant ${krylov(d["Tsep"],[d["s"]]).det()}$')]
save('primary_krylov',L)
L=[]
for i in range(5):
    L.append(node(i*1.25,1.8,rf'${i+1}$','circle,draw,minimum size=7mm,fill='+('black!75,text=white' if i==0 else 'white')))
    if i<4:L.append(line(i*1.25+.37,1.8,(i+1)*1.25-.37,1.8,'thick'))
L+=grid(krylov(d['path5'],[unit(5,0)]),.875,.7,.65,labels=['0','1','2','3','4'])
L.append(node(.57,.89,'$k$','font=\\scriptsize'))
L.append(node(2.5,-3.07,'unit diagonal; no entries below it','font=\\small'))
save('path_walks',L)
L=[]
pos=[]
for j in range(6):pos.append((1.8*math.cos(math.pi/2-2*math.pi*j/6),1.8*math.sin(math.pi/2-2*math.pi*j/6)))
for j in range(6):L.append(line(*pos[j],*pos[(j+1)%6],'thick'))
for j,(x,y) in enumerate(pos):L.append(node(x,y,str(j),'circle,draw,minimum size=7mm,fill='+('black!75,text=white' if j in [0,1] else 'white')))
for k,(ev,m) in enumerate([(-2,1),(-1,2),(1,2),(2,1)]):
    x=4.1+k*.95
    L.append(rf'\filldraw[fill=black!65,draw=black!65] ({x},-1.2) rectangle ++(.55,{m*.8});')
    L.append(node(x+.275,-1.56,f'${ev}$'))
    L.append(node(x+.275,-1.2+m*.8+.24,f'${m}$','font=\\scriptsize'))
L.append(node(5.8,1.72,'Exact eigenspace dimensions','font=\\sffamily\\small'));L.append(node(5.8,-2.05,'eigenvalue','font=\\scriptsize'))
save('cycle_multiplicity',L)
L=[]
for row in range(2):
    for i in range(5):
        expr=['1','x','x^2','x^3','x^4'][i]
        if row:expr=['y','xy','x^2y','x^3y','x^4y'][i]
        L.append(rf'\filldraw[fill=black!{8 if row==0 else 18},draw=white] ({i*1.3},{-row*.8}) rectangle ++(1.15,-.63);')
        L.append(node(i*1.3+.575,-row*.8-.315,'$'+expr+'$'))
    L.append(node(6.95,-row*.8-.315,r'$\cdots$'))
L.append(node(3.2,.52,'Independent coefficient slots: $a(x)$ and $b(x)$'))
L.append(node(3.2,-2.18,r'$y^2=x^3-x\quad\Longrightarrow\quad y^3=(x^3-x)y$'))
save('normal_form',L)
L=[r'\fill[black!6] (1.75,-.05) rectangle (5.25,2.65);',line(-.1,0,7.6,0,'->,black!45')]
for n in range(-7,8):
    x=(n+7)*.5;h=2.4*2**(-abs(n))
    L.append(line(x,0,x,h,'line width=1pt'));L.append(rf'\fill ({x},{h}) circle (1.4pt);')
    if n in [-6,-3,0,3,6]:L.append(node(x,-.28,f'${n}$','font=\\scriptsize'))
L += [node(3.5,2.99,'$x[n]=2^{-|n|}$'),node(3.5,-.82,r'shaded window: $|n|\le3$','font=\\small'),node(7.72,0,'$n$','anchor=west')]
save('shift_tail',L)
L=[]
for j in range(3):
    y=-j*.85;L.append(node(-.45,y,rf'$j={j}$','anchor=east'))
    for idx,n in enumerate(range(-6,7)):
        x=idx*.56
        if n%3==j:
            L.append(rf'\filldraw[fill=black!70,draw=white] ({x},{y-.26}) rectangle ++(.48,.52);')
            L.append(node(x+.24,y,str(n),'text=white,font=\\scriptsize'))
        else:L.append(rf'\draw[black!12] ({x},{y-.26}) rectangle ++(.48,.52);')
L.append(node(3.55,.66,'Every integer belongs to exactly one residue packet.'))
L.append(node(3.55,-2.5,r'$n=2=3\cdot0+2\quad\mapsto\quad n=3=3\cdot1+0$'))
save('residue_carry',L)
L=[line(0,0,6.2,0,'->,black!50'),line(0,0,0,4.45,'->,black!50')]
for n in range(7):L +=[line(-.04,n*.65,5.65,n*.65,'black!10'),node(-.23,n*.65,str(n),'font=\\scriptsize')]
for n in range(6):L.append(node(n*1.1,-.26,str(n),'font=\\scriptsize'))
h1=orbit([d['N']],[d['s']],6)[1];h2=orbit([d['N'],d['Pe'],d['Pf']],[d['s']],6)[1]
for h,sty in [(h1,'thick,dashed'),(h2,'very thick')]:
    h=h+[h[-1]]*(6-len(h));pts=' -- '.join(f'({i*1.1},{v*.65})' for i,v in enumerate(h))
    L.append(rf'\draw[{sty}] {pts};')
    for i,v in enumerate(h):L.append(rf'\fill ({i*1.1},{v*.65}) circle (1.5pt);')
L += [node(5.55,4.15,r'with $P_e,P_f$','anchor=east,font=\\scriptsize'),node(5.55,2.20,r'$N$ only','anchor=east,font=\\scriptsize'),node(3,-.83,'iteration $n$'),node(-.18,4.65,r'$\dim W_n$','anchor=west')]
save('hull_iteration',L)
L=grid(sp.Matrix([[10,14],[15,21]]),0,0,1.0,labels=['5f_1','7f_2'],top='The coefficient rectangle')
L += [node(-.25,-.5,'$2e_1$','anchor=east'),node(-.25,-1.5,'$3e_2$','anchor=east'),node(4.7,-.50,r'$10(e_1\otimes f_1)+14(e_1\otimes f_2)$'),node(4.7,-1.3,r'$+15(e_2\otimes f_1)+21(e_2\otimes f_2)$')]
save('tensor_rectangle',L)
print('Wrote',len(list(OUT.glob('*.tex'))),'deterministic vector plates.')
