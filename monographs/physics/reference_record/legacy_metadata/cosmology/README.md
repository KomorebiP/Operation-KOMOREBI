# Projector-Refinement Physics, Volume II

## Cosmology, Dark Sectors, Structure Formation, and Falsifiability

**Author:** Komorebi P.  
**Version:** 1.0.0  
**Edition:** First Research Monograph Edition  
**Release date:** 2026-08-19  
**Length:** 157 pages

This volume develops the cosmological and phenomenological half of the projector-refinement program. It begins with relativistic FLRW backgrounds and perturbations, introduces the scale-covariant refinement dark sector, evolves its collisionless distribution through CMB and lensing transport, follows the same frozen parameter set into nonlinear structure and baryonic response, and ends with linked rejection criteria and an explicit open-problem ledger.

## Structure

1. Relativistic Cosmological Backgrounds and Perturbations
2. The Scale-Covariant Refinement Dark Sector
3. Kinetic Cosmology, the CMB, and Lensing
4. Nonlinear Structure, Baryons, and Subhalo Survival
5. Falsifiability and Open Problems

The book contains 21 numbered chapters and three reference appendices.

## Build

Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\Build_Volume_II.ps1
```

Linux or WSL:

```bash
./Build_Volume_II.sh
```

A TeX distribution with `latexmk` is required. Figures and visualizations are generated from the archived Python workflows and included in the source package.

## Result status

The manuscript distinguishes:

- exact theorems
- conditional theorems and model consequences
- controlled numerical computations
- model propositions
- open problems

The scale-covariant interaction is a proposed model extension. The book does not claim a completed microscopic parameter derivation, a precision cosmological likelihood, historical priority, independent reproduction, or empirical confirmation.

## Reproducibility map

- `chapters/` - numbered monograph chapters
- `frontmatter/` and `part_intros/` - publication apparatus
- `appendices/` - formula, benchmark, and reproducibility guides
- `figures/` - publication figures
- `data/` - frozen numerical records
- `verification/` and `code/` - archived computational programs
- `source/` - generated TeX values and shared source fragments
- `audit/` - build, PDF-preflight, and render-comparison records

See `RIGHTS.md` before redistribution.
