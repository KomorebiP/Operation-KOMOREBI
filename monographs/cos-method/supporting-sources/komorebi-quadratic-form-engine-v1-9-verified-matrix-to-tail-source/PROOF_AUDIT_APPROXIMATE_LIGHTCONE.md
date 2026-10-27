# Proof audit - certified approximate light cones

Date: 2026-09-23

## Target

Replace the exact phase-graph hypothesis

\[
P_hHP_g=0
\]

by a quantitative certificate when discarded phase blocks are small but
nonzero.

## Outcome

**Proved as written** in finite dimension under the following hypotheses:

1. `P_1,...,P_q` are mutually orthogonal projectors summing to the identity.
2. `H` is a linear operator, represented here by a finite matrix.
3. `H_0` is obtained by retaining a declared set of complete phase blocks
   `P_h H P_g` and discarding the rest.
4. Phase profiles use Frobenius norms for block vectors and phase-transfer
   entries use operator 2-norms.

No positivity assumption is needed for the transfer theorem. Symmetric block
retention preserves self-adjointness. Positive semidefiniteness of the pruned
operator is not guaranteed and is not used by the proof.

## Strongest result

With

\[
\rho(X)_g=\|P_gX\|_F,
\qquad
\mathcal B_{hg}=\|P_hHP_g\|_2,
\]

one has

\[
\rho(H^kX)\le \mathcal B^k\rho(X).
\]

For a retained operator `H_0` and its transfer matrix `B_0`,

\[
\rho((H^k-H_0^k)X)
\le
(\mathcal B^k-\mathcal B_0^k)\rho(X).
\]

The result extends to every finite polynomial

\[
p(t)=\sum_j a_jt^j
\]

through

\[
\rho((p(H)-p(H_0))X)
\le
\sum_{j\ge1}|a_j|(\mathcal B^j-\mathcal B_0^j)\rho(X).
\]

## Decisive mechanism

The proof combines:

- phasewise submultiplicativity;
- the operator telescoping identity
  \(H^k-H_0^k=\sum_j H^{k-1-j}(H-H_0)H_0^j\);
- the identical telescoping identity for the nonnegative transfer matrices;
- orthogonality of the phase projectors.

## Boundary and conservatism

The certificate ignores cancellation and singular-vector alignment, so it can
be conservative. It certifies a chosen pruning pattern; it does not prove that
the pattern is communication-optimal. A thresholded phase graph inferred from
noisy empirical estimates requires a separate uncertainty layer.

## Computational audit

A deterministic PSD example used 12 phases of width 4, weak long-range
couplings, depths 1-8, seven pruning thresholds, and a signed degree-four
polynomial. All phasewise and global certificates passed.

The computation is evidence about the reference implementation and sharpness,
not the universal proof.
