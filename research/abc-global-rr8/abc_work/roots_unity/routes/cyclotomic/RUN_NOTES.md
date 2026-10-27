# Verification correction

The first new verifier run failed its contact-domain assertion because a manually selected control used A=18,n=3,p=7, although 7 does not divide 18^3+1. This was a test-input mistake, not a counterexample to a stated identity. The control was changed to A=3,n=3,p=7, for which 3^3+1=28. The depth assertion caught the invalid input before any filter result could be recorded.

The corrected verifier was rerun. Only its successful current output is recorded in `verification.json`; the mathematical note was not changed by this correction.
