# Literature and convention boundary — v0.28

Checked during this work:

- Stacks Project, Section 59.58, "Tate's continuous cohomology", tag 0DVG:
  https://stacks.math.columbia.edu/tag/0DVG
  Used to check the standard continuous inhomogeneous cochain convention.
- Kâzım Büyükboduk and Ryotaro Sakamoto, "L-Invariants, p-Adic Heights, and
  Factorization of p-Adic L-Functions", International Mathematics Research Notices
  2023(4), 2867–2943, DOI 10.1093/imrn/rnab322 (published online 24 November 2021):
  https://academic.oup.com/imrn/article/2023/4/2867/6438542
  Definition 2.1 (the publisher HTML was inspected in this release) includes a mapping cone of global restriction and local condition
  maps. This is comparison context, NOT a theorem imported to identify the present strict quotient
  with that article's arithmetic Selmer complex.

No proof here imports an unverified arithmetic theorem through a custom Lean axiom. All new
results compile against the pinned Mathlib and preserved source dependency closure.
The finite averaging argument is standard H1 rigidity. The value of this block is explicit
continuous local-prescription construction and integration with the actual representation defect.
No historical novelty or unconditional Strong Artin claim is made.

The low-degree strict quotient retains local one-cochain mismatches and does not quotient their
local zero-cochain gauges. Its secondary cokernel must therefore use Z1 rather than H1.
The separate finite positive theorem constructs local gauge conjugators directly. It is not a
formal equivalence between two independently defined Selmer complexes.
