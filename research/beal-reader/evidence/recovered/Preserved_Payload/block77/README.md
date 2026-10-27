# Komorebi Beal research — Block 77

## Secondary adjoint obstruction and affine Selmer reduction

Release 7.7.0, 21 September 2026.

This block starts from the exact Block 76 checkpoint and attacks the unresolved
`q` equation in the actual depth-one adjoint deformation.  The central result is
not an exclusion of the eight remaining bounded patterns.  It identifies the
second-stage obstruction precisely, proves a local-global theorem for that
obstruction, and isolates the remaining arithmetic problem as an affine Selmer
matching problem with the fixed-seven period value among its local conditions.

Authoritative predecessor:

`predecessor/Komorebi_Beal_Block76_Exact_Cyclotomic_Image_v7.6.0.zip`

Run:

    python -B verify.py --report ../Block77_Replay.json

Add `--replay-predecessor` only to run the immediate Block 76 default verifier.
It is not a request for the complete historical chain.

No new Lean certificate or independent mathematical review is claimed.
