# v1.0.0rc2 — portability and final release gates

- Reproduced and fixed a non-UTF-8 default-encoding failure in Lean source export.
- Made 131 existing text-I/O and subprocess encoding choices explicit across 24 files.
- Added the offline isolated-wheel acceptance runner and installed-package probe.
- Added twelve regression tests; retained the original public API and certificate schemas.
- Hardened the free-repair workflow with exact Lean/Mathlib pins and unchanged-certificate-source checks. Wrong-pin controls are rejected before compilation.
- Kept all 51 Lean modules and all 526 declaration statements unchanged.
- Narrowed tested support to the configuration actually exercised. Additional interpreter downloads failed DNS; native Windows/WSL remain untested.
- Left licensing unselected, with the final public tag awaiting the author's decision.

# Changelog

## 1.0.0rc1

Feature freeze of the standalone rational repair, finite-menu and branch-certificate specifications. All v0.5.0 Lean proof source bytes retained.

Added an installable standard-library-only Python wheel, public `komorebi_repair` API, `komorebi-repair` entry point, explicit non-kernel outcome contract, and offline quickstart. Existing wire schemas retained.

Corrected three low-level exact-matrix boundary problems: a conflicting explicit width could be ignored, boolean indices could be accepted as integers, and direct construction could admit mutable nested storage. These were API-integrity problems, not counterexamples to the Lean repair theorems. Probes and new tests are preserved.

Replaced stat-before-read size checking with an actual bounded read. Added explicit JSON nesting and integer-token limits and controlled malformed-data errors. Added certificate serialization-size checks. The first deep-nesting test showed that relying on the interpreter's recursion limit was insufficient; the final scanner has its own depth bound.

Added 56 API/parser/CLI tests, rechecked all 72 existing exported inputs/certificates through the public facade, and ran 128 fresh coordinate-invariance pairs with independent exact rank comparisons. Added release scope, trust model, publication-license boundary and platform gates.

No new general mathematics, new Lean theorem count, full parser formalization, existing-library integration, or unrestricted arithmetic result is claimed in this release-hardening pass.
