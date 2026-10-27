# Lean Block 01 — maintained claim C01

**Result:** C01 is now kernel checked, with a fresh build, printed-axiom audit, and replay through the toolchain's `leanchecker`. The other seven maintained claim groups are unchanged and not Lean-verified by this block.

The original theorem companion has 29 numbered entries. This block formalizes **Theorem 2.1, Cut-comparison identity and complete coverage**, together with 40 declarations for definitions' properties, gate and circuit semantics, corollaries, and examples. Declaration counts are not counts of independent discoveries.

## Mathematical statement

Let `c = p ++ q` be a legal classical NOT/CNOT/Toffoli circuit, with distinct wires in each gate. Let the endpoint encoding store `(x, 0^a, b)`. Assume, for every logical input `x` and both target bits `b`, that `c` restores the inputs and workspace and changes the target to `b XOR f(x)`.

Define `H_i(x)` as the XOR of register `i` after the prefix on target zero and register `i` after the reversed suffix on target zero. Then each `H_i(x)=true` implies `f(x)=true`, and `f(x)=true` holds exactly when some `H_i(x)=true`.

`Gate.eval_involutive`, `run_reverse_run`, and `run_injective` are proved from the actual gate definitions, not stipulated. `Restores` is a proposition defining endpoint correctness, not a custom axiom or an assumption of the cover theorem itself. `canonical_complete_safe_cover` handles every finite logical input size, every finite zero-ancilla count, and every cut index.

## Model boundaries

The module allows dirty workspace, temporary changes to inputs, and use of the target as a control. It does not allow quantum phases, measurement, or discarded workspace. Its conclusion is semantic safe coverage; there is no gate lower bound in this formal block.

`Boundary` is slightly more general than the canonical encoding: it requires a designated wire to store the supplied target bit. The canonical specialization supplies the exact finite-register model used in the manuscript. Target separation is not omitted.

## Evidence and dependencies

- Forty theorem declarations across `Gates`, `CutComparison`, and `Examples`.
- Fresh-source build and per-module warning-as-error checks.
- Only standard axioms: `propext`, `Classical.choice`, `Quot.sound`.
- No active `sorry`, `admit`, custom `axiom`, `native_decide`, or kernel-check bypass.
- The bundled checker replays all three modules. This is not independent human review or an independent kernel implementation.
- Four negative compile controls: a false proposition, repeated control/target wire, false target-only reconstruction, and a deliberately admitted proof rejected by the warning guard.
- The original full active scientific suite reproduced all seven frozen outputs. This is distinct from the universal Lean proof.

See `theorem-status.json`, `formalization/lean/theorem_inventory.json`, `evidence/lean-block01/verified/verification.json`, and the accompanying PDF for the exact declaration/source map.

## Preserved predecessors

Version 1.0.0 and the prior theorem-source package are unchanged in `archive/releases/`; the original 28-page PDF is in `docs/reference/`. Their historical statements that Lean had not yet been run remain accurate for those pinned editions.

## Next bounded formalization target

Formalize the multiplicative-degree lemma in F3 and the representation needed to connect the C01 packets to C02. No additional conjecture-solving or experimental route is a release requirement.
