# Projector-Resolved Seed Calculus V

## Polyphase Signal Calculus: Exact Reconstruction, Edge Packets, Wavelets, and Smith Coordinates

**Author: Komorebi P.**

This release contains Paper V of the Projector-Resolved Seed Calculus series together with its signal-processing implementation, exact finite tests, numerical edge experiments, Smith-coordinate figures, and reproducibility material.

The paper uses the operator language fixed in Papers I-III:

\[
\text{seed}
\longrightarrow
\text{address}
\longrightarrow
\text{project}
\longrightarrow
\text{transfer}
\longrightarrow
\text{refine}
\longrightarrow
\text{reconstruct}.
\]

For signals, the seed is the impulse `delta_0`, the address operator is translation, and residue projectors are the polyphase analysis coordinates. The paper proves exact polyphase reconstruction, nested refinement, FIR transfer laws, perfect-reconstruction filter-bank identities, Haar and lifting reconstruction, wavelet-packet energy conservation, nonlinear cyclic product laws, and the Möbius action induced by cyclic phase rotation on the Smith disk.

The edge theory is deliberately separated into two parts:

1. **Known edge packet.** If the discontinuous packet is supplied exactly and is not spectrally approximated, the reconstruction error is exactly the error of the remaining smooth packet.
2. **Estimated edge packet.** The included estimator is a narrow positive-contrast synthetic model. Its numerical performance is recorded, but it is not presented as a universal edge-recovery theorem.

The paper contains no local bibliography or citation commands. References for the complete series are maintained separately and will be added only at the end of the collected work.

## Contents

- `Projector_Resolved_Seed_Calculus_V.pdf` - final 28-page paper
- `Projector_Resolved_Seed_Calculus_V.tex` - complete LaTeX source
- `projector_signal/` - Python implementation
- `tests/` - automated finite and numerical tests
- `figures/` - 16 PNG and 16 vector-PDF figures
- `results/numerical_results.json` - machine-readable results
- `tables/` - numerical summary tables
- `Source_and_Claim_Map.md` - theorem, classical-boundary, numerical, and conjectural map
- `Verification_Notes.md` - build and audit record
- `Verification_Render.png` - full-page render contact sheet
- `Run_All.ps1` - Windows PowerShell reproduction script

## PowerShell reproduction

After extracting the folder into Downloads:

```powershell
$Work = "$env:USERPROFILE\Downloads\Projector_Seed_Calculus_V_Release"
Set-Location $Work
Set-ExecutionPolicy -Scope Process Bypass -Force
& .\Run_All.ps1 -Work $Work
```

The runner checks the current environment before installing anything. Packages already satisfying the requirements are left unchanged. To request dependency updates explicitly:

```powershell
& .\Run_All.ps1 -Work $Work -Update
```

To run only the Python study and tests:

```powershell
Set-Location "$env:USERPROFILE\Downloads\Projector_Seed_Calculus_V_Release"
python .\scripts\generate_all.py
python -m pytest -q
```

To compile the paper manually when `latexmk` is available:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error .\Projector_Resolved_Seed_Calculus_V.tex
```

## Computational scope

The included experiments are CPU-based. No GPU benchmark or GPU speed claim is made in Paper V. The exact theorems are independent of the numerical experiments.
