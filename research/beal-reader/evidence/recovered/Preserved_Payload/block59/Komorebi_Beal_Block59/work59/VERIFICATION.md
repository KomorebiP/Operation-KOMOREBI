# Reproduction contract

Run from the package root:

    python verify.py --replay-predecessors --report ../Block59_Replay.json

Python3.10+ and the standard library suffice. No network, SymPy, NumPy,
compiler, Lean, or attached account is needed. The predecessor verifier
replays its selected nested chain. New outputs are regenerated in a temporary
scratch directory; stored JSONs are compared in full, not accepted as success
flags. Reports must be outside the immutable package.

New jobs: period_certificate.py, local_torsion_checks.py, and
independent_period_certificate.py. Their coefficient domains are exact
integers, rational Q(phi), F_q and F_(q^2). All ranges and finite scan bounds
are in their source and outputs. There are no random seeds or numerical
tolerances. Generic Q in local algebra tests need not be a prime power and
is explicitly labeled as such.

The primary field basis is phi; the independent basis is sqrt5. The
independent implementation imports no primary arithmetic module. It checks
the inherited residue matrix directly with seventh-power symbols; a chosen
nonzero local symbol fixes a column normalization, not an assumed equality.
It also derives the integer determinant by a different algorithm.

Deliberately altered period membership and local residue rows must be rejected
by the independent checks. Archive-integrity tampering is tested separately.
Timeouts have status INCONCLUSIVE_TIMEOUT, not a proof or counterexample.
Default per-job wall cap is180seconds; the predecessor wrapper allows a
larger bounded aggregate interval. No extra memory or CPU quota is asserted.

Input hashes, command lines, Python/platform metadata, runtime, actual return
codes and output hashes are recorded by verify.py. The startup Block58 replay
is retained. The final archive replay and CRC/member audit are external to
the archive to avoid circular checksums. Passing checks certify these finite
assertions and byte preservation, not all source theorems or Beal. No new
Lean compilation or independent mathematical review is claimed.
