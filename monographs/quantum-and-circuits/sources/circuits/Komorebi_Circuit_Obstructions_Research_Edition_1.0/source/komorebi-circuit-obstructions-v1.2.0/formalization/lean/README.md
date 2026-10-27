# Lean Block 02: degree and complete-cover restoration bounds

Pinned toolchain: `leanprover/lean4:v4.34.0-rc2`. Only bundled `Std` is imported. No Mathlib or third-party packages are required.

From the repository root with that toolchain already on PATH:

```sh
python scripts/verify_lean.py
```

A portable toolchain can be selected without modifying PATH:

```sh
python scripts/verify_lean.py --toolchain /path/to/toolchain
```

The verifier makes a new source directory with no project build products, requires a strict build, audits all 115 theorem declarations, replays eight modules through the bundled checker, and rejects eight deliberately invalid controls. Each subprocess has a 90-second wall-time cap. Missing tools and timeouts are failures/inconclusive execution, never proof success. The script performs no downloads.

Only Linux x86_64 execution was tested. WSL is a suggested way to use a compatible Linux toolchain, not a separately executed platform test. No toolchain binaries are included.

## Modules

| Module | Declarations | Role |
|---|---:|---|
| Gates | 16 | Inherited legal semantics, inverse, and counts |
| CutComparison | 13 | Inherited C01 and every-cut specialization |
| Examples | 11 | Inherited dirty scratch and output-active controls |
| Degree | 19 | Concrete XOR-monomial degree certificates and closure |
| MultiplicativeDegree | 12 | Products of current registers, gate updates, degree with sharing |
| SafeDegree | 22 | Actual beta definition, existence, balanced cuts, bound |
| AffineOutput | 14 | Zero-Toffoli affine implementation, betaStar, joint endpoint |
| DegreeChecks | 8 | AND2 not affine, beta=betaStar=2, Toffoli necessity |

## Exact endpoint

`CircuitObstructions.restored_degree_and_cover_bound` proves that an implementation restoring every logical input and zero workspace for both initial target values satisfies:

```text
DegreeLE (toffoliCount c + 1) f
and
2 * betaStar f <= toffoliCount c + 3.
```

`DegreeLE` has a proved concrete polynomial representation. The actual least complete-safe degree beta and least affine-output bound betaStar exist; betaStar<=n is proved. No degree growth, balanced cut, or affine compiler is assumed as an axiom. Dirty intermediate input/workspace registers and output feedback are allowed.

This covers C01, the maintained NCT version of F3, and the lower-bound component of C02. The C02 evaluation-span dual and C03-C08 are not formalized by this block. Neither the declaration count nor a bounded Python test is a count of discoveries or a resolution of P versus NP.
