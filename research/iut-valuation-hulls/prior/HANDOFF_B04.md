# Continuation handoff

## Authoritative predecessor

`Komorebi_IUT_KTG_Block03_Checked_v0.3.0_2026-09-17.zip` (source archive in Library).
Original 22 Lean sources preserved unchanged; `KTG.lean` only gains two imports. The inherited primary IUT I-IV PDFs and Block03 source mapping remain in this package.

Recent separate arithmetic audit:
`ABC_Global_IUT_RR5_2026-10-25.zip` (source archive in Library).
This B04 package neither replaces nor silently modifies its claims.

## What B04 adds

* `KTG/HodgeReduct.lean`: carrier-safe multiplicative reduct interface, exact additive obstruction, positive preservation of powers and torsion, transported addition, and exact descent criterion.
* `KTG/HodgeFinite.lean`: finite marked-field model, two different field additions with identical multiplication, embedding in actual `KTransport`, and certified failure of additive reconstruction.
* `experiments/finite_theaters.py`: exhaustive small-field verification and counts.
* `experiments/negative_controls/`: two intentionally false Lean statements, compiler rejection required.

## What remains

Do not promote this model to a full IUT theta link. Do not claim the IUT III scalar witness is present.

1. Re-open `notes/IUT_312_FIELD_TO_SOURCE_MAP.md` and `notes/IUT_312_OPEN_OBLIGATIONS.md` in the predecessor.
2. Pick an actual source datum in IUT I/II (e.g. a prime-strip or a monoid/Frobenioid group law), and define a genuine typed Lean carrier using the source definitions, not an invented analogue.
3. Establish the source-backed preservation theorem under a specified link or prove an obstruction under the *actual* source assumptions.
4. Only afterward connect that instance to the IUT III log-volume witness and RR5 quantitative loss contract.

The conceptual test is: which observables factor through the exact retained arithmetic data, and which require extra rigidity or indeterminacy control? The finite model supplies a verified test pattern, not the required arithmetic instantiation.
