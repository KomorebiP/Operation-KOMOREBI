# Prescribed-parameter obstruction verification contract

The target is TARGET_CONTRACT.json. For an actual integer polynomial system F
in m solved and k parameter variables, a lower root x modulo q^L, a positive
modulus q, and L >= 1, derive the residual r from F(x)=q^L r. Let J and K be the
actual solved-coordinate and parameter-coordinate Jacobian blocks modulo q.
For each prescribed parameter digit v, the finite obstruction is

    [rbar + K v] in (Z/q)^e / range(J).

The obstruction must vanish exactly when an actual residue vector y modulo
q^(L+1) reduces to x at depth L, satisfies the original polynomial equations at
depth L+1, and has the prescribed free coordinates x_free + q^L v. The target
includes the exact digit-to-residue fiber equivalence and the resulting action
of ker(J). For prime p, the actual lift count is p^(m-rank(J)) when the class
vanishes and zero otherwise. The obstruction quotient has cardinality
p^(e-rank(J)). No vector-space rank formula is asserted for composite moduli.

The expanded contract writes J using actual polynomial partial derivatives,
writes the parameter contribution as the explicit K v sum, and counts a
subtype of actual residue vectors satisfying all three restrictions. Its
flattening equivalence proves that this is exactly the type counted by the
formalized lifting theorem. Both final contracts begin from the actual lower
root condition and derive a residual uniformly for all v. They do not assume
linearization, a preselected residual, or an abstract lift existence principle.

Run from the project root:

```bash
python3 scripts/verify_polynomial_prescribed.py \
  --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /path/to/a-new-run-directory
```

The output directory must not exist. Every active mathematical module, positive
control module, and statement contract is compiled from source into its empty
build directory. Only the pinned Lean toolchain and precompiled Mathlib
dependencies are reused. The gate is formal proof checking under that kernel,
not numerical testing or an independent implementation of Lean.

The pinned Lean version is 4.34.0-rc2 and Mathlib revision is
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The exact shipped executable-path
adapter is hash checked. It repairs executable-path discovery and does not
modify the compiler or kernel. Compilation uses one thread, warnings as errors,
and a 240-second per-file compiler timeout. The enclosing subprocess timeout
is 380 seconds and retains partial timeout output.

The source scan rejects omitted proofs, custom axioms, unsafe implementation
shortcuts, unbounded heartbeat/recursion settings, and listed kernel bypasses.
The frozen inventory contains every active source, import, declaration, and
hash. The gate checks exact file coverage, dependency order, duplicate names,
and source/inventory/target changes during the run. Each theorem, definition,
and abbreviation receives an explicit axiom closure query. Only propext,
Classical.choice, and Quot.sound are accepted. Parser regressions include Lean
identifiers with apostrophes, duplicate or mismatched reports, and forbidden
axioms.

The 35 inherited mathematical source hashes were checked against the actual
PRSC_IX_Complete_First_Order_Motion.zip archive, SHA-256
`9b0db84f38397e67b7f61fe32b8fa1bf82614324f98703749bc02e2c838ad766`.
They are compiled afresh with the four new prescribed-parameter modules.
Seven inherited negative controls remain active. New positive controls include
an actual parameter-only polynomial with surjective full Jacobian whose fixed
parameter digit is nevertheless obstructed, and an odd-prime sign check. The
new negative control incorrectly asserts existence in an obstructed prescribed
fiber. Expected-failure controls pass only on the specified type mismatch and
cannot pass due to missing imports/constants, timeouts, or panics.

Each fresh run records logs, exact source and output hashes, a verification
report, and a computation manifest. Failed development attempts and gate
attempts are preserved and classified. A compilation failure alone does not
refute the written theorem. The independent raw-source audit checks the
mathematical interpretation. Its frozen source and exposition hashes are
linked to the completed gate by audit/reconcile_review.py, which independently
re-parses the axiom output and reconciles all compiler logs and build hashes.

A successful gate does not establish compatible infinite lifting for arbitrary
parameter sequences, higher singular obstructions, presentation invariance,
or completed/global descent.
