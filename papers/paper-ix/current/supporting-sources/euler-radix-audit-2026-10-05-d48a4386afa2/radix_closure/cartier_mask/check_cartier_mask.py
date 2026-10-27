#!/usr/bin/env python3
"""Exact rational/spatial radix checks; no floating point or external modules."""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import json, sys, importlib.util

def trim(a):
    a=list(map(F,a))
    while len(a)>1 and not a[-1]: a.pop()
    return a
def add(a,b):
    c=[F(0)]*max(len(a),len(b))
    for i,x in enumerate(a):c[i]+=x
    for i,x in enumerate(b):c[i]+=x
    return trim(c)
def scale(a,q):return trim([x*q for x in a])
def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return trim(c)
def divmodp(a,b):
    a=trim(a);b=trim(b);q=[F(0)]*max(1,len(a)-len(b)+1)
    while a!=[0] and len(a)>=len(b):
        i=len(a)-len(b);z=a[-1]/b[-1];q[i]+=z
        a=add(a,scale([0]*i+b,-z))
    return trim(q),trim(a)
def invmod(a,m):
    r0,r1=m,a;s0,s1=[F(0)],[F(1)]
    while r1!=[0]:
        q,r=divmodp(r0,r1);r0,r1=r1,r;s0,s1=s1,add(s0,scale(mul(q,s1),-1))
    assert len(r0)==1
    return divmodp(scale(s0,1/r0[0]),m)[1]
def equal(f,g):return mul(f[0],g[1])==mul(g[0],f[1])
def section(f,b):
    n,d=f;nm=[(-1)**i*x for i,x in enumerate(n)];dm=[(-1)**i*x for i,x in enumerate(d)]
    top=add(mul(n,dm),scale(mul(nm,d),(-1)**b))
    bot=scale(mul(d,dm),2)
    assert all(not x for i,x in enumerate(top) if i%2!=b)
    assert all(not x for i,x in enumerate(bot) if i%2)
    return trim(top[b::2]),trim(bot[::2])
def state_step(v,b):
    x,y=v
    return (x,x-y) if b==0 else (-x+y,y)
def mass(a,k):
    if k==0:return F(4)
    if not a%2:return F(0)
    if k==1:return F(4)
    v=(2,4) if not ((a>>1)&1) else (4,2)
    for j in range(2,k):v=state_step(v,(a>>j)&1)
    return F(sum(v),3)
def rank(a):
    a=[list(map(F,r)) for r in a];row=0
    for col in range(len(a[0])):
        p=next((p for p in range(row,len(a)) if a[p][col]),None)
        if p is None:continue
        a[row],a[p]=a[p],a[row];z=a[row][col];a[row]=[x/z for x in a[row]]
        for p in range(len(a)):
            if p!=row and a[p][col]:
                z=a[p][col];a[p]=[x-z*y for x,y in zip(a[p],a[row])]
        row+=1
    return row
def bernoulli(n):
    out=[F(1)]
    for m in range(1,n+1):out.append(-sum(comb(m+1,j)*out[j] for j in range(m))/(m+1))
    return out
def prefix_terms(r,overrides=None):
    bb=bernoulli(2*r);out={}
    for n in range(r):
        beta=F(1) if not n else -F(4**n*(2*n-1),factorial(2*n))*bb[2*n]
        if overrides and n in overrides:beta=overrides[n]
        k=2*n-2
        for j,c in [(9,F(36**n,24)),(3,F(4**n,8)-F(36**n,24)),(1,-F(4**n,8))]:
            out[(j,k)]=out[(-j,k)]=beta*c
    return out
def laurent_jet(terms,n):
    # n! [t^n] sum c exp(j*t)*t^k, including negative k.
    return factorial(n)*sum(c*F(j**(n-k),factorial(n-k)) for (j,k),c in terms.items() if n>=k)
def principal(terms):
    return {h:sum(c*F(j**(h-k),factorial(h-k)) for (j,k),c in terms.items() if h>=k) for h in [-2,-1]}
def dissect(terms,N,a):
    out={}
    for (j,k),c in terms.items():
        if (j-a)%N==0:
            q=((j-a)//N,k);out[q]=out.get(q,F(0))+c*F(N)**(-k)
    return out
def main(path):
    R=([0,2,0,2],[1,0,-1,0,1]);S=([2,2],[1,-1,1]);U=([1],[1,1,1]);V=([0,1],[1,1,1])
    relations=[(section(R,0),([0],[1])),(section(R,1),S),
      (section(S,0),([2,4],[1,1,1])),(section(S,1),([4,2],[1,1,1])),
      (section(U,0),([1,1],[1,1,1])),(section(U,1),([-1],[1,1,1])),
      (section(V,0),([0,-1],[1,1,1])),(section(V,1),([1,1],[1,1,1]))]
    assert all(equal(a,b) for a,b in relations)
    orbit=set();queue=[(2,4),(4,2)]
    while queue:
        v=queue.pop()
        if v in orbit:continue
        orbit.add(v);queue.extend(state_step(v,b) for b in [0,1])
    assert len(orbit)==6
    residue_checks=0
    for k in range(1,8):
        N=2**k;m=[-1]+[0]*(N-1)+[1]
        rr=divmodp(mul(R[0],invmod(R[1],m)),m)[1];rr+= [F(0)]*(N-len(rr))
        for a in range(N):assert rr[a]==mass(a,k);residue_checks+=1
    # Independent coefficient-kernel growth discriminator in T=y-1.
    coeff=[];num=[4,8,6,2];den=[1,2,5,4,1]
    for n in range(161):coeff.append((num[n] if n<4 else 0)-sum(den[j]*coeff[n-j] for j in range(1,min(4,n)+1)))
    ranks=[rank([[coeff[(2**e)*n] for n in range(6)] for e in range(d)]) for d in range(1,7)]
    assert ranks==list(range(1,7))
    # Mellin recursion, checked by moments computed directly from U(exp t).
    uu=[F(1,3)]
    for n in range(1,17):uu.append(-sum(comb(n,j)*(1+2**(n-j))*uu[j] for j in range(n))/3)
    vv=[sum(comb(n,j)*uu[j] for j in range(n+1)) for n in range(17)]
    FU=lambda s,z:sum(comb(2*s,j)*z**j*uu[j] for j in range(2*s+1))
    FV=lambda s,z:sum(comb(2*s,j)*z**j*vv[j] for j in range(2*s+1))
    ee=[1];mellin_checks=0
    for s in range(9):
        if s:ee.append(-sum(comb(2*s,2*j)*ee[j] for j in range(s)))
        for z in [F(2),F(4),F(4,3),F(8,5)]:
            az=(1+z)**(2*s);zs=2*z/(1+z)
            assert FU(s,z)==FU(s,2*z)+FV(s,2*z)-az*FU(s,zs)
            assert FV(s,z)==-FV(s,2*z)+az*(FU(s,zs)+FV(s,zs))
            mellin_checks+=2
        assert (1+3*9**s)*ee[s]==2*FU(s,F(4))+4*FV(s,F(4))+9**s*(4*FU(s,F(4,3))+2*FV(s,F(4,3)))
        mellin_checks+=1
    boundary=[];moment_checks=0
    for r in [1,2,3,5,9]:
        tt=prefix_terms(r);sections=[dissect(tt,8,a) for a in range(8)]
        pp=[principal(s) for s in sections]
        wanted={1:(F(-16,3),F(8,3)),3:(F(16,3),F(0)),5:(F(16,3),F(-16,3)),7:(F(-16,3),F(8,3))}
        for a in range(8):assert (pp[a][-2],pp[a][-1])==wanted.get(a,(F(0),F(0)))
        for n in range(0,19):
            reg=F(0);defect=F(0)
            for a,ss in enumerate(sections):
                for j in range(n+1):reg+=comb(n,j)*a**(n-j)*8**j*laurent_jet(ss,j)
                defect+=pp[a][-1]*F(a**(n+1),8*(n+1))+pp[a][-2]*F(a**(n+2),64*(n+1)*(n+2))
            assert laurent_jet(tt,n)==reg+defect
            expected=F(1-2*5**(n+1)+7**(n+1),3*(n+1))+F(-1+3**(n+2)+5**(n+2)-7**(n+2),12*(n+1)*(n+2))
            assert defect==expected
            moment_checks+=1
        boundary.append({'r':r,'principal_parts':{str(a):[str(pp[a][-2]),str(pp[a][-1])] for a in [1,3,5,7]}})
    # Reproduce one complete 32-bit source-jet contact from the audited base.
    source=Path(__file__).resolve().parents[2]/'shifted_obstruction/critical_arithmetic/newton/check_contact_wronskian.py'
    spec=importlib.util.spec_from_file_location('audited_contact_helper',source);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    numerator=[0];fall=[1]
    for n in range(18):
        numerator=h.add(numerator,h.scale(fall,h.fm(F(8**n,factorial(n+1)))))
        fall=h.mul(fall,[-n,1])
    AA=h.mul(numerator,[pow(-2,j,h.MOD) for j in range(h.BITS)])
    ll=sum((-1)**(k+1)*F(8**k,k) for k in range(1,h.BITS+1))
    JJ=h.trim([0]+[h.fm(ll**n/F(8*factorial(n))) for n in range(1,h.BITS+1)])
    bb=h.bernoulli(22);be=[F(1)]+[-F(4**n*(2*n-1),factorial(2*n))*bb[2*n] for n in range(1,12)]
    PP=[[1]]
    for m in range(11):PP.append(h.mul(PP[-1],h.mul([-m,1],[-2*m-1,2])))
    packets=[h.mul(PP[m],h.shift(AA,-m)) for m in range(12)]
    r,a=2,3;hh=[0]
    for q in range(10):hh=h.add(hh,h.scale(packets[q],h.fm(8**(r+q)*be[r+q])))
    va,wa=h.ev(hh,a),h.ev(h.der(hh),a);aa,ja=h.ev(AA,a),h.ev(JJ,a);ap,jp=h.ev(h.der(AA),a),h.ev(h.der(JJ),a)
    det=(aa*jp-ap*ja)%h.MOD;inverse=pow(det,-1,h.MOD)
    d0=(va*jp-wa*ja)*inverse%h.MOD;d1=(aa*wa-ap*va)*inverse%h.MOD
    qq=h.add(h.add(hh,h.scale(AA,d0),-1),h.scale(JJ,d1),-1)
    assert h.ev(qq,a)==h.ev(h.der(qq),a)==0
    deformed=prefix_terms(4,{2:F(d0,8**2),3:F(d1,8**3)})
    for residue in range(8):assert principal(dissect(deformed,8,residue))==principal(dissect(prefix_terms(2),8,residue))
    deformation={'base_actual_cutoff':r,'quotient_point':a,'exponent_point':r+a,'precision_bits':h.BITS,
      'free_packet_coefficients':[d0,d1],'unit_jet_determinant':det,'residual_value_modulus':h.ev(qq,a),
      'residual_slope_modulus':h.ev(h.der(qq),a),'all_eight_principal_parts_unchanged':True,
      'nonclaim':'The two free coefficients are modular approximations to dyadic contact coefficients, not actual Bernoulli coefficients.'}
    result={'exact_rational_section_identities':len(relations),'recurrent_states':[list(v) for v in sorted(orbit)],
      'dyadic_residue_checks':residue_checks,'residue_depth_range':[1,7],
      'Amice_coefficient_kernel_ranks':ranks,'prefix_cutoffs':[1,2,3,5,9],
      'moment_reconstruction_checks':moment_checks,'moment_degree_range':[0,18],'boundary':boundary,
      'Mellin_recursion_checks':mellin_checks,'Mellin_integer_exponents':[0,8],'free_two_jet_contact':deformation,
      'scope':'Exact bounded checks only. Uniform closure and infinite-rank statements have separate proofs. No stationary nonvanishing conclusion.'}
    Path(path).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','identities':len(relations),'residues':residue_checks,'moment_checks':moment_checks,'kernel_ranks':ranks}))
if __name__=='__main__':main(sys.argv[1])
