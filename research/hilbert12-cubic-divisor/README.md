# Hilbert 12: Cubic Divisor Transport and Reconstruction

**Komorebi P. · Companion edition · October 7, 2026**

This set joins the traditional mathematical development, a reproducible Python visual guide, and a Lean companion. Editable TeX and Markdown, exact finite checks, original research checkpoints, and verification records accompany the PDFs.

## Reading order

1. `traditional/H12_Cubic_Divisor_Traditional.pdf`: definitions, arithmetic and theta normalization, divisor transport, cubic growth, canonical regularization, and analytic reconstruction.
2. `visual/H12_Cubic_Divisor_Visual_Guide.pdf`: eighteen Python figures, including a genuine three-dimensional integer chamber and its complex-plane image.
3. `lean/H12_Cubic_Divisor_Lean_Guide.pdf`: formal statement mapping, hypotheses, compiler and axiom evidence, resource limits, and the boundary of formal coverage.
4. `verification/FINAL_VALIDATION.md`: the edition's audit scope, checked artifacts, discovered failures, corrections, and remaining obligations.

## Mathematical scope

The principal correction has locally finite divisor support with two-sided cubic unsigned growth. Its ungrouped absolute canonical product has genus three. The fourth logarithmic derivative, reflection identity, and period-one transition specify the cubic exponential and a branch-free formula for the special cube.

The finite-theta obstruction applies to fixed positive-definite period matrices and affine restrictions, with finite polynomial combinations and derivatives. A nowhere-zero entire factor is allowed globally. Allowing arbitrary entire exponential factors inside sums would invalidate the quadratic growth bound; that larger class is not claimed.

The original equality `U_Gamma = U_alg` remains open. An analytic reconstruction by an infinite canonical product does not identify its special value with a class-field unit. The exact remaining polarized reality implication, and the separate periodic descent and principal-norm obligations, are stated in the manuscripts.

Lean checks the selected finite algebraic and integer statements. Complex divisor analysis, infinite-product convergence, and the class-field comparison remain ordinary mathematical arguments or open obligations as explicitly marked. Finite computations illustrate or test their stated ranges; floating diagnostics are not directed enclosures or universal proofs.

## Sources and evidence

The three publication folders are canonical for this edition. `sources/` and the original ZIPs under `provenance/` preserve the historical checkpoints unchanged, including wording corrected or restricted in the final manuscript. Fresh results are distinguished from inherited evidence. `SOURCE_MANIFEST.json` records packaged file hashes; `provenance/SOURCE_INTAKE_MANIFEST.json` records the protected originals.

## Rebuild

With the documented TeX dependencies installed:

```bash
python3 build_release.py
```

Use `--only traditional`, `--only visual`, or `--only lean` for one PDF. The script compiles the editable canonical TeX and records output under `verification/publication/rebuild/`. It does not silently overwrite mathematical source sections from historical inputs.

Regenerate figures with `python3 visual/generate_figures.py`. Numerical replay instructions and bounded-resource records are under `verification/numerical/`. The Lean project provides its pinned toolchain, dependency revision, and replay runner. Compiler runtimes and dependency caches are excluded from this ZIP.

Build a new verified source archive after an intentional edit with `python3 scripts/package_release.py`.
