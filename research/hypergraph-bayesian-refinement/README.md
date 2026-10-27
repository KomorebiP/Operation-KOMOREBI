# Hypergraph Lumpability and Bayesian Refinement

**Version:** 0.1.4  
**Author:** Komorebi P.  
**Project status:** `internal_complete`  
**Submission status:** independent proof review and literature review remain pending

This release contains the internally complete first paper in the series:

> **Hypergraph Lumpability and Bayesian Refinement for Dynamical Systems with Projector Resolutions**  
> Exact Interaction Quotients, Filtering Cocycles, and Certified Coarse Models

Version 0.1.4 integrates the final publication figure system into the manuscript. The theorem chain and proofs are unchanged. Nine visual assets are now generated directly from the certificate run as vector PDF and 600 dpi PNG files. They appear in seven figure environments, with the quotient views and the compression views paired for page economy. The new set includes the coefficient fiber map, exact quotient flow, exact filter residual, separate dynamical and Bayesian perturbation sweeps, the joint posterior certificate, and the hyperedge energy and pruning plots. The prose conventions from version 0.1.3 remain in force.

`internal_complete` means that the declared theorem chain, proofs, examples, algorithms, tests, and reproducibility materials are present. It does not mean that the paper is ready for journal submission.

## Core theorem chain

For a surjective coarse map \(C:X_f\to X_c\), the paper studies

\[
CA_m^f=A_m^cC^{\times m}
\Longrightarrow
CF_f=F_cC
\Longrightarrow
C\Phi_t^f=\Phi_t^cC.
\]

For normalized positive observations,

\[
CL_f=sL_cC
\Longrightarrow
C\mathsf B_f=\mathsf B_cC.
\]

The two identities combine to give

\[
C\Psi_{1:N}^f=\Psi_{1:N}^cC.
\]

When exact descent fails, the paper carries the interaction defect and the observation defect into an explicit certificate for the final posterior.

## Release contents

| Path | Purpose |
|---|---|
| `Hypergraph_Lumpability_Bayesian_Refinement.pdf` | Compiled 52 page paper |
| `Hypergraph_Lumpability_Bayesian_Refinement.tex` | Editable manuscript |
| `src/priq/core.py` | Finite reference implementation |
| `tests/test_priq.py` | Independent tests of the main formulas |
| `examples/run_certificates.py` | Deterministic certificate and figure generator |
| `figures/` | Vector PDF and large PNG figures |
| `tables/` | Generated LaTeX and CSV ledgers |
| `results/` | JSON verification and manuscript audit records |
| `build/pdf_contact_sheet.png` | Rendered overview of the manuscript |
| `tools/audit_manuscript.py` | Deterministic manuscript audit |
| `INTERNAL_COMPLETION_AUDIT.md` | Editorial and verification record |
| `PROOFREADING_AUDIT.md` | Final prose and proof presentation audit |
| `MANUSCRIPT_STATUS.md` | Build and claim status |
| `SOURCE_CROSSWALK.md` | Relation to earlier Komorebi work |
| `FILE_MANIFEST.json` | File sizes and SHA256 digests |

## Verified build state

| Check | Result |
|---|---:|
| Deterministic finite certificates | 35 passed, 0 failed |
| Independent pytest functions | 8 passed |
| Compiled manuscript | 52 pages |
| Theorem statements without an explicit proof | 0 |
| Undefined references or citations | 0 |
| Overfull boxes | 0 |
| Semicolons in ordinary manuscript prose | 0 |
| Banned stylistic dash compounds in ordinary manuscript prose | 0 |
| Deterministic manuscript audit | 22 passed, 0 failed |

These checks validate the supplied finite examples and implementation. They do not replace independent mathematical review or an external review of the literature and priority claims.

## Run the verification suite

From the extracted source root in PowerShell:

```powershell
$env:PYTHONPATH="$PWD\src"
python .\examples\run_certificates.py
python -m pytest -q
```

Build the paper and run the manuscript audit:

```powershell
$env:PYTHONPATH="$PWD\src"
python .\examples\run_certificates.py
python -m pytest -q
latexmk -pdf -interaction=nonstopmode -halt-on-error .\Hypergraph_Lumpability_Bayesian_Refinement.tex
python .\tools\audit_manuscript.py
```

POSIX shell:

```bash
PYTHONPATH=src python examples/run_certificates.py
PYTHONPATH=src python -m pytest -q
latexmk -pdf -interaction=nonstopmode -halt-on-error Hypergraph_Lumpability_Bayesian_Refinement.tex
python tools/audit_manuscript.py
```

## Dependencies

1. Python 3.11 or later
2. NumPy
3. Matplotlib
4. pytest for the independent test suite
5. A LaTeX installation containing `latexmk`, `pdflatex`, and the packages imported by the manuscript

The numerical reference implementation runs on the CPU and does not require network access.
