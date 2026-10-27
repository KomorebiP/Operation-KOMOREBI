# Lean status

## Checked environment

```text
Lean 4.34.0-rc2
commit 6a10ac8c22beadecabdbb0919c2b50214762f91d
Lake 5.0.0-src+6a10ac8
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
```

The toolchain was reconstructed from the five preserved `Lean_Compact_*.zip`
parts. Their concatenated XZ payload has SHA-256

```text
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7
```

and passed `xz -t` before extraction.

## Build result

```text
✔ KomorebiPadic.Arithmetic
✔ KomorebiPadic.IntervalGraph
✔ KomorebiPadic.ValuationModel
✔ KomorebiPadic.ConcreteBinomialModel
✔ KomorebiPadic.QuotientBarrier
✔ KomorebiPadic.RadixDescent
✔ KomorebiPadic.RepresentativeCompiler
✔ KomorebiPadic.FiniteCompiler
✔ KomorebiPadic
Build completed successfully (1152 jobs).
```

The final build used `-KwarningAsError=true` and exited with status zero.
Direct elaboration of the root module with `-DwarningAsError=true` also exited
zero.

## Source and kernel audit

- production Lean files: 9
- theorem declarations: 51
- definitions: 17
- structures: 2
- `sorry`: 0
- `admit`: 0
- project-local `axiom`: 0
- compiled `.olean`/`.ilean` files retained: 18

`#print axioms` was run for every theorem. The only dependencies reported were
standard Lean axioms already used by mathlib:

```text
propext
Quot.sound
Classical.choice
```

No unexpected axiom occurred.

## Negative controls

- a deliberately false theorem `1 = 2` was rejected
- a theorem containing `sorry` was rejected under warning-as-error
- 72 independently generated concrete compiler equalities passed
  `native_decide`

## Exact boundary

This checkpoint is checked under **Lean 4.34.0-rc2**, not stable Lean 4.34.0.
The stable-pinned Block 04 source remains preserved, but Block 05 has not been
rebuilt against stable mathlib commit
`5ed2965256430c3649e86755f9576b54eca72435`.
