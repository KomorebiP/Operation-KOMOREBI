# Packet-resolved posterior error: proof and scope

## 1. Completed block

The v5 actual-law coupling and residual stopping theorem are retained unchanged.
This release proves the missing finite self-adjoint Hilbert-Schmidt energy layer
and composes it with those probability theorems. All matrices are real and all
index types are finite. The matrix may be rectangular. The two Euclidean spaces
have independent packet resolutions.

This is not an operator-norm Pythagorean identity. It is not a claim that refining
a fixed residual decreases the error. It is a theorem that the resolved energies
account for the same error certificate exactly.

## 2. Geometry and normalization

Let Pi_a be matrices on the output space and Lambda_b matrices on the input space.
Each family has the following explicit hypotheses:

    Pi_a^T = Pi_a,                 Pi_a Pi_a = Pi_a,
    Pi_a Pi_c = 0 for a != c.

The corresponding conditions hold for Lambda. Completeness is separate:

    sum_a Pi_a = I,                sum_b Lambda_b = I.

SelfAdjointPackets stores symmetry, idempotence and pairwise annihilation.
Complete asserts coverage. No property is inferred merely from a field being
called orthogonal. Zero-dimensional spaces and empty fibers are allowed with
these same exact conditions.

Define matrixEnergy(A) = sum_i sum_j A_ij^2. It is nonnegative and vanishes exactly
when A is the zero matrix. Its transpose has the same energy, and

    matrixEnergy(A) = trace(A^T A).

FDMatrixPacketEnergy identifies this definition with the existing frobeniusSq
by definitional equality. It also identifies coordinate vector energy with the
genuine squared Euclidean norm. Thus the matrix/operator probability interface
uses the same normalization; no default matrix supremum norm is substituted.

## 3. Main rectangular identity

For any finite subsets s and t of the two packet index types, let

    Pi_s = sum_{a in s} Pi_a,      Lambda_t = sum_{b in t} Lambda_b.

The subset sums are proved symmetric and idempotent. Disjoint subset sums
annihilate one another. For an arbitrary rectangular matrix A,

    ||Pi_s A Lambda_t||_F^2
       = sum_{a in s} sum_{b in t} ||Pi_a A Lambda_b||_F^2.

This LOCAL theorem does not require global completeness. When both families
are complete, choose s and t to be their full index sets to obtain

    ||A||_F^2 = sum_a sum_b ||Pi_a A Lambda_b||_F^2.

Any partial double sum is bounded by the full energy of the same fixed A.

The proof uses the self-adjoint projector Gram identity

    ||Pi A||_F^2 = trace(A^T Pi A).

Trace linearity yields output additivity. Transpose gives input additivity.
Applying both proves the rectangular theorem. The vector theorem follows from
an exact one-column embedding and its matrix-action identity.

Main declarations:

    matrixEnergy_sumOn_both
    matrixEnergy_eq_sum_blocks
    vectorEnergy_eq_sum_packets
    frobeniusSq_eq_sum_packets
    norm_sq_eq_sum_packet_norms

## 4. Exact hierarchical refinement

Suppose coarse projectors C_p and D_q are exact fiber sums of the fine families:

    C_p = sum_{rho(a)=p} Pi_a,
    D_q = sum_{tau(b)=q} Lambda_b.

Then

    ||C_p A D_q||_F^2
       = sum_{rho(a)=p,tau(b)=q} ||Pi_a A Lambda_b||_F^2.

The parent energy is zero if and only if every indicated descendant matrix is
zero. This follows from nonnegative energies and the exact zero-energy criterion.
It concerns blocks of A, not identification of every possible cause of A.

The coarsen constructor derives a valid self-adjoint packet family from any
fiber grouping of a fine family. Its refinement equality is proved, and it
preserves completeness. Grouping maps need not be surjective. Empty fibers
produce zero projectors. The mean-vector contribution obeys the corresponding
local parent-to-child energy identity.

These results apply repeatedly along a declared hierarchy. They do not prove
that modifying a model or an approximate solve decreases posterior error.

## 5. Packet-resolved gain-residual certificate

Retain the v5 model assumptions P >= 0, R > 0, arbitrary rectangular H, and
independent Gaussian noise. Set

    S = H P H^T + R,       v = y-Hm,
    F = P H^T - B S,

where B is an arbitrary approximate gain. The valid Joseph Gaussian approximation
has mean m+Bv and covariance

    J(B) = (I-BH)P(I-BH)^T + B R B^T.

The retained conditioning theorem supplies the actual explicit posterior eta_y.
The retained all-plan Wasserstein infimum and coupling theorem bound its distance
to the Joseph approximation. Assume an explicit noise floor R >= sigma I with
sigma > 0. Define

    e_ab = ||Pi_a F Lambda_b||_F^2.

The newly checked theorem is

    W2^2(eta_y, etaHat_y)
       <= (sum_a sum_b e_ab) (1/sigma + ||v||^2/sigma^2).

For epsilon >= 0, the square-root-free condition

    (sum_a sum_b e_ab) (sigma + ||v||^2) <= epsilon^2 sigma^2

implies W2(eta_y,etaHat_y) <= epsilon.

The statement also permits local upper bounds b_ab >= e_ab. If their sum meets
the same stopping condition, the posterior tolerance follows. No assumption
requires first computing the exact gain, exact posterior covariance or exact
innovation inverse. But the validity of a numerical routine producing b_ab and
sigma is not proved here. They remain mathematically certified inputs.

Main declarations:

    posterior_wasserstein2Sq_le_packet_residual_energy
    posterior_wasserstein2_le_of_packet_tolerance
    posterior_wasserstein2_le_of_packet_majorants

## 6. Two-model posterior factor certificate

For the compatible factor models retained from v5, define

    da = a(y)-a0(y0),
    DU = (I-KH)L - (I-K0H0)L0,
    DV = K N - K0 N0.

Use complete self-adjoint output packets Pi, prior-latent packets Lambda and
noise-latent packets Xi. The new packet budget is

    sum_a ||Pi_a da||^2
      + sum_a sum_b ||Pi_a DU Lambda_b||_F^2
      + sum_a sum_c ||Pi_a DV Xi_c||_F^2.

Lean proves that this is EXACTLY the full quadratic cost of the previously
constructed actual posterior coupling. It therefore bounds W2^2 between the
actual posterior versions. A squared tolerance theorem and a local-upper-bound
budget theorem are included.

This is equality for the cost of a specified coupling, not equality between
W2^2 and that cost. The coupling need not be optimal. Factors remain explicit
with compatible latent dimensions. Their alignment and conversion from primitive
covariance discrepancies remain separate obligations.

Main declarations:

    FactoredGaussianModel.packetFactorErrorBudget_eq
    FactoredGaussianModel.factorCoupling_cost_eq_packets
    FactoredGaussianModel.posterior_wasserstein2Sq_le_packet_factors
    FactoredGaussianModel.posterior_wasserstein2_le_of_packet_factor_tolerance

## 7. Checks that guard the boundary

The rotated two-dimensional projections

    Pi_0 = (1/2) [[1,1],[1,1]],
    Pi_1 = (1/2) [[1,-1],[-1,1]]

are proved to be a complete self-adjoint family. A universal rectangular
regression applies the energy theorem to them, so the formal result is not
restricted to literal coordinate selectors.

The oblique matrices

    P = [[1,1],[0,0]],  Q = [[0,-1],[0,1]]

are proved idempotent, mutually annihilating and complete. Yet their energies
sum to 4 while the identity matrix has energy 2. This shows why the stronger
self-adjoint hypothesis is essential for this square-sum theorem.

A separate Python script checks 16 constructed exact-rational cases, with state
and observation dimensions 1 through 4, rational rotated projectors, 64 local
parent identities, vectors, singular-prior factored models, gain residuals and
local upper bounds. It also checks a missing-coverage counterexample. These are
finite diagnostics, not proofs of universal claims.

## 8. Verification and non-claims

The active slice contains 41 modules: 30 retained modules rebuilt from their
unchanged sources, 10 new proof modules, and one new full axiom-audit module.
The audit covers 165 theorem/lemma declarations, including 46 new declarations.
Counts include support identities and six new symbolic checks. They are not
counts of independent mathematical discoveries.

Use FINAL_VERIFICATION_RECEIPT.json and AXIOM_AUDIT.json for the actual recorded
run data. Every final source and direct dependency hash is checked. The pinned
mathlib cache is reused; the entire older continuous-time and moment-bridge
program is not rebuilt. Failed and incomplete attempts are not successful
verification evidence.

No operator-norm square-sum theorem, primitive-model identifiability, optimal
transport decomposition, adaptive progress/termination, certified floating point,
optimal packet selection, singular-innovation extension, nonlinear filtering,
new general Ito derivation, or literature priority is claimed. The all-plan
transport definition and its prior metric-development boundary are unchanged.
Canonical posterior versions retain their evidence-a.e. scope. The explicit
posterior comparisons here are pointwise in their observation arguments.
