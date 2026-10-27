# Beal research — Block 74
## Uniformizer probe and three-trace valuation

A local Galois probe annihilates all unit Kummer coordinates and reads the exact
period valuation. At actual depth one, three JOINTLY LABELLED rank-two traces
modulo343 recover the fixed-seven adjoint valuation through

    nu7 = beta(g)^-1 * (tr rho(tau*g)-tr rho(tau)-tr rho(g)+2)/49 mod7.

An all-depth version has exact valuation n+1+v7(v7(C)). This is conditional on
the explicitly inherited actual geometry. No candidate's numerical joint trace
has been calculated. ALL EIGHT patterns remain. No new point counts or Lean.

Run from this directory with bytecode disabled:

    python -B verify.py --report ../Block74_Replay.json

The default run checks Block74, not the full history. --replay-predecessor adds
one immediate Block73 default verifier. The exact Block73 archive is preserved
in predecessor/. Read work74/REPORT.md and the proof notes for all boundaries.
