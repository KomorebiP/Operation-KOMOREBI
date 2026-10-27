# Komorebi Constructive Repair Audit — v0.1.0

This is a **standalone experimental test harness** for a proposed constructive-repair refinement of Realization Calculus (particularly Paper III), with arithmetic and representation-theoretic regression examples from Paper IX and Paper XI.

It is **not** a new foundation, not a modification of the existing Komorebi Python library, and not a Lean-verified release.

## Run

Python 3.10+; main experiment requires **no third-party packages**.

```bash
python run_audit.py
python -m unittest -v test_repair_core
```

The first command writes:

- `audit_trace.txt` — 258+ lines of exact intermediate calculations and negative controls
- `case_records.jsonl` — one machine-readable record for each of 3,307 individual cases
- `audit_summary.json` — assertion counts, category counts, known limitations

Optional independent cross-check with SymPy 1.14:

```bash
python -m pip install sympy==1.14.0
python crosscheck_sympy.py
```

Then run `sha256sum -c SHA256SUMS.txt` to check the packaged evidence (do this before rerunning the scripts, as reruns rewrite outputs).

## Read first

1. `TECHNICAL_AUDIT.md`: detailed theorems, ordinary proofs, scope analysis, test results, all significant negative controls.
2. `audit_trace.txt`: short exact computation log and human-readable intermediate values.
3. `case_records.jsonl`: complete deterministic per-case evidence for reproducing or auditing the sampled computations.
4. `DEVELOPMENT_HISTORY.md`: stages and changes from initial to strengthened audit.
5. `FORMALIZATION_TARGETS.md`: suggested Lean contracts and what has **not** been compiled.

## Main status

- Restricted free-linear augmentation theorem: ordinary proof, tested.
- Finite admissible-menu optimization: exhaustively certified within input menu, tested by independent coefficient enumeration.
- Invariant preservation, information-losing transport, nonlinear obstructions: negative controls passed.
- Genuine Euler and cyclotomic trace regression tests: exact arithmetic passed in tested ranges.
- Global arithmetic representation / universal repair synthesis: **not proven**.
- Lean kernel compilation: **not attempted; toolchain absent**.

## File roles

`repair_core.py` is the finite exact-arithmetic solver, `run_audit.py` orchestrates primary experiments, `extra_audit.py` runs additional domain-linked tests, `test_repair_core.py` provides 20 regression unit tests, and `crosscheck_sympy.py` independently verifies ranks and coefficients using SymPy.

No floats, optimization heuristics masquerading as proofs, or unsupported existence claims are used in the exact solver.
