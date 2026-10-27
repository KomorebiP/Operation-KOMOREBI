# Komorebi Additive/Multiplicative Arithmetic Observation — Block 03

Continuation of the preceding two additive–multiplicative reconstruction research blocks.

## Contents

- `RESEARCH_NOTE.md`: theorem statements, self-contained mathematical proofs, exact claim boundaries, restart instructions.
- `proofs/FiniteObservation.lean`: algebraic three-sample filter, sharp lower bound and exact witness.
- `proofs/FilterBudget.lean`: generic finite annihilator L∞ error theorem over arbitrary lengths.
- `proofs/WittCarryExample.lean`: complete finite `F_3 → Z/9` Teichmüller carry example and nonsplitting proof.
- `proofs/Block03Negative.lean`: intentionally false statement to test compiler rejection.
- `tests/test_block03.py`: exact modular repetitions, sharp minimax, polyphase interpolation, Witt lift and carry-cocycle tests.
- `tests/test_recurrence_grammar.py`: general finite recurrence annihilator and escape-mode negative control.
- `tests/plot_block03.py`: deterministic mathematical figures.
- `evidence/`: machine-readable results, stdout logs, compiler audit and manifest.
- `figures/`: two explanatory mathematical graphics.

## Run exact tests

```bash
python3 tests/test_block03.py
python3 tests/test_recurrence_grammar.py
python3 tests/plot_block03.py
```

## Reproduce Lean checks

Use the separately supplied, pinned **Komorebi Portable Lean 4.34.0-rc2** kit and its `run.sh` entrypoint:

```bash
bash /path/to/Komorebi_Portable_Lean_4.34.0-rc2/run.sh check proofs/FiniteObservation.lean
bash /path/to/Komorebi_Portable_Lean_4.34.0-rc2/run.sh check proofs/FilterBudget.lean
bash /path/to/Komorebi_Portable_Lean_4.34.0-rc2/run.sh check proofs/WittCarryExample.lean
```

The intentionally false file must **fail** compilation. The archive includes exact `#print axioms` audit outputs; no `sorry`, `admit`, or added axioms are used in the positive Lean source.

## Scope

This package **does not** contain or prove a global abc height estimate, IUT reconstruction, or a new global arithmetic height mechanism. It distinguishes finite conditional statements and fully checked examples from broader open research goals.
