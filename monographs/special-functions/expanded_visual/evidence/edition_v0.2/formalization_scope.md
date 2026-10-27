# Special-function consolidation: formalization scope

Review date: 2026-10-07. Source snapshot: the 2026-08-02 projector-calculus Lean v1.1.0 ledger and its later same-day browser-safe core v1.2.2.

The directly sourced special-function formalization consists of a claim registry and a small finite coefficient tranche. It is not a completed Lean proof of all eight special-function papers. Paper proofs and numerical evidence must be assessed separately from the existence of Lean claim records.

## Exact claim inventory

Counts were recomputed from the current materialized `Komorebi_Projector_Calculus_Lean_v1.1.0_CLAIM_LEDGER.csv`, filtered to `corpus == special-functions`. The same full ledger was successfully read through Library. The whole ledger has 594 rows; the special-function subset has 173 rows.

| Volume | Source objects | Theorem/lemma/proposition/corollary claims | Definitions | Examples/remarks/algorithms | Boundary records | Conjecture records |
|---|---:|---:|---:|---:|---:|---:|
| I | 32 | 22 | 3 | 4 | 2 | 1 |
| II | 23 | 15 | 5 | 2 | 0 | 1 |
| III | 24 | 16 | 1 | 6 | 1 | 0 |
| IV | 16 | 10 | 0 | 5 | 1 | 0 |
| V | 21 | 17 | 1 | 1 | 1 | 1 |
| VI | 22 | 20 | 0 | 1 | 1 | 0 |
| VII | 15 | 10 | 2 | 2 | 1 | 0 |
| VIII | 20 | 15 | 3 | 1 | 1 | 0 |
| **Total** | **173** | **125** | **15** | **22** | **8** | **3** |

The 125 proof-bearing source claims consist of 92 theorems, 18 propositions, 14 corollaries, and 1 lemma. The 22 contextual/computational objects consist of 16 examples, 2 remarks, and 4 algorithms. These categories count extracted source objects; they do not count kernel-accepted Lean proof terms.

## Exact formalization statuses

| Volume | `phase-1-queued` | `queued` | `lean-draft-present` | `context-or-example` | `boundary-record` | `conjectural-goal` |
|---|---:|---:|---:|---:|---:|---:|
| I | 3 | 21 | 1 | 4 | 2 | 1 |
| II | 15 | 5 | 0 | 2 | 0 | 1 |
| III | 14 | 3 | 0 | 6 | 1 | 0 |
| IV | 9 | 1 | 0 | 5 | 1 | 0 |
| V | 12 | 6 | 0 | 1 | 1 | 1 |
| VI | 16 | 4 | 0 | 1 | 1 | 0 |
| VII | 8 | 4 | 0 | 2 | 1 | 0 |
| VIII | 11 | 7 | 0 | 1 | 1 | 0 |
| **Total** | **88** | **51** | **1** | **22** | **8** | **3** |

No special-function source record in this ledger has a `kernelChecked` status. The one partial source link is `Projector_Generated_Special_Functions_I.theorem.002`, “Exact polyphase reconstruction.” Its status in the CSV is `lean-draft-present`; the corresponding `ClaimRecord` in the full browser Lean source uses `.partialFormalization`.

## Actual Lean theorem content

The full browser file contains the module `KomorebiProjectorCalculus/SpecialFunctions/PolyphaseSections.lean` at rendered lines 1456–1492. It contains two definitions, `section` and `combineResidue`, and one theorem:

`Komorebi.SpecialFunctions.section_refinement`

This theorem proves that taking a child coefficient subsequence of a coefficient subsequence equals taking the corresponding subsequence at the product modulus. Its proof is arithmetic indexing, independent of convergence. It does not prove the paper's analytic series-reconstruction statement, Gamma asymptotics, Laguerre or Racah analysis, or a signed Möbius estimate.

The v1.2.2 browser-safe core contains a foundational finite tranche: operator grammar, algebraic hulls, finite projector reconstruction, transfer blocks, fibre/coordinate packets, matrix support, finite differences, coefficient sections, and finite diagonal amplitudes. Its header explicitly identifies the larger source ledger as data, not theorem assumptions. This later same-day file does not provide a new analytic formalization of the special-function papers.

## Whole-calculus verification boundary

The v1.1.0 manifest and release audit describe the entire projector calculus, not just the special-function series:

- 25 indexed source files and 24 generated claim-bearing modules.
- 594 extracted source objects encoded as Lean `ClaimRecord` values.
- 60 Lean source files containing 11,652 lines.
- 104 theorem-like declarations and 88 definition-like declarations in the finite tranche.
- Zero placeholder proofs and zero project axioms reported by the static scan.
- Static audit passed.
- Lean kernel build in the artifact container was not attempted; `passed` is null.

The status and audit documents explicitly state that ClaimRecord values are migration data rather than proofs, and that static absence of placeholders does not justify a `kernelChecked` label. This review did not execute a Lean build. No build certificate should be inferred from these counts.

## Boundaries to preserve in consolidation

The three conjecture records in I, II, and V are versions of the same principal Möbius coherence obstruction. Preserve all three source identifiers, but consolidate them under one canonical open conjecture rather than presenting them as three independent conjectures:

- `Projector_Generated_Special_Functions_I.conjecture.032`
- `Projector_Generated_Special_Functions_II.conjecture.023`
- `Projector_Generated_Special_Functions_V.conjecture.021`

The source boundary records in I–VI explicitly distinguish positive kernels, Gamma limits, total positivity, Jacobi models, semigroups, martingales, frames, and heat kernels from the signed principal Möbius cancellation bound. They state that those positive results do not establish the RH-equivalent signed coherence estimate.

Paper I also retains a negative control against blanket universal real-rootedness. Paper VII states that entropy arises after dephasing or measurement discards phase information, while the underlying orthogonal Racah transform remains invertible. Paper VIII gives a negative control against universal entropy monotonicity in the deformation parameter beyond one excitation, including an N=3 counterexample.

For a consolidated release, retain all source IDs, state the exact Lean scope, and maintain separate evidence fields for prose proof, numerical checks, Lean proof term, and kernel verification. The Lean appendix should be labeled partial coverage unless a later successful build certificate and theorem-to-source map are located.

## Successfully accessed sources

| Source | Exact Library file ID | Access |
|---|---|---|
| `Komorebi_Projector_Calculus_Lean_v1.1.0_CLAIM_LEDGER.csv` | `libfile_d19f24f2d66c8191a53f1f4d5c1649d6` | Successful full read; later materialized by root; raw CSV counted locally |
| `Komorebi_Projector_Calculus_Lean_v1.1.0_MANIFEST.json` | `libfile_dcf61e120fd08191827c8dfda78709fb` | Successful full read |
| `Komorebi_Projector_Calculus_Lean_v1.1.0_RELEASE_AUDIT.md` | `libfile_98c8be829b9c81918f8c794141057067` | Successful full read |
| `Komorebi_Projector_Calculus_Lean_v1.1.0_STATUS.md` | `libfile_cc41015a7c588191a7a483c993b0e28f` | Successful full read |
| `Komorebi_Projector_Calculus_Lean_Browser_Full.lean` | `libfile_fc2a8931e2c081918c9556e243d9dfa1` | Successful targeted find and read of relevant theorem module and source-claim status |
| `Komorebi_Projector_Calculus_Lean_Browser_Core_v1.2.2.lean` | `libfile_8d440b55caac8191b1441a8283c0ea77` | Successful full read |

Targeted searches covered projector-calculus Lean releases, special-function Lean/formalization, Racah, and log-Gamma. They did not identify a later analytic Lean completion. This is a bounded search finding, not proof that no later work exists. Unrelated returned candidates were not treated as evidence of special-function coverage.

An initial batch materialization attempt failed HTTP 403. Library text reads succeeded, and root subsequently materialized the ledger successfully. The findings above use successful reads and the raw materialized ledger; the failed transfer did not supply evidence.
