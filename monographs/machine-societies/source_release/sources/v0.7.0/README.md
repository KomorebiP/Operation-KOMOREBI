# Machine Societies — v0.7.0
## A Theory of Persistent Plural Computational Organization
**Komorebi P. · 8 October 2026 · 90-page integrated theoretical edition**

Read `Machine_Societies_v0.7.0.pdf`. The editable source is `Machine_Societies_v0.7.0.tex`. The bibliography is embedded in the source. Figures are vector PDFs, with their regeneration scripts in `figures/`.

This revision asks whether separate institutional guarantees admit one executable policy. It develops a simultaneous enforcement criterion, robust margins, a finite continuation kernel under a common information boundary, ranked service certificates, and an exact strategy-preserving abstraction theorem. A shared-budget commons example makes the obstruction explicit. The manuscript remains theoretical and contains no account of the author's private agent experiments.

The edition contains 56 theorem/proposition statements with prose proofs, 6 definitions, 18 formal counterexamples, 14 figures, and 52 references. Classical foundations are acknowledged. These counts do not establish priority, empirical social formation, independent peer review, or formal-kernel verification.

## Verify before regenerating
```bash
python validation/verify_release.py
```
The as-delivered hash inventory covers the snapshot, not a modified working copy. Rerunning mathematical checks replaces runtime receipts and therefore changes their hashes. The verifier checks integrity and the stored finite record, not the prose proofs.

## Rebuild the manuscript
A normal TeX installation must provide `latexmk`, pdfLaTeX, and the packages declared in the source, including `newtxtext`, `newtxmath`, and `placeins`. No private font files or external figure downloads are needed.
```bash
bash build.sh
```
On Windows with TeX installed:
```powershell
.\build.ps1
```
Both target `build/Machine_Societies_v0.7.0.pdf`, leaving the root PDF unchanged. The Bash build was run. The PowerShell script was inspected but not executed on Windows. Figure regeneration additionally requires Matplotlib. The mathematical checks require Python 3.10 or later and only the standard library.

## Rerun the exact finite suite
```bash
python validation/check_finite_models.py
```
The delivered run passed 62 groups and 700,130 exact assertions, including all 52 predecessor groups. Bounds and actual runtimes are recorded by group. Enumeration does not replace the conditional general proofs. The two new solvers are small reference implementations, not scalable distributed-control or production audit systems.

## Run the integrated commons example
```bash
python code/demo_commons.py --capacity 4 --due 3
python code/demo_commons.py --capacity 5 --due 3
```
The first returns `INFEASIBLE`: the two-slot audit and three due services need five slots. The second returns a checked one-step service certificate with common monitor `(0,1,1)`, false-positive rate `1/4`, and simultaneous incentive margin `1/2`. These use stipulated channels, penalties, and costs. No law was estimated from agent behavior.

`code/finite_contract.py` uses integer state masks, fixed permitted protocol profiles, and a declared common observation. It does not supply missing communication, authorization, or private information. The progress guarantee is sure certified completion, not merely almost-sure physical completion. `code/exact_enforcement.py` solves small rational monitor problems by vertex enumeration and rejects more than 200,000 candidate intersections.

## Review material
`REVISION_NOTES.md` describes the changes. `PROOFREADING_REPORT.md` states actual review scope and failures. `THEOREM_INDEX.md` maps statements to the source and printed pages. `validation/` contains bounded test domains, the computation manifest, an executable commons witness, targeted reference review, source-preservation and PDF checks, and clean-rebuild evidence. `sources/` preserves earlier source and review snapshots. Earlier deliverables remain unchanged.

The record retains legacy computation-manifest version 1, with separately pinned input and output hashes. The bundled project verifier is not an independently authenticated distribution of the plugin's validator. No Git commit, independent attestation, resource-limit enforcement, Lean certificate, PDF/A certification, or tagged-accessibility certification is claimed.
