# Formalization coverage — Model-Theory Normalization v0.3

## Completed cold execution

**PASS:** 222 local modules, 236 expected-outcome tasks,
7,871 explicit named library declarations axiom-audited.
The five new generic/boundary modules contain 32 theorem declarations, 10
definitions and one abbreviation. The 202 generated instances contain repeated
certificate equations and applications, not thousands of independent discoveries.

All local sources are compiled from an empty local build directory with warnings
as errors. All accepted source hashes are unchanged. All names in the inventory
have an axiom report. Only propext, Classical.choice and Quot.sound occur. No
custom project axiom, sorryAx or Lean.ofReduceBool is accepted. Five deliberately
invalid controls reject; the positive control accepts.

Lean: `Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)`
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The exact parent upstream source hashes and Lean
binary hash are verified. This is not a source rebuild of the entire upstream
Mathlib cache. Three independent generated modules may compile in parallel, each
with one Lean worker.

## New modules

| Module | Exact scope |
|---|---|
| MatrixObservationCode | Genuine finite test list, code/row/encoding equality, constructed local logical certificate, test reconstruction |
| MatrixLogicalBridge | Actual Mathlib IsQF formula and Set.Definable kernel, original-language TermDefinable coordinate tuple, actual-image quantified transport |
| MatrixLogicalFibers | Class formulas constructed by target tests, exact image-fiber truth, IsQF, nonempty and disjoint represented classes |
| MatrixLogicalWitnesses | A certified finite test/formula separates differently encoded states; growth witnesses become standard distinguishing formulas |
| MatrixImageBoundary | Actual residue-four counterexample to quantifying over the full free target instead of EncodedImage |

## Generated scope

Every one of the 202 frozen matrix certificates now has a standard first-order
defining formula for its actual kernel, a definability theorem, preservation of
all translated observational queries on the actual image, a class-formula theorem,
term-code exactness, and a universally indexed growth-formula theorem. The retained
643 individual growth witnesses also have checked row provenance and concrete
nonzero-value equations. There are 17 zero-coordinate certificates.

The source system is the literal matrix system inside the generated file. Lean
never enumerates its state vectors, including the 2^128-state large example.
Kernel `decide` is used only for finite coordinate/certificate identities, not
for enumeration of all source states or a fixed bound on future words.

## Parent preservation and limits

Fifteen inherited modules are copied byte-for-byte and rebuilt. Both complete
parent ZIPs are preserved unchanged. The 235-module representation parent and
entire p-adic development have not all been rebuilt in this block. In particular,
we do not report a new sharp arithmetic-minimum theorem here.

The formal interface uses a semiring and deterministic unary actions, with every
source state admissible. It is not unrestricted first-order elementarity, QE,
or theory-wide elimination of imaginaries. Class formulas use the declared names
for observation values. Raw test count need not equal minimum arithmetic dimension.
No formula-length, test-count, or horizon minimum is proved.

The Python discoverer, parser, Smith constructor, exporter, and independent checker
are not verified executables. Source transcription is independently tested; the
formal result does not certify an arbitrary informal human specification. These
are frozen synthetic regression cases, not independently held-out discoveries.
All proof interpretation review is self-review.
