# Proof Path Theory — monograph edition 1.3.0

**Komorebi P. · Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

The monograph is `docs/Proof_Path_Theory.pdf`. Its editable LaTeX source and all
14 figures are included. The body is organized into five parts: proof fields and
certificates, coherent realization, compression and memory, revision and inquiry,
and worked examples and implementation. A preface, reading guide, notation and
hypothesis appendix, theorem ledger, and reproduction guide complete the volume.

This edition proofreads and reorganizes the entire v1.2.0 manuscript. It also
corrects the admitted-leaf boundary in AND-DAG detection and replaces tolerant
floating-point comparisons in exact certificate selection by rational comparison
of the stored binary-float costs. The public cost display remains a float.

## Evidence to read first

- `PROOFREADING_REPORT.md`: substantive corrections and the scope of the review.
- `data/editorial_verification.json`: checks run for this edition.
- `editorial/logs/`: current tests, builds, finite checks, and regression diagnoses.
- `editorial/formal_baseline_v1.2.0.json`: hashes linking unchanged formal sources
  and their inherited evidence to the supplied v1.2.0 release.
- `docs/LEAN_GUIDE.md`: formal interfaces and trust boundaries.
- `data/claim_ledger.csv`: 33 stable result groups with explicit scope.
- `PROGRESS_LEDGER_v1.3.0.md`: completed work and remaining obligations.

**No fresh Lean compilation is claimed by the monograph review.** The eight
production modules and earlier kernel/axiom records are retained unchanged.
The current Python and publication checks are separate from that inherited
formal evidence. The whole manuscript is not Lean-formalized.

## Reproduce the finite and publication checks

Python 3.10 or later is required, with NumPy and pytest installed. Regenerating
figures also requires matplotlib and networkx. The PDF uses pdfLaTeX, NewTX,
Source Sans Pro, TikZ, and the other packages named in the source preamble.
Install dependencies before working offline. No model API is required.

```bash
python -m pip install -e . --no-build-isolation
python -m pytest
python scripts/deep_validation.py
python scripts/verify_bridge.py
python scripts/verify_editorial.py
```

From `docs/`, run pdfLaTeX three times to resolve the contents and references:

```bash
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
```

`verify_editorial.py` checks the source, result identifiers, finite sample record,
and formal-source identity. Its output does not substitute for the pytest,
exhaustive-computation, PDF build, or Lean commands. The dated report records
which of those commands were actually executed for this edition.

## Separate formal verification

With the separately supplied pinned runtime:

```bash
python scripts/verify_lean.py --runtime /path/to/portable-kit
python scripts/verify_release.py --runtime /path/to/portable-kit
```

These commands perform fresh checks and overwrite their active evidence records.
Copy the delivered package first to preserve its historical evidence. A newly
executed Lean run has different log hashes and must not be mistaken for the
unchanged inherited record expected by `verify_editorial.py`.

The compiler, cached dependencies, and their pins remain part of the formal trust
boundary. The earlier runtime was Linux x86-64. WSL is the intended Windows
route for that runtime; this review does not assert a native Windows Lean run.

## Small executable example

```python
from proof_path_theory import load_proof_field, ProofFieldViews

field = load_proof_field("examples/minimal_monograph.json")
views = ProofFieldViews(field)
assert field.targets <= views.least_model()
```

This checks closure in the declared inference model. The example's rule is an
explicit model assumption, not proof of an arbitrary mathematical implication.
The general semantic-soundness interface separately requires true leaves and
truth-preserving rules.

Package building is available through `python scripts/build_release.py`. The
wheel contains the Python library and its schemas. The full monograph ZIP also
contains the manuscript, figures, Lean source, tests, provenance, and evidence.

## License and boundaries

The author's redistribution license remains unselected. `LICENSE_NOTICE.md`
retains that decision rather than silently applying a license. The work is not
represented as independently peer-reviewed, as an empirical validation of social
models, or as a formal correctness proof of every program. Written mathematics,
finite tests, compiler evidence, and prospective applications are kept distinct.
