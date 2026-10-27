# Komorebi Quadratic-Form Engine v1.9

v1.9 extends the rigorous positive-tail contract one level upstream.

A binary64 factor matrix is treated as the exact dyadic matrix stored in
memory.  A high-precision eigensolver supplies only a candidate basis and
candidate eigenvalues.  Directed-rounding postchecks bound orthogonality and
reconstruction residuals, which yield coefficient-wise eigenvalue intervals.
Those intervals are propagated monotonically into the existing fail-closed
positive-tail enclosure.

The current verified matrix-to-spectrum implementation is dense/full-basis and
therefore aimed at correctness rather than large-scale memory efficiency.  The
next scalable step is a verified streamed range-core/residual-completion path.
