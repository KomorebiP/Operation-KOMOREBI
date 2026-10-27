# Komorebi p-adic Block 05

**Checked checkpoint:** prime-base Kummer radix descent, exact radix representatives, and a finite executable barrier compiler.

**Local release date:** 2026-09-17  
**Checked toolchain:** Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`  
**Checked mathlib:** `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

## Read in this order

1. `THEOREM_NOTE.md`
2. `LEAN_STATUS.md`
3. `PROOF_BOUNDARY.md`
4. `PROGRESS.md`
5. `CONTINUE_HERE.md`
6. `REPRODUCE.md`
7. `results/BUILD_VERIFICATION.json`

The authoritative checked source is under `lean/`. The compiled interface and
object files are retained under `compiled_rc2/`.

## Main result

For prime `p`, positive `Q`, and `1 ≤ q ≤ Q`,

```text
v_p ((pQ - 1).choose (pQ - q))
  = v_p ((Q - 1).choose ((q - 1) / p)).
```

Writing `a = floor((q-1)/p)`, the carry is constant throughout the radix block

```text
p*a < q ≤ p*(a+1).
```

The total diagonal cost is minimized at the maximal admissible point

```text
q_a = min(Q, p*(a+1)).
```

Therefore the original search over every `q = 1, ..., Q` is exactly equivalent
to the finite scan

```text
0 ≤ a ≤ floor((Q-1)/p).
```

The checked Boolean `radixCompilerCrosses` computes the minimum of those exact
representative costs and is proved equivalent to `CrossesBarrier`.

## Verification headline

- warning-as-error Lake build: **PASS**
- Lake jobs: **1,152**
- production Lean files: **9**
- theorem declarations: **51**
- concrete independently generated `native_decide` checks: **72 PASS**
- exact Python checks: **1,562,433 PASS**
- predecessor scripts rerun individually: **11 PASS**
- project-local `axiom`, `sorry`, or `admit`: **none**

This is a real kernel-checked RC2 checkpoint. It is not yet an exact rebuild
under stable Lean 4.34.0 and mathlib commit `5ed296...`.
