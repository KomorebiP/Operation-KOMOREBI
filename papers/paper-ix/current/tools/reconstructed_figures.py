#!/usr/bin/env python3
"""Exact finite checks and new illustrations for the recovered historical chapter.

These are new reconstructions, not recovered original images. Schematic panels
state interfaces and boundaries; their arrows are not claims of new proofs.
"""
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from math import comb, factorial
from pathlib import Path


def valuation(x: Fraction | int, p: int) -> int | None:
    x = Fraction(x)
    if not x:
        return None
    a, b, v = abs(x.numerator), x.denominator, 0
    while a % p == 0:
        a //= p; v += 1
    while b % p == 0:
        b //= p; v -= 1
    return v


def inverse(a: list[Fraction]) -> list[Fraction]:
    assert a[0] == 1
    b = [Fraction(1)]
    for n in range(1, len(a)):
        b.append(-sum(a[k] * b[n-k] for k in range(1, n+1)))
    return b


def multiply(a: list[int], b: list[int]) -> list[int]:
    c = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j] += x*y
    return c


def mm(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def mp(a: list[list[int]], n: int) -> list[list[int]]:
    r = [[1,0],[0,1]]
    for _ in range(n): r = mm(r,a)
    return r


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--figures', type=Path)
    args = parser.parse_args()
    counts: dict[str,int] = {}
    def check(ok: bool, family: str) -> None:
        if not ok: raise AssertionError(family)
        counts[family] = counts.get(family,0)+1
    H = [z for z in range(1,7) if pow(z,3,7)==1]
    selector = [sum(pow(z,n,7) for z in H)*pow(3,-1,7)%7 for n in range(16)]
    for n,z in enumerate(selector): check(z==int(n%3==0),'subgroup_selector')
    periodic = []
    for p,m in [(5,2),(7,2),(13,3)]:
        e=[1]
        for n in range(1,33): e.append(-sum(comb(m*n,m*q)*e[q] for q in range(n))%p)
        h=(p-1)//m
        for n in range(1,33-h): check(e[n+h]==e[n],'compressed_periods')
        periodic.append(dict(p=p,m=m,h=h,values=e))
    check(periodic[1]['values'][1:7]==[6,5,2,6,5,2],'historical_tail_correction')
    fourier=[]
    for n in range(17):
        lhs=sum(comb(2*n,2*q)*pow(2,q,7) for q in range(n+1))%7
        rhs=4*(pow(2,n,7)+pow(4,n,7))%7
        check(lhs==rhs,'fourier_root_filter');fourier.append(rhs)
    mat=[[comb(2*n,2*q)%7 if q<=n else 0 for q in range(9)] for n in range(9)]
    for n in range(9):
        for q in range(n+1):
            for j in range(7): check(comb(14*n+j,14*q)%7==mat[n][q],'standard_window_addresses')
    # Exact ordinary coefficients of sech(3t)^2 and (2t/sinh(2t))^2.
    bound=10
    cosh=[Fraction(3**(2*r),factorial(2*r)) for r in range(bound+1)]
    sinh_quotient=[Fraction(2**(2*r),factorial(2*r+1)) for r in range(bound+1)]
    squared=lambda a:[sum(a[k]*a[n-k] for k in range(n+1)) for n in range(len(a))]
    odd=inverse(squared(cosh));dyadic=inverse(squared(sinh_quotient))
    odd_v=[];dyad_v=[]
    for r in range(1,bound+1):
        a=valuation(odd[r]*factorial(2*r),3);b=valuation(dyadic[r]*factorial(2*r),2)
        check(a is not None and a>=2*r,'odd_kernel_floor');check(b==4*r-1,'dyadic_kernel_exact')
        odd_v.append(a);dyad_v.append(b)
    # Theta_4,1(r,k), independently by polynomial multiplication and differences.
    theta=[]
    for k in range(6):
        polynomial=[1,1]
        for _ in range(k): polynomial=multiply(polynomial,[0,4,6,4,1])
        row=[]
        for r in range(23):
            x=polynomial[r] if r<len(polynomial) else 0
            y=sum((-1)**(k-j)*comb(k,j)*comb(4*j+1,r) for j in range(k+1) if r<=4*j+1)
            check(x==y,'affine_kernel_independent')
            check(x%2==int(r in (4*k,4*k+1)),'affine_frobenius_window')
            row.append(x)
        theta.append(row)
    C=[[1,1],[1,0]]
    C12=mp(C,12)
    check(C12==[[233,144],[144,89]],'fibonacci_base_jump')
    for a in range(5):
        Q=mp(C,12*2**a)
        for i in range(2):
            for j in range(2): check((Q[i][j]-int(i==j))%(2**(a+3))==0,'fibonacci_refinement')
    # The image of (x,y) -> (x+y,0) over F_3.
    image=sorted({((x+y)%3,0) for x in range(3) for y in range(3)})
    check((1,0) in image and (0,1) not in image,'cokernel_control')
    check(sum((x+y)%3==2 for x in range(3) for y in range(3))==3,'cokernel_control')
    F=[0,1]
    for _ in range(18):F.append(F[-1]+F[-2])
    C3=mp(C,3)
    check(C3==[[3,2],[2,1]],'fibonacci_jump')
    for j in range(3):
        for k in range(5):
            x=mm(mp(C3,k),mp(C,j))
            check(x==mp(C,3*k+j),'packet_jump')
    check(C3[0][0]+C3[1][1]==4 and C3[0][0]*C3[1][1]-C3[0][1]*C3[1][0]==-1,'jump_characteristic')
    crt=[n for n in range(30) if n%3==1 and n%5==2]
    for n in range(30):check((n%3==1 and n%5==2)==(n%15==7),'crt_projectors')
    data=dict(status='PASS',scope='Bounded exact arithmetic and explicitly schematic new reconstructions. Original figure files remain unrecovered.',counts=counts,total_checks=sum(counts.values()),subgroup=H,selector=selector,periodic=periodic,fourier=fourier,matrix=mat,kernels={'odd_prime':3,'odd_valuations':odd_v,'dyadic_valuations':dyad_v},theta=theta,fibonacci=F,cokernel_image=image,crt=crt)
    if args.figures:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        args.figures.mkdir(parents=True,exist_ok=True)
        def save(fig,name):
            fig.tight_layout(pad=1.3)
            fig.savefig(args.figures/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
            fig.savefig(args.figures/(name+'.png'),dpi=150,bbox_inches='tight')
            plt.close(fig)
        def table(name,rows,heads,height=2.6):
            fig,ax=plt.subplots(figsize=(6.8,height));ax.axis('off')
            tab=ax.table(cellText=rows,colLabels=heads,loc='center',cellLoc='center')
            tab.auto_set_font_size(False);tab.set_fontsize(10);tab.scale(1,1.8);save(fig,name)
        table('architecture',[[r'$n=Nk+j$','residue address',r'$j$'],[r'$u=\omega(u)\langle u\rangle$','finite character',r'$\omega(u)$'],[r'$f(x)=\sum c_r\binom{x}{r}$','Mahler depth',r'$r$'],[r'$K\,H=\mathrm{sech}$','weighted reconstruction',r'$v_p(\kappa_r)$']],['coordinate layer','what is retained','coordinate'],2.8)
        fig,ax=plt.subplots(figsize=(6.8,2.5));ax.stem(range(16),selector);ax.set(xlabel='coefficient degree n',ylabel='selector mod 7',yticks=[0,1],xticks=list(range(0,16,3)),title='p = 7, subgroup H = {1, 2, 4}, order m = 3');save(fig,'subgroup_average')
        fig,ax=plt.subplots(figsize=(6.8,2.8))
        for z in periodic:ax.plot(range(1,17),z['values'][1:17],marker='o',label=f"p={z['p']}, m={z['m']}, h={z['h']}")
        ax.set(xlabel='positive row n',ylabel='residue of inverse',xticks=[1,4,8,12,16]);ax.legend(frameon=False,ncol=3,fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.24));save(fig,'standard_periods')
        table('standard_fourier',[[r'$\chi=2,\;y=3$','input character',r'$2^n$'],[r'$(1+y)^2=2$','first output mode',r'$4\,2^n$'],[r'$(1-y)^2=4$','second output mode',r'$4\,4^n$'],[r'$T(2^\bullet)_n$','sum modulo 7',r'$4(2^n+4^n)$']],['p = 7, m = 2, h = 3','root filter','mode at row n'],2.7)
        table('standard_matrix',[[str(n)]+list(map(str,mat[n])) for n in range(9)],['n / q']+list(map(str,range(9))),3.7)
        fig,ax=plt.subplots(figsize=(6.8,2.8));rr=list(range(1,11));ax.plot(rr,odd_v,marker='o',label='odd kernel, p = 3: exact data');ax.plot(rr,dyad_v,marker='s',label='dyadic kernel: 4r - 1');ax.plot(rr,[2*r for r in rr],linestyle='--',label='odd lower bound: 2r');ax.set(xlabel='positive kernel depth r',ylabel='local valuation');ax.legend(frameon=False,fontsize=9);save(fig,'local_kernel_weights')
        table('odd_dyadic_geometry',[['finite torsion','modulo p - 1','sign modulo 2'],['principal units',r'$1+p\mathbb{Z}_p$',r'$1+4\mathbb{Z}_2$'],['source choice','depleted unit branch','direct dyadic source'],['kernel floor',r'$2r$',r'$4r-1$']],['local coordinate','odd p','p = 2'],2.7)
        fig,ax=plt.subplots(figsize=(6.8,2.8));ax.imshow(np.array(theta)%2,aspect='auto',interpolation='nearest');ax.set(xlabel='ordinary coefficient degree r',ylabel='Mahler order k',xticks=list(range(0,23,2)),yticks=list(range(6)),title=r'$\Theta_{4,1}(r,k)\;\mathrm{mod}\;2$: support at $r=4k,4k+1$');save(fig,'mahler_polyphase_kernel')
        fig,ax=plt.subplots(figsize=(6.8,2.8))
        for a in range(4):ax.plot(range(7),[(a+3)*r for r in range(7)],marker='o',label=f'a = {a}, jump = {12*2**a}')
        ax.set(xlabel='Mahler / difference depth r',ylabel='certified binary digits',title='Fibonacci packet: bound (a + 3)r');ax.legend(frameon=False,fontsize=9,ncol=2);save(fig,'polyphase_precision_tree')
        fig,ax=plt.subplots(figsize=(6.4,2.7));ax.scatter([u for u,v in image],[v for u,v in image],s=80,label='image of correction map');ax.scatter([0],[1],marker='x',s=110,label='blocked residual');ax.set(xlabel='first coordinate mod 3',ylabel='second coordinate',xticks=[0,1,2],yticks=[0,1,2],ylim=(-.3,2.2),xlim=(-.3,2.4));ax.legend(frameon=False,fontsize=9);save(fig,'lift_obstruction')
        table('recurrence_packets',[[str(j)]+[str(F[3*k+j]) for k in range(5)] for j in range(3)],['address j','k = 0','k = 1','k = 2','k = 3','k = 4'],2.3)
        table('recurrence_root_power',[['C = [[1, 1], [1, 0]]',r'$x^2-x-1$',r'$\alpha,\beta$'],['C^3 = [[3, 2], [2, 1]]',r'$x^2-4x-1$',r'$\alpha^3,\beta^3$']],['Fibonacci state matrix','characteristic polynomial','roots'],2.0)
        fig,ax=plt.subplots(figsize=(6.8,2.6))
        for level,mod,res in [(2,3,1),(1,5,2),(0,15,7)]:
            xx=[n for n in range(30) if n%mod==res];ax.scatter(xx,[level]*len(xx),s=45)
        ax.set(xlabel='integer address n',yticks=[0,1,2],yticklabels=['joint: 7 mod 15','2 mod 5','1 mod 3'],xticks=[0,7,15,22,29],ylim=(-.5,2.5));save(fig,'crt_packets')
        table('claim_boundary',[['standard windows','finite periods and inverse coordinates'],['declared correction map','one-step cokernel obstruction'],['fixed integral recurrence','common source for its local images'],['arbitrary local families','global source NOT supplied'],['affine kernel valuations','general sharp higher laws remain open']],['scope','conclusion or boundary'],3.0)
        data['figures']=[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(args.figures.glob('*.pdf'))]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':'PASS','checks':sum(counts.values()),'counts':counts},indent=2))
if __name__=='__main__':main()
