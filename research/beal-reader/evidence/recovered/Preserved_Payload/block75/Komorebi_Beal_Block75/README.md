# Komorebi Beal — Block 75
## Global integral semilinearity and endpoint compatibility

Release 7.5.0, 21 September 2026.

The actual conjugate-curve isomorphism and oriented stable-lattice uniqueness give
an integral coefficient-semilinear operator preserving both endpoints at every
positive depth, under the precise G1–G3 hypotheses. G4 supplies a compatible local
choice of conjugation and an endpoint-adapted integral normal form. This is an
existence/comparison theorem, not a numerical construction for the eight patterns.
No pattern is eliminated, no labelled mixed trace is evaluated, and no Beal or
full-signature proof is asserted.

Read work75/REPORT.md, TARGET_CONTRACT.md, PROOF_BOUNDARY.md, and notes/*.md.
Reproduce the NEW finite assertions and corruption checks with:

    python -B verify.py --report ../Block75_Replay.json

To also replay the immediate Block74 default verifier:

    python -B verify.py --replay-predecessor --report ../Block75_With_Block74.json

Neither command is a new full historical-chain replay. The original Block74 ZIP
is byte-for-byte in predecessor/, with all its nested history. Keep bytecode off.
The verifier performs new scientific runs in a fresh scratch directory, deletes
expected scientific outputs first, compares their full contents, and independently
checks deliberately corrupted certificates. Python's standard library suffices.

Status: written conditional proofs, two separately implemented finite checks, and
same-assistant adversarial review. No new Lean or external independent review.
