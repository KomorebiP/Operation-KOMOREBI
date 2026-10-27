# Goal status

Original goal: P versus NP. NOT RESOLVED.

## Completed written derivations

1. Every restored NCT oracle at every cut satisfies f = OR_i(P_i(x,0) XOR Q^{-1}_i(x,0)).
2. Exact Boolean secant transport constructs unit covectors at all cuts in one shared circuit using at most 4T multiplications, with linear XOR/NOT cost in the original gate count.
3. T >= max(0,deg(f)-1,2 alpha_1(f)-3,2 alpha_0(f)-3) for unrestricted restored NCT oracles.
4. For nonzero monotone f, alpha_1 is the size of a smallest positive support; the positive-support ideal has the corresponding monomial basis.
5. Restored classical monomial oracles have exact total/Toffoli cost 2k-3, even with active output and unlimited initially clean workspace. This is a calibration, not a novelty claim about a known resource count.
6. A square-power, near-full CLIQUE family is uniformly NP-complete and has unrestricted restored-Toffoli lower bound `(2-o(1))N`, with N the edge-input length.
7. An n-bit OR of witness predicates can always be covered by n+1 parity combinations of those predicates. A semantic packet-count lower bound cannot become superpolynomial by counting witness monomials.

## Failed extrapolations

- Decoding the output direction is not generically superpolynomial for a short circuit: both direct comparison and shared secant transport are cheap.
- Exponential dimension of the minimal-degree positive-support ideal does not force an exponential number of parity packets.
- The existence of a small packet list does not give a small circuit for evaluating it. Dense coefficient descriptions remain uncharged by packet count.
- Degree and one-sided immunity are at most N, so their present lower-bound endpoint is linear.

## Remaining conjecture-level obligation

Prove superpolynomial shared generation cost for an exact safe discrepancy cover of an explicitly polynomially encoded NP family, despite nonlinear sharing, cancellation, coordinate changes, and restored arbitrary workspace. The current comparison theorem is a necessary representation obtained from actual circuits, not a universal efficient synthesis algorithm from a verifier.

## Review status

Written proofs with self-review and exact finite evidence. No Lean or external peer-review acceptance. No unsupported estimated probability of solving the original conjecture.
