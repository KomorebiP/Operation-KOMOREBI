# Actual Hilbert boundary controls

`formal/tests/positive/HilbertBoundaryCases.lean` passed its first strict compiler
attempt with one thread, warnings as errors, and automatic implicit variables
disabled. The final compiler log is empty. Exact source, object and log hashes
are in `attempt_001/result.json`; the source snapshot, environment and command
are preserved beside it.

The first control constructs a full basis of the actual Hilbert space ℝ whose
single basis vector is 2. It proves that the Gram entry is 4, and specializes
the actual normal-residual reconstruction and squared Hilbert-norm theorems at
T=0, α=-2, c=1/4 and r=0. The derived coordinate-equation covector is -2, the
reconstructed Hilbert residual is -1, and the inverse-Gram certificate is 1.
This tests a genuinely nonorthonormal basis and a negative parameter.

The second control constructs the actual empty orthonormal basis of
EuclideanSpace ℝ (Fin 0). For arbitrary real α, datum r and empty coefficient
vector c, it specializes the computed coordinate certificate theorem and the
original Hilbert-norm zero theorem. No positivity or nonempty-index premise is
introduced.

Mathematical proofreading self-review covered this entire new control file.
No mathematical-token corrections or unresolved issues remained. Production
source was not changed.
