# Verification record and reproduction contract

## Observed startup restoration

The original Block52 ZIP SHA256 is
4b4d14f7c7c3b5474a8c209845cf2652497e6a266d657af00d0171bcc4367157.
It was extracted cleanly, its required documents read, and its verifier run as

    python verify.py --replay-predecessors --report OUTSIDE_PACKAGE.json

The result was PASS_DECLARED_CHECKS, elapsed17.250772998000002 seconds. The
actual report and console output are STARTUP_BLOCK52_REPLAY.json and.log.
This included the Block51 replay and its six selected historical checks.
It is not a replay of every historical experiment ever mentioned in the archive.

## New finite programs

rigidity_checks.py uses exact integer pairs in Z[phi], phi^2=phi+1. It generates
644 square-zero matrices (600 with nonrational coefficients), checks 4298
admissible matrix-depth instances, and sees320 tight instances. These are
GENERATED matrices, not all integral Galois representations. It additionally
checks cyclic generator data at n=1,2,3 (5,245,12005 candidate pairs),1764
second-trace instances,10500 determinant-norm instances at n=1..12 and seven
specified Q values,300 square-zero products, and the exact fixed-prime bounds.

independent_residue_checks.py imports no primary-check module. It uses the
sqrt5 basis with s^2=5 and explicit norm inverses. It enumerates ALL 117649
elements of O/343, finding49 with square zero, exactly the multiples of 49.
It checks all 2352 units of O/49, then2303 separated lambda values with 49
same-residue a candidates each, totaling 112847 root tests. Exactly2303
correct character-root pairs survive. It also enumerates all 2352 normalized
(u,r) inF49^2 with r nonzero for the paired71, paired29, and 43 zero loci.

Both programs use no random sampling or floating-point proof comparison.
The first uses a generated integral family, the second complete finite rings.
Their independent arithmetic models are not independent mathematical reviewers.

COMPUTATION_MANIFEST.json records actual argv, runtime, environment, source
hashes before/after, scientific result hashes, logs, finite ranges and limits
for an observed run of both new scripts. It uses a project-specific schema,
not an asserted validation by an unavailable third-party manifest tool.

## Negative controls

Missing natural upper divisibility; unjustified full-depth bound; missing
residual character separation; the trace-only good 13 substitution; invalid
depths; and a nonunit inverse are rejected or explicitly exhibited as
counterexamples to those alternatives. The exact local n=3 sharpness example
is preserved. A test failure must never be relabeled successful because it
would improve the desired arithmetic conclusion.

## Release verifier

At the package root:

    python verify.py --replay-predecessors

An optional --report path must be OUTSIDE the package.
--timeout-seconds defaults to120 seconds per new job; the nested predecessor
wrapper has eight times that wall budget. No extra CPU or memory cap is
imposed by this runner. Environment/container limits can still apply.

The verifier audits payload membership and SHA256, checks the original
predecessor hash and CRC, and checks 12 named inherited source files from the
nested archives. It executes source only in isolated temporary copies, removes
old outputs before each job, and compares fresh JSON to reference results.
The two new job scripts must remain unchanged during execution. The immutable
original package must retain all input hashes before and after the replay.

With --replay-predecessors it invokes the original Block52 verifier, which
invokes Block51 and six selected historical checks. A timeout propagates as
INCONCLUSIVE_TIMEOUT, not PASS or nonexistence. Any scientific mismatch,
nonzero child exit, missing output, or altered hash fails verification.

The final release JSON and ZIP audit are supplied separately so they can
record the actual clean ZIP extraction, run outcome, and final archive hash
without introducing a circular in-archive self-hash.

## Limits

A PASS means the stated finite assertions and integrity/replay obligations
passed. It does not mean the written global theorem, class-field theorem, or
upstream geometry has been kernel-checked. No new Lean compilation, fresh
independent proof review, full Beal solution, or new point count is claimed.
