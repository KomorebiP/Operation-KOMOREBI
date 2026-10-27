# Singularity-Exact Reconstruction

## One closed executable construction

`gibbs_projector_closed.py` is the complete source object. Running it regenerates the numerical certificates, 39 vector/raster figure pairs, tables, KaTeX manuscript, LaTeX manuscript, PDF, audit, and manifest.

```powershell
python .\gibbs_projector_closed.py
```

Linux/macOS:

```bash
./run_all.sh
```

Python dependencies are listed in `requirements.txt`; `pdflatex` is required for the final PDF build.

## Exact model

The single worked signal is

\[
f(t)=\frac13\cos(2\pi t)+\frac14\sin(6\pi t)-\frac15\cos(10\pi t)
+\frac54\mathbf 1_{[1/4,3/4)}(t).
\]

The global Fourier partial sums retain the classical Gibbs boundary layer. The projector-resolved reconstruction instead identifies and retains the singularity packet exactly, projects the complement into the degree-five smooth packet, and synthesizes

\[
Q_5P_Sf+P_Jf=f.
\]

The sampled exact-reconstruction residual is `6.661338e-16`.

## Scope

The result is exact for the declared smooth-plus-one-interval model and for the correctly selected member of the declared finite dyadic interval dictionary. It does not assert automatic recovery of arbitrary unknown singularities or universal elimination of every Gibbs-like phenomenon.
