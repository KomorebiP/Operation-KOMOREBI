# Later-paper bridge audit

The original sections below are retained from the v0.3.0 audit. They describe
that earlier checkpoint, not the subsequently expanded v0.10.0 contract.

## Purpose and evidence boundary

This audit examined later Projector Calculus manuscripts, the corpus claim
ledger, the theorem inventory, the migration ledger, and the monolithic Lean
browser source for material relevant to Paper IV. Later TeX arguments informed
the proof design described below, but they are **not Lean evidence**. A result
counts toward Paper IV's formal coverage only after it is stated, compiled, and
kernel-audited in the `Komorebi.PaperIV` project.

The reviewed later sources are audit inputs. This note does not assert that
they are files in the Paper IV release.

## Pinned formal environment

- Lean: `leanprover/lean4:v4.34.0-rc2`
- Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Authoritative entry point: `formalization/lean/KomorebiPaperIV.lean`

## Monolithic browser decision

`Komorebi_Projector_Calculus_Lean_Browser_Full.lean` was compiled independently
against the exact Lean and Mathlib revisions above. Compilation failed with
**59 errors and 81 warnings**, and no valid object file was produced. The
failures include dependent-type mismatches, invalid field notation, parser
errors, missing instances, and unsolved goals.

The source contains no literal `sorry`, `admit`, or `axiom`. That fact does not
make it a certificate: after an elaboration error, Lean may display synthetic
`sorry` terms while recovering sufficiently to report later errors. The file is
therefore excluded from imports and from every formal-coverage count. Its
`ClaimRecord` entries are data, not theorem declarations.

## Useful proof blueprints

| Paper IV target | Audited later source and result | How it informed the Lean plan | Evidence status |
| --- | --- | --- | --- |
| 3.2; parts of 6.4 | Paper VII, **Cyclic quantum projectors** | Finite-character covariance, orthogonality, completeness, and a spectral route for a rescaled signed shift | TeX proof blueprint only |
| 4.5 | *Transfer Calculus: Pole Asymptotics Edition*, `HYP-001` and `HYP-002` | Direct factorial/Pochhammer coefficient calculation for the residue sections and signed denominator | TeX proof blueprint only |
| 6.4--6.6 | Paper VI, **Packet-path exponential**; Paper VII, **Finite Euclidean transfer**; Paper IX, **Companion jump theorem** | Matrix-power entries, exponential semigroup laws, and companion-shift iteration | TeX proof blueprints only |
| 6.4 | Paper XII, **Bezout primary projectors** | Possible primary-projector route to the simple spectrum of `X^N + 1` | Indirect TeX blueprint only |
| 7.2, 7.3, 7.7, 7.8 | *Transfer Calculus: Pole Asymptotics Edition*, `TRI-004` and `TRI-005` | Reciprocal tower recurrence and the partition/rising-factorial formula, yielding degree, leading term, initial polynomials, and the factor `r` | TeX proof blueprint only |
| 9.4 | Paper IX, **Unit EGF coordinate change** and **Triangular congruential inverse** | Generic unit-series and triangular-inversion organization; arbitrary residue order still requires a Paper IV proof | TeX proof blueprints only |
| 13.1--13.4 | *Transfer Calculus: Pole Asymptotics Edition*, `SPEC-002` | Conditional nearest-simple-pole coefficient estimate for reciprocal order one | TeX proof blueprint only |
| 12--14 architecture | *Projector-Generated Odd Zeta Calculus I*: **Odd-zeta trace theorem**, **Barnes determinant formula**, **Odd-zeta logarithm**, and **Hurwitz polyphase refinement** | Design analogies for diagonal spectral sums, products, logarithmic coefficients, and Hurwitz comparison | TeX architecture only; not a reusable certificate |

Paper X's seed zeta counts finite deformation levels and is not Paper IV's
analytic zero zeta. Paper XII's finite companion obstruction concerns companion
forests, not the signed companion matrix `J_N`. These similarly named objects
are not interchangeable.

## Ledger caveat

The browser and CSV claim ledgers describe an older 54-record Paper IV and are
stale relative to the revised 95-record manuscript. In particular, they still
mark the simple-zero, zero-continuation, and derivative-weight questions as
conjectural. The migration ledger also says that the original Amice pullback,
derivative conjugacy, and weighted convergence material moved to Paper IX, but
those named results were not present in the audited Paper IX source. Migration
records therefore document editorial intent, not formal or current article
evidence.

## Remaining infrastructure gaps

The later sources do not supply checked Lean implementations for:

- convergence and pointwise evaluation of the formal series;
- analytic ODE solution spaces and Wronskians;
- the specialized determinant identity for the companion-matrix exponential;
- indicator functions, dominant-sector estimates, and localization of large
  zeros;
- genus-zero canonical products and Mittag--Leffler expansions;
- trace-class operators and Fredholm determinants;
- higher-order pole asymptotics and the zero-zeta continuation arguments.

These claims must remain outside the Lean contract until the required
infrastructure and theorem-specific proofs are present in the pinned Paper IV
project.

## Targeted source inspection on September 5, 2026

Eight recovered TeX sources from Papers V, VI, VII, IX, X, XI, and XII were
searched for Wronskian, Bell-polynomial, Hadamard, Fredholm, zero-localization,
and zeta material. They are manuscript inputs, not checked Lean dependencies.
The Bell-state material in VII and the residual-seed zeta in X concern
different objects. None of these source files supplied a checked Lean proof
for the missing Paper IV analytic infrastructure. The new Bell, entire,
Wronskian, and companion bridges were proved locally from the pinned Mathlib
and Paper IV declarations.

Source-byte identities for this targeted inspection:

| Source | SHA-256 |
|---|---|
| `Projector_Resolved_Seed_Calculus_IX.tex` | `53e6cd9aa64a778a98f7d1fc38b22df810d96e5e2a3c50afbf7791d91c2f4606` |
| `Projector_Resolved_Seed_Calculus_V.tex` | `3cf53ca91b25c3c0db8fb2e3517fa35836d5338ebb127474795f26f8ac30253d` |
| `Projector_Resolved_Seed_Calculus_VI(1).tex` | `4fba354838ffa86356813a8e89a08ffe58f0ac1fc979ef57a633e8bd292ce0bb` |
| `Projector_Resolved_Seed_Calculus_VI.tex` | `23ffe9d3b90cd4c92294389c57597bdeaa3357eaddde05094670c4043520b5bd` |
| `Projector_Resolved_Seed_Calculus_VII.tex` | `17570d8125feaba00f824e86a4afd734d295a28ddd483b86a06d3c8742aee544` |
| `Projector_Resolved_Seed_Calculus_X.tex` | `1ad8a3d73a12b49146f3e1164def45f6af882edc86670a89e5bb0ac0fbe48c98` |
| `Projector_Resolved_Seed_Calculus_XI.tex` | `12f155557bbbca2076e4080bd3a3627c85e9dc26484a167647f4022f4637ea40` |
| `Projector_Resolved_Seed_Calculus_XII.tex` | `6d33333b27967d2cf713a8046f13d306ec22092a13e673d0c03a77dd7243d914` |

The remaining-infrastructure list above is historical. In v0.10.0, transfer
and signed convergence, both Wronskians, and first-column/trace bridges are
closed. The theorem map gives the current remaining boundary.

The v0.11.0 contract further closes unweighted zeta continuation, exact order-two/four models and branch dependence. Its full canonical product now has exact multiplicities and an entire nonvanishing quotient; the growth bound needed for Hadamard identification remains open.

The v0.12.0 contract proves the actual quotient-growth bound and Hadamard equality, then closes Newton zero sums, the analytic logarithm series, Mittag-Leffler fractions and the tangent/reciprocal/theta Bell formulas. At that release, eight results remained unmapped and the determinant and coefficient-asymptotic layers remained open.

The v0.13.0 contract completes the exact growth/order/type and full indicator results, closing all twelve Paper IV results in Section 11. At that release, seven results remained unmapped and determinant, normalized-section product and coefficient-asymptotic layers remained open, alongside earlier partial bridges.

The v0.14.0 contract closes the seven records listed above using actual operator, infinite-product, analytic Taylor and pole-removal constructions. Earlier partial bridges remain explicit in the current completion ledger.
