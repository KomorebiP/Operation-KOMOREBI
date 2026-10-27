"""Inventory immutable sources; this script does not validate mathematical truth."""
from pathlib import Path
import collections, hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
KINDS = "theorem|lemma|proposition|corollary|standardfact|definition|example|remark"
PATTERN = re.compile(r"\\begin\{(" + KINDS + r")\}(?:\[([^\]]*)\])?")
KEEP = set('''cor:minimum_transfer_order thm:multilevel_telescoping cor:summable_defects thm:projective_limit_semigroup cor:projective_generators thm:reversibility_descends cor:coarse_dirichlet_form prop:relative_sufficiency lem:normalization_bound thm:information_loss cor:bayes_oscillation cor:bayesian_covariance thm:exact_coarse_filter thm:filter_defect thm:feynman_kac_potential_bound thm:coarse_feynman_kac thm:rational_memory_realization cor:exponential_sum_memory cor:phase_type_rationality cor:one_phase_model'''.split())

NOTES = {
'thm:packet_convolution':'Norm absolutely convergent exponential Cauchy product; finite resolution of identity inserted. The group parameter is real; uniform continuity is the conventional norm-continuity-at-zero property.',
'prop:block_differential':'Differentiate norm series; both block products follow by the finite resolution. Initial off-diagonal blocks vanish.',
'thm:laplace_packet_resolvent':'Re z > ||A|| ensures integrability and decay. Integration of the norm derivative gives both inverse identities, then bounded multiplication commutes with Bochner integration.',
'cor:resolvent_packet_paths':'Order checked: zI-A=(zI-D)(I-R_D N), so inverse is (I-R_D N)^(-1)R_D. The condition presupposes z in the resolvent set of D.',
'thm:reducing_packets':'Commutation iff off-diagonal generator blocks vanish; differentiation at zero supplies necessity. All packets invariant gives block diagonal powers. Restrictions are operators on packet ranges.',
'thm:dyson_paths':'Variation of constants iterated in correct order. Simplex volume t^m/m! and norm bound exp(t||D||)||N||^m yield absolute convergence.',
'cor:acyclic_termination':'Each surviving term induces m edges; no path exceeds longest acyclic path. Length-zero paths supply diagonal terms.',
'thm:duhamel_defect':'Derivative of exp((t-s)A_c) C exp(sA_f) gives +Delta with correct types; both endpoint terms and growth factors checked.',
'prop:infinitesimal_defect':'Norm Taylor expansion yields Delta; converse follows from Duhamel. No unbounded-generator extension is inferred.',
'thm:resolvent_defect':'Left multiplication by zI-A_c and right multiplication by zI-A_f reduce both sides to Delta. Rectangular C permitted.',
'thm:holomorphic_defect':'Raw contour statement requires correction: arbitrary enclosing curves can have winding two. Common resolvent and winding one are necessary for the Dunford representation.',
'cor:exact_naturality':'Set Delta=0 in the corrected admissible-contour formula; exponentials and polynomials are entire and resolvents use holomorphic neighborhoods avoiding their pole.',
'lem:inverse_limit_banach':'The bounded product is Banach; each individual compatibility equation is closed even without a uniform bound on connecting-map norms.',
'thm:exact_projective_limit':'Growth bound preserves bounded coordinates; compatibility preserves inverse limit. Strong continuity needs the stated uniform-in-level condition. Uniformly bounded compatible generators satisfy it and define a bounded generator.',
'thm:summable_defect_completion':'Exact difference is C_(m,n) E_n R_n R_(n,m). Weighted summability yields uniform operator-norm Cauchy convergence and tail bound. It does not prove a semigroup law.',
'cor:contractive_defect_completion':'Every reconstruction/coarsening product has norm at most one, so each weight is at most one.',
'cor:generator_defect_completion':'Adjacent contraction Duhamel estimate is t||Delta_n||; sum gives T times tail on [0,T]. No uniform generator-norm bound is required for this estimate.',
'thm:asymptotic_closure':'Finite semigroup defect equals C T(s)(P-I)T(t)R. Limits on [0,2T] give law. C_(m,n)R_(n,m)=I gives U_m(0)=I. Norm continuity is conditional on the explicitly stated level norm continuity.',
'prop:range_leakage':'Drop contraction factors C_(m,n)T_n(s). Vanishing reconstructed-range leakage implies vanishing closure defect.',
'thm:generator_range_leakage':'Solve hidden equation driven by retained component. Two factors ||P|| arise when input x=P y and retained part is bounded. Orthogonal case has ||P||≤1. Bounded A scope must stay explicit.',
'cor:generator_closure_tower':'Orthogonal compression preserves dissipativity, hence its bounded exponential is contractive by differentiating squared norm. ||R_(n,m)||≤1 then controls leakage.',
'thm:finite_markov':'Shift by aI makes generator entrywise nonnegative. Exponential positivity and left conservation 1^TQ=0 establish column stochasticity.',
'thm:canonical_lumping_obstruction':'Surjective quotient descent exists iff CK vanishes on ker C. Formula CKR is independent of R only when obstruction vanishes; raw defect formula is valid for arbitrary R.',
'cor:lumping_obstruction_coordinates':'Each block-sum-zero subspace is spanned by within-block basis differences. Applying CK gives the stated aggregated column differences.',
'thm:lumping_characterization':'Column-by-column condition necessary and sufficient. Nonnegative aggregate entries and total column sum one preserve stochasticity.',
'cor:continuous_lumping':'Off-block aggregate rates are nonnegative; total coarse column sum zero. Bounded generator power series gives exact exponential intertwining.',
'thm:finite_horizon_lumping':'Correct telescoping order checked, including n=0 empty sum. Stochastic l1 operator norms are one; TV equals half l1.',
'cor:stationary_descends':'Apply CK=Kbar C to Kp=p. No converse or uniqueness of stationary laws asserted.',
'thm:finite_conditional_expectation':'Strictly positive pi prevents zero denominators. Weighted inner-product calculation establishes self-adjointness and blockwise idempotence.',
'thm:martingale_packets':'Nested orthogonal projections commute with product P_min. Differences are orthogonal idempotents, sum to P_r, and give Pythagorean energy.',
'cor:total_variance':'Subtract global mean, then split into range P_Q and its orthogonal complement. Real-valued scope is explicit.',
'thm:ou_semigroup':'Gaussian composition, Jensen and exchangeability give semigroup/contraction/self-adjointness; generating function gives eigenvalues and orthogonality. Polynomial density in Gaussian L2 is imported background, not established in this source. L-infinity strong continuity is not asserted.',
'cor:hermite_packets':'Parseval and diagonal action yield strong reconstruction and energy, conditional on the Hermite-basis input. No operator-norm convergence of identity resolution is asserted.',
'prop:ou_generator':'For polynomials, finite Taylor expansion can be integrated coefficientwise; Gaussian odd moments vanish and higher surviving terms are o(t). Integration by parts gives stated Dirichlet form.',
'cor:ou_spectral_gap':'Mean-zero coefficients begin at n=1; exp(-nt)≤exp(-t). Polynomial energy sum weights n≥1. Depends on complete Hermite basis.',
'cor:fractional_hermite':'Diagonal nonnegative self-adjoint number operator defines fractional semigroup for any alpha>0. Claim is an L2 contraction, not positivity for alpha>1.',
'prop:bayes_composition':'Positive evidences ensure denominators nonzero; likelihood scaling and sequential normalizers cancel.',
'thm:bayesian_packet_reconstruction':'Each nonzero packet evidence contributes exactly lambda_i p_i/Z. Zero-evidence packets have zero posterior mass and need no conditional shape.',
'thm:likelihood_perturbation':'Both numerator perturbation and evidence perturbation are bounded by weighted absolute difference. Swap likelihoods and take smaller bound, producing max evidence in denominator.',
'thm:prior_stability':'Evidence≥a>0 and numerator/evidence perturbations each ≤b||p-q||1; factor2b/a is valid though not claimed sharp.',
'thm:two_stage_bayes':'Split p into block mass and positive conditional prior; packet evidences factor and local formula follows. Zero-evidence packets are explicitly excluded from conditionals.',
'thm:bayesian_sufficiency':'Definition includes preservation of every within-packet conditional, so single-block case also forces constant likelihood. Positivity allows cancellation; coarse likelihood unique only up to common scale. This differs from mass-only sufficiency in the formal core.',
'thm:coarsest_bayesian_partition':'Block constancy for every likelihood is equivalent to refining common level sets. Holds even for a single common class under the stronger conditional-preservation definition.',
'prop:local_bayes_distortion':'Subtract local normalized prior; absolute deviations average to exact l1 error. Average likelihood bounded below by packet minimum.',
'thm:approximate_coarse_bayes':'Aggregation is l1-contractive; block-constant surrogate likelihood commutes with aggregation. Positive evidence for original update remains required by section setup.',
'thm:bayesian_information_chain':'Finite relative-entropy chain rule by p_i=m_alpha p_alpha,i and q_i=n_alpha q_alpha,i. Restrict logarithmic algebra to q_i>0; null terms follow by convention. q<<p ensures needed conditionals exist.',
'cor:coarse_data_processing':'Conditional KL≥0, with equality exactly equal conditional distributions, yields statement. Gibbs inequality is ordinary background; no parametric statistical sufficiency inferred.',
'cor:bayesian_information_gain':'Insert posterior/prior ratios. Both lambda and its packet average lie between positive min and max, yielding logarithmic bound.',
'cor:information_sufficiency':'All positive packets have positive posterior mass, so vanishing conditional KL gives equal local distributions and forces likelihood constancy.',
'thm:bayesian_flow':'Multiplying exponential likelihoods gives nonlinear semigroup. Quotient derivative, support preservation, and exact posterior odds agree.',
'thm:evidence_cumulants':'Twice differentiate finite log sum to get mean then centered second moment; derivative of score mean is variance.',
'cor:bayes_flow_concentration':'Factor maximum supported score. The supported maximum packet has positive initial mass; outside weight is ≤(1-p_M)exp(-delta t). Full-support-max case is separately acknowledged.',
'prop:hmm_preservation':'Column stochastic prediction followed by positive-evidence normalization preserves simplex.',
'thm:hmm_stability':'Insert stochastic contraction estimate ||Kp-Ktilde q||1≤||p-q||1+||K-Ktilde||1 and apply prior-stability constant.',
'thm:fractional_packet_calculus':'All operations diagonal on a finite positive self-adjoint spectral decomposition; zero eigenvalues allowed for positive alpha,beta.',
'thm:balakrishnan':'Reduce to scalar beta integral with 0<alpha<1. Zero eigenvalue contributes zero, and finite sum permits norm integral. Scalar Euler beta/reflection identity is imported elementary analytic background.',
'thm:exact_fractional_naturality':'One polynomial interpolates each scalar function on the finite union of spectra, so rectangular intertwining passes to it without a gap assumption.',
'thm:fractional_defect':'Sign checked: C R_f-R_c C=−R_c Delta_L R_f; L R=I−sR gives positive sR_c Delta_L R_f. Resolvent bound (s+m)^−1 and beta integral yield alpha m^(alpha−1). Duhamel generators are −L^alpha.',
'thm:poisson_subordination':'Scalar Gaussian identity gives kernel t/(2sqrt(pi)) s^(−3/2) exp(−t²/(4s)); t>0 controls origin and s^(−3/2) controls infinity, including zero spectral mode.',
'thm:nodal_green':'Discrete inverse entries equal min(i,j)(n+1-max(i,j))/(n+1). Scaling h² then dividing by h yields min(x_i,x_j)−x_i x_j. n≥1 implicit interior-node setting.',
'cor:discrete_green_quadrature':'Multiply exact inverse entries hG(x_i,x_j) by arbitrary nodal source. This is an exact discrete representation, not a continuum error assertion.',
'prop:discrete_inverse_bound':'Nonnegative inverse makes infinity norm max row sum. Quadratic barrier v_i=x_i(1-x_i)/2 solves L_h v=1 and max≤1/8.',
'thm:poisson_error':'C4 consistency error≤h²||D4u||∞/12 multiplied by inverse norm≤1/8 gives h²/96. Dirichlet endpoints used.',
'thm:low_mode':'With x=k*pi*h/2 in [0,pi/2], x−x³/6≥0 and sin x≥that expression. Squaring yields x²−sin²x≤x⁴/3. Physical modes have 1≤k≤n.',
'cor:mode_transfer':'Mean-value estimate for heat exponentials gives t(delta lambda)exp(-t lambda_h). Fixed k ensures positive common interval for fractional derivatives; no uniform-in-all-modes claim.',
'thm:discrete_feynman_kac':'K is column stochastic, so functions use K^T. Potential is applied at X_0,...,X_(n−1), terminal f at X_n; multiplication order matches.',
'thm:continuous_feynman_kac':'Finite-state conditioning produces generator Q^T−D_V and unique matrix ODE solution. Real V bounded automatically in finite state, with supnorm bound for V≥v0.',
'thm:feynman_kac_product':'Each one-step product differs from I+t(B+C)/n by O(n^−2); bounded product norms give O(n^−1) telescoping error. Order exp(B)exp(C) matches backward weighting.',
'cor:feynman_kac_semigroup':'Expectation gives positivity; time-homogeneous matrix exponential gives composition.',
'thm:feshbach_resolvent':'Block product L_z S_z gives correct off-diagonal minus signs and retained block zI−A_PP. Triangular inversion establishes compressed resolvent. P-resolvent-P is identified with restriction to X_P.',
'thm:memory_self_energy':'Raw decay claim lacks gamma>0. Spectral half-plane Laplace identity for bounded Banach hidden operator requires spectral/growth argument, now supplied to editor and checked against Engel-Nagel IV.3.12(iv).',
'thm:local_closure':'Resolvent equality, Laplace uniqueness and memory-zero equivalent in bounded setting; finite first-d-moment criterion uses Cayley-Hamilton and requires dim X_Q=d<infinity explicit.',
'thm:modal_memory':'Primary projections commute with A; nilpotent exponential and resolvent expansions have coefficients B_j,k/k! and pole order k+1. Integral of exp(Re mu t)t^k/k! is (−Re mu)^−k−1. Whole primary blocks retained; nonnormal projections need not be orthogonal.',
'cor:optimal_primary_selection':'Exchange argument minimizes omitted nonnegative weight sum for a fixed number of whole primary blocks. It does not optimize actual L1 error, retained dimension, or real conjugate-pair constraints.',
'cor:normal_modal_memory':'Normal finite operator has zero nilpotent parts and orthogonal spectral projections; specialize general modal result.',
'cor:pole_jordan_depth':'Principal parts at distinct poles cannot cancel across eigenvalues. Highest nonzero coefficient determines pole order; zero highest coefficient permits lower order.',
'cor:finite_auxiliary_realization':'Variation of constants for y with y(0)=0 gives convolution. Nonzero initial hidden state gives explicit forcing; no stability asserted.',
'thm:volterra_compression':'Subtract mild equations, use K*(x−xtilde)+(K−Ktilde)*xtilde. Fubini yields M_T L integral E plus M_T B t epsilon; bound t≤T and apply Gronwall. Requires ordinary continuous mild solutions / well-defined Bochner integrals.',
'cor:modal_trajectory_bound':'Insert whole-block L1 certificate into Volterra estimate with same initial state/forcing and comparison-trajectory bound B.',
'thm:killing_survival':'Transpose backward expectation then differentiate mass. Arbitrary V≥0 yields a substochastic killed chain, not necessarily transient or eventually absorbed; V=0 is boundary counterexample to wording.',
'thm:survival_hazard':'Metzler positivity and nonpositive column sums yield nonnegative density and nonincreasing survival. A finite conservative survivor can have nonzero limiting mass; proper absorption is not automatic.',
'thm:survival_moments':'Explicit strict spectral stability ensures integrability and mass one. a^T=1^T(-A) cancels one inverse power, giving m!1^T(-A)^−m p0.',
'prop:residual_life':'Divide positive surviving mass; semigroup law gives restarted conditional law. No memorylessness of scalar survival is inferred.',
'thm:competing_risks':'Finite-time sums need only nonnegative cause rows. Inverse formula for eventual masses requires strict spectral stability, absent from displayed theorem; A=0 shows inverse can fail.',
}

EARLIER_NOTES = {
'cor:minimum_transfer_order':'Dyson simplex tail starts at minimal directed path length; include trivial length-zero path for alpha=beta.',
'thm:multilevel_telescoping':'Expand C_(ell,j)E_j C_(j+1,m); all intermediate terms cancel with correct order and level types.',
'cor:summable_defects':'Contraction Duhamel bound t*delta_j and product contractions give multilevel tail; ell→infinity tail uniform over m>ell and bounded t.',
'thm:projective_limit_semigroup':'Product topology requires only coordinate continuity; exact intertwining preserves compatible sequences. Connecting maps should be bounded linear so the projective limit is a locally convex vector space.',
'cor:projective_generators':'Coordinatewise difference quotients converge in product topology and compatible derivative sequence lies in the limit; no supremum-norm or unbounded-generation claim.',
'thm:reversibility_descends':'Column convention detailed balance Q_ij*pi_j=Q_ji*pi_i; aggregate double sums prove coarse balance and stationarity.',
'cor:coarse_dirichlet_form':'J=C^T, Q^T J=J Qbar^T, and weighted inner products match because each coarse weight is the sum of fine pi.',
'prop:relative_sufficiency':'Declared fixed conditionals r^(a) make block evidence q_a times its r-average likelihood, hence mass-only exact coarse update for this prior family.',
'lem:normalization_bound':'Both normalization denominators give bounds; their minimum is denominator max(A,B). Nonnegative nonzero inputs ensure denominators positive.',
'thm:information_loss':'Exact effective block likelihood and normalization lemma bound the mass defect. Zero-mass blocks contribute zero and their finite likelihood value is irrelevant.',
'cor:bayes_oscillation':'Conditional mean belongs to convex hull, hence difference from representative≤max pointwise deviation; multiply by block masses.',
'cor:bayesian_covariance':'Differentiate fixed-observable expectation along replicator equation; finite sum gives Cov(h,g).',
'thm:exact_coarse_filter':'Prediction commutes by lumpability; update commutes by block-constant positive observation likelihood; induction gives full recursion.',
'thm:filter_defect':'Insert B_Lbar(CKp). Exact effective-likelihood error plus prior Lipschitz bound controls separate observation and dynamic defects.',
'thm:feynman_kac_potential_bound':'Nonnegative potentials give supnorm contractions; Duhamel with defect W−V yields t||V−W||∞.',
'thm:coarse_feynman_kac':'Transpose CQ=Qbar C, combine VJ=J Vbar, then power-series intertwining. Distinguish functions/backward from mass/forward convention.',
'thm:rational_memory_realization':'Partial fraction Jordan-block realization is valid over complex finite matrices. Pointwise kernel equivalence requires continuous exponential-order kernels; L1-local kernels yield equality a.e. after Laplace uniqueness.',
'cor:exponential_sum_memory':'Direct-sum realization has blocks lambda_j I_(d_j), where B_j,C_j factor through dimension d_j; repeated poles require Jordan blocks. Literal scalar blocks would be dimensionally inadequate for matrix coefficients.',
'cor:phase_type_rationality':'Stable finite subgenerator gives proper phase law, rational resolvent, and Jordan polynomial-exponential terms.',
'cor:one_phase_model':'Inherited transience requires lambda>0; explicit scalar formulas then follow with initial mass one.',
}

ISSUES = {
'thm:holomorphic_defect':'F1', 'thm:memory_self_energy':'F2,F3',
'thm:local_closure':'F4','thm:killing_survival':'F5','thm:competing_risks':'F6',
}

def sha(data): return hashlib.sha256(data).hexdigest()

def inventory(edition):
    source = next((ROOT/'source'/edition).glob('*.tex'))
    data = source.read_bytes(); text = data.decode()
    records = []
    for n,match in enumerate(PATTERN.finditer(text),1):
        kind,title = match.groups()
        stop = text.index('\\end{'+kind+'}',match.end()) + len('\\end{'+kind+'}')
        block = text[match.start():stop]
        labels = re.findall(r'\\label\{([^}]+)\}',block)
        label = labels[0] if labels else f'{edition}:{kind}:{n}'
        after = text[stop:]
        pm = re.match(r'\s*\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',after,re.S)
        proof = pm.group(0).strip() if pm else None
        headings = list(re.finditer(r'\\section\{([^}]+)\}',text[:match.start()]))
        section = headings[-1].group(1) if headings else None
        references = []
        for rr in re.findall(r'\\[cC]?ref\{([^}]+)\}',block+'\n'+(proof or '')):
            references.extend(rr.split(','))
        rec = {'ordinal':n,'kind':kind,'title':title,'label':label,'section':section,
          'source':str(source.relative_to(ROOT)),'line_start':text[:match.start()].count('\n')+1,
          'line_end':text[:stop].count('\n')+1,'statement_sha256':sha(block.encode()),
          'proof_sha256':sha(proof.encode()) if proof else None,'proof_present':bool(proof),
          'internal_references':references,'statement_tex':block,'proof_tex':proof}
        if edition=='strengthened':
            rec['review_scope']='statement and local written proof' if proof else 'definition/example/remark/background classification'
            rec['obligation_status']='failed as fully stated; restriction/clarification requested' if label in ISSUES else ('conditional external input' if kind=='standardfact' else 'passed at manuscript review level')
            rec['finding_ids']=ISSUES.get(label,'').split(',') if label in ISSUES else []
            rec['review_note']=NOTES.get(label,'Imported background retained as such; exact external theorem not independently authenticated in this audit.' if kind=='standardfact' else 'Context, definition, example, or scope remark read; not counted as a proved result.')
        elif label in KEEP or kind=='example':
            rec['review_scope']='earlier-only record selected for retained supplement'
            rec['obligation_status']='passed with setup clarifications recorded in audit'
            rec['review_note']=EARLIER_NOTES.get(label,'Example directly recomputed from the displayed finite model; original hypotheses retained.')
        else:
            rec['review_scope']='inventory/comparison only; not an additional full earlier-article audit'
            rec['obligation_status']='not addressed independently in earlier source'
        records.append(rec)
    result={'edition':edition,'source':str(source.relative_to(ROOT)),'source_sha256':sha(data),
      'inventory_method':'Regex on raw TeX theorem-like environments; immediate proof environment association; not a TeX parser or mathematical verifier.',
      'environment_counts':dict(collections.Counter(r['kind'] for r in records)),
      'proof_environment_count':len(re.findall(r'\\begin\{proof\}',text)),
      'attached_proof_count':sum(r['proof_present'] for r in records),
      'record_count':len(records),'records':records}
    (OUT/(edition.upper()+'_SOURCE_INVENTORY.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    for edition in ('strengthened','annals'):
        res=inventory(edition)
        print(edition,res['record_count'],res['proof_environment_count'],res['source_sha256'])
