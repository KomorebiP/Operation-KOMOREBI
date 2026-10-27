# Euler Lean XVIII: all-order packet differentiation and exact value–slope transport

**Operation Komorebi — 3 October 2026 — continuation v18**

## Status and scope

This release proves term-by-term differentiation of the ACTUAL infinite Euler
packet sum, at every ordinary derivative order and every dyadic argument. It
also proves all-order evaluated Hasse-jet interchange, complete differentiated
packet-tail bounds, the first-order differentiated residual recurrence, and an
exact denominator-free Wronskian criterion for critical zeros. All these
statements use the independently defined Euler residuals constructed in v17.

A key distinction is now formal: at a nonnegative integer row, every packet
beyond that row vanishes in VALUE, but every one has a NONZERO FIRST DERIVATIVE.
The analytic derivative sum must not be truncated using pointwise value zeros.
No assertion is made that the sum of all omitted nonzero slopes is always nonzero.

There are 66 new theorem/lemma declarations in seven modules. The complete
project has 483 such declarations in 49 mathematical modules. Counts include
helper lemmas and are not counts of novel mathematical results. All 42 incoming
mathematical modules remain byte-for-byte unchanged.

No new irregular wall is classified. The manuscript's terminal-degree and
binary-complexity bounds are not increased or relabelled as end-to-end formal
results. The Euler-specific critical-value nonvanishing problem remains open.
No historical-priority assertion is made for packet differentiation, which is
ordinary differentiation applied to a retained packet decomposition.

## 1. Exact objects and conventions

Let D=Z_2 and K=Q_2, implemented by mathlib's actual `ℤ_[2]` and `ℚ_[2]`.
Let A be the constructed restricted Euler source, beta_m the actual integral
Bernoulli kernel coefficient, and

    P_q(x) = product_(i=0..q-1) (x-i)(2x-2i-1).

All beta_m are nonzero. For r>0, v_2(beta_r)=s_2(r)-1.

The qth integral numerator packet is

    F_(r,q)(x) = 8^q beta_(r+q) P_q(x) A(x-q).

The integral numerator and field-valued residual are

    J_r = sum_q F_(r,q),      H_r = J_r / beta_r.

The qth packet of H_r is Pi_(r,q)=F_(r,q)/beta_r. In Lean it is
`eulerPacketFunction r q`, a function K -> K evaluated and differentiated on D.

The scalar normalizing H_r is 2^(-mu_r), and

    G_r = 2^(-mu_r) H_r = (2^(-mu_r)/beta_r) J_r.

The complete coefficient constructions and exact identification with the Euler
error are inherited from v17, not newly assumed hypotheses.

The evaluated kth Hasse jet is

    J_k(f,x) = sum_n choose(n+k,k) a_(n+k) x^n.

Every norm statement below also covers zero. Additive valuation interpretations
use v_2(0)=infinity mathematically; the code does not confuse that convention with
mathlib's integer-valued valuation at zero.

## 2. All-order genuine analytic derivatives

For any integral restricted series f, any c in K, any k>=0 and x in D, Lean proves

    iteratedDeriv k (c * qeval f) x = c * k! * J_k(f,x).       (1)

Here `iteratedDeriv` is mathlib's ordinary iterated analytic derivative. It is
not a newly defined derivative surrogate.

The proof is local on K. Equality of two functions on D gives eventual equality
at each x in D, because D is an open neighborhood of its own points in K. The
inherited first-derivative theorem is applied recursively to the restricted
Hasse series. The exact identity

    J_1(HasseSeries k f,x) = (k+1) J_(k+1)(f,x)

provides the factorial factor. Every member of the derivative tower has a proved
`HasDerivAt` statement.

This approach does not invoke a real/complex-only theorem about uniform limits
of derivatives. The formal proof uses the complete dyadic coefficient sums and
the actual Q_2 derivative framework.

## 3. Interchange with the entire Euler packet sum

The inherited coefficient estimates are

    |[X^n]F_(r,q)|_2 <= 8^(-q),
    |[X^n]F_(r,q)|_2 <= 2^(-(n+q)).

Hasse differentiation multiplies coefficients by integral binomial coefficients.
Therefore, for every k,n,q,

    |[X^n]HasseSeries k F_(r,q)|_2 <= 8^(-q),
    |[X^n]HasseSeries k F_(r,q)|_2 <= 2^(-(n+k+q)).

The second estimate bounds the packet/Taylor double sum by a product of two
summable geometric series. All exchanges of summation are therefore justified.
Lean proves

    J_k(J_r,x) = sum_q J_k(F_(r,q),x)                        (2)

for EVERY order k, with summability of the right side. Combining (1) and (2),

    H_r^(k)(x) = sum_q Pi_(r,q)^(k)(x)                      (3)

for every r,k>=0 and x in D. In the original Euler-tail application r>=1.
The equality at k=1 is the termwise packet-derivative theorem previously missing.

## 4. The two derivative channels

The formal derivative agrees with the first Hasse series. Its Leibniz rule,
analytic multiplicative evaluation, and the checked derivative of the actual
source translation give

    Pi_(r,q)'(x) = (8^q beta_(r+q)/beta_r) *
       [ P_q'(x) A(x-q) + P_q(x) A'(x-q) ].                (4)

The two terms retain the skeleton derivative and source derivative separately.
The source-shift derivative is established by eventual equality of the actual
translated series evaluation and x -> A(x-q), followed by uniqueness of the
analytic derivative. It is not an unsupported formal substitution at a nonzero
constant.

## 5. Uniform derivative-tail bounds and finite witnesses

Let J_(r,<Q) retain packets 0<=q<Q, with the source in each retained packet still
an exact infinite series. Let H_(r,<Q)=J_(r,<Q)/beta_r.

For EVERY k,Q>=0 and x in D,

    |J_k(J_r,x)-J_k(J_(r,<Q),x)|_2 <= 8^(-Q).              (5)

Thus P<=3Q implies equality modulo 2^P for every evaluated Hasse jet, with no
additional derivative-order loss. For ordinary derivatives,

    |H_r^(k)(x)-H_(r,<Q)^(k)(x)|_2
       <= |k!|_2 / |beta_r|_2 * 8^(-Q).                   (6)

The factorial norm is at most one. Division by beta_r is NOT free: its norm
factor remains explicit. Carry normalization also has its exact scaling cost:

    |J_k(G_r,x) - (2^(-mu_r)/beta_r) J_k(J_(r,<Q),x)|_2
       <= |2^(-mu_r)/beta_r|_2 * 8^(-Q).                 (7)

For an actual finite polynomial residue certificate p of J_(r,<Q), the code
checks the following complete implication. If P<=3Q, EVERY Taylor coefficient
of J_(r,<Q) reduces to the corresponding coefficient of p, and

    p(y)=0 implies p'(y)!=0 for all y modulo 2^P,

then H_r has no simultaneous value-and-derivative zero on D. The same conclusion
holds for the actual G_r. The polynomial coefficient hypothesis includes all
unlisted coefficients; it is not supplied by testing values at representatives.

A pointwise version requires only a nonzero residue of the truncated first jet.
It gives a rigorous finite slope witness for a nonzero derivative of H_r.

These are certificate SOUNDNESS theorems. They do not claim that the unresolved
Euler critical-value families satisfy the certificate hypotheses.

## 6. Integer-row value support is NOT derivative support

For every nonnegative integer n and every q>n,

    P_q(n)=0,        P_q'(n)!=0.

The formal proof of the second assertion uses the exact product recurrence for
P_q and the fact that all odd companion factors are nonzero on D. At the first
omitted packet,

    P_(n+1)'(n) = -P_n(n) != 0.

Every later factor preserves a simple zero at n. The source A(n-q) is a unit,
even at negative translated arguments. Therefore the actual analytic packets
satisfy

    Pi_(r,q)(n)=0,        Pi_(r,q)'(n)!=0                  (8)

for every q>n. In particular their derivative sequence is never eventually zero.

This resolves a potentially misleading inference: the exact FINITE evaluation
formula at an integer row cannot be differentiated after simply erasing the
packets that vanish at that point. Those packets do not vanish on a neighborhood.

Equation (8) concerns individual terms. It does not exclude cancellation in the
SUM of the derivative tail. Six separate finite-precision examples in the audit
show a nonzero omitted slope sum, but they are not used to assert that universally.

## 7. Actual differentiated residual transport and the Wronskian obstruction

Put

    c_r = 8 beta_(r+1)/beta_r,    Q(x)=x(2x-1).

The inherited exact recurrence is

    H_r(x)=A(x)+c_r Q(x) H_(r+1)(x-1).

Its derivative is now checked:

    H_r'(x)=A'(x)+c_r[(4x-1)H_(r+1)(x-1)
                       +Q(x)H_(r+1)'(x-1)].              (9)

Thus the value/slope pair has the equivalent triangular transport matrix

    (H_r,H_r')^T = (A,A')^T
       + c_r [[Q,0],[Q',Q]] (H_(r+1)(x-1),H_(r+1)'(x-1))^T.

The Lean source proves the scalar identities underlying this matrix notation.

Define the denominator-free Wronskian

    W_r(x) = A(x) [ Q'(x)H_(r+1)(x-1)+Q(x)H_(r+1)'(x-1) ]
             - A'(x) Q(x)H_(r+1)(x-1).

Lean proves EXACTLY

    c_r W_r(x) = A(x) H_r'(x) - A'(x) H_r(x).             (10)

Since c_r and A(x) are nonzero, this gives

    CriticalZero(H_r,x) iff H_r(x)=0 and W_r(x)=0.         (11)

No division by Q(x) or H_(r+1)(x-1) occurs, so the identity does not develop a
spurious singularity when one of those factors vanishes.

All ordinary derivatives respect normalization:

    G_r^(k)(x)=2^(-mu_r) H_r^(k)(x).

Consequently G_r and H_r have exactly the same analytic critical zeros, and the
Wronskian criterion applies to the ACTUAL normalized residual as well.

Equation (11) is an exact reduction, NOT a proof that W_r never vanishes.
The remaining Euler arithmetic nonvanishing task has not been assumed away.

## 8. A concrete all-depth derivative application

The source's actual complete mod-eight certificate gives

    |A'(x)|_2=1/2 for every x in D.

The Q=1 packet truncation of H_r has exactly the same derivative as A.
For every positive r with s_2(r)<=2, |beta_r|_2>=1/2. Thus (6) at k=1,Q=1 gives

    |H_r'(x)-A'(x)|_2<=1/4<|A'(x)|_2.

The ultrametric inequality implies

    |H_r'(x)|_2=1/2                                      (12)

for every dyadic x. In particular H_r has no critical point at these depths.

This is an end-to-end derivative statement about an infinite family of actual
Euler residuals. Those small binary-complexity depths were already root-free in
v17. It is not claimed as an increase in the manuscript root-classification range.

## 9. Module map

| New module | Declarations | Purpose |
|---|---:|---|
| RestrictedHigherDerivatives | 7 | All-order actual analytic derivatives and Hasse jets |
| ResidualPacketJets | 11 | Infinite packet-jet interchange and all-order precision |
| PacketDerivatives | 16 | Actual packet functions, product channels, derivative sums |
| PacketDerivativeBounds | 7 | Differentiated truncation and finite certificate soundness |
| PacketIntegerSlopes | 10 | Simple packet zeros and the nonterminating integer-row slope tail |
| ResidualSlopeTransport | 9 | Differentiated recurrence, Wronskian, normalized critical zeros |
| ResidualSlopeExamples | 6 | Source slope norm and a concrete sparse-depth derivative theorem |

The seven modules contain 785 lines including definitions and comments.
The 49 mathematical modules contain 5,404 lines. Counts include helper lemmas.

## 10. Remaining work

1. Formalize the terminal arithmetic r=b2^L-j and the full Euler wall normal form,
   including carry addresses and the regular complement.
2. Derive the local nearest-neighbor factorization and the stored higher-precision
   residue certificates from those Euler-defined objects, with all error budgets.
3. Supply the extra preparation and coordinate constructions for persistent
   multiple-residue branches where simple Hensel certificates do not suffice.
4. Prove the Euler-specific critical Wronskian/scalar nonvanishing, or classify
   an actual zero, in the remaining multiplier progressions. This remains a
   mathematical research question, not a compiler obligation.

No universal simplicity, unrestricted squarefreeness, new terminal-family atlas,
or larger binary-complexity classification is claimed.

## 11. Verification and provenance

The input v17 manifest verifies all 652 tracked files. The complete incoming
417-declaration project was freshly compiled and axiom-audited. All 42 incoming
mathematical modules remain byte-for-byte unchanged. The original v17 ZIP is
preserved in history/v17.

Two clean final replays compile and audit all 483 declarations, the second from
a separate mathematical source-tree copy and a different empty output directory.
See RELEASE_STATUS.json and evidence/v18_replay{1,2}/run.json for exact measured
results. Only Classical.choice, Quot.sound and propext are permitted in the
transitive axiom union. Unfinished proofs, custom mathematical axioms and native
proof evaluation are rejected by the source and compiler-output checks.

The standard-library exact/modular audit uses a Newton-built source, rational
Bernoulli recurrence, direct binomial translation, and polynomial differentiation.
Its 48-bit run passes 3,015 registered checks, including 272 two-channel product
identities, 640 all-coefficient differentiated-tail bounds, 528 exact packet-slope
products, and 16 denominator-free numerator Wronskian identities. Counts are
implementation checks, not substitutes for the Lean theorems.

The infinite-sum differentiation proof itself never relies on these samples.

### Development failures and recovery

The initial request for a streaming runtime-restoration session was rejected by
the container interface before execution. An ordinary polled subprocess restored
the hash-verified compact archive successfully. An early new-module compile
attempted to use a baseline dependency before its object file had been produced;
it failed and was rerun only after the required baseline output existed.

Development builds also rejected missing imports, coercion/typeclass mismatches,
incorrect API usage, and linter warnings. These were corrected before the final
clean replays. Their logs are retained in evidence/v18_development; no failed
build is counted as a passed verification. No mathematical assertion failed in
the retained exact/modular audit.

The runtime is Lean 4.34.0-rc2 with mathlib pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Both clean replays reuse the same
pinned cached dependencies; Lean and all of mathlib are not bootstrapped here.
No runtime binaries or font files are included in this source release.

## 12. Reproduction

Use fresh output paths to avoid overwriting retained evidence:

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_packet_derivatives.py --precision 48 --output /path/to/NEW_packet_checks.json
```

The source indexer is a project lexical utility, not an independent Lean parser.
Its complete declaration list is compared with the compiler's actual axiom-report
output. The trusted proof conclusion is the successful compilation and axiom
inspection, not merely a source-text scan.

## Sources

The v17 construction and all earlier mathematical modules are retained unchanged.
The new proofs use actual pinned mathlib infinite-sum, formal-derivative,
iterated-derivative, polynomial, and padic norm APIs. Online primary documentation
was consulted to distinguish the real/complex uniform-derivative theorems from
the coefficientwise dyadic argument used here; it is not substituted for the
compiled pinned source. Exact source hashes are recorded in PROVENANCE.json.

This is a formal extension of the Euler packet calculus. No claim of historical
novelty for ordinary differentiation, Hasse jets, or their product rules is made.
