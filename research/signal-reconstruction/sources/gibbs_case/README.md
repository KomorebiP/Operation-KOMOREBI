# Projector-Resolved Gibbs Reconstruction

This release follows one periodic signal from its smooth and discontinuous pieces through the Gibbs limit, packet separation, finite interval recovery, and exact reconstruction.

## Central signal

\[
f(x)=\frac14+\frac25\cos(2x)-\frac13\sin(3x)+\frac15\cos(5x)+\mathbf1_{[-\pi/3,\pi/3)}(x).
\]

## Main result

On the model space

\[
\mathcal M_5=\mathcal T_5\oplus\operatorname{span}\{j\},
\]

the operator

\[
\mathcal R_N=S_NP_s+P_j
\]

is the identity for every \(N\ge5\). The smooth packet is reconstructed from its finite Fourier support. The interval packet is carried through unchanged.

The finite sampled example uses every allowed periodic interval on a 96-point grid. It recovers

```text
(start, length, amplitude) = (32, 32, 1)
```

with a positive objective gap.

## Run

PowerShell:

```powershell
Set-Location <EXTRACTED_FOLDER>
Set-ExecutionPolicy -Scope Process Bypass -Force
.\Run_All.ps1
```

POSIX:

```bash
cd <EXTRACTED_FOLDER>
./run_all.sh
```

## Contents

- `Projector_Resolved_Gibbs_Case_Study.pdf` - 88-page monograph.
- `Projector_Resolved_Gibbs_Case_Study_KaTeX.md` - KaTeX-friendly derivation.
- `gibbs_packet_case.py` - the single Python implementation.
- `figures/` - 60 vector-PDF and 60 matching PNG figures.
- `tables/` - coefficient, metric, recovery, runtime, and test records.
- `results/` - numerical results and PDF audit data.
- `Run_All.ps1` and `run_all.sh` - complete rebuild commands.

## Scope

The theorem applies to the smooth-plus-one-interval model stated in the paper. The noise and off-grid sections report finite experiments. The work does not claim universal discontinuity discovery or unrestricted removal of Gibbs ringing.

## Layout revision

The revised edition places figure notes with their figures, removes standalone part pages, compacts the contents and figure list, and uses one Python statement per line. The visible PDF contains no semicolons. No page consists of a single sentence or isolated line.
