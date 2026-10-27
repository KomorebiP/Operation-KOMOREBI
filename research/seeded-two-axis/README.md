# Komorebi Seeded Two-Axis Calculus — v0.11.0

Author: Komorebi P.  
Working formalization, 27 September 2026.

## Current mathematical result

This release extends the cumulative manuscript to continuous representations of an actual profinite source. Its principal result is a complete finite-matrix criterion for unconstrained continuous representations

    rho_n : Z_p^r -> GL_2(Z/p^n).

Let a be the minimum scalar depth of the generator matrices. All-scalar inputs lift. Otherwise subtract their scalar parts, divide by p^a into matrices modulo p^(n-a), and select a normalized generator that is nonscalar modulo p. The representation lifts over Z_p exactly when every normalized generator commutes with that selected one. A cyclic vector gives explicit linear polynomials producing exactly commuting integral lifts.

A uniform extension horizon is 2n-1, sharp for n >= 2 and r >= 2. In arbitrary matrix rank, the same argument applies when a normalized generator is cyclic modulo p. Separate results cover continuous H^2 obstructions, source inflation, reconstruction from towers, and free pro-p sources. Coefficient reduction and source inflation have opposite variance.

These are written proofs and authoring-session self-review. They are not Lean-certified or independently reviewed. No claim of historical novelty, general Galois lifting, geometric local conditions, or automorphic existence is made.

## Files

- `Komorebi_Seeded_Two_Axis_Calculus_v0.11.0.pdf`: cumulative manuscript, 106 pages.
- `Komorebi_Seeded_Two_Axis_Calculus_v0.11.0.tex`: standalone LaTeX source.
- `proofs/profinite_lifting.tex`: new K72–K82 proof block.
- `tools/lift_abelian_rank2.py`: exact positive/negative certificate command.
- `examples/`: positive and negative JSON inputs and their certificates.
- `checks/`: all six exact regression suites, runner, and actual reports.
- `audit/`: source diff, integration script, proof/self-review records, final compile log, source and provenance checks.
- `research/records/`: durable research records, indexed by `RESEARCH_LOG.md`.
- `previous/`: exact supplied v0.10.0 source, PDF, and full package. Earlier history is retained inside that package.
- `SHA256SUMS.json`: checksums of every other file in this release.

## Use the rank-two certificate tool

Python 3.10 or newer is sufficient for the new standard-library tool and its dedicated suite. The full inherited suite was run with Python 3.13.5 and SymPy 1.14.0.

From the extracted release directory:

```bash
python tools/lift_abelian_rank2.py examples/positive_rank2.json
python tools/lift_abelian_rank2.py examples/negative_rank2.json
```

A custom input has this form:

```json
{
  "p": 3,
  "n": 3,
  "generators": [
    [[1, 3], [9, 1]],
    [[7, 12], [9, 7]]
  ]
}
```

The command checks that the prime and precision are valid, that the matrices commute at that precision, and that their residual orders are p-powers. `LIFTABLE` returns exact integral matrix entries (units in Z_p, not necessarily in GL_2(Z)). `NOT_LIFTABLE` returns a nonzero normalized commutator. Malformed input exits with code 2. Both positive and negative mathematical certificates are successful command outcomes with exit code 0.

Only the stated unconstrained GL_2 problem is certified. A supplied determinant, Galois condition, Hodge condition, ramification restriction, or finite-image requirement is not checked or preserved automatically.

## Reproduce

Install the dependencies listed in `requirements.txt` in a suitable Python environment. With a standard LaTeX installation providing the packages in the source:

```bash
python checks/run_all.py
python audit/integrate_v0110.py
latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.11.0.tex
```

Copy the last TeX engine log to `audit/latex_final.log` before running `python audit/check_source.py` to audit a fresh build. The distributed source check refers to the supplied final log and run reports. It verifies preservation, references, hashes, and reproducible source generation, not mathematical truth.

The full runner gives each script a 40-second timeout, sets single-thread numerical-library environment variables, removes a previous report before running its script, and records before/after script hashes. It imposes no memory cap. The standalone new suite is:

```bash
python checks/check_profinite_lifting.py --output checks/profinite_results.json
```

Re-running a test updates evidence timestamps and therefore changes checksums. The release checksum inventory describes the delivered files, not later regenerated outputs.

## Boundaries and next target

A continuous obstruction can be nonzero at one finite quotient and vanish after inflation to a finer quotient. A genuine relation of the fixed source still has to hold. Free pro-p and abelian pro-p sources therefore have different lifting behavior. The main abelian theorem retains exact commutativity without erasing coefficient information.

Remaining targets are specified noncommutative profinite presentations, noncyclic higher-rank centralizers, and additional arithmetic deformation conditions. The manuscript does not turn a finite-precision witness into an automorphic representation.
