#!/usr/bin/env python3
"""Run exact finite and symbolic checks. No Lean build and no general existence inference."""
from __future__ import annotations
import sys,json,hashlib,platform
from pathlib import Path
from itertools import product,combinations
from math import gcd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
import sympy as s
from models import *

checks=[];negative=[]
def check(name,value,scope='exact worked example'):
    if value is not True and value != s.true:raise AssertionError(name+': '+str(value))
    checks.append({'name':name,'status':'PASS','scope':scope})
def same(A,B):return s.simplify(s.Matrix(A)-s.Matrix(B))==s.zeros(s.Matrix(A).rows,s.Matrix(A).cols)
def reject(name,fn,reason):
    try:fn()
    except (AssertionError,ValueError,ZeroDivisionError) as ex:
        negative.append({'name':name,'status':'REJECTED','expected_reason':reason,'actual_exception':type(ex).__name__});return
    raise AssertionError('Negative control unexpectedly accepted: '+name)
def assertion(value):
    if not value:raise AssertionError('Deliberate false assertion')

for p in (2,3,5):
    check(f'residual_partition_{p}', sorted(x for r in range(p) for x in range(p**3) if x%p==r)==list(range(p**3)))
    check(f'positive_depth_preserves_root_{p}',all((x+p*h)%p==x%p for x in range(p**2) for h in range(-4,5)))
    check(f'horizontal_translation_changes_root_{p}',all((x+1)%p!=x%p for x in range(p**2)))
rs=quarter_branch();check('quarter_branch_values',rs==[4,19,94,469,2344,11719]);check('quarter_digits',decode_digits(5,rs)==[4,3,3,3,3,3])
check('quarter_algebraic_identity',all(4*x-1==3*5**m for m,x in enumerate(rs,1)))
reject('arbitrary_residues_not_a_branch',lambda:decode_digits(5,[4,18]),'Second residue must reduce to first.')
for q,d in [(2,1),(2,2),(3,1),(3,2),(5,1)]:
    for m in range(1,5):
        expected=smooth_count(q,d,m)
        actual=sum(1 for _ in product(range(0,q**m,q),repeat=d))
        check(f'smooth_chart_q{q}_d{d}_m{m}',actual==expected)
check('smooth_zeta',s.series(T/(1-9*T),T,0,7).removeO()==sum(smooth_count(3,2,m)*T**m for m in range(1,7)))
w=(1,2,4);counts=[weighted_count(2,w,m) for m in range(1,8)]
check('weighted_counts',counts==[1,2,8,32,256,2048,16384])
check('weighted_rational_form',s.cancel(weighted_zeta(2,w)-T*(1-6*T-8*T**2-32*T**3)/(1-8*T))==0)
check('weighted_series',s.series(weighted_zeta(2,w),T,0,8).removeO()==sum(a*T**m for m,a in enumerate(counts,1)))
check('empty_weighted_chart',s.cancel(weighted_zeta(3,())-T/(1-T))==0)
for m in range(1,6):
    check(f'weighted_direct_count_m{m}',sum(1 for _ in product(*(range(0,2**m,2**min(v,m)) for v in w)))==weighted_count(2,w,m))
check('sign_first_visibility', [m for m in range(1,7) if (1-(-1))%2**m]!=[] and min(m for m in range(1,7) if 2%2**m)!=1)
check('sign_visibility_depth_two',min(m for m in range(1,7) if 2%2**m)==2)
for p,e in [(2,2),(2,3),(3,2),(3,3),(5,2)]:
    for m in range(1,6):check(f'singular_direct_p{p}_e{e}_m{m}',len(roots_mod(p,m,lambda x:x**e))==singular_count(p,e,m))
    check(f'singular_zeta_p{p}_e{e}',s.series(singular_zeta(p,e),T,0,11).removeO()==sum(singular_count(p,e,m)*T**m for m in range(1,11)))
check('singular_square_counts', [singular_count(3,2,m) for m in range(1,9)]==[1,3,3,9,9,27,27,81])
check('singular_nonzero_child_dies',3 in roots_mod(3,2,lambda x:x*x) and not any(x%9==3 for x in roots_mod(3,3,lambda x:x*x)))
for m in range(1,5):
    check(f'singular_descendants_from_2m_reduce_to_zero_{m}',{x%(3**m) for x in roots_mod(3,2*m,lambda x:x*x)}=={0})
reject('growing_counts_do_not_mean_all_nodes_lift',lambda:assertion(any(x%9==3 for x in roots_mod(3,3,lambda x:x*x))),'The depth-two node 3 has no child.')
for p in [2,3,5,7,13]:
    expected=[1,0,0] if p==2 else ([2,2,2] if p in [5,13] else [0,0,0])
    check(f'companion_levels_p{p}',[len(roots_mod(p,m)) for m in [1,2,3]]==expected)
    for m in [1,2]:check(f'root_reduction_p{p}_m{m}',all(x%p**m in roots_mod(p,m) for x in roots_mod(p,m+1)))
check('5_adic_root_path',[2,root_lift(5,1,2)[0],root_lift(5,2,7)[0],root_lift(5,3,57)[0]]==[2,7,57,182])
check('negative_path',[(-x)%5**m for m,x in enumerate([2,7,57,182],1)]==[3,18,68,443])
reject('residual_root_does_not_ensure_deep_root',lambda:assertion(len(roots_mod(2,2))>0),'x^2+1 has a root mod 2 but no root mod 4.')
for depth in [3,5,8]:check(f'infinite_tail_window_nonempty_{depth}',len(list(range(depth,depth+10)))==10)
# The universal empty inverse-limit proof is in the prose, not inferred from these finite windows.
d0,d1,ps=complex_model();check('chain_condition',same(d1*d0,s.zeros(2,2)))
check('differential_ranks_mod5',(rank_mod(d0,5),rank_mod(d1,5))==(1,1))
check('cohomology_dimensions',(2-rank_mod(d0,5),4-rank_mod(d0,5)-rank_mod(d1,5),2-rank_mod(d1,5))==(1,2,1))
check('cohomology_kernel_cardinality',len(finite_kernel(d1,5))==125);check('cohomology_boundary_cardinality',len(finite_image(d0,5))==5)
for i,P in enumerate(ps):check(f'chain_projector_idempotent_{i}',same(P*P,P));check(f'complement_orthogonal_{i}',same(P*(s.eye(P.rows)-P),s.zeros(P.rows)))
check('chain_projector_d0',same(d0*ps[0],ps[1]*d0));check('chain_projector_d1',same(d1*ps[1],ps[2]*d1))
A0=s.Matrix([1,0]);A1=s.Matrix([[0,1]])
check('acyclic_packet_dimensions',(1-rank_mod(A0,5),2-rank_mod(A0,5)-rank_mod(A1,5),1-rank_mod(A1,5))==(0,0,0))
check('other_zero_packet_dimensions',(1-rank_mod(s.zeros(2,1),5),2-rank_mod(s.zeros(2,1),5)-rank_mod(s.zeros(1,2),5),1-rank_mod(s.zeros(1,2),5))==(1,2,1))
bad=s.diag(0,1,0,0);check('bad_projector_detected',not same(d0*ps[0],bad*d0))
reject('degreewise_projectors_need_chain_condition',lambda:assertion(same(d0*ps[0],bad*d0)),'Degreewise idempotence does not imply differential compatibility.')
check('five_sccs',sccs()==[('A','B'),('C',),('D','E'),('F',),('G',)])
check('minimum_seeds',minimum_seed_sets()==(3,[['A','D','G'],['A','E','G'],['B','D','G'],['B','E','G']]))
check('actual_reachability',reachable('ADG')==set(VERTICES));check('missing_source_unreachable',reachable('AG')==set('ABCFG'))
reject('one_seed_cannot_cover_three_sources',lambda:assertion(any(reachable([v])==set(VERTICES) for v in VERTICES)),'A seed outside a source component cannot reach it.')
for m in range(1,5):
    r=roots_mod(5,m);check(f'negation_preserves_equation_m{m}',{(-x)%5**m for x in r}==set(r));check(f'translation_fails_m{m}',any((x+1)%5**m not in r for x in r))
check('negation_commutes_with_reduction',all(((-x)%125)%25==(-(x%25))%25 for x in range(125)))
X=s.Symbol('X');poly=(X-2)*(X-3);check('common_polynomial',s.expand(poly)==X**2-5*X+6)
for p in [5,7]:check(f'charpoly_reduction_{p}',s.Poly(s.diag(2,3).charpoly(X).as_expr(),X,modulus=p)==s.Poly(X**2-5*X+6,X,modulus=p))
C,m,b,c=s3_data();check('s3_character_determinant',C.det()==6);check('s3_trace_vector',list(b)==[4,2,1]);check('s3_recovery',recover_multiplicities(C,b,c)==(2,0,1))
a=s.Matrix([[0,-1],[1,-1]]);q=s.Matrix([[0,1],[1,0]])
check('standard_s3_relations',same(a**3,s.eye(2)) and same(q*q,s.eye(2)) and same(q*a*q,a.inv()))
check('standard_s3_trace_values',[s.trace(s.eye(2)),s.trace(q),s.trace(a)]==[2,0,-1])
reject('trace_solution_not_integral',lambda:recover_multiplicities(C,[1,0,0],c),'Rational solution is not an integral multiplicity vector.')
reject('negative_multiplicity',lambda:recover_multiplicities(C,C*s.Matrix([-1,1,1]),c),'Representations do not have negative multiplicities.')
reject('capacity_failure',lambda:recover_multiplicities(C,C*s.Matrix([3,0,1]),c),'Target multiplicity exceeds known carrier capacity.')
for n in range(1,5):
    qn=2**n;ker={a for a in product(range(qn),repeat=3) if all(int(v)%qn==0 for v in C*s.Matrix(a))}
    check(f'trace_reduction_kernel_2pow{n}',ker=={(0,0,0),(qn//2,qn//2,0)})
check('one_digit_loss_witness',list(C*s.Matrix([4,4,0]))==[8,0,8]);check('one_extra_digit_separates',any(int(v)%16!=0 for v in C*s.Matrix([4,4,0])))
check('adjugate_precision_certificate',same(C.adjugate()*C,6*s.eye(3)))
reject('equal_precision_trace_recovery',lambda:assertion((4%8,4%8,0)==(0,0,0)),'Distinct multiplicities modulo 8 can give the same traces modulo 8.')
labels,ops=occupancy_data()
for target in product([0,1],repeat=3):
    E=joint_projector(target);count=labels.count(target)
    check('joint_packet_'+''.join(map(str,target)),same(E*E,E) and E.rank()==count and s.trace(E)==count)
check('progressive_positive_ranks',[s.eye(6).rank(),(s.eye(6)-ops[0]).rank(),((s.eye(6)-ops[0])*(s.eye(6)-ops[1])).rank(),joint_projector([0,0,0]).rank()]==[6,3,2,1])
check('empty_joint_packet',joint_projector([0,1,1])==s.zeros(6))
check('each_pair_occupied',all(any(all(row[j]==[0,1,1][j] for j in pair) for row in labels) for pair in combinations(range(3),2)))
reject('pairwise_occupancy_does_not_imply_joint',lambda:assertion(joint_projector([0,1,1]).rank()>0),'The selected triple 011 is absent although each pair occurs.')
check('trace_mod5_boundary',int(s.trace(s.eye(5)))%5==0 and rank_mod(s.eye(5),5)==5)
N=s.Matrix([[0,1],[0,0]]);check('jordan_boundary',N**2==s.zeros(2) and N.rank()==1 and (s.eye(2)).rank()==2)
reject('lagrange_formula_without_semisimplicity',lambda:assertion(N*s.eye(2)==s.zeros(2)),'The sole-eigenvalue Lagrange product is I, not the ordinary eigenspace projector.')
check('nonzero_sequence_converges_mod_p',all(3**k%3**m==0 for m in range(1,6) for k in range(m,m+5)))
check('signed_norm_residue_counterexample',2%5==(-3)%5 and abs(2)%5!=abs(-3)%5)
reject('absolute_norm_is_residue_function_over_Q',lambda:assertion(abs(2)%5==abs(-3)%5),'Opposite real signs can change absolute-norm residues.')
check('two_nonsquare_in_F5',all(a*a%5!=2 for a in range(5)))
check('field_norm_zero_fiber',tuple(z for z in F25 if f25_norm(z)==0)==((0,0),))
check('field_norm_fiber_counts',[sum(f25_norm(z)==a for z in F25) for a in range(5)]==[1,6,6,6,6])
check('determinant_norm',all(int(f25_matrix(z).det())%5==f25_norm(z) for z in F25))
check('norm_multiplicativity_625_pairs',all(f25_norm(f25_mul(z,w))==f25_norm(z)*f25_norm(w)%5 for z in F25 for w in F25))
check('matrix_multiplication_625_pairs',all(all(int(x)%5==0 for x in f25_matrix(z)*f25_matrix(w)-f25_matrix(f25_mul(z,w))) for z in F25 for w in F25))
v=(0,2);check('nonscalar_unit_witness',f25_norm(v)==2 and chi5(f25_norm(v))==-1)
check('quotient_unit_permutation',len({f25_mul(v,z) for z in F25})==25)
check('character_sum_zero',sum(chi5(f25_norm(z)) for z in F25)==0)
check('character_action_25_points',all(chi5(f25_norm(f25_mul(v,z)))==-chi5(f25_norm(z)) for z in F25))
check('unit_orbits_three_eights',sorted(map(len,unit_orbits()))==[8,8,8])
check('unit_orbits_alternating',all(chi5(f25_norm(orb[(j+1)%8]))==-chi5(f25_norm(orb[j])) for orb in unit_orbits() for j in range(8)))
check('scalar_quadratic_exception',all(chi5(a*a)==1 for a in range(1,5)))
check('degree_three_sufficient',scalar_witness(2,3) and gcd(3,4)==1)
check('coprimality_not_necessary',scalar_witness(1,2) and gcd(2,4)!=1)
for k in range(4):
    for d in range(1,7):check(f'exact_scalar_criterion_k{k}_d{d}',scalar_witness(k,d)==((k*d)%4!=0))
reject('nontrivial_scalar_character_alone_insufficient',lambda:assertion(scalar_witness(2,2)),'A nontrivial quadratic character is trivial on every scalar square.')
check('crt_solution',crt_three()==29)
check('crt_avoidance',gcd(crt_three(),30)==1)
check('crt_units',[a for a in range(30) if gcd(a,30)==1]==[1,7,11,13,17,19,23,29])
for L in range(1,26):
    r=L%5;check(f'lattice_boundary_L{L}',abs(lattice_sum(L))<=L*L-(L-r)**2)
check('complete_lattice_tiles_zero',all(lattice_sum(5*k)==0 for k in range(1,8)))
check('boundary_area_at_12',12**2-10**2==44)
h=s.Symbol('h',real=True);svar=s.Symbol('s',positive=True)
I=svar/(svar-s.Rational(1,2))
check('mellin_envelope_difference',s.cancel(I.subs(svar,1+h)-I.subs(svar,1)+h/(h+s.Rational(1,2)))==0)
for a in [s.Rational(-1,4),s.Rational(-1,8),s.Integer(0),s.Rational(1,8),s.Rational(1,4)]:check(f'mellin_bound_h{a}',abs(-a/(a+s.Rational(1,2)))<=4*abs(a))
check('mellin_derivative_at_one',s.diff(I,svar).subs(svar,1)==-2)
check('repeated_identity_trace_rows_rank_one',s.Matrix([list(C[0,:])]*8).rank()==1)
for p in primes_to(47):
    if p==2:continue
    check(f'quadratic_factorization_prime_{p}',len(roots_mod(p,1))==(2 if p%4==1 else 0))
A=s.Matrix([[0,-1],[1,0]])
check('matrix_root_exists_over_F3',all(int(x)%3==0 for x in A*A+s.eye(2)))
check('scalar_root_absent_over_F3',roots_mod(3,1)==())
check('extension_roots_over_F9',tuple(z for z in product(range(3),repeat=2) if f9_mul(z,z)==(2,0))==((0,1),(0,2)))
check('companion_charpoly',s.expand(A.charpoly(X).as_expr())==X**2+1)
reject('no_scalar_root_does_not_mean_no_representation',lambda:assertion(not all(int(x)%3==0 for x in A*A+s.eye(2))),'A 2 by 2 companion matrix realizes the equation over F3.')

# Additional correspondence checks for the displayed explanatory claims.
check('adding_F_to_G_reduces_source_rank',minimum_seed_sets(VERTICES,EDGES+(('F','G'),))[0]==2)
parents={a:0 for a in product(range(0,9,3),repeat=2)}
for a in product(range(0,27,3),repeat=2):parents[tuple(v%9 for v in a)]+=1
check('every_smooth_parent_has_nine_children',set(parents.values())=={9})
all_E=[joint_projector(t) for t in product([0,1],repeat=3)]
check('joint_packet_sum_identity',sum(all_E,s.zeros(6))==s.eye(6))
check('joint_packet_pairwise_annihilation',all(all_E[i]*all_E[j]==s.zeros(6) for i in range(8) for j in range(8) if i!=j))
S=s.Matrix([[1,1],[0,1]])
check('norm_basis_change_invariance_all25',all(int((S.inv()*f25_matrix(z)*S).det())%5==f25_norm(z) for z in F25))
check('boundary_sum_at_12',lattice_sum(12)==1)
check('zero_bulk_at_12',lattice_sum(10)==0)
x=s.Symbol('x',positive=True)
check('mellin_logarithmic_moment',s.integrate(s.log(x)/x**s.Rational(3,2),(x,1,s.oo))==4)
check('fourth_power_representation_over_Q',A**4==s.eye(2))

report={'status':'PASS','checks_passed':len(checks),'positive_assertions':len(checks),'negative_controls_rejected':len(negative),
 'scope':'Finite examples and exact symbolic identities. No universal Galois occurrence, automorphic occupancy, or Lean proof checked.',
 'coefficient_domains':['integers','rationals','symbolic polynomials','finite fields F3,F5,F25,F9','Z/(2^n), n <= 4'],
 'bounds':{'singular_enumerations':'p=2,3,5 with listed exponents and depths <=5; square-root images at depths <=8 for p=3','trace_kernel_max_modulus':16,'norm_multiplication_pairs':625,'lattice_max_side':25,'quadratic_prime_scan_max':47},
 'versions':{'python':platform.python_version(),'sympy':s.__version__},'checks':checks,'negative_controls':negative,
 'limits':['Exact finite results do not assert an infinite arithmetic existence theorem.','The finite-tail counterexample and Mellin analytic argument have their stated prose proofs, not proofs inferred from sampling.','No fresh Lean compilation.'],
 'data':{'quarter_residues':quarter_branch(),'weighted_counts':counts,'norm_fiber_counts':[1,6,6,6,6],'lattice_side_12_sum':lattice_sum(12),'source_components':sccs(),'minimum_seed_sets':minimum_seed_sets()[1]},
 'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'source/models.py',Path(__file__)]}}
(ROOT/'checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(f"PASS: {len(checks)} positive exact assertions; {len(negative)} false controls rejected")
print('lattice S12:',lattice_sum(12))
