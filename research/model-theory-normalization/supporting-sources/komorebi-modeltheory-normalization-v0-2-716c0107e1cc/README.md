# Komorebi Model-Theory Normalization v0.2

A checked compiler from Komorebi's observational syntax to Mathlib's standard
first-order language, with guarded quantifiers, exact fragment transport and
quantifier-free definability from certified finite observation codes.

Read NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md, RESULTS.md, PROOF_AUDIT.md
and EXTERNAL_INPUTS.md. This is the model-theory branch, not Representation
Calculus v0.5 or a new p-adic arithmetic block.

The archive contains the frozen v0.1 ZIP and all current local proof sources,
reference code, tests, exact logs, input/output hashes and proof boundaries.
It excludes the multi-gigabyte Lean/Mathlib runtime and compiled local outputs.

## Reproduce

1. Check the distribution before rerunning any audit (audits rewrite evidence):

       python tools/verify_integrity.py

2. Run the independent finite reference:

       python tests/audit.py

3. With the pinned portable Lean/Mathlib runtime:

       python tools/audit_all.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
       python tools/validate_manifest.py LEAN_MANIFEST.json --root .
       python tools/validate_manifest.py COMPUTATION_MANIFEST.json --root .

The audit checks the actual Lean and Mathlib pins, uses an empty local build
folder, compiles every source with warnings-as-errors, audits all named axioms,
and requires the positive/negative controls to have their specified outcomes.
No download or network access occurs in these commands. Python 3.10+ is needed
for the match syntax; the exact tested version is recorded in the manifests.
