# Independent cross-radix and Cartier audit

The closure claim under review is that the recovered cross-radix and Cartier
machinery excludes a common zero of the **prescribed** Euler residual and its
ordinary derivative, in particular on the terminal-161 chart. Primary verdict:
**incomplete, with the smallest missing implication being a constraint on the
prescribed Bernoulli units that excludes the stationary contact.** The new
transport, compiler, and scoped obstruction theorems reviewed below are valid;
none asserts that they close this implication.

This is an independent review by `/root/cross_cartier_review`, reading the raw
proofs and implementations, with separate replay outputs. It is not a claim of
formal verification. No Lean compilation was performed. Author files were not
edited by the reviewer. One scope clarification was requested and incorporated
by the Cartier author: the contact model preserves the inherited derivative
valuation law only for `0 <= j < r`, not an unstated all-order law.

## Exact objects, revisions, and dependencies

The coefficient field is Q_2, with ordinary `s` or `x` derivatives. The actual
tail coefficients are the specified rational Bernoulli coefficients; the two
free-coefficient contact examples are explicitly outside that arithmetic class.
Spatial sections act on the measure variable `y`, while coefficient sections
act on powers of `T=y-1`. They are different operations.

Reviewed proof revisions:

- `cross_radix/CROSS_RADIX_AND_TRIPLICATION.md`, SHA256
  `962331260cef7d736a3b2692cb968748bde00230a7edec4cb5459857275a46e6`.
- `cartier_mask/EXACT_SPATIAL_COMPILER.md`, SHA256
  `ac6b5d9514f718c107b2369a247be275b95fecdcffd556cdfc9e1246a277076e`.

All proof, script, contract, current-evidence, and replay hashes are recorded in
`CROSS_CARTIER_REVIEW_HASHES.json`. Paths there are relative to the project root.

Dependency graph:

1. The base source `A`, packet product identity, Euler interpolation, prescribed
   prefix, and inherited packet bounds feed the cross-radix derivations.
2. The finite hyperbolic identity gives odd-radix transport and its exact cutoff
   cocycle. Kernel triplication gives the full nonlinear cutoff identity.
3. Rational integer evaluations plus finite digit rank would give rational digit
   matrices and polynomial archimedean growth; actual Euler interpolation
   contradicts that growth. No Bell theorem is needed for this obstruction.
4. The rational transform `R` gives the spatial sections, six-state automaton,
   and bounded measures `mu_U,mu_V`. Restriction of their integrals gives the
   Mellin recursion and its derivative.
5. Root-of-unity filtering of the actual finite prefix gives its meromorphic
   states. Reconstruction of both polar coefficients gives `B_8`; retaining
   these coefficients is essential.
6. Actual positive-order distribution modes preclude the stated generic strict
   contraction. The source's unit value/slope determinant gives the exact
   free-packet contact countermodel. Neither supplies actual Bernoulli contact.

Leaves 1 and the existence of the initial regularized measure are inherited
base results, with the cited computational implementations replayed where used.
The new algebraic and analytic implications were reconstructed in this review.
The cross-radix archive is used to check applicability, not to import an
unaudited external theorem.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Odd affine lanes preserve multiplicity but do not partition Z_2 | Passed | Nonzero affine derivative factor; odd multiplier is a unit |
| Odd-radix operator converges in the restricted algebra | Passed | Summand Gauss valuation at least `k+s_2(k)` up to a fixed norm; differentiation is bounded |
| Odd-radix Euler identity, composition, and cutoff forcing | Passed | Finite identities at nonnegative integers followed by density; arbitrary input sequence composition is triangular at each such integer |
| Full beta triplication and all cutoff terms | Passed | Direct expansion of `(3f+4t)^2 f(9t)=9f^3`, including constant forcing cancellation |
| Uniform actual Delta_9 valuations 157 and 158 | Passed relative to cited base bounds | q=0 is strictly dominant after q=161 is removed; derivative estimates were checked separately |
| Infinite k-kernel rank over Q_2 for actual G_r(n) | Passed | Rational minors descend finite rank to Q; digit products give polynomial growth, contradicting the Euler EGF pole |
| CrossRadix v0.12 applicability | Passed as a negative applicability check | Actual value sequence fails its regularity input; archive itself does not supply shell-lattice membership |
| Spatial six-state compiler | Passed | Eight exact section identities, invariant vector orbits, and residue reconstruction |
| Infinite Amice coefficient-section rank | Passed | Distinct new pole radii at each even decimation; dominant conjugate poles never merge |
| Fixed-cutoff meromorphic state space | Passed | Root-of-unity sections preserve the finitely many log powers and contract Laurent exponents |
| B_8 and derivative correction | Passed | Both `t^-2` and `t^-1` contributions retained; exact coefficient reconstruction and ordinary differentiation |
| Mellin integral domain and joint value/slope recursion | Passed | Unit squares lie in `1+8 Z_2`; bounded measures permit uniform integration and differentiation |
| Neutral mode blocks generic strict contraction | Passed in stated scope | Nonzero `H_k` is an exact fixed vector of `H -> 2^-k H(s,2z)`; an occupied actual cutoff contains k=2 |
| Free two-packet contact model | Passed in stated scope | Integral unit jet determinant solves the two equations exactly; pole data remain unchanged |
| Prescribed Bernoulli critical value is nonzero | Not addressed by a closing implication | Transport compatibility and retained source do not enforce the required unit inequality |
| Universal Euler simplicity and all higher addresses | Not addressed | No claim of closure is supported |

## Critical derivations and scope checks

For odd-radix transport, the binomial polynomial has Gauss valuation at least
`s_2(k)-k`, while the integer coefficient `w_(m,k)` has valuation at least `2k`.
The resulting positive slope proves convergence of the operator and all ordinary
derivatives. At a nonnegative integer the sum truncates exactly. Thus the use of
dense integer evaluations for composition is valid for arbitrary restricted
inputs, not merely for the Euler solution. The even-radix warning is also
correct: unmodified powers of an even integer do not interpolate continuously
in the dyadic exponent.

For the strict defect theorem, q=0 contributes value valuation 154+3=157 and
derivative valuation 154+3+1=158. The q=1, q=2, and intermediate packets have
the advertised larger derivative bounds. For q>=162 the factorial derivative
bound is at least 152; the first tail gamma valuation is at least 4 and the
deflection factor contributes at least 3. This gives 159, strictly above 158.
At the remote region where that explicit gamma formula stops, normalized
integrality and the much larger factorial bound suffice. The conclusion is
not zero propagation: a hypothetical double zero of G gives a nonzero scaled
tail jet, without contradicting the full shifted-operator identity.

For finite digit rank, every integer evaluation of G_r is rational: packets
past the evaluation point vanish, including the packet whose removable source
value itself involves log9. Independent rational sequences are detected by a
finite rational minor. Hence a finite Q_2 section span really does yield a
finite rational representation. O(log n) products of fixed rational matrices
have polynomial real growth. Equation (9) would then bound Euler numbers by an
exponential times a polynomial. Their exponential generating function would be
entire; multiplying it by cosh gives the identity 1, contradicted at `i*pi/2`.
This proof does not rule out zero-set automata, finite precision, or a different
derived sequence.

The spatial formula is interpreted near `y=1` through the bounded measure and
then rationally continued. Both signs of the local square root remain in the
Amice disc on a sufficiently small neighborhood. For the meromorphic prefix,
the torsion log branch gives the algebraic formula (3.2); these states are not
silently asserted to be bounded measures. Their Laurent reconstruction is an
exact identity. In particular, expansion of `exp(a t) t^-2` contributes to every
ordinary nonnegative moment, explaining why finite parts alone are insufficient.
The stated removable point of B_8 at s=-1 follows since its second numerator
vanishes there. On the focused chart all displayed divisions are regular.

For the Mellin recursion, `z in 2 Z_2` implies `(1+zu)^2 in 1+8 Z_2` uniformly
in u. The logarithm therefore defines the stated analytic dependence on s, and
its derivatives are uniformly bounded under the measure integral. Splitting
u into even and odd residue classes gives precisely `2z` and `2z/(1+z)`, with
the odd multiplier `((1+z)^2)^s`. The chain rule in s retains its logarithm.
The mod-4 support split of R then gives (6.2), whose second term contributes
the additional log9 upon differentiation.

The neutral-mode argument is a limitation of generic strict contraction on the
enlarged state class, not a claim that no restricted arithmetic invariant can
work. Independently recomputing the actual `j=9` residue at depth four gives
`32/(3t^2)-1/2+9t^2/640` for r=3. Thus the displayed k=2 mode is actually
occupied, rather than inserted solely as an artificial state. Its section
weight exactly cancels the contraction of its moment argument, for both value
and slope.

For the contact model, `A=1 mod 2`, `A'=0 mod 2`, and `J'=1 mod 2`; hence the
two-by-two value/slope matrix has unit determinant at every a in Z_2. The right
side lies in `2^(3r)`, so both solved coefficients do as well. Multiplication
by the prefix packet preserves the forced lower zeros. Multiplication by the
regularizer places the perturbation and all its ordinary derivatives in
`2^(3r+2)`, which preserves the inherited exact law `3j+2` for `j<r`. It does
not establish any all-order law. The two added powers are nonnegative, so
neither polar coefficient nor B_8 changes. These facts do not identify the
free dyadic coefficients with the actual next Bernoulli coefficients.

## Source and computation checks

Read the actual v0.12 `BELL_EXTERNAL_INTERFACE.md` and `PROOF_BOUNDARIES.md`,
and verified the archive and all four entries pinned by `SOURCE_BOUNDARIES.json`.
Bell's external theorem was not used in any new proof. The internal interface
requires regularity or the supplied eventual quasi-polynomial profile; it does
not establish such input for arbitrary Euler data.

Both author checkers were read and independently replayed with bounded runner
contracts. Replay directories are `review/cross_replay` and
`review/cartier_replay`. Both result JSON files are byte-identical to the
current author results. All four author/replay manifests validate with
`python3 audit_helpers/validate_manifest.py --root . <manifest>`.

The cross replay covers degree 24 formal identities, 75 odd Euler moment
identities, complete available cutoff coefficients for r=2,...,9, and the two
fixed actual stationary defect calculations at 210 global bits and 180 output
bits. The Cartier replay covers eight exact section identities, six states,
254 residue checks through depth seven, kernel ranks one through six, 95
prefix moment reconstructions, 81 Mellin checks, and the named 32-bit contact
model. Finite checks supplement the proofs; they do not prove an all-r claim.
The earlier Cartier `certified_run` is superseded and was not treated as
current-source evidence.

## Remaining gap and strongest safe conclusion

The strongest safe conclusion is that the full regularized Euler measure has
an exact six-state spatial compiler and a two-function joint value/slope
recursion, while the actual cutoff has a finite meromorphic compiler retaining
the source. These additions are compatible with the existing stationary
obstruction. Generic finite-state compilation of the entire value sequence and
generic strict contraction of the augmented state are both excluded in the
precise senses proved above.

To close the focused chart, a further property of the actual Bernoulli units
must exclude the simultaneous equations after the polar correction and shifted
operator terms are retained. No cheaper additional precision check repairs
that missing implication. A proposed next invariant should first be tested
against the exhibited neutral mode and free contact model, then shown to hold
specifically for the prescribed Bernoulli coefficients. Universal closure would
also require the remaining higher-address coverage.
