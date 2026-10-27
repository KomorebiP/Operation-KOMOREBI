# Komorebi Euler collision cores — first Lean handoff (v13)

**3 October 2026.** This is a standalone Lean continuation of the v12 research
package, not a claim that every v12 theorem is now formalized.

## Result

The release has **77 named theorem/lemma declarations in eight mathematical
modules**, compiled with Lean **4.34.0-rc2** and the pinned mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

It formalizes the nearest-neighbor coefficient core, the coefficientwise child
refinement bound, genuine derivative chart reductions, quadratic/cubic
critical discriminant identities, residue-certificate soundness for polynomials
over the actual 2-adic integers, and simple-root Hensel lifting. The exact
synthetic triple-root counterexample is also kernel checked.

All 77 declarations have a transitive `#print axioms` record. The union is only
`propext`, `Classical.choice`, and `Quot.sound`. No unfinished proof, custom axiom,
or native-evaluation proof axiom is used. Counts include helper lemmas and
negative controls; they are not 77 separately novel mathematical results.

**The remaining Euler-specific bridges are listed in `PROOF_AND_STATUS.md` and
`PROOF_BOUNDARY.json`.** In particular, the infinite Euler residual has not yet
been formally connected to the supplied normalized series and residue
congruences. No remaining critical scalar is proved universally nonzero.

## Reproduce with the portable kit

Use the previously recovered `Komorebi_Portable_Lean_4.34.0-rc2` directory.
No runtime binaries or font files are included in this release.

```sh
python3 scripts/replay.py \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /absolute/path/to/NEW_replay_directory
```

The script checks the toolchain and mathlib manifest, uses one Lean worker,
treats warnings as errors, compiles into a fresh directory, audits every named
theorem/lemma, and rejects any axiom outside the stated allowlist. It never saves
the full process environment. Existing evidence directories are refused.

The saved evidence was produced by this command in the working container.
Two clean replays are retained. Cached pinned mathlib dependencies were used;
Lean and all of mathlib were not rebuilt from source in this turn.

## Reproduce with a normal Lean/Lake installation

The portable Linux workflow above is the executed replay path. For a standard
installation with access to the pinned dependencies:

```sh
lake update
lake exe cache get
lake build
lake env lean -j1 -DwarningAsError=true Audit.lean
```

On Linux, after dependency setup, the full guarded replay also works without
`--runtime`:

```sh
python3 scripts/replay.py --evidence /absolute/path/to/NEW_replay_directory
```

`lean-toolchain` and `lakefile.toml` pin the required versions. The source uses
Lean's `module`/`public import` syntax for that toolchain; older Lean versions are
not supported by this handoff.

## File map

- `Euler/*.lean`: eight mathematical modules.
- `Euler.lean`: public umbrella import.
- `Audit.lean`: transitive axiom checks for all indexed declarations.
- `THEOREM_INDEX.json`: declaration names, source paths and line numbers.
- `PROOF_AND_STATUS.md`: statements, hypotheses, exact limitations, next targets.
- `PROOF_BOUNDARY.json`: machine-readable bridge/closure ledger.
- `evidence/clean_replay_*/`: successful clean compiler and axiom logs.
- `evidence/dev_*.log`: development diagnostics, deliberately separated from the
  successful replay logs. Failed attempts are not presented as passing proofs.
- `reference/V12_PROOF_AND_STATUS.md`: unchanged input note for cross-reference;
  not evidence that every statement in that note is now kernel checked.
- `PROVENANCE.json`: input archive hash, input integrity replay, version pins.

For integrity verification, run `python3 scripts/verify_manifest.py`.
The manifest is an integrity record, not a proof of the mathematics. The
compiler and transitive axiom audit provide the formal-checking evidence.
