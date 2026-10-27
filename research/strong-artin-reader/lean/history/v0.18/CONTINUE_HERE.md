# Continue Strong Artin from v0.18

## Restore point

Use this directory as the canonical additive checkpoint above:

```text
Strong_Artin_Lean_v0.17.0_Local_Pairing_FiniteDepth_GenericSupport_Checked.zip
```

Do not replace the base archive or weaken the explicit zero-norm and arithmetic-comparison hypotheses.

## Strongest checked endpoint

```text
finite cyclic H¹
  ≃ coefficients / range(generator - 1)
  ≃ Matrix / frobeniusCoboundaries
```

and

```text
tame q=1 relation space
  ≃ Dual(finite cyclic H¹),
```

with pairing `trace(P * X)`.

On a one-dimensional compared arithmetic quotient, every nonzero Tate functional is a unique unit multiple of the trace functional, so the two detect exactly the same classes.

## Next technical theorem

Construct a comparison for the selected Taylor--Wiles local line from continuous local unramified cohomology to a finite cyclic quotient satisfying the zero-norm hypothesis. Then prove the arithmetic local Tate pairing is nonzero on that line. Exact normalization may be deferred because v0.18 removes it from the nonvanishing criterion.

A clean route is:

1. show every continuous residual cocycle factors through a finite cyclic quotient of the unramified quotient;
2. enlarge the cyclic order, if necessary, so the cyclic norm acts as zero on the finite coefficient module;
3. identify generator evaluation with the v0.18 `h1ClassOfValue`;
4. transport local Tate duality to the selected one-dimensional quotient;
5. prove the transported functional is nonzero;
6. instantiate `tate_ne_zero_iff_traceProbe_ne_zero`.

## Independent global target

Continue in parallel on the patchable residual occurrence problem:

```text
finite-Satake descent
  -> nonzero determinant-bearing residual automorphic complex.
```

The local comparison does not solve this existence problem.

## Verification

Run:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Preserve warnings-as-errors, zero proof escapes, and the exact base hash recorded in `README.md`.
