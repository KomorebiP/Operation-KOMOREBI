# Fresh journal verification

Authoritative machine record: `../../verification/lean/fresh_verification.json`
(relative to this directory). Read it together with the raw logs.

Observed result: PASS. Twenty local modules compiled into an initially empty
object directory; 35 mapped rows; 84 distinct mapped targets; 1,126 namespace
entries audited, including definitions and generated helpers. Mapped
transitive axiom reports and the namespace-wide gate allow only `propext`,
`Classical.choice`, and `Quot.sound`. Both intended-rejection controls passed.

All compiler invocations use one worker and treat warnings as errors.
The dependency cache was reused at matching pins, not independently rebuilt.
The old 8,883-job result belongs to the archived release and is not this run's
job count. The old blanket-import attempt was interrupted for resource
pressure; narrowed-import development failures and the audit-output parser
correction are retained separately.
