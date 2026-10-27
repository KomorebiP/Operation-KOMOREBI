# Proof Path Theory — monograph edition 1.8.0

**Komorebi P. · Operation Komorebi**

Certificates, compression, discovery fields, and mathematical memory.

## The publication

The **76-page** monograph is `docs/Proof_Path_Theory.pdf`, with editable LaTeX
in the adjacent `.tex` file. It retains the five-part monograph design and adds
one mathematical illustration: **25 numbered vector figures**, one cover motif,
and **six worked visual studies**. The eight-page sampler is extracted from this
edition, not copied from a predecessor.

The 41 prior result groups and all 149 prior mathematical environments remain.
Six new groups and fourteen new statement/proof environments establish a precise
checker and exchange contract. Publication **1.8.0** and Python distribution
**1.6.0** have distinct versions. The original named-field schemas and provenance
encoding are unchanged; the new positional trace format has its own version tag.

## What is newly proved

An executable Lean replay checker refines the existing `Field` and seeded
closure, not a new semantics defined to agree with program output. Accepted
complete traces certify the **least** seeded model. Both derivability and a
final saturation check are necessary. A forbidden-node witness is a causal trace,
and one exists exactly when the fixed protected problem is infeasible.

The typed problem and certificate codecs have proved left inverses and hence
are injective at Lean's `Json` syntax-tree boundary. Acceptance of decoded
records gives the same protected closure/feasibility theorem. Unknown addresses,
boolean-as-integer inputs, invented nodes, incomplete closures, and changed
observations have explicit negative tests.

## Reproducible exchange

```bash
python scripts/check_manifest.py
python -m pip install -e ".[release]" --no-build-isolation
proof-path wire-export examples/and_dag.json --negative B --output-prefix trial
proof-path wire-check trial.problem.json trial.certificate.json
```

The request, proposed result, and source address book are separate files.
An accepted negative result is an obstruction for that request. A rejected
certificate is not an infeasibility verdict. See `docs/TRACE_EXCHANGE.md` for
syntax, resource limits, trust boundaries, and the Lean consumer.

## Current evidence

- **18** production Lean modules freshly built and replayed by Lean's own kernel.
- **283** explicit named-declaration axiom audits, including **169** named theorems.
- **233** source-package tests and the same suite against an installed wheel.
- **83,994** serialized cases matched by the independent model oracle, Python
  checker, and actual Lean JSON consumer, with zero verdict mismatches.
- Existing exhaustive protected, semantic-cover, linear, recovery, retention,
  and covariance checks are rerun separately and retain their declared domains.

The mathematical theorem counts, result groups, concrete examples, and test
counts are different inventories. None is a count of novel discoveries.

Current records:

```text
evidence/formal_1.8.0/verification.json
data/release_verification.json
data/publication_verification_1.8.0.json
data/trace_exchange_1.8.0.json
data/recovery_extension_checks_1.8.0.json
formal/CONCORDANCE.json
PROGRESS_LEDGER_v1.8.0.md
```

The 13 preceding production Lean modules are unchanged. Five new modules are
`Trace`, `TraceCompleteness`, `TraceWire`, `TraceExamples`, and `TraceFixtures`.
The IO adapter `CheckTraceJson.lean` is executed but not counted as a proved IO
implementation. The pinned compiler and nine dependency revisions are checked;
Mathlib's cached imports are not freshly rebuilt as a whole.

## Rebuild and verify

Use a fresh working copy. Rebuilding changes evidence hashes; check the supplied
manifest before running rebuild commands, not after.

```bash
python -m pytest -o addopts='' -q
python scripts/deep_validation.py
python scripts/verify_bridge.py
python scripts/check_recovery_extension.py
python scripts/check_trace_exchange.py
python scripts/design_figures.py
python scripts/verify_lean.py --runtime /path/to/portable-kit
python scripts/verify_release.py --runtime /path/to/portable-kit
```

The full release verifier obtains a new formal run, rebuilds the manuscript,
builds a wheel and source distribution, tests the installed wheel separately,
and checks publication/source correspondence. The publication-only verifier
checks recorded evidence and source identity; it does not invoke Lean.

Figures need an installed Lato font. Font files and the large offline Lean kit
are not distributed in this package. pdfLaTeX, NewTX, Source Sans Pro, TikZ,
and the other declared preamble packages are needed for the manuscript.
Installation may access a package index unless dependencies are supplied locally.
The finite computation and verification commands use no model API.

## Boundaries and rights

The JSON AST codec and the Lean Boolean checker are proved. The text parser,
printer, IO, Python producer/checker, and source-to-index adapter are not thereby
universally verified. Concrete cross-language agreement is tested evidence.
The original named proof fields remain acyclic; cyclic checker fixtures use the
separate lower-level indexed domain. Semantic interpretation still requires
sound leaves/rules and true positive observations. Social models remain
conditional and are not empirically established by these tests.

The existing license notice is unchanged. No license was chosen on the author's
behalf. Hosted CI, native Windows execution, and all supported Python versions
were not run here. Current Linux/Python and pinned Lean runs are recorded.
