# Stratified Relational Workspace Theory

**A Core-Transfer Framework for Distributed Cognition, Collaboration, and Epistemic Systems**

- **Author:** Komorebi P.
- **Repository version:** `1.0.0`
- **Status:** Complete preprint monograph; external mathematical and empirical review pending

[Read the 209-page monograph](monograph/Stratified_Relational_Workspace_Theory.pdf)

## Overview

Stratified Relational Workspace Theory studies when a collection of people, models, artifacts, instruments, and computational processes supports a genuine shared workspace rather than replicated storage, centralized control, or merely correlated activity.

A stratified relational workspace is defined as a temporally persistent, causally efficacious, jointly reconstructible structure represented only partially in several heterogeneous components. Its identity is determined by invariants preserved under admissible transfer, and its operative capacity is relational only when no individual component or matched local-storage null reproduces the relevant function.

The central identity principle is

$$
\boxed{\text{workspace identity}=\text{persistent invariant causal organization under admissible transport}.}
$$

The framework does **not** infer consciousness, personhood, moral status, or unrestricted autonomy from structural coherence, agency, or self-maintenance.

## Scope of the monograph

The theory develops five connected layers:

1. **Structural geometry.** Heterogeneous local state spaces, core-residual decompositions, compatible global sections, holonomy-fixed cores, transfer Laplacians, spectral stability, gauge covariance, and pathwise leakage.
2. **Operational relationality.** Canonical predictive states, feasible interventions, coalition risk, matched relational nulls, causal specificity, and reentry.
3. **Persistence and identity.** Moving workspace subspaces, reconstruction frames, erasure resilience, handoff, replacement invariance, gluing, and hierarchical composition.
4. **Formation and agency.** Learned transfers, boundary recovery, provenance, goal retention, counterfactual policy evaluation, damage detection, repair, and self-maintenance.
5. **Epistemic robustness.** Faithful coarse-graining, decomposition robustness, specification robustness, experimental identifiability, partial identification, and uniform finite-sample certification.

The individual mathematical ingredients are largely established. The candidate contribution is their noncompensatory integration into one falsifiable certification architecture, together with matched near-miss systems that the certificate is designed to reject.

## Repository structure

| Path | Purpose |
|---|---|
| [`monograph/`](monograph/) | Canonical modular LaTeX source and compiled PDF |
| [`archive/v1.0.0/`](archive/v1.0.0/) | Frozen single-file source snapshot from which the modular source is generated |
| [`verification/`](verification/) | Deterministic mathematical regression checks and reference outputs |
| [`audits/`](audits/) | Priority register, theorem-like statement index, and verification records |
| [`docs/`](docs/) | Build, review, reproducibility, licensing, release, and publication guidance |
| [`scripts/`](scripts/) | Cross-platform build, verification, packaging, and source-splitting utilities |
| [`.github/`](.github/) | Continuous integration, tagged-release automation, issue forms, and pull-request templates |

## Build

A recent TeX Live installation with `latexmk` is required. From the repository root:

```bash
python scripts/repo.py build
```

Equivalent Make target:

```bash
make build
```

Windows PowerShell:

```powershell
python .\scripts\repo.py build
```

The generated PDF is written to `build/Stratified_Relational_Workspace_Theory.pdf`.

Detailed platform notes are in [`docs/BUILDING.md`](docs/BUILDING.md).

## Verify

Install the Python verification dependencies:

```bash
python -m pip install --requirement requirements.txt
```

Run the complete repository audit:

```bash
python scripts/repo.py verify --strict
```

Strict verification checks:

- successful LaTeX convergence;
- absence of unresolved references, duplicate labels, box warnings, and LaTeX warnings;
- the expected 209-page output;
- embedded fonts and unencrypted, text-based PDF output;
- extracted-text equivalence between the rebuilt and committed PDFs;
- exact correspondence between the modular source and frozen monolithic snapshot;
- repository metadata and internal Markdown links;
- all deterministic mathematical regression checks.

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for the verification model and its limits.

## Package a release

```bash
python scripts/repo.py package --strict
```

This produces a versioned PDF, source ZIP, source tarball, and `SHA256SUMS.txt` under `dist/`. Pushing a tag such as `v1.0.0` activates the included release workflow.

## Review and contribution

The preferred review path is issue-first. Mathematical reports should identify the statement label, assumptions, precise concern, and either a counterexample, proof gap, or proposed correction. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [`review guide`](docs/REVIEW_GUIDE.md).

The [`statement index`](audits/statement_index.md) lists every theorem, proposition, lemma, corollary, definition, example, and remark. The [`priority register`](audits/priority_register.csv) distinguishes standard machinery, adaptations, synthesis claims, and unresolved empirical claims.
The [`GitHub readiness report`](audits/github_readiness_report.md) records the clean-checkout, packaging, Git, and PDF-regression audit.

## Citation

Citation metadata is available in [`CITATION.cff`](CITATION.cff) and [`CITATION.bib`](CITATION.bib).

## License status

This release is publicly readable but is currently **not distributed under an open reuse license**. All rights are reserved unless applicable law or separate permission allows reuse. The rationale and possible future licensing options are documented in [`docs/LICENSING.md`](docs/LICENSING.md).
