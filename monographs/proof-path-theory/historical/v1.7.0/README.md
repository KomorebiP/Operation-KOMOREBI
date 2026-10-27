# Proof Path Theory — monograph edition 1.7.0

**Komorebi P. · Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

## The publication

`docs/Proof_Path_Theory.pdf` is the **69-page monograph**. Its editable source is
`docs/Proof_Path_Theory.tex`. Five illustrated parts, **24 vector figures**, and
five visual studies connect the formal definitions with inspectable finite
examples. `docs/Proof_Path_Theory_Visual_Sampler.pdf` contains eight pages from
this same book. No mathematical argument is replaced by a picture.

This edition adds eight result groups to the 33 earlier groups. The new results
connect protected rule models, exact gluing criteria, typed rule transports,
attained-image decoding, joint task representations, and hash data processing.
The new interfaces are in five freshly checked Lean modules and three finite
Python modules. The 131 earlier mathematical statement and proof environments
are preserved, with 18 new environments added.

## What is stronger

- A protected rule-model problem returns its least model or a derivation of an
  explicitly forbidden node. The result checker is separate from the producer.
- Whole-support coverage can be replaced by an exact semantic criterion: rules
  visible in the patches must entail every original rule. A negative answer
  supplies matching local models that have no global extension.
- A task factors through an encoding exactly when equal encodings give equal
  answers. The formal decoder is now defined on attained outputs, matching the
  manuscript, including empty-domain cases. Joint tasks give the least required
  distinctions, not necessarily the smallest file or fastest program.
- Typed rule transports preserve derivations and pull models back. A checked
  collapse example shows why a transport must not be called an equivalence.

## Versions and evidence

Publication **1.7.0** and Python distribution **1.5.0** have distinct version
numbers. The provenance encoding introduced in Python 1.4.0 is unchanged.
Historical digest migration remains documented in `docs/PROVENANCE_FORMAT.md`.

Thirteen production modules were rebuilt in a fresh object directory, replayed
with Lean's own kernel, and axiom audited. The inventory contains **93 named
theorems and 149 named declarations**, including examples and helpers. This is
not a novelty count. The eight original mathematical modules are unchanged.
The five additions are Recovery, Extension, Transport, ExtensionExamples, and
SemanticCover. The pinned dependencies were cached, not rebuilt as a whole.

Current formal evidence: `evidence/formal_1.7.0/verification.json`.
Current integrated execution evidence: `data/release_verification.json`.
Source and publication audit: `data/publication_verification_1.7.0.json`.
Exact extended checks: `data/recovery_extension_checks_1.7.0.json`.
Scope and next restart point: `PROGRESS_LEDGER_v1.7.0.md`.

None of these records claims formal verification of the entire manuscript,
universal correctness of Python or the exporter, or empirical validity of the
social models. Initial failures and corrections are retained under
`evidence/development_1.7.0/`. A failed import or unavailable decision procedure
is not counted as rejection of a false theorem.

## Reproduce

Before modifying an extracted archive, check the delivered bytes:

```bash
python scripts/check_manifest.py
```

Install the declared dependencies, then execute the finite checks:

```bash
python -m pip install -e ".[release]" --no-build-isolation
python -m pytest -o addopts='' -q
python scripts/deep_validation.py
python scripts/verify_bridge.py
python scripts/check_recovery_extension.py
python scripts/verify_publication_edition.py
python examples/recovery_and_extension.py
```

The finite computations use no model API. Installation may need a package index
unless its dependencies have been made available locally. The supplied wheel
and source distribution are installation conveniences. The complete monograph
ZIP is the authoritative handoff for all current and historical evidence.

Figures require an installed Lato font. Font files are not distributed.
The manuscript needs pdfLaTeX, NewTX, Source Sans Pro, TikZ, upquote, and the
other packages named in its preamble.

```bash
python scripts/design_figures.py
cd docs
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
pdflatex -interaction=nonstopmode -halt-on-error Proof_Path_Theory.tex
```

With the separately supplied pinned runtime, run the complete technical check:

```bash
python scripts/verify_release.py --runtime /path/to/portable-kit
```

A formal-only run uses `scripts/verify_lean.py` with the same argument.
The publication verifier checks that the recorded successful run still matches
the current sources. It does not itself invoke Lean. Rebuilding or rerunning
these commands changes evidence hashes, so use a fresh working copy and keep
the delivered original. Check the manifest before, not after, rebuilding.

PowerShell extraction commands are in Appendix C; `scripts/run_all.ps1` runs the
finite checks after installation. The PowerShell script and hosted GitHub jobs
were not executed in this Linux session. Local Python and Lean commands were.

## Rights

The existing license notice is unchanged. No redistribution license has been
chosen on the author's behalf. Mathematical correctness, software behavior,
priority, independent review, and empirical validation remain separate tasks.
