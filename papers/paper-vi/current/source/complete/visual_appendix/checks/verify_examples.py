#!/usr/bin/env python3
"""Exact finite/symbolic checks, with explicitly rejected false controls. No Lean invocation."""
from __future__ import annotations
import argparse, hashlib, json, platform, sys
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'source'))
from models import R,M,norm1,stochastic,basis,chain,transfer,expectation,bayes,coarse_effective,posterior_packets,filter_model,green,fk_paths
checks=[];controls=[]
def check(name,condition,detail=''):
    if not bool(condition):raise RuntimeError('Exact check failed: '+name+' '+detail)
    checks.append({'name':name,'status':'PASS','detail':detail})
def eq(name,a,b,detail=''):
    diff=a-b
    okay=all(s.simplify(x)==0 for x in diff) if isinstance(diff,s.MatrixBase) else s.simplify(diff)==0
    check(name,okay,detail)
def reject(name,condition,why):
    if bool(condition):raise RuntimeError('False control was not rejected: '+name)
    controls.append({'name':name,'status':'REJECTED','reason':why})
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'checks/EXACT_CHECKS.json');args=ap.parse_args()
    Q,K,C,Kc,H,Ps,bad=chain();q,r=s.symbols('q r',real=True);t=s.symbols('t',nonnegative=True);z=s.symbols('z',positive=True)
    eq('four_state_column_generator',s.ones(1,4)*Q,s.zeros(1,4));check('generator_off_diagonal_positive',all(Q[i,j]>=0 for i in range(4) for j in range(4) if i!=j))
    check('fine_transition_stochastic',stochastic(K));check('coarse_transition_stochastic',stochastic(Kc));check('perturbed_transition_stochastic',stochastic(bad))
    eq('walsh_orthonormality',H.T*H,s.eye(4));eq('generator_spectral_resolution',H.T*Q*H,s.diag(0,-2,-4,-6));eq('transition_spectrum',H.T*K*H,s.diag(1,R(3,4),R(1,2),R(1,4)))
    for i in range(4):
        for j in range(4):eq(f'projector_multiplication_{i}_{j}',Ps[i]*Ps[j],Ps[i] if i==j else s.zeros(4))
    eq('projectors_complete',sum(Ps,s.zeros(4)),s.eye(4));eq('transfer_initial',transfer(1),s.eye(4));eq('transfer_composition_polynomial',transfer(q)*transfer(r),transfer(q*r))
    eq('transfer_generator_derivative',-2*q*transfer(q).diff(q),Q*transfer(q));eq('transfer_columns_mass_one',s.ones(1,4)*transfer(q),s.ones(1,4));eq('transfer_midtime_seed',transfer(R(1,2))*basis(4,0),M([R(15,32),R(5,32),R(9,32),R(3,32)]))
    E=[s.diag(1,1,0,0),s.diag(0,0,1,1)]
    for a in range(2):
        for b in range(2):eq(f'packet_convolution_{a}_{b}',E[a]*transfer(q*r)*E[b],sum([E[a]*transfer(q)*Eg*transfer(r)*E[b] for Eg in E],s.zeros(4)))
    for m in range(7):eq(f'exact_lumping_horizon_{m}',C*K**m,Kc**m*C)
    eq('generator_lumping',C*Q,M([[-2,2],[2,-2]])*C)
    D=C*bad-Kc*C;eq('one_step_defect',D,M([[-R(1,16),0,0,0],[R(1,16),0,0,0]]));eq('one_step_defect_l1',norm1(D),R(1,8))
    for m in range(9):
        defect=C*bad**m-Kc**m*C;rhs=sum([Kc**(m-1-j)*D*bad**j for j in range(m)],s.zeros(2,4))
        eq(f'defect_telescoping_{m}',defect,rhs);check(f'finite_horizon_l1_bound_{m}',norm1(defect)<=m*norm1(D))
    reject('arbitrary_partition_dynamics_commute',C*bad==Kc*C,'A one-column perturbation changes an aggregate transition probability.')
    # Scalar Duhamel and resolvent identities retain the sign convention.
    u=s.symbols('u',real=True)
    eq('scalar_duhamel',s.integrate(s.exp(-2*(t-u))*s.exp(-u),(u,0,t)),s.exp(-t)-s.exp(-2*t))
    eq('scalar_resolvent_defect',1/(z+1)-1/(z+2),1/((z+1)*(z+2)))
    weights,W,E,E0,Ds,f,energies=expectation()
    eq('conditional_idempotent',E*E,E);eq('conditional_weighted_adjoint',W*E,E.T*W);eq('conditional_constant_preserved',E*s.ones(4,1),s.ones(4,1));eq('conditional_average',E*f,M([2,2,R(26,7),R(26,7)]));eq('conditional_mean',E0*f,s.ones(4,1)*R(16,5))
    eq('tower_coarse_after_fine',E0*E,E0);eq('tower_fine_after_coarse',E*E0,E0)
    for i in range(3):
        for j in range(3):eq(f'martingale_packet_product_{i}_{j}',Ds[i]*Ds[j],Ds[i] if i==j else s.zeros(4))
    eq('martingale_reconstruction',sum([d*f for d in Ds],s.zeros(4,1)),f);eq('weighted_energy_pythagoras',sum(energies),f.dot(W*f));eq('weighted_energy_value',sum(energies),13)
    reject('euclidean_symmetry_is_weighted_symmetry',E==E.T,'The conditional expectation is self-adjoint for W, not the unweighted dot product.')
    p=s.ones(4,1)/4;ell=M([4,1,1,1]);post,m,qs,evidence=posterior_packets(p,ell)
    eq('bayesian_posterior',post,M([4,1,1,1])/7);eq('bayesian_evidence',evidence,R(7,4));eq('packet_masses',m,M([R(5,7),R(2,7)]));eq('packet_reconstruction',sum([m[i]*qs[i] for i in range(2)],s.zeros(4,1)),post)
    eq('first_conditional_shape',qs[0],M([R(4,5),R(1,5),0,0]));eq('second_conditional_shape',qs[1],M([0,0,R(1,2),R(1,2)]))
    zero_post,zm,zq,_=posterior_packets(p,M([0,0,1,1]));eq('zero_evidence_packet_mass',zm[0],0);eq('zero_evidence_packet_vector',zq[0],s.zeros(4,1));eq('zero_packet_reconstruction',zm[1]*zq[1],zero_post)
    pa=M([R(1,2),0,R(1,2),0]);pb=M([0,R(1,2),R(1,2),0])
    eq('necessity_equal_coarse_priors',C*pa,C*pb);eq('necessity_first_posterior',C*bayes(pa,ell)[0],M([R(4,5),R(1,5)]));eq('necessity_second_posterior',C*bayes(pb,ell)[0],M([R(1,2),R(1,2)]))
    reject('same_coarse_prior_implies_same_coarse_posterior',C*bayes(pa,ell)[0]==C*bayes(pb,ell)[0],'Within-block likelihoods differ; the coarse prior lacks the necessary information.')
    P,r=coarse_effective(p,ell);eq('effective_likelihood',r,M([R(5,2),1]));eq('effective_likelihood_factorization',bayes(P,r)[0],C*post)
    declared=M([1,1]);bbar,zbar=bayes(P,declared);loss=(s.diag(*P)-bbar*P.T);delta=r-declared;direct=C*post-bbar
    eq('information_loss_factorization',loss*delta/evidence,direct);eq('information_loss_exact_vector',direct,M([R(3,14),-R(3,14)]));eq('information_loss_null_scale',loss*declared,s.zeros(2,1));eq('information_loss_total_mass_zero',sum(direct),0)
    check('information_loss_l1_bound',norm1(direct)<=2*sum(P[i]*abs(delta[i]) for i in range(2))/min(evidence,zbar))
    # All 35 denominator-four priors: includes zero-mass packets. Each item is exact.
    grid=[M([a,b,c,4-a-b-c])/4 for a in range(5) for b in range(5-a) for c in range(5-a-b)]
    constant=M([3,3,1,1]);records=[]
    for p0 in grid:
        P0,r0=coarse_effective(p0,ell);fine,z0=bayes(p0,ell)
        records.append(C*bayes(p0,constant)[0]==bayes(C*p0,[3,1])[0] and C*fine==bayes(P0,r0)[0])
    check('all_35_simplex_grid_priors',len(grid)==35 and all(records),'Finite exhaustive denominator-four grid, not the all-prior theorem.')
    ell2=M([1,2,3,4]);bp,z1=bayes(p,ell);bp2,z2=bayes(bp,ell2);both,zz=bayes(p,s.diag(*ell)*ell2)
    eq('independent_likelihood_composition',bp2,both);eq('evidence_product',z1*z2,zz);eq('likelihood_scale_invariance',bayes(p,7*ell)[0],post)
    # Explicit nonlinear two-state update and its flow.
    v=s.symbols('v',positive=True);eta=s.symbols('eta',positive=True);x=s.symbols('x',real=True)
    f3=3*x/(1+2*x);eq('bayes_jacobian_scalar',s.diff(f3,x),3/(1+2*x)**2)
    logistic=lambda a,p:a*p/(1+(a-1)*p)
    eq('bayes_nonlinear_semigroup',logistic(v,logistic(eta,x)),logistic(v*eta,x))
    flow=s.exp(t)/(1+s.exp(t));eq('replicator_derivative',s.diff(flow,t),flow*(1-flow))
    eq('replicator_time_log_two',flow.subs(t,s.log(2)),R(2,3))
    reject('bayes_is_affine',f3.subs(x,R(1,2))==(f3.subs(x,0)+f3.subs(x,1))/2,'Normalization changes mixtures: 3/4 is not 1/2.')
    zero_rejected=False
    try:bayes(M([1,0]),[0,1])
    except ValueError:zero_rejected=True
    check('zero_total_evidence_explicitly_rejected',zero_rejected)
    # HMM order and an exact two-level sequence.
    K2=M([[R(3,4),R(1,4)],[R(1,4),R(3,4)]]);l2=[1,R(1,2)];start=basis(2,0)
    eq('hmm_prediction_then_update',bayes(K2*start,l2)[0],M([R(6,7),R(1,7)]))
    reject('prediction_commutes_with_update',bayes(K2*start,l2)[0]==K2*bayes(start,l2)[0],'Conditioning belongs to a time step; the two operators do not commute.')
    rows,joint=filter_model();raw=basis(4,0)
    for i,row in enumerate(rows):
        eq(f'filter_coarse_reconstruction_{i}',C*row['posterior'],row['coarse']);eq(f'filter_evidence_reconstruction_{i}',row['z'],row['coarse_z']);eq(f'filter_probability_{i}',sum(row['posterior']),1)
        raw=s.diag(*row['likelihood'])*K*raw
    eq('filter_joint_evidence',joint,R(13,32));eq('filter_unnormalized_mass',sum(raw),joint);eq('filter_joint_normalization',raw/joint,rows[-1]['posterior']);eq('filter_final_posterior',rows[-1]['posterior'],M([41,15,40,8])/104);eq('filter_final_coarse',rows[-1]['coarse'],M([R(7,13),R(6,13)]))
    # Conjugacy uses elementary polynomial integrals.
    theta=s.symbols('theta',real=True);prior=12*theta*(1-theta)**2;lik=theta**2*(1-theta);posterior=140*theta**3*(1-theta)**3
    eq('beta_prior_normalized',s.integrate(prior,(theta,0,1)),1);eq('beta_ordered_evidence',s.integrate(prior*lik,(theta,0,1)),R(3,35));eq('beta_posterior_normalized',s.integrate(posterior,(theta,0,1)),1);eq('beta_polynomial_update',prior*lik/R(3,35),posterior);eq('beta_posterior_mean',s.integrate(theta*posterior,(theta,0,1)),R(1,2));eq('beta_binomial_evidence',s.binomial(3,2)*R(3,35),R(9,35))
    # Fractional functions of the actual four-state Laplacian.
    L=-Q;S=sum([s.sqrt(2*j)*Ps[j] for j in range(4)],s.zeros(4));eq('spectral_square_root_square',S*S,L);eq('spectral_square_root_zero_mode',S*s.ones(4,1),s.zeros(4,1));eq('new_long_range_entry',S[0,3],(s.sqrt(6)-s.sqrt(2)-2)/4)
    check('new_long_range_entry_negative',S[0,3]<0);reject('fractional_power_preserves_sparsity',S[0,3]==0,'The zero entry L[0,3] becomes nonzero in its positive square root.')
    eq('square_root_exact_coarsening',C*S,M([[1,-1],[-1,1]])*C)
    eq('scalar_fractional_defect',s.sqrt(9)-s.sqrt(4),1);check('common_gap_linear_bound',1<=R(1,2)*4**R(-1,2)*5)
    for n in [2,4,10,100]:eq(f'gapless_scalar_defect_{n}',s.sqrt(R(1,n*n)),R(1,n))
    # The Poisson-clock Jacobian reduces the scalar normalization to a Gaussian.
    a=s.symbols('a',positive=True);u=s.symbols('u',positive=True);ss=a*a/(4*u*u)
    density=a/(2*s.sqrt(s.pi))*s.Symbol('ss',positive=True)**R(-3,2)*s.exp(-a*a/(4*s.Symbol('ss',positive=True)))
    eq('poisson_clock_change_of_variable',density.subs(s.Symbol('ss',positive=True),ss)*(-s.diff(ss,u)),2*s.exp(-u*u)/s.sqrt(s.pi))
    eq('poisson_clock_normalization',s.integrate(2*s.exp(-u*u)/s.sqrt(s.pi),(u,0,s.oo)),1)
    # Dirichlet inverse and an exact nonzero mesh error.
    for n in [1,3,7,15]:
        h,T,Lh,xs,G=green(n);inv=Lh.inv();eq(f'green_inverse_{n}',Lh*(h*G),s.eye(n));eq(f'green_scaled_identity_{n}',inv/h,G)
        u0=M([x-x**4 for x in xs]);forcing=M([12*x*x for x in xs]);err=-h*h*M([x*(1-x) for x in xs])
        eq(f'quartic_residual_{n}',Lh*u0-forcing,2*h*h*s.ones(n,1));eq(f'quartic_solution_error_{n}',inv*forcing-u0,err);eq(f'quartic_error_max_{n}',max(abs(e) for e in err),h*h/4)
    h,T,Lh,xs,G=green(3);eq('green_display_matrix',Lh.inv(),M([[3,2,1],[2,4,2],[1,2,3]])/64)
    reject('raw_inverse_equals_continuum_kernel',Lh.inv()==G,'The grid quadrature factor h is essential.')
    # Exhaustive path sum, distinct from stochastic Monte Carlo.
    Kf,w,terminal,paths=fk_paths();back=s.diag(*w)*Kf.T;forward=Kf*s.diag(*w)
    eq('feynman_kac_path_probability',sum(a['probability'] for a in paths),1);eq('feynman_kac_path_sum',sum(a['contribution'] for a in paths),(back**3*terminal)[0]);eq('feynman_kac_forward_duality',terminal.dot(forward**3*basis(2,0)),(back**3*terminal)[0]);check('feynman_kac_exhaustive_path_count',len(paths)==8)
    reject('arrival_and_departure_weighting_agree',(Kf.T*s.diag(*w))**3*terminal==back**3*terminal,'Departure-state potential weighting fixes matrix order.')
    # Exact elimination and nonnormal memory.
    A=M([[-1,1],[1,-1]]);res=(z*s.eye(2)-A).inv();schur=z+1-1/(z+1)
    eq('schur_actual_inverse_entry',res[0,0],1/schur);eq('schur_partial_fractions',res[0,0],(1/z+1/(z+2))/2)
    retained=(1+s.exp(-2*t))/2;hidden=(1-s.exp(-2*t))/2
    eq('two_state_retained_ode',s.diff(retained,t),-retained+hidden);eq('two_state_hidden_ode',s.diff(hidden,t),retained-hidden);eq('memory_convolution',s.integrate(s.exp(-(t-u))*retained.subs(t,u),(u,0,t)),hidden)
    eq('memory_laplace',s.integrate(s.exp(-z*t)*s.exp(-t),(t,0,s.oo)),1/(z+1));eq('compression_nonsemigroup_defect',retained.subs(t,2*s.log(2))-retained.subs(t,s.log(2))**2,R(9,64))
    reject('retained_block_is_a_semigroup',retained.subs(t,2*s.log(2))==retained.subs(t,s.log(2))**2,'Excursions into the hidden packet return later.')
    N=M([[0,1],[0,0]]);J=-2*s.eye(2)+N;ET=s.exp(-2*t)*(s.eye(2)+t*N)
    eq('jordan_nilpotent',N*N,s.zeros(2));eq('jordan_exponential_ode',ET.diff(t),J*ET);eq('jordan_exponential_initial',ET.subs(t,0),s.eye(2));eq('jordan_memory_kernel',(M([[1,0]])*ET*M([0,1]))[0],t*s.exp(-2*t));eq('jordan_memory_laplace',s.integrate(s.exp(-z*t)*t*s.exp(-2*t),(t,0,s.oo)),1/(z+2)**2)
    eq('jordan_resolvent', (z*s.eye(2)-J).inv(),s.eye(2)/(z+2)+N/(z+2)**2)
    reject('eigenvalues_determine_nonnormal_exponential',ET==s.exp(-2*t)*s.eye(2),'The nilpotent Jordan part contributes t times exp(-2t).')
    # Erlang-two phase-type survival, including a zero initial hazard.
    T=M([[-1,0],[1,-1]]);trans=s.exp(-t)*M([1,t]);surv=(1+t)*s.exp(-t);density=t*s.exp(-t)
    eq('transient_ode',trans.diff(t),T*trans);eq('survival_sum',sum(trans),surv);eq('exit_density_derivative',-s.diff(surv,t),density);eq('hazard_formula',density/surv,t/(1+t));eq('survival_at_zero',surv.subs(t,0),1);eq('exit_probability',s.integrate(density,(t,0,s.oo)),1);eq('mean_exit_time',s.integrate(surv,(t,0,s.oo)),2);eq('exit_second_moment',s.integrate(t*t*density,(t,0,s.oo)),6)
    # Actual rectangular holomorphic/rational naturality with a Jordan component.
    Af=M([[2,1,0],[0,2,0],[0,0,9]]);Ac=Af[:2,:2];Cr=M([[1,0,0],[0,1,0]])
    eq('rectangular_generator_intertwining',Cr*Af,Ac*Cr);eq('rectangular_polynomial_naturality',Cr*Af**3,Ac**3*Cr);eq('rectangular_rational_naturality',Cr*(s.eye(3)+Af).inv(),(s.eye(2)+Ac).inv()*Cr)
    eq('jordan_function_derivative_term',(s.eye(2)+Ac).inv(),s.eye(2)/3-N/9)
    reject('holomorphic_calculus_only_uses_values',(s.eye(2)+Ac).inv()==s.eye(2)/3,'The derivative at a repeated eigenvalue acts on its Jordan direction.')
    # Refinement norms: explicitly independent scalar pairs, not a fabricated coherent tower.
    for n in [1,2,3,4,8,16]:
        eq(f'gapless_square_root_norm_{n}',s.sqrt(R(1,n*n)),R(1,n))
        check(f'gapped_square_root_linear_bound_{n}',s.sqrt(1+R(1,n*n))-1<=R(1,2*n*n))
    report={'status':'PASS','scope':'Exact finite examples and symbolic identities. Not a Lean replay or a continuum existence proof.','checks_passed':len(checks),'checks':checks,'invalid_controls_rejected':controls,'finite_families':{'simplex_grid_denominator':4,'simplex_grid_size':35,'feynman_kac_horizon':3,'feynman_kac_paths':8,'green_interior_sizes':[1,3,7,15],'defect_horizons':list(range(9))},'plotting_boundary':'Plots are sampled vector drawings of declared exact functions. Numerical coordinates are not accepted as exact proof evidence.','python_version':platform.python_version(),'sympy_version':s.__version__,'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'source/models.py',Path(__file__)]},'computed_values':{'weighted_energies':[str(x) for x in energies],'filter_evidences':[str(x['z']) for x in rows],'filter_joint_evidence':str(joint),'feynman_kac_value':str(sum(a['contribution'] for a in paths))}}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(checks)} exact checks; {len(controls)} false controls rejected.');print(json.dumps(report['computed_values'],indent=2))
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as e:raise SystemExit(str(e)) from e
