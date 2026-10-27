# Verification notes

**Project:** Universal Generative Deformation Calculus  
**Version:** 1.1.0  
**Author:** Komorebi P.

## Mathematical and computational verification

- Independent tests: **50 of 50 passed**
- Built-in experiment checks: **18 of 18 passed**
- Finite visual-atlas realizations: **11**
- Python-generated figures: **20 PDF/PNG pairs**
- Integer walk: **8,191 raw paths**, **25 quotient nodes**, **46 quotient edges**
- Analytic system: **315 raw paths**, **77 quotient nodes**, **149 quotient edges**, and **24 audited invalid operations**
- Polynomial system: **781 raw paths**, **224 quotient nodes**, **355 quotient edges**
- Sequence system: **156 raw paths**, **111 quotient nodes**, **135 quotient edges**
- Gaussian system: **2,125 raw paths**, **126 quotient nodes**, **335 quotient edges**
- Projective qubit system: **1,365 raw paths**, **6 quotient states**, **24 quotient edges**
- Matrix system: **400 raw paths**, **55 quotient nodes**, **161 quotient edges**
- Affine-shape system: **259 raw paths**, **147 quotient nodes**, **210 quotient edges**
- Graph system: **150 raw paths**, **17 quotient classes**, **41 quotient edges**
- Congruence-lifting examples distinguish unique simple lifts from singular branching

## Package verification

- Wheel built successfully: `komorebi_generative_deformation-1.1.0-py3-none-any.whl`
- Clean target-directory wheel import and version check passed
- Installed command-line exploration smoke test passed
- Command-line exploration smoke tests are included
- PowerShell-compatible build and verification scripts are included

## Document verification

- Final manuscript length: **59 pages**
- No LaTeX overfull or underfull box warnings
- No undefined references
- Every page rendered at 170 DPI and inspected through a full-document contact sheet
- PDF preflight and font-embedding checks are recorded with the release

## Claim boundary

The release proves and implements a calculus relative to a **declared admissible direction grammar**. It does not claim that one finite grammar enumerates every conceivable mathematical transformation, that finite search completes an infinite forest without an additional theorem, or that generated families are historically new without a separate literature and priority review.
