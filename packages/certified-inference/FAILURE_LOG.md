# Failures, corrections, and unsuccessful routes — v14 / Core 1.0.0

Four completed draft Lean failures were corrected:

1. CachedPacketState: `initialize` is reserved syntax. Renamed it `initialState`
   and removed unused section instances.
2. CachedPacketSearch: the zero-step trajectory had not reduced before rewriting
   its score. Explicitly changed the hypothesis to the current state's score.
3. CachedPacketSolver: a local let hid the branch from the splitting tactic.
   Reduced the let before splitting the actual program guards.
4. CachedRoundingBoundary: added the setup-check import and unfolded cache validity
   before invoking kernel decision. This resolved both scope and decidability.

Exact attempted-source snapshots, compiler logs and receipts remain under audit/.
Inherited v13 and earlier completed failures remain separate historical evidence.
The final receipt is authoritative for total counts and any incomplete attempts.
The former v13 failure narrative is in HISTORY/v13_release_control/FAILURE_LOG.md.

A diagnostic launcher used the wrong working directory and could not locate the
script. Reissuing it from the release directory passed. Two exploratory reads
used nonexistent guessed paths (a rounding module and a runtime metadata file);
file discovery located the actual sources/directories. These were orchestration
errors, not failed mathematical checks. An arXiv HTML retrieval failed; the primary
PDF was read successfully instead.

## A rounded-cache route failed mathematically

Independently rounding gain and stored residual centers does not preserve the
exact cache invariant. The scalar checked boundary has internal score zero and
true residual score two. The independent final verifier rejects the candidate.
This refutes that particular cache update, not the soundness of the final verifier
or the possibility of a future cache with propagated enclosures. No rounded
selective convergence theorem is claimed in this release.

## A broad performance claim was not supported

Caching reduces the measured selective iteration cost. The full-cost experiments
do not establish overall superiority over an efficient full Richardson baseline.
Final certificate calculation, output and formal checking are substantial costs.
The finite benchmark does not prove a universal impossibility result either.

The bounded literature search found established selection, caching, conditioning,
Wasserstein-analysis and arithmetic-certification ingredients. It did not establish
priority for the integrated artifact. Attribution and limits are recorded explicitly.

Three deliberately invalid Lean controls were rejected. The final exact diagnostics
passed 1,068 assertions with nine expected input/resource/export rejections. Negative
controls are successful checks, not unresolved proof failures.

The PowerShell launcher is provided for convenience and was not executed on Windows.
Verification was performed on Linux using the pinned portable runtime. The build and
adversarial review were performed by the same assistant, not an external reviewer.

Final seal: 117 / 117 fresh active-module checks, 543 / 543 allowed-axiom
coverage, 4 corrected current-block completed draft failures,
11 inherited completed failures, and 0 incomplete source snapshots.
All successful source, attempted-source, log, compiled-output and direct-dependency
hashes matched. The official Mathbox computation-manifest validator passed.

Current-block failed draft receipts:

- CachedPacketState: audit/20260912T164030687391Z/CachedPacketState.json
- CachedPacketSearch: audit/20260912T164221445638Z/CachedPacketSearch.json
- CachedPacketSolver: audit/20260912T164248068913Z/CachedPacketSolver.json
- CachedRoundingBoundary: audit/20260912T164518852803Z/CachedRoundingBoundary.json
