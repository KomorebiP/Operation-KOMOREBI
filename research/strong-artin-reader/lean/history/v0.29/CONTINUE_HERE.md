# Continue from v0.29 Continuous Local Gauge Obstruction

Read README.md, RESEARCH_BOUNDARY.md and RESULT.json completely. The base is the
exact v0.28 archive identified by checksum, NOT another similarly named branch.

The newly closed arrow is continuous local matching UP TO independent kernel
conjugacy. It includes local C0 gauge terms. Do not revert to the strict Z1
cokernel when the intended problem allows local conjugacy.

Key identities:

```
boundary(b,(x_i)) = (db, (res_i b + d0 x_i))
t_i(h) = (1+x_i) ((1-b)r)(alpha_i(h)) (1+x_i)^(-1)
0 -> coker(H1_global -> H1_local) -> H2_local_gauge -> H2_global
```

The last displayed map is NOT asserted surjective. The secondary H1 class is
independent of an absolute primitive. The general zero criterion is proved without
order invertibility; it does not imply general vanishing.

The next consequential task is to choose ONE genuine arithmetic local condition,
identify its permitted gauge complex, and compute or control the actual H1
localization image or distinguished relative H2 class. Do not substitute an
arbitrary Selmer-equivalence assumption, slack variables, or a zero automorphic
module. A compatible finite-tower theorem is a valid separate internal route,
but has a different scope from arithmetic local-condition vanishing.

Replay in bounded batches with verify.py as documented in README.md. Preserve
warnings-as-errors and the exact base hashes. Passing helper modules is not a new
Strong Artin theorem. Update the boundary only when an actual statement changes.
