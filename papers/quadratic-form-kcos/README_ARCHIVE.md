# Quadratic-Form Engine / K-COS

**Komorebi P. · Final companion edition · October 7, 2026**

This reading set joins the complete quadratic-form manuscript with query-adaptive spectral packetization, a visual guide, a focused Lean companion, executable Python, and verification evidence. The editable TeX and Markdown files are included.

## Reading order

1. `traditional/Quadratic_Form_KCOS_Traditional.pdf`: full traditional development, proofs, historical experiments, and final-edition scope.
2. `visual/Quadratic_Form_KCOS_Visual_Guide.pdf`: reproducible Python illustrations and finite worked examples.
3. `lean/Quadratic_Form_KCOS_Lean_Guide.pdf`: exact formal statements, hypotheses, declaration mapping, compiler evidence, and remaining obligations.
4. `verification/FINAL_VALIDATION.md`: evidence for this edition, including failures found and their corrections.

The canonical manuscripts are in those three folders. Documentation retained under `engine/` is inherited research history and does not supersede the final-edition manuscripts. Original source ZIPs and original figure bytes are preserved under `provenance/` and `engine/`. The publication folders include corrected layout derivatives where needed. SHA-256 records distinguish them.

## Mathematical and implementation contract

The central object is a finite Gaussian quadratic form. Exact factor and block identities preserve its operator while changing storage and execution. Structural phase bounds, spectral recovery, and spectral packets supply distinct layers of the calculation.

The positive directed backend uses a nonempty positive spectrum of rank greater than two, an admissible positive tilt, a nonnegative threshold, and a support endpoint above the threshold. The current automatic planner handles upper-tail queries above the mean. The public accuracy decision compares a directed upper bound on the interval's multiplicative ratio with a directed lower bound on the requested tolerance. Authoritative interval endpoints are serialized outward.

The dense verified-spectrum bridge treats stored binary64 factors as exact dyadic matrices; it does not enclose an unknown pre-rounding matrix. The large-scale streaming architecture and the signed/noncentral floating paths have their own mathematical and numerical scope. A floating analytic error ledger is not, by itself, a directed machine enclosure.

The Lean companion checks a declared finite algebraic and real-order subset. It does not certify Gaussian laws, the infinite COS series, the transcendental interval backend, or the entire Python engine. Each boundary is mapped in the companion.

## Rebuild and replay

Rebuild all three PDFs with a TeX installation:

```bash
python3 build_release.py
```

Use `--only traditional`, `--only visual`, or `--only lean` for one companion. The logs are written under `verification/publication/`.

The visual figure generator is `visual/generate_figures.py`; run it from the visual folder as documented in that source. Numerical replay commands and the exact environment are recorded under `verification/`. Lean replay uses the pinned toolchain and dependency revision recorded in the Lean project. A compiler runtime is not embedded in this publication ZIP.

The display corrections are documented in `verification/VISUAL_LAYOUT_CORRECTIONS.md`; the mathematical and numerical evidence remains unchanged. Original empirical tables remain labeled as historical evidence. Fresh tests apply to the corrected final engine. The verification records distinguish those two forms of evidence.
