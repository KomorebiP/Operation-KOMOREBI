# Continue from Block 05

Treat this directory as the sole authoritative checked predecessor for the next
p-adic block.

## Restore first

1. Read `START_HERE.md`, `THEOREM_NOTE.md`, `LEAN_STATUS.md`, and
   `PROOF_BOUNDARY.md` completely.
2. Reproduce the warning-as-error build.
3. Run:

```bash
python verification/verify_radix_compiler.py
lake env lean -DwarningAsError=true verification/LeanCompilerVector.lean
lake env lean -DwarningAsError=true verification/AxiomAudit.lean
```

4. Confirm `results/BUILD_VERIFICATION.json` and all source hashes before
   editing theorem statements.

## Next block target: suffix-window compiler

Formalize an abstract branch-and-bound theorem with data

```text
visible : Nat → Nat
carry   : Nat → Nat
cost a  = visible a + carry a
```

under these hypotheses on a backward scan:

- `carry a ≥ 0`;
- earlier indices have no smaller visible cost;
- a current best complete cost `B` has already been observed;
- at index `a`, `B ≤ visible a`.

Prove that every earlier cost is at least `B`, so the remaining prefix can be
discarded without changing the minimum.

Then instantiate:

```text
visible a = (pQ - radixRepresentative p Q a)(h+1)
carry a   = v_p((Q-1).choose a).
```

The desired checked endpoint is an executable suffix scan proved equal to
`minRadixBarrierCost`.

## Secondary target

After the suffix theorem, connect the Boolean barrier compiler to the complete
quotient search and final-fiber scan, yielding a checked executable function
that returns the exact maximum correction layer `M_{p,r,h}`.

## Do not weaken these boundaries

- Keep primality explicit.
- Do not apply the prime-base compiler to composite bases.
- Do not infer a universal theorem from bounded computation.
- Do not claim the stable Lean 4.34.0 pin has been checked until it is actually
  built.
- Preserve failed attempts and negative controls.
