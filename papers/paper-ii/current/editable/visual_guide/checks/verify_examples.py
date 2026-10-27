#!/usr/bin/env python3
"""Exact executable checks for the new illustrations, not new Lean proofs."""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import models as m
checks=[]

def check(name:str, value, scope:str)->None:
    ok=bool(value)
    checks.append({'name':name,'passed':ok,'scope':scope})
    if not ok: raise AssertionError(name)

# Concrete nested masks and the full-dimensional coordinate changes.
for n,q in [(16,2),(16,4),(16,8),(12,3),(7,4),(0,3)]:
    ps=[m.residue_projector(n,q,r) for r in range(q)]
    check(f'projector_algebra_n{n}_q{q}',sum(ps,sp.zeros(n))==sp.eye(n) and
          all(ps[i]*ps[j]==(ps[j] if i==j else sp.zeros(n)) for i in range(q) for j in range(q)),
          'Exact integer matrices, including an empty carrier and uneven packet lengths.')
for small,large in [(2,4),(4,8),(2,8),(3,12)]:
    check(f'nested_masks_{small}_{large}',all(m.residue_projector(24,small,r)==sum(
          (m.residue_projector(24,large,s) for s in range(large) if s%small==r),sp.zeros(24)) for r in range(small)),
          '24 displayed coefficient positions; the general rule is the modular-address proof in the text.')
a=m.refinement_model()
check('coordinate_inverse',a['J'].T*a['J']==sp.eye(8),'Two permutation-coordinate systems on the same Q^8.')
check('coordinate_cocycle',(a['P8']*a['P4'].T)*a['J']==a['P8']*a['P2'].T,'Exact three-level permutation cocycle.')
check('operator_naturality',a['J']*a['T2']==a['T4']*a['J'],'Concrete 8 by 8 cyclic-filter matrix.')
check('operator_reconstruction',a['P2'].T*a['T2']*a['P2']==a['T'],'No averaging or scalar packet summaries.')
check('block_refinement',all(m.residue_projector(8,2,b)*a['T']*m.residue_projector(8,2,c)==sum(
      (m.residue_projector(8,4,j)*a['T']*m.residue_projector(8,4,i) for j in range(4) for i in range(4)
       if j%2==b and i%2==c),sp.zeros(8)) for b,c in product(range(2),repeat=2)),
      'All four coarse blocks expanded into embedded fine blocks.')
inc=sp.Matrix([[1,0,1,0],[0,1,0,1]])
check('scalar_aggregation_loses_information',inc.rank()==2 and inc*sp.Matrix([1,0,-1,0])==sp.zeros(2,1),
      'Counterexample for numerical packet summaries, not exact range-restricted packet coordinates.')
check('fourier_F7_table',m.fourier_table_mod7()==[[int(i==j) for j in range(3)] for i in range(3)],
      'All nine finite orthogonality entries, N=3 in F_7.')
check('fourier_periodic_extension',all(5*sum(pow(4,j*k,7)*pow(2,n*k,7) for k in range(3))%7==int(n%3==j)
      for j in range(3) for n in range(48)),'All 144 coefficient comparisons on n=0..47.')
check('coefficient_parity_F2',[int(n%2==1) for n in range(8)]!=[0]*8 and pow(2,1,2)==0,
      'A coefficient mask survives where averaging by 2 cannot be formed.')
check('order_two_not_fourier_over_product_ring',((2*2)%3,(2*2)%3)==(1,1) and
      ((2*(1+2))%3,(2*(1+1))%3)==(0,1),'omega=(-1,1), eta=(2,2) in F_3 x F_3; off-diagonal table entry is not zero.')
grid=m.crt_grid()
check('CRT12_bijection',sorted(x for row in grid for x in row)==list(range(12)) and grid[1][3]==7,
      'All 12 residue labels in the 4 by 3 grid.')
check('CRT_selector_products',all(m.residue_projector(36,12,n)==m.residue_projector(36,4,n%4)*m.residue_projector(36,3,n%3)
      for n in range(12)),'All 12 masks on 36 displayed addresses.')
check('noncoprime_compatibility_boundary',not any(n%4==0 and n%6==1 for n in range(12)),
      'Concrete incompatible residues: coprimality is not dispensable.')

w=m.weighted_model()
check('weighted_A_square',w['A']**2==8*sp.eye(2),'Integral matrices a=2E01 and b=4E10.')
check('noncommuting_letters',w['a']*w['b']==8*sp.diag(1,0) and w['b']*w['a']==8*sp.diag(0,1),
      'Written products ab and ba have different source/target packets.')
check('normalization_order',w['T']==sp.Matrix([[5,3],[4,1]]) and w['Dinv']*w['D']==sp.eye(2),
      'T=D(I+A), with a supplied two-sided inverse of D.')
for L in range(1,9):
    total,inv=m.pruned_inverse(L)
    check(f'pruned_two_sided_inverse_depth{L}',m.matrix_mod(w['T']*inv,2**L)==sp.eye(2) and
          m.matrix_mod(inv*w['T'],2**L)==sp.eye(2),f'Exact arithmetic modulo 2^{L}.')
    geometric=sum(((-w['A'])**n for n in range(L)),sp.zeros(2))
    check(f'pruning_equals_geometric_depth{L}',m.matrix_mod(total-geometric,2**L)==sp.zeros(2),
          'All positive-weight words below the displayed precision cutoff.')
s,inv=m.pruned_inverse(5)
check('displayed_inverse_mod32',s==sp.Matrix([[9,-18],[-4,9]]) and m.matrix_mod(inv,32)==sp.Matrix([[9,5],[28,13]]),
      'All six nonzero retained operator words summed with their signs.')
check('wrong_inverse_order_rejected',m.matrix_mod(w['T']*(w['Dinv']*s),32)!=sp.eye(2),
      'Counterexample: D^{-1}S is generally not SD^{-1}.')
check('short_cutoff_residual',m.matrix_mod((sp.eye(2)+w['A'])*(sp.eye(2)-w['A'])-sp.eye(2),32)==24*sp.eye(2),
      'Length cutoff 2 leaves -8 I; it is insufficient modulo 32.')
check('ceiling_cutoffs',all(L<=b*((L+b-1)//b) for L in range(1,25) for b in range(1,9)),
      '192 finite cutoff instances; general inequality is separately explained.')

z=m.zeta_model(); counts=m.walk_counts(24)
check('canonical_zeta_polynomials',z['Q']==1-z['t']-2*z['t']**3 and z['adjugate'][0,1]==2*z['t']**2,
      'Exact determinant and adjugate, not a supplied denominator.')
series=sp.series(z['Z01'],z['t'],0,25).removeO().expand()
check('walk_recurrence_vs_rational',all(int(series.coeff(z['t'],n))==counts[n] for n in range(25)),
      'Independent first-edge dynamic program compared with the rational expansion through weight 24.')
for n in range(11):
    check(f'walk_enumeration_weight{n}',len(m.enumerate_walks(n))==counts[n],
          'Literal directed-edge traversal; parallel edges a and b are kept distinct.')
check('displayed_weight5_walks',set(m.enumerate_walks(5))=={'llla','lllb','ara','arb','bra','brb'},
      'Six walks: two loop prefixes and four choices through a return cycle.')
check('zeta_linear_recurrence',all(counts[n]==counts[n-1]+2*counts[n-3] for n in range(3,25)),
      'After numerator degree 2; q_0=1.')
zero_words=[('ell',)*k for k in range(101)]
check('zero_weight_loop_counterexample',len(set(zero_words))==101 and all(sum(0 for _ in word)==0 for word in zero_words),
      'Words ell^k for k=0..100 are distinct at weight zero; the text gives the all-k argument, not a universal finite test.')

s=m.sign_model();x=sp.Symbol('x')
check('sign_involution',s['A']**2==sp.eye(2),'Actual integral involution.')
check('sign_numerator_quasi_idempotence',s['N']**2==2*s['N'],'N=I+A, prior to division.')
check('evaluated_Bezout',-(s['A']-sp.eye(2))+(s['A']+sp.eye(2))==2*sp.eye(2) and
      (s['A']-sp.eye(2))*(s['A']+sp.eye(2))==sp.zeros(2),'r=2 certificate with U=-I,V=I.')
check('sign_projector_algebra',s['Eplus']**2==s['Eplus'] and s['Eminus']**2==s['Eminus'] and
      s['Eplus']*s['Eminus']==sp.zeros(2) and s['Eplus']+s['Eminus']==sp.eye(2),'Exact rational matrices.')
check('sign_kernel_action',s['Eplus']*sp.Matrix([1,0])==sp.Matrix([1,0]) and
      s['Eplus']*sp.Matrix([-1,2])==sp.zeros(2,1),'Two rational eigenspaces.')
check('sign_resultant',sp.resultant(x-1,x+1,x)==2,'Concrete polynomial resultant computed symbolically.')
check('lattice_index',s['B'].det()==2 and s['A']*s['B']==s['B']*sp.diag(1,-1),
      'Integral eigenvectors span an index-two sublattice of Z^2.')
for p in (2,3,5,7,11):
    check(f'local_denominator_weight_p{p}',m.padic_weight(s['Eplus'],p)==int(p==2) and
          m.padic_weight(s['Eminus'],p)==int(p==2),'Reduced rational denominators; prime-local, not global integer integrality.')
check('inflated_certificate_not_minimal',2*s['N']/4==s['Eplus'] and m.padic_weight(s['Eplus'],2)==1,
      'r=4 also clears the certificate, but its exponent two is not the minimal projector weight.')
for depth in (1,2,3,4,5):
    check(f'precision_delay_sharp_m{depth}',s['Eplus']*sp.Matrix([0,2**depth])==sp.Matrix([2**(depth-1),0]) and
          s['Eplus']*sp.Matrix([0,2**(depth+1)])==sp.Matrix([2**depth,0]),
          'Counterexample to zero delay and exact sufficiency of one additional dyadic input digit.')

for p,L,weights in [(2,0,(1,2)),(2,1,(1,2)),(2,2,(1,2)),(2,3,(1,2)),(2,4,(1,2)),(3,2,(0,1)),(4,2,(1,2))]:
    f=m.smith_fibres(p,L,weights);mod=p**L
    check(f'Smith_all_fibres_p{p}_L{L}_s{weights}',all(f.get(rhs,0)==m.smith_count_formula(p,L,weights,rhs)
          for rhs in product(range(mod),repeat=len(weights))),
          f'Complete domain and target enumeration, modulus {mod}; composite p=4 included where present.')
st=m.smith_transport_model()
check('Smith_actual_diagonalization',st['D']==sp.diag(2,4) and st['V'].det()==1,
      'Explicit unimodular V supplied and multiplied, not a general Smith algorithm.')
yfib=[sp.Matrix(y) for y in product(range(8),repeat=2) if m.matrix_mod(st['D']*sp.Matrix(y),8)==st['rhs']]
xset={tuple(m.matrix_mod(st['V']*y,8)) for y in yfib}
actual={tuple(x) for x in product(range(8),repeat=2) if m.matrix_mod(st['M']*sp.Matrix(x),8)==st['rhs']}
check('Smith_transport_fibre',xset==actual and len(actual)==8,'All 64 original-coordinate inputs compared with all diagonal-coordinate inputs.')
check('Smith_unit_zero_boundary',m.smith_count_formula(2,3,(0,3),(5,0))==8 and
      m.smith_count_formula(2,3,(0,3),(5,4))==0,'A literal zero factor has a full 8-element fibre only at target zero.')
check('Smith_printed_three_coordinate_example',m.smith_count_formula(2,6,(0,1,3),(1,2,8))==16 and
      m.smith_count_formula(2,6,(0,1,3),(1,2,4))==0,'Manuscript example evaluated from exact diagonal formula; not brute force over 64^3 inputs.')
check('Smith_cardinality_conservation',all(sum(m.smith_fibres(2,L,(1,2)).values())==2**(2*L) for L in range(1,5)),
      'Partition of the entire finite input set into its fibres.')
sg=m.signal_model();w=sg['w']
check('finite_FIR_convolution',sg['y']==[1,4,8,12,16,20,17,6],'Zero-extended finitely supported signal, not periodic wraparound.')
check('polyphase_convolution',all(sg['out'][j]==sum(v*w**i for i,v in enumerate(sg['y'][j::2])) for j in range(2)),
      'Actual delay polynomial matrix H(w), including the cross-phase delay.')
check('signal_reinterleaving',[v for i in range(4) for v in (sg['y'][::2][i],sg['y'][1::2][i])]==sg['y'],
      'Exact even/odd synthesis after filtering.')
pts=m.smith_chart_points()
check('reflection_orbit_radius',all(sp.simplify(p['gamma']*sp.conjugate(p['gamma']))==sp.Rational(1,4) for p in pts),
      'Eight algebraic points, with no floating-point complex comparison.')
check('reflection_impedance_roundtrip',all(sp.simplify((p['z']-1)/(p['z']+1)-p['gamma'])==0 for p in pts),
      'All denominators nonzero on radius 1/2.')
check('half_turn_is_reciprocal',all(sp.simplify(pts[(k+4)%8]['z']*pts[k]['z'])==1 for k in range(8)),
      'Eight exact half-turn identities; the general two-phase identity remains the source theorem.')
check('quarter_turn_labels',pts[0]['z']==3 and pts[4]['z']==sp.Rational(1,3) and pts[2]['z']==(3+4*sp.I)/5,
      'Displayed chart labels are exact.')

f=m.defect_model()
check('one_step_defect',f['Delta']==sp.Matrix([[0,sp.Rational(1,16)],[0,0]]),'Actual independently selected coarse/fine operators.')
for n in range(1,9):
    defect=f['C']*f['Tf']**n-f['Tc']**n*f['C']
    telescoped=sum((f['Tc']**(n-1-k)*f['Delta']*f['Tf']**k for k in range(n)),sp.zeros(2))
    check(f'power_defect_n{n}',defect==telescoped and defect[0,1]==(2**n-1)*f['epsilon'] and
          m.infinity_norm(defect)<=n*2**(n-1)*f['epsilon'],
          'Exact infinity-norm comparison with rho=2; the growth bound is not uniform in n.')
for z in [sp.Rational(-1),sp.Rational(0),sp.Rational(3),sp.Rational(21,10),sp.Rational(201,100)]:
    rf=(z*sp.eye(2)-f['Tf']).inv();rc=(z*sp.eye(2)-f['Tc']).inv()
    err=f['C']*rf-rc*f['C']
    check(f'resolvent_z{z}',err==rc*f['Delta']*rf and err[0,1]==f['epsilon']/((z-1)*(z-2)) and
          m.infinity_norm(err)<=m.infinity_norm(rc)*m.infinity_norm(f['Delta'])*m.infinity_norm(rf),
          'Rational spectral parameter outside {1,2}, explicit two-sided inverse matrices.')
check('poles_excluded',all((z*sp.eye(2)-f['Tf']).det()==0 for z in (1,2)),
      'No resolvent is asserted at either pole.')
# Invalid data must fail instead of silently manufacturing an example.
for name,fn in [('zero_modulus',lambda:m.residue_projector(8,0,0)),('zero_depth',lambda:m.weighted_terms(0)),
                ('bad_prime_weight',lambda:m.padic_weight(s['Eplus'],4)),('bad_Smith_base',lambda:m.smith_fibres(1,3,(1,)))]:
    rejected=False
    try: fn()
    except ValueError: rejected=True
    check('reject_'+name,rejected,'Expected invalid-input ValueError.')

report={'status':'PASS','scope':'Exact finite examples and symbolic identities for an editorial appendix; no new Lean or universal classification claim.',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),'check_count':len(checks),'sympy_version':sp.__version__,
        'model_sha256':hashlib.sha256((ROOT/'source/models.py').read_bytes()).hexdigest(),
        'checks':checks}
(ROOT/'checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(checks)} named exact checks. Finite tested ranges are recorded in EXACT_CHECKS.json.')
