# Realization Calculus: Quantum and Circuits

Arithmetic, Symmetry, and the Cost of Realization

Komorebi P.

Start with `volume/output/Realization_Calculus_Quantum_and_Circuits.pdf`. This is the current 344-page professional monograph edition, styled to match the finished Komorebi Physics volume. It contains the four mathematical treatments, scientific visual studies, formal companions, glossary, and collected references. Older standalone PDFs retained in the component directories are historical editions and do not supersede this book.

## What this completion adds

- Fresh Lean source builds, axiom inspection, and kernel replay for the 96-declaration arithmetic bridge and 115-declaration circuit development, across thirteen modules.
- A written adaptive discarded-state error certificate for projected quantum trajectories, with an exact rational example.
- An analytic proof of the exact three-versus-two entangling costs and common orbit of the four two-qubit Clifford exceptions. The exhaustive census establishes completeness of that finite exceptional set.
- Repairs to entropy asymptotics, Schur-block uniqueness, access hypotheses, subgroup actions, retraction criteria, weighted counting series, additive cost assumptions, and reversible-gate parity.
- Four recovered catalytic reproduction programs, complete finite replays, stricter packet leakage handling, and correct complex-valued numerical updates.
- A professional monograph layout with a navy cover, serif typography, linked part reading guides, and bundled fonts with their original licence notices.
- An exact source-to-book check for all 328 explicitly delimited statement and proof blocks; the presentation revision preserves all mathematical text.

## Verification and scope

The official formal inventories total 211 named declarations. They are supporting mathematical statements, not 211 new discoveries. Both developments use only `propext`, `Classical.choice`, and `Quot.sound`. Lean and its dependency cache were pinned, but were not themselves rebuilt from source. Kernel replay uses Lean's own kernel.

The three inherited arithmetic rejection controls and eight circuit rejection controls pass. The inherited arithmetic false-mode control has an opaque reduction diagnostic. A supplemental positively proved mode value and its negation, followed by an explicit false-coordinate rejection, resolve that diagnostic weakness. These two verification lemmas are not added to the 96-declaration inventory.

Current exact arithmetic checks comprise 3,003 inherited assertions, 5,374 release assertions, and 472 supplemental assertions. The symmetry suite adds 308 exact rational/integer checks and 21 API controls; floating reconstruction is recorded separately with its tolerance. Circuit tests include all four-input truth tables and an independent evaluation-dual check on 278 functions. The catalytic replay records its exact finite state populations and gate/cost models. Overlapping checks are not independent theorem counts.

Successful release checks do not mean that every written result in the book is formalized in Lean. The general-modulus arithmetic theory, symmetry theory, catalytic theory, evaluation-span dual and circuit claims C03–C08 retain their stated written or finite evidence. All remaining research questions are listed in `PROGRESS_LEDGER_v1.0.0.md` and in the book.

## Contents

| Path | Purpose |
|---|---|
| `volume/` | Current PDF, editable consolidated TeX, figures, regeneration scripts and layout checks |
| `sources/` | Four component source packages, including Lean, Python, C++, exact data and preserved historical evidence |
| `verification/` | Fresh Lean receipts, source snapshots, logs, theorem inventories and runtime reconstruction record |
| `review/` | Component reviews, exact computation receipts, source patches and focused mathematical audits |
| `release_tools/` | Portable formal-replay wrapper and reproduction instructions |
| `INPUT_PROVENANCE.json` | Exact retrieved input identities and hashes |
| `STATUS.json` | Machine-readable completion and coverage boundaries |
| `SHA256SUMS.txt` | Hashes for every shipped file except this checksum list itself |

The large portable Lean runtime is an external dependency and is not bundled. Use the already supplied Lean Compact kit with the replay wrapper. Python and TeX reproduction require the component dependencies described in `release_tools/README.md` and `volume/README.md`.

## Research endpoints retained

The volume does not resolve universal efficient quantum simulation, unrestricted circuit hardness, every-field minimal catalytic dimension, the full asymptotic catalytic distortion problem, or the larger nonlinear/Gaussian/phase synthesis programs. Four-bit exploratory and separate Latin-class computations without recoverable input data are explicitly pending rather than accepted as fresh evidence.

This task preserves the original rights and attribution notices. It does not publish the files to a repository or assign a new distribution licence. Historical manifests belong to their original snapshots. The root checksum list identifies the current assembled package.
