# Complex Signal and Image Benchmark

This release contains the complete benchmark for projector-resolved Gibbs reconstruction on complex one-dimensional signals, finite-dictionary images, out-of-model geometry, and natural images.

## Main files

- `Complex_Signal_Image_Gibbs_Benchmark.pdf`
- `Complex_Signal_Image_Gibbs_Benchmark.tex`
- `Complex_Signal_Image_Gibbs_Benchmark_KaTeX.md`
- `complex_signal_image_benchmark.py`
- `generate_tables.py`

## Reproduce everything

Linux or macOS:

```bash
bash run_all.sh
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
& .\Run_All.ps1
```

The runner generates all figures, tables, and results, then compiles the PDF.

## Python dependencies

- NumPy
- SciPy
- Matplotlib
- SymPy
- pandas
- scikit-image
- Pillow

## Benchmark layers

1. Complex one-dimensional finite-rate and stress cases
2. Noise, collision, and model-order sweeps
3. Exact finite geometric dictionaries in two dimensions
4. Out-of-dictionary stars, text, and rings
5. Exploratory natural images

## Claim boundary

The exact recovery statements apply only under the declared finite-rate or finite-dictionary hypotheses. Natural images and out-of-dictionary geometry are exploratory tests. They are included to expose the limits of the current packet model.
