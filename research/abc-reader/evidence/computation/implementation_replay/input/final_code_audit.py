from __future__ import annotations
import importlib.util
import json
import math
import sys
from pathlib import Path
import sympy as sp

ART=Path('/mnt/data/final_audit_artifacts')
sys.path.insert(0,str(ART))

def load(name:str):
    path=ART/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

results={}

moving=load('abc_moving_interval_search_arbitrary_precision')
for label,(a,b) in {
    'worked':(3,125),
    'unit':(1,4374),
    'overflow':(24833,5020969537415167),
}.items():
    r=moving.MovingEscapeSearch(a,b).search()
    assert type(r.c) is int and type(r.phi) is int and type(r.best_k) is int
    assert r.master_gap >= 1.0-1e-14
    assert r.phase_integrality_factor >= 1.0-1e-14
    results[f'moving_{label}']={
        'c':str(r.c),'phi':str(r.phi),'best_k':r.best_k,
        'master_gap_exact':r.master_gap_exact,
        'endpoint':r.endpoint_template,
    }

witt=load('abc_witt_kummer_fermat')
cd=witt.contact_data(128)
assert cd.powerful_part==64 and cd.global_kernel==1 and cd.global_image==64
assert witt.kummer_kernel_bruteforce(128)==1
for M in range(2,11): assert witt.character_orthogonality(M)<1e-10
for ell in (2,3,5):
    for steps in (1,2,5): assert abs(witt.hecke_moments(ell,steps)['mean']-1)<1e-12
a,b=sp.symbols('a b')
f2,s2=witt.witt_carry_polynomials(2)
f3,s3=witt.witt_carry_polynomials(3)
assert sp.expand(f2+a*b)==0
assert sp.expand(s2+a*b*(a+b)**2)==0
assert sp.expand(f3+a*b*(a+b))==0
assert sp.expand(s3+a*b*(a+b)*(a*a+a*b+b*b)**3)==0
results['witt_kummer']={'contact_128':cd.powerful_part,'kernel_128':cd.global_kernel,'orthogonality_cases':9}

poly=load('abc_polylog_transducer')
import mpmath as mp
mp.mp.dps=80
for weight in (1,2,3):
    lhs,rhs,res=poly.polylog_distribution(weight,7,mp.mpc('0.71'))
    assert res < mp.mpf('1e-60')
for z in (mp.mpf('0.1'),mp.mpf('0.3'),mp.mpf('0.7'),mp.mpf('0.9')):
    assert abs(poly.rogers_residual(z))<mp.mpf('1e-60')
    assert abs(poly.trilog_closure_residual(z))<mp.mpf('1e-55')
assert poly.distribution_determinant(3,64)==64**3
results['polylog']={'distribution_cases':3,'functional_cases':8,'depth3_det':str(64**3)}

filtered=load('abc_filtered_contact_complex')
assert filtered.contact_order(128)==64
assert filtered.associated_graded_rank(128)==6
assert filtered.split_forced_kernel(128)==32
tr=filtered.cyclic_transfer(64,4)
assert (tr.kernel_order,tr.image_order,tr.cokernel_order)==(16,4,1)
for p in (2,3,5):
    for j in range(2,7): assert filtered.extension_is_nonsplit(p,j)
results['filtered_contact']={'source':64,'target':4,'kernel':16,'image':4}

ray=load('abc_integral_hecke_transfer')
for n in (1,8,9,72,128,625,6561,5020969537440000): assert ray.verify_ray_identity(n)
for p,e in ((2,7),(3,5),(5,4),(13,4)):
    assert sum(ray.exact_character_conductor_counts(p,e).values())==p**(e-1)
    assert ray.local_twist_conductor_sum(p,e)==ray.local_twist_closed_form(p,e)
B=ray.synthetic_congruence_order(8,packets=3)
for target in range(B.rows):
    eta,_=ray.projector_denominator(B,target)
    assert eta==ray.congruence_module_order(B,target)
results['integral_hecke']={'ray_cases':8,'character_cases':4,'synthetic_rank':B.rows}

cot=load('abc_hecke_cotangent')
inv=cot.toy_hecke_order_invariants([4,8,16,3,9])
assert inv['congruence_exponent']==144 and inv['cotangent_order']==13824 and inv['wiles_defect_factor']==96
mono=cot.monogenic_filter_invariants([0,2,5,9],target=0)
assert mono['projector_denominator']==90 and mono['cotangent_order']==90 and mono['wiles_defect_factor']==1
assert cot.persistence_profile(128).order==64
assert cot.cyclic_kernel_lower_bound(128)==32
results['hecke_cotangent']={'toy':inv,'monogenic':mono}

coh=load('abc_adelic_coherence_lattice')
rec=coh.analyze_triple(3,125,128,'audit')
assert (rec.dyadic_sign_factor,rec.kummer_factor,rec.wieferich_factor,rec.coherence_factor)==(2,1,1,32)
mod,row=coh.crt_coherence_row(rec)
assert int(mod)==32 and tuple(int(x) for x in row)==(29,31)
assert sum(x*y for x,y in zip(row,rec.primitive_exponents,strict=True))%mod==0
for vector,modulus in [((1,2),31),((2,-3,5),64),((1,0,0,7),125)]:
    g=coh.arbitrary_index_annihilator(vector,modulus)
    assert math.gcd(modulus,*map(abs,g))==1
    assert sum(x*y for x,y in zip(g,vector,strict=True))%modulus==0
results['coherence']={'factorization':[rec.dyadic_sign_factor,rec.kummer_factor,rec.wieferich_factor,rec.coherence_factor],'row':list(row),'modulus':mod}

out=Path('/mnt/data/final_verification_work/final_code_audit_results.json')
out.write_text(json.dumps({'passed':True,'results':results},indent=2,default=str)+'\n')
print(json.dumps({'passed':True,'groups':len(results),'results':results},indent=2,default=str))
