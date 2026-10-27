# Projector-Resolved Seed Calculus IX

## Arithmetic Packet Calculus: Euler Families, Supercongruences, and Weighted p-adic Reconstruction

**Author:** Komorebi P.

The release contains the final paper, complete LaTeX source, exact arithmetic code, automated tests, Python-generated figures, formula registries, and machine-readable numerical certificates. The uniform odd-prime sector and weighted dyadic sector are developed separately and are recombined only through explicit packet and CRT laws.

## PowerShell

After extracting the release:

```powershell
$Work = Join-Path $HOME "Downloads\Projector_Seed_Calculus_IX_Release"
Set-Location $Work
Set-ExecutionPolicy -Scope Process Bypass -Force
& ".\Run_All.ps1" -Work $Work
```

The runner leaves installed packages unchanged. It installs only missing packages unless `-Update` is supplied.

## Direct Python calls

```powershell
python -m pytest -q
python .\scripts\generate_all.py
python -m pip wheel . --no-deps --no-build-isolation -w .\dist
```

The finite computations certify the stated test ranges; they do not replace the uniform proofs or promote the explicitly labeled conjectures to theorems.
