# Unified inference research review

This is a planning and mathematical-derivation supplement to the v4 checkpoint.
It is NOT a checked Lean release. No authoritative proof-state file was modified.

## Evidence checked in this review

The v4 archive passed ZIP CRC and all 472 internal SHA-256 checks. All 38 active
module sources matched the hashes in their archived successful compilation
receipts. Lean was not rerun in this review. The receipt records 138 active
lemma/theorem declarations (51 inherited Gaussian, 39 normalized dependencies,
48 new in the preceding bridge release).

`checks/exact_checks.py` runs 18 constructed small-matrix cases over exact
rationals in SymPy, across state/observation dimensions (1,1), (2,1), (2,2),
(2,3), (3,2), (3,3). These bounded checks support implementation/sign/index
consistency, not universal proof or novelty. Results are in EXACT_CHECK_RESULTS.json.

## A. Mixed posterior covariance identity

Two models have positive semidefinite priors P,P0, positive definite noise R,R0,
and rectangular observation maps H,H0. Define

    S = H P H^T + R,  K = P H^T S^-1,
    G = I-KH,  C = P-KHP,

and the corresponding subscript-0 quantities. Let dP=P-P0, dH=H-H0, dR=R-R0.
The proposed exact identity is

    C-C0 = G dP G0^T + K dR K0^T - C dH^T K0^T - K dH C0.

Paper proof: the previously established Kalman identities imply

    GP=C,  P0 G0^T=C0,  C H^T=K R,  H0 C0=R0 K0^T.

Consequently

    G P G0^T + K R K0^T = C + C dH^T K0^T,
    G P0 G0^T + K R0 K0^T = C0 - K dH C0.

Subtract and rearrange. No inverse of either prior or posterior covariance is
used. For H=H0 and R=R0 this reduces to

    C-C0 = G (P-P0) G0^T.

A proposed norm bound is the sum of the four product norms. This need not always
improve the existing six-term budget; after both bounds are proved, their minimum
is also a valid bound.

For P=ones(2), P0=I, H=H0=I, R=R0=I, the existing general budget is 6. The fixed-H,R
bound is 1/2 and equals the actual operator error on this example. This is not a
universal sharpness result.

## B. Residual-certified inexact Gaussian conditioning

Fix one valid model. An arbitrary approximate gain Khat defines

    v = y-Hm,
    ahat = m+Khat v,
    J(Khat) = (I-Khat H) P (I-Khat H)^T + Khat R Khat^T,
    etahat_y = N(ahat,J(Khat)).

J(Khat) is positive semidefinite, so this is a valid Gaussian approximation.
It is not asserted to be the exact conditional law of the original model.

Use independent X~N(m,P), e~N(0,R) and define a sampler for any gain B by

    Z_B = X+B(y-HX-e).

Its law is N(m+Bv,J(B)). For the exact gain K, the existing Gaussian conditioning
and Joseph identities show that this law is the actual posterior version eta_y.
Thus (Z_K,Z_Khat) is a candidate coupling requiring no cross-model factor
alignment and no inverse of P.

Let

    F = P H^T - Khat S.

Then

    K-Khat = F S^-1,
    J(Khat)-C = F S^-1 F^T.

The second identity follows by expanding J at K. The cross terms vanish because
K S = P H^T. It also follows that the approximate covariance is no smaller than C
in the positive-semidefinite order.

The sampler difference is

    Z_K-Z_Khat = (K-Khat)[v-H(X-m)-e].

The bracket has mean v and covariance S. The proposed exact quadratic coupling
cost is therefore

    E ||Z_K-Z_Khat||^2 = ||F S^-1 v||^2 + tr(F S^-1 F^T).

A coupling gives an upper bound on W2 by its definition. Hence the target theorem is

    W2(eta_y,etahat_y)^2
      <= ||F S^-1 v||^2 + tr(F S^-1 F^T).

If S >= sigma I for a known sigma>0, this yields

    W2(eta_y,etahat_y)^2
      <= ||F||_op^2 ||v||^2 / sigma^2 + ||F||_F^2 / sigma.

A sufficient computable stopping condition, using ||F||_op <= ||F||_F, is

    ||F||_F <= epsilon*sigma/sqrt(sigma+||v||^2).

A lower bound R>=sigma I supplies the required innovation bound since HPH^T is
positive semidefinite. Numerical evaluation of residuals and bounds requires
separately certified rounding/enclosures to make this a machine-level guarantee.

For a linear observable T, replace F by TF in the displayed upper bound to
certify the two pushforward posterior laws.

## C. Full two-model coupling

For aligned compatible factors P=LL^T and R=BB^T, let standard Gaussian xi,zeta
be independent. The Joseph sampler is

    a(y) + GL xi - KB zeta.

Using the same noises for the other model proposes the bound

    W2(eta_y,eta0_y0)^2 <= ||a-a0||^2
       + ||GL-G0L0||_F^2 + ||KB-K0B0||_F^2.

This requires proving sampler laws, coupling marginals, quadratic integrability,
and a connection to the named Wasserstein definition. It is not a new Lean result.

## D. Geometry and implementation boundaries

1. An additive decomposition of the energy of a fixed error does not reduce it.
   Refining a representation and changing an approximating model are distinct.
2. Self-adjoint orthogonal complete projections give Frobenius square sums;
   pairwise-annihilating idempotents alone do not give that Hilbert geometry.
3. Factor-dependent coupling costs can be positive for identical laws: 1 and -1
   both generate N(0,1), but the unaligned shared-noise cost is 4.
4. At the singular boundary, N(0,delta I_n) versus delta_0 has covariance operator
   difference delta and squared W2 distance n*delta. Uniform covariance-Lipschitz
   W2 and dimension-free bounds from only that operator discrepancy are impossible.
5. Smaller primitive-parameter error need not yield smaller posterior error:
   with P=R=1, m=y=0 and true H=1, H0=-1 has exactly the same posterior; H1=1/2
   is closer in parameter norm but gives posterior variance 4/5 instead of 1/2.
6. Certificates concern a specified reference model, not its empirical truth.
   Lipschitz-observable guarantees do not automatically bound every event probability.
7. A proposed refinement step may keep the incumbent unless a better certificate
   is obtained. That ensures non-increase of the selected certificate, but not
   termination or optimality without additional hypotheses.

## E. Bounded literature comparison

Primary sources inspected, without an exhaustive novelty search:

- James T. Wilson et al., Pathwise Conditioning of Gaussian Processes,
  JMLR 22(105), 2021; arXiv:2011.04026v3. Theorem 1 gives Matheron's rule;
  Section 6 / Proposition 5 already analyzes posterior Wasserstein approximation
  error. https://arxiv.org/html/2011.04026v3
- S. L. Cotter, M. Dashti, A. M. Stuart, Approximation of Bayesian Inverse Problems
  for PDEs, arXiv:0909.2126v1 / SIAM J. Numer. Anal. 48(1), 2010. Theorem 2.4 and
  Corollary 2.5 transfer forward approximation to posterior Hellinger bounds
  under their specified regularity/integrability assumptions.
  https://arxiv.org/html/0909.2126v1
- P. Del Moral and E. Horton, A Note on Riccati Matrix Difference Equations,
  SIAM J. Control Optim. 60(3), 2022, DOI 10.1137/21M1437226. Journal metadata
  and abstract inspected as adjacent Riccati stability literature, not as a
  verification that it states the proposed four-term identity.

No novelty is inferred for any proposed identity, coupling, or residual bound.
The prospective contribution must be assessed at the level of the exact combined
formal theorem and its useful computational guarantees.
