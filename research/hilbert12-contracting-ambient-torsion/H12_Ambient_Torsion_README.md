# Hilbert 12: contracting ambient torsion and theta transport

**Author:** Komorebi P.

This research package continues the pure cubic experiment \(K=\mathbb Q(\beta)\), \(\beta^3=7\).

## Contents

- `H12_Contracting_Ambient_Torsion_Research_Note.md`: formal statements, proofs, analytic theta-return formulas, the complete mod-seven torsion dynamics and the exact distribution identity.
- `h12_contracting_seven_packet_verify.py`: integer and rational algebra of the seven-point packet, plus optional high-precision numerical theta-carry checks.
- `h12_full_ambient_torsion_verify.py`: all 343 period carries, all orbit lengths, the order-21 arithmetic action, and optional numerical tests of the rank-three distribution identity.
- `H12_Contracting_Seven_Packet_Verification_Log.txt`: accepted exact and numerical run.
- `H12_Full_Ambient_Torsion_Verification_Log.txt`: accepted exact and numerical run.
- `SHA256SUMS.txt`: hashes of the included files, excluding the hash file itself.

## Reproduction

Requires Python 3 with SymPy and mpmath. The optional complete distribution numerical test also uses mpmath. NumPy is not required.

```bash
python h12_contracting_seven_packet_verify.py
python h12_full_ambient_torsion_verify.py

python h12_contracting_seven_packet_verify.py --numeric
python h12_full_ambient_torsion_verify.py --numeric
```

## Verification boundary

The exact script assertions check algebraic and finite-group identities. The analytic distribution formula is proved from the convergent elliptic-gamma logarithmic series in the mathematical note. Its numerical replay is supplementary, not an interval certificate. No Lean compilation or independent external review is claimed for this package.

**Open:** The exact identity between the normalized elliptic-gamma special value and the constructed cubic class-field unit. This package does not solve Hilbert's twelfth problem, the complex cubic algebraicity conjecture, or the remaining polarized phase identity.
