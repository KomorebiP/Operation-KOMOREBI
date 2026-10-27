# Projector-Resolved Seed Calculus from Seed to Reconstruction

## Complete seed-to-finish edition with seven worked realizations

**Author:** Komorebi P.

This release develops the finite calculus from its primitive datum to its final reconstruction certificate before presenting the seven retained domain examples. No theorem, worked example, formula, figure, table, code listing, or negative control from the previous detailed edition has been removed.

The dependency chain is

```text
primitive seed
-> typed operator grammar
-> generated hull and seed rank
-> relations and quotient normal forms
-> addresses
-> complete packet projectors
-> analysis and synthesis
-> transfer blocks and path calculus
-> refinement and coarsening
-> transform atlases and redundant exact frames
-> nonlinear interaction packets
-> obstruction packets
-> dense-core completion
-> final reconstruction and residual certificate.
```

A single master example in `C^8` is carried through every stage. The same formal architecture is then proved independently in seven areas:

1. finite linear algebra and operator transfer blocks;
2. signals, polyphase coordinates, Haar wavelets, and Fourier packets;
3. quantum information and parity-resolved circuit paths;
4. conditional expectation and Bayesian coarsening;
5. analytic root filters, closed forms, and an exact integer-sequence candidate;
6. a coupled-oscillator physics problem;
7. nonlinear signal packets and finite holonomy.

## Main theorem schema

A finite seed system consists of a typed primitive datum, a fixed admissible operator grammar, its generated hull, a complete packet family, and compatible analysis and synthesis maps. For a complete family of pairwise-annihilating projectors,

```text
P_alpha P_beta = delta_{alpha,beta} P_alpha,
sum_alpha P_alpha = I,
```

one obtains

```text
x = sum_alpha P_alpha x,
T = sum_{alpha,beta} P_beta T P_alpha.
```

Compatible descendants reconstruct their parent packets exactly. Invertible coordinate transforms pull ordinary coordinate selectors back to complete projector atlases. Multilinear maps resolve into interaction tensors, and a failed correction is localized by an obstruction projector. The document proves these statements in finite dimension and records the hypotheses needed for completion beyond the finite setting.

## Master seed example

The foundational implementation uses

```text
X = C^8,
s = e_0,
U e_j = e_{j+1 mod 8},
U^8 = I.
```

The orbit matrix `[s, Us, ..., U^7s]` has rank eight, so one seed generates the whole space. The example then develops:

- coordinate, parity, residue-modulo-four, and Fourier packets;
- the operator `T = 2I - U + 3U^2` and all transfer blocks;
- packet-path multiplication for operator products;
- exact Fourier diagonalization;
- an exact weighted spatial/Fourier/Haar multi-atlas frame;
- the nonlinear map `N(x) = x + (Ux) .* (U^3x)` and all bilinear interaction packets;
- solvable and blocked correction data for an explicit obstruction projector.

Every stage is followed by a symbolic synthesis or residual certificate.

## Document inventory

- `Seven_Area_Worked_Proof_Atlas.pdf` - final 140-page paper.
- `Seven_Area_Worked_Proof_Atlas.tex` - modular LaTeX source.
- `seed_to_core.tex` - primitive seed, grammar, hull, relations, and addresses.
- `core_to_areas.tex` - transfer calculus, refinement, atlases, nonlinearity, obstruction, completion, and the master theorem.
- `Seven_Area_Worked_Proof_Atlas_Detailed_KaTeX.md` - KaTeX-friendly derivation retaining all seven worked areas.
- `Projector_Resolved_Seed_Calculus_Seed_to_Reconstruction_Contact_Sheet.png` - complete 140-page layout audit.
- `proof_atlas/foundations.py` - exact symbolic master construction.
- `proof_atlas/foundation_figures.py` - the 23 foundational figures.
- `proof_atlas/` - the seven retained domain implementations and detailed certificates.
- `tests/` - 32 exact tests.
- `figures/` - 61 vector-PDF and 61 matching PNG figures.
- `tables/` - machine-readable exact tables and the candidate sequence b-file.
- `results/results.json` - exact certificate ledger.
- `results/pdf_preflight_seed_to_finish.json` - final PDF preflight.
- `results/layout_audit.json` - render and layout audit.

## Reproduction

Linux or macOS:

```bash
./run_all.sh
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\Run_All.ps1
```

The default runner regenerates the foundational certificate, the 23 new figures, the figure inventory, and the result ledger. The full mode also regenerates all retained domain figures and tables:

```bash
python run_all.py --full
```

Manual verification:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python -m pytest -q
latexmk -pdf -interaction=nonstopmode -halt-on-error Seven_Area_Worked_Proof_Atlas.tex
```

## Verification architecture

The final suite contains **32 exact tests**:

- 11 seed-to-reconstruction foundation tests;
- 7 primary domain certificate tests;
- 7 independent domain re-derivations;
- 7 detailed intermediate-step audits.

The figure inventory contains **61 pairs**:

- 23 new foundational figures;
- 38 retained detailed domain figures.

The final PDF contains **140 US-Letter pages**. All pages were rendered at 180 DPI and inspected through seven contact sheets and representative full-resolution pages. PDF preflight returned no warnings. All fonts are embedded. The LaTeX log contains no overfull boxes, underfull boxes, or undefined references.

## Exact status

The paper proves a finite seed-to-reconstruction calculus and supplies seven complete realizations under declared hypotheses. It demonstrates that the framework is internally consistent, non-vacuous, and operational across algebraic, signal, quantum, probabilistic, arithmetic, physical, and nonlinear settings. It does not infer every infinite-dimensional, categorical, statistical, or physical extension from the finite results. The candidate integer sequence is accompanied by exact closed forms, recurrences, composition identities, integer certificates, and an OEIS-ready record without an unconditional historical-priority claim.
