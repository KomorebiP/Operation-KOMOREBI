# Using the Komorebi Space Lean library

## Environment

This edition uses Lean `4.34.0-rc2`, compiler revision `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The supplied toolchain file and dependency manifest identify the required environment. Keep their versions together.

The source package contains the project sources and verification evidence. It does not include the multi-gigabyte Lean compiler and dependency cache. Provision the pinned versions with the normal Lean and Lake workflow, or reuse an existing matching installation and cache. With the pinned toolchain installed, prepare external dependency caches from this `lean` directory:

```sh
lake exe cache get
```

Preparation can require network access. The integrated audit uses the installed external caches and records their identities, but does not rebuild or independently authenticate them. There is no package-specific offline installer in this edition.

## Build

Run this command from the directory containing `lakefile.toml`:

```sh
lake build
```

The configured default targets are `KomorebiSpaceCombined` and `KomorebiSpaceDiagonal`. A bare build requests both without updating dependency revisions. Use `lake build KomorebiSpaceDiagonal` for the focused diagonal development.

The build checks the source library against the installed pinned environment. A different dependency revision or compiler version is a different verification environment.

## Imports

| Import | Mathematical content |
| --- | --- |
| `KomorebiSpace` | Coherent realization, obstruction, descent, transport, and quantitative repair. |
| `KomorebiSpaceRegularization` | Regularized Hilbert repair, primal and dual certificates, and protected regularized repair. |
| `KomorebiSpaceCombined` | The general library, including bounded realization, budget duality and robustness, limits, and coordinate certificates. |
| `KomorebiSpaceDiagonal` | Actual infinite diagonal model, certified tails, sharp all-budget asymptotic, rounded noisy and inexact rates, and the concrete range obstruction. |

A narrower import is useful in a small application:

```lean
import KomorebiSpace.CoordinateCovector

open KomorebiSpace.CoordinateCovector

#check gram_isUnit
#check protected_coordinate_certificate
```

Both coordinate modules contribute declarations to the namespace `KomorebiSpace.CoordinateCovector`. A declaration's namespace is not always identical to its source module.

For the two added diagonal connections, use:

```lean
import KomorebiSpace.DiagonalInexactRate
import KomorebiSpace.DiagonalRangeObstruction

#check KomorebiSpace.DiagonalRegularization.diagonal_inexact_rounded_rate
#check KomorebiSpace.DiagonalRegularization.T_not_closed_range
#check KomorebiSpace.DiagonalRegularization.w_mem_closure_not_range
```

## Inspect a theorem

Create `Example.lean` beside the package configuration, then add:

```lean
import KomorebiSpace.Correction

#check KomorebiSpace.CorrectionProblem.flatten_iff
#print KomorebiSpace.CorrectionProblem.flatten_iff
#print axioms KomorebiSpace.CorrectionProblem.flatten_iff
```

After building the imports, elaborate the file with:

```sh
lake env lean -j1 -DwarningAsError=true -DautoImplicit=false Example.lean
```

`#check` prints the declaration type, `#print` includes its proof term, and `#print axioms` lists axiom dependencies. The `-j1` option belongs to Lean and limits that process to one thread. Warning rejection and disabled automatic implicit binders help expose accidental omissions in new statements.

## Read the assumptions precisely

The library's `gradient` is the normal equation residual `T* (T a - r) + alpha a`, one half of the usual derivative gradient of the squared regularized objective. The error estimates use this normalization.

Protected corrections have type `p.ker`, the entire kernel of the protected observation. A basis used for its coordinate certificate spans this whole space. The certificate uses the inverse Gram quadratic form, not the raw squared coordinate norm.

The regularized optimizer requires a strictly positive parameter. Algebraic basis-change identities can have weaker hypotheses. A minimum preimage limit requires attainment of the projected datum. Convergence of fitted data to the range closure does not alone provide such a preimage.

The concrete inexact rate retains both the data-noise bound and a normal-residual bound computed against the measured datum. Its rounded schedule assumes `0 < δ ≤ 1`; a scalar tolerance budget alone does not assert that a proposed correction meets that tolerance. The range obstruction concerns the actual infinite diagonal operator. It does not infer nonclosedness from a finite numerical truncation.

## Run the integrated verification audit

From the publication root, one directory above this `lean` directory, run:

```sh
python3 verification/runner/runner.py --output ../verification-v1.15.0-01
```

The output directory must be new and outside the publication tree. The runner snapshots the input sources, rebuilds every project target into an initially empty object directory, inventories project declarations, checks recursive axiom dependencies, and runs the 56 diagnostic controls. It compiles sequentially with `-j1`, `-DwarningAsError=true`, and `-DautoImplicit=false`. Sequential compilation limits concurrency without imposing a fixed memory cap.

An ordinary `lake build` is a separate compilation check. The runner's control suite contains expected successes, expected elaboration rejections, and expected axiom-policy rejections. The package's normal Lake configuration does not declare these as a `lake test` driver. `receipt.json` records the attempt's actual status and evidence; a failed or interrupted attempt is retained. A static `--plan-only` run does not constitute proof verification.

The permitted axiom dependencies are `propext`, `Classical.choice`, and `Quot.sound`. Project-specific axioms, admitted proofs, and unsafe production declarations are outside the accepted policy. Classical `noncomputable` constructions are mathematical existence constructions, not numerical solvers.

The current suite includes all 52 inherited controls and four added controls for the inexact rate and range obstruction. Their expected outcomes are 18 acceptances, 35 elaboration rejections, and three policy rejections. The runner checks the specified diagnostics so that an infrastructure error does not count as an intended mathematical rejection. See [the runner guide](../verification/runner/README.md) for settings, provenance, failure interpretation, and the full acceptance conditions.

Compiler and installed external-cache bytes are recorded at the replay's endpoints. Those identity checks do not authenticate the caches or detect a transient modification restored before the final snapshot. Compilation and axiom checks also do not by themselves establish correspondence with the printed mathematics; independent statement reviews address that question.

The Technical Record preserves the historical parent and diagonal audits separately. To repeat the earlier diagonal-only procedure, unpack `../verification/DIAGONAL_ACCEPTED_EVIDENCE.zip` into a separate directory and follow its `REPRODUCIBILITY.md`. That historical package contains its accepted sources, scripts, and controls together.

## Follow an executable example

[WORKED_EXAMPLE.md](../examples/WORKED_EXAMPLE.md) connects a finite rational protected correction to exact expected output, certificate-generation and verification commands, and the relevant general Lean declarations. Its Python computations are tested implementations, not certified Lean extractions.

For citation and current reuse status, see [CITATION.bib](../CITATION.bib) and [REUSE.md](../REUSE.md).
