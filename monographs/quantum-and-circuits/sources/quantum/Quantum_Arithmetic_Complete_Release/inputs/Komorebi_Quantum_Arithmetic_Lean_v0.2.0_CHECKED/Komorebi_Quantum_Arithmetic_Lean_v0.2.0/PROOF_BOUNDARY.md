# Proof boundary

## What the compiled declarations establish

All 22 original statements are unchanged. They certify the twelve entry Ramanujan
signal, its rational 12 by 12 cyclic projector, symmetry, idempotence, signal
recovery, removal of the displayed perturbation, the exact energy identity,
cyclotomic phase and DFT tables, equal squared input amplitudes, and rational
probability normalization.

The specification module additionally proves that the selected residues are
exactly those coprime to 12, that the coordinate root has no smaller positive power
than 12, that every literal projector entry equals c12(i-j)/12 with cyclic
indexing, that signal and perturbation are orthogonal, and that the actual DFT
probability tables have total mass one and coprime mass one versus zero.

The complex interpretation module defines a map from four rational coordinates
into the ordinary complex numbers using the positive real square root of 3. It
proves preservation of addition, multiplication, conjugation, powers, and finite
sums. Consequently the exact DFT certificates transfer to a complex Fourier
transform with phase sqrt(3)/2 + i/2.

The unitary module defines the actual normalized complex Fourier matrix F and
proves both F.conjTranspose * F = 1 and F * F.conjTranspose = 1. The intermediate
character orthogonality certificate is itself checked by kernel reduction.

## Trust boundary

The theorem dependency audit permits only the standard Lean foundations
`propext`, `Classical.choice`, and `Quot.sound`. It rejects any other axiom.
No `sorryAx`, `Lean.ofReduceBool`, or project-specific axiom is permitted.
The final build includes no native decision proof.

`leanchecker` replays the project's compiled declarations using Lean's kernel.
It is an additional replay check, not a second independently implemented proof
assistant. Imported Mathlib declarations are trusted from the pinned environment
rather than all being re-proved from scratch in this run.

The independent Python check verifies the finite arithmetic by a separate
implementation. It is supplementary evidence, not the justification for the Lean
proofs. Floating point arithmetic is not used in the load-bearing certificates.

## What is not claimed

This release does not formalize arbitrary q, the general Möbius divisor identity,
the whole Komorebi framework, or every sentence of the essay. It does not provide
a quantum circuit synthesis theorem, a state preparation cost bound, a hardware
experiment, or any quantum advantage claim.

The explicit Matrix equality identifying the literal rational projector with
F D F.conjTranspose, and Matrix action identities for separately defined normalized
state vectors, are not supplied as additional cross-representation theorems in
this release. Their constituent finite tables and Fourier unitarity are checked.

The coordinate interpretation is proved sound for the operations used. It is not
packaged as a global field instance, and injectivity of that interpretation is not
needed for the transferred identities and is not asserted here.

The normalized Fourier matrix is fully formalized. The probability consequences
are represented as exact finite tables. A general Hilbert-space measurement API,
density matrices, and a physical implementation of a phase-removal operation are
outside this package. The signed and unsigned signals denote separately specified
states, not a claimed universal quantum operation that discards relative phase.

## Novelty boundary

Formal verification establishes the displayed propositions under their definitions.
It does not establish historical novelty, priority, or the significance of the
larger research program. The framework's interpretation and those assessments
remain separate questions.
