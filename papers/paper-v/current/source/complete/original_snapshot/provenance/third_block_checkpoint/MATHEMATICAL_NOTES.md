# Mathematical notes for the checked block

Author: Komorebi P.

The previous FIR, quotient/remainder, arbitrary-branching, and exact-Haar derivations are preserved in provenance/second_block_checkpoint/MATHEMATICAL_NOTES.md. Their former uncompiled-source status is superseded by the current verification report.

1. A residue mask is dominated pointwise in norm by its input. This establishes l2 membership and norm contraction, allowing the mask to be constructed as a bounded linear map. The pointwise identities then lift to equality of bounded operators.
2. Reindexing an l2 sequence along a bijection preserves the sum of squared norms. Applying this to the signed quotient/remainder equivalence gives norm-preserving polyphase coordinates and both inverse laws.
3. Complete-pruning equivalence is proved by induction. If the root is selected, exactly-one-path-hit forces every other node to be unselected. Otherwise each child subtree inherits completeness. Recursion constructs the cut, and extensionality of selected nodes proves its uniqueness. Positivity of branching ensures every node has a terminal descendant.
4. The normalized Haar energy equality on arbitrary complex l2 channels follows from the parallelogram law and the exact square-root normalization. Both inverse laws follow from module algebra.
5. A CRT equivalence identifies a product-modulus residue with a unique pair of component residues. Equality of residue masks then follows pointwise. Coprimality of a power of two with an odd modulus gives the dyadic-odd specialization.
6. Dividing the homogeneous Smith matrix by two makes composition exactly multiplicative in its phase parameter. Nonzero phase parameters preserve nonzero homogeneous pairs. At phase -1 the map swaps the two coordinates, correctly interchanging zero and infinity.

These notes explain the checked constructions. They do not fill the explicit remaining obligations in THEOREM_LEDGER.md.
