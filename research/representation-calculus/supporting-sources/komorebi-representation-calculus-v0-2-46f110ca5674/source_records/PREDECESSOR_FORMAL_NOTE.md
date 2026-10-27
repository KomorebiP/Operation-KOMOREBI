# A task-indexed, proof-carrying calculus of representation

## Status, lineage, and objective

This is a new conceptual research branch, not a replacement for the p-adic checkpoint and not a claimed Block 16. It formalizes the proposed machine-native interpretation of Komorebi using precise definitions, written propositions, a finite reference implementation, and falsifiable research targets.

The new propositions below are written and self-reviewed. No new Lean build was run. They draw on standard observational semantics, module theory, commuting diagrams, finite refinement, and first-order polynomial lifting. No historical-novelty claim is made for these ingredients. The proposed contribution is their integration into a representation-discovery architecture, whose empirical value is not yet demonstrated.

The inspected project anchor is Block 15's exact projector closure and strict orbit/envelope distinction. Its retained theorem and coverage notes are copied verbatim into source_records. Their historical Lean status is reported by those records, not newly authenticated by this branch. Earlier operator-symbolic language drafts already discuss typed transformations, observational quotients, proofs and provenance. This note sharpens rather than claims to originate that direction.

**Target thesis.** A machine-native calculus should make the discovery, comparison, compression, repair, and certification of representations into explicit mathematical operations. It should not promise one universal normal form or a decision procedure for arbitrary mathematics.

## 1. Representation profiles

A preservation profile is

\[
\Pi=(R,\Sigma,\Omega,\mathcal F,\mathcal S),
\]

where R is the coefficient regime, Sigma the allowed operation signature, Omega the required observations, F a precision/error filtration if present, and S the required structural properties. For example, S can demand integer linearity, exact reconstruction, continuity, or preservation of a designated lattice.

In the linear deterministic stratum, a represented system consists of an R-module H, maps T_a:H->H for a in Sigma, admissible initial data, and linear observations o_j:H->R. A one-seed machine has an initial x0. Its reachable module is the R-span of T_w x0 for finite words w. If the intended task allows arbitrary initial states, that interface must be stated instead; the finite quotient experiment below uses all 64 states as admissible initial states.

For a word w=a1...an read left to right, T_w=T_an ... T_a1. The empty word acts as the identity. Define

\[
\operatorname{Beh}_{\Pi}(x)(w,j)=o_j(T_w x).
\]

The nonlinear extension replaces linear observations and modules with typed states and admissible contexts. For multi-input operations one needs all well-typed observation contexts, not just unary words. This note proves its core statements in the linear unary stratum; it does not assert that every other stratum reduces to that stratum.

A representation may be adequate for one profile and invalid for another. A real approximation is not an exact integer representation. A finite coefficient prefix is not an all-index object. An invariant overapproximation is not a reachable-state equality.

## 2. The exact observable quotient

Define

\[
N_\Pi=\bigcap_{w,j}\ker(o_jT_w).
\]

**Proposition Q1.** N_Pi is the largest invariant submodule contained in the common observation kernel. The quotient Q_Pi=H/N_Pi has well-defined induced actions and observations and preserves every allowed future observation.

**Proof.** N_Pi is an intersection of submodules. If x is in N_Pi, then o_j T_w T_a x=0 for all w,j because a followed by w is an allowed word. Hence T_a x lies in N_Pi. Every observation vanishes on N_Pi by taking the empty word, so it descends. If K is invariant and every observation vanishes on K, then every word image of K stays in K, and every o_j T_w vanishes on K. Thus K is contained in N_Pi. Quotient well-definedness and exact behavior preservation follow. End proof.

**Proposition Q2: universal sufficiency.** Let q:H->Q be a surjective R-linear encoding with induced actions and observations such that q T_a=S_a q and o_j=o'_j q. Then ker(q) is contained in N_Pi and there is a unique R-linear map h:Q->H/N_Pi satisfying h q=the quotient map. It intertwines the actions and observations.

**Proof.** If qx=0, induction on words gives qT_w x=S_w qx=0, and hence o_jT_w x=0. Define h(qx)=[x]; the kernel inclusion makes it well-defined. Surjectivity gives uniqueness. Intertwining follows on each qx. End proof.

The quotient is intrinsic up to the appropriate canonical isomorphism. A basis, sparse realization, or proof-efficient presentation of it is not unique. Compression can preserve observations while losing the ability to reconstruct the original state.

For one-seed all-word behavior over R=Z/p^rZ, if its intrinsic behavior module B is finitely generated, its minimum free linear coordinate count is mu_R(B). The upper bound chooses generators and lifts actions through the free synthesis. For the lower bound, the reachable submodule U of any competing R^d machine maps onto B. Every submodule of R^d has at most d generators over this finite chain ring, by Smith theory or by lifting to an integer lattice. Thus mu_R(B)<=d. The coefficient-ring condition is load-bearing: submodules of a free rank-one module over a general ring can require more than one generator.

This is a precise model-relative minimality statement. It is not a lower bound for arbitrary algorithms, neural networks, Kolmogorov complexity, or every possible notion of memory.

## 3. Two directions of refinement

**Proposition Q3.** On a fixed ambient system, enlarging the permitted operation alphabet or observation family makes N_Pi smaller or equal. Enlarging the operation alphabet makes the reachable module generated from fixed initial data larger or equal.

**Proof.** The first assertion intersects a larger family of kernels. The second takes a span over a larger word set. End proof.

These are two distinct closure directions. A new semantic operation can both expose previously hidden information and make new states reachable. It cannot be silently registered as though it were merely an implementation detail.

At finite precision r and observation horizon L, one can define x~_(r,L)y by agreement modulo p^r for all words of length at most L. This is generally not stable under an additional transition: a word of length L+1 may distinguish the states. It becomes an all-word quotient only after a closure/stability proof. If the observation codomain is p-adically separated, agreement at every r,L implies exact agreement. No computable uniform termination claim follows in the infinite setting.

### Exact finite refinement

For a finite complete transition system, begin with equality of current observations and repeatedly refine each state's class by the tuple of successor classes. Each strict step increases the number of classes, so at most |X|-1 strict steps are possible. At a fixed point, equal classes have equal outputs and class-equal successors. Induction proves equality of outputs for every word. Conversely, states equal for all words cannot be separated by any refinement step. Thus the stable partition is exactly all-word observational equivalence.

The reference experiment uses (x,y,z) in (Z/4Z)^3, observes x, and permits T(x,y,z)=(x+y,y,z). Current-output classes number four; the exact future-output classes number sixteen and are indexed by (x,y). Adding S(x,y,z)=(z,y,x) makes all sixty-four states distinguishable. This experiment is finite and exhaustive over the declared state space. It is not an AI benchmark or a proof that an arbitrary unknown object has been learned.

## 4. Typed representation changes

The proposed intermediate language distinguishes at least these morphism classes:

| Morphism | Required contract |
|---|---|
| Exact isomorphism | Two inverses and preserved operations/observations/declared structure |
| Observational quotient | Exact output preservation and action descent; state inversion need not exist |
| Sound enclosure | Inclusion or sound concretization relation; reverse reachability not implied |
| Precision reduction | Exact relation between declared moduli and operations |
| Approximate transport | Explicit residual and a proved accumulated error bound |
| Completion | Defined topology, compatible finite maps, existence and uniqueness obligations |

An implementation pass is a theorem-backed constructor. It records coefficient regime, source and target semantics, preconditions, proof obligations, scope of equality, precision, cost model, and dependencies. An enclosure must not be inserted into an equality-only e-class. A conjectured bridge must not be promoted to a theorem edge because a finite test passed.

For same-ring linear systems A,B with action maps A_a,B_a, define the residual of q:A->B by

\[
\Delta_a(q)=qA_a-B_aq.
\]

**Proposition T1: residual composition.** If v:B->C, then

\[
\Delta_a(vq)=v\Delta_a(q)+\Delta_a(v)q.
\]

**Proof.** Expand both terms on the right; -vB_aq and +vB_aq cancel. End proof.

Thus exact intertwiners compose. In a normed stratum,

\[
\|\Delta_a(vq)\|\le\|v\|\|\Delta_a(q)\|+
\|\Delta_a(v)\|\|q\|.
\]

A local residual estimate alone does not prove a long-word error bound without further bounds on products of the transition operators. Exact initial-state and output contracts plus exact intertwining imply all-word output preservation by induction. Across coefficient rings, replace linearity with an explicitly specified semilinear/base-change interface.

## 5. Projectors are not free semantic operations

Block 15 supplies a concrete warning. Its actual binary-three-color orbit H is properly contained in the least module E closed under both digits and all coefficient projectors. It proves

\[
\psi(P)=16[x^4]P+[x^6]P\equiv0\pmod{64}
\quad\text{for every }P\in H,
\]

while 32x^6 is in E and violates the relation. These are polynomial coordinates after factoring out the seed; they are not consecutive raw partition coefficients.

Internal coordinate extraction is allowed as an analysis step if synthesis and every required compatibility condition are retained. It does not imply that applying the same projector is an admissible semantic action on H.

**Proposition I1: certified constraint refinement.** Suppose H is generated from x0 by Sigma in an invariant envelope E. Let psi:E->C be linear, with psi(x0)=0 and psi T_a=U_a psi for some maps U_a on C. Then H is contained in ker(psi). Therefore E'=E intersect ker(psi) is a smaller invariant envelope containing H.

**Proof.** The commutation equation implies invariance of ker(psi). It contains x0, so it contains all word images and their span. End proof.

In the Block15 example, U_a=0 works modulo 64. At precision six the normalized envelope has degrees 0,2,3,4,5,6 and weights 0,0,0,1,4,5. The relation becomes a4+a6=0 modulo two.

The finite reference search enumerates all 64 F2-linear predicates on those six normalized coordinates. Requiring a predicate to kill the seed and both full digit images yields exactly the zero predicate and (0,0,0,1,0,1). The search receives the action matrices, not the desired relation. The matrices are independently computed from a binomial formula, not imported from the preceding compiler. This is a reproducible rediscovery of a known project invariant, not a novel result or learned autonomous discovery claim.

A cut that removes one spurious state is not thereby a complete orbit classification. Equality with the reduced envelope requires a reverse inclusion, explicit generators, or another completeness certificate.

## 6. Residuals and obstructions must be distinguished

A residual says a chosen construction failed an equation. An obstruction says no permitted correction can fix it. These are not interchangeable.

For a linear correction problem J delta=-c, the obstruction is the class [c] in coker(J). This quotient removes the dependence on which preliminary representative produced the residual.

### A fully specified polynomial lifting interface

Let p be prime, r>=1, and f:Z^n->Z^m a tuple of integer polynomials. Let x_r solve f=0 modulo p^r, choose an integer representative x, and put

\[
c_r=f(x)/p^r\pmod p,\qquad J=Df(x)\pmod p.
\]

**Proposition O1.** A lift of x_r to a solution modulo p^(r+1) exists if and only if

\[
[c_r]=0\quad\text{in }\operatorname{coker}(J).
\]

If a lift exists, its correction set is an affine translate of ker(J). It has p^(n-rank J) elements. The obstruction class is independent of the integer representative x.

**Proof.** Every lift has the unique form x+p^r delta modulo p^(r+1), with delta in F_p^n. Expanding each polynomial, all terms quadratic in the correction contain p^(2r), divisible by p^(r+1). Therefore

\[
f(x+p^r\delta)/p^r\equiv c_r+J\delta\pmod p.
\]

Solvability is exactly membership of -c_r in image(J). Its solutions form an affine kernel coset. Replacing x by x+p^r eta changes c_r to c_r+J eta and leaves J modulo p unchanged. The cokernel class is therefore independent of that choice. End proof.

If the obstruction is nonzero, finite-dimensional duality supplies a row functional lambda with lambda J=0 and lambda c_r!=0. This is a compact certificate excluding all permitted corrections. This is the standard first-order lifting mechanism expressed as a reusable interface, not a claim that Komorebi invented it.

Example: x^2+1=0 has x=1 modulo two, but c=1 and J=0 modulo two, so that root cannot lift modulo four. In contrast, a nonzero Frobenius defect in a chosen Cartier presentation need not obstruct existence of the original series. It may obstruct only retention of that particular normal form. The certificate must state its target and permitted corrections.

The finite audit exhausts every lower root of every scalar polynomial c0+c1*x+c2*x^2 with coefficients -2..2, for p=2,3,5 and r=1,2,3. It checks predicted versus actual lift fibers and representative invariance. Its bounded execution does not replace the multivariate proof above.

## 7. A quantitative information profile

Assume a fixed sequence of nonnegative weights s_i with finitely many s_i<r for each r, and

\[
H_r\cong\bigoplus_{s_i<r}p^{s_i}(\mathbb Z/p^r\mathbb Z).
\]

Define

\[
D(r)=\#\{i:s_i<r\},\qquad
L(r)=\log_p|H_r|=\sum_i(r-s_i)_+.
\]

**Proposition C1.** With L(0)=0,

\[
L(r)-L(r-1)=D(r),\qquad
D(r+1)-D(r)=\#\{i:s_i=r\}.
\]

**Proof.** Each summand in the first difference is one exactly when s_i<r. Each difference of indicator functions in the second is one exactly when s_i=r. The finite-tail assumption justifies the finite sums. End proof.

Thus D counts active algebraic directions, L counts the base-p digits needed to distinguish arbitrary module elements, and the second formula counts newly born directions. These are different resource quantities.

For the known binary-two-color spectrum s=(0,0,k^2-1,k^2+k+1 for k>=1),

\[
D(r)=2\sqrt r+O(1),\qquad L(r)=\frac43 r^{3/2}+O(r).
\]

The latter follows by summing two quadratic ladders up to sqrt(r); each contributes (2/3)r^(3/2)+O(r), and the two initial directions contribute 2r. At r=64 the exact quantities are D=17 and L=717. A full free coordinate array with 17 residues modulo 2^64 uses 1088 bits, while the mixed cyclic-factor coordinates have 717 independent bits.

This is not a lower bound on storage for the orbit SET of one deterministic automaton, which can be smaller than its linear span. It is not a lower bound for arbitrary programs that compute one coefficient. It is a precise cost for representing arbitrary elements of the specified module.

## 8. A certificate-producing discovery loop

A minimal loop for one stratum is:

1. Parse a problem into a declared semantic profile and bind it to the intended mathematical object.
2. Propose an encoding, basis, filtration, envelope, or operator relation.
3. Generate exact obligations: initialization, action preservation, observations, membership, inverse/reconstruction when required, and precision compatibility.
4. Try inexpensive falsifiers before long proofs. Record the failure target precisely.
5. Extract and certify a refinement, or prove the candidate contract.
6. Compose only certified transformations into a derivation.
7. Recheck final proof terms in the selected kernel and publish the exact theorem and remaining assumptions.

The learned proposer need not be trusted. The correctness claim is conditional on sound certificates and a sound final checker. The proposer affects success rate and cost, not what an accepted proof means. If the original formal specification is the wrong problem, kernel checking does not repair that semantic error.

A certificate identity should bind the source/target definitions, coefficient regime, operation signature, observation family, precision/horizon, proof statement, and dependencies. Cryptographic hashes supply identity and provenance, not mathematical truth. An elementary test certificate covers only its declared finite scope unless a proved reduction makes it universal.

For finite complete systems the refinement procedure above terminates with an exact quotient. For arbitrary mathematical structures no such termination or automatic discovery theorem has been established. Outcomes must include certified success, certified rejection, and unresolved.

### A two-sided discovery certificate

Maintain two certified bounds on the true reachable module:

\[
L_t\subseteq H\subseteq U_t.
\]

The lower bound is generated by explicitly witnessed words and their linear
combinations. The upper bound contains the seed and is invariant under every
allowed operation. New genuine orbit witnesses enlarge L_t. Proved invariant
constraints shrink U_t. A candidate outside L_t is not automatically outside H;
a separation certificate is required before calling it unreachable.

**Proposition R1.** If the modules are finite, the bounds are valid, and
|L_t|=|U_t|, then L_t=H=U_t. Over a finite chain ring it suffices to compare their
exact module lengths. Alternatively, proving L_t itself invariant and containing
the seed already proves L_t=H.

**Proof.** Equality of finite cardinalities together with inclusion gives equality
of L_t and U_t; H lies between them. For the alternative, invariance and seed
membership put every word and its span in L_t, while the witness construction
already puts L_t in H. End proof.

This is elementary finite algebra, not a new abstract theorem. Its architectural
role is substantial: a discovered basis earns exactness through matching lower
and upper certificates, not through enough successful samples. Universal
all-precision classification still requires a uniform argument beyond any fixed
finite instance.

## 9. Not one gigantic normal form

The core is best organized as multiple typed dialects with verified bridges: exact finite algebra, integral lattices, filtered local arithmetic, analytic approximation, stochastic models, and topological limits can have different representation laws. Merely casting an object into a generic graph does not preserve its useful structure or make discovery easy.

Existing work is essential context. MLIR supplies reusable extensible multi-level compiler infrastructure. E-graphs and equality saturation compactly retain equivalent programs and support optimization and synthesis. Abstract interpretation studies sound passage to simpler semantic universes and fixpoint approximations. Lean distinguishes mathematical proofs from computations, including noncomputable constructions based on choice. None of those ideas begins with this proposal.

The research question is whether a Komorebi integration of operational semantics, exact representation invariants, typed loss/enclosure, precision, and certified repair can reduce the cost of discovering new verified mathematics. A conceptual resemblance to a compiler does not establish that result.

The earlier contrast 'humans compress, machines compile' was too sharp. Both need compression, and humans have long designed algorithms and normal forms. A large rule set can worsen search. Useful redundancy requires indexing, preserved domains, and cost-aware selection. Machine-native should mean controllable semantic interfaces, not unreadable notation or mere volume.

## 10. The right optimization objective

Minimum algebraic dimension is only one axis. A machine should compare representations by a resource vector such as

\[
(\text{discovery cost},\text{construction cost},\text{state bits},
\text{transition cost},\text{certificate size},\text{checking cost}).
\]

A smaller state dimension may produce denser matrices or harder proofs. A larger representation may be faster to search or check. A weighted scalar objective can be introduced only after choosing a workload and units; there is no universal cost-free best basis.

For amortized reuse, a discovered representation is worthwhile when construction and proof costs are outweighed by savings on subsequent tasks. If C_build+C_proof is the up-front cost and C_old-C_new>0 is a per-query saving, the elementary break-even condition is

\[
N(C_{old}-C_{new})>C_{build}+C_{proof}.
\]

This is a planning equation, not an empirical measurement of our system.

The role of AI would be to propose high-value intermediate representations and lemmas, while the formal layer decides which operations and transfers are valid. The architecture's machine-native property can therefore be tested without speculating about model consciousness or access to hidden neural representations.

## 11. Falsifiable evaluation program

Hold fixed the model, theorem-prover version, external tools, total computation and source access. Compare a generic model-plus-prover workflow, a typed transformation registry, and that registry augmented with certified failure-driven refinement and learned representation proposals.

Use genuinely held-out structural families, not only new coefficient indices from already classified sequences. Suitable separate test strata include radix/color partition systems, finite linear dynamics with hidden observations, and prime-power polynomial lifting. Success in one does not automatically demonstrate cross-domain reuse.

Measure actual proof acceptance under identical contracts, total search/construction/checking cost, ability to reject invalid candidates, newly derived and reusable invariant schemas, and transfer to unseen structural regimes. Include ablations that remove learned proposals, remove certified residuals, or replace typed transport with unconstrained rewriting.

A 'discovery' must identify what was withheld. Recovering a known relation from provided matrices is a useful mechanistic test but not evidence of autonomous theorem invention. A proof accepted against the wrong source specification counts as a failure of the end-to-end system.

## 12. Current boundary and next precise claim

This release provides written statements Q1-Q3, T1, I1, O1 and C1, an exact finite prototype, and a pinned computation record. No new Lean declarations, trained policy, universal theorem-discovery algorithm, complete binary-three-color classification, or broad novelty verdict is claimed.

The next appropriate core verification target is a reusable, profile-indexed finite linear-system library that proves action descent, universal observational sufficiency, transport composition, sound invariant cuts, and finite termination. A subsequent benchmark should require the system to discover a coupled representation from an unrevealed structural family and emit an independently checkable bridge back to the original specification.

**The intended advance is mathematics in which changing the representation is itself a certified, searchable, reusable mathematical operation.**
