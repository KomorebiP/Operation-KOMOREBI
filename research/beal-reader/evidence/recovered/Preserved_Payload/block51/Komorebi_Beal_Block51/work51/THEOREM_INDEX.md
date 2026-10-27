# Block 51 theorem index

These identifiers index written arguments, not Lean declarations.

| ID | Statement | Proof location | Dependencies |
|---|---|---|---|
| T51.1 | Integral ramification depth n=t+2s, 0<=s<=h | LOCAL_DEPTH_THEOREM.md §1 | Explicit DVR matrix hypotheses only |
| T51.2 | Local cup vanishes below / is nonzero at the upper endpoint | LOCAL_DEPTH_THEOREM.md §3 | T51.1; local tame setting; t,h>=1 |
| T51.3 | Sharp family at every allowed depth, with compact irreducible examples | LOCAL_DEPTH_THEOREM.md §4 | Direct matrices; not a global realization |
| T51.4 | Actual stable lattices form the segment 0..n | ARITHMETIC_SUPPORT.md §1 | Inherited absolute irreducibility, split toric natural lattice at three |
| T51.5 | Natural variable monodromy content t_v=1+v_7(v_q(C)) | ARITHMETIC_SUPPORT.md §2 | Explicit sextic, split twist, graph-period comparison, integral RM |
| T51.6 | Nonempty depth-sensitive ramification support S_n | ARITHMETIC_SUPPORT.md §3 | T51.1, T51.4, T51.5; inherited local restrictions and class-group input |
| C51.7 | Parity/multiplicity cost and conditional two-depth regime | ARITHMETIC_SUPPORT.md §4 | T51.6 plus stated ordinary hypotheses |
| C51.8 | Exact multiplicity and unit-coordinate cost for the old ray family | ARITHMETIC_SUPPORT.md §5 | T51.2, coupling identity, additional realization and Kummer hypotheses |

No entry proves the full (3,5,7) signature or Beal. Proof boundaries and
finite checks are documented separately. No literature-wide novelty
classification is asserted.
