"""Sixteen exact sequence lessons, with bounded reproducibility evidence.

The sequences are integer/rational objects. Floating arithmetic is used only to
place marks and evaluate explicitly labeled logarithmic display coordinates.
This file proves no novelty claim, asymptotic claim, or universal certificate.
Run: python figures_sequences.py
"""
from pathlib import Path
from fractions import Fraction as Q
from math import comb, factorial, gcd, log10
from itertools import permutations
from datetime import datetime, timezone
import hashlib
import json
import platform
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from guide_style import ROOT, COLORS, INK, MUTED, PALE, save_figure

N = 18
STEMS = [
 'S01_fibonacci_lucas','S02_tribonacci_tetranacci','S03_jacobsthal',
 'S04_sqrt3_pell','S05_binomial_catalan','S06_catalan_convolution',
 'S07_bell_stirling','S08_fubini_factorial','S09_derangements',
 'S10_euler_updown','S11_bernoulli_pair','S12_partition_product',
 'S13_apery_recurrence','S14_divisor_convolution','S15_binary_families',
 'S16_polynomial_ladder']

def recurrence(seed, taps, degree=N):
    a = list(seed)
    for n in range(len(a), degree + 1):
        a.append(sum(t*a[n-j] for j,t in enumerate(taps, 1)))
    return a

def convolution(a,b,degree):
    return [sum(a[k]*b[n-k] for k in range(n+1)) for n in range(degree+1)]

def invert(a,degree):
    assert a[0] != 0
    b = [Q(1,a[0])]
    for n in range(1,degree+1):
        b.append(-sum(a[k]*b[n-k] for k in range(1,n+1))/a[0])
    return b

def table(ax, rows, labels, cols, font=12, scale=1.7):
    ax.axis('off')
    tab=ax.table(cellText=rows,rowLabels=labels if labels else None,colLabels=cols,
                 loc='center',cellLoc='center',rowLoc='center')
    tab.auto_set_font_size(False);tab.set_fontsize(font);tab.scale(1,scale)
    for (r,c),cell in tab.get_celld().items():
        cell.set_edgecolor('#D8E3E4');cell.set_linewidth(.7)
        if r==0 or c==-1:
            cell.set_facecolor(PALE);cell.get_text().set_color(COLORS[0])
    return tab

def basic_axes(ax, title, xlabel='Index n', ylabel='Value'):
    ax.set_title(title,pad=10);ax.set_xlabel(xlabel);ax.set_ylabel(ylabel)
    ax.grid(axis='y');ax.set_axisbelow(True)

def logvals(a):
    return np.array([log10(1+x) for x in a])

def factor_mu(n):
    original=n; count=0; p=2
    while p*p<=n:
        if n%p==0:
            n//=p;count+=1
            if n%p==0:return 0
            while n%p==0:n//=p
        p+=1
    if n>1:count+=1
    return (-1)**count

def partitions(n,maxpart=None):
    if n==0:return [()]
    if maxpart is None:maxpart=n
    out=[]
    for j in range(min(n,maxpart),1-1,-1):
        out.extend([(j,)+p for p in partitions(n-j,j)])
    return out

def main():
    started=datetime.now(timezone.utc).isoformat();t0=time.monotonic()
    input_names=['figures_sequences.py','chapters_sequences.tex','guide_style.py',
                 'evidence/OEIS_SOURCE_RECORDS.json']
    inputs=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
            for p in input_names]
    C={};prefixes={}
    def record_prefix(identifier, values, first=0):
        prefixes[identifier]={'initial_index':first,'first_eight_terms':list(values[:8])}

    # 01: one recurrence, two initial states; common-index norm identity.
    fib=recurrence([0,1],[1,1]);luc=recurrence([2,1],[1,1])
    defect=[luc[n]**2-5*fib[n]**2 for n in range(N+1)]
    assert defect==[4*(-1)**n for n in range(N+1)]
    record_prefix('A000045',fib);record_prefix('A000032',luc)
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1.4,1]})
    n=np.arange(13)
    axs[0].plot(n,fib[:13],'-o',label='Fibonacci: seeds 0, 1',ms=4)
    axs[0].plot(n,luc[:13],'-s',label='Lucas: seeds 2, 1',ms=4)
    basic_axes(axs[0],'Same recurrence, different seeds');axs[0].set_xticks([0,3,6,9,12]);axs[0].legend(loc='upper left',fontsize=10.5)
    axs[1].bar(n,defect[:13],color=[COLORS[i%2] for i in n],width=.72)
    axs[1].axhline(0,color=MUTED,lw=1)
    basic_axes(axs[1],'Common-index defect',ylabel=r'$L_n^2-5F_n^2$')
    axs[1].set(yticks=[-4,0,4],ylim=(-5.6,5.6),xticks=[0,3,6,9,12])
    save_figure(fig,STEMS[0]);C['S01']={'Fibonacci':fib,'Lucas':luc,'defect':defect,'worked_index':7,'worked_defect':-4}

    # 02: exact OEIS seed conventions; no zero is hidden by log scaling.
    trib=recurrence([0,0,1],[1,1,1]);tetra=recurrence([0,0,0,1],[1,1,1,1])
    record_prefix('A000073',trib);record_prefix('A000078',tetra)
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1,1.25]})
    table(axs[0],[trib[:4],tetra[:4]],['Tribonacci','Tetranacci'],['n=0','1','2','3'],font=11.5,scale=2.3)
    axs[0].set_title('Fix the seeds before iterating',pad=15)
    axs[1].plot(range(17),logvals(trib[:17]),'-o',ms=4,label='Three-term memory')
    axs[1].plot(range(17),logvals(tetra[:17]),'-s',ms=4,label='Four-term memory')
    basic_axes(axs[1],'Growth on a labeled log scale',ylabel=r'$\log_{10}(1+a_n)$');axs[1].set_xticks([0,4,8,12,16]);axs[1].legend(fontsize=10.5)
    save_figure(fig,STEMS[1]);C['S02']={'tribonacci':trib,'tetranacci':tetra,'plot_transformation':'log10(1+a_n)'}

    # 03: independently compare a closed form with recurrence iteration.
    jac=recurrence([0,1],[1,2]);closed=[(2**n-(-1)**n)//3 for n in range(N+1)]
    assert jac==closed
    record_prefix('A001045',jac);rem=[2**n-3*jac[n] for n in range(N+1)]
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained')
    n=np.arange(13);axs[0].bar(n,jac[:13],color=COLORS[0])
    basic_axes(axs[0],'Jacobsthal growth');axs[0].set_xticks([0,3,6,9,12])
    axs[1].bar(n,rem[:13],color=[COLORS[i%2] for i in n]);axs[1].axhline(0,color=MUTED,lw=1)
    basic_axes(axs[1],'Remove the growing mode',ylabel=r'$2^n-3J_n$');axs[1].set(yticks=[-1,0,1],ylim=(-1.4,1.4),xticks=[0,3,6,9,12])
    save_figure(fig,STEMS[2]);C['S03']={'Jacobsthal':jac,'mode_remainder':rem,'closed_form_matches':True}

    # 04: integer multiplication in Z[sqrt(3)], no floating cancellation.
    x=[1];y=[0]
    for n in range(N):x.append(2*x[-1]+3*y[-1]);y.append(x[-2]+2*y[-1])
    assert all(x[n]**2-3*y[n]**2==1 for n in range(N+1))
    assert x==recurrence([1,2],[4,-1]) and y==recurrence([0,1],[4,-1])
    record_prefix('A001075',x);record_prefix('A001353',y)
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[1.25,1]})
    table(axs[0],[[n,x[n],y[n],1] for n in range(8)],[],['n','x(n)','y(n)','norm'],font=11.5,scale=1.5)
    axs[0].set_title('One unit, two integer coordinates')
    axs[1].axis('off')
    axs[1].text(.5,.78,'x(n+1) = 2x(n) + 3y(n)\ny(n+1) = x(n) + 2y(n)',ha='center',va='center',fontsize=14)
    axs[1].text(.5,.48,'(7, 4) → (26, 15)',ha='center',fontsize=15,color=COLORS[0])
    axs[1].text(.5,.24,'determinant = 1\nnorm x² − 3y² = 1',ha='center',va='center',fontsize=14)
    save_figure(fig,STEMS[3]);C['S04']={'x':x,'y':y,'norms':[1]*(N+1),'update_matrix':[[2,3],[1,2]]}

    # 05-06: direct binomial Catalan values and independent convolution.
    central=[comb(2*n,n) for n in range(N+1)];cat=[central[n]//(n+1) for n in range(N+1)]
    assert all(central[n]%(n+1)==0 for n in range(N+1))
    assert all(cat[n+1]==sum(cat[k]*cat[n-k] for k in range(n+1)) for n in range(N))
    record_prefix('A000984',central);record_prefix('A000108',cat)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'height_ratios':[.8,1.3]})
    table(axs[0],[central[:7],list(range(1,8)),cat[:7]],['Binomial','Divide by','Catalan'],list(range(7)),font=11.5,scale=1.25)
    n=np.arange(15);axs[1].plot(n,[log10(v) for v in central[:15]],'-o',ms=4,label='Central binomial')
    axs[1].plot(n,[log10(v) for v in cat[:15]],'-s',ms=4,label='Catalan')
    basic_axes(axs[1],'Normalize by the changing factor n + 1',ylabel=r'$\log_{10}(\mathrm{value})$');axs[1].set_xticks([0,3,6,9,12,14]);axs[1].legend(fontsize=10.5)
    save_figure(fig,STEMS[4]);C['S05']={'central_binomial':central,'Catalan':cat,'divisors':list(range(1,N+2))}
    products=[cat[k]*cat[4-k] for k in range(5)]
    assert products==[14,5,4,5,14] and sum(products)==42
    fig,ax=plt.subplots(figsize=(8.1,4.1),layout='constrained')
    ax.bar(range(5),products,color=COLORS[:5],width=.62)
    for k,v in enumerate(products):ax.text(k,v+.6,str(v),ha='center',fontsize=15)
    ax.set(xticks=range(5),xticklabels=['1 × 14','1 × 5','2 × 2','5 × 1','14 × 1'],ylim=(0,18.5))
    basic_axes(ax,'Five products add to C(5) = 42',xlabel=r'Product $C_kC_{4-k}$',ylabel='Contribution')
    save_figure(fig,STEMS[5]);C['S06']={'worked_target_index':5,'products':products,'sum':42,'convolution_checked_through_target':N}

    # 07-08: exact Stirling recurrence and two independent row-sum recurrences.
    S=[[0]*(N+1) for _ in range(N+1)];S[0][0]=1
    for n in range(1,N+1):
        for k in range(1,n+1):S[n][k]=S[n-1][k-1]+k*S[n-1][k]
    bell=[sum(r) for r in S];fub=[sum(factorial(k)*S[n][k] for k in range(n+1)) for n in range(N+1)]
    bell_alt=[1];fub_alt=[1]
    for n in range(1,N+1):
        bell_alt.append(sum(comb(n-1,k)*bell_alt[k] for k in range(n)))
        fub_alt.append(sum(comb(n,j)*fub_alt[n-j] for j in range(1,n+1)))
    assert bell==bell_alt and fub==fub_alt
    record_prefix('A000110',bell);record_prefix('A000670',fub);record_prefix('A000142',[factorial(n) for n in range(N+1)])
    # Exact EGF checks: exp(e^t-1), via derivative recurrence; reciprocal 2-e^t.
    h=[Q(0)]+[Q(1,factorial(n)) for n in range(1,N+1)]
    exp_h=[Q(1)]
    for n in range(1,N+1):exp_h.append(sum(k*h[k]*exp_h[n-k] for k in range(1,n+1))/n)
    assert exp_h==[Q(bell[n],factorial(n)) for n in range(N+1)]
    denominator=[Q(1)]+[-Q(1,factorial(n)) for n in range(1,N+1)]
    assert invert(denominator,N)==[Q(fub[n],factorial(n)) for n in range(N+1)]
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[3.2,1]})
    A=np.array([[S[n][k] if k<=n else np.nan for k in range(8)] for n in range(8)],float)
    axs[0].imshow(np.log1p(A),cmap='Blues',aspect='auto')
    for n in range(8):
        for k in range(n+1):axs[0].text(k,n,str(S[n][k]),ha='center',va='center',fontsize=11,color='white' if S[n][k]>25 else INK)
    axs[0].set(xticks=range(8),yticks=range(8),xlabel='Number of blocks k',ylabel='Set size n',title='Stirling triangle S(n, k)')
    axs[1].axis('off');axs[1].set(xlim=(0,1),ylim=(7.5,-.5))
    for n in range(8):
        axs[1].text(.5,n,str(bell[n]),ha='center',va='center',fontsize=13,color=COLORS[0],bbox={'facecolor':PALE,'edgecolor':'none','boxstyle':'round,pad=.28'})
    axs[1].set_title('Bell row sum B(n)')
    save_figure(fig,STEMS[6]);C['S07']={'Stirling_rows':S,'Bell':bell,'independent_recurrence_match':True,'EGF_coefficient_match':True,'shade':'log1p; numbers exact'}
    weights=[factorial(k) for k in range(1,6)];stir=S[5][1:6];weighted=[a*b for a,b in zip(stir,weights)]
    assert weighted==[1,30,150,240,120] and sum(weighted)==541
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'height_ratios':[.8,1.2]})
    table(axs[0],[stir,weights,weighted],['S(5, k)','k!','Product'],list(range(1,6)),font=12,scale=1.25)
    axs[1].bar(range(1,6),weighted,color=COLORS[:5],width=.6)
    for k,v in enumerate(weighted,1):axs[1].text(k,v+6,str(v),ha='center',fontsize=12)
    basic_axes(axs[1],'Ordered blocks: contributions sum to 541',xlabel='Number of blocks k',ylabel='Weighted count');axs[1].set(xticks=range(1,6),ylim=(0,285))
    save_figure(fig,STEMS[7]);C['S08']={'Fubini':fub,'factorial_weights':weights,'worked_products':weighted,'sum':541,'independent_recurrence_match':True,'EGF_coefficient_match':True}

    # 09: signed sum, recurrence, and brute-force counts in a deliberately small range.
    der=[sum((-1)**k*(factorial(n)//factorial(k)) for k in range(n+1)) for n in range(N+1)]
    alt=[1,0]
    for n in range(2,N+1):alt.append((n-1)*(alt[n-1]+alt[n-2]))
    assert der==alt
    brute=[sum(all(i!=p[i] for i in range(n)) for p in permutations(range(n))) for n in range(9)]
    assert brute==der[:9]
    record_prefix('A000166',der)
    terms=[(-1)**k*(factorial(6)//factorial(k)) for k in range(7)]
    fig,ax=plt.subplots(figsize=(8.1,4.1),layout='constrained')
    ax.bar(range(7),terms,color=[COLORS[0] if v>0 else COLORS[1] for v in terms],width=.62)
    for k,v in enumerate(terms):ax.text(k,v+(35 if v>0 else -40),str(v),ha='center',va='bottom' if v>0 else 'top',fontsize=12)
    ax.axhline(0,color=MUTED,lw=1);ax.axhline(265,color=COLORS[2],ls='--',label='Final sum = 265')
    basic_axes(ax,'Inclusion-exclusion at n = 6',xlabel='Excluded fixed-point count k',ylabel='Signed contribution');ax.set(xticks=range(7),ylim=(-910,950));ax.legend(loc='upper right',fontsize=11)
    save_figure(fig,STEMS[8]);C['S09']={'derangements':der,'terms_at_6':terms,'brute_force_max_n':8,'brute_force_counts':brute,'recurrence_domain':'n>=2'}

    # 10: formal rational inversion of cosine; sine times secant.
    cosine=[Q(0)]*(N+1);sine=[Q(0)]*(N+1)
    for n in range(N+1):
        if n%2==0:cosine[n]=Q((-1)**(n//2),factorial(n))
        else:sine[n]=Q((-1)**((n-1)//2),factorial(n))
    secant=invert(cosine,N);tangent=convolution(sine,secant,N)
    euler=[int((secant[n]+tangent[n])*factorial(n)) for n in range(N+1)]
    assert all((secant[n]+tangent[n])*factorial(n)==euler[n] for n in range(N+1))
    euler_alt=[1,1]
    for n in range(1,N):
        value=sum(comb(n,k)*euler_alt[k]*euler_alt[n-k] for k in range(n+1))
        assert value%2==0;euler_alt.append(value//2)
    assert euler==euler_alt
    updown_brute=[sum(all((p[i]<p[i+1]) if i%2==0 else (p[i]>p[i+1]) for i in range(n-1)) for p in permutations(range(n))) for n in range(9)]
    assert updown_brute==euler[:9]
    record_prefix('A000111',euler);record_prefix('A000364',euler[0::2]);record_prefix('A000182',euler[1::2],1)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained')
    table(axs[0],[[euler[2*m] for m in range(6)],[factorial(2*m) for m in range(6)]],['Secant number','Divide by'],[f'deg {2*m}' for m in range(6)],font=11.5,scale=1.55)
    axs[0].set_title('Even degrees belong to secant')
    table(axs[1],[[euler[2*m+1] for m in range(6)],[factorial(2*m+1) for m in range(6)]],['Tangent number','Divide by'],[f'deg {2*m+1}' for m in range(6)],font=11.5,scale=1.55)
    axs[1].set_title('Odd degrees belong to tangent')
    save_figure(fig,STEMS[9]);C['S10']={'Euler_up_down':euler,'secant_numbers':euler[0::2],'tangent_numbers':euler[1::2],'EGF_series_match':True,'independent_differential_recurrence_match':True,'permutation_max_n':8,'permutation_counts':updown_brute}

    # 11: B1 = -1/2. Rational recurrence plus exact EGF reciprocal product.
    bern=[Q(1)]
    for n in range(1,N+1):bern.append(-sum(comb(n+1,k)*bern[k] for k in range(n))/Q(n+1))
    assert bern[1]==-Q(1,2)
    series=[bern[n]/factorial(n) for n in range(N+1)]
    g=[Q(1,factorial(n+1)) for n in range(N+1)]
    assert convolution(series,g,N)==[Q(1)]+[Q(0)]*N
    numer=[b.numerator for b in bern];denom=[b.denominator for b in bern]
    record_prefix('A027641',numer);record_prefix('A027642',denom)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',sharex=True)
    n=np.arange(13)
    axs[0].scatter(n,numer[:13],c=[COLORS[0] if v>=0 else COLORS[1] for v in numer[:13]],s=48,zorder=3)
    axs[0].vlines(n,0,numer[:13],colors=[COLORS[0] if v>=0 else COLORS[1] for v in numer[:13]])
    axs[0].set_yscale('symlog',linthresh=1);axs[0].set_yticks([-100,-1,0,1,5]);axs[0].set_yticklabels(['−100','−1','0','1','5'])
    basic_axes(axs[0],'Reduced numerator p(n): signed log scale',xlabel='',ylabel='Numerator');axs[0].set_ylim(-1600,11)
    axs[0].annotate('−691',xy=(12,-691),xytext=(10.7,-70),fontsize=11.5,ha='center',arrowprops={'arrowstyle':'->','color':MUTED,'lw':1})
    axs[1].bar(n,denom[:13],color=COLORS[2],width=.58);axs[1].set_yscale('log')
    basic_axes(axs[1],'Positive denominator q(n): log scale',ylabel='Denominator');axs[1].set_xticks(range(13));axs[1].set_ylim(.8,6500)
    axs[1].text(12,2730,'2730',ha='right',va='bottom',fontsize=10.5)
    save_figure(fig,STEMS[10]);C['S11']={'Bernoulli_rationals':list(map(str,bern)),'numerators':numer,'denominators':denom,'B1':'-1/2','exact_EGF_reciprocal_match':True}

    # 12: finite product truncated by degree, independently enumerated small counts.
    part=[0]*(N+1);part[0]=1
    for j in range(1,N+1):
        for n in range(j,N+1):part[n]+=part[n-j]
    enum=[len(partitions(n)) for n in range(11)]
    assert part[:11]==enum
    record_prefix('A000041',part)
    parts4=partitions(4);assert len(parts4)==5
    fig,axs=plt.subplots(1,2,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'width_ratios':[.85,1.5]})
    table(axs[0],[[' + '.join(map(str,p))] for p in parts4],[],['Partitions of 4'],font=13,scale=2)
    axs[0].set_title('Five choices of multiplicities')
    axs[1].bar(range(19),part,color=COLORS[0],width=.68)
    basic_axes(axs[1],'Prefix of the reciprocal product',ylabel='Partition count p(n)');axs[1].set_xticks([0,3,6,9,12,15,18])
    save_figure(fig,STEMS[11]);C['S12']={'partitions':part,'partitions_of_4':[list(p) for p in parts4],'independent_enumeration_through':10,'enumerated_counts':enum,'finite_factors':list(range(1,N+1))}

    # 13: binomial sum and polynomial-coefficient recurrence are separate code paths.
    apery=[sum(comb(n,k)**2*comb(n+k,k)**2 for k in range(n+1)) for n in range(N+1)]
    for n in range(1,N):
        assert (n+1)**3*apery[n+1]==(2*n+1)*(17*n*n+17*n+5)*apery[n]-n**3*apery[n-1]
    record_prefix('A005259',apery)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'height_ratios':[1.4,.7]})
    axs[0].plot(range(15),[log10(v) for v in apery[:15]],'-o',color=COLORS[0],ms=4)
    basic_axes(axs[0],'Apéry growth: exact integers, logarithmic display',ylabel=r'$\log_{10}A_n$');axs[0].set_xticks([0,3,6,9,12,14])
    axs[0].text(.02,.96,'A(0..3) = 1, 5, 73, 1445',transform=axs[0].transAxes,ha='left',va='top',fontsize=12)
    axs[1].axis('off')
    axs[1].text(.5,.68,'n = 2:  535 × 73 − 8 × 5 = 39015',ha='center',va='center',fontsize=14,color=COLORS[0])
    axs[1].text(.5,.25,'39015 ÷ 27 = 1445',ha='center',va='center',fontsize=14)
    save_figure(fig,STEMS[12]);C['S13']={'Apery':apery,'recurrence_n_range':[1,N-1],'worked_n':2,'worked_numerator':39015,'worked_divisor':27,'worked_A3':1445}

    # 14: multiplicative definitions and independent divisor inversion.
    mu=[0]+[factor_mu(n) for n in range(1,61)]
    phi=[0]+[sum(gcd(n,k)==1 for k in range(1,n+1)) for n in range(1,61)]
    mu_alt=[0,1]
    for n in range(2,61):mu_alt.append(-sum(mu_alt[d] for d in range(1,n) if n%d==0))
    assert mu==mu_alt
    assert all(sum(mu[d] for d in range(1,n+1) if n%d==0)==(n==1) for n in range(1,61))
    assert all(sum(phi[d] for d in range(1,n+1) if n%d==0)==n for n in range(1,61))
    record_prefix('A008683',mu[1:],1);record_prefix('A000010',phi[1:],1)
    divs=[d for d in range(1,13) if 12%d==0];mv=[mu[d] for d in divs];pv=[phi[d] for d in divs]
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',sharex=True)
    axs[0].bar(range(6),mv,color=[COLORS[0] if v>=0 else COLORS[1] for v in mv],width=.6);axs[0].axhline(0,color=MUTED,lw=1)
    basic_axes(axs[0],'Möbius divisor sum at 12 is zero',xlabel='',ylabel='mu(d)');axs[0].set(yticks=[-1,0,1],ylim=(-1.5,1.5))
    axs[1].bar(range(6),pv,color=COLORS[2],width=.6)
    for k,v in enumerate(pv):axs[1].text(k,v+.1,str(v),ha='center',fontsize=12)
    basic_axes(axs[1],'Totient divisor sum at 12 is twelve',xlabel='Divisor d of 12',ylabel='phi(d)');axs[1].set(xticks=range(6),xticklabels=divs,ylim=(0,5))
    save_figure(fig,STEMS[13]);C['S14']={'mu_indices_1_60':mu[1:],'phi_indices_1_60':phi[1:],'worked_divisors':divs,'worked_mu':mv,'worked_phi':pv,'mu_sum':sum(mv),'phi_sum':sum(pv),'prime_definition_vs_divisor_inversion_match':True}

    # 15: formulas, channel recurrences, and odd-binomial count for Gould.
    w=[n.bit_count() for n in range(64)];thue=[v%2 for v in w];gould=[2**v for v in w]
    for n in range(32):
        assert w[2*n]==w[n] and w[2*n+1]==w[n]+1
        assert thue[2*n]==thue[n] and thue[2*n+1]==1-thue[n]
        assert gould[2*n]==gould[n] and gould[2*n+1]==2*gould[n]
    odd_count=[sum(comb(n,k)%2 for k in range(n+1)) for n in range(64)]
    assert gould==odd_count
    record_prefix('A000120',w);record_prefix('A010060',thue);record_prefix('A001316',gould)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained')
    for panel,start in enumerate([0,8]):
        indices=list(range(start,start+8))
        rows=[[f'{n:04b}' for n in indices],w[start:start+8],thue[start:start+8],gould[start:start+8]]
        tab=table(axs[panel],rows,['Binary','Weight','Parity','Gould'],indices,font=12,scale=1.6)
        axs[panel].set_title(f'Binary addresses {start} through {start+7}',pad=13)
        # Shade odd parity to make the channel pattern legible without extra density.
        for column,n in enumerate(indices):
            if thue[n]:tab[(3,column)].set_facecolor('#F4DDD3')
    save_figure(fig,STEMS[14]);C['S15']={'binary_weight':w,'Thue_Morse':thue,'Gould':gould,'odd_binomial_count_match':True,'channel_recurrences_parent_range':[0,31]}

    # 16: boundary-aware prefix sums and backward differences.
    ints=list(range(N+1));tri=[n*(n+1)//2 for n in ints];tet=[comb(n+2,3) for n in ints];sq=[n*n for n in ints];cube=[n**3 for n in ints]
    assert all(tri[n]==sum(range(1,n+1)) and tet[n]==sum(tri[1:n+1]) for n in ints)
    assert all(tri[n]-tri[n-1]==n and tet[n]-tet[n-1]==tri[n] for n in range(1,N+1))
    assert all(sq[n]-sq[n-1]==2*n-1 and cube[n]-cube[n-1]==3*n*n-3*n+1 for n in range(1,N+1))
    record_prefix('A000027',ints[1:],1);record_prefix('A000217',tri);record_prefix('A000292',tet);record_prefix('A000290',sq);record_prefix('A000578',cube)
    fig,axs=plt.subplots(2,1,figsize=(8.1,4.1),layout='constrained',gridspec_kw={'height_ratios':[1.5,.7]})
    table(axs[0],[ints[1:7],tri[1:7],tet[1:7],sq[1:7],cube[1:7]],['n','Triangular','Tetrahedral','Square','Cube'],list(range(1,7)),font=12,scale=1.45)
    axs[0].set_title('Common indices: n = 1 through 6')
    axs[1].axis('off')
    for ypos,color,direction,operation in [(.75,COLORS[0],1,'prefix sum'),(.2,COLORS[1],-1,'difference')]:
        for xpos,label in [(.08,'n'),(.5,'T(n)'),(.92,'H(n)')]:
            axs[1].text(xpos,ypos,label,ha='center',va='center',fontsize=14,color=color)
        for left,right in [(.13,.44),(.56,.86)]:
            xa,xb=(left,right) if direction==1 else (right,left)
            axs[1].annotate('',xy=(xb,ypos),xytext=(xa,ypos),arrowprops={'arrowstyle':'->','lw':1.5,'color':color})
            axs[1].text((left+right)/2,ypos+.12,operation,ha='center',fontsize=10.5,color=color)
    save_figure(fig,STEMS[15]);C['S16']={'positive_integer_extension_at_zero':0,'triangular':tri,'tetrahedral':tet,'squares':sq,'cubes':cube,'difference_domain':'1<=n<=18','boundary_T0_H0':[0,0]}

    # Exact generated prefix comparison with fresh authenticated OEIS metadata.
    current=json.loads((ROOT/'evidence/OEIS_SOURCE_RECORDS.json').read_text())
    meta={r['id']:r for r in current['records']}
    assert len(prefixes)==30 and set(prefixes)==set(meta)
    for identifier,p in prefixes.items():
        assert p['initial_index']==meta[identifier]['initial_index'],identifier+' offset'
        assert p['first_eight_terms']==meta[identifier]['first_eight_terms'],identifier+' prefix'
    for item in inputs:item['sha256_after']=hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest();assert item['sha256']==item['sha256_after']
    outputs=[]
    for stem in STEMS:
        for suffix in ['.pdf','.png']:
            p=ROOT/'figures'/(stem+suffix)
            outputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest={
      'schema_version':1,'claim_id':'sequence-atlas-exact-definitions-v0.3',
      'repository':{'commit':None,'dirty':True,'artifact_version':'v0.3; local document source; no Git revision'},
      'command':['python','figures_sequences.py'],
      'environment':{'software':[f'Python {platform.python_version()}',f'NumPy {np.__version__}',f'Matplotlib {matplotlib.__version__}'],'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'All sixteen displayed finite constructions and worked examples reproduce direct definitions and stated independent checks; all thirty generated OEIS prefixes match pinned official metadata.',
        'coefficient_domain':'exact Python integers and fractions.Fraction rationals; floating point only for plotting coordinates',
        'conventions':'OEIS native offsets; B1=-1/2; ordinary versus exponential coefficients stated per lesson; causal/backward differences used only in stated ranges',
        'inputs':[p['path'] for p in inputs],
        'bounds':{'default_max_index':18,'sequence_prefix_terms':8,'permutation_max_n':8,'partition_enumeration_max_n':10,'divisor_max_n':60,'binary_max_n':63,'OEIS_source_commit':current['source_commit']},
        'non_claims':['Finite checks do not substitute for universal proofs of the classical identities.','No claim of novelty, asymptotic growth certification, generic fixed taps for triangular transforms, or Lean formalization.','Plot placement and logarithmic ordinates are approximate display coordinates; sequence arithmetic is exact.']},
      'randomness':{'used':False,'generator':'none','seed':None},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-t0,'exit_status':0},
      'outputs':outputs,'input_artifacts':inputs,
      'checks':[{'id':k,'status':'PASS','details':v} for k,v in C.items()]+[{'id':'official_OEIS_prefixes','status':'PASS','count':30}],
      'sequence_prefixes':prefixes,
      'result':'implementation and finite assertion verified in the stated range',
      'residual_risks':['Schema v1 is used for legacy compatibility; explicit input hashes are included as a supplementary field, but no machine-enforced resource cap is claimed.','Final assembled-PDF typography is checked by the parent guide workflow after chapter integration.']}
    (ROOT/'evidence/sequence_checks.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'sequence_figures':16,'exact_checks':'PASS','official_prefixes':30,'runtime_seconds':manifest['run']['runtime_seconds']}))

if __name__=='__main__':main()
