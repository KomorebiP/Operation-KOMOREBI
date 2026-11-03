# SF-LEAN-B11: real types and exact radial order

For the actual canonical pair with 0<q,r,a,b<1, this block proves the remaining
type and limit conclusions of Theorem F.2 in its maximum-modulus convention:

\[
0<c_-w_i\le\underline\tau_i\le\overline\tau_i\le c_+w_i<\infty,
\qquad
\lim_{R\to\infty}\frac{\log\log M_i(R)}{\log R}=\rho.
\]

The types are actual real filter liminf/limsup values of log(M_i(R))/R^rho
atTop. Their boundedness and coboundedness premises are proved, not supplied
by default-value conventions. M_i(R) is explicitly the real supremum of
the norm image of the complex sphere. For R>=0 it equals the positive real
component and is attained; the equality includes R=0. The corresponding
limsup definition of radial order is proved equal to rho. The constants
are those already constructed in Blocks09-10; all bounds are finite real
numbers, with strictly positive lower coefficients.

The new source `lean/CoupledGrowthTypes.lean` has **22 named theorem
declarations**, including supporting lemmas. The registered scope is **273
names**: 39 inherited finite-core names and 29,21,19,16,13,19,23,22,16,34,22
in Blocks01-11. This completes the registered canonical F.2 growth contract,
including both explicit comparisons from Blocks09-10. It does not prove
F.3, all ancillary claims in Appendix F, or full monograph coverage.

## Proof and correspondence

Authority: the type convention and Theorem F.2 in
`monograph/sections_v11/coupled_growth_full.tex`, lines 159-197 and 348-350
at the base revision. `realComponent` supplies a Fin 2-indexed version of
the actual UReal/VReal functions. `growthRatio`, `lowerType`, `upperType`,
`radialExponent` and `radialOrder` state the exact real conventions.

The two-sided growth-ratio theorem from Block10 yields eventual upper and
lower bounds on each ratio. A general real type sandwich constructs both
IsBoundedUnder witnesses. The upper bound supplies the coboundedness needed
by le_liminf_of_le; the lower bound supplies that needed by limsup_le_of_le.
Both boundedness witnesses and the nontrivial atTop filter justify
liminf_le_limsup. The positive explicit lower coefficient then proves both
types positive. The result asserts real finite bounds, not an extended-real
liminf assigned a convenient finite default.

For the radial exponent, write a<=log(F(R))/R^rho<=b with a,b>0. At R>1,
R^rho and log(R) are positive. Multiplication first gives log(F(R))>0.
Taking logarithms of the two positive comparisons and dividing by log(R)
gives the squeeze

\[
\rho+\frac{\log a}{\log R}
\le\frac{\log\log F(R)}{\log R}
\le\rho+\frac{\log b}{\log R}.
\]

Since log(R) tends to +infinity, both perturbations tend to zero. The
eventual squeeze theorem gives the full atTop limit; its limsup is rho.
This generic argument works for any real rho whenever its stated positive
comparison hypotheses hold, so no hidden rho>=1 condition is introduced.
For the canonical functions, positivity of F(R) is separately proved from
the existing linear lower bound.

Block08's spherical IsGreatest theorem is converted to the new real
supremum `maximumModulus`. A supremum equality is used only when the sphere
is nonempty (R>=0), with its greatest point supplied as a witness. Eventual
equality transports the type definitions and radial limit to this actual
spherical supremum. A second interface supplies the same statements for
the norm at the positive real point.

The exact interfaces and 22-name source map are in CLAIM_MAP.json and
declarations.json. This proof does not assert convergence of the normalized
growth ratio itself or uniform angular growth. Those are not conclusions
of F.2 in the manuscript. F.3 concerns proportions of lower/upper types,
not an unconditional ordinary type limit.

## Verification and file I/O

The [receipt](evidence/receipt.json) records **48 passing steps**: version,
nine dependency revisions, warning-as-error compilation and exact axiom
audits for eleven coupled modules, same-kernel replay of those modules,
four rejection controls and one positive fixture file. All **234 coupled
declarations** are freshly axiom-audited; the finite core's 39-name evidence
is inherited. Allowed logical axioms are propext, Classical.choice and
Quot.sound. Pinned Mathlib is cached rather than freshly rebuilt/replayed.
Review provenance is self-review, not independent review.

The first fresh replay stopped during the older CoupledRescaling axiom audit
with a process allocation failure (`std::bad_alloc`). Its receipt, raw logs
and retry resource observation are preserved under `attempts/`. The accepted
fresh run uses a new directory and the same mathematical inputs. Only its
48 passing steps are used as the accepted proof evidence.

The controls reject feeding a one-sided eventual bound to the real type
sandwich, a zero lower coefficient in the logarithmic squeeze, replacing
the radial exponent limit by a type-ratio limit, and a placeholder. They
are API/domain rejections, not blanket counterexample theorems. Positive
fixtures consume the constant-two type sandwich, the radial exponent of
exp(2R), a fractional exponent example, canonical type bounds for either
component, the maximum at zero, and the actual maximum-modulus limit.

```text
python tools/verify_coupled_growth_types.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block11
```

Use a new external work directory. --git and --packages support other local
layouts. The verifier performs no installation or network access. Lean is
4.34.0-rc2; Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The
topological liminf/limsup module was already cached.

[IO_MANIFEST.json](IO_MANIFEST.json) hashes 41 formal replay inputs, 49
packaged outputs, eleven generated objects and 27 staged source copies.
It separately hashes the 16 inputs and two outputs used for the remaining-
work assessment, and inventories the preserved failed replay separately.
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) seals all
immutable block records, the dated guide, evidence, formal inputs and the
bounded assessment's source files. It excludes itself and live guidance.
This is not a new complete archive validation.

## Checkpoint and remaining work

Base: 1c7814ef551709f44547561fe9b04ff7f9faa505. Cutoff and assessment are
this same SF-LEAN-B11 source-bound checkpoint. The real bounded-filter and
logarithmic-squeeze route resolves the registered F.2 target. An extended-real
route is deferred for unbounded profiles; its first uncertainty is excluding
infinities before converting to real types. A direct little-o route is
deferred for sharper errors; its first uncertainty is positive-domain
transport. Neither alternative is refuted or exhausted. No delegated or
delayed runs remain. Earlier reports preserve earlier route histories.

The next executable target is **F.3's Perron proportions**. Start with
scaled liminf/limsup transport for p(R-1) and pR, then prove the componentwise
type-vector inequalities from the existing lower/upper recurrences. Use the
positive left characteristic vector to turn each inequality into equality,
and prove the eigenvalue-one space is one-dimensional. Recover the type
ratios and the equivalence of ordinary type-limit existence for the two
components. Do not infer ordinary type convergence merely from F.2.

[REMAINING_WORK.md](REMAINING_WORK.md) and its machine-readable counterpart
give a source-bound chapter-level inventory: ancillary Appendix F identities,
operator classification H.1, the resolution/evaluation certificates in I-J,
and the much wider analytic development in A-E. This is a correspondence
inventory, not a new whole-manuscript proof audit or a completion percentage.
Earlier proof blocks, source manuscripts and reading PDFs are preserved.
