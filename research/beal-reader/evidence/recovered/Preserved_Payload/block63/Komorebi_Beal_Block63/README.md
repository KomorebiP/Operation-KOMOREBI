# Komorebi Beal — Block 63
## Prime-83 torsion exponent obstruction and the nonzero unit coefficient

Version 6.3.0. 20 September 2026.

The exact original Block62 ZIP is in predecessor/. It contains the unmodified
nested predecessors. The main new conditional arithmetic theorem is

    a_phi != 0 and 13 divides C

throughout the retained reducible Frey-representation branch, with no bound on
its conductor or its actual depth. The finite obstruction at83 uses both the
order and an actual order49 divisor class in the exceptional finite Jacobian.

At depth1, complete beta ramification contained in
{43,113,127,197,337,463,547,883,1373,1667} is also excluded. Adding617 leaves
two necessary-system survivors, which are preserved and are not Frey realizations.

Read work63/REPORT.md and work63/PROOF_BOUNDARY.md. Reproduce with Python 3.10+
(standard library only):

    python -B verify.py --replay-predecessors --report ../Block63_Replay.json

The default verifier audits and reruns only this block. The explicit flag also
executes Block62 and its declared selected nested chain. Neither mode constitutes
an independent mathematical review or Lean proof. All arithmetic applications
retain the geometric, Kummer, class-group and representation hypotheses.
