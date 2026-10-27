# Self-Calibrating Polyphase Fourier Reconstruction

This release contains a theorem-facing Fourier edge-recovery study and one closed Python implementation.

## Main result

The paper studies periodic signals `f = s + j` with a smooth background and a finite unknown jump packet. Decimated derivative moments recover aliased edge phases. Offset polyphase channels recover the missing physical phase from the Fourier data. Under a branch-margin condition, the selected root equals the oracle root and inherits the decimated method's one-order location gain. In the exact bandlimited control class, an explicit construction uses at most `3*Lmax + 1` high-frequency coefficients to recover the unknown order, physical phases, and jump amplitudes. The recovered edge is then synthesized directly rather than represented by a truncated global Fourier series.

## Files

- `Self_Calibrating_Polyphase_Gibbs_Reconstruction.pdf` - final paper
- `Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex` - complete LaTeX source
- `Self_Calibrating_Polyphase_Gibbs_Reconstruction_KaTeX.md` - KaTeX-friendly derivation
- `polyphase_gibbs_breakthrough.py` - single implementation
- `figures/` - 39 PDF and 39 PNG figures
- `tables/` - rate, noise, oracle, random-family, finite-budget, collision, offset, runtime, and test data
- `results/results.json` - principal numerical ledger
- `results/pdf_preflight.json` - structural PDF check

## Reproduction

From the extracted source directory:

```powershell
python polyphase_gibbs_breakthrough.py --out .
pdflatex -interaction=nonstopmode -halt-on-error Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex
pdflatex -interaction=nonstopmode -halt-on-error Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex
```

Required Python packages:

- NumPy
- SciPy
- SymPy
- Matplotlib

The implementation is deterministic. It exits with an assertion failure if any named certificate fails.

## Recorded verification

- 31 of 31 named checks passed
- 40 figure pairs generated
- 68 PDF pages
- no PDF preflight warnings
- no LaTeX overfull or underfull boxes
- no undefined references
- all fonts embedded
- no blank or one-line pages

## Claim boundary

Prony inversion, annihilating filters, finite-rate innovation, decimated algebraic Fourier reconstruction, and shifted-sample de-aliasing are established methods. The contribution developed in the paper is the oracle-equivalent, rate-preserving integration of unknown-order detection, offset-channel branch recovery, validation, and native edge synthesis for the declared piecewise-smooth Fourier class.

The paper does not claim separation-free recovery, arbitrary edge geometry, a minimax noisy theorem, or confirmed historical priority for the complete package.
