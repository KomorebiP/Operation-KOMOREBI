# Reproducibility contract

## Software and arithmetic

The mathematical suites use the Python standard library, integers, `fractions.Fraction`, and, in one inherited information identity, rational coefficients of prime logarithms. Figure coordinates alone use floating point. The release was built with the versions recorded under `validation/environment.txt` and `validation/final/computation_manifest.json`.

The PDF build requires LaTeX and `latexmk`. Pandoc is needed only for the optional reading Markdown export. Matplotlib is needed only to regenerate figures. PyMuPDF was used for release text, geometry and render checks, not by the reference mathematical programs. No external model, GPU, network service, or private dataset is needed for the mathematical examples.

## Main commands

```bash
bash build.sh
python code/make_markdown.py
python code/verify_release.py
```

`build.sh` uses the supplied vector figures and records fresh results under `build/validation_rerun/`. Regenerating the reading export or PDF can change file hashes even when mathematical text is identical. The original release checksum file describes the originally distributed bytes. Compare a fresh build's mathematical text and receipts separately instead of interpreting every regenerated timestamp as a mathematical change.

## Three finite suites

| Suite | Groups | Assertions |
|---|---:|---:|
| `finite_checks.py` | 15 | 132,536 |
| `expanded_checks.py` | 13 | 39,945 |
| `edition_checks.py` | 10 | 80,188 |
| Total | 38 | 252,669 |

Detailed domains are recorded per group. Checks cover only those domains. Graph optimization is compared with direct encoders; acquisition optimization with complete history policies; the new resource optimization with independently generated bounded trees and explicit path simulation. All implementations are authored within this project. They are algorithmic cross-checks, not independent external research replications.

## Witnesses and costs

The new policy checker does not invoke the optimizer. It checks exact possible branches and uniform admissibility, rejects an invalid recipient message, simulates every allowed initial state, and separately counts all stored controller nodes. The cost vector retains its named units. Installed software and supplied model tables are not claimed to be learned. Code bytes are recorded, not minimized.

The six-record instrument witness is for one old-record fibre. The generic arithmetic demonstration works across all 25 old-record fibres. It is not counted as 25 identical controllers, and it is not certified as the shortest possible program.

## Provenance limits

The execution record retains the project's legacy schema v1 with additional before/after input hashes. The verifier is project-authored and executed. It is not an independently authenticated plugin distribution. Each child command has a 30-second wall timeout. No separate memory, affinity, or CPU-time cap was imposed. No Git revision or external execution attestation is claimed.

The source and all 17 predecessor statement/proof pairs were compared directly. A clean source copy was rebuilt and its pagewise extracted PDF text compared with the release. Binary PDF identity, Windows execution, cross-platform equivalence, PDF/A and tagged accessibility are not certified. Some inherited figures use embedded Type 3 font subsets; all used fonts are embedded and there are no distributed standalone font files.
