# Komorebi Seeded Two-Axis Calculus v0.9.0

**86-page cumulative working manuscript. Written proofs and self-review, not Lean certification or independent mathematical review.**

## This release

K53–K61 add natural arithmetic exchange comparisons, a sharp precision bound for lifting fixed linear constraints, cohomological obstructions to lifting invariant vectors and equivariant maps, and a canonical derived comparison with a nonzero defect. The non-scalar cyclic representation over Z/p² also has a one-step obstruction to lifting to Z/p³. A positive theorem proves exact comparison on inputs with a supplied coefficient lift.

Classical group cohomology and derived tensor machinery are attributed in the manuscript. No historical novelty, unrestricted representation-lifting theorem, new foundational axiom, automorphic existence, or Langlands reciprocity is claimed.

## Contents

- `Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.pdf`: cumulative manuscript, 86 pages.
- Matching `.tex`: standalone source, with references included.
- `proofs/`: new theorem/proof and audit fragments used in integration.
- `checks/`: four finite regression suites, exact JSON results, and a bounded runner.
- `audit/`: source diff, provenance, source checks, build log, static checks, contact sheets, and self-review.
- `previous/`: unchanged v0.8.0 PDF, TeX, and full ZIP. Its archive preserves the earlier release history.
- `research/records/`: compact research records, linked by `RESEARCH_LOG.md`.
- `STATUS.md`: exact present scope and remaining mathematical obligations.
- `SHA256SUMS`: integrity inventory. It does not certify mathematical correctness.

## Build

A LaTeX installation with the packages listed in the preamble and `latexmk` is required. The manuscript uses standard installed fonts; font files are not distributed.

```bash
latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.tex
```

The output is written under `build/`. The supplied PDF is copied from a successful build. A clean build should resolve references after latexmk's normal multiple passes. The preserved final log is `audit/latex_final.log`.

To regenerate the standalone source from the unchanged base and proof fragments:

```bash
python audit/integrate_v090.py
```

**That command overwrites the root v0.9.0 TeX and source diff.** Edit the integration script/fragments, or save manual source edits separately before rerunning. This reconstruction does not alter the preserved v0.8.0 source. Source reconstruction was checked for idempotence.

## Exact finite tests

The recorded environment is Python 3.13.5 with SymPy 1.14.0. The tests do not use the network. SymPy is the only nonstandard mathematical dependency; a pinned `requirements.txt` is included.

```bash
python checks/run_all.py
```

This executes the four suites, enforcing a 40-second wall-clock timeout per process and setting numerical-library thread environment limits. It overwrites result JSON and run logs. No hard memory limit is imposed. The runner reports exit codes, source hashes before/after, timestamps, duration, and output hashes in `checks/all_runs.json`.

Individual commands:

```bash
python checks/check_models.py --max-length 10 --output checks/base_regression_results.json
python checks/check_interactions.py --output checks/interaction_results.json
python checks/check_resolution_towers.py --output checks/resolution_results.json
python checks/check_intrinsic_exchange.py --output checks/intrinsic_results.json
python audit/check_source.py
```

The final static check uses the supplied LaTeX log. Copy a newly built log to `audit/latex_final.log` before using it to audit a rebuilt PDF. Rerunning any command changes output provenance and therefore invalidates the release checksum inventory until it is regenerated.

## Proof boundary

The finite assertions are not universal proofs. In particular, no truncated computation is used to infer cohomology in all integer degrees. The infinite-degree counterexample has a separate cyclic-resolution/Tor proof. Its ambient category is unbounded D(k), not Perf(k). The positive coefficient-lift theorem supplies a necessary obstruction, not a converse lifting criterion.

Independent proof review and Lean formalization remain outstanding.
