# Build and evidence contract

Runtime: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Each Lean process uses -j1 -DwarningAsError=true and a 40-second cap. Increase an
outer tool timeout above the process cap so the verifier can save a timeout receipt.
Use the declared module order. Do not import a historical monolith that defines the
same names as the retained normalized modules.

Active proofs are the .lean files under Komorebi only. Deliberately invalid
negative controls and failed attempted sources are outside that directory. Zero
forbidden tokens and complete axiom auditing refer to active sources, not those
explicitly invalid regression inputs.

A successful check requires final source and direct project dependency hashes to
match their successful receipts and live compiled outputs. The mathlib cache is
reused. No full mathematical-universe rebuild is claimed. The independent exact
rational script checks its declared sixteen cases only.

The seal records a local snapshot Git commit, not a published GitHub release. If
rebuilding from the distributable without .git, initialize a local repository and
commit the sources before running the seal, or supply the preserved SOURCE_COMMIT
fallback. No remote repository or network access is required.

The generic official Mathbox manifest validator was unavailable. The included
project auditor and SHA-256 archive manifest are the checks actually performed.

The integrity auditor is read-only by default. The --seal flag intentionally writes
a new receipt, after which the output and archive manifests must be regenerated.
