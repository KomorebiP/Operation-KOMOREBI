# Verification summary — publication 1.8.0 / Python 1.6.0

Current formal record: `evidence/formal_1.8.0/verification.json`.
Current full execution record: `data/release_verification.json`.
Current publication/source audit: `data/publication_verification_1.8.0.json`.

18 production modules built and kernel-replayed. 283 explicit named axiom audits,
including 169 named theorems. Ten invalid proof controls rejected as expected;
an additional false-axiom control accepted only relative to its explicit axiom
and rejected by the separate policy.

233 source tests and the same 233 tests against an installed wheel. 83,994 exact
canonical serialized cases agree with the independent model oracle and actual
Lean consumer. The earlier protected, cover, linear, recovery, retention and
covariance suites are rerun in their declared bounded domains.

The universal proof covers the Lean checker and typed JSON syntax-tree codec,
not the entire Python producer, source adapter, byte parser, printer or IO.
The 76-page monograph has 25 vector figures and 47 result groups. All 149 prior
mathematical environments are retained, with 14 new ones added.

See `FINALIZATION_REPORT.md` and `PROGRESS_LEDGER_v1.8.0.md` for exact scopes,
failures, corrections and restart point. Final delivery hashes are generated
after cleanup; a CRC check is not substituted for exact manifest coverage.
