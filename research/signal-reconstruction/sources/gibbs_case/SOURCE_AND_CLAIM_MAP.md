# Source and claim map

## Exact theorem chain

1. `smooth_fourier_coefficient` and `jump_fourier_coefficient` give the exact coefficients.
2. `dirichlet_kernel` and `jump_fourier_partial_sum` give finite Fourier reconstruction.
3. `gibbs_profile` and `gibbs_constant` give the scaled edge profile and limiting constant.
4. `PacketState`, `smooth_fourier_partial_sum`, and `packet_reconstruction` implement the smooth-edge split and synthesis.
5. `CandidateLibrary` builds the finite residualized interval family and profile least-squares fit.
6. `CandidateLibrary.search` performs the finite minimization and reconstructs the signal.
7. The final checks in `build_experiment` test the identities, recovery result, and negative controls.

## Status map

| Claim | Status | Basis |
|---|---|---|
| Fourier coefficient formulas | Exact identity | Direct integration and numerical quadrature checks |
| Dirichlet-kernel reconstruction | Exact identity | Fourier algebra |
| Gibbs sine-integral profile | Asymptotic theorem | Derivation in the paper and finite scaling checks |
| Complementary smooth and edge packets | Exact theorem | Direct-sum model |
| Reconstruction for `N >= 5` | Exact theorem | Degree-five Fourier closure and zero residual |
| Exact finite interval recovery | Exact finite theorem under the distinct-ray condition | Complete enumeration and positive gap |
| Noise robustness | Numerical experiment | Fixed random seed and finite repetitions |
| Off-grid localization | Numerical experiment | Six finite grid sizes |
| Universal edge recovery | Not claimed | Outside the stated model |

## Artifact map

- `Projector_Resolved_Gibbs_Case_Study.pdf` - the 88-page proof and worked example.
- `Projector_Resolved_Gibbs_Case_Study_KaTeX.md` - KaTeX-friendly derivation.
- `Projector_Resolved_Gibbs_Case_Study.tex` - complete LaTeX source.
- `gibbs_packet_case.py` - single Python implementation.
- `tables/test_ledger.csv` - machine-readable test record.
- `results/numerical_results.json` - principal numerical results.
- `results/pdf_preflight.json` - structural PDF preflight.
- `results/layout_audit.json` - final layout audit.
