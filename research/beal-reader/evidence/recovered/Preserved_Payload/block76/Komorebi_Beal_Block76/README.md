# Komorebi Beal — Block 76
## Exact cyclotomic image at depth one

Release 7.6.0, 21 September 2026. The sole execution predecessor is the exact
Block75 v7.5.0 ZIP in predecessor/. Its SHA256 is
ffb94f91800a530e6c0869559a26b79e3d9c284d2991fe83614261610a31dd20.

Under the retained actual representation hypotheses at depth one, the image over
the FULL 7-cyclotomic tower is determined exactly by the first opposite-coordinate
image B. It contains the full second principal congruence subgroup of SL2(O).
For the eight bounded all-inert patterns B=F7; the same exact matrix-image group
therefore occurs for every hypothetical realization of each pattern.

This is an exact conditional IMAGE theorem, not the construction of a Galois map,
its local decomposition-group embeddings, a global adjoint solution, or a Frey
realization. All eight patterns remain. No mixed trace for the actual uniformizer
probe has been numerically evaluated. No Beal or signature proof is claimed.

Run with bytecode disabled:

    python -B verify.py --report ../Block76_Replay.json

Add --replay-predecessor to run one immediate Block75 DEFAULT verifier as well.
Neither option is a fresh replay of the full nested historical chain.
The verifier regenerates both scientific outputs in a fresh scratch directory,
compares their complete contents, and checks explicit corruption controls.

Written universal proofs, two separately implemented finite checks, and
same-assistant self-review. No new Lean compilation or independent mathematical
review. Python's standard library suffices. See work76/PROOF_BOUNDARY.md.
