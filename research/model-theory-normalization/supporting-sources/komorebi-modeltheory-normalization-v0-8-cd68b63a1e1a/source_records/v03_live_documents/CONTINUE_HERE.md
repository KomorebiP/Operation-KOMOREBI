# Continue from Model-Theory Normalization v0.3

Treat this release and its manifest as the authoritative M3 checkpoint. The two
original parents are unchanged under history/. Read NORMALIZED_CORE.md,
FORMALIZATION_COVERAGE.md, RESULTS.md, DEVELOPMENT_FAILURES.md, and PROOF_AUDIT.md
before editing. Verify FILE_MANIFEST.json before replaying tests.

## Closed target

A valid finite matrix certificate gives a finite complete observation test code,
an actual standard first-order quantifier-free definition of its encoding kernel,
a term-definable code tuple, source/image preservation for every translated
observational formula, class formulas, and distinguishing formulas. All 202 saved
synthetic matrix cases have compiled applications. No source state space is
enumerated by the exporter or the symbolic Lean proof.

## Preservation requirements

* Preserve the original observation language and state/value distinction.
* Do not treat the full free target as the quantified target when P is not onto it.
* Class-query requests must designate actual image elements.
* Test-list length, matrix dimension and shortest formula are different costs.
* Parameter-free definability is relative to the declared value-naming language.
* Keep all-source-state semantics distinct from one-seed reachability.
* Preserve negative controls and scope warnings.
* Kernel-check generated source; never equate export with acceptance.

## Next focused obligation

Formalize the discovery loop itself: define the finite row-module growth state,
prove every accepted row is an actual observation-word combination, connect a
finite-chain-ring module-length ranking to termination, and prove a returned
closed span supplies the matrix certificate inputs. The Python implementation is
still an untrusted producer whose accepted output is checked afterward.

A separate later direction is a genuinely relational language where quantifier
depth adds information; do not claim this observational fragment already supplies
full first-order elementarity or theory-wide elimination of imaginaries.

## Reproduction

See README.md. The exact dependency pins and cold-audit commands are included.
The multi-gigabyte runtime and upstream compiled cache are not bundled.
