# Final handoff — Block 12

The exact maximum-layer compiler is unchanged.  Its Block 11 complexity
certificate now admits an exact direct parameter presentation:

```text
K = (r - 1) / (h + 1)
e = K / (p * (p - 1))
T ≤ 2 * (K / (p - 1) + 1) + p + p * e * (e + 1) / 2.
```

For prime `p` and positive `r`, Lean also proves the `h`-free bound obtained by
replacing `K` with `r - 1`.

Resume from `CONTINUE_HERE.md`.  Do not infer stable-toolchain compatibility
from the RC2 build receipt.
