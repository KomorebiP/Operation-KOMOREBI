# Failures and corrections

All unsuccessful compiler invocations have retained source snapshots, logs and
exit-status receipts in audit/. No failed invocation is counted as a proof check.

- PosteriorOutputSemantics: the first draft omitted DecidableEq instances required
  by the existing real matrix operator API and left coordinate embeddings opaque
  to exact_mod_cast. The next draft still needed explicit reduction of pointwise
  subtraction. Retaining the required instances, exposing rational coordinate
  casts, and a definitional equality step resolved the semantic bridge.
- PosteriorOutputSolver: the proof was rejected under warnings as errors because
  if_pos and if_neg are deprecated in the pinned runtime. The current
  ite_eq_left and ite_eq_right names resolved the failure.
- Concrete output exporter: direct equality decision for two-dimensional function
  expressions did not synthesize the needed decision procedure. Pointwise finite
  case proofs compute each covariance entry. The scalar case additionally needed
  sequential tactics instead of redundant all-goals combinators. An intervening
  quantified decision attempt also failed; its snapshot is retained.
- Diagnostics setup: SymPy was unavailable in both the default and primary Python
  environments. Both attempted contract-creation commands failed before a
  diagnostic run. The final suite uses standard-library exact Fraction arithmetic
  and a separately implemented direct Joseph-factor scalar-sum reference.
- One initial orchestration call failed JavaScript parsing before launching a
  process. It made no mathematical or filesystem change.

The final receipt gives the exact completed compiler-failure count. Three negative
controls are deliberate expected rejections, not defects: false equality, an
explicit placeholder, and an enclosure with a deliberately dropped radius.

Early diagnostic manifests are historical snapshots. The final diagnostic run
was repeated after the exporter edits so its recorded input hashes match final
sources. Only that final run supplies the current finite-evidence record.

The portable runtime was restored from five pre-existing parts. All five part
hashes and the combined archive hash matched their preserved metadata. The v11
continuation's SHA256 and ZIP integrity also matched. No external runtime download
or new mathematical source claim was required.

Final outcome: 82 active modules passed, with 416 declarations audited and six
completed draft compiler failures. There were no incomplete compilation receipts.
