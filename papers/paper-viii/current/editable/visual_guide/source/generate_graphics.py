#!/usr/bin/env python3
"""Generate 26 editable, deterministic mathematical plates, without image models.

Plot coordinates sample explicitly stated formulas. Symbolic identities and
finite-optimum claims are checked separately in checks/verify_examples.py.
"""
from pathlib import Path
import json,math
import sympy as s
from models import *
from drawing import Plate,seq,F,tex,OUT

def main():
    OUT.mkdir(parents=True,exist_ok=True);index=[]
    def done(p):index.append(p.finish())
    D,u,v,A,x=bdlr()
    p=Plate('three_views','One operator, several exact descriptions and distinct cost contracts')
    p.matrix(.2,3.8,A,.52,title=r'$A$: 36 visible entries')
    p.line(4.0,.2,4.0,4.35,'black!35')
    p.bars(4.4,.9,[36,24],['dense','factors'],width=3.7,height=2.5,maxv=36,title='stored scalars')
    pt=p.axes(9.0,.8,4.4,2.8,6,10,[0,2,4,6],[0,5,10],xlabel='error budget',ylabel='toy compilation cost')
    for e,c in [(0,10),(2,8),(4,7),(6,1)]:xx,yy=pt(e,c);p.circ(xx,yy,.075)
    p.line(8.65,.2,8.65,4.35,'black!35');done(p)

    p=Plate('factored_application','Contract first, then apply local blocks and a single scalar coupling')
    for j,(title,values) in enumerate([(r'$x$',x),(r'$Dx$',D*x),(r'$u(v^Tx)$',u*(v.T*x)),(r'$Ax$',A*x)]):
        p.matrix(.8+j*3.45,3.8,values,.52,title=title)
    p.text(5.15,2.1,'$+$',r'font=\Large');p.text(9.0,2.1,'$=$',r'font=\Large')
    p.text(7,.1,r'$v^Tx=3$ is shared by all six output coordinates.',r'font=\small');done(p)

    p=Plate('work_storage','Modeled representation savings, not measured speedup')
    ns=[6,12,24,48];rat=[s.Rational(n,4) for n in ns]
    p.bars(.75,.8,rat,[str(n) for n in ns],width=6,height=2.65,maxv=12,title=r'$n/(b+2r)$ with $b=2,r=1$')
    p.text(3.75,.1,'ambient dimension $n$',r'font=\scriptsize')
    p.text(10.55,3.8,'Six-dimensional running operator')
    for yy,txt in [(2.85,r'dense: $36$ scalars, $72q$ work'),(1.9,r'BDLR: $24$ scalars, $48q$ work'),(.95,r'ratio: $3/2$, not a timing result')]:p.text(10.55,yy,txt,r'font=\small')
    done(p)

    c,FF,C,lam,xc=fourier4()
    p=Plate('circulant','Four coefficients become four exact Fourier multipliers')
    p.matrix(.7,3.7,C,.73,title='$C(c)$')
    p.matrix(4.95,3.7,lam,.73,title=r'$\sqrt4\,Fc$',cellw=1.45)
    p.text(10.7,3.4,r'$F_{jk}=\frac12\,\mathrm i^{-jk}$')
    p.text(10.7,2.2,r'$C=F^*\diag(\sqrt4 Fc)F$')
    p.text(10.7,1.0,r'$\sqrt4=2$ is essential.')
    p.text(7,.05,'A unitary transform changes the normalization of the convolution eigenvalues.',r'font=\scriptsize');done(p)

    T,g,Cg,xt=toeplitz_model()
    p=Plate('toeplitz','Padding separates wanted Toeplitz coordinates from wraparound')
    p.matrix(.35,3.8,T,.78,title='$T$')
    p.matrix(4.1,3.8,g,.51,title=r'circulant column $g$')
    p.matrix(7.1,3.8,xt.col_join(s.zeros(3,1)),.51,title=r'padded input')
    out=Cg*xt.col_join(s.zeros(3,1));p.matrix(10.6,3.8,out,.51,title='six outputs')
    p.rect(10.6,3.8-3*.51,.51,3*.51,'draw,line width=1.2pt');p.text(12.5,2.95,r'keep\\first three',r'font=\scriptsize')
    p.text(7,.05,'Padding is part of the operator identity, not optional workspace.',r'font=\scriptsize');done(p)

    KA,KB,KX=kron_model()
    p=Plate('kronecker','Column-major addresses fix the transpose in the contraction law')
    p.matrix(.55,3.6,KX,.95,title='$X$')
    p.matrix(4.1,3.95,vec(KX),.72,title=r'$\operatorname{vec}(X)$')
    p.matrix(7.2,3.6,KB*KX*KA.T,.9,title=r'$BXA^T$',cellw=1.5)
    p.text(12.2,3.25,r'$A^T$\\not $A^*$',r'font=\small')
    p.text(7,.55,r'$(A\otimes B)\operatorname{vec}(X)=\operatorname{vec}(BXA^T)$');done(p)

    p=Plate('walsh','Every value in the three Walsh butterfly stages')
    stages=walsh_stages(list(range(1,9)))
    for i,stage in enumerate(stages):
        yy=3.75-i*1.03;p.text(.3,yy-.28,('input' if i==0 else 'stage '+str(i)),r'anchor=west,font=\scriptsize')
        for j,value in enumerate(stage):
            xx=2.0+j*1.38;p.rect(xx,yy-.59,1.15,.59,'draw=black!40,fill='+('white' if value==0 else 'black!8'));p.text(xx+.575,yy-.295,str(value))
    p.text(7,-.25,r'$8\log_2 8=24$ additions/subtractions; $H_8H_8^T=8I$.',r'font=\scriptsize');done(p)

    DA,DB,ua,va,ub,vb,AA,BB,UC,VC=product_model()
    p=Plate('bdlr_product','Two thin factors store the complete quadratic cross term')
    p.matrix(.8,3.8,UC,.52,title='$U_C$')
    p.matrix(5.1,3.8,VC,.52,title='$V_C$')
    p.text(10.3,3.45,r'$AB=D_AD_B+U_CV_C^T$')
    p.text(10.3,2.15,r'$U_A(V_A^TU_B)V_B^T$')
    p.text(10.3,1.35,'must be retained',r'font=\small')
    p.text(7,.1,r'Two input rank-one corrections produce at most rank two, not three.',r'font=\scriptsize');done(p)

    p=Plate('woodbury','The six-dimensional inverse uses one nonzero scalar denominator')
    p.matrix(.8,3.8,M([[3,-1],[-1,3]])/8,.85,title=r'one block of $D^{-1}$')
    p.text(6.25,3.5,r'$D^{-1}u=\tfrac14 u$')
    p.text(6.25,2.25,r'$S=1+u^TD^{-1}u=\tfrac52$')
    p.text(6.25,.9,r'$A^{-1}=D^{-1}-\tfrac1{40}uu^T$')
    p.matrix(10.6,3.55,M([[0,0],[0,1]]),.85,title=r'$I-e_1e_1^T$')
    p.text(11.45,.7,r'invertible $D$\\singular update',r'font=\scriptsize');done(p)

    QL,RL,RR,L,R,G,LR=compact_model()
    p=Plate('compact_core','Redundant input columns disappear in actual range coordinates')
    p.matrix(.45,3.8,L,.65,title=r'$L$: rank $2$')
    p.matrix(4.55,3.8,R,.65,title=r'$R$: rank $3$')
    p.matrix(8.75,3.8,G,.87,title=r'$G$: $2\times3$')
    p.text(10.1,.85,r'$LR^T=Q_LG$')
    p.text(6.8,.15,'The stored width is three; the left range has only two independent directions.',r'font=\scriptsize');done(p)

    p=Plate('optimality','Exact singular tails and an ambient competitor outside the range')
    p.matrix(.65,3.8,LR,.72,title=r'$LR^T$')
    p.matrix(5.05,3.8,QL*M([[5,0,0],[0,0,0]]),.72,title='rank-one output')
    p.bars(9.7,.9,[5,2,0],['rank 0','rank 1','rank 2'],width=3.8,height=2.6,maxv=5,title='spectral error')
    p.text(7,.1,r'Frobenius errors: $\sqrt{29},\ 2,\ 0$. The rank-one choice loses only the second mode.',r'font=\scriptsize');done(p)

    p=Plate('error_chain','Later multiplications amplify early additive errors')
    p.bars(.8,.9,[Q(1,10),Q(1,5),Q(1,20)],['1','2','3'],width=5,height=2.7,maxv=Q(6,5),title='local injected errors')
    p.bars(8.0,.9,[Q(6,5),Q(4,5),Q(1,20)],['1','2','3'],width=5,height=2.7,maxv=Q(6,5),title='final contributions')
    p.text(7,.05,r'$\widehat p_j=a_j\widehat p_{j-1}+e_j$, with $(a_1,a_2,a_3)=(2,3,4)$.',r'font=\scriptsize');done(p)

    K=diamond()
    p=Plate('cancellation','An allowed two-step path need not leave a nonzero coefficient')
    p.matrix(.7,3.6,K,.8,title='$K$')
    p.matrix(5.6,3.6,(K.applyfunc(lambda a:int(a!=0)))**2,.8,title='path counts at length two')
    p.text(11.85,3.0,r'$1+(-1)=0$')
    p.text(11.85,1.65,r'$K^2=0$')
    p.text(7,.1,r'Structural support is an upper bound. It does not encode destructive cancellation.',r'font=\scriptsize');done(p)

    AT,bt,xx,levels=dag_model()
    p=Plate('triangular','A dependency schedule with the actual solved values')
    for j,level in enumerate(levels):
        for vtx in level:
            yy=3.9-vtx*.48;p.rect(1+j*1.85,yy,1.45,.35,'draw,fill=black!14');p.text(1+j*1.85+.725,yy+.175,str(vtx),r'font=\scriptsize')
    for j in range(4):p.text(1.72+j*1.85,.25,'stage '+str(j+1),r'font=\scriptsize')
    p.matrix(10.6,4.1,xx,.48,title=r'$x=(2I+K)^{-1}\mathbf1$')
    p.text(.35,4.42,'packet task',r'anchor=west,font=\scriptsize');done(p)

    p=Plate('schur_fill','Eliminating one coordinate changes retained coupling')
    p.matrix(.75,3.6,schur_model()[0],.86,title=r'$A$ before elimination')
    p.matrix(5.65,3.6,schur_model()[1],.95,title=r'$S=A_{RR}-A_{RH}A_{HH}^{-1}A_{HR}$')
    p.matrix(10.25,3.6,schur_model(True)[1],.95,title='cancelling variant')
    p.text(7,.7,r'A hidden route creates $-1/2$; adding $+1/2$ in the original block cancels it.',r'font=\scriptsize');done(p)

    p=Plate('krylov','A common polynomial links invariant packets')
    pt=p.axes(.95,.75,4.65,3.1,1.5,1.5,[-1,0,1],[-1,0,1],xlabel='packet 1',ylabel='packet 2',xmin=-1.5,ymin=-1.5)
    p.curve(pt,[-1.3,1.3],[-1.3,1.3]);p.text(3.25,4.25,r'$A=I_2,\ v=(1,1)^T$')
    p.text(9.5,3.3,r'$p(A)v=p(1)(1,1)^T$')
    p.text(9.5,2.1,r'$\dim\mathcal K_m(A,v)=1$')
    p.text(9.5,.9,r'Independent local spans have dimension $2$.')
    done(p)

    p=Plate('preconditioning','Normalization changes a stretched energy ellipse into a controlled one')
    PA,PD,PB,PN=preconditioner()
    import numpy as np
    for xx0,mat,title in [(.95,PA,'before: $x^TAx=1$'),(7.65,PN,'after: $y^T(I+E)y=1$')]:
        pt=p.axes(xx0,.7,5.2,3.25,1.7,1.7,[-1,0,1],[-1,0,1],xmin=-1.7,ymin=-1.7)
        vals,V=np.linalg.eigh(np.array(mat,float));theta=np.linspace(0,2*np.pi,160);Z=V@np.diag(1/np.sqrt(vals))@np.vstack([np.cos(theta),np.sin(theta)])
        p.curve(pt,Z[0],Z[1]);p.text(xx0+2.6,4.3,title)
    p.text(7,-.1,r'Exact normalized eigenvalues: $1/2,3/2$. Hence $\kappa_2=3$.',r'font=\scriptsize');done(p)

    p=Plate('block_error','Many small omitted blocks can add coherently')
    EA,ER=error_model();p.matrix(.7,3.8,100*ER,.78,title=r'$100E$: twelve omitted entries')
    p.bars(7.35,.85,[1,3,s.sqrt(12)],['one block','spectral','Frobenius'],width=5.5,height=2.65,maxv=4,title=r'error norms, in units of $1/100$')
    p.text(7,.1,r'$\|E\|_F^2=12/10^4$, while $E\mathbf1=(3/100)\mathbf1$.',r'font=\scriptsize');done(p)

    p=Plate('precision','Equal tolerance and equal error contribution are different allocations')
    p.bars(.7,.8,[Q(1,4),Q(1,4),Q(1,2)],['edge 1','edge 2','edge 3'],width=5.4,height=2.7,maxv=Q(3,5),title=r'unclipped contributions $s_e\epsilon_e$')
    p.bars(7.8,.8,[Q(1,10),Q(3,10),Q(3,5)],['edge 1','edge 2','edge 3'],width=5.4,height=2.7,maxv=Q(3,5),title='clipped contributions')
    p.text(7,.05,r'Both allocations spend exactly one unit of error budget.',r'font=\scriptsize');done(p)

    p=Plate('discrete','First nine exact-budget columns of the three-edge program')
    tabs=precision_dp()
    for row,tab in enumerate(tabs):
        yy=3.5-row*.84;p.text(.5,yy,'edges '+str(row),r'anchor=west,font=\scriptsize')
        for b in range(9):
            xx=2.2+b*1.2;p.rect(xx-.5,yy-.3,1,.6,'draw=black!25,fill='+('black!8' if b in tab else 'white'))
            p.text(xx,yy,str(tab[b][0]) if b in tab else r'$\infty$',r'font=\scriptsize')
    for b in range(9):p.text(2.2+b*1.2,4.12,str(b),r'font=\scriptsize')
    p.text(7,.1,'Columns are exact weights; the budget optimum is the minimum across allowed columns.',r'font=\scriptsize');done(p)

    p=Plate('tree_frontier','A real budget optimum can be invisible to every penalty parameter')
    pt=p.axes(.85,.8,6.0,3.2,6.5,11,[0,2,4,6],[1,5,10],xlabel='error',ylabel='cost')
    rows=prunings(tree_model())
    for cost,err,ll in rows:
        xx,yy=pt(err,cost);p.circ(xx,yy,.075,'fill=black' if cost!=9 else 'draw,fill=white')
    p.curve(pt,[0,6],[10,1],'dashed,black!60')
    p.text(10.1,3.6,r'Budget $B=2$: cost $8$')
    p.text(10.1,2.35,r'Penalty optimum: root or full split')
    p.text(10.1,1.0,r'$8+2\lambda\le1+6\lambda$\\and $8+2\lambda\le10$\\cannot both hold.',r'font=\small');done(p)

    p=Plate('local_update','A single leaf update changes only its ancestors')
    tr=tree_model();old=node_values(tr,2);new=node_values(changed_leaf(tr,'a0',3),2)
    names=['a0','a1','a','b0','b1','b','r']
    for j,n in enumerate(names):
        xx=.8+j*1.9;p.text(xx+.7,4.0,'$'+n+'$')
        for yy,value in [(2.75,old[n]),(1.6,new[n])]:
            p.rect(xx,yy-.35,1.4,.7,'draw,fill='+('black!14' if old[n]!=new[n] else 'white'));p.text(xx+.7,yy,tex(value))
    p.text(7,.45,'Top: old values. Bottom: new values. Only a0, a, and r change.',r'font=\scriptsize');done(p)

    p=Plate('batch_shapes','Equal mathematical shapes can share a launch only under the same contract')
    shapes=[(2,2),(2,3),(3,2),(2,2),(3,2),(2,3)]
    for j,(rr,cc) in enumerate(shapes):
        xx=.75+2.2*j;p.matrix(xx,3.9,s.ones(rr,cc),.42,title=str(rr)+r'$\times$'+str(cc))
        p.text(xx+.55,1.8,'task '+str(j+1),r'font=\scriptsize')
    p.text(7,.95,'Three shape classes, six independent tasks.',r'font=\small')
    p.text(7,.1,'Grouping does not remove arithmetic, data transfer, or shared-output dependencies.',r'font=\scriptsize');done(p)

    p=Plate('amortization','Strict improvement starts after the break-even reuse count')
    pt=p.axes(.9,.8,8,3.15,12,90,[0,3,6,9,12],[0,30,60,90],xlabel='reuse count $R$',ylabel='toy time units')
    rs=list(range(13));p.curve(pt,rs,[7*r for r in rs]);p.curve(pt,rs,[30+2*r for r in rs],'dashed,line width=1.1pt')
    xx,yy=pt(6,42);p.circ(xx,yy,.075);p.text(11.6,3.4,'solid: $7R$');p.text(11.6,2.3,'dashed: $30+2R$')
    p.text(11.6,1.2,r'tie at $6$\\first win at $7$');done(p)

    p=Plate('contract_match','Metadata decides whether two times answer the same question')
    headings=['row','output','scope','time'];widths=[1.3,4.4,4.8,2.0];xxs=[.45,1.75,6.15,10.95]
    rows=[['A','explicit matrix','materialization included','12'],['B','low-rank factors','factor product only','2'],['C','explicit matrix','factor product + decode','14'],['D','explicit matrix','different input precision','1']]
    for j,h in enumerate(headings):p.text(xxs[j]+widths[j]/2,4.1,h,r'font=\bfseries\small')
    for i,row in enumerate(rows):
        yy=3.2-i*.8
        for j,t in enumerate(row):p.rect(xxs[j],yy-.32,widths[j],.64,'draw=black!30,fill='+('black!7' if i%2==0 else 'white'));p.text(xxs[j]+widths[j]/2,yy,t,r'font=\scriptsize')
    p.text(7,-.1,'Synthetic times: A versus C is contract-aligned. A versus B is not a sixfold speedup.',r'font=\scriptsize');done(p)

    p=Plate('end_to_end','A full product is applied from its factors without materialization')
    DA,DB,ua,va,ub,vb,AA,BB,UC,VC=product_model();z=VC.T*x;local=DA*DB*x;global_=UC*z
    p.matrix(.7,3.65,z,.75,title=r'$V_C^Tx$')
    p.matrix(4.1,3.85,local,.51,title=r'$D_AD_Bx$')
    p.matrix(7.3,3.85,global_,.51,title=r'$U_C(V_C^Tx)$')
    p.matrix(10.55,3.85,AA*BB*x,.51,title=r'$(AB)x$')
    p.text(7,.1,'Two intermediate scalars and six output coordinates, with an exact dense reference.',r'font=\scriptsize');done(p)
    (OUT/'FIGURE_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print(f'Generated {len(index)} editable vector plates.')
if __name__=='__main__':main()
