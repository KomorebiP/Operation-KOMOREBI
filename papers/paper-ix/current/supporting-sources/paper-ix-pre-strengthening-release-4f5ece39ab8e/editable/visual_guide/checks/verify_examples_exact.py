#!/usr/bin/env python3
"""Fresh standard-library replacement for inherited SymPy checks; exact illustrative calculations.

Every assertion is recorded by name. Parameter sweeps count as one assertion
with an explicit case count; they are never advertised as universal proofs.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,time,hashlib,platform
from itertools import product
from math import factorial,comb
from fractions import Fraction as Q
import argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from models import *

ROOT=Path(__file__).resolve().parents[1]
checks=[];controls=[];t0=time.perf_counter()
def require(name,condition,detail=None,cases=1):
    if not bool(condition):raise AssertionError(name+' FAILED: '+str(detail))
    checks.append(dict(name=name,passed=True,cases=cases,detail=detail))
def reject(name,false_claim,detail=None):
    if bool(false_claim):raise AssertionError('Invalid control unexpectedly accepted: '+name)
    controls.append(dict(name=name,rejected=True,detail=detail))
def bernoulli(n):
    # Independent rational recurrence from t/(exp(t)-1), B_1=-1/2.
    bs=[Q(1)]
    for j in range(1,n+1):
        bs.append(-sum(Q(comb(j+1,k))*bs[k] for k in range(j))/Q(j+1))
    return bs[n]
def poly_mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def matrix_mul(a,b):
    return [[sum(Q(a[i][k])*Q(b[k][j]) for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def scaled_eye(n,q):return [[Q(q if i==j else 0) for j in range(n)] for i in range(n)]

# Digits, selectors, and exact finite CRT.
require('valuation_zero_is_infinity',val(0,2) is None)
require('rational_valuation_can_be_negative',val(Q(1,84),3)==-1)
require('ultrametric_three_points',[val(9-1,2),val(13-1,2),val(13-9,2)]==[3,2,2])
require('residue_of_odd_denominator',residue(Q(1,3),2,5)==11)
try:residue(Q(1,2),2,3)
except ValueError: controls.append(dict(name='nonintegral_rational_residue',rejected=True))
else:raise AssertionError('Nonintegral rational was reduced without permission.')
a=list(range(1,19))
ps=[[a[n] if n%6==j else 0 for n in range(18)] for j in range(6)]
require('selectors_reconstruct_every_coefficient',all(sum(ps[j][n] for j in range(6))==a[n] for n in range(18)),cases=18)
require('selectors_are_idempotent_and_disjoint',all((ps[j][n] if n%6==k else 0)==(ps[j][n] if j==k else 0) for j in range(6) for k in range(6) for n in range(18)),cases=648)
require('width_two_refines_to_width_six',all(sum(ps[j][n] for j in range(6) if j%2==r)==(a[n] if n%2==r else 0) for r in range(2) for n in range(18)),cases=36)
require('CRT_twelve_addresses_are_bijective',len({(n%4,n%3) for n in range(12)})==12)
require('CRT_twelve_inverse',all(crt_pair(n%4,4,n%3,3)==n for n in range(12)),cases=12)
reject('noncoprime_addresses_are_independent',len({(n%4,n%2) for n in range(4)})==8)

# Hurwitz multiplication and two independent Euler constructions.
require('Hurwitz_ones_are_powers_of_two',hurwitz([1]*9,[1]*9,8)==tuple(2**n for n in range(9)),cases=9)
require('Cauchy_ones_are_linear',all(sum(1 for _ in range(n+1))==n+1 for n in range(9)),cases=9)
reject('Cauchy_and_Hurwitz_are_interchangeable',hurwitz([1]*5,[1]*5,4)[4]==5)
require('prime_Leibniz_middle_coefficients_vanish',all(comb(p,k)%p==0 for p in [2,3,5,7] for k in range(1,p)),cases=13)
for p in [2,3,5,7]:
    # Full windows through index 6+p are available in both inputs.
    aa=[n*n-2*n+3 for n in range(14)];bb=[(-1)**n*(2*n+1) for n in range(14)]
    full=hurwitz(aa,bb,6+p)
    shift_a=hurwitz(aa[p:],bb,6);shift_b=hurwitz(aa,bb[p:],6)
    require(f'prime_Leibniz_direct_complete_window_p{p}',all((full[n+p]-shift_a[n]-shift_b[n])%p==0 for n in range(7)),cases=7)

for N,j in [(1,0),(2,0),(2,1),(4,0),(4,1),(4,2),(4,3),(6,3),(10,4)]:
    c=euler_packet(N,j,8)
    require(f'Euler_recurrence_vs_reciprocal_N{N}_j{j}',c==packet_from_ordinary_inverse(N,j,8),cases=9)
    require(f'cleared_triangular_rows_N{N}_j{j}',all(sum(comb(N*n+j,N*q)*c[q] for q in range(n+1))==(1 if n==0 else 0) for n in range(9)),cases=9)
    require(f'denominator_product_N{N}_j{j}',all((clearing_product(N,j,n)*c[n]).denominator==1 for n in range(9)),cases=9)
c=euler_packet(6,3,2)
require('normalization_exact_values',c==(Q(1),Q(-1,84),Q(703,5460)))
require('normalization_difference',c[2]-c[1]==Q(64,455))
require('normalization_difference_valuation',val(c[2]-c[1],3)==0)
require('unnormalized_difference',6*(c[2]-c[1])==Q(384,455))
require('unnormalized_difference_valuation',val(6*(c[2]-c[1]),3)==1)
reject('unrestricted_no_factorial_loss',at_least(c[2]-c[1],3,1))
require('Bernoulli_boundary_specialization',all(bernoulli(2*n)*(2-2**(2*n))==euler_packet(2,1,8)[n] for n in range(9)),cases=9)

# Newton coordinates, genuine cancellation, and finite affine kernels.
a=[3**n for n in range(10)];dt=difference_table(a)
require('Newton_recursive_table_vs_stencils',all(dt[k][n]==difference(a,n,k) for k in range(10) for n in range(10-k)),cases=55)
require('Newton_coefficients_geometric',all(dt[k][0]==2**k for k in range(10)),cases=10)
require('Newton_reconstruction',all(sum(comb(n,k)*dt[k][0] for k in range(n+1))==a[n] for n in range(10)),cases=10)
f=[2*n+6*choose(n,2) for n in range(8)]
require('weighted_difference_cancellation',difference(f,1,1)==8 and val(2,2)==val(6,2)==1 and val(8,2)==3)
require('affine_Mahler_cancellation',theta(2,1,3,2)==8 and 4+4==8)
require('binary_kernel_formula',all(theta(2,0,k+j,k)==2**(k-j)*comb(k,j) for k in range(13) for j in range(k+1)),cases=91)
reject('minimum_term_weight_always_exact',val(4+4,2)==min(val(4,2),val(4,2)))
require('geometric_step_amplification',all(difference(a,n,k,h)==Q(3**n*(3**h-1)**k) for h in [0,1,2,3] for k in range(3) for n in range(3) if n+k*h<len(a)),cases=36)

# Standard window and bounded instances of the all-address difference bounds.
for p,m in [(3,2),(5,2)]:
    N=p*m;h=(p-1)//m
    cs=[euler_packet(N,j,32) for j in range(N)]
    require(f'standard_window_address_independence_p{p}',all(residue(cs[j][n],p,1)==residue(cs[0][n],p,1) for j in range(p) for n in range(13)),cases=p*13)
    require(f'Lucas_row_reduction_p{p}',all((comb(N*n+j,N*q)-comb(m*n,m*q))%p==0 for j in range(p) for n in range(9) for q in range(n+1)),cases=p*45)
    require(f'standard_period_from_row_one_p{p}',all(residue(cs[j][n+h]-cs[j][n],p,1)==0 for j in range(p) for n in range(1,12)),cases=p*11)
    sweep=[]
    for j in range(N):
        uu=[factorial(j)*x for x in cs[j]]
        for n in range(5):
            for k in range(5):
                for u in [1,2,3]:
                    if n+k*u*h>=len(uu):continue
                    lower=min(k*(1+(val(u,p) or 0)),m*n)
                    dv=difference(uu,n,k,u*h)
                    sweep.append(at_least(dv,p,lower))
    require(f'amplified_all_address_bound_p{p}',all(sweep),cases=len(sweep),detail='Rows 0..4, orders 0..4, multipliers 1,2,3; no extrapolation from these tests.')
require('standard_p5_rows', [residue(x,5,1) for x in euler_packet(10,0,8)]==[1,4,0,4,0,4,0,4,0])
reject('standard_period_starts_at_row_zero',residue(euler_packet(10,0,2)[2]-1,5,1)==0)
u=[6*x for x in euler_packet(6,3,10)]
newton_terms=[comb(3,k)*difference(u,1,k) for k in range(1,4)]
require('Nishibuchi_degree_conversion',6*(1+3)==6*1+2*3**2)
require('Nishibuchi_worked_period',at_least(u[4]-u[1],3,2))
require('Nishibuchi_Newton_sum',sum(newton_terms)==u[4]-u[1])
require('Nishibuchi_each_Newton_term',all(at_least(v,3,2) for v in newton_terms),cases=3)

# Actual finite unit coordinates.
for p,L in [(3,2),(5,2),(7,1)]:
    mod=p**(L+1);units=[a for a in range(mod) if a%p]
    require(f'unit_coordinates_p{p}',all((w:=pow(a,p**L,mod)) and pow(w,p-1,mod)==1 and (a*pow(w,-1,mod))%p==1 for a in units),cases=len(units))
require('unit_coordinate_example',pow(2,25,125)==57 and 2*pow(57,-1,125)%125==11)
require('dyadic_sign_coordinates',all((a*(1 if a%4==1 else -1))%4==1 for a in range(1,32,2)),cases=16)
require('dyadic_sign_example',(-29)%32==3 and 29%4==1)
reject('mod_two_recovers_sign',(1%2)!=((-1)%2))

# Four dyadic packets: numerical instances of the proved exact theorem.
co,do=packet_offsets()
for j in range(4):
    cc=euler_packet(4,j,64);uu=[factorial(j)*v for v in cc]
    require(f'dyadic_integrality_j{j}',all(at_least(v,2,0) for v in cc),cases=len(cc))
    require(f'dyadic_first_Newton_offset_j{j}',val(difference(cc,0,1),2)==co[j])
    dis=[(n,T) for n in range(9) for T in range(1,33)]
    require(f'exact_normalized_displacements_j{j}',all(val(cc[n+T]-cc[n],2)==val(T,2)+co[j] for n,T in dis),cases=len(dis))
    require(f'exact_unnormalized_displacements_j{j}',all(val(uu[n+T]-uu[n],2)==val(T,2)+do[j] for n,T in dis),cases=len(dis))
    sweep=[(n,k,u) for n in range(5) for k in range(6) for u in range(5)]
    require(f'all_row_all_order_lower_bound_j{j}',all(at_least(difference(cc,n,k,u),2,k*(1+(val(u,2) or 0))) for n,k,u in sweep),cases=len(sweep))
    for depth in [1,2,3,4]:
        perm=scaled_packet_map(j,depth);mod=2**depth
        require(f'finite_isometry_permutation_j{j}_r{depth}',sorted(perm)==list(range(mod)),cases=mod)
        pairs=list(product(range(mod),repeat=2))
        vv=lambda x: depth if x==0 else min(depth,val(x,2))
        require(f'finite_isometry_distances_j{j}_r{depth}',all(vv(perm[a]-perm[b])==vv(a-b) for a,b in pairs),cases=len(pairs))
    p16=scaled_packet_map(j,4);p8=scaled_packet_map(j,3)
    require(f'finite_isometry_reduction_j{j}',all(p16[a]%8==p8[a%8] for a in range(16)),cases=16)
    r=6;least=2**max(0,r-do[j])
    require(f'least_period_instance_j{j}',all(at_least(uu[n+least]-uu[n],2,r) for n in range(5)))
    require(f'smaller_periods_fail_at_zero_j{j}',all(not at_least(uu[T]-uu[0],2,r) for T in range(1,least)),cases=max(0,least-1))
require('original_period_table_depth_ten',[2**max(0,10-d) for d in do]==[512,512,32,128],detail='Evaluation of the proved formula, not a direct 512-row sweep.')
require('exact_images_low_residues',all(residue(2*v,2,5)==2 for v in euler_packet(4,2,20)) and all(residue(6*v,2,3)==6 for v in euler_packet(4,3,20)),cases=42)
reject('all_four_unnormalized_periods_equal',len(set(2**max(0,10-d) for d in do))==1)

# Classical Euler reconstructions and sharp dyadic weights.
e=classical_euler(18)
require('classical_signed_Euler_prefix',e[:7]==(1,-1,5,-61,1385,-50521,2702765))
require('classical_N2_packet_matches',tuple(Q(x) for x in e[:10])==euler_packet(2,0,9),cases=10)
for p in [1,3,5,9]:
    require(f'odd_length_exact_reconstruction_{p}',all(sum(odd_terms(p,n))==e[n] for n in range(11)),cases=11)
    if p in [3,5]:
        pairs=[(n,M) for n in range(11) for M in range(n+2)]
        require(f'odd_prime_truncation_{p}',all((e[n]-sum(odd_terms(p,n)[:M+1]))%p**(2*M+2)==0 for n,M in pairs),cases=len(pairs))
require('beta_prefix',beta(3)==(Q(1),Q(-1,3),Q(1,15),Q(-2,189)))
require('dyadic_source_is_unit',all(val(dyadic_source(n),2)==0 for n in range(19)),cases=19)
require('dyadic_exact_reconstruction',all(sum(dyadic_terms(n))==e[n] for n in range(19)),cases=19)
require('kappa_Bernoulli_identity',all(kappa(m)==-2**(4*m)*(2*m-1)*bernoulli(2*m) for m in range(1,16)),cases=15)
require('kappa_exact_valuation',all(val(kappa(m),2)==4*m-1 for m in range(1,16)),cases=15)
pairs=[(n,M) for n in range(19) for M in range(n+2)]
require('sharp_uniform_dyadic_lower_bound',all(at_least(e[n]-dyadic_truncation(n,M),2,4*M+3) for n,M in pairs),cases=len(pairs))
require('first_omitted_row_attains_bound',all(e[M+1]-dyadic_truncation(M+1,M)==kappa(M+1) and val(kappa(M+1),2)==4*M+3 for M in range(12)),cases=12)
require('row_dependent_summand_weights',all(val(dyadic_terms(n)[m],2)==4*m-1+val(comb(2*n,2*m),2) for n in range(1,16) for m in range(1,n+1)),cases=120)
require('full_depth_is_exact',all(dyadic_truncation(n,n)==e[n] for n in range(19)),cases=19)
reject('uniform_extra_dyadic_digit',at_least(e[2]-dyadic_truncation(2,1),2,8))
reject('every_row_attains_uniform_bound',val(e[6]-dyadic_truncation(6,0),2)==3)

# Direct polynomial evaluation compared to correction equations.
for q in [2,3,4,5]:
    cases=[]
    for coeff in [(-2,0,1),(-5,0,1),(2,1,1),(0,0,1),(0,1)]:
        for L in [1,2]:
            mod=q**L
            for x in range(mod):
                ev=lambda z:sum(c*z**i for i,c in enumerate(coeff))
                der=lambda z:sum(i*c*z**(i-1) for i,c in enumerate(coeff) if i)
                if ev(x)%mod:continue
                r=(ev(x)//mod)%q;j=der(x)%q
                cases.append(all((ev(x+mod*t)%(mod*q)==0)==((r+j*t)%q==0) for t in range(q)))
    require(f'polynomial_correction_exact_q{q}',all(cases),cases=len(cases))
lt=lift_univariate((-2,0,1),7,3,1,5)
require('square_root_digit_tower',[r['next'] for r in lt]==[10,108,2166,4567,38181])
require('square_root_digits',[r['digit'] for r in lt]==[1,2,6,1,2])
require('square_root_tower_evaluates',all((r['next']**2-2)%(r['modulus']*7)==0 for r in lt),cases=5)
require('representative_change_coset',all((((x+7*a)**2-2)//7-(x*x-2)//7-2*x*a)%7==0 for x in [3,10] for a in range(7)),cases=14)
J=[[1,1,0],[0,0,0]];r=(-1,0);fiber=correction_fiber(J,r,3)
require('torsor_nine_digits',len(fiber)==9 and fiber==[(a,(1-a)%3,c) for a in range(3) for c in range(3)])
require('torsor_kernel_rank',rank_mod(J,3)==1 and len(correction_fiber(J,(0,0),3))==9)
require('torsor_translations',all(tuple((x-y)%3 for x,y in zip(a,b)) in correction_fiber(J,(0,0),3) for a,b in product(fiber,repeat=2)),cases=81)
require('obstructed_fiber_empty',not correction_fiber(J,(-1,1),3))
require('composite_kernel_is_not_field_formula',len(correction_fiber([[2]],(0,),4))==2)
reject('composite_rank_one_implies_single_lift',len(correction_fiber([[2]],(0,),4))==1)

# Shared corrections, redundant equations, and prescribed parameters.
obs=list(product(range(3),repeat=2));pairs=list(product(obs,repeat=2));U=list(product(range(3),repeat=3))
require('shared_label_fiber_product',all((a[1]==b[0])==any((w[0],w[1])==a and (w[1],w[2])==b for w in U) for a,b in pairs),cases=81)
require('shared_label_cardinality',sum(a[1]==b[0] for a,b in pairs)==27)
reject('separate_lifts_imply_joint',any(x%4==0 and (x-2)%4==0 for x in [0,2]))
require('presentation_redundancy_changes_cokernel',rank_mod([[1]],3)==rank_mod([[1],[0]],3)==1 and 3**(1-1)!=3**(2-1))
require('singular_dead_branches',roots_mod((-5,0,1),2)==[1] and roots_mod((-5,0,1),4)==[1,3] and roots_mod((-5,0,1),8)==[])
reject('one_singular_lift_guarantees_all_depths',bool(roots_mod((-5,0,1),8)))
reject('nonlinear_depth_zero_linearization',any((-1+0*t)%2==0 for t in range(2)))
require('depth_zero_has_actual_root',1**2-1==0)
require('prescribed_T_zero_digit',len(correction_fiber([[0]],(0,),2))==2)
require('prescribed_T_nonzero_digit',len(correction_fiber([[0]],(1,),2))==0)
require('full_jacobian_surjective_not_solved_block',rank_mod([[0,1]],2)==1 and rank_mod([[0]],2)==0)
require('chosen_solved_block_every_parameter',all(len(correction_fiber([[1]],(v,),2))==1 for v in range(2)))

# Nonsingular chart, strict threshold, and first-order precision.
for L in [3,4,5,6,7,8]:
    q=2**L;g=graph_roots(q)
    require(f'root_chart_all_even_parameters_L{L}',len(g)==q//2 and all((y+y*y+t)%q==0 for t,y in g),cases=len(g))
    vv=lambda x: L if x==0 else min(L,val(x,2))
    require(f'root_chart_congruence_levels_L{L}',all(vv(t-u)==vv(y-z) for (t,y),(u,z) in product(g,repeat=2)),cases=len(g)**2)
psi=[Q(0)]+[-Q(comb(2*(n-1),n-1),n) for n in range(1,9)]
psq=poly_mul(psi,psi)
require('implicit_series_residual_to_degree_eight',all(psi[n]+psq[n]+(1 if n==1 else 0)==0 for n in range(9)),cases=9)
require('implicit_series_derivative_sign',psi[1]==-1)
reject('implicit_derivative_positive',psi[1]==1)
require('weighted_root_linear_displacement',2*(-8)+16==0 and val(-8,2)==4-1)
require('weighted_threshold_failure',val(1**2+3,2)==2 and val(2,2)==1 and roots_mod((3,0,1),8)==[])
reject('weighted_nonstrict_threshold_suffices',bool(roots_mod((3,0,1),8)))
require('weighted_quadratic_residual',val(1**2-17,2)==4 and val(2,2)==1)
require('finite_weighted_candidates', [x for x in roots_mod((-17,0,1),256) if x%4==1]==[105,233])
require('finite_extra_branch_dies',all((x*x-17)%512 for x in [105,361]) and all((x*x-17)%512==0 for x in [233,489]))
require('weighted_sqrt_displacement',val(233-1,2)==3)
require('joint_linear_parameter_and_coefficient',(-8)+4+4==0)
reject('omit_parameter_forcing',at_least(-8-(-4),2,4))
reject('reverse_parameter_sign',at_least(-8-0,2,4))
y=next(y for y in roots_mod((2,1,1),256) if y%2==0)
require('nonlinear_motion_root_residue',y==90)
require('nonlinear_motion_error_is_exact_two_digits',val(y+2,2)==2)
reject('uniform_extra_motion_digit',at_least(y+2,2,3))
J=[[2,0],[0,8]];A=[[4,0],[0,1]];B=[[2,0,1],[0,8,3],[0,0,1]];C=[[4,0,-4],[0,1,-3],[0,0,8]]
require('inverse_weight_smaller_than_determinant',val(2*8,2)==4 and all(Q(z).denominator==1 for row in A for z in row) and Q(4,8).denominator==2)
require('augmentation_left_inverse',matrix_mul(C,B)==scaled_eye(3,8))
require('augmentation_right_inverse',matrix_mul(B,C)==scaled_eye(3,8))
require('weighted_vector_motion',[-128*Q(1,2),-128*Q(1,8)]==[-64,-16])

# CRT compatibility and an end-to-end arithmetic-to-root calculation.
crt=[crt_pair(0,2**r,1,3**r) for r in range(1,7)]
require('finite_CRT_approximants',crt==[4,28,136,1216,1216,16768])
require('finite_CRT_satisfies_each_precision',all(crt[r-1]%(2**r)==0 and crt[r-1]%(3**r)==1 for r in range(1,7)),cases=6)
require('finite_CRT_compatible_transitions',all(crt[r]%(6**r)==crt[r-1] for r in range(1,6)),cases=5)
syn=synthesis()
require('synthesis_Euler_value',syn['E']==1385)
require('synthesis_truncation',syn['truncation']==Q(-91019,45))
require('synthesis_error_precision',val(syn['coefficient_error'],2)==8)
require('synthesis_shared_target_mod256',syn['target']==syn['approx_target']==210)
require('synthesis_unique_even_root_mod256',syn['even_roots']==[14])
require('synthesis_polynomial_residual',14**2+14-210==0)
require('synthesis_root_vs_true_integer_target',(14**2+14-2*1385)%256==0)
require('synthesis_odd_branch_kept_separate',[x for x in range(256) if (x*x+x-210)%256==0]==[14,241])

# New guide pages: explicit transported selectors and recurrence packets.
T=[[1,0,0,0],[1,1,0,0],[0,2,1,0],[0,0,3,1]]
V=[[1,0,0,0],[-1,1,0,0],[2,-2,1,0],[-6,6,-3,1]]
P=[[1,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,0,0]]
Phat=matrix_mul(matrix_mul(T,P),V)
require('transported_coordinates_two_inverse_orders',matrix_mul(T,V)==scaled_eye(4,1) and matrix_mul(V,T)==scaled_eye(4,1))
require('transported_selector_actual_matrix',Phat==[[1,0,0,0],[1,0,0,0],[2,-2,1,0],[6,-6,3,0]])
require('transported_selector_is_idempotent',matrix_mul(Phat,Phat)==Phat)
require('transported_selectors_are_complementary',matrix_mul(Phat,[[Q(i==j)-Phat[i][j] for j in range(4)] for i in range(4)])==scaled_eye(4,0))
reject('transported_selector_is_raw_even_selector',Phat==P)
fib=[0,1]
for n in range(2,16):fib.append(fib[-1]+fib[-2])
comp=[[1,1],[1,0]];jump=matrix_mul(comp,comp)
require('Fibonacci_two_step_actual_jump',jump==[[2,1],[1,1]])
square_jump=matrix_mul(jump,jump)
require('Fibonacci_jump_characteristic_identity',all(square_jump[i][j]-3*jump[i][j]+(1 if i==j else 0)==0 for i in range(2) for j in range(2)),cases=4)
require('Fibonacci_even_packet_values',fib[::2][:7]==[0,1,3,8,21,55,144])
require('Fibonacci_odd_packet_values',fib[1::2][:7]==[1,2,5,13,34,89,233])
require('Fibonacci_even_and_odd_packet_recurrence',all(fib[n+4]-3*fib[n+2]+fib[n]==0 for n in range(12)),cases=12)
reject('one_step_companion_for_two_step_packet',matrix_mul(comp,[[1],[0]])==matrix_mul(jump,[[1],[0]]))
require('zero_equation_preserves_root_set_mod5',all((x%5==0)==(x%5==0 and 0%5==0) for x in range(25)),cases=25)
require('zero_equation_adds_cokernel_coordinate',rank_mod([[1]],5)==rank_mod([[1],[0]],5)==1 and 5**0!=5**1)
U=[[1,2],[0,1]];Ui=[[1,-2],[0,1]];JJ=[[1,0],[0,0]]
require('invertible_equation_change_has_inverse',matrix_mul(U,Ui)==scaled_eye(2,1) and matrix_mul(Ui,U)==scaled_eye(2,1))
require('invertible_equation_change_preserves_attainment',all(((a,b) in {matvec(JJ,t,5) for t in product(range(5),repeat=2)})==(matvec(U,(a,b),5) in {matvec(matrix_mul(U,JJ),t,5) for t in product(range(5),repeat=2)}) for a,b in product(range(5),repeat=2)),cases=25)
# Explicit finite residue root path for one fixed parameter.
root_path=[]
for L in range(1,9):
    rr=[y for y in range(0,2**L,2) if (y+y*y+2)%2**L==0]
    require(f'fixed_parameter_unique_even_residue_L{L}',len(rr)==1,cases=2**(L-1))
    root_path.append(rr[0])
require('fixed_parameter_root_path_values',root_path==[0,2,2,10,26,26,90,90])
require('fixed_parameter_root_path_compatible',all(root_path[k]%2**k==root_path[k-1] for k in range(1,8)),cases=7)
reject('finite_root_is_exact_integer_root',90+90**2+2==0)
files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),ROOT/'source/models.py']}
result={'status':'PASS','scope':'Fresh integer/Fraction replacement check of all displayed arithmetic and bounded example families; original SymPy script was not executed. No Lean compiler is invoked.','checks_passed':len(checks),'positive_case_evaluations':sum(x['cases'] for x in checks),'negative_controls_rejected':len(controls),'checks':checks,'invalid_controls_rejected':controls,'runtime_seconds':time.perf_counter()-t0,'python_version':platform.python_version(),'arithmetic':'Python unbounded integers and fractions.Fraction; independent rational Bernoulli recurrence, polynomial multiplication and explicit matrix multiplication.','randomness_used':False,'source_sha256':files,'limits':['Parameter sweeps are finite tests, not universal proofs.','Finite residue representatives are not exact p-adic roots.','Period tables at larger depths evaluate the manuscript formula; direct sweeps have stated smaller bounds.','Fresh standard-library replacement checks do not constitute a rerun of the inherited SymPy workflow.','Exactness refers to integer/rational arithmetic, not independently kernel-checked proofs.']}
ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,default=ROOT/'checks/FRESH_EXACT_CHECKS.json');args=ap.parse_args();args.result.parent.mkdir(parents=True,exist_ok=True);args.result.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','checks_passed','positive_case_evaluations','negative_controls_rejected','runtime_seconds']},indent=2))
