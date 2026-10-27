# Cache directory correction

The first integrated run, `centered_run01`, failed before any compiler command
with `Pinned external cache missing`. The runtime's manifest check had passed.
The runner incorrectly required every declared dependency to have a compiled
library directory. The authenticated runtime includes the `Cli` dependency's
source and pinned revision but no `.lake/build/lib/lean` directory, and this
extension does not directly import a `Cli` module.

The correction records missing build directories and omits them from the search
path. It then resolves every direct external import from the production closure,
controls and generated auditors against existing dependency and toolchain
directories. Each resolved `.olean` must match the pinned runtime manifest.
Missing required imports remain fatal. Fresh compilation checks all transitive
imports. No empty cache directory is created and no compiler, theorem, source,
axiom, or control requirement is weakened.

All nine dependency Git pins and both full declared-runtime endpoint checks
remain in force. Only the nine mutable Git indexes retain the original explicit
exclusion. The failed first run is preserved without alteration.

The focused correction check resolved 40 direct external imports through eight
dependency cache directories and the toolchain library. Exactly one dependency
build directory was absent: `Cli`. An intentionally nonexistent import was
rejected. The check did not run or claim final mathematical acceptance.

Previous runner SHA-256:
`30fadbf66c4fc035e65521ee1451315223a8613aeb661da07746c95e2a50bb3e`

Corrected runner SHA-256:
`2ae5b2e524b3a7527b4a762bc6914296dc06e90ee11056fba6eaaf6c7a1eaa26`

Evidence: `selfcheck03/CACHE_RESOLUTION.json` and `selfcheck03/SELF_CHECK.json`.
