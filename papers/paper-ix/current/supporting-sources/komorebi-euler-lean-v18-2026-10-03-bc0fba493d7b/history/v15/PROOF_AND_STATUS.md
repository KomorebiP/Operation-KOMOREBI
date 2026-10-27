# Euler Lean XV: the actual source, Bernoulli kernel, and sharp reconstruction tail

**Operation Komorebi — 3 October 2026 — continuation v15**

## Status and boundaries

This continuation constructs a specific restricted power series over the actual
dyadic integers and proves that its values on EVERY nonnegative integer are the
original Euler source. Its full coefficient reduction modulo eight, evaluation,
first analytic derivative nonvanishing, and a complete finite-coefficient cutoff
are kernel-checked. These statements no longer assume an unspecified source
satisfies a coefficient certificate.

The actual Bernoulli-defined coefficient kappa_m is constructed in Z_2. Its exact
valuation 4m-1 for m>0 is proved from mathlib's Bernoulli denominator theorem. The
actual paired falling-factorial packet has a checked block-composition identity,
a doubled-factorial identity, and finite support on nonnegative integer rows.

The resulting finite coefficient/source reconstruction has a sharp uniform tail
modulus 2^(4M+3), proved in Lean including failure of modulus 2^(4M+4) at the first
omitted row. This is a theorem about the EXACT reconstruction sum defined below.
Identification of that sum with an INDEPENDENTLY DEFINED signed Euler sequence
has NOT yet been formalized. We do not define Euler numbers to equal the desired
sum and then report its identification as a proof.

There are 224 indexed theorem/lemma declarations in 22 mathematical modules:
143 inherited and 81 new. The mathematical source has 2,549 lines, including
comments and definitions. These counts include helper lemmas, not independently
novel mathematical results. Two fresh-output compilations and complete transitive
axiom audits passed on identical mathematical sources, one from a separate copy.

No new terminal-family numerical atlas, global nondegeneracy theorem, exact
critical-scalar nonvanishing theorem, or mathematical coverage increase is claimed.
No historical-priority assessment was performed.

## 1. The Newton-source construction

Let D=Z_2 (`ℤ_[2]`), Q=Q_2 (`ℚ_[2]`), and retain v14's actual evaluation of a
restricted formal power series:

    reval f x = sum' n, coeff n f * x^n.

Define the rational number

    u_q = 2^q/(q+1)!.

Legendre's factorial bound gives

    v_2(u_q) = q-v_2((q+1)!) >= 0.

`sourceScalar q` is this actual rational number embedded in D, with its norm
bound proved. Define the tap

    c_q = sourceTap q = 4^q sourceScalar q = 8^q/(q+1)!.

Thus ||c_q|| <= (1/4)^q. No division by a nonunit is performed inside D without
first proving the rational quotient is integral.

Let (X)_q denote the falling factorial `descPochhammer D q`. Define N coefficientwise:

    coeff n N = sum' q, c_q * coeff n (X)_q.

The construction proves convergence of each sum. More strongly,

    coeff n N = 4^n * sum' m, 4^m * u_(m+n) * coeff n (X)_(m+n).

The remaining factor is in D. Hence N is restricted and its Taylor coefficients
have at least the geometric 4^n bound.

An explicitly proved summable double series justifies changing coefficient and
packet summation order. Consequently

    reval N x = sum' q, c_q (x)_q                     for every x in D.

This is not a formal substitution that assumes evaluation commutes with an
uncontrolled infinite sum.

## 2. The original Euler source on every integer row

The integral geometric series

    I(X) = sum_(n>=0) (-2)^n X^n

is restricted and satisfies

    (1+2X) I(X) = 1.

Define the actual source series

    source(X) = I(X) N(X).

Restrictedness follows from the ring theorem for restricted series. Evaluation
of multiplication by the linear polynomial is proved directly by convergent
summation, giving

    (1+2x) reval source x = reval N x                for every x in D.

At a nonnegative integer n, all packets q>n vanish. The kernel checks the exact
binomial identity

    (n+1)c_q (n)_q = 8^q choose(n+1,q+1).

The finite binomial theorem now gives

    8(n+1) reval N n = 9^(n+1)-1.

Therefore, in Q_2,

    qeval source n
      = (9^(n+1)-1)/(8(n+1)(2n+1))
      = (3^(2n+2)-1)/(4(2n+1)(2n+2)).

`eulerSource_original_formula` proves this for every n, not for a finite test range.
The source is constructed on all Z_2 by the convergent series above. The release
does not additionally identify its special value at -1 with a p-adic logarithm,
or prove the equivalent 9^x expression for noninteger x in a separate exponential
API. Neither is needed for the stated integer-row formula and unit theorem.

## 3. Complete source residue certificates and analytic consequence

For any precision P and cutoff Q with P<=2Q, every omitted tap has zero residue
modulo 2^P. Let

    N_Q(X) = sum_(q<Q) c_q (X)_q.

The compiled theorem proves for EVERY coefficient n:

    coeff n N mod 2^P = coeff n N_Q mod 2^P.

This includes all omitted Taylor coefficients. It uses continuity of the actual
residue homomorphism to map a convergent sum, not just agreement of a finite vector.

At P=3 and Q=2,

    N(X) = 1+4X mod 8.

The exact linear inverse identity then gives the full series certificate

    source(X) = 1+2X+4X^2 mod 8.                   [coefficientwise]

Using the inherited infinite-series soundness bridge, Lean derives

    reval source x = 1+2x+4x^2 mod 8,
    J_1(source,x) = 2 mod 8.

The v14 analytic derivative identity identifies J_1 with the genuine derivative
of qeval at every integral dyadic argument. Thus the ACTUAL source derivative is
nonzero everywhere on Z_2. This is a source statement, not a nondegeneracy theorem
for an arbitrary sum of Euler packets.

Already modulo two the source is coefficientwise one. Its values are therefore
nonzero dyadic units, with norm exactly one throughout Z_2.

## 4. Actual Bernoulli kernel and sharp valuation

Define, over Q,

    kappa_m = -2^(4m) (2m-1) B_(2m).

Here 2m-1 is the rational expression, so m=0 gives kappa_0=1 rather than a natural
subtraction artifact. `eulerKappaRat` uses mathlib's actual `bernoulli` function.

For m>0, the imported theorem `Bernoulli.padicValRat_bernoulli` gives

    v_2(B_(2m))=-1.

The odd factor has valuation zero. Multiplication gives exactly

    v_2(kappa_m)=4m-1.

Nonzero coefficients and nonnegative valuations are proved before embedding them
in D. In the actual dyadic ring/field, the exact norm theorem is

    ||eulerKappa m|| = 2^(-(4m-1))                 for m>0.

This is an arithmetic proof from the Bernoulli definition and denominator theorem.
It does not assume the valuation as a field in a structure. The separate generating
function identity identifying the beta/kappa series as a hyperbolic inverse has
not yet been formalized in this project.

## 5. Actual packet algebra and three source taps

The new polynomial `eulerPacket q` is the product

    P_q(X) = product_(i<q) (X-i)(2X-2i-1).

Lean proves

    P_(a+b)(x) = P_a(x) P_b(x-a),
    (2x)_(2q) = 2^q P_q(x),
    P_q(n)=0 when n,q are nonnegative integers and q>n.

The proofs hold in the actual dyadic ring. The finite support identity permits
exact truncation of a finite packet sum on original integer offsets.

Set

    W_n=(n+1)(2n+1) reval source n.

From the all-row source formula,

    8W_n=9^(n+1)-1.

The exact three-tap relation is now compiled:

    W_(n+2)-10W_(n+1)+9W_n=0.

Thus the tap polynomial (xi-1)(xi-9) annihilates the denominator-cleared source.
The theorem does not incorrectly drop the polynomial weight from the source.

## 6. Sharp bound for the finite reconstruction and its actual error

Define the summand, finite row, retained prefix and omitted tail using precisely
the constructed source and Bernoulli coefficient:

    T(N,m)=kappa_m choose(2N,2m) source(N-m),
    R_N=sum_(m=0..N) T(N,m),
    R_(M,N)=sum_(0<=m<=N, m<=M) T(N,m),
    Tail_(M,N)=sum_(0<=m<=N, M<m) T(N,m).

Natural subtraction in the displayed source argument is used only in sums where
m<=N. Lean proves

    R_N-R_(M,N)=Tail_(M,N).

Integral binomial coefficients have norm at most one and source values have norm
one. The ultrametric finite-sum inequality therefore gives for every M,N:

    ||Tail_(M,N)|| <= 2^(-(4M+3)),
    Tail_(M,N) = 0 mod 2^(4M+3).

If N<=M the tail is exactly zero. At N=M+1 it has only one term:

    Tail_(M,M+1)=kappa_(M+1).

Consequently

    ||Tail_(M,M+1)|| = 2^(-(4M+3)),
    Tail_(M,M+1) != 0 mod 2^(4M+4).

The claimed reconstruction bound is therefore UNIFORMLY OPTIMAL, with an explicit
witness row for every M. The proof is complete for the reconstruction as defined.

IMPORTANT: `R_N = E_(2N)` for an independently specified signed Euler sequence is
NOT a theorem in this release. The generic truncation theorem becomes a formally
identified Euler-number error theorem only after that equality is proved. This
is a remaining identification task, not a condition hidden in the definition.

## 7. What is closed and what remains

Closed in Lean here:

- Actual integral Newton taps and their decay.
- Actual restricted numerator/source with justified double-sum evaluation.
- Source agreement with the original formula on every nonnegative integer.
- Complete numerator truncation and complete mod-eight source certificate.
- Unit source values and nonzero genuine first derivative throughout Z_2.
- Bernoulli-defined kappa coefficients with their exact 4m-1 valuation.
- Actual packet block/paired-factorial/finite-support identities.
- The source's exact three-tap annihilator after its required weight.
- Sharp finite reconstruction error modulus and its first-row optimality witness.

Remaining formal construction:

1. Prove the generating-function identity / recurrence identifying R_N with the
   independently defined signed Euler numbers.
2. Construct the infinite H_r and normalized G_r from the full Euler coefficients,
   prove their convergence and exact finite-tail factorization, and derive the
   normalization/minimum/carry claims in Lean.
3. Derive the actual local nearest-neighbor identities and numerical residue
   certificates from those original-index definitions, including each tail bound.
4. Finish general affine translation and full-disc preparation/chart constructions
   where needed by arbitrary local branches. The v14 direct simple-root theorem
   itself requires neither a guessed truncation nor unproved preparation.

Remaining mathematics, unchanged:

- Exact critical-scalar nonvanishing or a classified exact zero in the surviving
  terminal-129 and terminal-161 multiplier progressions.
- No universal Euler simplicity or squarefreeness over algebraic extensions.

No earlier manuscript terminal-degree or binary-complexity bound is promoted to
an end-to-end Lean corollary here.

## 8. Evidence and trust boundary

All 148 tracked entries in the incoming v14 manifest matched. The entire inherited
143-declaration project was recompiled and axiom-audited before development.
The unmodified tracked v14 snapshot is retained in history/v14.

The final mathematical sources were compiled from two different fresh output
directories, the second time from a separate source-tree copy. Every one of the
224 indexed declarations was subjected to #print axioms in each replay. The
permitted transitive union was exactly

    Classical.choice, Quot.sound, propext.

No custom mathematical axiom, unfinished proof or native-evaluation proof axiom
was accepted. Definitions and helper lemmas are included in the source; the named
theorem count does not express a count of novel results or discharge unstated
hypotheses in the inherited collision theorems.

The Lean runtime is 4.34.0-rc2; mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Replays use cached pinned mathlib dependencies; neither Lean nor all of mathlib was
rebuilt from source. Full machine-readable runs and axiom lists are supplied.

A separate exact Python Fraction audit checks 33 rows against Euler numbers
obtained from the independent cosh-reciprocal recurrence, as well as 528 nonempty
tail bounds. All 691 registered finite checks passed. This corroborates the
alignment but does NOT replace the missing universal Lean Euler identification.

### Failures and recovery

Runtime extraction exceeded one tool call's time budget. Resuming extraction left
one partial cached dependency, which was identified by its wrong byte length and
re-extracted. The combined runtime archive hash matches the inherited pin. The
first combined baseline replay also exceeded the interaction call budget and was
repeated to completion in a separately polled process.

Development compilations caught API names, numeral-coercion mismatches, summation
order/associativity details and warnings treated as errors. One attempted kernel
`decide` proof of a polynomial equality did not reduce; it was replaced by an
ordinary explicit ring-homomorphism proof. All failed development diagnostics are
retained separately from the two successful final replays. No failure is counted
as a successful theorem.

## 9. Reproduction

Python 3.10+ is sufficient for the scripts. The mathematical project requires the
pinned Lean and mathlib described above. Runtime binaries are not distributed.

    python3 scripts/verify_manifest.py
    python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
        --evidence /path/to/NEW_replay_directory
    python3 scripts/check_rational_alignment.py --output /path/to/NEW_alignment.json

The replay refuses an existing output directory and excludes preexisting compiled
project modules. Mathematical sources are hashed before and after compilation.
Development build files are intentionally not part of the source release.

## Sources

The pinned mathlib sources supply the actual Bernoulli function and its proved
von Staudt-Clausen consequence, p-adic rings/fields/valuation, finite binomial and
Pochhammer identities, restricted-series ring operations, and infinite-sum tools.
Official API reference:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/Bernoulli.html

The exact imported source hash is recorded in PROVENANCE.json; current online
documentation is not substituted for the pinned compiled dependency.
The v14 construction and proof boundaries are retained unchanged in history/v14.
The Newton-source and packet/tail deductions in this release are given by the
new Lean modules. No historical-priority claim is made for those formulations.
