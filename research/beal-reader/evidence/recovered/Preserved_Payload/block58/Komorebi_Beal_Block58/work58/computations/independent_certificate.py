#!/usr/bin/env python3
"""Independent Block58 checker: imports no primary arithmetic.
Direct counts for EVERY good parameter pair in F_41 and F_59, both degrees.
Quadratic fields theta^2+theta+1 and explicit square-root multiplicities.
Conductor fields use sqrt(5), direct seventh powers, and subset determinants.
Standard library only; universal geometric applications are not certified here.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

QS=[41,59]
U=[97,197,293,491,587,883,1373,1471,1567,1667]
AB=[(0,1),(2,0),(3,0),(-1,2),(7,0),(3,1),(4,-1),(4,1),(5,-1),(5,2),(7,-2),
    (6,1),(7,-1),(7,2),(9,-2)]
NAMES=['phi','2','3','sqrt5','7','pi11','bar_pi11','pi19','bar_pi19','pi31','bar_pi31',
       'pi41','bar_pi41','pi59','bar_pi59']

def check(ok,msg):
    if not ok:raise ValueError(msg)

def trim(p):
    while len(p)>1 and p[-1]==0:p.pop()
    return p

def gcd_degree(f,g,q):
    f,g=trim(f[:]),trim(g[:])
    while g!=[0]:
        r=f[:];iv=pow(g[-1],-1,q)
        while len(r)>=len(g) and r!=[0]:
            d=len(r)-len(g);c=r[-1]*iv%q
            for i,b in enumerate(g):r[d+i]=(r[d+i]-c*b)%q
            trim(r)
        f,g=g,r
    return len(f)-1

def root_tables(q):
    check(q%3==2,'theta^2+theta+1 irreducibility')
    def mul(x,y):
        a,b=x;c,d=y
        return ((a*c-b*d)%q,(a*d+b*c-b*d)%q)
    r1=[0]*q;r2=[0]*(q*q);xs=[]
    for a in range(q):r1[a*a%q]+=1
    for a in range(q):
        for b in range(q):
            x=(a,b);square=mul(x,x);cube=mul(square,x);six=mul(cube,cube)
            r2[square[0]*q+square[1]]+=1;xs.append((a,b,*cube,*six))
    check(sum(r1)==q and r1[0]==1,'Base root multiplicities')
    check(sum(r2)==q*q and r2[0]==1 and sum(bool(x) for x in r2)==(q*q+1)//2,'Quadratic root multiplicities')
    return r1,r2,xs

def all_pair_counts(ref):
    q=ref['q'];check(q in QS,'Undeclared q')
    roots5=[r for r in range(q) if r*r%q==5];sq={x*x%q for x in range(q)}
    signs={1 if 3*(5-r)*pow(2,-1,q)%q in sq else -1 for r in roots5}
    check(len(roots5)==2 and len(signs)==1,'Twist roots/signs');nu=signs.pop()
    check(nu==ref['nu'] and ref['f']==1,'Primary twist/base-field error')
    rt1,rt2,xs=root_tables(q);p7={pow(c,7,q) for c in range(1,q)}
    expected={}
    for row in ref['rows']:
        for pair in row['admissible_pairs']:
            k=tuple(pair);check(k not in expected,'Duplicate primary member');expected[k]=row
    seen=set();counts={str(m):0 for m in (7,49,343)};traces=set();gcds=0;digest=hashlib.sha256()
    target=[q*q,-2*q*(q+1),(q+1)**2+2*q,-2*(q+1),1]
    for A in range(q):
        for B in range(q):
            if (pow(A,3,q)+pow(B,5,q))%q not in p7:continue
            seen.add((A,B));f=[5*B*B%q,12*A%q,0,10*B%q,0,0,1]
            derivative=[i*f[i]%q for i in range(1,7)]
            check(gcd_degree(f,derivative,q)==0,'Singular alleged good pair');gcds+=1
            n1=2+sum(rt1[(pow(x,6,q)+10*B*pow(x,3,q)+12*A*x+5*B*B)%q] for x in range(q))
            a=12*A%q;b=10*B%q;c=5*B*B%q
            n2=2+sum(rt2[((s+b*u+a*x+c)%q)*q+(t+b*v+a*y)%q] for x,y,u,v,s,t in xs)
            trace=q+1-n1;trace_square=q*q+1-n2;num=trace*trace-trace_square
            check(num%2==0,'Nonintegral Newton coefficient')
            P=[q*q,-q*trace,num//2,-trace,1]
            T=[x*(nu if i%2 else 1) for i,x in enumerate(P)]
            match={str(m):all((x-y)%m==0 for x,y in zip(T,target)) for m in (7,49,343)}
            e=expected.get((A,B));check(e is not None,'Primary misses an admissible pair')
            check((n1,n2,P,T,match)==(e['N1'],e['N2'],e['Pq_ascending'],e['twisted_polynomial'],e['matches']),
                  f'Independent direct point count disagrees at q={q},A={A},B={B}')
            for m in counts:counts[m]+=match[m]
            if match['7']:traces.add(-T[3])
            digest.update((json.dumps([A,B,n1,n2,P,T,match],sort_keys=True)+'\n').encode())
    check(seen==set(expected) and len(seen)==ref['pairs'],'Full pair coverage mismatch')
    check(counts==ref['matches_by_pairs'] and sorted(traces)==ref['residual_twisted_traces'],'Finite loci differ')
    return {'q':q,'method':'Direct every-pair degree-one and degree-two square-root counts; no orbit reduction',
      'pairs':len(seen),'N1_counts':len(seen),'N2_counts':len(seen),'smoothness_gcd_checks':gcds,
      'quadratic_field':'theta^2+theta+1','twist_from_radicand':nu,'matches_by_pairs':counts,
      'residual_twisted_traces':sorted(traces),'all_pair_result_sha256':digest.hexdigest()}

class Field:
    def __init__(self,q,root=None):
        check(q>2 and all(q%d for d in range(2,math.isqrt(q)+1)),'Residue modulus not prime')
        self.q=q;self.root=root;self.Q=q*q if root is None else q
        check(pow(5,(q-1)//2,q)==q-1 if root is None else root*root%q==5,'Residue root invalid')
    def elem(self,a,b=0):
        return ((a+b*self.root)%self.q,0) if self.root is not None else (a%self.q,b%self.q)
    def mul(self,x,y):
        a,b=x;c,d=y
        return self.elem(a*c+5*b*d,a*d+b*c)
    def pow(self,x,n):
        v=(1,0)
        while n:
            if n&1:v=self.mul(v,x)
            x=self.mul(x,x);n//=2
        return v
    def phi(self,a,b):
        half=(self.q+1)//2
        return self.elem(a+b*half,b*half)

def det(a):
    n=len(a);check(all(len(r)==n for r in a),'Nonsquare determinant')
    states=[0]*(1<<n);states[0]=1
    for mask in range(1,1<<n):
        i=mask.bit_count()-1;pos=0;z=0
        for j in range(n):
            if mask>>j&1:
                z+=(-1 if (i+pos)%2 else 1)*a[i][j]*states[mask^(1<<j)];pos+=1
        states[mask]=z
    return states[-1]

def residue_rank(ref):
    check(ref['universe']==U,'Conductor universe altered')
    check([r['name'] for r in ref['row_elements']]==NAMES,'Row names altered')
    check([r['phi_coefficients'] for r in ref['row_elements']]==[list(x) for x in AB],'Row elements altered')
    own=[]
    for q in U:
        roots=[r for r in range(q) if r*r%q==5]
        specs=sorted([(((1+r)*pow(2,-1,q))%q,r) for r in roots]) if roots else [(None,None)]
        for phi,sqrt5 in specs:
            F=Field(q,sqrt5);z=F.Q-1;h=0
            while z%7==0:z//=7;h+=1
            symbols=[F.pow(F.phi(*ab),(F.Q-1)//7) for ab in AB]
            generator=next(x for x in symbols if x!=(1,0));table={F.pow(generator,j):j for j in range(7)}
            check(len(table)==7 and F.pow(generator,7)==(1,0),'Seventh root not primitive')
            own.append({'q':q,'phi_root':phi,'norm':F.Q,'h':h,'logs':[table[s] for s in symbols]})
    check(len(own)==len(ref['places'])==12,'Place coverage')
    scales=[]
    for o,r in zip(own,ref['places']):
        check(all(o[k]==r[k] for k in ('q','phi_root','norm','h')),'Place identification')
        raw=r['logs_mod7'];first=next(i for i,x in enumerate(o['logs']) if x)
        c=raw[first];check(c%7!=0,'Normalization vanishes')
        check([v*pow(c,-1,7)%7 for v in raw]==o['logs'],'Direct seventh-power symbols disagree')
        scales.append(c)
    M=[[o['logs'][i] for o in own] for i in range(len(AB))]
    raw=[[v*c%7 for v,c in zip(row,scales)] for row in M]
    check(raw==ref['matrix_mod7'],'Duplicated primary residue matrix disagrees')
    rows=ref['rank_minor']['row_indices'];check(len(rows)==len(set(rows))==12 and all(0<=x<15 for x in rows),'Bad minor rows')
    D=det([row for i,row in enumerate(raw) if i in rows])
    canonical_det=det([row for i,row in enumerate(M) if i in rows])
    check(D==ref['rank_minor']['integer_determinant'] and D%7==ref['rank_minor']['determinant_mod7']!=0,'Full-column determinant failed')
    check(canonical_det%7!=0,'Independent-basis determinant vanished')
    A=[3,0,0,5,2,5,0,0,0,0,1,0];B=[5,0,2,0,0,0,0,0,2,5,1,0]
    check(all(sum(x*y for x,y in zip(r,v))%7==0 for v in (A,B) for r in raw[:11]),'Old kernel control invalid')
    E=[[sum(x*y for x,y in zip(raw[i],v))%7 for v in (A,B)] for i in (11,13)]
    check(E==[[3,4],[0,4]]==ref['new_rows_on_old_kernel'] and det(E)%7==5,'Old-pattern contradiction failed')
    norms={NAMES[i]:a*a+a*b-b*b for i,(a,b) in enumerate(AB) if i>=11}
    check(norms==ref['norms_new_generators']==dict(pi41=41,bar_pi41=41,pi59=59,bar_pi59=59),'Principal norms failed')
    return {'fields':12,'direct_seventh_power_symbols':len(AB)*12,'rank':12,'kernel_dimension':0,
        'integer_determinant':D,'canonical_basis_determinant':canonical_det,'column_scales':scales,
        'new_rows_on_old_kernel':E,'norms':norms,'does_not_use_kummer_coefficients':True}

def discriminant_audit(path):
    d=json.loads(path.read_text());r=d['prime2549'];q=2549;mod=343
    check(r['q']==q and all(q%i for i in range(2,51)), 'Independent prime proof')
    check(q%5==4 and (q-1)//49==52 and 52%7!=0, 'Splitting/depth arithmetic')
    check(r['D_divisibility']==117649==mod*mod and r['D_upper_bound']==40784==16*q,
          'Discriminant numerical bounds')
    check(117649>40784 and 100**2<=4*q<101**2, 'Strict collapse bound')
    survivors=[t for t in range(-100,101) if (t-(q+1))%mod==0]
    check(not survivors and survivors==r['allowed_integer_traces'], 'Trace interval not empty')
    check((q+1)%mod==149==r['trace_residue'], 'Trace residue mismatch')
    roots=[x for x in range(q) if x*x%q==5]
    check(roots==r['sqrt5_roots'], 'Square roots of five mismatch')
    # Re-enumerate by discriminant, not by the primary program's c2 interval.
    choices=[]
    for s in range(-201,202):
        if (s-2*(q+1))%mod:continue
        for D in range(0,16*q+1):
            if (s*s-D)%4:continue
            c=(s*s-D)//4+2*q
            if (c-((q+1)**2+2*q))%mod:continue
            z=16*q-D-s*s
            if z>=0 and z*z>=4*s*s*D:choices.append(dict(trace=s,middle_coefficient=c,D=D))
    choices.sort(key=lambda x:(x['trace'],x['middle_coefficient']))
    check(choices==d['rank_four_only_candidates'] and len(choices)==18, 'Generic Weil candidate enumeration')
    control=d['rank_four_not_rank_two_negative_control']
    a,b=-47,49;tr=2*a+b;norm=a*a+a*b-b*b
    check(tr==-45 and norm+2*q==2603, 'Coefficient-field factorization')
    P=[q*q,-q*tr,norm+2*q,-tr,1]
    check(P==control['polynomial_ascending'] and tr*tr-4*norm==12005, 'Control quartic/discriminant')
    check(12005==5*49**2 and 12005<110**2 and 155**2<16*q,
          'Exact real-root magnitude control')
    check(12005%117649!=0 and b%343!=0 and b%49==0, 'Insufficient scalar precision control')
    return {'prime2549_verified':True,'integer_trace_candidates':0,'generic_Weil_candidates':18,
            'rank_four_only_control_verified':True,'point_counts_at2549':0}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--primary',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--discriminant',required=True,type=Path);a=ap.parse_args()
    p=json.loads(a.primary.read_text());check([r['q'] for r in p['finite_frobenius']]==QS,'Good-prime scope')
    # Check symbols first so an altered row is rejected without repeating all pair counts.
    R=residue_rank(p['reciprocity']);D=discriminant_audit(a.discriminant);F=[all_pair_counts(r) for r in p['finite_frobenius']]
    out={'schema':'komorebi.beal.block58.independent.v1','status':'PASS_INDEPENDENT_FINITE_ASSERTIONS',
      'primary_sha256':hashlib.sha256(a.primary.read_bytes()).hexdigest(),'imports_primary_arithmetic':False,
      'finite_frobenius':F,'reciprocity':R,'discriminant':D,'nonclaims':['Not independent mathematical review','No upstream geometry verification']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'every_pair_N1_N2_checks':sum(x['pairs'] for x in F),
       'independent_power_symbols':R['direct_seventh_power_symbols'],'rank':R['rank']}))
if __name__=='__main__':main()
