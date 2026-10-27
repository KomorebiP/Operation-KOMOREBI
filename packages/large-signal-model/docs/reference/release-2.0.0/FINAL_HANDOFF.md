# Final PR-LASM Handoff

**Author:** Komorebi P.

This release closes the construction phase of the Projector-Resolved Large Algebraic Signal Model.

## Canonical capstone

The canonical paper is:

`paper/Projector_Resolved_Large_Algebraic_Signal_Model.pdf`

The executable model is the package:

`komorebi-pr-lasm==2.0.0`

The main command is:

```text
python -m komorebi_arc3_offline.lasm_cli benchmark --output results/pr_lasm_benchmark
```

## Architecture

The model retains every frame in an exact multi-atlas archive and derives declared statistical states for prediction. It supports spatial, Fourier, Haar-wavelet, polyphase, and categorical color coordinates; mixed-depth packet refinement; a typed Bayesian operator grammar; explicit memory kernels; exact deterministic replay graphs; and active planning.

## Verified finite release

- 36 automated tests passed.
- Seven controlled operator mechanisms and their seven intended atlases were identified.
- Four deterministic interactive systems were solved.
- The exact reconstruction residuals remained at floating-point roundoff.
- The 25 supplied local environment source trees passed static offline validation.
- The wheel built and imported from an isolated target.
- The 38-page paper and all 30 figure pairs passed layout and PDF checks.

## Official local suite

The full release includes the 25 environment trees and Windows/Conda offline launch scripts. The official `arc-agi` and `arcengine` packages were absent from the build container, so this handoff does not contain an official ARC score. Running the supplied scripts on the target machine is an empirical deployment step, not a missing definition in the model.

## Claim boundary

PR-LASM is a complete finite candidate architecture for an exact-reconstruction, multi-atlas, fully algebraic large signal model with Bayesian operator selection and active planning. It is not presented as universal program induction or AGI.
