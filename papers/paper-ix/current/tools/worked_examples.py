#!/usr/bin/env python3
"""Eight exact reading examples. No Lean invocation and no universal claims from sampling."""
from __future__ import annotations
from fractions import Fraction
from math import factorial,comb
from pathlib import Path
import argparse,json,hashlib

def coefficients(N:int,j:int,last:int)->list[Fraction]:
    if N<1 or not 0<=j<N or last<0: raise ValueError('Require N>0, 0<=j<N, last>=0.')
    a=[Fraction(factorial(j),factorial(N*n+j)) for n in range(last+1)]
    b=[Fraction(1)]
    for n in range(1,last+1): b.append(-sum(a[k]*b[n-k] for k in range(1,n+1)))
    return [b[n]*factorial(N*n) for n in range(last+1)]

def recurrence(N:int,j:int,last:int)->list[Fraction]:
    c=[Fraction(1)]
    for n in range(1,last+1):
        c.append(-sum(Fraction(comb(N*n+j,N*k))*c[k] for k in range(n))/comb(N*n+j,N*n))
    return c

def valuation(x:Fraction|int,p:int)->int|None:
    x=Fraction(x)
    if not x:return None
    a,b=abs(x.numerator),x.denominator;v=0
    while a%p==0:a//=p;v+=1
    while b%p==0:b//=p;v-=1
    return v

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--figures',type=Path);args=ap.parse_args()
    counts={}
    def check(b:bool,group:str)->None:
        if not b:raise AssertionError(group)
        counts[group]=counts.get(group,0)+1
    for N in (1,2,3,4,6,8):
        for j in range(N):
            a=coefficients(N,j,12);b=recurrence(N,j,12)
            for x,y in zip(a,b):check(x==y,'independent_coefficient_equalities')
    rows=[coefficients(4,j,4) for j in range(4)]
    check(rows[0]==list(map(Fraction,[1,-1,69,-33661,60376809])),'displayed_definitions')
    check(rows[1][1:3]==[Fraction(-1,5),Fraction(121,45)],'displayed_definitions')
    c=coefficients(6,3,2);d=c[2]-c[1]
    check(d==Fraction(64,455) and valuation(d,3)==0,'normalization_counterexample')
    check(6*d==Fraction(384,455) and valuation(6*d,3)==1,'normalization_counterexample')
    sign=coefficients(3,0,2);twist=[(-1)**n*x for n,x in enumerate(sign)]
    check(sign==list(map(Fraction,[1,-1,19])),'odd_prime_sign_control')
    check(sign[1]-sign[0]==-2 and valuation(-2,3)==0,'odd_prime_sign_control')
    check(twist==list(map(Fraction,[1,1,19])) and valuation(twist[2]-twist[1],3)==2,'odd_prime_sign_control')
    c0=coefficients(4,0,32);row=c0[:];newton=[]
    while row:newton.append(row[0]);row=[b-a for a,b in zip(row,row[1:])]
    for k in range(1,33):check(valuation(newton[k],2)==2*k-k.bit_count(),'newton_valuations')
    for n in range(33):
        check(sum(comb(n,k)*newton[k] for k in range(n+1))==c0[n],'newton_exact_reconstruction')
        check((sum(comb(n,k)*newton[k] for k in range(min(n,4)+1))-c0[n])%256==0,'newton_precision_256')
    tower=[];x=1
    for L in range(1,8):
        modulus=3**L;r=(x*x-7)//modulus;jac=2*x%3
        check((x*x-7)%modulus==0,'smooth_tower')
        digits=[t for t in range(3) if (r+jac*t)%3==0]
        check(len(digits)==1,'smooth_tower')
        t=digits[0];y=x+modulus*t
        check((y*y-7)%(3*modulus)==0 and y%modulus==x,'smooth_tower')
        tower.append(dict(L=L,modulus=modulus,x=x,residual=r,digit=t,next=y))
        x=y
    blocked=[(3*t)**2-3 for t in range(3)]
    for z in blocked:check(z%9==6,'singular_no_lift')
    for t in range(3):check((3*t)**2%9==0,'singular_positive_control')
    shared=[]
    for t in range(3):
        pair=[t%3,(t-1)%3];shared.append(pair)
        check(pair!=[0,0],'shared_obstruction')
        check([(3*t)//3%3,(3*t-3)//3%3]==pair,'shared_obstruction')
    check(any(a==0 for a,b in shared) and any(b==0 for a,b in shared),'shared_obstruction')
    motion=[]
    for A in range(2,8):
        root=-3**(A-1)
        check(3*root+3**A==0,'weighted_motion')
        check(valuation(3**A,3)==A and valuation(root,3)==A-1,'weighted_motion')
        motion.append(dict(A=A,root=root,coefficient_valuation=A,motion_valuation=A-1))
    data=dict(status='PASS',scope='Exact finite worked examples, not new universal theorems or a Lean run.',counts=counts,total_checks=sum(counts.values()),first_rows=[[str(x) for x in r[:3]] for r in rows],normalization={'C1':str(c[1]),'C2':str(c[2]),'difference':str(d),'original_difference':str(6*d)},sign={'C':[str(x)for x in sign],'twisted':[str(x)for x in twist]},newton={'first_five':[str(x)for x in newton[:5]],'mod256':[int(x%256)for x in newton[:5]],'valuations':[valuation(x,2)for x in newton]},tower=tower,blocked_residues=[z%9 for z in blocked],shared_residuals=shared,motion=motion)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,indent=2)+'\n')
    if args.figures:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        args.figures.mkdir(parents=True,exist_ok=True)
        def save(fig,name):
            fig.tight_layout(pad=1.4);fig.savefig(args.figures/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None});fig.savefig(args.figures/(name+'.png'),dpi=150,bbox_inches='tight');plt.close(fig)
        def table(name,values,colnames,rowlabels=None):
            fig,ax=plt.subplots(figsize=(6.8,2.3));ax.axis('off')
            t=ax.table(cellText=values,colLabels=colnames,rowLabels=rowlabels,loc='center',cellLoc='center');t.auto_set_font_size(False);t.set_fontsize(11);t.scale(1,1.8);save(fig,name)
        table('reciprocal_rows',[[str(j)]+data['first_rows'][j] for j in range(4)],['address j','C(0)','C(1)','C(2)'])
        fig,ax=plt.subplots(figsize=(6.8,2.8));ax.bar(['normalized difference','original Euler difference'],[0,1]);ax.axhline(1,linestyle='--',linewidth=1);ax.set(ylabel='3-adic valuation',ylim=(-.3,1.6),yticks=[0,1]);ax.text(0,.16,'64/455',ha='center');ax.text(1,1.15,'384/455',ha='center');save(fig,'normalization_loss')
        table('odd_prime_sign',[[str(n),str(sign[n]),str(twist[n])] for n in range(3)],['row n','C at width 3, address 0','(-1)^n C(n)'])
        fig,ax=plt.subplots(figsize=(6.8,2.9));ks=list(range(1,17));ax.plot(ks,[valuation(newton[k],2)for k in ks],marker='o');ax.axhline(8,linestyle='--',label='precision cutoff: 8 bits');ax.set(xlabel='Newton order k',ylabel='v2 of the Newton coefficient',xticks=[1,2,3,4,5,8,12,16]);ax.legend(frameon=False);save(fig,'newton_cutoff')
        table('smooth_tower',[[str(v[k])for k in ['L','modulus','x','digit','next']] for v in tower[:5]],['L','3^L','current x','next digit','next x'])
        table('singular_block',[[str(t),str(3*t),str(blocked[t]),str(blocked[t]%9)]for t in range(3)],['digit t','candidate y','y^2 - 3','residue mod 9'])
        fig,ax=plt.subplots(figsize=(5.6,3));ax.scatter([0],[0],marker='x',s=120,label='required residual');ax.scatter([p[0]for p in shared],[p[1]for p in shared],s=70,label='available shared digits');
        for t,(a,b) in enumerate(shared):ax.annotate('t = '+str(t),(a,b),xytext=(8,5),textcoords='offset points')
        ax.set(xlabel='first residual mod 3',ylabel='second residual mod 3',xticks=[0,1,2],yticks=[0,1,2],xlim=(-.3,2.7),ylim=(-.3,2.5));ax.legend(frameon=False,loc='upper right');save(fig,'shared_obstruction')
        fig,ax=plt.subplots(figsize=(6.8,2.8));aa=[v['A']for v in motion];ax.plot(aa,aa,marker='o',label='coefficient precision');ax.plot(aa,[a-1 for a in aa],marker='s',label='root displacement precision');ax.set(xlabel='A in 3x + 3^A',ylabel='3-adic valuation',xticks=aa);ax.legend(frameon=False);save(fig,'weighted_motion')
    print(json.dumps({'status':'PASS','checks':sum(counts.values()),'counts':counts},indent=2))
if __name__=='__main__':main()
