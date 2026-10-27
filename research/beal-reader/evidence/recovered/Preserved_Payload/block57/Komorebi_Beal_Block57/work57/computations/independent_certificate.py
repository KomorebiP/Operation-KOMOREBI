#!/usr/bin/env python3
"""Independent Block57 certificate verifier. No imports of primary arithmetic.
Uses sqrt(5) residue fields and direct seventh-power symbols. Matrix rank is
certified by subset-expansion integer determinants and Cramer's rule; remaining
kernel restrictions use only 1x1 and 2x2 minors. Standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from math import isqrt
from pathlib import Path

QS=[97,197,293,491,587,883,1373,1471,1567,1667]
NAMES=['phi','2','3','sqrt5','7','pi11','bar_pi11','pi19','bar_pi19','pi31','bar_pi31']
AB=[(0,1),(2,0),(3,0),(-1,2),(7,0),(3,1),(4,-1),(4,1),(5,-1),(5,2),(7,-2)]

def check(ok,msg):
    if not ok: raise ValueError(msg)

class SqrtField:
    def __init__(self,q,root=None):
        check(q>=2 and all(q%d for d in range(2,isqrt(q)+1)),'not prime')
        self.q=q;self.root=root;self.size=q*q if root is None else q
        if root is None:check(pow(5,(q-1)//2,q)==q-1,'inert field not irreducible')
        else:check(root*root%q==5,'bad split root')
    def elt(self,a,b=0):
        if self.root is not None:return ((a+b*self.root)%self.q,0)
        return (a%self.q,b%self.q)
    def product(self,u,v):
        a,b=u;c,d=v
        return self.elt(a*c+5*b*d,a*d+b*c)
    def exp(self,x,e):
        z=(1,0)
        for bit in bin(e)[2:]:
            z=self.product(z,z)
            if bit=='1':z=self.product(z,x)
        return z
    def phi_element(self,a,b):
        inv2=(self.q+1)//2
        return self.elt(a+b*inv2,b*inv2)

def determinant_dp(a):
    """Leibniz expansion by subsets, not elimination/Bareiss."""
    n=len(a);check(all(len(r)==n for r in a),'nonsquare')
    dp=[0]*(1<<n);dp[0]=1
    for mask in range(1,1<<n):
        k=mask.bit_count();row=k-1;value=0;pos=0
        for j in range(n):
            if mask>>j&1:
                sign=-1 if (row+pos)%2 else 1
                value+=sign*a[row][j]*dp[mask^(1<<j)];pos+=1
        dp[mask]=value
    return dp[-1]

def norm_last(v):
    j=next(i for i in range(len(v)-1,-1,-1) if v[i])
    inv=pow(v[j],-1,7)
    return [x*inv%7 for x in v]

def constrained_nullity(basis,zero_mask):
    # All vectors lie in the proven two-dimensional kernel.
    d=len(basis[0]);rows=[(basis[0][i],basis[1][i]) for i in range(d) if not (zero_mask>>i&1)]
    nonzero=[(a%7,b%7) for a,b in rows if a%7 or b%7]
    if not nonzero:return 2
    a,b=nonzero[0]
    return 0 if any((a*d-b*c)%7 for c,d in nonzero[1:]) else 1

def mask_for(K,a,b=(0,0,0)):
    ans=0
    for i,row in enumerate(K):
        if sum(x*y for x,y in zip(row,a))%7==0 and sum(x*y for x,y in zip(row,b))%7==0:ans|=1<<i
    return ans

def main(primary_path:Path,output:Path):
    p=json.loads(primary_path.read_text())
    check(p['universe']==QS,'declared universe changed')
    check([x['name'] for x in p['row_elements']]==NAMES,'row names changed')
    check([x['phi_coefficients'] for x in p['row_elements']]==[list(x) for x in AB],'generators changed')
    own=[];symbol_count=0;order_checks=0
    for q in QS:
        roots=[x for x in range(q) if x*x%q==5]
        specs=[( (1+x)*pow(2,-1,q)%q,x) for x in roots] if roots else [(None,None)]
        specs.sort(key=lambda x:-1 if x[0] is None else x[0])
        for phi_root,sqrt_root in specs:
            f=SqrtField(q,sqrt_root);h=0;k=f.size-1
            while k%7==0:h+=1;k//=7
            check(h>=2,'not a high place')
            elements=[f.phi_element(a,b) for a,b in AB]
            syms=[f.exp(x,(f.size-1)//7) for x in elements]
            z=next(x for x in syms if x!=(1,0));check(f.exp(z,7)==(1,0),'bad root order')
            table={f.exp(z,j):j for j in range(7)};check(len(table)==7,'not primitive seventh root')
            logs=[table[x] for x in syms]
            first=next(i for i,x in enumerate(logs) if x)
            check(logs[first]==1,'canonical direct-symbol normalization failure')
            symbol_count+=len(syms);order_checks+=7
            own.append({'q':q,'phi_root':phi_root,'h':h,'norm':f.size,'canonical_logs':logs})
    check(len(own)==12,'place coverage failed')
    scales=[]
    for i,(o,a) in enumerate(zip(own,p['places'])):
        check(all(o[k]==a[k] for k in ('q','phi_root','h','norm')),'place identification failed')
        raw=[a['logs_mod7'][name] for name in NAMES]
        first=next(j for j,x in enumerate(raw) if x%7);c=raw[first]%7
        check([(x*pow(c,-1,7))%7 for x in raw]==o['canonical_logs'],'independent symbols disagree')
        scales.append(c)
    M=[[o['canonical_logs'][i] for o in own] for i in range(len(NAMES))]
    # Check both stored matrix and stored logs, not just one copy.
    for i in range(len(NAMES)):
        for j in range(12):
            check(M[i][j]==p['matrix_mod7'][i][j]*pow(scales[j],-1,7)%7,'matrix/log mismatch')
    K=[[M[i][j] for i in (0,2,3)] for j in range(12)]
    for j in range(12):
        check(K[j]==[x*pow(scales[j],-1,7)%7 for x in p['kummer_rows_mod7'][j]],'Kummer normalization mismatch')
    rows=p['rank_minor']['rows'];cols=p['rank_minor']['columns']
    check(len(set(rows))==len(rows)==10 and len(set(cols))==len(cols)==10,'rank witness dimensions')
    A=[[M[i][j] for j in cols] for i in rows];d=determinant_dp(A)
    check(d%7!=0,'rank-ten minor vanished')
    rawminor=[[p['matrix_mod7'][i][j] for j in cols] for i in rows]
    check(determinant_dp(rawminor)==p['rank_minor']['integer_determinant'],'raw integer determinant differs')
    frees=[i for i in range(12) if i not in cols];basis=[];cramer_count=0
    for free in frees:
        rhs=[-M[i][free] for i in rows];v=[0]*12;v[free]=1
        for j,col in enumerate(cols):
            B=[line[:] for line in A]
            for i in range(10):B[i][j]=rhs[i]
            v[col]=determinant_dp(B)*pow(d,-1,7)%7;cramer_count+=1
        check(all(sum(x*y for x,y in zip(line,v))%7==0 for line in M),'Cramer vector fails an unused row')
        basis.append(v)
    check(len(basis)==2 and basis[0][frees[0]]==1 and basis[1][frees[1]]==1,'kernel independence')
    # Ten independent columns and two independent null vectors prove rank exactly ten.
    expected_basis=[norm_last([v[i]*scales[i]%7 for i in range(12)]) for v in p['kernel_basis']]
    check(basis==expected_basis,'independently recovered kernel differs')
    fs=[];all_masks=[]
    for u0,u1,r0,r1 in itertools.product(range(7),repeat=4):
        if r0==r1==0:continue
        z=mask_for(K,(u0,r0,1),(u1,r1,0));nu=constrained_nullity(basis,z)
        all_masks.append(z)
        fs.append({'u':[u0,u1],'r':[r0,r1],'zero_indices':[i for i in range(12) if z>>i&1],'nullity':nu})
    check(fs==p['complete_F49_directions'],'complete F49 zero-set/rank results differ')
    check(len(fs)==2352 and sum(x['nullity']>0 for x in fs)==2,'wrong admissible coefficients')
    # Enumerate every F49-valued pair of parameters of the full rank-two kernel.
    mask_lookup={z:[] for z in set(all_masks)}
    for x,z in zip(fs,all_masks):mask_lookup[z].append((x['u'],x['r']))
    compatible_nonzero=0;full_parameters=0;compatible_masks=set()
    for a0,a1,b0,b1 in itertools.product(range(7),repeat=4):
        full_parameters+=1
        if a0==a1==b0==b1==0:continue
        mask=0
        for i in range(12):
            if (a0*basis[0][i]+b0*basis[1][i])%7 or (a1*basis[0][i]+b1*basis[1][i])%7:mask|=1<<i
        if any(mask & ~z==0 for z in mask_lookup):compatible_nonzero+=1;compatible_masks.add(mask)
    check(full_parameters==2401 and compatible_nonzero==96 and len(compatible_masks)==2,'nonzero layer classification failed')
    check(compatible_masks=={sum(1<<i for i in x['support_indices']) for x in p['actual_candidate_patterns']},'supports differ')
    classified=[];directions=[(u,r,1) for u in range(7) for r in range(1,7)]
    for mask in range(1<<len(QS)):
        selected=[q for i,q in enumerate(QS) if mask>>i&1]
        selected_ideals=sum(1<<i for i,o in enumerate(own) if o['q'] in selected)
        bad=[]
        for a in directions:
            z=mask_for(K,a)&selected_ideals
            if constrained_nullity(basis,z):bad.append(list(a))
        classified.append({'mask':mask,'prime_support':selected,'criterion_passed':not bad,'surviving_alphas':bad})
    check(classified==p['classification'],'independent 1024 support classifications disagree')
    passed=sum(x['criterion_passed'] for x in classified)
    check(passed==912,'wrong pass count')
    ids=[i for i,o in enumerate(own) if o['q'] in (97,293)]
    pair=[[M[i][j] for j in ids] for i in (0,5)]
    check(pair==[[1,1],[6,3]] and determinant_dp(pair)%7==4,'two-place exclusion failed')
    # Independent rational cancellation, including the inert place 1373
    # that matters for the new depth-four exclusion.
    rational_checks=0
    for pattern,claimed in zip(p['actual_candidate_patterns'],p['rational_cancellation']):
        raw_vector=pattern['inertia_vector']
        canonical_vector=[raw_vector[i]*scales[i]%7 for i in range(12)]
        for row in claimed['values']:
            a=row['rational_element'];total=0
            for i,v in enumerate(canonical_vector):
                if not v:continue
                q=own[i]['q'];pr=own[i]['phi_root'];sr=None if pr is None else (2*pr-1)%q
                f=SqrtField(q,sr);check(a%q!=0,'nonunit probe')
                syms=[f.exp(f.phi_element(*ab),(f.size-1)//7) for ab in AB]
                z=next(x for x in syms if x!=(1,0))
                table={f.exp(z,j):j for j in range(7)}
                total+=v*table[f.exp(f.elt(a),(f.size-1)//7)]
            check(total%7==row['value_mod7']==0,'rational Frobenius cancellation failed')
            rational_checks+=1
    check(rational_checks==28,'rational probe coverage changed')
    for pattern in p['actual_candidate_patterns']:
        forced=pattern['support_indices'];possible=[]
        for i,rec in enumerate(own):
            if i in forced:possible.append(i);continue
            if sum(a*b for a,b in zip(K[i],pattern['alpha']))%7:continue
            if rec['phi_root'] is None and rec['h']<3:continue
            possible.append(i)
        check(possible==pattern['depth3_beta_possible_indices'],'conditional beta support mismatch')
        check(forced==pattern['depth3_beta_forced_indices'],'conditional forced support mismatch')
    # Small determinant cases exercise sign/zero handling independently.
    determinant_checks=0
    for a,b,c,d0 in itertools.product(range(-2,3),repeat=4):
        check(determinant_dp([[a,b],[c,d0]])==a*d0-b*c,'determinant benchmark failure')
        determinant_checks+=1
    result={'schema':'komorebi.beal.block57.independent.v1','status':'PASS',
      'primary_sha256':hashlib.sha256(primary_path.read_bytes()).hexdigest(),
      'arithmetic':'sqrt5-basis direct seventh-power symbols; subset determinant expansion and Cramer kernels',
      'imports_primary_arithmetic':False,'prime_ideal_fields':12,'independent_power_symbols':symbol_count,
      'root_order_checks':order_checks,'rational_unit_checks':rational_checks,'rank':10,'kernel_dimension':2,'Cramer_determinants':cramer_count,
      'determinant_small_benchmarks':determinant_checks,'F49_natural_directions':2352,
      'full_F49_kernel_parameter_pairs':full_parameters,'compatible_nonzero_kernel_vectors':compatible_nonzero,
      'compatible_inertia_supports':2,'rational_subsets_classified':1024,'pass_subsets':912,'survivor_subsets':112,
      'pair_minor':pair,'pair_determinant_mod7':4,'column_rescalings':scales,
      'canonical_residue_matrix':M,'independent_Cramer_kernel':basis,
      'nonclaims':['Finite evidence is not a universal support bound','No Frey realization or Beal proof',
                   'Independent implementation is not independent mathematical review']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','prime_ideal_fields','rank','F49_natural_directions','pass_subsets','pair_determinant_mod7')},sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--primary',required=True,type=Path);ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();main(a.primary,a.output)
