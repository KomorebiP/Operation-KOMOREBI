# Continue from Block 12

Use this directory as the sole authoritative predecessor for the next p-adic
compiler block.

## Preserve

- all 165 theorem statements inherited from Block 11;
- all 14 Block 12 theorem statements;
- the exact totalized identity eliminating `B` and `d`;
- the exact equality between the Block 11 and `(p,r,h)` envelopes;
- the `h`-free raw-precision bound;
- every executable compiler counter and all prior certificates;
- the distinction between universal Lean proof and bounded computation;
- the Lean `4.34.0-rc2` / mathlib `aeb72f1e...` provenance boundary;
- timeout-as-inconclusive handling;
- the 179-theorem axiom census and both negative controls.

## Next mathematical block

Formalize defect monotonicity.  A natural target is:

```text
h₁ ≤ h₂ → coarseK r h₂ ≤ coarseK r h₁
```

and hence

```text
maximumLayerCompilerParameterEnvelopeBound p r h₂
  ≤ maximumLayerCompilerParameterEnvelopeBound p r h₁.
```

Then prove the raw-precision envelope is attained at `h = 0`:

```text
maximumLayerCompilerParameterEnvelopeBound p r 0
  = maximumLayerCompilerRawPrecisionBound p r.
```

This would identify the `h`-free expression as the exact worst-case member of
the certified envelope family, not merely a transported upper bound.

## Independent compatibility lane

An exact rebuild under stable Lean `4.34.0` with mathlib revision
`5ed2965256430c3649e86755f9576b54eca72435` remains separate.  Do not alter
mathematical statements merely to satisfy that lane.
