# Using the Komorebi Space Lean library

## Environment

This edition uses Lean `4.34.0-rc2`, compiler revision `6a10ac8c22beadecabdbb0919c2b50214762f91d`, and mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The supplied toolchain file and dependency manifest identify the required environment. Keep their versions together.

The source package contains the project sources and verification evidence. It does not include the multi-gigabyte Lean compiler and dependency cache. Provision the pinned versions with the normal Lean and Lake workflow, or reuse an existing matching installation and cache. There is no package-specific offline installer in this edition.

## Build

Run this command from the directory containing `lakefile.toml`:

```sh
lake build
```

The configured default target is `KomorebiSpaceCombined`. A bare build uses that target without updating dependency revisions.

The build checks the source library against the installed pinned environment. A different dependency revision or compiler version is a different verification environment.

## Imports

| Import | Mathematical content |
| --- | --- |
| `KomorebiSpace` | Coherent realization, obstruction, descent, transport, and quantitative repair. |
| `KomorebiSpaceRegularization` | Regularized Hilbert repair, primal and dual certificates, and protected regularized repair. |
| `KomorebiSpaceCombined` | The complete library, including bounded realization, budget duality and robustness, limits, and coordinate certificates. |

A narrower import is useful in a small application:

```lean
import KomorebiSpace.CoordinateCovector

open KomorebiSpace.CoordinateCovector

#check gram_isUnit
#check protected_coordinate_certificate
```

Both coordinate modules contribute declarations to the namespace `KomorebiSpace.CoordinateCovector`. A declaration's namespace is not always identical to its source module.

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

## Compilation and the accepted verification audit

An ordinary build is a compilation check. The accepted audit additionally records source hashes, compiler and dependency identities, declaration provenance, permitted axiom dependencies, diagnostic control outcomes, and independent reviews. Its control suite contains expected successes, expected mathematical rejections, and expected axiom-policy rejections. The package's normal Lake configuration does not declare these as a `lake test` driver.

The permitted axiom dependencies are `propext`, `Classical.choice`, and `Quot.sound`. Project-specific axioms, admitted proofs, and unsafe production declarations are outside the accepted policy. Classical `noncomputable` constructions are mathematical existence constructions, not numerical solvers.

Use the separate technical record to repeat the complete accepted audit in its exact environment. A successful local `lake build` does not by itself recreate that entire evidence record.
