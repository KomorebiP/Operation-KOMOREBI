# Weighted lifting verification contract

The target is `TARGET_CONTRACT.json`: actual square polynomial systems over
the p-adic integers, arbitrary p-adic centers, and a rationally invertible
actual Jacobian whose inverse denominator is bounded by the stated exponent
`s`. For `r > 2s`, the target includes root existence, uniqueness throughout
the full ball of depth `s+1`, and displacement depth `r-s`.

The computational assertion is Lean kernel acceptance of the checked theorem
sources and expanded statement contracts under the pinned toolchain. This is
proof checking of universally quantified statements, rather than a finite
numerical sample. The mathematical reading of those statements still needs
the separate proof audit.

Run from the project root:

```bash
python3 scripts/verify_polynomial_weighted.py \
  --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /path/to/a-new-empty-run-directory
```

The output directory must not exist. Its `build` subdirectory starts empty.
All project modules, positive control supports, and contracts are compiled
again in dependency order. The pinned Mathlib dependencies are reused; the
gate does not claim an independent Lean kernel implementation or a Mathlib
rebuild. The runner has one compiler thread, a 240-second compiler timeout
per source, and warnings as errors. No unbounded heartbeat or recursion
limit is allowed by the source scan. The gate has a 380-second subprocess
timeout and preserves partial output on that timeout.

The exact shipped `compat/app_path.so` is hash checked and used directly to
repair executable-path discovery in this environment. The gate places
temporary adapter working files under its output directory. The adapter
does not modify the kernel, tactic proofs, or compiler executable.

`inventory.json` freezes every active source and declaration. Regeneration
through `scripts/generate_inventory.py` is a release-maintenance operation,
not a verification step. The verifier rejects source, target, or inventory
changes during a run, extra source files, unexpected declaration names,
duplicate declarations, and forbidden source constructs. The parser retains
apostrophes in Lean identifiers and is tested against duplicated,
mismatched, and forbidden-axiom reports. Every inventoried theorem,
definition, and abbreviation receives an explicit `#print axioms` query;
only `propext`, `Classical.choice`, and `Quot.sound` are accepted.

`audit/inherited_sources.json` records the 25 unchanged mathematical sources
from the parameter-chart release. New weighted sources and contracts are
checked alongside those exact sources. Two new negative controls correspond
to independently proved mathematical counterexamples: `r = 2s` does not
suffice at `p = 2`, and the displacement depth `r-s` cannot gain a digit
uniformly. Four inherited negative controls remain active. A negative
control passes only on the expected type mismatch, and cannot pass because
of a missing module, missing constant, panic, or timeout.

Failures are evidence of a source, environment, or resource issue until
classified; a failed compilation is not by itself a counterexample to the
mathematical theorem. Every run gets logs, source and output hashes, a
verification report, and a computation manifest. A successful run verifies
the exact frozen statements; it does not resolve general singular lifting,
native presentation invariance, completed descent, first-order root motion,
or analyticity.
