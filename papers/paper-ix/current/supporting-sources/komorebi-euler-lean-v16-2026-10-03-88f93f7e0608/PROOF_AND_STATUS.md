# Euler Lean XVI: independent Euler identification and the sharp Euler error theorem

**Operation Komorebi — 3 October 2026 — continuation v16**

## Status and exact boundary

This release closes the first formal obligation left by v15: the constructed
Bernoulli/source reconstruction equals the independently defined signed Euler
sequence at EVERY nonnegative row. The Euler sequence is defined from the inverse
of the rational formal cosh series. Its definition contains neither the source,
the Bernoulli kernel, nor the reconstruction sum.

The proof is an identity of formal power series over Q, followed by exact
coefficient extraction and a checked embedding into the actual dyadic integers.
The usual even Euler recurrence, odd vanishing, ordinary integer-valuedness, and
uniqueness under the cosh convolution recurrence are proved as well.

Consequently the existing sharp finite reconstruction-tail modulus is now a
formally identified Euler-number error theorem. The first omitted row witnesses
failure of a modulus one binary digit stronger, for every truncation depth.

There are 55 new theorem/lemma declarations in six new modules, bringing the
project to 279 declarations in 28 modules. These counts include helper lemmas and
are not counts of novel mathematical results. All 22 inherited mathematical
modules are unchanged.

No new terminal-family atlas or numerical coverage bound is claimed. The infinite
row residuals H_r and G_r, their actual carry normalization and local coefficient
certificates, still need their end-to-end Lean construction. The surviving
critical-scalar questions remain mathematical research obligations. Neither
universal Euler simplicity nor squarefreeness over extensions is proved here.

## 1. Independent Euler definition

Use the rational formal power-series ring Q[[t]]. Define

    exp_a(t) = rescale(a, exp Q),
    C_a(t) = (exp_a(t) + exp_(-a)(t))/2.

The implementation expresses multiplication by 1/2 through the constant-series
ring map; it does not use an inverse of the variable t. Formal exponential
multiplication and differentiation come from the pinned mathlib library.

Define independently

    EGF_Euler(t) = C_1(t)^(-1),
    E_n = n! * [t^n] EGF_Euler(t).

In Lean these are `signedEulerEGF` and `signedEulerRat`. The constant coefficient
of C_1 is one, so its inverse is a genuine formal-series unit inverse.

The coefficients of C_a are proved to be

    [t^(2n)] C_a = a^(2n)/(2n)!,
    [t^(2n+1)] C_a = 0.

The signed convention is therefore the reciprocal-cosh convention, with
E_0=1, E_2=-1, E_4=5, E_6=-61.

## 2. The actual Bernoulli kernel at the generating-function level

Let

    B(t) = sum_(n>=0) B_n t^n/n!,
    A(t) = B(4t),
    K(t) = A(t) - t A'(t).

The actual Bernoulli generating-function theorem gives

    A(t)(exp_4(t)-1) = 4t.

Formal differentiation gives

    A'(t)(exp_4(t)-1) + 4 A(t) exp_4(t) = 4.

An exact ring calculation combining these two equalities yields

    K(t)(exp_4(t)-1)^2 = 16 t^2 exp_4(t).               (1)

This is `formalKernel_cleared_identity`. There is no convergence assumption and
no division by t or by exp_4-1.

Coefficient extraction gives, for every n,

    [t^n]K(t) = (1-n) 4^n B_n/n!.

The odd coefficients vanish: the degree-one factor is zero, and every other odd
Bernoulli number vanishes. At even indices,

    [t^(2m)]K(t) = kappa_m/(2m)!,
    kappa_m = -2^(4m)(2m-1)B_(2m).

This is the SAME `eulerKappaRat` whose sharp valuation and dyadic embedding were
proved in v15. The degree-zero formula gives kappa_0=1. No new coefficient sequence
is substituted for the arithmetic kernel.

## 3. The actual source at the generating-function level

Define S by shifting the coefficient sequence of C_3-C_1 two places and dividing
by four. Its first two removed coefficients are both zero. Lean proves

    4t^2 S(t) = C_3(t)-C_1(t).                        (2)

It then proves that S has zero odd coefficients and

    [t^(2N)]S(t) = A_N/(2N)!,
    A_N = (9^(N+1)-1)/(8(N+1)(2N+1)).

The v15 Newton-source theorem proves that the constructed restricted source has
value A_N at every nonnegative integer N. The new lemma `eulerSource_reval_rat`
connects that exact analytic evaluation to this rational expression in Q_2.

Thus this formal EGF and the already-constructed p-adic source describe exactly
the same sequence of integer-row values. The two variables have different roles:
t is a formal EGF variable; x is the dyadic row argument of the restricted source.

## 4. The central all-row identity

The exponential product law proves

    4(C_3-C_1)C_1 = exp_4 + exp_(-4) - 2.

Together with (2), this gives

    16t^2 S(t)C_1(t) = exp_(-4)(exp_4-1)^2.           (3)

Multiply by K and use (1) and exp_(-4)exp_4=1. Both sides contain the nonzero
factor 16t^2. Cancelling that factor in the integral domain Q[[t]] gives

    K(t) S(t) C_1(t) = 1,

hence

    K(t) S(t) = EGF_Euler(t).                         (4)

This is the theorem `formal_euler_reconstruction`. It proves the generating-
function identity from the existing Bernoulli definition and independent cosh
series. It does not define the target Euler series as K*S.

Now use the finite Cauchy product at coefficient 2N. The checked parity-sum
lemma removes every odd index. Multiplication by (2N)! converts the remaining
factorial ratio into an actual binomial coefficient. Therefore

    E_(2N) = sum_(m=0..N) kappa_m choose(2N,2m) A_(N-m)   (5)

for EVERY N. This is `signedEulerRat_reconstruction` over Q.

Each coefficient extraction is a finite sum even though the ambient identity is
between infinite formal series. There is no interchange of uncontrolled analytic
limits in this step.

## 5. Independent recurrence, parity, uniqueness, and integrality

From the defining inverse identity, Lean proves

    sum_(m=0..N) choose(2N,2m) E_(2m) = if N=0 then 1 else 0.

Equivalently,

    E_(2(N+1)) = -sum_(m=0..N) choose(2(N+1),2m) E_(2m).

It also proves E_(2N+1)=0 and the initial values listed above.

`signedEulerRat_even_unique` states that ANY rational sequence satisfying this
cosh convolution recurrence equals the defined even signed Euler sequence.
This makes the identification with the standard recurrence explicit.

Strong induction on the recurrence proves ordinary integrality:

    forall n, exists z:Z, E_n = (z:Q).

The integer-valuedness proof uses only the recurrence and finite sums; it is not
an integrality hypothesis imported into the reconstruction theorem.

## 6. End-to-end dyadic Euler truncation and optimality

The cast theorem is

    (reconstructionRow N : Q_2) = (E_(2N) : Q_2).

The dyadic norm bound on reconstructionRow proves that the independent rational
Euler number can be embedded in Z_2. `signedEulerEven N` is that actual rational
cast with its proved norm bound, not a synonym for reconstructionRow.

Lean proves their equality in Z_2:

    reconstructionRow N = signedEulerEven N.

Keep the v15 retained prefix without changing its definition:

    reconstructionTrunc M N
      = sum_(0<=m<=N, m<=M) kappa_m choose(2N,2m) source(N-m).

The new final theorems are

    signedEulerEven N - reconstructionTrunc M N = reconstructionTail M N,

    redPow (4M+3) (signedEulerEven N - reconstructionTrunc M N) = 0,

    ||signedEulerEven N - reconstructionTrunc M N||
      <= 2^(-(4M+3)).

At the first omitted row,

    signedEulerEven (M+1) - reconstructionTrunc M (M+1) = kappa_(M+1),

    ||signedEulerEven (M+1) - reconstructionTrunc M (M+1)||
      = 2^(-(4M+3)),

    redPow (4M+4) (signedEulerEven (M+1) - reconstructionTrunc M (M+1)) != 0.

These are now sharp error theorems ABOUT THE INDEPENDENT EULER SEQUENCE. The
source/kernel/reconstruction alignment gap recorded by v15 is closed.

If N<=M the retained prefix is exactly the Euler number. Empty tails are handled
without introducing a finite value for the valuation of zero.

## 7. New module map

| Module | Declarations | Role |
|---|---:|---|
| EulerFormalKernel | 9 | Scaled Bernoulli identity, differentiation, cleared kernel formula |
| EulerFormalSource | 9 | Independent cosh/inverse, source EGF, formal product identity |
| EulerIdentification | 8 | Kernel/source coefficients, parity projection, all-row rational equality |
| EulerSequence | 12 | Independent cosh recurrence, odd vanishing, uniqueness, initial values |
| EulerIntegrality | 2 | Ordinary integer-valuedness at all indices |
| EulerError | 15 | Actual dyadic cast, Euler error identity, sharp modulus and optimality |

The six modules contain 529 lines including comments and definitions. All 22
inherited mathematical modules remain byte-for-byte identical.

## 8. Remaining formal and mathematical obligations

1. Construct H_r and G_r from the actual infinite packet sum, prove convergence,
   the whole-tail factorization, and the carry/minimum normalization in Lean.
2. Derive the exact nearest-neighbor coefficient factorizations and numerical
   residue certificates FROM those Euler-defined functions, including all
   omitted-packet precision bounds.
3. Formalize any additional translation, closed-disc preparation and chart
   constructions needed for persistent multiple-residue branches. The existing
   v14 simple-root bridge already handles genuine restricted-series evaluation
   and derivatives when its coefficient hypotheses are supplied.
4. Prove exact critical-scalar nonvanishing, or classify an exact zero, in the
   unresolved arithmetic progressions. This remains a mathematical research
   question and is not discharged by compilation.

No previous manuscript terminal-degree or bit-complexity bound is relabeled as
an end-to-end Lean theorem in this release. The uniform Euler truncation theorem
is now end-to-end; the full rowwise collision classification is not.

## 9. Verification and trust boundary

See `RELEASE_STATUS.json` and `evidence/replay1/run.json`,
`evidence/replay2/run.json` for the executed results and timings. The second
replay uses a separate source-tree copy and a new empty project output directory.
Both builds import the same pinned cached mathlib dependencies; neither Lean nor
the entirety of mathlib is bootstrapped from source here.

The input v15 manifest checked all 293 tracked files. Its entire 224-declaration
project was recompiled and axiom-audited before development. Runtime recovery
verified the exact inherited combined XZ archive hash before extraction. The
restoration completed without an extraction timeout in this run.

Both completed clean replays passed: 59.157264 and 58.664216 seconds. Each
compiled all 28 modules and audited all 279 indexed declarations. All 30 output
.olean files (modules, root and audit) had identical hashes between the two
replays before compiled artifacts were removed from the source release.

All 279 indexed declarations are included in each final `#print axioms` audit.
Only Classical.choice, Quot.sound and propext are permitted. The source indexer
is a lexical project utility, not an independent Lean parser. Its coverage is
checked against the compiler's actual axiom-report output.

The supplementary exact Python Fraction audit checks rows N=0..128 against the
independently generated cosh-reciprocal recurrence, including all 8,256 nonempty
finite-tail bounds in those rows. It passes 8,899 registered checks. These are
corroboration, not the proof of the universally quantified Lean statements.

### Development diagnostics

Early development compilations encountered a module-search-path collision while
reusing the baseline build, nonmatching coercion normal forms, a misplaced tactic
`by`, unused simp arguments, a renamed conditional lemma, and concrete binomial
normalization issues. They were corrected before final clean replays. Diagnostic
probes containing deliberately queried unavailable API names are retained only
as logs, not as mathematical source modules. No unfinished proof or custom axiom
is accepted in the release. The final verification status is reported from the
actual clean replay outputs, not the development attempts.

## 10. Reproduction

Use the pinned Lean 4.34.0-rc2 and mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_rational_alignment.py --limit 128 --output /path/to/NEW_check.json
```

The replay refuses existing output directories, starts with no project compiled
outputs, and hashes the mathematical source before and after compilation. Runtime
binaries and dependency caches are not part of this source package.

## Sources and attribution

The Bernoulli generating-function identity, formal exponential multiplication,
formal derivation, inverse power-series operations, factorial/binomial identities,
and actual p-adic casts are supplied by the pinned mathlib sources. Exact hashes
are recorded in PROVENANCE.json. Online documentation was consulted to locate the
relevant primary APIs, but was not substituted for the compiled pinned source:

- https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/Bernoulli.html
- https://leanprover-community.github.io/mathlib4_docs/Mathlib/RingTheory/PowerSeries/Exp.html

This is a formalization of the previously derived Euler reconstruction, not a
claim of historical novelty for the Euler/Bernoulli generating-function identities.
