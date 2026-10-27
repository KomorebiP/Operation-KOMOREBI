#!/usr/bin/env python3
"""Bounded exact audit of Continuation 04.

Run from any working directory: python check_completion_v4.py
No third-party libraries. Scientific assertions never use floating point.
Large-index Bernoulli residues are independently checked against power sums.
A coefficientwise certificate plus the proved error bound covers an entire
2-adic ball, not just the sampled integer values.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, platform, sys, time
import dyadic_modular as d
import check_dyadic_tail as old
BASE=Path(__file__).resolve().parent


def b_power_sum(n:int,bits:int)->int:
    # From the power-sum expansion, the error in
    # 2^(1-h)*sum_{a<2^h}a^n - 2 B_n has valuation >=h-1.
    h=bits+1;mod=1<<(bits+h-1)
    z=sum(pow(a,n,mod) for a in range(1<<h))%mod
    assert z%(1<<(h-1))==0
    return z>>(h-1)


def original_normalized_tail(r:int,x:int,bits:int)->int:
    """Evaluate G_r via original unfactored kappa/binomial/source terms.

    Uses binomial complement 2*(x-q), not the factorial cancellation used by G.
    Intended for nonnegative modest x, but arbitrarily large integer r.
    """
    if x<0:raise ValueError('integer tail requires x>=0')
    mu,_=d.minimum(r);N=r+x
    b0=comb(2*N,2*x);loss=d.v2(b0);p=bits+loss;mod=1<<p
    value=0
    for q in range(min(x,max(0,(p+mu-1)//4))+1):
        cost=4*q-mu
        if cost>=p:continue
        m=r+q
        unit=(-(2*m-1)*d.twice_bernoulli_mod(2*m,p))%mod
        binomial=comb(2*N,2*(x-q))%mod
        source=old.source_mod(x-q,p)
        value=(value+(1<<cost)*unit*binomial*source)%mod
    assert value%(1<<loss)==0
    ur=(-(2*r-1)*d.twice_bernoulli_mod(2*r,bits))%(1<<bits)
    divisor=ur*(b0>>loss)%(1<<bits)
    return (value>>loss)*pow(divisor,-1,1<<bits)%(1<<bits)


def predicted_capped(atlas:list[dict],x:int,bits:int)->int:
    found=[l for l in atlas if x%(1<<l['k'])==l['s']]
    assert len(found)==1
    leaf=found[0]
    if leaf['kind']=='constant':return min(bits,leaf['value'])
    if leaf['kind']!='simple_root':raise AssertionError('unresolved leaf in a completed test')
    diff=(x-leaf['root_mod'])%(1<<leaf['root_bits'])
    vv=leaf['root_bits'] if diff==0 else int(d.v2(diff))
    return min(bits,leaf['offset']+vv)


def signature(atlas:list[dict])->list:
    return sorted((l['kind'],l['s'],l['k'],l.get('value',l.get('offset'))) for l in atlas)


def run()->dict:
    start=time.perf_counter();counts={}
    def count(key,n=1):counts[key]=counts.get(key,0)+n
    # Fresh coefficient construction, independent inverse convolution and Euler recurrence.
    maxn=128
    ks=old.inverse_coefficients(maxn)
    bs=old.bernoulli_even(maxn)
    es=old.euler_even(maxn)
    for m in range(1,maxn+1):
        assert ks[m]==-2**(4*m)*(2*m-1)*bs[m]
        for bits in (4,8,16,32,64):
            assert d.twice_bernoulli_mod(2*m,bits)==old.mod_fraction(2*bs[m],bits)
            count('Bernoulli_residue_vs_exact')
    # Independent large-index residues by finite power sums, with a proved h bound.
    large_indices=[2*((1<<(17+delta))-5+q) for delta in range(1,8) for q in (0,1,5,6)]
    large_indices += [2*((1<<90)-j) for j in (1,5,15,31)]
    for n in large_indices:
        for bits in (6,10):
            assert b_power_sum(n,bits)==d.twice_bernoulli_mod(n,bits)
            count('large_Bernoulli_vs_power_sum')
    # Two unrelated constructions of the source, including negative arguments.
    for bits in (8,24,64):
        poly=d.source_polynomial(bits)
        for x in range(-40,81):
            assert d.evaluate(poly,x,1<<bits)==old.source_mod(x,bits)
            count('source_series_vs_modular_power')
    # All exact rational tails through N=128, not merely the special walls.
    data={r:d.tail_polynomial(r,24) for r in range(1,maxn+1)}
    for N in range(maxn+1):
        terms=[ks[m]*comb(2*N,2*m)*old.source(N-m) for m in range(N+1)]
        assert sum(terms,F(0))==es[N]
        count('full_reconstruction')
        tail=F(0)
        for r in range(N,0,-1):
            tail+=terms[r]
            mu=data[r]['mu']
            normalized=tail/(ks[r]*comb(2*N,2*r))*(1<<(-mu))
            actual=old.mod_fraction(normalized,24)
            assert d.evaluate(data[r]['coefficients'],N-r,1<<24)==actual
            count('all_rational_tails')
    # The five-root family: complete coefficient certificates at all exceptional distances.
    stages=[]
    for delta in range(1,8):
        r=(1<<(17+delta))-5
        lo=d.tail_polynomial(r,12);hi=d.tail_polynomial(r,64)
        assert hi['mu']==-delta and hi['minima']==[5]
        # Precision compatibility of every coefficient, not just function values.
        assert d.trim([z%4096 for z in hi['coefficients']])==lo['coefficients']
        count('coefficient_precision_compatibility')
        atlas=d.root_atlas(hi)
        assert not any(z['kind'].startswith('unresolved') for z in atlas)
        expected=(0,0,2,3,3,5,5)[delta-1]
        assert sum(z['kind']=='simple_root' for z in atlas)==expected
        certificates=[]
        for leaf in atlas:
            c=leaf.get('content',leaf.get('value'))
            poly=d.affine(lo['coefficients'],leaf['s'],1<<leaf['k'],1<<(c+1))
            assert all(z%(1<<c)==0 for z in poly)
            red=d.trim([(z>>c)%2 for z in poly])
            assert red==leaf['reduction']
            assert red==[1] if leaf['kind']=='constant' else red in ([0,1],[1,1])
            certificates.append({'s':leaf['s'],'k':leaf['k'],'content':c,'reduction':red,'kind':leaf['kind']})
            count('whole_ball_coefficient_certificates')
        # A separate original-tail calculation, using a different formula and source path.
        samples=list(range(65))+[95,127,191,255]
        for x in samples:
            assert original_normalized_tail(r,x,40)==d.evaluate(hi['coefficients'],x,1<<40)
            count('five_wall_original_unfactored_tails')
        for x in range(4096):
            residue=d.evaluate(hi['coefficients'],x,1<<32)
            actual=32 if residue==0 else int(d.v2(residue))
            assert predicted_capped(atlas,x,32)==actual
            count('five_wall_atlas_value_checks')
        fac=d.weierstrass_mod(hi)
        assert fac['degree']==5
        alt=d.root_atlas({**hi,'coefficients':fac['W']})
        assert signature(atlas)==signature(alt)
        for u,v in zip(sorted(atlas,key=lambda z:(z['s'],z['k'])),sorted(alt,key=lambda z:(z['s'],z['k']))):
            if u['kind']=='simple_root':
                bits=min(u['root_bits'],v['root_bits'])
                assert (u['root_mod']-v['root_mod'])%(1<<bits)==0
        count('five_wall_Weierstrass_factorization')
        stages.append({'delta':delta,'L':17+delta,'r':r,'mu':hi['mu'],
                       'polynomial_mod_256':[z%256 for z in fac['W']],
                       'full_W_mod_2_64':fac['W'],
                       'certificates':certificates,'atlas':atlas,
                       'G_valuations_x_0_through_12':[int(d.v2(d.evaluate(hi['coefficients'],x,1<<64))) for x in range(13)]})
    # General separation theorem on larger, genuinely multiple-root geometries.
    separation=[]
    for j in range(1,33):
        D=j-1-(j-1).bit_count();K=(j-1).bit_length()
        threshold=max(1,D+K)
        for delta in sorted(set((max(1,threshold-1),threshold,threshold+1))):
            r=(1<<(d.wall_threshold(j)+delta))-j
            dat=d.tail_polynomial(r,max(48,threshold+12))
            atlas=d.root_atlas(dat)
            assert not any(z['kind'].startswith('unresolved') for z in atlas)
            roots=sum(z['kind']=='simple_root' for z in atlas)
            if delta>=threshold:assert roots==j
            separation.append({'j':j,'delta':delta,'bound':threshold,'r_bit_length':r.bit_length(),'roots':roots})
            count('general_separation_cases')
    # Exact, necessary-and-sufficient regular-wall emergence thresholds.
    # Each residue ball is certified coefficientwise, not by point samples.
    regular_wall_cases=[]
    for j in range(1,33):
        ej=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        if any(e<=0 for e in ej[1:]):continue
        scales=[]
        for i in range(j):
            di=j-1-i.bit_count()-(j-1-i).bit_count()
            ki=0 if j==1 else max(i,j-1-i).bit_length()
            scales.append((i,di,ki,di+ki))
        assert sum((F(1,1<<k) for i,di,k,ti in scales),F(0))==1
        maxt=max(ti for i,di,k,ti in scales)
        for delta in range(1,max(2,maxt+2)):
            r=(1<<(d.wall_threshold(j)+delta))-j
            p=max(24,maxt+5)
            dat=d.tail_polynomial(r,p)
            actual=d.root_atlas(dat)
            assert not any(z['kind'].startswith('unresolved') for z in actual)
            expected_roots=sum(delta>=ti for i,di,k,ti in scales)
            assert sum(z['kind']=='simple_root' for z in actual)==expected_roots
            for i,di,k,ti in scales:
                c=min(delta,ti)
                ap=d.affine(dat['coefficients'],i,1<<k,1<<(c+1))
                assert all(z%(1<<c)==0 for z in ap)
                red=d.trim([(z>>c)%2 for z in ap])
                expected=[1] if delta<ti else ([1,1] if delta==ti else [0,1])
                assert red==expected,(j,delta,i,red,expected)
                count('regular_wall_whole_ball_certificates')
            regular_wall_cases.append({'j':j,'delta':delta,'roots':expected_roots})
            count('regular_wall_families_at_distance')
    # The first irregular wall j=17. All lower distances are certified explicitly;
    # the general separation theorem covers every delta>=20.
    irregular=[]
    expected_counts=[1]*10+[2,2,4,8,8,12,14,15,15,17]
    for delta in range(1,21):
        j=17;r=(1<<(53+delta))-j
        dat=d.tail_polynomial(r,64);low=d.tail_polynomial(r,32)
        assert d.trim([z%(1<<32) for z in dat['coefficients']])==low['coefficients']
        atlas=d.root_atlas(dat)
        assert not any(z['kind'].startswith('unresolved') for z in atlas)
        assert sum(z['kind']=='simple_root' for z in atlas)==expected_counts[delta-1]
        assert sum((F(1,1<<z['k']) for z in atlas),F(0))==1
        certificates=[]
        for leaf in atlas:
            c=leaf.get('content',leaf.get('value'))
            ap=d.affine(low['coefficients'],leaf['s'],1<<leaf['k'],1<<(c+1))
            assert all(z%(1<<c)==0 for z in ap)
            red=d.trim([(z>>c)%2 for z in ap])
            assert red==leaf['reduction']
            assert red==[1] if leaf['kind']=='constant' else red in ([0,1],[1,1])
            certificates.append({'s':leaf['s'],'k':leaf['k'],'content':c,'reduction':red,'kind':leaf['kind']})
            count('irregular_wall_whole_ball_certificates')
        for x in range(33):
            assert original_normalized_tail(r,x,40)==d.evaluate(dat['coefficients'],x,1<<40)
            count('irregular_wall_original_unfactored_tails')
        irregular.append({'j':17,'delta':delta,'r':r,'mu':dat['mu'],
                           'atlas':atlas,'certificates':certificates})
        count('irregular_wall_distances')
    # Independently verify d_i+k_i bound by direct factorial and pair distances.
    for j in range(2,129):
        weights=[]
        for i in range(j):
            D=sum(int(d.v2(i-h)) for h in range(j) if h!=i)
            k=1+max(int(d.v2(i-h)) for h in range(j) if h!=i)
            expected=j-1-i.bit_count()-(j-1-i).bit_count()
            assert D==expected
            weights.append(D+k)
            count('skeleton_local_scale_checks')
        assert max(weights)==j-1-(j-1).bit_count()+(j-1).bit_length()
        count('uniform_scale_checks')
    # Arbitrary, not only post-wall, depths: constructive finite polynomial preparation.
    extra_rs=list(range(1,65))+[127,254,255,510,511,2045,4093,4095,(1<<68)-17,(1<<100)-31,
        int('1010111110111111111011111111111111',2)]
    preparations=[]
    for r in extra_rs:
        dat=d.tail_polynomial(r,32);fac=d.weierstrass_mod(dat)
        assert fac['degree']==max(dat['minima'])
        assert fac['degree'] <= (r.bit_count()-1)//3
        mod=1<<32
        for x in range(-16,49):
            a=d.evaluate(dat['coefficients'],x,mod);w=d.evaluate(fac['W'],x,mod)
            assert (32 if not a else d.v2(a))==(32 if not w else d.v2(w))
            count('Weierstrass_valuation_checks')
        preparations.append({'r':r,'mu':dat['mu'],'degree':fac['degree'],'bound':(r.bit_count()-1)//3})
        count('arbitrary_depth_preparations')
    return {'status':'PASS','counts':counts,'five_root_stages':stages,
            'separation_cases':separation,'regular_wall_cases':regular_wall_cases,
            'first_irregular_wall':irregular,'preparations':preparations,
            'runtime_seconds':time.perf_counter()-start,
            'non_claims':['No Lean run.','No historical priority assessment.',
                'An unresolved precision leaf is not evidence for a root or for no roots.',
                'No uniform simple-root theorem for arbitrary r is asserted.',
                'Finite coefficient certificates use the explicit rigorous truncation bound; point sampling alone is not a proof.']}


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=='__main__':
    started=datetime.now(timezone.utc).isoformat();ret=run()
    out=BASE/'RESULTS_COMPLETION_04.json';out.write_text(json.dumps(ret,indent=2)+'\n')
    manifest={
      'schema_version':1,'claim_id':'DYADIC-TAIL-CONTINUATION-04',
      'repository':{'commit':'not a git checkout; v3 archive preserved as input checkpoint','dirty':True},
      'command':f'{sys.executable} {Path(__file__).name}',
      'environment':{'software':[sys.version,platform.platform()],
                     'hardware':f'{platform.machine()}, {os.cpu_count()} logical CPUs visible; single-process arithmetic'},
      'mathematics':{'assertion_tested':'Coefficient-certified five-root wall classification, finite polynomial preparation, and bounded independent arithmetic comparisons.',
        'coefficient_domain':'Exact rational arithmetic and integer residues modulo powers of two.',
        'conventions':'B_1=-1/2; signed E_(2N); r=M+1; v2(0)=infinity; finite precision zeros are only lower bounds.',
        'inputs':[{'path':p.name,'sha256':sha(p)} for p in [BASE/'dyadic_modular.py',Path(__file__),BASE/'check_dyadic_tail.py']],
        'bounds':{'exact_half_index':128,'five_wall_deltas':list(range(1,8)),
                  'five_wall_certificate_modulus_bits':12,'irregular_wall_certificate_modulus_bits':32,
                  'root_and_preparation_bits':64,'first_irregular_wall_deltas':list(range(1,21)),
                  'large_unfactored_tail_bits':40,'general_separation_j_max':32,
                  'hardware_resource_caps':'single process; no background work; no internal timeout modifies range'},
        'non_claims':ret['non_claims']},
      'randomness':{'used':False,'generator':'none; deterministic inputs','seed':None},
      'run':{'started_at':started,'runtime_seconds':ret['runtime_seconds'],'exit_status':0},
      'outputs':[{'path':out.name,'sha256':sha(out)}],
      'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in ret['counts'].items()],
      'result':'Implementation and finite assertions verified in the stated ranges; universal theorems are separately proved in COMPLETION_04.md.',
      'residual_risks':['Not Lean-checked.','Version-1 manifest records hashes but not a bounded-runner trace.','Historical v1-v3 logs are preserved, not all rerun here.']}
    (BASE/'MANIFEST_COMPLETION_04.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':ret['status'],'counts':ret['counts'],'runtime_seconds':ret['runtime_seconds']},indent=2))
