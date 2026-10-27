#!/usr/bin/env python3
"""v6 exact audits: terminal-carry theorem and odd-multiplier parameter atlases."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from fractions import Fraction as F
from math import comb
import dyadic_modular as d
from terminal_carry_v6 import (terminal_descriptor,separating_scales,regular_root_count,
    wall_template,parameter_certificate,validate_paired_atlas,paired_atlas)
from certificates_v5 import validate_atlas
from check_completion_v4 import original_normalized_tail


def run_combinatorial():
    start=time.perf_counter();counts={};examples=[]
    def count(k,n=1):counts[k]=counts.get(k,0)+n
    for r in range(1,262145):
        a=terminal_descriptor(r)
        # Independent wider finite scan, via exact successive-weight identity.
        qmax=(r.bit_count()-1)//3+16
        weights=[0]
        for q in range(1,qmax+1):weights.append(weights[-1]+4-int(d.v2(r+q)))
        mu=min(weights);J=[q for q,w in enumerate(weights) if w==mu]
        assert (a['mu'],a['minima'])==(mu,J)
        for q in J:
            if q:assert (r+q)%16==0
        count('consecutive_depth_terminal_checks')
    # Enter large and competing-carry regimes, not just more small rows.
    for L in (8,16,32,64,128,256,512):
        for j in range(1,65):
            for b in (1,3,5,(1<<127)+1,(1<<127)-1):
                r=b*(1<<L)-j
                if r<1:continue
                a=terminal_descriptor(r)
                limit=(r.bit_count()-1)//3+1
                naive=[3*q+(r+q).bit_count()-r.bit_count() for q in range(limit)]
                assert a['mu']==min(naive)
                if a['j']:
                    assert r==a['odd_multiplier']*(1<<a['L'])-a['j']
                    assert a['odd_multiplier']%2
                count('large_adversarial_terminal_checks')
    # The local carry at q=1 must not replace the globally terminal one.
    r=(1<<64)-17;a=terminal_descriptor(r)
    assert d.v2(r+1)==4 and a['j']==17 and a['L']==64
    assert d.lam(r,1)==0 and d.lam(r,17)==-11
    examples.append(a);count('remote_carry_override_cases')
    irregular=[]
    for j in range(1,65):
        e=[3*q+(j-1).bit_count()-(j-q-1).bit_count() for q in range(j)]
        if any(z<=0 for z in e[1:]):irregular.append(j)
        count('terminal_labels_classified')
    assert irregular==[17,33,49]
    assert (195-1)//3==64
    # Branch-content cutoff checked by polynomial coefficients, not point values.
    P=96;mod=1<<P;p=[1]
    for q in range(65):
        if q:
            i=q-1;p=d.mul(d.mul(p,[-i,1],mod),[-(2*i+1),2],mod)
        for e in (0,1):
            f=d.affine(p,e,2,mod)
            v=int(min(d.v2(z) for z in f if z))
            expected=sum(i%2==e for i in range(q))
            assert v==expected and v>=q//2
            count('parity_cutoff_coefficient_checks')
    # Synthetic repeated root remains explicitly unresolved.
    at=paired_atlas([0,0,1],[0],24,max_depth=8)
    assert any(a['kind'].startswith('unresolved') for a in at)
    count('repeated_root_guard')
    return {'status':'PASS','mode':'combinatorial','counts':counts,
        'irregular_labels_through_64':irregular,'examples':examples,
        'runtime_seconds':time.perf_counter()-start,
        'non_claims':['Finite tests do not replace the terminal-carry proof.',
                      'No universal algebraic-closure squarefreeness theorem.']}


def run_regular():
    start=time.perf_counter();counts={};records=[]
    def count(k,n=1):counts[k]=counts.get(k,0)+n
    labels=list(range(1,17))+[24,32,48,64]
    for j in labels:
        scales=separating_scales(j);tmax=max(a['threshold'] for a in scales)
        deltas=sorted({0,1,max(1,tmax-1),max(1,tmax),max(1,tmax+1)})
        for delta in deltas:
            L=d.wall_threshold(j)+delta
            for b in (3,5,(1<<81)+1):
                r=b*(1<<L)-j;desc=terminal_descriptor(r)
                assert desc['j']==j and desc['regular']
                P=max(32,tmax+12);dat=d.tail_polynomial(r,P);mod=1<<P
                roots=0
                for a in scales:
                    poly=d.affine(dat['coefficients'],a['s'],1<<a['k'],mod)
                    content=min(delta,a['threshold'])
                    assert all(z%(1<<content)==0 for z in poly)
                    red=d.trim([(z>>content)&1 for z in poly])
                    if delta<a['threshold']:assert red==[1]
                    else:
                        assert red==([1,1] if delta==a['threshold'] else [0,1])
                        roots+=1
                    count('generalized_regular_whole_ball_certificates')
                assert roots==regular_root_count(desc)
                # Independent point path: original unfactored finite rational sum.
                if j in (1,3,5,16,32,64) and b==3:
                    for x in (0,1,2,5,9):
                        Q=min(P,48)
                        assert d.evaluate(dat['coefficients'],x,1<<Q)==original_normalized_tail(r,x,Q)
                        count('regular_original_tail_comparisons')
                records.append({'r':r,'j':j,'L':L,'b':b,'delta':delta,'mu':desc['mu'],
                                'precision':P,'root_count':roots})
                count('generalized_regular_members')
    return {'status':'PASS','mode':'regular','counts':counts,'members':records,
            'runtime_seconds':time.perf_counter()-start,
            'non_claims':['No finite count proves a universal theorem; the proof is in the note.']}


def expected_roots(j,delta,b):
    if delta==0:return 1
    if j==17:
        if delta<=10:return 1
        if delta==11:return 2 if b%64 in (1,41) else 0
        if delta==12:return 2
        if delta==13:return 4
        if delta<=15:return 8
        if delta==16:return 12
        if delta==17:return 14
        if delta<=19:return 15
        return 17
    if j==33:
        if delta<=26:return 1
        if delta==27:return 0
        return {28:2,29:4,30:8,31:24,32:28,33:30,34:31,35:31}.get(delta,33)
    if j==49:
        if delta<=42:return 1
        return {43:4,44:6,45:12,46:16,47:28,48:30,49:39,50:43,51:45}.get(delta,49)
    raise ValueError(j)


def run_irregular(j):
    if j not in (17,33,49):raise ValueError('Supported audited labels 17,33,49')
    start=time.perf_counter();counts={};records=[];examples=[]
    def count(k,n=1):counts[k]=counts.get(k,0)+n
    stop=max(a['threshold'] for a in separating_scales(j));P=40 if j==17 else 64
    for delta in range(stop+1):
        L=d.wall_threshold(j)+delta;tmp=wall_template(j,L,P)
        pending=[(1,1)];certs=[]
        while pending:
            b,k=pending.pop();a=parameter_certificate(tmp,b,k,max_depth=16)
            if a['complete']:certs.append(a)
            else:
                assert k<8,('unresolved_parameter_ball',j,delta,b,k)
                pending.extend([(b,k+1),(b+(1<<k),k+1)])
        assert sum((F(1,1<<a['parameter_exponent']) for a in certs),F())==F(1,2)
        for ai,a in enumerate(certs):
            for old in certs[:ai]:
                assert (a['parameter_residue']-old['parameter_residue'])%(1<<min(a['parameter_exponent'],old['parameter_exponent']))!=0
            # Test the logical root-count condition on every relevant residue;
            # whole-parameter coverage follows from the paired coefficients.
            for b in range(1,64,2):
                if b%(1<<a['parameter_exponent'])==a['parameter_residue']:
                    assert a['root_count']==expected_roots(j,delta,b)
                    count('parameter_residue_classification_checks')
            count('uniform_parameter_balls')
            count('uniform_parameter_x_leaf_certificates',len(a['atlas']))
        # Independent true G for b!=1, compare whole parity polynomials.
        representatives=[3,41]
        if delta in (0,11,stop):representatives.append((1<<80)+1)
        for b in representatives:
            r=b*(1<<L)-j;desc=terminal_descriptor(r)
            assert desc['j']==j and desc['L']==L and desc['mu']==tmp['mu']
            dat=d.tail_polynomial(r,P);mod=1<<P
            f=d.add([b*z%mod for z in tmp['low']],tmp['high'],mod)
            for e in (0,1):
                lhs=d.affine([(b*z)%mod for z in dat['coefficients']],e,2,mod)
                rhs=d.affine(f,e,2,mod)
                assert lhs==rhs
                count('template_vs_original_series_parity_coefficients')
            aa=d.root_atlas(dat);validate_atlas(dat,aa)
            assert sum(a['kind']=='simple_root' for a in aa)==expected_roots(j,delta,b)
            count('independent_multiplier_atlases')
            if b==3 and delta in (0,1,11,stop-1,stop):
                for x in (0,1,2,3,5,8,11,17,27,59):
                    Q=min(P,48)
                    assert d.evaluate(dat['coefficients'],x,1<<Q)==original_normalized_tail(r,x,Q)
                    count('irregular_original_unfactored_tail_comparisons')
            if j==17 and delta==11 and b==3:examples.append({'b':b,'r':r,'atlas':aa})
        records.append({'j':j,'L':L,'delta':delta,'precision':P,'template':tmp,'parameter_certificates':certs})
        count('complete_distances')
    # A quadratic preparation displays the exact difference between b=1 and b=3.
    if j==17:
        quadratic=[]
        for b in (1,3,41):
            r=b*(1<<64)-17;dat=d.tail_polynomial(r,48)
            poly=d.affine(dat['coefficients'],3,8,1<<48);c=int(min(d.v2(z) for z in poly if z))
            assert c==14
            sub={'r':r,'precision':48-c,'coefficients':[z>>c for z in poly]}
            fac=d.weierstrass_mod(sub);assert fac['degree']==2
            w=fac['W'];bits=sub['precision'];disc=(w[1]**2-4*w[0])%(1<<bits)
            assert disc!=0;val=int(d.v2(disc));unit=(disc>>val)%8
            assert (val%2==0 and unit==1)==(b in (1,41))
            quadratic.append({'b':b,'r':r,'local_address':'x=3+8y','content':c,'precision':bits,
                'W_mod512':[z%512 for z in w],'discriminant_valuation':val,'discriminant_unit_mod8':unit})
            count('quadratic_original_factorization_checks')
        examples.append({'quadratic_preparations':quadratic})
    return {'status':'PASS','mode':'irregular','j':j,'delta_interval':[0,stop],
            'counts':counts,'distances':records,'examples':examples,
            'runtime_seconds':time.perf_counter()-start,
            'non_claims':['The uniform parameter statement requires the actual terminal label j.',
                'No analytic interpolation in the multiplier is asserted.',
                'No claim about repeated roots outside Z_2 or at all unclassified labels.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['combinatorial','regular','irregular'],required=True)
    parser.add_argument('--j',type=int);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    result=run_combinatorial() if a.mode=='combinatorial' else run_regular() if a.mode=='regular' else run_irregular(a.j)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','mode','counts','runtime_seconds')},indent=2))
