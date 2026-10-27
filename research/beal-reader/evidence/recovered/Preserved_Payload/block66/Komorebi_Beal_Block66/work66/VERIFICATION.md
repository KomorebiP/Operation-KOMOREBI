# Block 66 verification and evidence boundary

Python 3.10 or later and the standard library suffice. No network is used by
replay. Keep bytecode disabled so frozen predecessor extractions remain unchanged.
Run from the extracted package root:

    python -B verify.py --replay-predecessors --report ../Block66_Replay.json

For the new block alone, omit --replay-predecessors. For integrity checks alone,
use --integrity-only. Reports must be written outside the immutable package.
The default cap is 600 wall-clock seconds per job; it can be raised with
--job-timeout. A timeout returns status INCONCLUSIVE_TIMEOUT and a nonzero exit.
No incomplete run is accepted as a certificate or a mathematical exclusion.

## What replay verifies

1. Exact payload member set and SHA256 of every payload file, including the
   original Block65 ZIP. The manifest excludes itself to avoid a circular hash.
2. Fourteen named inherited files across seven nested archives, and byte identity
   of the copied complete112-candidate certificate with its original ZIP member.
3. Six full JSON outputs, freshly regenerated in a temporary copy after deleting
   every expected output. A cached earlier output cannot mask a failed run.
4. Corruption rejection for an altered curve count, a twisted column, an invented
   common-polynomial pair, a false zero-survivor count, an invalid semilinear
   quadruple and an altered package payload. Rejection requires the expected
   diagnostic, not merely an arbitrary nonzero process exit.
5. With --replay-predecessors, the original Block65 verifier and its declared
   selected nested predecessor chain. This is not a claim that every historical
   exploratory computation is rerun.

The original Block65 selected-chain replay completed before development in
155.898522239 seconds. Its report/log are retained. Each of the six new programs
also completed directly before packaging. Final release acceptance is recorded
in an EXTERNAL report from a freshly extracted final ZIP; consult that report
rather than treating this document as a success flag.

## Mathematical meaning

The new coefficient argument is a written conditional proof, not a theorem
established by enumerating a few Frobenius elements. Both coefficient programs
check the exact finite-field kernel lemma and all 1728 accepted quadruples on
all343 Kummer-coordinate vectors, giving592704 checks per implementation.
The primary alone additionally checks823543 finite joint-projector vectors.
Kummer theory, Chebotarev, the actual quartic comparison and the inherited
representation hypotheses remain explicit written-proof dependencies.

The two curve programs account for all172732 admissible equation pairs, with
2172 degree-one and296 degree-two curve-class counts EACH. The independent
program checks smoothness and curve assignment for every admissible pair.
Degree-two counts following necessary degree-one rejection are explicit nulls.
The new filter independently checks600 twisted symbols, four exact cyclotomic
norms, all25 columns and all stage lists. The final necessary system has TWO
survivors, not zero. No globally realized Frey representation is supplied.

No new Lean compilation or independent mathematical review occurred. Separate
arithmetic implementations are not an independent proof review.

## Observed development replay

The complete six-output development replay, including all six corruption
controls, returned PASS with process exit0 in 82.210 seconds.
Its exact report/log and outer exit record are retained. This run preceded
addition of these documentary records; the final extracted-ZIP replay checks
the complete final payload and selected predecessor chain separately.
