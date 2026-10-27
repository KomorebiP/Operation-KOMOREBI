# Realization boundaries: the common-completion construction

Start with **FINITE_QUOTIENT_BLINDNESS.md**. It constructs countable, residually finite, reduced abelian groups whose complete unmarked finite-quotient systems are identical, while their least presentation degrees range over every Turing degree.

## Main formulas

For a subset A of the natural numbers, choose one prime from each consecutive pair. Let D be the direct sum of all prime-order cyclic groups and P their product. The selected coordinate mask u_A defines

    G_A = preimage in P of the rational line spanned by [u_A] in P/D.

The manuscript proves:

- G_A/mG_A is C_rad(m) for every positive integer m.
- All profinite completions are the same computable procyclic group P.
- G_A is isomorphic to G_B exactly when A and B differ finitely.
- A copy of G_A is computable in an oracle X exactly when A is computable in X.
- A repeated diagonal construction stays outside any fixed countable finite-description grammar, without changing the completion.

The selector's finite changes must not be confused with distinct unmarked isomorphism types. Finite definability and computable presentation must also remain separate.

## Run the exact examples and checks

Python 3.10 or later is sufficient. No third-party packages are required.

From the extracted package directory:

```text
python src/dense_lift_groups.py
python src/exact_checks.py --output verification/local_checks.json
python inherited/exact_checks.py
```

The scripts use exact fractions and modular arithmetic. The test masks are computable examples, not simulated halting oracles. The current run passed 114,738 finite assertions, including six expected rejections of deliberately false simplifications. Infinite results are supported by the written proofs, not inferred from those tests.

## Contents

`FINITE_QUOTIENT_BLINDNESS.md` contains definitions and full ordinary proofs.
`src/` contains the explicit cocycle group implementation and exact checks.
`verification/` contains fresh reports, source hashes, a worked example, and input provenance.
`inherited/` preserves the earlier package files unchanged.
`PROGRESS_LEDGER_v0.2.0.md` records proof status, corrections, limitations, and the next restart point.

## Verification boundary

No Lean compiler is installed in the working runtime, and no Lean compilation is claimed. No independent external review has been performed. The earlier spectrum coding was matched to a known source; historical priority of the stronger combined construction remains unestablished. The original input archive is not overwritten.
